#!/usr/bin/env python
import random
import time
import math

from lib.types import Vector, Cell, Nutrient
from player import Player, CellController
from quadtree import Quadtree, Rect


def run_singleplayer(world_size, scene):
    return World(world_size, [Player()], scene)


class World:
    food_density: float = 0.0001

    min_food_size: float = 10
    max_food_size: float = 10
    scan_distance: float = 100

    initial_cell_size: int = 50

    def __init__(self, world_size, players, scene):
        print('setting up world...')
        self.size = Vector(world_size, world_size)
        self.scene = scene

        self.nutrients = []
        self.nutrients_qt = Quadtree(Rect(0, 0, world_size, world_size)) 

        num_food = int(world_size**2 * self.food_density)
        for i in range(num_food):
            pos = self.random_pos()
            self.add_nutrient(Nutrient(
                pos,
                random.randint(self.min_food_size, self.max_food_size)
            ))

        self.players = players
        for p in self.players:
            pos = Vector(self.size.x / 2, self.size.y / 2)
            c = CellController(p, pos, self.initial_cell_size)
            self.add_cell(p, c)

    def random_pos(self):
        # return Vector(randint(0, self.size.x), randint(0, self.size.y))
        a = random.random() * 2 * math.pi
        r = self.size.x/2 * math.sqrt(random.random())
        return Vector(self.size.x/2 + r * math.cos(a), self.size.x/2 + r * math.sin(a))

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
        # other_cells = [c for p in self.players for c in p.cells if c is not cell]

        for n in self.nutrients_qt.query(cell.position, self.scan_distance):
            results.append(n)
        return results
        """
        for x in self.nutrients + other_cells:
            dist = (cell.position - x.position).magnitude()
            if dist < self.scan_distance:
                # if player, send a proxy that only has position 
                if type(x) is CellController:
                    results.append((dist, Cell(x.position, x.size)))
                else:
                    results.append((dist, x))
        return [x for dist, x in sorted(results, key=lambda tup: tup[0])]
        """

    def add_nutrient(self, nutrient):
        """add objects to world; sync to js"""
        self.nutrients.append(nutrient)
        self.nutrients_qt.insert(nutrient)
        self.scene.addNutrient(nutrient, len(self.nutrients)-1)

    def del_nutrient(self, nutrient):
        """remove nutrient based on index"""
        self.nutrients_qt.delete(nutrient)
        self.nutrients.remove(nutrient)
        self.scene.delNutrient(nutrient)

    def add_cell(self, player, cell):
        for p in self.players:
            if p is player:
                p.cells.append(cell)
                self.scene.addCell(cell, len(p.cells)-1)
                return
        raise Exception('player not found')

    def update_script(self, script):
        """update script; right now assume there's only one player"""
        p = self.players[0]
        p.script = script


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
