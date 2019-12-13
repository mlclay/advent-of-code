#!/usr/bin/python3
import enum
from collections import defaultdict
from queue import Queue, Empty

from intcode import IntcodeProgram
from exceptions import WaitingForInput, ProgramHalted


class Tile(enum.Enum):
    EMPTY = (0, ' ')
    WALL = (1, '█')
    BLOCK = (2, '#')
    PADDLE = (3, '_')
    BALL = (4, 'o')

    def __new__(cls, value, display):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.display = display
        return obj

    def __str__(self):
        return self.display


def draw_screen(tiles):
    score_key = (-1, 0)
    print(f'Score: {(0 if score_key not in tiles else tiles[score_key]):36}')
    for y in range(0, 23):
        for x in range(0, 43):
            print(tiles[(x, y)], end='')
        print()


def get_key(tiles, val):
    for key, value in tiles.items():
        if val == value:
            return key

    raise Exception(f'Tile {val} missing')


def get_paddle_x(tiles):
    return get_key(tiles, Tile.PADDLE)[0]


def get_ball_x(tiles):
    return get_key(tiles, Tile.BALL)[0]


def process_frame(program, tiles):
    while True:
        try:
            x = program.get_output(block=False)
            y = program.get_output(block=False)

            if (x, y) == (-1, 0):
                tiles[(x, y)] = program.get_output(block=False)  # score
            else:
                tiles[(x, y)] = Tile(program.get_output(block=False))
        except Empty:
            break


def main():
    input_queue = Queue()
    output_queue = Queue()

    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')
    arcade_data = program.dump_memory()

    program.run_to_end()

    tiles = defaultdict(int)

    while True:
        try:
            x = program.get_output(block=False)
            y = program.get_output(block=False)
            tile = Tile(program.get_output(block=False))
            tiles[tile] += 1
        except Empty:
            break

    print(f'Block Count: {tiles[Tile.BLOCK]}')

    program.load_memory(arcade_data)
    program.set_memory_address(0, 2)

    tiles = {}

    while True:
        try:
            program.execute_next()

        except WaitingForInput:
            process_frame(program, tiles)

            # draw_screen(tiles)

            paddle = get_paddle_x(tiles)
            ball = get_ball_x(tiles)

            if paddle > ball:
                program.queue_input(-1)
            elif paddle < ball:
                program.queue_input(1)
            else:
                program.queue_input(0)

        except ProgramHalted:
            print('Program Complete')
            process_frame(program, tiles)
            break

    draw_screen(tiles)
    print(f'Final Score: {tiles[(-1, 0)]}')


if __name__ == '__main__':
    main()
