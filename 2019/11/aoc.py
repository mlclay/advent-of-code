#!/usr/bin/python3
from collections import defaultdict
from queue import Queue

from intcode import IntcodeProgram
from exceptions import WaitingForInput, ProgramHalted


BLACK = 0
WHITE = 1


class Point:
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.heading = heading


class Robot:

    TURN_LEFT = 0
    TURN_RIGHT = 1

    HEADING_UP = 0
    HEADING_RIGHT = 1
    HEADING_DOWN = 2
    HEADING_LEFT = 3

    def __init__(self):
        self.position = Point(0, 0, 0)

    def get_grid_pos(self):
        return self.position.x, self.position.y

    def move(self, direction):
        if direction == Robot.TURN_LEFT:
            self.position.heading = (self.position.heading + 3) % 4
        elif direction == Robot.TURN_RIGHT:
            self.position.heading = (self.position.heading + 1) % 4
        else:
            raise Exception(f'Invalid Direction {direction}')

        if self.position.heading == Robot.HEADING_UP:
            self.position.y += 1
        elif self.position.heading == Robot.HEADING_DOWN:
            self.position.y -= 1
        elif self.position.heading == Robot.HEADING_RIGHT:
            self.position.x += 1
        elif self.position.heading == Robot.HEADING_LEFT:
            self.position.x -= 1
        else:
            raise Exception(f'Invalid Heading ... somehow {self.position}')


def start_on_black():
    input_queue = Queue()
    output_queue = Queue()

    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)

    program.initialize_memory_from_file('input.txt')

    input_queue.put(BLACK)

    painting_robot = Robot()
    painted_grid = defaultdict(int)

    while True:
        try:
            program.execute_next()
        except WaitingForInput:
            new_color = output_queue.get()
            direction = output_queue.get()

            painted_grid[painting_robot.get_grid_pos()] = new_color
            painting_robot.move(direction)

            input_queue.put(painted_grid[painting_robot.get_grid_pos()])
        except ProgramHalted:
            print('Program Complete')
            print(f'Painted {len(painted_grid.keys())} tiles at least once')
            break


def start_on_white():
    input_queue = Queue()
    output_queue = Queue()

    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)

    program.initialize_memory_from_file('input.txt')

    input_queue.put(WHITE)

    painting_robot = Robot()
    painted_grid = defaultdict(int)

    while True:
        try:
            program.execute_next()
        except WaitingForInput:
            new_color = output_queue.get()
            direction = output_queue.get()

            painted_grid[painting_robot.get_grid_pos()] = new_color
            painting_robot.move(direction)

            input_queue.put(painted_grid[painting_robot.get_grid_pos()])
        except ProgramHalted:
            break

    grid = [key for key in painted_grid.keys()]
    max_x = max(grid, key=lambda val: val[0])[0]
    max_y = max(grid, key=lambda val: val[1])[1]
    min_x = min(grid, key=lambda val: val[0])[0]
    min_y = min(grid, key=lambda val: val[1])[1]

    for y in range(max_y, min_y - 1, -1):
        for x in range(min_x, max_x + 1):
            print(' ' if painted_grid[(x, y)] == BLACK else '█', end='')
        print()


def main():
    start_on_black()
    start_on_white()


if __name__ == '__main__':
    main()
