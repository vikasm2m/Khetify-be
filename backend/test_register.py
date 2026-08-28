import urllib.request
import json

data = json.dumps({
    "name": "Test User",
    "email": "test99@test.com",
    "password": "password123",
    "role": "CUSTOMER"
}).encode('utf-8')

req = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/register", data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Error Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Other Error:", e)
