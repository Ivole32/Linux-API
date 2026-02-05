from fastapi import HTTPException, Depends, Header
from api.database.user_database.user_database import user_database

from api.exeptions.exeptions import *

def verify_api_key(x_api_key: str = Header(...)):
    try:
        user_database.get_user_perm_by_api_key("test")



    # // TODO
    except UserNotFoundError:
        # User nor found or wrong api key
        pass

    except (Exception, KeyHashError):
        # Unexpected error
        pass