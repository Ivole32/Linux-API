from fastapi import HTTPException, Depends, Header
from api.database.user_database.user_database import user_database

from api.exeptions.exeptions import *

def get_current_user_from_api_key(x_api_key: str = Header(...)):
    try:
        user = user_database.get_user_perm_by_api_key(x_api_key)
        if not user:
            raise UserPermReadError("Unexpected error loading user_perm: get_user_perm_by_api_key returned Null")

        else:
            return user

    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Unauthorized")

    except (Exception, UserPermReadError, KeyHashError):
        raise HTTPException(status_code=500, detail="Unexpected error while authentificating user")
    
def get_current_admin_user(user = Depends(get_current_user_from_api_key)):
    if not user["is_admin"]:
        raise HTTPException(403, "Admin required")
    return user