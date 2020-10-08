from dataclasses import dataclass

@dataclass
class CellInterface:
    position = None
    velocity = None
    dest = None
    scan_requested = False
    scan_results = []

    def scan(self):
        self.scan_requested = True
        return self.scan_results

    def set_destination(self, pos):
        self.dest = pos
