"""Repository for Health Records."""
from water.domain.entities import WaterRecord
from water.infrastructure.models import WaterRecord as WaterRecordModel

class WaterRecordRepository:
    """
    Repository for Health Records.
    """
    @staticmethod
    def save(water_record) -> WaterRecord:
        """
        Save a water record to the database.
            Arguments:
                water_record (WaterRecord): The water record to save.
            Returns:
                WaterRecord: The saved water record with its ID.
        """
        record = WaterRecordModel.create(
            device_id   = water_record.device_id,
            bpm         = water_record.bpm,
            created_at  = water_record.created_at
        )
        return WaterRecord(
            water_record.bpm,
            water_record.created_at,
            water_record.device_id,
            record.id
        )