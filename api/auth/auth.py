from fastapi import HTTPException, Depends, Header
from api.database.user_database.user_database import user_database

from api.exeptions.exeptions import *

def _get_current_user_from_api_key(
    x_api_key: str = Header(
        default_factory=lambda: user_database.demo_api_key,
        description="API key for authentication. Default is demo key if not provided."
    )
) -> dict:
    try:
        user = user_database.get_user_perm_by_api_key(x_api_key)
        if not user:
            raise UserPermReadError("Unexpected error loading user_perm: get_user_perm_by_api_key returned Null")
        return user
    except APIKeyEmptyError:
        raise HTTPException(status_code=400, detail="API key value can not be empty")
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except (Exception, UserPermReadError, KeyHashError):
        raise HTTPException(status_code=500, detail="Unexpected error while authentificating user")

def get_current_admin(user=Depends(_get_current_user_from_api_key)):
    """
    Dependency for requiring an admin user. Uses demo API key as default in docs.
    """
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    if not user["activated"]:
        raise HTTPException(status_code=403, detail="API key has to be activated")
    return user

def get_current_user(user=Depends(_get_current_user_from_api_key)):
    """
    Dependency for requiring an activated user. Uses demo API key as default in docs.
    """
    if not user["activated"]:
        raise HTTPException(status_code=403, detail="API key has to be activated")
    return user