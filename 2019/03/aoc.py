#!/usr/bin/python3


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'Point({self.x},{self.y})'

    def __repr__(self):
        return f'Point({self.x},{self.y})'

    def __hash__(self):
        return hash(f'{self}')

    def new_point_from_offset(self, x=0, y=0):
        return Point(x=self.x + x, y=self.y + y)

    def manhattan_distance(self, other_point=None):
        if other_point is None:
            other_point = Point(0, 0)
        return abs(self.x - other_point.x) + abs(self.y - other_point.y)


class Wire:
    def __init__(self):
        self.current_point = Point()
        self.included_points = set()

    @staticmethod
    def xy_delta_from_segment(segment):
        heading = segment[0]
        distance = int(segment[1:])

        x = 0
        y = 0

        if heading == 'U':
            y = distance
        elif heading == 'R':
            x = distance
        elif heading == 'D':
            y = -1 * distance
        elif heading == 'L':
            x = -1 * distance
        else:
            raise Exception(f'Unknown heading {heading} in segment {segment}')

        return x, y

    def update(self, segment):
        x, y = Wire.xy_delta_from_segment(segment)
        next_point = self.current_point.new_point_from_offset(x=x, y=y)

        if x:
            intermediate_points = set(Point(x=_x, y=self.current_point.y)
                                      for _x in range(min(next_point.x, self.current_point.x),
                                                      max(next_point.x, self.current_point.x) + 1))

        elif y:
            intermediate_points = set(Point(x=self.current_point.x, y=_y)
                                      for _y in range(min(next_point.y, self.current_point.y),
                                                      max(next_point.y, self.current_point.y) + 1))
        else:
            raise Exception(f'Unexpectedly stayed at same point during update with segment {segment}')

        self.current_point = next_point
        self.included_points.update(intermediate_points)

    def intersection(self, other_wire):
        intersection = self.included_points.intersection(other_wire.included_points)
        intersection.discard(Point())
        return intersection


def parse_input():
    """
    Parse input.txt to Wire objects
    """

    wires = []

    with open('input.txt', 'r') as txt:
        for segments in txt:
            wire = Wire()
            for segment in segments.strip().split(','):
                wire.update(segment)
            wires.append(wire)

    return wires


def main():
    wires = parse_input()

    intersection = wires[0].intersection(wires[1])

    part_one = min([x.manhattan_distance() for x in intersection])

    print(f'Distance: {part_one}')


if __name__ == '__main__':
    main()
