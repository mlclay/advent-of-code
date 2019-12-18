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


def draw_camera_image(image_data):
    newline = image_data.index(10)
    y = 0
    while newline > 0:
        line = image_data[:newline]
        print(''.join([chr(x) for x in line]))
        image_data = image_data[newline + 1:]
        newline = image_data.index(10)
        y += 1


def drive_around(program, draw=False):
    """
    A     L,12,L,8,L,8,
    B     L,12,R,4,L,12,R,6,
    A     L,12,L,8,L,8,
    C     R,4,L,12,L,12,R,6,
    B     L,12,R,4,L,12,R,6,
    A     L,12,L,8,L,8,
    C     R,4,L,12,L,12,R,6,
    A     L,12,L,8,L,8,
    C     R,4,L,12,L,12,R,6,
    B     L,12,R,4,L,12,R,6
    """

    main_routine = 'A,B,A,C,B,A,C,A,C,B'
    routine_a = 'L,12,L,8,L,8'
    routine_b = 'L,12,R,4,L,12,R,6'
    routine_c = 'R,4,L,12,L,12,R,6'
    visualize = 'n'

    for input_data in [main_routine, routine_a, routine_b, routine_c, visualize]:
        for character in input_data:
            program.queue_input(ord(character))
        program.queue_input(10)

    image_data = []

    while True:
        try:
            program.execute_next()
            try:
                output = program.get_output(block=False)
                if output > 255:
                    print(f'Part Two: {output}')
                elif draw:
                    image_data.append(output)
                    if image_data[-1] == image_data[-2] == 10:
                        draw_camera_image(image_data)
                        image_data = []
            except IndexError:
                pass
            except Empty:
                pass

        except ProgramHalted:
            print('Program Complete')
            break


def main():
    input_queue = Queue()
    output_queue = Queue()
    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')
    memory_dump = program.dump_memory()
    program.run_to_end()

    scaffolding = build_scaffolding(program)

    alignment_parameters = []

    for scaffold in scaffolding:
        if scaffolding.issuperset(scaffold.get_neighbors()):
            alignment_parameters.append(scaffold.x * scaffold.y)

    print(f'Part One: {sum(alignment_parameters)}')

    program.load_memory(memory_dump)
    program.set_memory_address(0, 2)

    drive_around(program)


if __name__ == '__main__':
    main()

