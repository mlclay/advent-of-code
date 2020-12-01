#!/usr/bin/python3


def parse_input():
    """
    Parse input.txt to list of masses
    """

    values = []

    with open('input.txt', 'r') as input_file:
        for value in input_file:
            values.append(int(value.strip()))

    values.sort()
    return values


def two_sum(values, target=2020):
    seen_values = set()

    for value in values:
        other = target - value
        if other in seen_values:
            return value, other
        seen_values.add(value)

    return None


def three_sum(values, target=2020):

    for value in values:
        other = target - value
        sums = two_sum(values, target=other)
        if sums:
            return sums + (value,)

    return None


def main():
    values = parse_input()
    sums = two_sum(values)
    if sums:
        print(sums[0] * sums[1])

    sums = three_sum(values)
    if sums:
        print(sums[0] * sums[1] * sums[2])


if __name__ == '__main__':
    main()
