#!/usr/bin/env python
from random import randint
import time
import math

import lib
import lib.types
import lib.cell

from player import Player, CellController

def run_singleplayer(w, h, script, scene):
    return World(w, h, [Player(script)], scene)

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

    def update_script(self, script):
        """update script; right now assume there's only one player"""
        p = self.players[0]
        p.script = script
        for c in p.cells:
            c.script = script

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
