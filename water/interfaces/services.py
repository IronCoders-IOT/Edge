"""Interfaces for water record services."""
from flask import Blueprint, request, jsonify
import time

from iam.interfaces.services import authenticate_request
from water.application.services import WaterRecordApplicationService
from shared.infrastructure import backend_client
from water.quality import get_quality_text

water_api = Blueprint("water_api", __name__)

water_record_service = WaterRecordApplicationService()

last_quality_sent = {}  # device_id: last_quality
last_level_sent = {}    # device_id: (level_percentage, timestamp)

TANK_HEIGHT_CM = 14.0  # Total tank height in centimeters
LEVEL_CRITICAL_THRESHOLD = 20    # Critical low level percentage
ABRUPT_DROP_THRESHOLD = 10       # Abrupt drop in percentage
ABRUPT_TIME_WINDOW_SEC = 120     # Time window for abrupt drop (seconds)

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new water record."""
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.get_json()
    try:
        device_id = data.get("device_id", "esp32-01")
        raw_distance_cm = None  # To include in the response/debug
        level_percentage = None  # Water level in percentage

        if "raw_tds" in data and "raw_distance" in data:
            tds_raw = data["raw_tds"]
            raw_distance = data["raw_distance"]
            # Convert tds_raw to tds (ppm)
            voltage = tds_raw * (3.3 / 4095.0)
            tds = (133.42 * voltage ** 3) - (255.86 * voltage ** 2) + (857.39 * voltage)
            # Conversion from raw_distance to cm
            distance = raw_distance * 0.034 / 2
            raw_distance_cm = distance
            # Water level percentage
            level_percentage = max(0, min(100, ((TANK_HEIGHT_CM - distance) / TANK_HEIGHT_CM) * 100))
            print(f"Received distance in cm: {distance:.2f} - Level: {level_percentage:.1f}%")

            # If the level is 0, the event says "no water"
            if level_percentage == 0:
                qualityValue = "No water"
            else:
                qualityValue = get_quality_text(tds)
            levelValue = level_percentage   # percentage
            eventType = "water-measurement"
            sensorId = 1
            bpm = 0

            # Logic to determine if POST should be sent
            now = time.time()
            abrupt_drop = False
            critical_level = False

            last_level_tuple = last_level_sent.get(device_id)
            if last_level_tuple:
                prev_level, prev_time = last_level_tuple
                # Detect abrupt drop (>10% in less than 2 minutes)
                if prev_level - level_percentage > ABRUPT_DROP_THRESHOLD and now - prev_time < ABRUPT_TIME_WINDOW_SEC:
                    abrupt_drop = True
            # Detect critical level
            if level_percentage < LEVEL_CRITICAL_THRESHOLD:
                critical_level = True

            last_quality = last_quality_sent.get(device_id)
            # Only prevent POST if there is NO quality change, NO abrupt drop, and NOT critical level
            # Always send if level_percentage == 0
            if level_percentage != 0 and last_quality == qualityValue and not abrupt_drop and not critical_level:
                return jsonify({
                    "message": "No significant event, no POST sent.",
                    "distance_cm": distance,
                    "level_percentage": level_percentage
                }), 200

            # Update records
            last_quality_sent[device_id] = qualityValue
            last_level_sent[device_id] = (level_percentage, now)

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

        # Send event to backend (optional, ignored if it fails)
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
            "created_at": record.created_at.isoformat() + "Z",
            "distance_cm": raw_distance_cm,
            "level_percentage": level_percentage
        }), 201

    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400