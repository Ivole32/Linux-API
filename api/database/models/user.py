from sqlalchemy import Column, String, DateTime, func, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

SCHEMA = "users"

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": SCHEMA}
    user_id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    immutable = Column(Boolean, nullable=False, server_default=text("false"))

class UserAuth(Base):
    __tablename__ = "user_auth"
    __table_args__ = {"schema": SCHEMA}
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    api_key_hash = Column(String, nullable=True, unique=True)

class UserPerm(Base):
    __tablename__ = "user_perm"
    __table_args__ = {"schema": SCHEMA}
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    is_admin = Column(Boolean, server_default=text("false"))
    activated = Column(Boolean, server_default=text("false"))


# Relationships defined in:
# - f84c0e0cdb7e_fixed_error_with_user_child_creation_in_
# - 37abce9a74cb_fixed_missing_relationships_table_

# Immmutable users defined in:
# - 29d2e30dee1b_added_immutable_column
# - e6519d238a1b_added_immutable_user_functions
# - c37fe0d02922_make_first_admin_immutable_by_default
# - a2660751bd38_fix_for_non_immutable_user_deletion