"""
Database initialization module for a Smart Band project.
This module sets up the SQLite database connection and initializes it.
"""
from peewee import SqliteDatabase

from monitoring.domain.entities import WaterRecord

db = SqliteDatabase('smart_band.db')

def init_db() -> None:
    """
    Initializes the database connection.
    """
    db.connect()
    from iam.infrastructure.models import Device
    db.create_tables([Device, WaterRecord], safe=True)
    db.close()