"""Interfaces for IAM services."""
from flask import Blueprint, request, jsonify, Response

from iam.application.services import AuthApplicationService

"""Blueprint for IAM service interfaces."""
iam_api = Blueprint('iam_api', __name__)

"""Initialize dependencies for IAM service."""
auth_service = AuthApplicationService()

@iam_api.route('/devices/register', methods=['POST'])
def register_device():
    """Register a new device and get its credentials.
    
    Returns:
        Response: JSON response containing the device_id and api_key.
    """
    device = auth_service.register_device()
    return jsonify({
        "device_id": device.device_id,
        "api_key": device.api_key
    }), 201

def authenticate_request() -> None | tuple[Response, int]:
    """Authenticate the incoming request using device ID and API key.
    This function checks for the presence of 'device_id' in the request JSON
    and 'X-API-Key' in the request headers.
    If either is missing or invalid, it returns 401 Unauthorized responses.
    Returns:
        None: If authentication is successful, returns None.
        Response: If authentication fails, returns a JSON response with an error message.
    """
    device_id   = request.json.get('device_id') if request.json else None
    api_key     = request.headers.get('X-API-Key')
    if not device_id or not api_key:
        return jsonify({"error": "Device ID and API key are required"}), 401
    if not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401
    return None