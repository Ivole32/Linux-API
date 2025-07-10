from threading import Thread
import psutil
from time import sleep

class LoadMonitor(Thread):
    def __init__(self):
        super().__init__()
        self.load_per_minute = []
        self.running = True

    def run(self):
        while self.running:
            load1, _, _ = psutil.getloadavg()
            self.load_per_minute.append(load1)
            sleep(60)

    def get_last_loads(self, n=None):
        if n is None or n > len(self.load_per_minute):
            n = len(self.load_per_minute)
        return self.load_per_minute[-n:]

    def get_average(self, n=None):
        vals = self.get_last_loads(n)
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    monitor = LoadMonitor()
    monitor.start()
    try:
        while True:
            sleep(10)
            print("Letzte 3 Load-Werte:", monitor.get_last_loads(3))
            print("Durchschnitt (alle):", monitor.get_average())
    except KeyboardInterrupt:
        monitor.stop()
        monitor.join()