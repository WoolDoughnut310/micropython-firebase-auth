import network
import time
from firebase_auth import FirebaseAuth

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect("ssid", "pass")
    print("Waiting for Wi-Fi connection", end="...")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print()

api_key = "INSERT_API_KEY"
auth = FirebaseAuth(api_key)
response = auth.sign_in("email", "password")
