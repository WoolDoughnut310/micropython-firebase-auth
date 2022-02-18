import sys

if sys.implementation.name == "micropython":
    import urequests as requests
    import ujson as json
    import utime as time

    class FileNotFoundError(Exception):
        pass
else:
    import requests
    import json
    import time

AUTH_ENDPOINT = "https://identitytoolkit.googleapis.com/v1/accounts"


class AuthError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f"{self.message} ({self.code})"


class AuthSession:
    def __init__(self, api_key, credentials):
        self.api_key = api_key
        self.credentials = credentials

    def _handle_credentials(self, data):
        self.set_credentials(dict(
            access_token=data["idToken"],
            refresh_token=data["refreshToken"],
            token_expiry=time.time() + int(data["expiresIn"])
        ))

    def request(self, endpoint, data=None, method=None, **kwargs):
        if data is None:
            data = {}

        if method:
            data["idToken"] = self.access_token
        else:
            # Endpoint returning credentials
            data["returnSecureToken"] = True

        response = requests.request(
            method if method is not None else "POST",
            f"{AUTH_ENDPOINT}:{endpoint}?key={self.api_key}",
            json=data,
            **kwargs
        )
        self._check_status_code(response)

        if method is None:
            data = response.json()
            self._handle_credentials(data)

        return response

    @property
    def access_token(self):
        current_token = self.credentials["access_token"]
        expiry = self.credentials["token_expiry"]
        if current_token and time.time() <= expiry:
            return current_token

        return self._refresh_access_token()

    def set_credentials(self, creds):
        if creds.get("access_token"):
            self.credentials["access_token"] = creds["access_token"]
        if creds.get("refresh_token"):
            self.credentials["refresh_token"] = creds["refresh_token"]
        if creds.get("token_expiry"):
            self.credentials["token_expiry"] = creds["token_expiry"]

    def clear_credentials(self):
        self.credentials = {}
        self.save_credentials({})

    @classmethod
    def load_credentials(cls):
        try:
            with open("credentials.json") as credentials_file:
                credentials = json.loads(credentials_file.read())
            assert credentials["refresh_token"]
            assert credentials["access_token"]
            assert credentials["token_expiry"]
        except (OSError, ValueError, FileNotFoundError, KeyError, AssertionError):
            return {}

        return credentials

    @classmethod
    def save_credentials(cls, creds):
        with open("credentials.json", "w") as creds_file:
            json.dump(creds, creds_file)

    @staticmethod
    def _check_status_code(response):
        if response.status_code >= 400:
            error = AuthSession._error_from_response(response)
            raise AuthError(error)

    @staticmethod
    def _error_from_response(response):
        try:
            error = response.json()["error"]
            message = error["message"]
            code = error["code"]
        except (ValueError, KeyError):
            message = response.text
            code = 400
        return {"message": message, "code": code}

    def _refresh_access_token(self):
        endpoint = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        params = dict(
            grant_type="refresh_token",
            refresh_token=self.credentials["refresh_token"]
        )
        response = requests.post(endpoint, json=params)
        self._check_status_code(response)
        data = response.json()
        self._handle_credentials(data)

        return self.credentials["access_token"]


class FirebaseAuth:
    def __init__(self, api_key):
        credentials = AuthSession.load_credentials()
        self.session = AuthSession(api_key, credentials)
        self.user = {}

    def _fill_details(self, data):
        if data.get("localId"):
            self.user["uid"] = data["localId"]
        if data.get("email"):
            self.user["email"] = data["email"]
        if data.get("displayName"):
            self.user["display_name"] = data["displayName"]
        if data.get("photoUrl"):
            self.user["photo_url"] = data["photo_url"]

    # Refreshes user data
    def refresh_user(self):
        response = self.session.request("lookup", method="POST")
        raw_user = response.json()["users"][0]
        self._fill_details(raw_user)

    # Create a new email and password user.
    # Leave email=None and password=None to sign in anonymously
    def sign_up(self, email=None, password=None):
        if email is None and password is None:
            data = {}
        else:
            data = dict(email=email, password=password)
        self.session.request("signUp", data)
        self.refresh_user()

    # Sign in a user with an email and password.
    def sign_in(self, email, password):
        data = dict(email=email, password=password)
        self.session.request("signInWithPassword", data)
        self.refresh_user()

    # Clear user session
    def sign_out(self):
        self.session.clear_credentials()
        self.user = {}
