#!/usr/bin/python3

WALL = '#'
PATH = '.'
EMPTY = ' '

START = 'AA'
STOP = 'ZZ'


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.teleport = None
        self.inside = False

    def __str__(self):
        _teleport = f' -> {self.teleport}' if self.teleport else ''
        return f'({self.x},{self.y}){_teleport}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(self.__str__())

    def __copy__(self):
        point = Point(self.x, self.y)
        point.teleport = self.teleport
        point.inside = self.inside
        return point

    def one_north(self):
        return Point(self.x, self.y + 1)

    def one_east(self):
        return Point(self.x + 1, self.y)

    def one_south(self):
        return Point(self.x, self.y - 1)

    def one_west(self):
        return Point(self.x - 1, self.y)

    def get_neighbors(self):
        return {self.one_north(), self.one_south(), self.one_west(), self.one_east()}


def parse_input():
    """
    Parse input.txt to paths
    """

    paths = []
    teleports = []
    start = None
    finish = None

    with open('input.txt', 'r') as txt:
        for y_pos, y_row in enumerate(txt):
            inside = False
            was_inside = False
            for x_pos, space in enumerate(y_row):
                if space == WALL or space == PATH:
                    if was_inside:
                        inside = False
                    else:
                        inside = True

                if inside and not was_inside and space != WALL and space != PATH:
                    was_inside = True

                if space == PATH:
                    paths.append(Point(x_pos, y_pos))
                elif space.isalpha():
                    point = Point(x_pos, y_pos)
                    point.teleport = space
                    point.inside = inside
                    teleports.append(point)

    for index, teleport_one in enumerate(teleports):
        teleport_two = None

        if teleport_one.one_east() in teleports[index:]:
            teleport_two = teleports[teleports.index(teleport_one.one_east())]
        if teleport_one.one_north() in teleports[index:]:
            teleport_two = teleports[teleports.index(teleport_one.one_north())]

        if not teleport_two:
            continue

        teleporter_name = f'{teleport_one.teleport}{teleport_two.teleport}'

        path_point = [x for x in teleport_one.get_neighbors() if x in paths]
        if not path_point:
            path_point = [x for x in teleport_two.get_neighbors() if x in paths]

        if teleporter_name == 'AA':
            start = path_point[0]
            start.teleport = teleporter_name
        elif teleporter_name == 'ZZ':
            finish = path_point[0]
            finish.teleport = teleporter_name
        else:
            paths[paths.index(path_point[0])].teleport = teleporter_name
            paths[paths.index(path_point[0])].inside = teleport_one.inside or teleport_two.inside

    return start, finish, paths


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

    def __str__(self):
        return f'Node<{self.g},{self.h},{self.f}>{self.position}'

    def __repr__(self):
        return self.__str__()


def astar(paths, point_1, point_2):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
    """

    # Create start and end node
    start_node = Node(None, point_1)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, point_2)
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
            if node_position not in paths:
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


def pre_pathing_calculation(start, finish, paths):
    points_of_interest = [start, finish]
    points_of_interest.extend([x for x in paths if x.teleport])

    poi_pre_path = {}

    for index, point_1 in enumerate(points_of_interest):
        for index_2 in range(index + 1, len(points_of_interest)):
            point_2 = list(points_of_interest)[index_2]

            path = astar(paths, point_1, point_2)

            if not path:
                continue

            if point_1 not in poi_pre_path:
                poi_pre_path[point_1] = {}
            if point_2 not in poi_pre_path:
                poi_pre_path[point_2] = {}

            poi_pre_path[point_1][point_2] = len(path) - 1
            poi_pre_path[point_2][point_1] = len(path) - 1

    return poi_pre_path


def main():
    start, finish, paths = parse_input()
    poi_pre_path = pre_pathing_calculation(start, finish, paths)

    possible_routes = [{
        'point': start,
        'taken': [start.teleport],
        'distance': 0
    }]

    minimum_final_distance = None
    completed_paths = []

    while possible_routes:
        route = possible_routes.pop(0)
        for next_step in poi_pre_path[route['point']]:
            if next_step.teleport in route['taken']:
                continue
            if next_step.teleport != STOP:

                teleporter_exits = [x for x in paths if x.teleport == next_step.teleport]
                teleporter_exits.remove(next_step)

                new_point = {
                    'point': teleporter_exits[0].__copy__(),
                    'taken': route['taken'].copy(),
                    'distance': route['distance'] + 1
                }

                new_point['taken'].append(next_step.teleport)
                new_point['distance'] += poi_pre_path[route['point']][next_step]
                if minimum_final_distance is None or new_point['distance'] < minimum_final_distance:
                    possible_routes.append(new_point)
            else:
                route['taken'].append(next_step.teleport)
                route['distance'] += poi_pre_path[route['point']][next_step]
                if minimum_final_distance is None or route['distance'] < minimum_final_distance:
                    minimum_final_distance = route['distance']
                completed_paths.append(route)

    print(f'Part One: {min(completed_paths, key=lambda r: r["distance"])}')

    possible_routes = [{
        'point': start,
        'taken': [start.teleport],
        'distance': 0,
        'depth': 0
    }]

    minimum_final_distance = None
    completed_paths = []

    while possible_routes:
        route = possible_routes.pop(0)
        for next_step in poi_pre_path[route['point']]:
            if route['depth'] == 0 and not next_step.inside and next_step.teleport != STOP:
                continue
            if route['depth'] != 0 and (next_step.teleport == START or next_step.teleport == STOP):
                continue
            if next_step.teleport != STOP:

                teleporter_exits = [x for x in paths if x.teleport == next_step.teleport]
                teleporter_exits.remove(next_step)

                new_point = {
                    'point': teleporter_exits[0].__copy__(),
                    'taken': route['taken'].copy(),
                    'distance': route['distance'] + 1,
                    'depth': route['depth'] + (1 if next_step.inside else -1)
                }

                new_point['taken'].append(next_step.teleport)
                new_point['distance'] += poi_pre_path[route['point']][next_step]
                if minimum_final_distance is None or new_point['distance'] < minimum_final_distance:
                    possible_routes.append(new_point)
            else:
                route['taken'].append(next_step.teleport)
                route['distance'] += poi_pre_path[route['point']][next_step]
                if minimum_final_distance is None or route['distance'] < minimum_final_distance:
                    minimum_final_distance = route['distance']
                completed_paths.append(route)

    print(f'Part Two: {min(completed_paths, key=lambda r: r["distance"])}')


if __name__ == '__main__':
    main()
