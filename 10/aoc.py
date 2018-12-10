#!/usr/bin/python
import re
from collections import defaultdict


class XY:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f'[{self.x}, {self.y}]'

    def __add__(self, other):
        return XY(x=(self.x + other.x),
                  y=(self.y + other.y))


class Star:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def __str__(self):
        return f'Position {self.position} \tVelocity {self.velocity}'

    def move(self):
        self.position = self.position + self.velocity

    def plot(self, sky):
        sky[self.position.x][self.position.y] = '#'


def parse_input():
    """
    Parse input.txt to list of tuple(player count, final marble)

    :return: list of tuples
    """

    stars = []

    with open('input.txt', 'r') as txt:
        for line in txt:
            # position=< 9,  1> velocity=< 0,  2>
            match = re.findall(r'(-?\d+)', line.strip())
            position = XY(x=match[0], y=match[1])
            velocity = XY(x=match[2], y=match[3])
            stars.append(Star(position=position, velocity=velocity))

    return stars


def main():
    stars = parse_input()

    def empty_sky():
        return '.'

    for count in range(0, 15000):
        sky = defaultdict(lambda: defaultdict(empty_sky))

        for star in stars:
            star.plot(sky)

        min_x = min(sky.keys()) - 1
        max_x = max(sky.keys()) + 2
        min_y = min([min(list(x.keys())) for x in sky.values()]) - 1
        max_y = max([max(list(x.keys())) for x in sky.values()]) + 2

        if (max_y - min_y) < 13:
            print(f'ITERATION {count}')

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    print(sky[x][y], end='')
                print()

        for star in stars:
            star.move()


if __name__ == '__main__':
    main()
