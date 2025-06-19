import requests
import threading

token_lock = threading.Lock()
_backend_token = None

BACKEND_URL = "http://localhost:8080"  # Cambia esto por la URL real del backend
LOGIN_ENDPOINT = "/api/v1/authentication/sign-in"  # Ajusta si el endpoint es diferente
EVENTS_ENDPOINT = "/api/v1/events"       # Ajusta si el endpoint es diferente
USERNAME = "pupu.pupu"                    # Cambia por el usuario real
PASSWORD = "DNI"                # Cambia por el password real

def get_backend_token():
    global _backend_token
    with token_lock:
        if _backend_token is not None:
            return _backend_token
        url = BACKEND_URL + LOGIN_ENDPOINT
        data = {"username": USERNAME, "password": PASSWORD}
        resp = requests.post(url, json=data)
        if resp.status_code == 200:
            # Ajusta la clave según la respuesta real del backend
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
        # Token expirado, refrescar
        with token_lock:
            _backend_token = None
        token = get_backend_token()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(url, json=event_data, headers=headers)
    return resp 