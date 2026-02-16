from fastapi import HTTPException, Depends, Header
from api.database.user_database.user_database import user_database

from api.exceptions.exceptions import *

user_database.create_init_user()

def _get_current_user_perm_from_api_key(
    x_api_key: str = Header(
        user_database.demo_api_key,
        description="API key for authentication."
    )
) -> dict:
    """
    Resolve a user's permission record from the X-API-Key header.

    This dependency function is designed to be used with FastAPI's
    `Depends`. It reads the API key from the request header, verifies
    it against the user database and returns the permission record.

    Raises HTTPException with appropriate status codes for empty,
    missing or invalid API keys.
    """
    try:
        user_perm = user_database.get_user_perm_by_api_key(x_api_key)
        if not user_perm:
            raise UserPermReadError("Unexpected error loading user_perm: get_user_perm_by_api_key returned Null")
        return user_perm
    except APIKeyEmptyError:
        raise HTTPException(status_code=400, detail="API key value can not be empty")
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except (Exception, UserPermReadError, KeyHashError):
        raise HTTPException(status_code=500, detail="Unexpected error while authenticating user")

def get_current_admin_perm(user_perm=Depends(_get_current_user_perm_from_api_key)):
    """
    Dependency for requiring an admin user. Uses demo API key as default in docs.
    """
    if not user_perm["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    if not user_perm["activated"]:
        raise HTTPException(status_code=403, detail="API key has to be activated")
    return user_perm

def get_current_user_perm(user_perm=Depends(_get_current_user_perm_from_api_key)):
    """
    Dependency for requiring an activated user. Uses demo API key as default in docs.
    """
    if not user_perm["activated"]:
        raise HTTPException(status_code=403, detail="API key has to be activated")
    return user_perm