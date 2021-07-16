import random
from abc import abstractmethod, ABC
from time import sleep
from cavenscan_stats import CavenscanStats


class CavenscanMcu(ABC):

    def __init__(self):
        self._port: str = None

    @abstractmethod
    def scan(self, from_channel: int, to_channel: int) -> CavenscanStats:
        pass

    @abstractmethod
    def get_ports(self) -> list[str]:
        pass

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port


class CavenscanMcuEmulator(CavenscanMcu):

    def scan(self, from_channel: int, to_channel: int) -> CavenscanStats:
        sleep(0.25)
        data = []
        scans = random.randint(80, 100)
        for i in range(from_channel, to_channel + 1):
            if 10 < i < 15:
                val = int(abs(random.gauss(0, 7)))
            else:
                val = int(abs(random.gauss(0, 0.5)))

            data.append(scans if val > scans else val)
        return CavenscanStats(scans, data)

    def get_ports(self) -> list[str]:
        return ['COM1', 'COM2', 'COM3']
