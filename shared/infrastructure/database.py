"""
Database initialization module for a Smart Band project.
This module sets up the SQLite database connection and initializes it.
"""
from peewee import SqliteDatabase

db = SqliteDatabase('aquaconecta.db')

def init_db() -> None:
    """
    Initializes the database connection.
    """
    db.connect()
    # Importa los modelos DENTRO de la función para evitar ciclos de importación
    from iam.infrastructure.models import Device
    from monitoring.infrastructure.models import WaterRecord
    db.create_tables([Device, WaterRecord], safe=True)
    db.close()