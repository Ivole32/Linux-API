from fastapi import APIRouter, Request, HTTPException

from core_functions.limiter import limiter
from core_functions.auth import get_user_role
from core_functions.load_monitor import LoadMonitor
from core_functions.infos import get_system_infos, list_processes, get_system_uptime, get_system_user_infos

router = APIRouter()

monitor = LoadMonitor()
monitor.start()
monitor.set_decimal_place_value(2)

@router.get(
        "/system/uptime",
        tags=["System"],
        description="Returns the system uptime in seconds.",
        responses={
            200: {
                "description": "System uptime returned",
                "content": {
                    "application/json": {
                        "examples": {
                            "Success": {
                                "summary": "Uptime",
                                "value": {
                                    "uptime_seconds": 123456
                                }
                            }
                        }
                    }
                }
            },
            401: {
                "description": "Unauthorized. Invalid API key",
                "content": {
                    "application/json": {
                        "examples": {
                            "Unauthorized": {
                                "summary": "Missing or invalid API key",
                                "value": {
                                    "detail": "Unauthorized"
                                }
                            }
                        }
                    }
                }
            }
        }
)
@limiter.limit("10/minute")
def get_uptime(request: Request, user_data = get_user_role("user")):
    return get_system_uptime()

@router.get(
        "/system/processes",
        tags=["System"],
        description="Returns a list of currently running processes.",
        responses={
            200: {
                "description": "Process list returned",
                "content": {
                    "application/json": {
                        "examples": {
                            "Success": {
                                "summary": "Process list",
                                "value": [
                                    {"pid": 1, "name": "init"},
                                    {"pid": 123, "name": "python"}
                                ]
                            }
                        }
                    }
                }
            },
            401: {
                "description": "Unauthorized. Invalid API key",
                "content": {
                    "application/json": {
                        "examples": {
                            "Unauthorized": {
                                "summary": "Missing or invalid API key",
                                "value": {
                                    "detail": "Unauthorized"
                                }
                            }
                        }
                    }
                }
            }
        }
)
@limiter.limit("20/minute")
def get_processes(request: Request, user_data = get_user_role("user")):
    processes = list_processes()
    return processes

@router.get(
        "/system/system-infos",
        tags=["System"],
        description="Returns detailed system information including CPU, memory, disk, and OS details.",
        responses={
            200: {
                "description": "System information returned",
                "content": {
                    "application/json": {
                        "examples": {
                            "Success": {
                                "summary": "System info",
                                "value": {
                                    "cpu": "Intel Xeon",
                                    "memory": "16GB",
                                    "disk": "512GB SSD",
                                    "os": "Ubuntu 22.04"
                                }
                            }
                        }
                    }
                }
            },
            401: {
                "description": "Unauthorized. Invalid API key",
                "content": {
                    "application/json": {
                        "examples": {
                            "Unauthorized": {
                                "summary": "Missing or invalid API key",
                                "value": {
                                    "detail": "Unauthorized"
                                }
                            }
                        }
                    }
                }
            }
        }
)
@limiter.limit("10/minute")
def system_infos(request: Request, user_data = get_user_role("user")):
    system_info = get_system_infos()
    return system_info

@router.get(
    "/system/system-user",
    tags=["System"],
    description="Returns information about the current system user.",
    responses={
        200: {
            "description": "System user info returned",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "System user info",
                            "value": {
                                "username": "ubuntu",
                                "uid": 1000
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized. Invalid API key",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "Missing or invalid API key",
                            "value": {
                                "detail": "Unauthorized"
                            }
                        }
                    }
                }
            }
        }
    }
)
@limiter.limit("5/minute")
def system_user_infos(request: Request, username: str, user_data = get_user_role("user")):
    return_code, user_info = get_system_user_infos(username)

    if return_code == True:
        return user_info
    
    elif return_code == None:
        raise HTTPException(status_code=404, detail="User not found on the system")
    
    else:
        raise HTTPException(status_code=500, detail="500 Internal server error")
    

@router.get(
        "/system/avg-load",
        tags=["System"],
        description="Returns system load averages for 1, 5, and 15 minutes.",
        responses={
            200: {
                "description": "System load averages returned",
                "content": {
                    "application/json": {
                        "examples": {
                            "Success": {
                                "summary": "Load averages",
                                "value": {
                                    "load_1min": 0.12,
                                    "load_5min": 0.08,
                                    "load_15min": 0.05
                                }
                            }
                        }
                    }
                }
            },
            401: {
                "description": "Unauthorized. Invalid API key",
                "content": {
                    "application/json": {
                        "examples": {
                            "Unauthorized": {
                                "summary": "Missing or invalid API key",
                                "value": {
                                    "detail": "Unauthorized"
                                }
                            }
                        }
                    }
                }
            }
        }
)
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