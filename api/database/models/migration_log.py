from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base
from datetime import datetime

from .base import Base

SCHEMA = "internal"

class MigrationLog(Base):
    __tablename__ = "migration_log"
    __table_args__ = {"schema": SCHEMA}

    migration_id = Column(Integer, primary_key=True, autoincrement=True)
    revision = Column(String(50), nullable=False)
    direction = Column(String(20), nullable=False) # upgrade / downgrade
    status = Column(String(20), nullable=False) # success / failed
    info = Column(String(), server_default=text("'No more info included'"))
    timestamp = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )