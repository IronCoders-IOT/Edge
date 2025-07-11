"""Interfaces for monitoring record services."""
from flask import Blueprint, request, jsonify
import time

from iam.interfaces.services import authenticate_request
from monitoring.application.services import WaterRecordApplicationService
from shared.infrastructure import backend_client
from monitoring.quality import get_quality_text

DEVICE_ID_MAP = {
    "esp32-01": 1,
    "esp32-wokwi": 2,
}
water_api = Blueprint("water_api", __name__)

water_record_service = WaterRecordApplicationService()

last_quality_sent = {}  # device_id: last_quality
last_level_sent = {}    # device_id: (level_percentage, timestamp)

LEVEL_DIFF_THRESHOLD = 5  # Send POST if it changes ±5% compared to the last event
LEVEL_CRITICAL_THRESHOLD = 20    # Critical low level percentage

DIST_FULL = 3.0   # Change to the real distance with the tank full
DIST_EMPTY = 14.0 # Change to the real distance with the tank empty

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new monitoring record."""
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.get_json()
    try:
        device_id = data.get("device_id", "esp32-01")
        raw_distance_cm = None  # To include in the response/debug
        level_percentage = None  # Water level in percentage

        internal_device_id = DEVICE_ID_MAP.get(device_id)
        if internal_device_id is None:
            return jsonify({"error": f"Unknown device_id: {device_id}"}), 400

        if "raw_tds" in data and "raw_distance" in data:
            tds_raw = data["raw_tds"]
            raw_distance = data["raw_distance"]
            # Convert tds_raw to tds (ppm)
            voltage = tds_raw * (3.3 / 4095.0)
            tds = (133.42 * voltage ** 3) - (255.86 * voltage ** 2) + (857.39 * voltage)
            # Conversion from raw_distance to cm
            distance = raw_distance * 0.034 / 2
            raw_distance_cm = distance

            # --- Adjustment to mark 100% when full and 0% when empty ---
            if distance <= DIST_FULL:
                level_percentage = 100.0
            elif distance >= DIST_EMPTY:
                level_percentage = 0.0
            else:
                level_percentage = ((DIST_EMPTY - distance) / (DIST_EMPTY - DIST_FULL)) * 100.0
                level_percentage = max(0, min(100, level_percentage))

            print(f"Received distance in cm: {distance:.2f} - Level: {level_percentage:.1f}%")

            # If the level is 0, the event says "without water"
            if level_percentage == 0:
                qualityValue = "without water"
            else:
                qualityValue = get_quality_text(tds)
            levelValue = level_percentage  # percentage
            eventType = "monitoring measurement"
            deviceId = internal_device_id
            bpm = 0

            # Logic to determine if POST should be sent
            now = time.time()
            send_post = False

            prev_level_tuple = last_level_sent.get(device_id)
            prev_quality = last_quality_sent.get(device_id)

            # Force POST if it is the first time
            if prev_level_tuple is None or prev_quality is None:
                send_post = True
            else:
                prev_level, prev_time = prev_level_tuple
                # Check if level change is >=5%
                if abs(prev_level - level_percentage) >= LEVEL_DIFF_THRESHOLD:
                    send_post = True
                # Check if water quality changed
                elif prev_quality != qualityValue:
                    send_post = True
                # Check if level is critical
                elif level_percentage < LEVEL_CRITICAL_THRESHOLD:
                    send_post = True
                # Check if the level is 0
                elif level_percentage == 0:
                    send_post = True

            if not send_post:
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
            deviceId = data["deviceId"]

        created_at = data.get("created_at")

        record = water_record_service.create_water_record(
            device_id, bpm, created_at, request.headers.get("X-API-Key")
        )

        # Send event to backend (optional, ignored if it fails)
        try:
            event_data = {
                "eventType": eventType,
                "qualityValue": qualityValue,
                "levelValue": round(float(levelValue), 2),
                "deviceId": deviceId,
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
            "distance_cm": raw_distance_cm,
            "level_percentage": level_percentage
        }), 201
    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400