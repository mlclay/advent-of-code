#!/usr/bin/python
import re

LINE_PATTERN = r'(\w)(?!\1)(?i:\1)'
LINE_REGEX = re.compile(LINE_PATTERN)


def parse_input():
    with open('input.txt', 'r') as txt:
        polymer_sequence = txt.read()
    return polymer_sequence.strip()


def squash_polymer(polymer_sequence):
    while True:
        polymer_sequence, replacements = re.subn(LINE_REGEX, '', polymer_sequence)
        if not replacements:
            return polymer_sequence


def main():
    polymer_sequence = parse_input()
    squashed = squash_polymer(polymer_sequence)

    print(f'Part One: {len(squashed)}')


if __name__ == '__main__':
    main()
