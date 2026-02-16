import psutil
from time import sleep
from threading import Thread

from api.exeptions.exeptions import NoAverageCpuLoad, NoAverageSystemLoad

class LoadMonitor(Thread):
    def __init__(self):
        # Init Thread superclass
        super().__init__()

        # Data variables
        self.system_load_per_minute = []
        self.cpu_loads_per_minute = []

        # Cache variables
        self._system_load_average_cache = None
        self._cpu_load_average_cache = None

        self.running = True

    def run(self):
        while self.running:
            load1, _, _ = psutil.getloadavg() # Get avg system load for the last one minute
            self.system_load_per_minute.append(load1) # Append avg system load to system load list

            cpu_load = psutil.cpu_percent(interval=1, percpu=False) # Get the cpu load for the last one second
            self.cpu_loads_per_minute.append(cpu_load)

            self.__reset_caches() # Reset all caches to force updating values
            sleep(59) # Getting cpu_load needs 1 second => wait 60 - 1 seconds

    def stop(self):
        self.running = False

    def __reset_caches(self):
        self._system_load_average_cache = None
        self._cpu_load_average_cache = None

    def get_last_system_loads(self, n=None):
        if n is None or n > len(self.system_load_per_minute):
            n = len(self.system_load_per_minute)

        return [load for load in self.system_load_per_minute[-n:]]

    def get_average_system_load(self, n=None):
        if self._system_load_average_cache is not None:
            return self._system_load_average_cache

        vals = self.get_last_system_loads(n)
        if not vals:
            raise NoAverageSystemLoad("get_last_system_loads returned no values")

        average = sum(vals) / len(vals)

        self._system_load_average_cache = average
        return average

    def get_last_cpu_loads(self, n=None):
        if n is None or n > len(self.cpu_loads_per_minute):
            n = len(self.cpu_loads_per_minute)

        return [load / 100 for load in self.cpu_loads_per_minute[-n:]]

    def get_average_cpu_load(self):
        if self._cpu_load_average_cache is not None:
            return self._cpu_load_average_cache
        
        if not self.cpu_loads_per_minute:
            raise NoAverageCpuLoad("cpu_loads_per_minute not set")

        average = sum(self.cpu_loads_per_minute) / len(self.cpu_loads_per_minute)

        self._cpu_load_average_cache = average
        return average

    def is_ready(self) -> bool:
        return self.is_alive() and self.running

# Global singletone instance
load_monitor = LoadMonitor()

# Start singeltone instance
load_monitor.start()