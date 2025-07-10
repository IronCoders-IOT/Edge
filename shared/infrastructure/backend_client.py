import requests
import threading

token_lock = threading.Lock()
_backend_token = None

BACKEND_URL = "https://aquaconecta-gch4brewcpb5ewhc.centralus-01.azurewebsites.net" 
LOGIN_ENDPOINT = "/api/v1/authentication/sign-in"  
EVENTS_ENDPOINT = "/api/v1/events"       
USERNAME = "Belen.Ramos"
PASSWORD = "99887766"

def get_backend_token():
    global _backend_token
    with token_lock:
        if _backend_token is not None:
            return _backend_token
        url = BACKEND_URL + LOGIN_ENDPOINT
        data = {"username": USERNAME, "password": PASSWORD}
        resp = requests.post(url, json=data)
        if resp.status_code == 200:
            _backend_token = resp.json().get("token")
            return _backend_token
        else:
            raise Exception(f"Login failed: {resp.text}")

def post_event_to_backend(event_data):
    global _backend_token
    token = get_backend_token()
    url = BACKEND_URL + EVENTS_ENDPOINT
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, json=event_data, headers=headers)
    if resp.status_code == 401:
        # Token expired, refresh
        with token_lock:
            _backend_token = None
        token = get_backend_token()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(url, json=event_data, headers=headers)
    return resp 