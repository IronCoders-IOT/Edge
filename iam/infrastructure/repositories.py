"""Repository for managing device entities in the IAM context."""
import peewee
from typing import Optional
from iam.domain.entities import Device
from iam.infrastructure.models import Device as DeviceModel
import uuid
from datetime import datetime, UTC

class DeviceRepository:
    @staticmethod
    def find_by_id_and_api_key(device_id: str, api_key: str) -> Optional[Device]:
        """find a device by its ID and API key.

        Args:
            device_id (str): The unique identifier for the device.
            api_key (str): The API key associated with the device.

        Returns:
            Device: The device if found, otherwise None.
        """
        try:
            device = DeviceModel.get((DeviceModel.device_id == device_id) & (DeviceModel.api_key == api_key))
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def create_device() -> Device:
        """Creates a new device with automatically generated ID and API key.
        
        Returns:
            Device: The newly created device.
        """
        device = DeviceModel.create_device()
        return Device(device.device_id, device.api_key, device.created_at)

    @staticmethod
    def get_or_create_test_device() -> Device:
        """Get or create a test device for development purposes.
        Returns:
            Device: A test device with automatically generated credentials.
        """
        try:
            # Try to find an existing test device
            device = DeviceModel.get(DeviceModel.api_key == "test-api-key-123")
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            # If no test device exists, create one with the test API key
            device = DeviceModel.create(
                device_id=str(uuid.uuid4()),
                api_key="test-api-key-123",
                created_at=datetime.now(UTC)
            )
            return Device(device.device_id, device.api_key, device.created_at)