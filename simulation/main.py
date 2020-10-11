#!/usr/bin/env python
from random import randint
import time

import lib
import lib.types
import lib.cell


player_context = {
        k: lib.__dict__[k]
        for k in lib.__all__
}

DIST_ERROR_MARGIN = 0.1


class Player:
    max_accel: float = 10
    drag_coeff: float = 1/10
    size_coeff: float = 1/10

    consume_rate: float = 2
    step_interval_ms: int = 1000

    def __init__(self, script):
        self.health = 100
        self.size = 50
        self.position = None
        self.velocity = None
        self.dest = None
        self.cell = lib.cell.CellInterface()

        self.context = player_context.copy()
        self.context['cell'] = self.cell

        self.script = script
        self.last_step = 0

    def step(self, time):
        """run player script on interval
        return true if script is run"""
        if time - self.last_step < self.step_interval_ms:
            return False

        self.cell.position = self.position.copy()
        self.cell.velocity = self.velocity.copy()
        exec(self.script, self.context)
        self.last_step = time
        return True

    def process(self, world, time):
        """process inputs from program"""
        self.process_scan(world)
        self.consume_nutrients(world, time)

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

    def process_scan(self, world):
        if self.cell.scan_requested:
            self.cell.scan_results = world.get_nearby(self)
            self.cell.scan_requested = False

    def consume_nutrients(self, world, time):
        for i, f in enumerate(world.nutrients):
            if (self.position - f.position).magnitude() < DIST_ERROR_MARGIN:
                f.size -= self.consume_rate
                if f.size <= 0:
                    del world.nutrients[i]
                self.size += min(self.consume_rate, self.size)
                print('eating!', self.size)
                break
        

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
            p.position = self.random_pos()
            p.velocity = lib.types.Vector(0, 0)

    def random_pos(self):
        return lib.types.Vector(randint(0, self.size.x), randint(0, self.size.y))

    def update(self, time, delta):
        to_process = []
        for p in self.players:
            if p.step(time):
                to_process.append(p)
            # move all cells, regardless
            p.move(delta)
        # process all cells that got run
        for p in to_process:
            p.process(self, time)

    def get_nearby(self, player):
        results = []
        other_players = [p for p in self.players if p is not player]
        for x in self.nutrients + other_players:
            dist = (player.position - x.position).magnitude()
            if dist < self.scan_distance:
                # if player, send a proxy that only has position 
                if type(x) is Player:
                    results.append((dist, lib.types.Robot(x.position, x.size)))
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
    
    world = World(players)
    while True:
        world.update(0.6)
        time.sleep(0.1)
