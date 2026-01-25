from datetime import datetime
from sqlalchemy import Column, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

SCHEMA = "users"

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": SCHEMA}
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)

class UserAuth(Base):
    __tablename__ = "user_auth"
    __table_args__ = {"schema": SCHEMA}
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    api_key_hash = Column(String, nullable=False)

class UserPerm(Base):
    __tablename__ = "user_perm"
    __table_args__ = {"schema": SCHEMA}
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    is_admin = Column(Boolean, default=False)
    activated = Column(Boolean, default=False)