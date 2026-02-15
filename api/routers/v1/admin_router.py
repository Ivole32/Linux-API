# FastAPI imports
from fastapi import APIRouter, Depends, Request, HTTPException, Query

# Rate limiting
from api.limiter.limiter import limiter

# Readiness check utility
from api.utils.check_class_readiness import ensure_class_ready

# Database
from api.database.user_database.user_database import user_database

# Logging
from api.logger.logger import logger

# Auth
from api.auth.auth import get_current_admin_perm

# Import UUID
from uuid import UUID

# Exceptions
from api.exeptions.exeptions import *

check_database_ready = lambda: ensure_class_ready(user_database, name="Userdatabase")

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(check_database_ready)]
)

@router.get("/users", description="Get a full list of users.")
@limiter.limit("10/minute")
async def list_users(request: Request, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=100), _ = Depends(get_current_admin_perm)):
    try:
        return user_database.list_users(page=page, limit=limit)
    
    except Exception as e:
        logger.error(f"Unexpected error while fetching users: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while fetching users")
    
@router.patch("/users/{user_id}/role")
@limiter.limit("10/minute")
async def change_user_role(request: Request, user_id: UUID, is_admin: bool = False, user_perm = Depends(get_current_admin_perm)):
    try:
        if user_id == user_perm["user_id"]:
            raise HTTPException(status_code=403, detail="Can't change your own admin perm.")

        success = user_database.update_user_perm(user_id=user_id, is_admin=is_admin)
        return {"success": success, "user_id": user_id, "is_admin": is_admin}

    except NoChangesNeeded:
        raise HTTPException(status_code=204, detail="No changes had to be made")

    except ImmutableException:
        raise HTTPException(status_code=403, detail="Can't set users role: user is immutable")

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User with this user_id not found.")

    except NoRowsAffected:
        raise HTTPException(status_code=500, detail="No changes could be made: No rows affected")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error while changing user role: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while changing user role.")
    
@router.patch("/users/{user_id}/activate")
@limiter.limit("10/minute")
async def activate_user(request: Request, user_id: UUID, _ = Depends(get_current_admin_perm)):
    try:
        success = user_database.update_user_perm(user_id=user_id, activated=True)
        return {"success": success, "user_id": user_id}

    except NoChangesNeeded:
        raise HTTPException(status_code=204, detail="User already activated.")
    
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User with this user_id not found.")
    
    except ImmutableException:
        raise HTTPException(status_code=403, detail="Can't activate user: user is immutable")
    
    except NoRowsAffected:
        raise HTTPException(status_code=500, detail="No changes could be made: No rows affected")

    except Exception as e:
        logger.error(f"Unexpected error while activating user: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while activating user.")
    
@router.patch("/users/{user_id}/deactivate")
@limiter.limit("10/minute")
async def deactivate_user(request: Request, user_id: UUID, user_perm = Depends(get_current_admin_perm)):
    try:
        if user_id == user_perm["user_id"]:
            raise HTTPException(status_code=403, detail="Can't deactivate own admin account.")

        success = user_database.update_user_perm(user_id=user_id, activated=False)
        return {"success": success, "user_id": user_id}

    except NoChangesNeeded:
        raise HTTPException(status_code=204, detail="User already deactivated.")
    
    except ImmutableException:
        raise HTTPException(status_code=403, detail="Can't deactivate user: user is immutable")

    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User with this user_id not found.")

    except NoRowsAffected:
        raise HTTPException(status_code=500, detail="No changes could be made: No rows affected")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error while deactivating user: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while deactivating user.")