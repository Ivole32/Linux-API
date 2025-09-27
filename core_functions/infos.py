import subprocess
import platform
import psutil
import pwd
import os

"""from load_monitor import LoadMonitor

monitor = LoadMonitor()
monitor.start()"""

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
            "name": info.get("name"),
            "status": info.get("status"),
            "pid": info.get("pid")
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

def get_system_load():
    load1, load5, load15 = psutil.getloadavg()
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
    return {
        "load_average": {
            "test": monitor.get_last_loads(100)
        }#,
       # "cpu_percent": cpu_percent,
       # "cpu_percent_per_core": cpu_per_core
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
    
def get_service_informations():
    services = {}
    init_dir = "/etc/init.d"
    for service in os.listdir(init_dir):
        path = os.path.join(init_dir, service)
        if os.access(path, os.X_OK):
            try:
                result = subprocess.run([path, "status"], capture_output=True, text=True)
                status = result.stdout.strip() or result.stderr.strip()
                description = ""
                try:
                    with open(path, "r") as f:
                        for line in f:
                            if "Description:" in line:
                                description = line.strip().split("Description:", 1)[-1].strip()
                                break
                except Exception:
                    description = ""
                services[service] = {
                    "status": status,
                    "description": description
                }
            except Exception as e:
                services[service] = {
                    "status": f"Error: {e}",
                    "description": ""
                }
    return services

if __name__ == "__main__":
    """print(get_system_infos())
    print(list_processes())
    while True:
        print("\n\n")
        print(str(get_system_load()))"""
    print(str(get_system_user_infos("ivo")))