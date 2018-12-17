#!/usr/bin/python
from enum import Enum


class XY:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f'[{self.x}, {self.y}]'


class MineCart(XY):
    def __init__(self, x, y, char):
        super(MineCart, self).__init__(x, y)
        self.heading = MineCart.Heading.from_char(char)
        self.next_turn = -1

    def __str__(self):
        xy = super(MineCart, self).__str__()
        return f'{xy}\tHeading {self.heading}\tNext Int: {self.next_turn}'

    def corner(self, char):
        if (self.heading == MineCart.Heading.NORTH and char == '/') or (
                self.heading == MineCart.Heading.SOUTH and char == '\\'):
            self.heading = MineCart.Heading.EAST
            return

        if (self.heading == MineCart.Heading.SOUTH and char == '/') or (
                self.heading == MineCart.Heading.NORTH and char == '\\'):
            self.heading = MineCart.Heading.WEST
            return

        if (self.heading == MineCart.Heading.EAST and char == '/') or (
                self.heading == MineCart.Heading.WEST and char == '\\'):
            self.heading = MineCart.Heading.NORTH
            return

        if (self.heading == MineCart.Heading.WEST and char == '/') or (
                self.heading == MineCart.Heading.EAST and char == '\\'):
            self.heading = MineCart.Heading.SOUTH
            return

        raise Exception('Invalid Turn')

    def intersection(self):
        self.heading = self.heading + self.next_turn

        self.next_turn = self.next_turn + (1 if self.next_turn < 1 else - 2)

    def move(self, mine_carts, cross_roads):
        old_coordinates = (self.x, self.y)

        if self.heading == MineCart.Heading.NORTH:
            self.y -= 1
        elif self.heading == MineCart.Heading.SOUTH:
            self.y += 1
        elif self.heading == MineCart.Heading.WEST:
            self.x -= 1
        elif self.heading == MineCart.Heading.EAST:
            self.x += 1

        new_coordinates = (self.x, self.y)

        del mine_carts[old_coordinates]

        if new_coordinates in mine_carts.keys():
            raise MineCart.CollisionError(new_coordinates)

        self.handle_cross_roads(cross_roads)

        mine_carts[new_coordinates] = self

    def handle_cross_roads(self, cross_roads):
        if (self.x, self.y) in cross_roads.keys():
            cross_road = cross_roads[(self.x, self.y)]
            if cross_road.turn:
                self.corner(cross_road.turn)
            elif cross_road.intersection:
                self.intersection()

    class Heading(Enum):
        NORTH = 0
        EAST = 1
        SOUTH = 2
        WEST = 3

        def __str__(self):
            return self.name

        def __add__(self, other):
            if not isinstance(other, int):
                raise Exception('Invalid Heading Addition')
            return MineCart.Heading((self.value + other) % 4)

        @staticmethod
        def from_char(char):
            if char == '^':
                return MineCart.Heading.NORTH
            if char == '>':
                return MineCart.Heading.EAST
            if char == 'v':
                return MineCart.Heading.SOUTH
            if char == '<':
                return MineCart.Heading.WEST
            raise Exception('Invalid Heading')

    class CollisionError(Exception):
        def __init__(self, coordinates):
            super(MineCart.CollisionError, self).__init__(f'Collision at [{coordinates[0]},{coordinates[1]}]')
            self.coords = XY(coordinates[0], coordinates[1])


class CrossRoad(XY):
    def __init__(self, x, y, char):
        super(CrossRoad, self).__init__(x, y)
        self.intersection = char == '+'
        self.turn = char if not self.intersection else None

    def __str__(self):
        xy = super(CrossRoad, self).__str__()
        return f'{xy}\tInt? {self.intersection}\tTurn? {self.turn}'


def parse_input():
    """
    Parse input.txt to dictionary of cross roads and mine carts

    :return: cross_roads keyed by coordinates, mine_carts keyed by coordinates
    """

    cross_roads = {}
    mine_carts = {}

    cross_road_chars = ('+', '/', '\\')
    mine_cart_chars = ('^', '>', 'v', '<')

    with open('input.txt', 'r') as txt:
        for y, line in enumerate(txt):

            for cross_road in [CrossRoad(x, y, char) for x, char in enumerate(line) if char in cross_road_chars]:
                cross_roads[(cross_road.x, cross_road.y)] = cross_road

            for cart in [MineCart(x, y, char) for x, char in enumerate(line) if char in mine_cart_chars]:
                mine_carts[(cart.x, cart.y)] = cart

    return cross_roads, mine_carts


def main():
    cross_roads, mine_carts = parse_input()

    try:
        while True:
            for key, value in sorted(mine_carts.items(), key=lambda kv: (kv[0][1], kv[0][0])):
                value.move(mine_carts, cross_roads)
    except MineCart.CollisionError as collision:
        print(f'Collision at {collision.coords}')


if __name__ == '__main__':
    main()
