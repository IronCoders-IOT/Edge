"""Domain entities for water records."""
from datetime import datetime

class WaterRecord:
    """represents a water record with a device ID, BPM, and timestamp.
       Attributes:
            id (int): Unique identifier for the water record.
            device_id (str): Identifier for the device that recorded the BPM.
            bpm (float): Beats per minute recorded by the device.
            created_at (datetime): Timestamp when the record was created.
    """
    def __init__(self, bpm: float, created_at: datetime, device_id: str = None, id: int = None):
        """initializes a WaterRecord instance.
        Args:
            bpm (float): Beats per minute recorded by the device.
            created_at (datetime): Timestamp when the record was created.
            device_id (str, optional): Identifier for the device that recorded the BPM. Defaults to None.
            id (int, optional): Unique identifier for the water record. Defaults to None.
        """
        self.id = id
        self.device_id = device_id
        self.bpm = bpm
        self.created_at = created_at
