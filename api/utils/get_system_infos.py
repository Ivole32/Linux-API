import platform
import psutil
import pwd
import time
from typing import Dict, List, Tuple, Optional, Any


def get_system_infos() -> Dict[str, Any]:
    """
    Collects basic system information.

    Returns:
        dict: A dictionary containing general system information such as
        OS details, CPU count, total memory, and total disk space.
    """
    return {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total": psutil.virtual_memory().total,
        "disk_total": psutil.disk_usage("/").total,
    }


def list_processes() -> List[Dict[str, Optional[str]]]:
    """
    Lists running system processes.

    Returns:
        list: A list of dictionaries, each containing:
        - pid (int): Process ID
        - name (str): Process name
        - status (str): Current process status
    """
    processes = []

    for proc in psutil.process_iter(["pid", "name", "status"]):
        info = proc.info
        processes.append({
            "pid": info.get("pid"),
            "name": info.get("name"),
            "status": info.get("status"),
        })

    return processes


def get_system_uptime() -> Dict[str, int]:
    """
    Calculates the system uptime.

    Returns:
        dict: Uptime information split into days, hours, minutes,
        seconds, and total uptime in seconds.
    """
    boot_time = psutil.boot_time()
    now = time.time()
    uptime_seconds = int(now - boot_time)

    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "full_seconds": uptime_seconds,
    }


def get_system_user_infos(username: str) -> Tuple[Optional[bool], Dict[str, Dict[str, Any]]]:
    """
    Retrieves system user information for a given username.

    Args:
        username (str): The system username to look up.

    Returns:
        tuple:
        - True and user info dict if the user exists
        - None and empty dict if the user was not found
        - False and empty dict if an unexpected error occurred
    """
    try:
        user_info = pwd.getpwnam(username)

        return True, {
            username: {
                "user_name": user_info.pw_name,
                "uid": user_info.pw_uid,
                "gid": user_info.pw_gid,
                "home_dir": user_info.pw_dir,
                "shell": user_info.pw_shell,
            }
        }

    except KeyError:
        # User does not exist
        return None, {}

    except Exception:
        # Unexpected error
        return False, {}