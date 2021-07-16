from dataclasses import dataclass


@dataclass
class CavenscanStats:
    """Scan statistics"""
    scans_count: int
    stats: list[int]
