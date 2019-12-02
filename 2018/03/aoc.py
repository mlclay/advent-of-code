#!/usr/bin/python
import re
from collections import defaultdict


class FabricSquare:
    # `#1 @ 82,901: 26x12`
    LINE_PATTERN = r'#(?P<num>\d+) @ (?P<left_offset>\d+),(?P<top_offset>\d+): (?P<width>\d+)x(?P<height>\d+)'
    LINE_REGEX = re.compile(LINE_PATTERN)

    def __init__(self, num, left_offset, top_offset, width, height):
        self.num = num
        self.left_offset = int(left_offset)
        self.top_offset = int(top_offset)
        self.width = int(width)
        self.height = int(height)
        self.coords = self.generate_coords()

    def generate_coords(self):
        coords = []

        for x in range(self.left_offset, self.left_offset + self.width):
            for y in range(self.top_offset, self.top_offset + self.height):
                coords.append((x, y))

        return coords

    def __str__(self):
        return (
            f'Num: {self.num}; '
            f'Left: {self.left_offset}; '
            f'Top: {self.top_offset}; '
            f'Width: {self.width}; '
            f'Height: {self.height}; '
        )

    @staticmethod
    def from_string(string):
        match = FabricSquare.LINE_REGEX.match(string)

        return FabricSquare(num=match.group('num'),
                            left_offset=match.group('left_offset'),
                            top_offset=match.group('top_offset'),
                            width=match.group('width'),
                            height=match.group('height'))


def parse_input():
    perfect_square_id = None
    all_squares = []
    fabric = defaultdict(int)

    with open('input.txt', 'r') as txt:

        # Process list for Part 1
        for line in txt:
            line = line.strip()

            square = FabricSquare.from_string(line)
            all_squares.append(square)

            for coord in square.coords:
                fabric[coord] += 1

        multi_claims = {k: v for (k, v) in fabric.items() if v > 1}

    # Process squares for Part 2
    for square in all_squares:
        multi_claims_in_square = [x for x, y in square.coords if (x, y) in multi_claims.keys()]

        if len(multi_claims_in_square) == 0:
            perfect_square_id = square.num
            break

    return len(multi_claims), perfect_square_id


if __name__ == '__main__':
    part_one, part_two = parse_input()

    print(f'Part One: {part_one}\nPart Two: {part_two}')
