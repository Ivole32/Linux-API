# FastAPI imports
from fastapi import APIRouter, Depends, Request, HTTPException

# Rate limiting
from api.limiter.limiter import limiter

# Readiness check utility
from api.utils.check_class_readiness import ensure_class_ready

# Database
from api.database.user_database.user_database import user_database

# Models
from api.models.user import UserRegisterRequest, UserDeleteRequest

# Logging
from api.logger.logger import logger

# Import exceptions
from api.exeptions.exeptions import *

from psycopg.errors import UniqueViolation

from api.auth.auth import get_current_admin_perm, get_current_user_perm

check_database_ready = lambda: ensure_class_ready(user_database, name="UserDatabase")
#create_init_user = lambda: user_database.create_init_user()

router = APIRouter(
    prefix="/user",
    tags=["User"],
    dependencies=[Depends(check_database_ready)], # Only handle requests if database is ready
    # on_startup=[create_init_user] // Used in auth.py to fix None demo_api_key for auth functionality
)

@router.post("/register", description="Register a new user if you are admin.")
@limiter.limit("5/minute")
async def register_user(request: Request, user_info: UserRegisterRequest, _ = Depends(get_current_admin_perm)):
    try:
        username, user_id, plain_api_key = user_database.create_user(username=user_info.username, is_admin=user_info.is_admin, activate=user_info.activate)

    except UserRecordCreationError:
        raise HTTPException(status_code=500, detail="User record could not be created")
    
    except (UserAuthCreationError, NoUserAuthCreatedError, KeyHashError):
        raise HTTPException(status_code=500, detail="User auth record could not be set")
    
    except (UserPermEditError, NoUserPermEditedError):
        raise HTTPException(status_code=500, detail="No user perm record could be created")

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="This username is already taken")

    except Exception as e:
        logger.error(f"Unexpected error while creating user: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while creating user.")

    else:
        return {"username": username, "user_id": user_id, "api_key": plain_api_key}

@router.delete("/delete", description="Delete current user or other user (if you are admin).")
@limiter.limit("5/minute")
async def delete_user_account(request: Request, user_info: UserDeleteRequest, user_perm = Depends(get_current_user_perm)):
    try:
        # User wants to delete himself => Normal user perms required
        if user_info.user_id.lower() == "me" or user_info.user_id == user_perm["user_id"]:
            if not user_database.delete_user(user_id=user_perm["user_id"]):
                raise UserDeletionError("User not deleted")
            return {"detail": "User deleted"}

        # User wants to delete other user => Admin user perms required
        # Validate current user has admin permissions
        get_current_admin_perm(user_perm)

        # Deletion after admin validation
        if not user_database.delete_user(user_id=user_info.user_id):
            raise UserDeletionError("User not deleted")
        return {"detail": "User deleted"}

    except LastAdminError:
        raise HTTPException(status_code=403, detail="Can not delete the last admin account.")
    
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Requested user not found.")
    
    except Exception as e:
        logger.error(f"Unexpected error while deleting user: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while deleting user.")

@router.get("/me", description="Load your user profile.")
@limiter.limit("10/minute")
async def get_user_account(request: Request, user_perm = Depends(get_current_user_perm)):
    try:
        return user_database.get_user_by_user_id(user_id=user_perm["user_id"])
    
    except Exception as e:
        logger.error(f"Unexpected error while loading your user's profile")
        raise HTTPException(status_code=500, detail="Unexpected error while loading your profile.")