# micropython-firebase-auth

**Firebase implementation** based on [REST API](https://firebase.google.com/docs/reference/rest/database), based on [micropython-firebase-realtime-database](https://github.com/ckoever/micropython-firebase-realtime-database) from ckoever.

### Installation
You can use **uPip** to install library from **PyPi**
```python
import upip
upip.install("micropython-firebase-auth")
```
or you can just upload `firebase_auth/firebase_auth.py` to your microcontroller:
```bash
python pyboard.py -d PORT -f cp irebase_auth.py :
```

### Commands that are implemented
```
- sign_in
- sign_out
- sign_up
```
### Required modules
```
ujson, urequests, time, sys
```

### Connect to Wifi
```python
import time
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect("ssid", "pass")
    print("Waiting for Wi-Fi connection", end="...")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print()
```
### Create a FirebaseAuth instance
```python
from firebase_auth import FirebaseAuth

auth = FirebaseAuth("API_KEY")
```
The API key is required, read about it [here](https://firebase.google.com/docs/projects/api-keys#find-api-keys)
or you can find it at `Project Settings > General` in your project's [console](https://console.firebase.google.com)
## Functions
### sign_in
```python
auth.sign_in(email, password)
```
Authenticate a user with email and password
### sign_up
```python
auth.sign_up(email=None, password=None)
```
Registers an account with the given email and password
  - leave `email` and `password` empty to sign in anonymously
  
    ```python
    auth.sign_up(None, None) # Sign in as guest
    ```
  Example:
  ```python
  auth.sign_up("email", "password")
  print("Hello, " + auth.user.display_name)
  ```
### sign_out
```python
auth.sign_out()
```
Clears authentication session and stored user data
## Attributes
### user
```python
auth.user: dict()
```
Returns the user data for the currently authenticated user  
  - #### Properties  
      `uid`  
      `email`  
      `display_name` - Optional  
      `photo_url` - Optional  
### session
```python
auth.session: AuthSession
```
The `AuthSession` object used to handle requests to the backend

## AuthSession
### request
```python
session.request(method, endpoint, data=None, **kwargs)
```
Make a request to an [auth](https://firebase.google.com/docs/reference/rest/auth) endpoint requiring an idToken (the [accessToken](#access_token))
### access_token
```python
session.access_token
```
Gets the access token for use within other Firebase services such as RTDB, Firestore, etc.
### AuthSession.load_credentials
```python
AuthSession.load_credentials()
```
Reads a stored version of session credentials from a `credentials.json` file
### AuthSession.save_credentials
```python
AuthSession.save_credentials(creds)
```
Stores a session credentials object into `credentials.json` file
Example:
```python
# Storing data on system before going to sleep for 10s
import machine

creds = auth.session.credentials
AuthSession.save_credentials(creds)

machine.deepsleep(10000)
```
