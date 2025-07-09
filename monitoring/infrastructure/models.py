"""Peewee model for monitoring records."""
from peewee import Model, AutoField, CharField, FloatField, DateTimeField
from shared.infrastructure.database import db

class WaterRecord(Model):
    """model representing a monitoring record with a device ID, BPM, and timestamp.
         Attributes:
                id (int): Unique identifier for the monitoring record.
                device_id (str): Identifier for the device that recorded the BPM.
                bpm (float): Beats per minute recorded by the device.
                created_at (datetime): Timestamp when the record was created.
    """
    id = AutoField()
    device_id = CharField()
    bpm = FloatField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'health_records'
