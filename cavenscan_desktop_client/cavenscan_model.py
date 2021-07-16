from cavenscan_mcu import CavenscanMcu
from cavenscan_stats import CavenscanStats


class CavenscanModel:

    def __init__(self, mcu: CavenscanMcu, from_channel: int = 0, to_channel: int = 127,
                 lines_count: int = 5) -> None:
        self._mcu = mcu
        self._from_channel = from_channel
        self._to_channel = to_channel
        self._lines_count = lines_count
        self.reset()

    def reset(self):
        self._current_line = -1
        self._channels_count = (self.to_channel - self.from_channel + 1)
        self._total_stats: CavenscanStats = CavenscanStats(0, list([0] * self._channels_count))
        self._stats: list[CavenscanStats] = list([CavenscanStats(0, [])] * self._lines_count)

    def clear_stats(self) -> None:
        self.reset()

    def scan(self) -> CavenscanStats:
        stats = self._mcu.scan(self.from_channel, self.to_channel)
        self._current_line = self.next_line
        self._stats[self._current_line] = stats
        self._total_stats.scans_count += stats.scans_count
        for i in range(len(stats.stats)):
            self._total_stats.stats[i] += stats.stats[i]
        return stats

    def save_stats(self, filename: str) -> None:
        print(filename) #todo save as csv

    def get_ports(self) -> list[str]:
        return self._mcu.get_ports()

    @property
    def lines_count(self) -> int:
        return self._lines_count

    @property
    def curr_line(self) -> int:
        return self._current_line

    @property
    def from_channel(self) -> int:
        return self._from_channel

    @property
    def to_channel(self) -> int:
        return self._to_channel

    @property
    def channels_count(self) -> int:
        return self._channels_count

    @property
    def next_line(self) -> int:
        return (self._current_line + 1) % self._lines_count

    def get_total_stats(self) -> CavenscanStats:
        return self._total_stats

    def get_stats(self, line_number: int) -> CavenscanStats:
        return self._stats[line_number]
