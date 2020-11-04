import time
import sys
import math
import traceback
from js import console

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
    def __init__(self, script=''):
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
        self.player = player
        # cell is added to list after creation, so don't have to do -1
        self.name = 'Cell {}'.format(len(player.cells))
        self.size = size
        self.position = position
        self.velocity = lib.types.Vector(0, 0)
        self.dest = None
        self.cell = lib.cell.CellInterface()
        self.stdout = FileBridge(self)

        self.last_step = 0
        self.context = player_context.copy()
        self.context['cell'] = self.cell
        self.context['print'] = self.print

    def step(self, time):
        """run player script on interval
        return true if script is run"""
        if time - self.last_step < self.step_interval_ms:
            return False

        self.cell.size = self.size
        self.cell.position = self.position.copy()
        self.cell.velocity = self.velocity.copy()
        self.last_step = time

        try:
            exec(self.player.script, self.context)
        except Exception as e:
            cls, exc, tb = sys.exc_info()
            ss = traceback.extract_tb(tb)

            line_number: int = 0
            if cls is SyntaxError:
                line_number = e.lineno
            else:
                line_number = ss[-1].lineno

            # strip out the first stack frame since that is our code
            lines = traceback.format_exception(cls, exc, tb.tb_next)
            msg = ''.join(lines).strip()
            # send error event to 
            event_service.emit(event_service.events.ERROR, msg, {
                'cell': self.name,
                'line': line_number,
                })

        return True

    def process(self, world, time):
        """process inputs from program"""
        self.consume_nutrients(world, time)
        self.process_scan(world)
        self.process_divide(world)

    def consume_nutrients(self, world, time):
        dist = get_radius(self.size) + get_radius(world.max_food_size) + DIST_ERROR_MARGIN
        for n in world.nutrients_qt.query(self.position, dist):
            n.size -= self.consume_rate
            if n.size <= 0:
                world.del_nutrient(n)
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

    def write(self, s):
        self.buffer.append(s)
        l = len(s)
        if l > 0 and s[l-1] == '\n':
            self.flush()

    def flush(self):
        msg = ''.join(self.buffer)
        event_service.emit(event_service.events.PRINT, msg, {
                'cell': self.cell.name,
                'ts': time.time(),
                })
        # faster way of doing clear()
        self.buffer *= 0
