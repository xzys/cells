#!/usr/bin/env python
from dataclasses import dataclass
from lib.types import Vector, Sprite

@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    def contains(self, pos: Vector):
        return (pos.x >= self.x and
                pos.x < self.x + self.w and
                pos.y >= self.y and
                pos.y < self.y + self.h)

    def intersects(self, rec):
        return not (
                rec.x >= self.x + self.w or
                rec.x + rec.w < self.x or
                rec.y >= self.y + self.h or
                rec.y + rec.h < self.y)


class Quadtree:
    max_points: int = 4

    def __init__(self, area: Rect, depth: int = 0):
        self.area = area
        self.depth = depth
        self.sprites = []
        # subtrees
        self.divided = False
        self.nw: Quadtree = None
        self.ne: Quadtree = None
        self.sw: Quadtree = None
        self.se: Quadtree = None

    def insert(self, sprite: Sprite):
        """try to insert a point into this quadtree"""
        if not self.area.contains(sprite.position):
            return False

        if len(self.sprites) < self.max_points:
            self.sprites.append(sprite)
            return True

        if not self.divided:
            self.divide()

        return (self.nw.insert(sprite) or
                self.ne.insert(sprite) or
                self.sw.insert(sprite) or
                self.se.insert(sprite))

    def delete(self, sprite: Sprite):
        for i, s in enumerate(self.sprites):
            if s == sprite:
                del self.sprites[i]
                return True

        if self.divided:
            for qt in (self.nw, self.ne, self.se, self.sw):
                if qt.delete(sprite):
                    return True
        return False

    def divide(self):
        """divide into 4 sections"""
        a = self.area
        nw, nh = a.w/2, a.h/2
        self.nw = Quadtree(Rect(a.x,      a.y,      nw, nh), self.depth+1)
        self.ne = Quadtree(Rect(a.x + nw, a.y,      nw, nh), self.depth+1)
        self.sw = Quadtree(Rect(a.x + nw, a.y + nh, nw, nh), self.depth+1)
        self.se = Quadtree(Rect(a.x,      a.y + nh, nw, nh), self.depth+1)
        self.divided = True

    def query(self, pos: Vector, dist: float):
        """return sprites this dist away"""
        boundry = Rect(pos.x - dist, pos.y - dist, pos.x + dist, pos.y + dist) 
        found = []
        self.query_circle(boundry, pos, dist, found)
        return found

    def query_circle(self, boundry: Rect, pos: Vector, dist: float, found: bool):
        if not self.area.intersects(boundry):
            return

        for s in self.sprites:
            if boundry.contains(s.position) and (s.position - pos).magnitude() <= dist:
                found.append(s)

        if self.divided:
            self.nw.query_circle(boundry, pos, dist, found)
            self.ne.query_circle(boundry, pos, dist, found)
            self.sw.query_circle(boundry, pos, dist, found)
            self.se.query_circle(boundry, pos, dist, found)
