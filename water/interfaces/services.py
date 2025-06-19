"""Interfaces for water record services."""
from flask import Blueprint, request, jsonify
from water.application.services import WaterRecordApplicationService
from iam.interfaces.services import authenticate_request
from shared.infrastructure import backend_client
water_api = Blueprint("water_api", __name__)

water_record_service = WaterRecordApplicationService()

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new water record.
    Esta versión requiere que el device_id venga en el JSON.
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result
    data = request.json
    try:
        device_id = data["device_id"]
        bpm = data["bpm"]
        created_at = data.get("created_at")
        eventType= data["eventType"]
        qualityValue = data["qualityValue"]
        levelValue = data["levelValue"]
        sensorId= data["sensorId"]
        record = water_record_service.create_water_record(
            device_id, bpm, created_at, request.headers.get("X-API-Key")
        )
        # Enviar evento al backend
        try:
            event_data = {
                "eventType": eventType,
                "qualityValue": qualityValue,
                "levelValue": levelValue,
                "sensorId": sensorId,
            }
            backend_client.post_event_to_backend(event_data)
        except Exception as e:
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

