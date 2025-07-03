"""Repository for managing device entities in the IAM context."""
from datetime import UTC, datetime

import peewee
from typing import Optional

from flask import request

from iam.domain.entities import Device
from iam.infrastructure.models import Device as DeviceModel

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
    def get_or_create_test_device() -> Device:
        """Get or create a test device for development purposes.
        Returns:
            Device: A test device with a predefined ID and API key.
        """
        device_id = request.json.get('device_id')
        if not device_id:
            raise ValueError("device_id is required")
        device, _ = DeviceModel.get_or_create(
            device_id=device_id,
            defaults={
                "api_key": "test",
                "created_at": datetime.now(UTC)
            }
        )
        return Device(device.device_id, device.api_key, device.created_at)