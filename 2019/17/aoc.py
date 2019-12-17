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


def build_scaffolding(program):
    scaffolding = set()
    x = y = 0

    while True:
        try:
            output = program.get_output(block=False)
            character = chr(output)
            print(character, end='')

            if character in ['#', '^', '>', 'v', '<']:
                scaffolding.add(Point(x, y))

            if output == 10:
                x = 0
                y += 1
            else:
                x += 1

        except Empty:
            print('Scaffold Complete')
            break

    return scaffolding


def main():
    input_queue = Queue()
    output_queue = Queue()
    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')
    program.run_to_end()

    scaffolding = build_scaffolding(program)

    alignment_parameters = []

    for scaffold in scaffolding:
        if scaffolding.issuperset(scaffold.get_neighbors()):
            alignment_parameters.append(scaffold.x * scaffold.y)

    print(f'Part One: {sum(alignment_parameters)}')


if __name__ == '__main__':
    main()
