"""Peewee models for the IAM service."""
from peewee import Model, CharField, DateTimeField
from shared.infrastructure.database import db
import uuid
from datetime import datetime

class Device(Model):
    """model representing a device in the IAM service.

    Attributes:
        device_id (str): Unique identifier for the device.
        api_key (str): An API key associated with the device. It can be null.
        created_at (datetime): Timestamp when the device was created. It can be null.
    """
    device_id   = CharField(primary_key=True)
    api_key     = CharField(null=True)
    created_at  = DateTimeField(null=True)

    class Meta:
        database    = db
        table_name  = 'devices'

    @classmethod
    def create_device(cls) -> 'Device':
        """Creates a new device with an automatically generated ID and API key.
        
        Returns:
            Device: The newly created device.
        """
        device_id = str(uuid.uuid4())
        api_key = "test-api-key-123"
        return cls.create(
            device_id=device_id,
            api_key=api_key,
            created_at=datetime.utcnow()
        )