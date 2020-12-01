#!/usr/bin/python3
from collections import defaultdict


def two_sum():
    values = defaultdict(bool)

    with open('input.txt', 'r') as input:
        for value in input:
            value = int(value.strip())
            other = 2020 - value
            if other in values:
                return value, other
            values[value] = True

    return None


if __name__ == '__main__':
    sums = two_sum()
    if sums:
        print(sums[0] * sums[1])
