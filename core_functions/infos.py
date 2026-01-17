import platform
import psutil
import pwd

def get_system_infos():
    system_info = {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total": psutil.virtual_memory().total,
        "disk_total": psutil.disk_usage('/').total,
    }

    return system_info

def list_processes():
    processes = []
    for proc in psutil.process_iter(['status', 'pid', 'name']):
        info = proc.info
        processes.append({
            "pid": info.get("pid"),
            "name": info.get("name"),
            "status": info.get("status")
        })
    return processes

def get_system_uptime():
    import time
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
        "full_seconds": uptime_seconds
    }

def get_system_user_infos(username):
    try:
        user_info = pwd.getpwnam(username)
        return True, {
            username: {
                "user_name" : user_info.pw_name,
                "UID": user_info.pw_uid,
                "GID": user_info.pw_gid,
                "home_dir": user_info.pw_dir,
                "shell": user_info.pw_shell
            }
        }
    except KeyError:
        return None, {}
    except Exception:
        return False, {}