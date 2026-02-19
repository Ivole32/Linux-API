from sqlalchemy import Column, Integer, String, DateTime, text

from .base import Base

SCHEMA = "internal"

class MigrationLog(Base):
    """
    ORM model representing an applied migration log entry.

    Stores the revision, direction, status and optional info for each
    migration operation recorded by Alembic.
    """
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