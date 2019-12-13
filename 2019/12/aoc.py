#!/usr/bin/python3
import re
from functools import reduce
from math import gcd


def lcm(a, b):
    return int(a * b / gcd(a, b))


def lcms(*numbers):
    return reduce(lcm, numbers)


class Point:
    __slots__ = ['x', 'y', 'z']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, int(value))

    def __add__(self, other):
        return Point(x=self.x + other.x,
                     y=self.y + other.y,
                     z=self.z + other.z)

    def __sub__(self, other):
        return Point(x=self.x - other.x,
                     y=self.y - other.y,
                     z=self.z - other.z)

    def __abs__(self):
        return Point(x=abs(self.x), y=abs(self.y), z=abs(self.z))

    def __str__(self):
        return f'<x={self.x:3}, y={self.y:3}, z={self.z:3}>'

    def step_delta(self, other):
        delta = other - self
        return Point(x=(abs(delta.x) / delta.x) if delta.x else 0,
                     y=(abs(delta.y) / delta.y) if delta.y else 0,
                     z=(abs(delta.z) / delta.z) if delta.z else 0)

    @property
    def energy(self):
        _abs = abs(self)
        return _abs.x + _abs.y + _abs.z


class Moon:

    def __init__(self, x, y, z):
        self.position = Point(x=x, y=y, z=z)
        self.velocity = Point(x=0, y=0, z=0)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Moon: ' \
               f'pos={self.position}, ' \
               f'vel={self.velocity}, ' \
               f'kin: {self.kinetic_energy}, ' \
               f'pot: {self.potential_energy}, ' \
               f'tot: {self.total_energy}'

    def calculate_gravity_pull(self, other):
        self.velocity += self.position.step_delta(other.position)
        other.velocity += other.position.step_delta(self.position)

    def apply_velocity(self):
        self.position += self.velocity

    @property
    def potential_energy(self):
        return self.position.energy

    @property
    def kinetic_energy(self):
        return self.velocity.energy

    @property
    def total_energy(self):
        return self.potential_energy * self.kinetic_energy


def parse_input():
    """
    Parse input.txt to Moon instances
    """
    regex = re.compile(r'<x=(?P<x>-?\d+), y=(?P<y>-?\d+), z=(?P<z>-?\d+)>')

    moons = []

    with open('input.txt', 'r') as txt:
        for moon in txt:
            moons.append(Moon(**regex.match(moon).groupdict()))

    return moons


def part_one():
    moons = parse_input()

    for step in range(1, 1001):
        for moon_num, moon in enumerate(moons):
            for next_moon in range(moon_num + 1, len(moons)):
                moon.calculate_gravity_pull(moons[next_moon])
            moon.apply_velocity()

    print(f'After 1000 steps:')
    for moon_num, moon in enumerate(moons):
        print(moon)
    print(f'System Total Energy: {sum([moon.total_energy for moon in moons])}')


def part_two_slow():
    moons = parse_input()
    dimension_steps = {'x': 0, 'y': 0, 'z': 0}

    initial_positions = {
        'x': [moon.position.x for moon in moons],
        'y': [moon.position.y for moon in moons],
        'z': [moon.position.z for moon in moons],
    }
    initial_velocities = {
        'x': [moon.velocity.x for moon in moons],
        'y': [moon.velocity.y for moon in moons],
        'z': [moon.velocity.z for moon in moons],
    }

    found_x_cycle = False
    found_y_cycle = False
    found_z_cycle = False

    while True:
        for moon_num, moon in enumerate(moons):
            for next_moon in range(moon_num + 1, len(moons)):
                moon.velocity += moon.position.step_delta(moons[next_moon].position)
                moons[next_moon].velocity += moons[next_moon].position.step_delta(moon.position)
            moon.apply_velocity()

        if not found_x_cycle:
            dimension_steps['x'] += 1
            if initial_positions['x'] == [moon.position.x for moon in moons] and \
                    initial_velocities['x'] == [moon.velocity.x for moon in moons]:
                found_x_cycle = True

        if not found_y_cycle:
            dimension_steps['y'] += 1
            if initial_positions['y'] == [moon.position.y for moon in moons] and \
                    initial_velocities['y'] == [moon.velocity.y for moon in moons]:
                found_y_cycle = True

        if not found_z_cycle:
            dimension_steps['z'] += 1
            if initial_positions['z'] == [moon.position.z for moon in moons] and \
                    initial_velocities['z'] == [moon.velocity.z for moon in moons]:
                found_z_cycle = True

        if found_x_cycle and found_y_cycle and found_z_cycle:
            break

    print(f'Steps in cycle: {dimension_steps}')
    print(f'LCM: {lcms(*dimension_steps.values())}')


def part_two_fast():
    moons = parse_input()
    dimension_steps = {'x': 0, 'y': 0, 'z': 0}

    initial_positions = {
        'x': [moon.position.x for moon in moons],
        'y': [moon.position.y for moon in moons],
        'z': [moon.position.z for moon in moons],
    }
    initial_velocities = {
        'x': [moon.velocity.x for moon in moons],
        'y': [moon.velocity.y for moon in moons],
        'z': [moon.velocity.z for moon in moons],
    }

    found_x_cycle = False
    found_y_cycle = False
    found_z_cycle = False

    while True:
        for moon_num, moon in enumerate(moons):
            for next_moon in range(moon_num + 1, len(moons)):
                other = moons[next_moon]
                if not found_x_cycle:
                    delta = other.position.x - moon.position.x
                    delta = (abs(delta) / delta) if delta else 0
                    moon.velocity.x += delta
                    other.velocity.x -= delta
                if not found_y_cycle:
                    delta = other.position.y - moon.position.y
                    delta = (abs(delta) / delta) if delta else 0
                    moon.velocity.y += delta
                    other.velocity.y -= delta
                if not found_z_cycle:
                    delta = other.position.z - moon.position.z
                    delta = (abs(delta) / delta) if delta else 0
                    moon.velocity.z += delta
                    other.velocity.z -= delta

            if not found_x_cycle:
                moon.position.x += moon.velocity.x
            if not found_y_cycle:
                moon.position.y += moon.velocity.y
            if not found_z_cycle:
                moon.position.z += moon.velocity.z

        if not found_x_cycle:
            dimension_steps['x'] += 1
            if initial_positions['x'] == [moon.position.x for moon in moons] and \
                    initial_velocities['x'] == [moon.velocity.x for moon in moons]:
                found_x_cycle = True

        if not found_y_cycle:
            dimension_steps['y'] += 1
            if initial_positions['y'] == [moon.position.y for moon in moons] and \
                    initial_velocities['y'] == [moon.velocity.y for moon in moons]:
                found_y_cycle = True

        if not found_z_cycle:
            dimension_steps['z'] += 1
            if initial_positions['z'] == [moon.position.z for moon in moons] and \
                    initial_velocities['z'] == [moon.velocity.z for moon in moons]:
                found_z_cycle = True

        if found_x_cycle and found_y_cycle and found_z_cycle:
            break

    print(f'Steps in cycle: {dimension_steps}')
    print(f'LCM: {lcms(*dimension_steps.values())}')


def main():
    part_one()
    part_two_fast()


if __name__ == '__main__':
    main()
