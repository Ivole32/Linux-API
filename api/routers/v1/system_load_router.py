# FastAPI imports
from fastapi import APIRouter, HTTPException, Request, Depends

# Rate limiting
from api.limiter.limiter import limiter

# Readiness check utility
from api.utils.check_class_readiness import ensure_class_ready

# Load Monitor
from api.services.load_monitor import load_monitor

# Logging
from api.logger.logger import logger

# Auth
from api.auth.auth import get_current_user_perm

# Exceptions
from api.exeptions.exeptions import NoAverageCpuLoad, NoAverageSystemLoad

check_load_monitor_ready = lambda: ensure_class_ready(load_monitor, name="LoadMonitor")

router = APIRouter(
    prefix="/system/load",
    tags=["System"],
    dependencies=[Depends(check_load_monitor_ready)]
)

@router.get("/average", description="Get average system and cpu load")
@limiter.limit("10/minute")
async def avg_load(request: Request, _ = Depends(get_current_user_perm)):
    try:
        return {
            "system": {
                "average_load": load_monitor.get_average_system_load(),
            },
            "cpu": {
                "average_load": load_monitor.get_average_cpu_load(),
            }
        }
    
    except NoAverageSystemLoad:
        raise HTTPException(status_code=500, detail="Could not load avg system load")
    
    except NoAverageCpuLoad:
        raise HTTPException(status_code=500, detail="Could not load avg cpu load")

    except Exception as e:
        logger.error("Unexpected error while getting average system and cpu loads")
        raise HTTPException(status_code=500, detail="Unexpected error while loading/returning values")
    
@router.get("/cpu/average", description="Get average cpu load")
@limiter.limit("10/minute")
async def avg_load(request: Request, _ = Depends(get_current_user_perm)):
    try:
        return {
            "cpu": {
                "average_load": load_monitor.get_average_cpu_load(),
            }
        }
    
    except NoAverageCpuLoad:
        raise HTTPException(status_code=500, detail="Could not load avg cpu load")

    except Exception as e:
        logger.error("Unexpected error while getting average cpu load")
        raise HTTPException(status_code=500, detail="Unexpected error while loading/returning values")
    
@router.get("/system/average", description="Get average system load")
@limiter.limit("10/minute")
async def avg_load(request: Request, _ = Depends(get_current_user_perm)):
    try:
        return {
            "system": {
                "average_load": load_monitor.get_average_system_load(),
            }
        }
    
    except NoAverageSystemLoad:
        raise HTTPException(status_code=500, detail="Could not load avg system load")

    except Exception as e:
        logger.error("Unexpected error while getting average system load")
        raise HTTPException(status_code=500, detail="Unexpected error while loading/returning values")

@router.get("/values", description="Get system and cpu load values")
@limiter.limit("10/minute")
async def avg_load(request: Request, n: int = 5, _ = Depends(get_current_user_perm)):
    try:
        return {
            "system": {
                "last_loads": load_monitor.get_last_system_loads(n=n)
            },
            "cpu": {
                "last_loads": load_monitor.get_last_cpu_loads(n=n)
            }
        }

    except Exception as e:
        logger.error("Unexpected error while getting system and cpu load values")
        raise HTTPException(status_code=500, detail="Unexpected error while loading/returning values")
    
@router.get("/cpu/values", description="Get cpu load values")
@limiter.limit("10/minute")
async def avg_load(request: Request, n: int = 5, _ = Depends(get_current_user_perm)):
    try:
        return {
            "cpu": {
                "last_loads": load_monitor.get_last_cpu_loads(n=n)
            }
        }

    except Exception as e:
        logger.error("Unexpected error while getting cpu load values")
        raise HTTPException(status_code=500, detail="Unexpected error while loading/returning values")
    
@router.get("/system/values", description="Get system load values")
@limiter.limit("10/minute")
async def avg_load(request: Request, n: int = 5, _ = Depends(get_current_user_perm)):
    try:
        return {
            "system": {
                "last_loads": load_monitor.get_last_system_loads(n=n)
            }
        }

    except Exception as e:
        logger.error("Unexpected error while getting system load values")
        raise HTTPException(status_code=500, detail="Unexpected error while loading/returning values")