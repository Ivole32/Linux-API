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

# System info utils
from api.utils.get_system_infos import get_system_uptime, list_processes, get_system_infos, get_system_user_infos

check_load_monitor_ready = lambda: ensure_class_ready(load_monitor, name="LoadMonitor")

router = APIRouter(
    prefix="/system/info",
    tags=["System", "Info"],
    dependencies=[Depends(check_load_monitor_ready)]
)

@router.get("/uptime", description="Get system uptime")
@limiter.limit("10/minute")
async def get_uptime(request: Request, _ = Depends(get_current_user_perm)):
    try:
        return get_system_uptime()
    
    except Exception as e:
        logger.error(f"Unexpected error while loading system uptime: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while loading system uptime")

@router.get("/processes", description="Get system processes")
@limiter.limit("10/minute")
async def get_processes(request: Request, _ = Depends(get_current_user_perm)):
    try:
        return list_processes()
    
    except Exception as e:
        logger.error(f"Unexpected error while listing system processes: {e}")
        raise HTTPException(status_code=500, detail="Unexpected erro while loading system processes")
    
@router.get("/system-info", description="Get system infos")
@limiter.limit("10/minute")
async def get_system_info(request: Request, _ = Depends(get_current_user_perm)):
    try:
        return get_system_infos()
    
    except Exception as e:
        logger.error(f"Unexpected error while loading system infos: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while loading system infos")
    
@router.get("/system-user", description="Get infoormation about a system user")
@limiter.limit("10/minute")
async def get_system_user_info(request: Request, username: str, _ = Depends(get_current_user_perm)):
    try:
        success, user_info = get_system_user_infos(username=username)
        if success:
            return user_info
        else:
            raise HTTPException(status_code=404, detail="System user not found")
        
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error while loading system user infos: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while loading system user infos")