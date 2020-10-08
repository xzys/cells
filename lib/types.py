#!/usr/bin/env python
from dataclasses import dataclass
import math


@dataclass
class Vector:
    x: int
    y: int

    def __eq__(self, v):
        return self.x == v.x and self.y == v.y 

    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y)

    def __mul__(self, c):
        return Vector(self.x * c, self.y * c)

    def __truediv__(self, c):
        return Vector(self.x / c, self.y / c)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def copy(self):
        return Vector(self.x, self.y)


@dataclass
class Nutrient:
    position: Vector
    size: int


@dataclass
class Cell:
    position: Vector
    size: int
