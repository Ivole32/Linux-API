from pickle import loads
from threading import Thread
import psutil
from time import sleep

class LoadMonitor(Thread):
    def __init__(self):
        super().__init__()
        self.load_per_minute = []

        self._average_cache = None

        self.cpu_load_per_minute = []

        self.running = True

        self.decimal_places = 2

    def run(self):
        while self.running:
            load1, _, _ = psutil.getloadavg()
            self.load_per_minute.append(load1)

            cpu_load = psutil.cpu_percent(interval=1, percpu=True)
            self.cpu_load_per_minute.append(cpu_load)

            self._average_cache = None
            sleep(60)

    def get_last_loads(self, n=None):
        if n is None or n > len(self.load_per_minute):
            n = len(self.load_per_minute)

        return [round(load, self.decimal_places) for load in self.load_per_minute[-n:]]

    def get_average(self, n=None):
        if self._average_cache is not None:
            return self._average_cache

        vals = self.get_last_loads(n)
        if not vals:
            return 0.0

        average = sum(vals) / len(vals)
        average = round(average, self.decimal_places)

        self._average_cache = average
        return average

    def get_average_cpu_load(self) -> None:
        for cpu_load in self.cpu_load_per_minute:
            return round(sum(cpu_load) / len(cpu_load), self.decimal_places)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    monitor = LoadMonitor()
    monitor.start()
    try:
        while True:
            sleep(10)
            print("Last 3 Load-Values:", monitor.get_last_loads(3))
            print("Average (all):", monitor.get_average())
    except KeyboardInterrupt:
        monitor.stop()
        monitor.join()