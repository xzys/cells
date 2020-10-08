#!/usr/bin/env python
from random import randint
import importlib
import os
import time

import lib
import lib.types
import lib.cell


PLAYERS_DIR = './players'

player_context = {
        k: lib.__dict__[k]
        for k in lib.__all__
}


class Player:
    max_accel: float = 5
    drag_coeff: float = 1/10
    size_coeff: float = 1/10

    consume_rate: float = 2
    max_size: float = 100

    def __init__(self, filename):
        self.health = 100
        self.size = 20
        self.position = None
        self.velocity = None
        self.dest = None
        self.cell = lib.cell.CellInterface()

        with open(filename) as f:
            self.script = f.read()

        self.context = player_context.copy()
        self.context['cell'] = self.cell

    def step(self):
        self.cell.position = self.position.copy()
        self.cell.velocity = self.velocity.copy()
        exec(self.script, self.context)

    def process(self, world):
        """process inputs from program"""
        self.move()
        self.process_scan(world)
        self.consume_nutrients(world)

    def move(self):
        # apply drag before, so that it's taken into account when getting dest
        # TODO drag should affect based on surface area not volume
        self.velocity *= 1 - self.drag_coeff
        self.velocity *= 1/(self.size * self.size_coeff)

        if self.cell.dest:
            target = self.cell.dest - self.position - self.velocity
            dist = target.magnitude()
            # set acceleration
            accel = target * min(self.max_accel / dist if dist > 0 else 0, 1)
            # print('accel', accel, accel.magnitude())
            self.velocity += accel 

        self.position += self.velocity

    def process_scan(self, nearby):
        if self.cell.scan_requested:
            self.cell.scan_results = world.get_nearby(self)
            self.cell.scan_requested = False

    def consume_nutrients(self, world):
        for i, f in enumerate(world.foods):
            if f.position == self.position:
                if self.size >= self.max_size:
                    return

                f.size -= self.consume_rate
                if f.size <= 0:
                    del world.foods[i]
                self.size += min(self.consume_rate, self.size)
                print('eating!', self.size)
                break
        


def find_players():
    players = []
    files = [fn for fn in os.listdir(PLAYERS_DIR) if fn.endswith('.py')]
    for fn in files:
        players.append(Player(os.path.join(PLAYERS_DIR, fn)))
    return players


class World:
    size = lib.types.Vector(100, 100)
    num_initial_food: int = 100
    max_food_size: float = 30
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
        self.players = players
        self.foods = self.place_initial_food()

    def start(self):
        print('starting world...')
        for p in self.players:
            p.position = self.random_pos()
            p.velocity = lib.types.Vector(0, 0)
        self.run()

    def run(self):
        while True:
            for p in self.players:
                p.step()

            for p in self.players:
                p.process(self)

            time.sleep(0.2)
    
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
    players = find_players()
    
    world = World(players)
    world.start()
