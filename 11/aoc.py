#!/usr/bin/python


class Grid:
    def __init__(self, serial_number, height, width):
        self.serial_number = serial_number
        self.height = height
        self.width = width
        self.cells = [[Grid.Cell(self, x, y) for x in range(1, self.width + 1)] for y in range(1, self.height + 1)]
        self.generate_square_power()

    def __str__(self):
        return f'Height {self.height} \tWidth {self.width}'

    def generate_square_power(self):
        for x in range(0, self.width):
            for y in range(0, self.height):
                cell = self.cells[x][y]
                if self.width - x >= 3 and self.height - y >= 3:
                    cell.square_power = sum(
                        [sum([self.cells[xx][yy].power_level for xx in range(x, x + 3)]) for yy in range(y, y + 3)])

    def find_max_3x3_cell(self):
        max_square_power = 0
        top_left_cell = None
        for cell_row in self.cells:
            for cell in cell_row:
                if cell.square_power > max_square_power:
                    max_square_power = cell.square_power
                    top_left_cell = cell

        return top_left_cell

    class Cell:
        def __init__(self, grid, x, y):
            self.grid = grid
            self.x = int(x)
            self.y = int(y)
            self.rack_id = self.x + 10
            self.power_level = self.calculate_power_level()
            self.square_power = 0

        def __str__(self):
            return f'[{self.x}, {self.y}] (Rack ID: {self.rack_id}; Power Level: {self.power_level}; Square Power: {self.square_power})'

        def calculate_power_level(self):
            power_level = self.rack_id * self.y
            power_level += self.grid.serial_number
            power_level *= self.rack_id
            power_level = str(power_level)
            power_level = int(power_level[-3]) if len(power_level) > 2 else 0
            power_level -= 5
            return power_level


def main():
    grid = Grid(3999, 300, 300)

    max_3x3_cell = grid.find_max_3x3_cell()

    print(f'Part One: {max_3x3_cell}')


if __name__ == '__main__':
    main()
