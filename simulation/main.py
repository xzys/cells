#!/usr/bin/env python
from random import randint
import time
import math

import lib
import lib.types
import lib.cell


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
    step_interval_ms: int = 500

    min_size_to_divide: int = 60

    def __init__(self, player: Player, position: lib.types.Vector, size: int):
        self.health = 100
        self.size = size
        self.position = position
        self.velocity = lib.types.Vector(0, 0)
        self.dest = None
        self.cell = lib.cell.CellInterface()

        self.context = player_context.copy()
        self.context['cell'] = self.cell

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

class World:
    num_initial_food: int = 100
    min_food_size: float = 10
    max_food_size: float = 10
    scan_distance: float = 400

    initial_cell_size: int = 50

    def __init__(self, width, height, players, scene):
        print('setting up world...')
        self.size = lib.types.Vector(width, height)
        self.scene = scene

        self.nutrients = []
        for i in range(self.num_initial_food):
            self.add_nutriend(lib.types.Nutrient(
                self.random_pos(),
                randint(self.min_food_size, self.max_food_size)
            ))

        self.players = players
        for p in self.players:
            c = CellController(p, self.random_pos(), self.initial_cell_size)
            self.add_cell(p, c)

    def random_pos(self):
        return lib.types.Vector(randint(0, self.size.x), randint(0, self.size.y))

    def update(self, time, delta):
        to_process = []
        for p in self.players:
            for c in p.cells:
                if c.step(time):
                    to_process.append(c)

        # process all cells that got run
        for c in to_process:
            c.process(self, time)

    def get_nearby(self, cell):
        results = []
        other_cells = [c for p in self.players for c in p.cells if c is not cell]
        for x in self.nutrients + other_cells:
            dist = (cell.position - x.position).magnitude()
            if dist < self.scan_distance:
                # if player, send a proxy that only has position 
                if type(x) is CellController:
                    results.append((dist, lib.types.Cell(x.position, x.size)))
                else:
                    results.append((dist, x))
        return [x for dist, x in sorted(results, key=lambda tup: tup[0])]

    """add objects to world; sync to js"""
    def add_nutriend(self, nutrient):
        self.nutrients.append(nutrient)
        self.scene.addNutrient(nutrient)

    def add_cell(self, player, cell):
        for p in self.players:
            if p is player:
                p.cells.append(cell)
                self.scene.addCell(cell)
                return
        raise Exception('player not found')


def run_singleplayer(w, h, script, scene):
    return World(w, h, [Player(script)], scene)


if __name__ == '__main__':
    print('running in python mode')
    import os
    players = []

    PLAYERS_DIR = './players'
    files = [fn for fn in os.listdir(PLAYERS_DIR) if fn.endswith('.py')]
    for fn in files:
        with open(os.path.join(PLAYERS_DIR, fn)) as f:
            players.append(Player(f.read()))
    
    world = World(100, 100, players)
    t = time.time()
    delta = 1000
    while True:
        world.update(t, delta/100)
        time.sleep(delta/1000)
        t += delta
