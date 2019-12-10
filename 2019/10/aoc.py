#!/usr/bin/python3
from collections import namedtuple

ASTEROID = '#'
Point = namedtuple('Point', 'x y')


def parse_input():
    """
    Parse input.txt to asteroids
    """

    asteroids = []

    with open('input.txt', 'r') as txt:
        for y_pos, y_row in enumerate(txt):
            for x_pos, space in enumerate(y_row.strip()):
                if space == ASTEROID:
                    asteroids.append(Point(x_pos, y_pos))

    return asteroids


def main():
    asteroids = parse_input()

    best_station = 0
    best_station_los = 0

    for possible_station in asteroids:

        line_of_sight = set()
        for index, asteroid in enumerate(asteroids):
            delta_x = possible_station.x - asteroid.x
            delta_y = possible_station.y - asteroid.y

            if delta_x == delta_y == 0:
                continue

            slope = f'{(delta_y/delta_x):.9f}' if delta_x else 'inf'*4
            slope += f'_{"-" if delta_x < 0 else "+"}_{"-" if delta_y < 0 else "+"}'

            line_of_sight.add(slope)

        if len(line_of_sight) > best_station_los:
            best_station_los = len(line_of_sight)
            best_station = possible_station

    print(f'Best Station: {best_station}\t{best_station_los}')


if __name__ == '__main__':
    main()
