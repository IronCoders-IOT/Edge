"""Interfaces for water record services."""
from flask import Blueprint, request, jsonify
from water.application.services import WaterRecordApplicationService
from shared.infrastructure import backend_client

water_api = Blueprint("water_api", __name__)

water_record_service = WaterRecordApplicationService()

# Autenticación simple embebida
VALID_DEVICES = {
    "esp32-01": "test-api-key-123",
    # Agrega más si necesitas: "esp32-02": "otra-clave"
}

def authenticate_request():
    api_key = request.headers.get("X-API-Key")
    json_data = request.get_json(silent=True)

    if not json_data:
        return jsonify({"error": "Missing JSON body"}), 400

    device_id = json_data.get("device_id")

    if not api_key or not device_id:
        return jsonify({"error": "Missing device_id or API key"}), 401

    expected_key = VALID_DEVICES.get(device_id)
    if expected_key != api_key:
        return jsonify({"error": "Invalid device_id or API key"}), 401

    return None

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new water record.
    Esta versión requiere que el device_id venga en el JSON.
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.get_json()
    try:
        device_id = data["device_id"]
        bpm = data["bpm"]
        created_at = data.get("created_at")
        eventType = data["eventType"]
        qualityValue = data["qualityValue"]
        levelValue = data["levelValue"]
        sensorId = data["sensorId"]

        record = water_record_service.create_water_record(
            device_id, bpm, created_at, request.headers.get("X-API-Key")
        )

        # Enviar evento al backend (opcional, se ignora si falla)
        try:
            event_data = {
                "eventType": eventType,
                "qualityValue": qualityValue,
                "levelValue": levelValue,
                "sensorId": sensorId,
            }
            backend_client.post_event_to_backend(event_data)
        except Exception:
            pass

        return jsonify({
            "id": record.id,
            "device_id": record.device_id,
            "bpm": record.bpm,
            "eventType": eventType,
            "qualityValue": qualityValue,
            "levelValue": levelValue,
            "sensorId": sensorId,
            "created_at": record.created_at.isoformat() + "Z"
        }), 201

    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
