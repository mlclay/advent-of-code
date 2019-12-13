#!/usr/bin/python3
import enum
from collections import defaultdict
from queue import Queue, Empty

from intcode import IntcodeProgram


class Tile(enum.IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4


def main():
    input_queue = Queue()
    output_queue = Queue()

    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')

    program.run_to_end()

    tiles = defaultdict(lambda: Tile.EMPTY)

    while True:
        try:
            x = program.get_output(block=False)
            y = program.get_output(block=False)
            tile = Tile(program.get_output(block=False))
            tiles[tile] += 1
        except Empty:
            break

    print(f'Block Count: {tiles[Tile.BLOCK]}')


if __name__ == '__main__':
    main()
