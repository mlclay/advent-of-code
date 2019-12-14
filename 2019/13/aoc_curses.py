#!/usr/bin/python3
import curses
import enum
from queue import Queue, Empty
from time import sleep

from intcode import IntcodeProgram
from exceptions import WaitingForInput, ProgramHalted


class Tile(enum.Enum):
    EMPTY = (0, ' ')
    WALL = (1, '█')
    BLOCK = (2, '#')
    PADDLE = (3, '~')
    BALL = (4, 'o')

    def __new__(cls, value, display):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.display = display
        return obj

    def __str__(self):
        return self.display


def draw_screen(stdscr, tiles):
    score_key = (-1, 0)
    for y in range(0, 23):
        for x in range(0, 43):
            stdscr.addstr(y, x, f'{tiles[(x, y)]}')
    stdscr.addstr(24, 0, f'Score: {(0 if score_key not in tiles else tiles[score_key]):36}')

    stdscr.refresh()


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


def get_key(tiles, val):
    for key, value in tiles.items():
        if val == value:
            return key

    raise Exception(f'Tile {val} missing')


def get_paddle_x(tiles):
    return get_key(tiles, Tile.PADDLE)[0]


def get_ball_x(tiles):
    return get_key(tiles, Tile.BALL)[0]


def main(stdscr):
    automatic = True

    # Clear screen
    stdscr.clear()

    input_queue = Queue()
    output_queue = Queue()

    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')
    program.set_memory_address(0, 2)

    tiles = {}

    while True:
        try:
            program.execute_next()

        except WaitingForInput:
            process_frame(program, tiles)

            draw_screen(stdscr, tiles)

            if automatic:
                sleep(.05)
                paddle = get_paddle_x(tiles)
                ball = get_ball_x(tiles)

                if paddle > ball:
                    program.queue_input(-1)
                elif paddle < ball:
                    program.queue_input(1)
                else:
                    program.queue_input(0)

            else:
                capture_key = stdscr.getch()

                if capture_key == curses.KEY_LEFT:
                    program.queue_input(-1)
                elif capture_key == curses.KEY_RIGHT:
                    program.queue_input(1)
                else:
                    program.queue_input(0)

        except ProgramHalted:
            process_frame(program, tiles)
            break

    draw_screen(stdscr, tiles)

    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)
