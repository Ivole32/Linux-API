"""
API models for user related requests
"""
from pydantic import BaseModel, Field
from api.config.config import USERNAME_MIN_LENGHT, USERNAME_MAX_LENGHT

class UserRegisterRequest(BaseModel):
    """
    Data model to register users
    """
    username: str = Field(..., min_length=USERNAME_MIN_LENGHT, max_length=USERNAME_MAX_LENGHT)
    is_admin: bool = Field(default=False)
    activate: bool = Field(default=False)