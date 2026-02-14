"""
API models for user related requests
"""
from pydantic import Field, field_validator
from api.models.base import SecureBaseModel as BaseModel
from uuid import UUID
from api.config.config import USERNAME_MIN_LENGHT, USERNAME_MAX_LENGHT

class UserRegisterRequest(BaseModel):
    """
    Data model to register users
    """
    username: str = Field(..., min_length=USERNAME_MIN_LENGHT, max_length=USERNAME_MAX_LENGHT)
    is_admin: bool = Field(default=False)
    activate: bool = Field(default=False)

class UserDeleteRequest(BaseModel):
    user_id: str = Field(
        default="me",
        min_length=2,
        description="UUID of the user or 'me'"
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        if v == "me":
            return v

        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError("user_id must be 'me' or a valid UUID")