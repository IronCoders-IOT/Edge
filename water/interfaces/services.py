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
last_level_sent = {}    # device_id: (nivel_porcentaje, timestamp)

ALTURA_TANQUE_CM = 14.0  # Altura total del tanque en centímetros
LEVEL_CRITICAL_THRESHOLD = 20    # Porcentaje crítico de nivel bajo
ABRUPT_DROP_THRESHOLD = 10       # Caída brusca en porcentaje
ABRUPT_TIME_WINDOW_SEC = 120     # Ventana de tiempo para caída brusca (segundos)

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new water record."""
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.get_json()
    try:
        device_id = data.get("device_id", "esp32-01")
        raw_distance_cm = None  # Para incluirlo en la respuesta/debug
        nivel_porcentaje = None  # Nivel de agua en porcentaje

        if "raw_tds" in data and "raw_distance" in data:
            tds_raw = data["raw_tds"]
            raw_distance = data["raw_distance"]
            # Convert tds_raw to tds (ppm)
            voltage = tds_raw * (3.3 / 4095.0)
            tds = (133.42 * voltage ** 3) - (255.86 * voltage ** 2) + (857.39 * voltage)
            # Conversion from raw_distance to cm
            distance = raw_distance * 0.034 / 2
            raw_distance_cm = distance
            # Porcentaje de nivel de agua
            nivel_porcentaje = max(0, min(100, ((ALTURA_TANQUE_CM - distance) / ALTURA_TANQUE_CM) * 100))
            print(f"Distancia recibida en cm: {distance:.2f} - Nivel: {nivel_porcentaje:.1f}%")
            qualityValue = get_quality_text(tds)
            levelValue = nivel_porcentaje   # porcentaje
            eventType = "water-measurement"
            sensorId = 1
            bpm = 0

            # Lógica para determinar si se debe enviar POST
            now = time.time()
            abrupt_drop = False
            critical_level = False

            last_level_tuple = last_level_sent.get(device_id)
            if last_level_tuple:
                prev_level, prev_time = last_level_tuple
                # Detectar bajada abrupta (>10% en menos de 2 minutos)
                if prev_level - nivel_porcentaje > ABRUPT_DROP_THRESHOLD and now - prev_time < ABRUPT_TIME_WINDOW_SEC:
                    abrupt_drop = True
            # Detectar nivel crítico
            if nivel_porcentaje < LEVEL_CRITICAL_THRESHOLD:
                critical_level = True

            last_quality = last_quality_sent.get(device_id)
            # Solo impedir el POST si NO hay cambio de calidad, NO hay bajada abrupta y NO es nivel crítico
            if last_quality == qualityValue and not abrupt_drop and not critical_level:
                return jsonify({
                    "message": "No significant event, no POST sent.",
                    "distance_cm": distance,
                    "nivel_porcentaje": nivel_porcentaje
                }), 200

            # Actualizar registros
            last_quality_sent[device_id] = qualityValue
            last_level_sent[device_id] = (nivel_porcentaje, now)

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
            "nivel_porcentaje": nivel_porcentaje
        }), 201

    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400