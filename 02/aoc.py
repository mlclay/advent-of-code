#!/usr/bin/python
from collections import defaultdict, Counter


def parse_input():

    with open('input.txt', 'r') as txt:

        checksum_segments = defaultdict(int)

        for line in txt:
            char_frequency = Counter(line.strip())
            frequencies = defaultdict(bool, {v: True for k, v in char_frequency.items()})

            for x in [2, 3]:
                if frequencies[x]:
                    checksum_segments[x] += 1

    return checksum_segments[2] * checksum_segments[3]


if __name__ == '__main__':
    part_one = parse_input()

    print(f'Part One: {part_one}')
