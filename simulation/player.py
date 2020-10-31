import time
import math

import lib
import lib.types
import lib.cell

from js import event_service

player_context = {
        k: lib.__dict__[k]
        for k in lib.__all__
}

DIST_ERROR_MARGIN = 1

get_radius = lambda size: math.sqrt(size / math.pi)


class Player:
    def __init__(self, script):
        self.cells = []
        self.script = script


class CellController:
    max_accel: float = 100
    drag_coeff: float = 1/10
    size_coeff: float = 1/10

    consume_rate: float = 2
    step_interval_ms: int = 1000

    min_size_to_divide: int = 60

    def __init__(self,
            player: Player,
            position: lib.types.Vector,
            size: int,
            ):
        # cell is added to list after creation
        self.name = 'Cell {}'.format(len(player.cells))
        self.health = 100
        self.size = size
        self.position = position
        self.velocity = lib.types.Vector(0, 0)
        self.dest = None
        self.cell = lib.cell.CellInterface()
        self.stdout = FileBridge(self)

        self.context = player_context.copy()
        self.context['cell'] = self.cell
        self.context['print'] = self.print

        self.player = player
        self.script = player.script
        self.last_step = 0

    def step(self, time):
        """run player script on interval
        return true if script is run"""
        if time - self.last_step < self.step_interval_ms:
            return False

        self.cell.size = self.size
        self.cell.position = self.position.copy()
        self.cell.velocity = self.velocity.copy()
        exec(self.script, self.context)
        self.last_step = time
        return True

    def process(self, world, time):
        """process inputs from program"""
        self.consume_nutrients(world, time)
        self.process_scan(world)
        self.process_divide(world)

    def consume_nutrients(self, world, time):
        for i, n in enumerate(world.nutrients):
            if ((self.position - n.position).magnitude() <
                get_radius(self.size) + get_radius(n.size) + DIST_ERROR_MARGIN):

                n.size -= self.consume_rate
                if n.size <= 0:
                    del world.nutrients[i]
                self.size += min(self.consume_rate, n.size)
                break
        
    def process_scan(self, world):
        if self.cell.scan_requested:
            self.cell.scan_results = world.get_nearby(self)
            self.cell.scan_requested = False

    def process_divide(self, world):
        if self.cell.divide_requested:
            if self.size >= self.min_size_to_divide:
                new_size = self.size // 2
                self.size = new_size

                c = CellController(self.player, self.position.copy(), new_size)
                world.add_cell(self.player, c)

                self.cell.divide_requested = False

    def print(self, *args, **kwargs):
        """handle printing by pointing stdout at FileBridge"""
        print(*args, **kwargs, file=self.stdout)


class FileBridge:
    """class to act as stdout and stderr"""
    def __init__(self, cell):
        self.buffer = []
        self.cell = cell
        self.ctx = {
                'cell': self.cell.name,
                'ts': time.time()
        }

    def write(self, s):
        self.buffer.append(s)
        l = len(s)
        if l > 0 and s[l-1] == '\n':
            self.flush()

    def flush(self):
        self.ctx['ts'] = time.time()
        msg = ''.join(self.buffer)
        event_service.emit(event_service.events.PRINT, msg, self.ctx)
        # faster way of doing clear()
        self.buffer *= 0
