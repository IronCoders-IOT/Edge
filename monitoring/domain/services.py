"""Domain Services for Health Records."""
from datetime import timezone, datetime
from dateutil.parser import parse
from monitoring.domain.entities import WaterRecord
import uuid

class WaterRecordService:
    """Service for managing monitoring records."""
    def __init__(self):
        """Initializes the HealthRecordService."""
        pass

    @staticmethod
    def create_record(device_id: str, bpm: float, created_at: str | None) -> WaterRecord:
        """creates a WaterRecord instance.
        Args:
            device_id (str): Identifier for the device that recorded the BPM.
            bpm (float): Beats per minute recorded by the device.
            created_at (str | None): Timestamp when the record was created, in ISO format.
        Returns:
            HealthRecord: An instance of WaterRecord with the provided data.
       """
        try:
            bpm = float(bpm)
            if not (0 <= bpm <= 200):
                raise ValueError("BPM must be between 0 and 200.")
            if created_at:
                parsed_created_at = parse(created_at).astimezone(timezone.utc)
            else:
                parsed_created_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            raise ValueError("Invalid input for BPM or created_at.")
        return WaterRecord(bpm=bpm, created_at=parsed_created_at, device_id=device_id)