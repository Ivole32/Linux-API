# FastAPI imports
from fastapi import APIRouter, Depends, Request, HTTPException

# Rate limiting
from api.limiter.limiter import limiter

# Logging
from api.logger.logger import logger

# Import exceptions
from api.exceptions.exceptions import *

from api.auth.auth import get_current_admin_perm

from api.metrics.health import flush_health

from api.database.postgres_pool import postgres_pool

from api.database.migrate import migration_needed

from api.database.user_database.user_database import user_database
from api.database.metric_database.metric_database import metric_database

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/metrics")
@limiter.limit("10/minute")
async def metric_metrics(request: Request, _ = Depends(get_current_admin_perm)):
    try:
        return {
            "flush_worker": {
                "success_count": flush_health.success_count,
                "error_count": flush_health.error_count,
                "error_rate": flush_health.error_rate(),
                "consecutive_failures": flush_health.consecutive_failures,
                "last_error": flush_health.last_error,
                "last_success": flush_health.last_success,
                "last_attempt": flush_health.last_attempt
            }
        }
    
    except Exception as e:
        logger.error(f"Unexpected error while returning metric health: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while returning metric health")
    
@router.get("/database")
@limiter.limit("10/minute")
async def database_metrics(request: Request, _ = Depends(get_current_admin_perm)):
    try:
        return {
            "postgresql": {
                "ready": postgres_pool.is_ready(),
                "migration_needed": migration_needed()
            },
            "user_database": {
                "ready": user_database.is_ready()
            },
            "metric_database": {
                "ready": metric_database.is_ready()
            }
        }
    
    except Exception as e:
        logger.error(f"Unexpected error while returning database health: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while returning database health")