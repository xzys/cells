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
    max_accel: float = 5
    drag_coeff: float = 1/10
    size_coeff: float = 1/10

    consume_rate: float = 1
    max_size: float = 100

    def __init__(self, script):
        self.health = 100
        self.size = 20
        self.position = None
        self.velocity = None
        self.dest = None
        self.cell = lib.cell.CellInterface()

        self.script = script

        self.context = player_context.copy()
        self.context['cell'] = self.cell

    def step(self):
        self.cell.position = self.position.copy()
        self.cell.velocity = self.velocity.copy()
        exec(self.script, self.context)

    def process(self, world, delta):
        """process inputs from program"""
        self.process_scan(world)
        self.consume_nutrients(world)
        self.move(delta)

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

    def process_scan(self, nearby):
        if self.cell.scan_requested:
            self.cell.scan_results = world.get_nearby(self)
            self.cell.scan_requested = False

    def consume_nutrients(self, world):
        for i, f in enumerate(world.foods):
            if (self.position - f.position).magnitude() < DIST_ERROR_MARGIN:
                if self.size >= self.max_size:
                    return

                f.size -= self.consume_rate
                if f.size <= 0:
                    del world.foods[i]
                self.size += min(self.consume_rate, self.size)
                print('eating!', self.size)
                break
        

class World:
    size = lib.types.Vector(100, 100)
    num_initial_food: int = 100
    max_food_size: float = 20
    scan_distance: float = 25

    @classmethod
    def random_pos(cls):
        return lib.types.Vector(randint(0, cls.size.x), randint(0, cls.size.y))

    @classmethod
    def place_initial_food(cls):
        foods = []
        for i in range(cls.num_initial_food):
            foods.append(lib.types.Nutrient(cls.random_pos(), randint(0, cls.max_food_size)))
        return foods

    def __init__(self, players):
        self.foods = self.place_initial_food()

        self.players = players
        for p in self.players:
            p.position = self.random_pos()
            p.velocity = lib.types.Vector(0, 0)

    def update(self, delta):
        for p in self.players:
            p.step()

        for p in self.players:
            p.process(self, delta)

    def get_nearby(self, player):
        results = []
        other_players = [p for p in self.players if p is not player]
        for x in self.foods + other_players:
            dist = (player.position - x.position).magnitude()
            if dist < self.scan_distance:
                # if player, send a proxy that only has position 
                if type(x) is Player:
                    results.append((dist, lib.types.Robot(x.position, x.size)))
                else:
                    results.append((dist, x))
        return [x for dist, x in sorted(results, key=lambda tup: tup[0])]


if __name__ == '__main__':
    print('running in python mode')
    import os
    players = []

    PLAYERS_DIR = './players'
    files = [fn for fn in os.listdir(PLAYERS_DIR) if fn.endswith('.py')]
    for fn in files:
        with open(os.path.join(PLAYERS_DIR, fn)) as f:
            players.append(Player(f.read()))
    
    print('setting up world...')
    world = World(players)
    while True:
        world.update(0.6)
        time.sleep(0.1)
