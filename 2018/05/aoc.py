#!/usr/bin/python
import re
from string import ascii_lowercase

LINE_PATTERN = r'(\w)(?!\1)(?i:\1)'
LINE_REGEX = re.compile(LINE_PATTERN)


def parse_input():
    """
    Parse input.txt to string

    :return: polymer sequence string
    """
    with open('input.txt', 'r') as txt:
        polymer_sequence = txt.read()
    return polymer_sequence.strip()


def squash_polymer(polymer_sequence):
    """
    Remove adjacent inverse-case letters from the sequence until no more can be removed

    :param polymer_sequence: string sequence of polymer units
    :return: squashed polymer
    """
    while True:
        polymer_sequence, replacements = re.subn(LINE_REGEX, '', polymer_sequence)
        if not replacements:
            return polymer_sequence


def remove_unit(polymer_sequence, unit):
    """
    Removes a single unit from the polymer_sequence

    :param polymer_sequence: string sequence of polymer units
    :param unit: single character to remove
    :return: polymer_sequence with all instances of unit removed
    """
    return re.sub(f'[{unit}]', '', polymer_sequence, flags=re.IGNORECASE)


def test_all_units(polymer_sequence):
    """
    Finds the shortest polymer possible by removing one unit at a time and squashing

    :param polymer_sequence: string sequence of polymer units
    :return: length of shortest squashed polymer
    """
    shortest_length = len(polymer_sequence)

    for char in ascii_lowercase:
        test_polymer = remove_unit(polymer_sequence, char)

        squashed_length = len(squash_polymer(test_polymer))

        if squashed_length < shortest_length:
            shortest_length = squashed_length

    return shortest_length


def main():
    polymer_sequence = parse_input()

    squashed = squash_polymer(polymer_sequence)
    shortest_chain = test_all_units(polymer_sequence)

    print(f'Part One: {len(squashed)}')
    print(f'Part Two: {shortest_chain}')


if __name__ == '__main__':
    main()
