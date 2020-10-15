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

DIST_ERROR_MARGIN = 0.1


class Player:
    def __init__(self, script):
        self.cells = []
        self.script = script


class CellController:
    max_accel: float = 10
    drag_coeff: float = 1/10
    size_coeff: float = 1/10

    consume_rate: float = 2
    step_interval_ms: int = 500

    min_size_to_divide: int = 60

    def __init__(self, player: Player, position: lib.types.Vector):
        self.health = 100
        self.size: int = 50
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
        self.process_divide()

    def move(self, delta):
        # apply drag before, so that it's taken into account when getting dest
        # TODO drag should affect based on surface area not volume
        self.velocity *= (1 - self.drag_coeff) * delta

        if self.cell.dest:
            target = self.cell.dest - self.position - self.velocity
            dist = target.magnitude()
            if dist > DIST_ERROR_MARGIN:
                # unit vector
                direction = target / dist
                mass = self.size * self.size_coeff
                # set either max accel, or account for delta and mass
                force = direction * min(self.max_accel, dist * mass)
                self.velocity += force / mass * delta

        self.position += self.velocity * delta

    def consume_nutrients(self, world, time):
        for i, n in enumerate(world.nutrients):
            if (self.position - n.position).magnitude() < DIST_ERROR_MARGIN:
                n.size -= self.consume_rate
                if n.size <= 0:
                    del world.nutrients[i]
                self.size += min(self.consume_rate, self.size)
                break
        
    def process_scan(self, world):
        if self.cell.scan_requested:
            self.cell.scan_results = world.get_nearby(self)
            self.cell.scan_requested = False

    def process_divide(self):
        if self.cell.divide_requested:
            if self.size >= self.min_size_to_divide:
                c = CellController(self.player, self.position.copy())

                # TODO let physics handle repulsion
                angle_divide = math.atan2(self.velocity.y, self.velocity.x)
                repulsion = lib.types.Vector(math.cos(angle_divide), math.sin(angle_divide)) * 10
                c.velocity += repulsion 
                self.player.cells.append(c)

                self.velocity -= repulsion 
                self.size = self.size // 2

                self.cell.divide_requested = False


class World:
    num_initial_food: int = 100
    min_food_size: float = 10
    max_food_size: float = 20
    scan_distance: float = 100

    def __init__(self, width, height, players):
        print('setting up world...')
        self.size = lib.types.Vector(width, height)

        self.nutrients = []
        for i in range(self.num_initial_food):
            self.nutrients.append(lib.types.Nutrient(
                self.random_pos(),
                randint(self.min_food_size, self.max_food_size)
            ))

        self.players = players
        for p in self.players:
            c = CellController(p, self.random_pos())
            p.cells.append(c)

    def random_pos(self):
        return lib.types.Vector(randint(0, self.size.x), randint(0, self.size.y))

    def update(self, time, delta):
        to_process = []
        for p in self.players:
            for c in p.cells:
                if c.step(time):
                    to_process.append(c)
                # move all cells, regardless
                c.move(delta)

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


def run_singleplayer(w, h, script):
    return World(w, h, [Player(script)])


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
