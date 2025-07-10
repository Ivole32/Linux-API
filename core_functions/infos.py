import platform
import psutil

from load_monitor import LoadMonitor

monitor = LoadMonitor()
monitor.start()

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
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        processes.append(proc.info)
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

if __name__ == "__main__":
    print(get_system_infos())
    print(list_processes())
    while True:
        print("\n\n")
        print(str(get_system_load()))