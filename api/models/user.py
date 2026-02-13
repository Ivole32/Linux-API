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

class UserDeleteRequest(BaseModel):
    """
    Data model to delete users
    """
    user_id: str = Field(default="me", min_length=1) # Min lenght so it is actually required (idk.)

class UserListRequest(BaseModel):
    """
    Data model to get a user list as admin
    """
    page: int = Field(default=1, description="The page you are on")
    limit: int = Field(default=50, description="The limit of users to fetch")