#!/usr/bin/python
from collections import defaultdict


def parse_input():
    seen_frequencies = defaultdict(bool)
    first_duplicate = None
    freq_one_loop = None
    freq_running = 0

    seen_frequencies[freq_running] = True

    with open('input.txt', 'r') as txt:

        while not first_duplicate:

            for line in txt:
                freq_running += int(line)

                if first_duplicate is None and seen_frequencies[freq_running]:
                    first_duplicate = freq_running

                seen_frequencies[freq_running] = True

            if freq_one_loop is None:
                freq_one_loop = freq_running

            txt.seek(0)

    return freq_one_loop, first_duplicate


if __name__ == '__main__':
    part_one, part_two = parse_input()

    print(f'Part One: {part_one}\nPart Two: {part_two}')
