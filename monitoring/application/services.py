"""Application services for managing monitoring records."""
from monitoring.domain.entities import WaterRecord
from monitoring.domain.services import WaterRecordService
from monitoring.infrastructure.repositories import WaterRecordRepository
from iam.application.services import AuthApplicationService
from shared.infrastructure import backend_client


class WaterRecordApplicationService:
    """Service for managing monitoring records."""
    def __init__(self):
        """Initialize the health record application service."""
        self.water_record_repository = WaterRecordRepository()
        self.water_record_service = WaterRecordService()
        self.iam_service = AuthApplicationService()

    def create_water_record(self, device_id: str, bpm: float, created_at: str, api_key: str) -> WaterRecord:
        """
        create a new monitoring record.
            Arguments:
                device_id (str): The ID of the device.
                bpm (float): The beats per minute value.
                created_at (str): The timestamp when the record was created.
                api_key (str): The API key for authentication.
            Returns:
                HealthRecord: The created monitoring record.
            Raises:
                ValueError: If the device ID or API key is invalid.
        """
        if not self.iam_service.get_by_id_and_api_key(device_id, api_key):
            raise ValueError("Invalid device ID or API key")
        record = self.water_record_service.create_record(device_id, bpm, created_at)
        saved_record = self.water_record_repository.save(record)
        return saved_record