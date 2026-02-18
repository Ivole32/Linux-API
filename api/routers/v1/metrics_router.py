# FastAPI imports
from fastapi import APIRouter, Depends, Request, HTTPException

# Rate limiting
from api.limiter.limiter import limiter

# Readiness check utility
from api.utils.check_class_readiness import ensure_class_ready

# Logging
from api.logger.logger import logger

# Import exceptions
from api.exceptions.exceptions import *

from api.auth.auth import get_current_admin_perm

from api.utils.check_class_readiness import ensure_class_ready

# Database
from api.database.metric_database.metric_database import metric_database


from api.models.metrics import *

check_database_ready = lambda: ensure_class_ready(metric_database, name="MetricDatabase")

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
    dependencies=[Depends(check_database_ready)]
)


@router.get("/global")
@limiter.limit("10/minute")
async def global_metrics(request: Request, params: GlobalMetricRequest, _ = Depends(get_current_admin_perm)):
    try:
        return metric_database.get_global_metrics(start_time=params.start_time,
                                                  end_time=params.end_time,
                                                  limit=params.limit,
                                                  offset=params.offset,
                                                  newest_first=params.newest_first
                                                  )
    
    except Exception as e:
        logger.error(f"Unexpected error while loading global metrics: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while loading global metrics")

@router.get("/routes")
@limiter.limit("10/minute")
async def route_metrics(request: Request, params: RouteMetricsRequest, _ = Depends(get_current_admin_perm)):
    try:
        return metric_database.get_route_metrics(route=params.route,
                                                 start=params.start,
                                                 end=params.end,
                                                 limit=params.limit,
                                                 cursor=params.cursor)
    
    except Exception as e:
        logger.error(f"Unexpected error while loading routes metrics: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while loading routes metrics")
    
@router.get("/status-codes")
@limiter.limit("10/minute")
async def status_code_metrics(request: Request, params: RouteStatusCodeMetricsRerquest, _ = Depends(get_current_admin_perm)):
    try:
        return metric_database.get_route_status_code_metrics(route=params.route,
                                                             status_code=params.status_code,
                                                             start_time=params.start_time,
                                                             end_time=params.end_time,
                                                             limit=params.limit,
                                                             offset=params.offset,
                                                             newest_first=params.newest_first
        )
    
    except Exception as e:
        logger.error(f"Unexpected error while loading route status code metrics: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while loading route status code metrics")