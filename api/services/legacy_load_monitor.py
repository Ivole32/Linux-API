import psutil
from time import sleep
from threading import Thread

class LegacyLoadMonitor(Thread):
    def __init__(self):
        super().__init__()
        self.system_load_per_minute = []
        self._system_load_average_cache = None

        self.cpu_loads_per_minute = []
        self._cpu_load_average_cache = None

        self.__decimal_places = 2

        self.running = True

    def run(self):
        while self.running:
            load1, _, _ = psutil.getloadavg()
            self.system_load_per_minute.append(load1)

            cpu_load = psutil.cpu_percent(interval=1, percpu=False)
            self.cpu_loads_per_minute.append(cpu_load)

            self.__reset_caches()
            sleep(60)

    def stop(self):
        self.running = False

    def __reset_caches(self):
        self._system_load_average_cache = None
        self._cpu_load_average_cache = None

    def set_decimal_place_value(self, decimal_places):
        self.__decimal_places = decimal_places
        self.__reset_caches()

    def get_last_system_loads(self, n=None):
        if n is None or n > len(self.system_load_per_minute):
            n = len(self.system_load_per_minute)

        return [round(load, self.__decimal_places) for load in self.system_load_per_minute[-n:]]

    def get_average_system_load(self, n=None):
        if self._system_load_average_cache is not None:
            return self._system_load_average_cache

        vals = self.get_last_system_loads(n)
        if not vals:
            return 0.0

        average = sum(vals) / len(vals)
        average = round(average, self.__decimal_places)

        self._system_load_average_cache = average
        return average

    def get_last_cpu_loads(self, n=None):
        if n is None or n > len(self.cpu_loads_per_minute):
            n = len(self.cpu_loads_per_minute)

        return [round(load / 100, self.__decimal_places) for load in self.cpu_loads_per_minute[-n:]]

    def get_average_cpu_load(self):
        if self._cpu_load_average_cache is not None:
            return self._cpu_load_average_cache
        
        if not self.cpu_loads_per_minute:
            return 0.0

        average = sum(self.cpu_loads_per_minute) / len(self.cpu_loads_per_minute)
        average = round(average / 100, self.__decimal_places)

        self._cpu_load_average_cache = average
        return average

if __name__ == "__main__":
    monitor = LegacyLoadMonitor()
    monitor.start()
    try:
        while True:
            sleep(10)
            print("Last 3 Load-Values:", monitor.get_last_system_loads(3))
            print("Average (all):", monitor.get_average_system_load())
            print("Average CPU Load:", monitor.get_average_cpu_load())
    except KeyboardInterrupt:
        monitor.stop()
        monitor.join()