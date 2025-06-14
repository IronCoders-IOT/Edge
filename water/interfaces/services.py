"""Interfaces for water record services."""
from flask import Blueprint, request, jsonify
from water.application.services import WaterRecordApplicationService

water_api = Blueprint("water_api", __name__)

water_record_service = WaterRecordApplicationService()

@water_api.route("/api/v1/water-monitoring/data-records", methods=["POST"])
def create_water_record():
    """Create a new water record.
    This endpoint allows devices to submit water records with their
    beats per minute (bpm), and an optional timestamp for when the record was created.
    A unique device ID will be automatically generated for each record.
    Returns:
        JSON response with the created water record details or an error message.
    """
    data = request.json
    try:
        bpm = data["bpm"]
        created_at = data.get("created_at")
        record = water_record_service.create_water_record(
            request.headers.get("X-API-Key"),
            bpm=bpm,
            created_at=created_at
        )
        return jsonify({
            "id": record.id,
            "device_id": record.device_id,
            "bpm": record.bpm,
            "created_at": record.created_at.isoformat() + "Z"
        }), 201
    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

