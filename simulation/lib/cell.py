from dataclasses import dataclass
from .types import *

class InvalidArgumentsException(Exception):
    pass

@dataclass
class CellInterface:
    size: int = 0
    position: Vector = None
    velocity: Vector = None
    dest: Vector = None
    scan_requested: bool = False
    scan_results = []

    divide_requested: bool = False

    def scan(self):
        """request a scan of this cell's surroundings
        also return results from the last scan"""
        self.scan_requested = True
        return self.scan_results

    def set_destination(self, *args):
        """set a destination for this cell to move to"""
        if len(args) == 1 and type(args[0]) is Vector:
            self.dest = args[0]
        elif len(args) == 2:
            self.dest = Vector(args[0], args[1])
        else:
            raise InvalidArgumentsException('invalid arguments: try doing `cell.destin(x, y) or cell.destination(Vector(x, y))`')

    def divide(self):
        self.divide_requested = True
