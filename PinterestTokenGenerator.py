import requests
from urllib.parse import urlencode
import base64
from config import load_config

cfg = load_config()

CLIENT_ID = cfg.get("PINTEREST_CLIENT_ID")
CLIENT_SECRET = cfg.get("PINTEREST_CLIENT_SECRET")
CODE = cfg.get("PINTEREST_CODE")
REDIRECT_URI = "https://localhost/"

# Authorization: Basic <base64(client_id:client_secret)>
basic_token = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {
    "Authorization": f"Basic {basic_token}",
    "Content-Type": "application/x-www-form-urlencoded"
}
payload = urlencode({
    "grant_type": "authorization_code",
    "code": CODE,
    "redirect_uri": REDIRECT_URI
})

response = requests.post(
    "https://api.pinterest.com/v5/oauth/token",   # <--- SANDBOX endpoint
    headers=headers,
    data=payload
)

print(response.status_code)
print(response.text)


#To get the token, first use this link: https://www.pinterest.com/oauth/?response_type=code&client_id="PINTEREST_CLIENT_ID"&redirect_uri=https://localhost/&scope=boards:read,boards:write,pins:read,pins:write
#get the token, and paste it in figuresend