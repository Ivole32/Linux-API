from fastapi import APIRouter, Request

from core_functions.auth import get_user_role
from core_functions.infos import get_system_infos, list_processes, get_system_uptime
from core_functions.limiter import limiter

router = APIRouter()

@router.get(
        "/system/uptime",
        tags=["System"],
        description="This endpoint returns the system uptime in days, hours, minutes, and seconds + full seconds.",
        responses={
            200: {"description": "Uptime returned successfully"},
            401: {"description": "Unauthorized. Invalid API key"},
        }
)
@limiter.limit("10/minute")
def get_uptime(request: Request, user_data = get_user_role("user")):
    return get_system_uptime()

@router.get(
        "/system/processes",
        tags=["System"],
        description="Returns a list of all running processes on the server with their PID, name, and status.",
        responses={
            200: {"description": "Processes listed successfully"},
            401: {"description": "Unauthorized. Invalid API key"}
        }
)
@limiter.limit("20/minute")
def get_processes(request: Request, user_data = get_user_role("user")):
    processes = list_processes()
    return processes

@router.get(
        "/system/system-infos",
        tags=["System"],
        description="This endpoint returns the system information of the server.",
        responses={
            200: {"description": "System information returned"},
            401: {"description": "Unauthorized. Invalid API key"}
        }
)
@limiter.limit("10/minute")
def system_infos(request: Request, user_data = get_user_role("user")):
    system_info = get_system_infos()
    return system_info