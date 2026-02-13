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

check_database_ready = lambda: ensure_class_ready(user_database, name="Userdatabase")

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(check_database_ready)]
)

@router.get("/users", description="Get a full list of users.")
@limiter.limit("10/minute")
def list_users(request: Request, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=100), _ = Depends(get_current_admin_perm)):
    try:
        return user_database.list_users(page=page, limit=limit)
    
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while fetching users")