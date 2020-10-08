from dataclasses import dataclass
from .types import *

@dataclass
class CellInterface:
    position: Vector = None
    velocity: Vector = None
    dest: Vector = None
    scan_requested: bool = False
    scan_results = []

    def scan(self):
        self.scan_requested = True
        return self.scan_results

    def set_destination(self, pos: Vector):
        self.dest = pos
