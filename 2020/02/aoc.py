#!/usr/bin/python3
from collections import Counter


def parse_policy(policy):
    count, check, password = policy.strip().split()
    count = list(map(int, count.split('-')))
    check = check[0]
    return count, check, password


def main():
    part_one = part_two = 0
    with open('input.txt', 'r') as input_file:
        for policy in input_file:
            count, check, password = parse_policy(policy)

            counter = Counter(password)
            if count[0] <= counter[check] <= count[1]:
                part_one += 1

            if bool(password[count[0] - 1] == check) ^ bool(password[count[1] - 1] == check):
                part_two += 1

    print(f'Part One: {part_one}')
    print(f'Part Two: {part_two}')


if __name__ == '__main__':
    main()
