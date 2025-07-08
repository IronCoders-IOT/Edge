"""Repository for Health Records."""
from monitoring.domain.entities import WaterRecord
from monitoring.infrastructure.models import WaterRecord as WaterRecordModel

class WaterRecordRepository:
    """
    Repository for Health Records.
    """
    @staticmethod
    def save(water_record) -> WaterRecord:
        """
        Save a monitoring record to the database.
            Arguments:
                water_record (WaterRecord): The monitoring record to save.
            Returns:
                WaterRecord: The saved monitoring record with its ID.
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