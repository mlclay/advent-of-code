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


def main():
    input_queue = Queue()
    output_queue = Queue()
    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')
    memory_dump = program.dump_memory()

    tractor_beam_effect = {}

    for y in range(0, 50):
        for x in range(0, 50):
            program.load_memory(memory_dump)
            program.queue_input(x)
            program.queue_input(y)
            program.run_to_end()
            output = program.get_output(block=False)
            if output:
                tractor_beam_effect[Point(x, y)] = output
                print(f'#', end='')
            else:
                print(f'.', end='')
        print()

    print(f'Part One: {len(tractor_beam_effect)}')


if __name__ == '__main__':
    main()

