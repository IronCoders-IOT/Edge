"""Interfaces for water record services."""
from flask import Blueprint, request, jsonify
from water.application.services import WaterRecordApplicationService
from iam.interfaces.services import authenticate_request
from shared.infrastructure import backend_client
from water.quality import get_quality_text

water_api = Blueprint("water_api", __name__)

water_record_service = WaterRecordApplicationService()

last_quality_sent = {}

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new water record.
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result
    data = request.json
    try:
        device_id = data.get("device_id", "esp32-01")
        if "raw_tds" in data and "raw_distance" in data:
            tds_raw = data["raw_tds"]
            raw_distance = data["raw_distance"]
            # Convert tds_raw to tds (ppm)
            voltage = tds_raw * (3.3 / 4095.0)
            tds = (133.42 * voltage * voltage * voltage) - (255.86 * voltage * voltage) + (857.39 * voltage)
            # Conversion from raw_distance to cm
            distance = raw_distance * 0.034 / 2
            qualityValue = get_quality_text(tds)
            levelValue = distance
            eventType = "water-measurement"
            sensorId = 1
            bpm = 0
            # Only send POST if the quality has changed
            last_quality = last_quality_sent.get(device_id)
            if last_quality == qualityValue:
                return jsonify({"message": "Water quality hasn't changed, no POST sent."}), 200
            last_quality_sent[device_id] = qualityValue
        else:
            bpm = data["bpm"]
            eventType = data["eventType"]
            qualityValue = data["qualityValue"]
            levelValue = data["levelValue"]
            sensorId = data["sensorId"]
        created_at = data.get("created_at")

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

