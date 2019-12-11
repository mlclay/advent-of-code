#!/usr/bin/python3
import math
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


def part_one(asteroids):
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
    return best_station


def angle_and_distance(origin, point, refvec=(0, -1)):
    """Trig was a long time ago... Borrowed from https://stackoverflow.com/a/41856340"""
    # Vector between point and the origin: v = p - o
    vector = [point[0] - origin[0], point[1] - origin[1]]

    # Length of vector: ||v||
    lenvector = math.hypot(vector[0], vector[1])

    # If length is zero there is no angle
    if lenvector == 0:
        return -math.pi, 0

    # Normalize vector: v/||v||
    normalized = [vector[0] / lenvector, vector[1] / lenvector]
    dotprod = normalized[0] * refvec[0] + normalized[1] * refvec[1]  # x1*x2 + y1*y2
    diffprod = refvec[1] * normalized[0] - refvec[0] * normalized[1]  # x1*y2 - y1*x2
    angle = math.atan2(diffprod, dotprod)

    # Negative angles represent counter-clockwise angles so we need to subtract them
    # from 2*pi (360 degrees)
    if angle <= 0:
        return 2 * math.pi + angle, lenvector

    # I return first the angle because that's the primary sorting criterium
    # but if two vectors have the same angle then the shorter distance should come first.
    return angle, lenvector


def part_two(asteroids, laser):
    angles = {}

    for asteroid in asteroids:
        if laser != asteroid:
            angle, distance = angle_and_distance(laser, asteroid)
            if angle not in angles:
                angles[angle] = []
            angles[angle].append((distance, asteroid))
            angles[angle].sort()

    destroyed = []
    while True:
        keys = sorted(angles.keys(), reverse=True)
        if not keys:
            break
        for key in keys:
            destroyed.append(angles[key].pop(0))
            if not angles[key]:
                del angles[key]

    print(f'200th Destroyed: {destroyed[199]}\t{destroyed[199][1][0] * 100 + destroyed[199][1][1]}')
    return destroyed


def main():
    asteroids = parse_input()

    laser = part_one(asteroids)

    part_two(asteroids, laser)


if __name__ == '__main__':
    main()
