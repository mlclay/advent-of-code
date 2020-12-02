#!/usr/bin/python3
from collections import Counter


def main():
    valid = total = 0
    with open('input.txt', 'r') as input_file:
        for policy in input_file:
            total += 1
            count, check, password = policy.strip().split()
            count = list(map(int, count.split('-')))
            check = check[0]
            counter = Counter(password)
            if count[0] <= counter[check] <= count[1]:
                valid += 1

    print(valid)


if __name__ == '__main__':
    main()
