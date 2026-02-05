from fastapi import APIRouter, Request, HTTPException

from api.limiter.limiter import limiter
from api.core_functions.auth import get_user_role
from api.services.load_monitor import LoadMonitor
from api.utils.get_system_infos import get_system_infos, list_processes, get_system_uptime, get_system_user_infos

router = APIRouter(prefix="/system")

monitor = LoadMonitor()
monitor.start()
monitor.set_decimal_place_value(2)

@router.get("/uptime", description="This endpoint returns the system uptime in days, hours, minutes, and seconds + full seconds.")
@limiter.limit("10/minute")
def get_uptime(request: Request, user_data = get_user_role("user")):
    return get_system_uptime()

@router.get("/processes", description="Returns a list of all running processes on the server with their PID, name, and status.")
@limiter.limit("20/minute")
def get_processes(request: Request, user_data = get_user_role("user")):
    processes = list_processes()
    return processes

@router.get("/system-infos", description="This endpoint returns the system information of the server.")
@limiter.limit("10/minute")
def system_infos(request: Request, user_data = get_user_role("user")):
    system_info = get_system_infos()
    return system_info

@router.get("/system-user", description="Returns informations about a specific user account on the server like UID, GID, shell and home dir.")
@limiter.limit("5/minute")
def system_user_infos(request: Request, username: str, user_data = get_user_role("user")):
    return_code, user_info = get_system_user_infos(username)

    if return_code == True:
        return user_info
    
    elif return_code == None:
        raise HTTPException(status_code=404, detail="User not found on the system")

@router.get("/avg-load", description="Returns the average load of the system over the last minutes.")
@limiter.limit("5/minute")
def avg_load(request: Request, decimal_places: int = 2, last_load_length: int = 3, user_data = get_user_role("user")):
    monitor.set_decimal_place_value(decimal_places)
    return {
        "system": {
            "average_load": monitor.get_average_system_load(),
            "last_loads": monitor.get_last_system_loads(n=last_load_length)
        },
        "cpu": {
            "average_load": monitor.get_average_cpu_load(),
            "last_loads": monitor.get_last_cpu_loads(n=last_load_length)
        }
    }