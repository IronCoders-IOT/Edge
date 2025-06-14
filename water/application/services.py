"""Application services for managing water records."""
from water.domain.entities import WaterRecord
from water.domain.services import WaterRecordService
from water.infrastructure.repositories import WaterRecordRepository



class WaterRecordApplicationService:
    """Service for managing water records."""
    def __init__(self):
        """Initialize the water record application service."""
        self.water_record_repository = WaterRecordRepository()
        self.water_record_service = WaterRecordService()

    def create_water_record(self, bpm: float, created_at: str) -> WaterRecord:
        """
        create a new water record.
            Arguments:
                bpm (float): The beats per minute value.
                created_at (str): The timestamp when the record was created.
            Returns:
                HealthRecord: The created water record.
        """
        record = self.water_record_service.create_record(bpm, created_at)
        return self.water_record_repository.save(record)