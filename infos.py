import platform
import psutil

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

if __name__ == "__main__":
    print(get_system_infos())