#!/usr/bin/python3


class SpaceObject:
    def __init__(self, name):
        self.name = name
        self.orbits = None
        self.orbited_by = []

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, SpaceObject):
            return self.name == other.name
        raise NotImplementedError

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.name} orbits {self.orbits.name if self.orbits else None};'

    def get_depth_to(self, other):
        return 0 if other == self else self.orbits.get_depth_to(other) + 1

    def get_orbits_list_to(self, other):
        if self.orbits != other:
            return [self.orbits.name] + self.orbits.get_orbits_list_to(other)
        return [self.orbits.name]


def parse_input():
    """
    Parse input.txt to Wire objects
    """

    space_objects = []

    with open('input.txt', 'r') as txt:
        for local_orbit in txt:
            center, orbiter = local_orbit.strip().split(')')

            try:
                orbiter = space_objects[space_objects.index(orbiter)]
                if orbiter.orbits:
                    raise Exception(f'{orbiter} already in orbit!')
            except ValueError:
                orbiter = SpaceObject(orbiter)
                space_objects.append(orbiter)

            try:
                center = space_objects[space_objects.index(center)]
            except ValueError:
                center = SpaceObject(center)
                space_objects.append(center)

            center.orbited_by.append(orbiter)
            orbiter.orbits = center

    return space_objects


def main():
    space_objects = parse_input()

    indirect_orbits = 0
    for space_object in space_objects:
        indirect_orbits += space_object.get_depth_to('COM')

    print(f'Part One: {indirect_orbits}')

    you = space_objects[space_objects.index('YOU')]
    san = space_objects[space_objects.index('SAN')]

    you_orbits = set(you.get_orbits_list_to('COM'))
    san_orbits = set(san.get_orbits_list_to('COM'))

    print(f'Part Two: {len(you_orbits.symmetric_difference(san_orbits))}')


if __name__ == '__main__':
    main()
