#!/usr/bin/python3
import curses
import enum
from collections import defaultdict
from queue import Queue

from intcode import IntcodeProgram
from exceptions import WaitingForInput, ProgramHalted


class Tile(enum.Enum):
    UNKNOWN = (-1, ' ')
    WALL = (0, '█')
    TRAVERSABLE = (1, '.')
    O2_SYSTEM = (2, 'O')

    def __new__(cls, value, display):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.display = display
        return obj

    def __str__(self):
        return self.display


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


class Movement:
    EAST = 4
    WEST = 3
    SOUTH = 2
    NORTH = 1

    @staticmethod
    def inverse(movement):
        if movement == Movement.NORTH:
            return Movement.SOUTH
        if movement == Movement.SOUTH:
            return Movement.NORTH
        if movement == Movement.EAST:
            return Movement.WEST
        if movement == Movement.WEST:
            return Movement.EAST


class RepairDroid:

    def __init__(self):
        self.position = Point(0, 0)
        self.movement = Movement.NORTH
        self.path_map = {self.position: Tile.TRAVERSABLE}
        self.path_hits = defaultdict(int)
        self.path_hits[self.position] += 1
        self.backup = False

    def get_grid_pos(self):
        return self.position.x, self.position.y

    @property
    def at_o2_system(self):
        return self.path_map.get(self.position, Tile.UNKNOWN) == Tile.O2_SYSTEM

    def _set_next_movement(self):
        possible_movements = []
        need_to_know = []
        movement_updated = False

        for direction, movement in [('one_north', Movement.NORTH),
                                    ('one_east', Movement.EAST),
                                    ('one_south', Movement.SOUTH),
                                    ('one_west', Movement.WEST)]:
            direction_method = getattr(self.position, direction)
            direction_point = direction_method()
            direction_tile = self.path_map.get(direction_point, Tile.UNKNOWN)

            if direction_tile == Tile.UNKNOWN and not movement_updated:
                self.movement = movement
                movement_updated = True

            elif direction_tile == Tile.UNKNOWN:
                need_to_know.append(direction_point)

            if direction_tile != Tile.WALL:
                possible_movements.append((movement, self.path_hits[direction_point]))

        if movement_updated:
            if not possible_movements:
                raise Exception(f'Unable to determine direction from {self.position}')

        if need_to_know:
            self.backup = True

        if not movement_updated:
            self.movement = min(possible_movements, key=lambda x: x[1])[0]

    def process_program_outcome(self, program):
        outcome = program.get_output()

        if self.movement == Movement.NORTH:
            outcome_position = self.position.one_north()
        elif self.movement == Movement.SOUTH:
            outcome_position = self.position.one_south()
        elif self.movement == Movement.EAST:
            outcome_position = self.position.one_east()
        elif self.movement == Movement.WEST:
            outcome_position = self.position.one_west()
        else:
            raise Exception(f'Unknown Movement {self.movement}')

        self.path_map[outcome_position] = Tile(outcome)

        if self.path_map[outcome_position] == Tile.WALL:
            self.backup = False
            self._set_next_movement()
        else:
            self.position = outcome_position
            self.path_hits[self.position] += 1

            if self.backup:
                self.backup = False
                self.movement = Movement.inverse(self.movement)
            else:
                self._set_next_movement()

        program.queue_input(self.movement)

    def _get_bounding_box(self):
        x_min = min(self.path_map.keys(), key=lambda point: point.x).x
        y_min = min(self.path_map.keys(), key=lambda point: point.y).y
        x_max = max(self.path_map.keys(), key=lambda point: point.x).x
        y_max = max(self.path_map.keys(), key=lambda point: point.y).y

        return x_min, y_min, x_max, y_max

    def draw_map(self, stdscr, message=None, shortest_path=[]):
        x_min, y_min, x_max, y_max = self._get_bounding_box()
        y_offset = abs(y_min) if y_min < 0 else 0
        x_offset = abs(x_min) if x_min < 0 else 0
        for y in range(y_min, y_max + 1):
            for x in range(x_min, x_max + 1):

                point_tile = self.path_map.get(Point(x, y), Tile.UNKNOWN)
                point_color = curses.color_pair(2) if Point(x, y) in shortest_path else curses.color_pair(1)
                if Point(x, y) == Point(0, 0):
                    stdscr.addstr(y + y_offset, x + x_offset, f'S', point_color)
                elif Point(x, y) == self.position and point_tile != Tile.O2_SYSTEM:
                    stdscr.addstr(y + y_offset, x + x_offset, f'D', point_color)
                else:
                    stdscr.addstr(y + y_offset, x + x_offset, f'{point_tile}', point_color)
        if message:
            stdscr.addstr(y_max + 2 + y_offset, 0, message)
            stdscr.addstr(y_max + 3 + y_offset, 0, 'Press any key to continue')

        stdscr.refresh()


class Node:
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(grid, start, end):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        children = []
        for node_position in [
            current_node.position.one_north(),
            current_node.position.one_south(),
            current_node.position.one_east(),
            current_node.position.one_west(),
        ]:  # Adjacent squares

            # Make sure walkable terrain
            position_terrain = grid.get(node_position, Tile.UNKNOWN)
            if position_terrain == Tile.UNKNOWN or position_terrain == Tile.WALL:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            skip_child = False

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    skip_child = True

            if skip_child:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position.x - end_node.position.x) ** 2) + ((child.position.y - end_node.position.y) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    skip_child = True

            if skip_child:
                continue

            # Add the child to the open list
            open_list.append(child)


def main(stdscr):
    # Clear screen
    stdscr.clear()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    input_queue = Queue()
    output_queue = Queue()

    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')

    droid = RepairDroid()
    program.queue_input(droid.movement)

    while not droid.at_o2_system:
        try:
            program.execute_next()

        except WaitingForInput:
            droid.process_program_outcome(program)
            droid.draw_map(stdscr)

    droid.draw_map(stdscr, message=f'O2 System at {droid.position}')
    stdscr.getch()

    shortest_path = astar(droid.path_map, Point(0, 0), droid.position)

    droid.draw_map(stdscr, shortest_path=shortest_path, message=f'Part One: {len(shortest_path) - 1}')
    stdscr.getch()
    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)
