#!/usr/bin/python
from collections import defaultdict
from operator import itemgetter


def parse_input():
    """
    Parse input.txt to string

    :return: list of tuples defining X,Y coordinates
    """
    danger_points = []

    with open('input.txt', 'r') as txt:
        for line in txt:
            x, y = line.strip().split(', ')
            danger_points.append(tuple((int(x), int(y))))

    return danger_points


def get_bounding_box(target_coordinates):
    """
    Determines bounding box from input coordinates

    :param target_coordinates: List of x,y tuple coordinates
    :return:
    """
    x_min = min(target_coordinates, key=itemgetter(0))[0]
    y_min = min(target_coordinates, key=itemgetter(1))[1]
    x_max = max(target_coordinates, key=itemgetter(0))[0]
    y_max = max(target_coordinates, key=itemgetter(1))[1]

    return x_min, y_min, x_max, y_max


def manhattan_distance(grid_location, target_coordinate):
    """
    Generate Manhattan Distance

    :param grid_location: X, Y coordinate
    :param target_coordinate: X, Y coordinate
    :return: integer manhattan distance
    """
    return abs(grid_location[0] - target_coordinate[0]) + abs(grid_location[1] - target_coordinate[1])


def calculate_grid_distances(danger_points, x_min, y_min, x_max, y_max):
    """
    For each applicable point in the bounding box, find the closest danger point

    :param danger_points: List of danger points
    :param x_min: Bounding Box minimum X
    :param y_min: Bounding Box minimum Y
    :param x_max: Bounding Box maximum X
    :param y_max: Bounding Box maximum Y
    :return: tuple: dictionary of x,y coordinates mapped to the closet x,y danger point
             and dictionary of x,y coordinates and the sum of manhattan distance to all safe points
    """
    danger_grid = {}
    summation_grid = defaultdict(int)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            min_distance = y_max + x_max
            danger_grid[(x, y)] = None

            for danger_point in danger_points:
                distance = manhattan_distance((x, y), danger_point)
                summation_grid[(x, y)] += distance

                if distance == min_distance:
                    danger_grid[(x, y)] = None

                elif distance < min_distance:
                    min_distance = distance
                    danger_grid[(x, y)] = danger_point

    return danger_grid, summation_grid


def remove_invalid_grid_points(grid, danger_points, x_min, y_min, x_max, y_max):
    """
    Removes danger point from grid distances if the area is infinite (if the area touches the bounding box)

    :param grid: dictionary of x,y coordinates mapped to the closet x,y danger point
    :param danger_points: List of danger points
    :param x_min: Bounding Box minimum X
    :param y_min: Bounding Box minimum Y
    :param x_max: Bounding Box maximum X
    :param y_max: Bounding Box maximum Y
    :return: dictionary: Dictionary containing coordinate->distance map for non-infinite areas
    """

    valid_danger_points = danger_points.copy()

    for k, v in grid.items():
        if v in valid_danger_points and (k[0] == x_min or k[0] == x_max or k[1] == y_min or k[1] == y_max):
            valid_danger_points.remove(v)

    return {k: v for k, v in grid.items() if v in valid_danger_points}


def get_largest_area(valid_grid):
    """
    Find the largest area from the valid grid coordinates

    :param valid_grid: grid containing non-infinite area partitions
    :return: int: Size of largest area in the valid_grid
    """
    area = defaultdict(int)

    for k, v in valid_grid.items():
        area[v] += 1

    return sorted(area.items(), key=lambda kv: kv[1], reverse=True)[0][1]


def main():
    target_coordinates = parse_input()

    x_min, y_min, x_max, y_max = get_bounding_box(target_coordinates)

    danger_grid, summation_grid = calculate_grid_distances(target_coordinates, x_min, y_min, x_max, y_max)
    valid_grid = remove_invalid_grid_points(danger_grid, target_coordinates, x_min, y_min, x_max, y_max)

    largest_area = get_largest_area(valid_grid)

    print(f'Part One: {largest_area}')

    safe_area = {k: v for k, v in summation_grid.items() if v < 10000}

    print(f'Part Two: {len(safe_area)}')


if __name__ == '__main__':
    main()
