#!/usr/bin/python3
from queue import Queue, Empty

from intcode import IntcodeProgram
from exceptions import WaitingForInput, ProgramHalted


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x},{self.y})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(self.__str__())

    def one_north(self):
        return Point(self.x, self.y + 1)

    def one_east(self):
        return Point(self.x + 1, self.y)

    def one_south(self):
        return Point(self.x, self.y - 1)

    def one_west(self):
        return Point(self.x - 1, self.y)

    def get_neighbors(self):
        return [
            self.one_north(),
            self.one_south(),
            self.one_west(),
            self.one_east()
        ]


def run_get_output(program, memory_dump, x, y):
    program.load_memory(memory_dump)
    program.queue_input(x)
    program.queue_input(y)
    program.run_to_end()
    return program.get_output(block=False)


def edge_detector(program, memory_dump, start=0, left_x=0, right_x=0, stop=50):
    """
    Find the edges of the tractor beam funnel.  Start on the outside and walk towards
    the known center of the beam until we have an affected drone (output == 1).  Capture
    that x,y as an edge coordinate.  If our first scan hits in the tractor beam, take a
    small step away from tractor beam center and try again to find the edge
    """
    left_edge_coordinates = [Point(int(left_x), start)]
    right_edge_coordinates = [Point(int(right_x), start)]

    for y in range(start, stop):
        left_test = max(0, left_edge_coordinates[-1].x - 1)
        right_test = right_edge_coordinates[-1].x + 2

        first = True

        while True:
            if left_test > right_test:
                break
            output = run_get_output(program, memory_dump, left_test, y)
            if first and y != 0 and output:
                # We undershot, reset and try again
                left_test = max(0, left_test - 2)
                continue
            if output:
                left_edge_coordinates.append(Point(left_test, y))
                break
            left_test += 1
            first = False

        first = True
        while True:
            if right_test < left_test:
                break
            output = run_get_output(program, memory_dump, right_test, y)
            if first and y != 0 and output:
                # We overshot, reset and try again
                right_test += 2
                continue
            if output:
                right_edge_coordinates.append(Point(right_test, y))
                break
            right_test -= 1
            first = False

    return sorted(set(left_edge_coordinates), key=lambda point: point.y), \
           sorted(set(right_edge_coordinates), key=lambda point: point.y)


def part_one(program, memory_dump):
    left_edge_coordinates, right_edge_coordinates = edge_detector(program, memory_dump)
    tractor_beam_effect = 0

    assert len(left_edge_coordinates) == len(right_edge_coordinates)

    for edges in zip(left_edge_coordinates, right_edge_coordinates):
        tractor_beam_effect += (edges[1].x - edges[0].x) + 1

    print(f'Part One: {tractor_beam_effect}')
    return left_edge_coordinates, right_edge_coordinates


def best_fit_slope_and_intercept(edge_coordinates):
    """
    Calculate m and b from y=mx+b
    """
    count = len(edge_coordinates)

    x_mean = sum([coord.x for coord in edge_coordinates]) / count
    y_mean = sum([coord.y for coord in edge_coordinates]) / count
    xx_mean = sum([coord.x * coord.x for coord in edge_coordinates]) / count
    xy_mean = sum([coord.x * coord.y for coord in edge_coordinates]) / count

    m = (((x_mean * y_mean) - xy_mean) /
         ((x_mean * x_mean) - xx_mean))

    b = y_mean - m * x_mean

    return m, b


def part_two(program, memory_dump, left_edge_coordinates, right_edge_coordinates):
    """
    Calculate best-fit lines for tractor beam edges.  Use those to guess where the beam will be wide enough
    to meet the acceptance criteria.  Do a full edge scan of the target area.  Calculate closest point.
    """

    # Calculate m and b for each edge of the tractor beam funnel
    left_edge_m, left_edge_b = best_fit_slope_and_intercept(left_edge_coordinates)
    right_edge_m, right_edge_b = best_fit_slope_and_intercept(right_edge_coordinates)

    # Use best-fit line to guess where in the y range we need to detect actual edges for calculation
    y = 100
    while True:
        right_x = (y - right_edge_b) / right_edge_m
        left_x = (y + 100 - left_edge_b) / left_edge_m
        if right_x - 100 >= left_x:
            break
        y += 1

    # Best-fit lines gives us an estimate, extend our search range a little
    left_edge_coordinates, right_edge_coordinates = edge_detector(program, memory_dump,
                                                                  start=y - 50,
                                                                  left_x=left_x,
                                                                  right_x=right_x,
                                                                  stop=y + 150)

    # There may be a couple squares that fit on the edges, find the closest
    squares = []
    for right_edge in right_edge_coordinates:
        if Point(right_edge.x - 99, right_edge.y + 99) in left_edge_coordinates:
            squares.append((right_edge.x - 99) * 10000 + right_edge.y)
    print(f'Part Two: {min(squares)}')


def main():
    input_queue = Queue()
    output_queue = Queue()
    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')
    memory_dump = program.dump_memory()

    left_edge_coordinates, right_edge_coordinates = part_one(program, memory_dump)
    part_two(program, memory_dump, left_edge_coordinates, right_edge_coordinates)


if __name__ == '__main__':
    main()
