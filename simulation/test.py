#!/usr/bin/env python
import sys

class FakeFile:
    def __init__(self):
        self.buffer = []

    def write(self, s):
        self.buffer.append(s)
        if s[len(s)-1] == '\n':
            self.flush()

    def flush(self):
        print('OK', ''.join(self.buffer), end='')
        self.buffer *= 0 # faster way of doing clear()

class Printer:
    def __init__(self):
        self.log = FakeFile()

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.log)

p = Printer()
p.print('hey', 123, [1,3,4])
p.print('hey', 123, [1,3,124])
p.print('')
