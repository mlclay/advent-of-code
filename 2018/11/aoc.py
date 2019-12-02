#!/usr/bin/python
import operator
from collections import defaultdict


class Grid:
    """
    Contains a 2d list of all Cells and includes calculations to generate square power and find cells with maximum power
    """

    def __init__(self, serial_number, height, width):
        self.serial_number = serial_number
        self.height = height
        self.width = width
        self.cells = [[Grid.Cell(self, x, y) for x in range(1, self.width + 1)] for y in range(1, self.height + 1)]
        self.generate_square_power()

    def __str__(self):
        return f'Height {self.height} \tWidth {self.width}'

    def generate_square_power(self):
        """
        For each Cell in the grid, calculate the total square power for all applicable square sizes
        """
        for x in range(0, self.width):
            for y in range(0, self.height):

                cell = self.cells[x][y]
                biggest_square = min(self.width - x, self.height - y)

                for square_size in range(1, biggest_square + 1):

                    if square_size > 1:
                        # Use prior, pre-calculated square to initialize this square
                        cell.square_power[square_size] = cell.square_power[square_size - 1]

                        # Add all cell powers in the newest row
                        cell.square_power[square_size] += sum(
                            [self.cells[xx][y + square_size - 1].power_level for xx in range(x, x + square_size)])

                        # Add all cell powers in the newest column
                        # Except the final cell, which was already included in the newest row summation
                        cell.square_power[square_size] += sum(
                            [self.cells[x + square_size - 1][yy].power_level for yy in range(y, y + square_size - 1)])

                    else:
                        # Square of size=1 is simply the power_level of the cell
                        cell.square_power[square_size] = cell.power_level

    def find_max_cell(self, size=None):
        """
        Find the cell whose square of size has the highest combined power level

        :param size: Single square dimension used for maximum combined power lookup (default: 3)
        :return: Cell at the top-left of the square with highest combined power level, size of square for that power
        """
        max_square_power = -99999
        top_left_cell = None
        max_size = size

        for cell_row in self.cells:
            for cell in cell_row:

                if size:
                    if cell.square_power[size] > max_square_power:
                        max_square_power = cell.square_power[size]
                        top_left_cell = cell

                else:
                    max_cell_square = max(cell.square_power.items(), key=operator.itemgetter(1))
                    if max_cell_square[1] > max_square_power:
                        max_square_power = max_cell_square[1]
                        top_left_cell = cell
                        max_size = max_cell_square[0]

        return top_left_cell, max_size

    class Cell:
        """
        Single cell in the Grid.  Encapsulates the Rack ID, Power Level, and dictionary of Square Powers of various size
        """

        def __init__(self, grid, x, y):
            self.grid = grid
            self.x = int(x)
            self.y = int(y)
            self.rack_id = self.x + 10
            self.power_level = self.calculate_power_level()
            self.square_power = defaultdict(int)

        def __str__(self):
            return f'[{self.x}, {self.y}] (Rack ID: {self.rack_id}; Power Level: {self.power_level}; Square Power: {self.square_power})'

        def calculate_power_level(self):
            """
            Calculates Power Level of this cell

            :return: Calculated Power Level
            """
            power_level = self.rack_id * self.y
            power_level += self.grid.serial_number
            power_level *= self.rack_id
            power_level = str(power_level)
            power_level = int(power_level[-3]) if len(power_level) > 2 else 0
            power_level -= 5
            return power_level


def main():
    grid = Grid(3999, 300, 300)

    max_3x3_cell, size = grid.find_max_cell(3)
    print(f'Part One: [{max_3x3_cell.x},{max_3x3_cell.y}] {size}')

    max_any_cell, size = grid.find_max_cell()
    print(f'Part Two: [{max_any_cell.x},{max_any_cell.y}] {size}')


if __name__ == '__main__':
    main()
