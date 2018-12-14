#!/usr/bin/python
import os
import re
from collections import defaultdict

STATE_PATTERN = r'initial state: (?P<initial_state>[\.#]+)'
STATE_REGEX = re.compile(STATE_PATTERN)

RULE_PATTERN = r'(?P<pattern>[\.#]{5}) => (?P<result>[\.#])'
RULE_REGEX = re.compile(RULE_PATTERN)

DEBUG = os.environ.get('DEBUG', False)


class Rule:
    def __init__(self, pattern, result):
        self.pattern = plant_str_to_bool(pattern)
        self.result = plant_str_to_bool(result)[0]

    def __str__(self):
        return f'{self.pattern} --> {bool_to_plant_str(self.result)}'


class PlantTracker:
    def __init__(self, initial_state):
        bool_array = plant_str_to_bool(initial_state)
        self.pots = defaultdict(bool, zip(range(0, len(bool_array)), bool_array))
        self.rules = []

    def __str__(self):
        pot_list = [self.pots[x] for x in range(min([-5] + list(self.pots.keys())) - 5, max(self.pots.keys()) + 5)]
        return f'{bool_to_plant_str(pot_list)}'

    def add_rule(self, rule):
        self.rules.append(rule)

    def _get_comparison_pots(self, pot):
        comparison_range = (x for x in range(pot - 2, pot + 3))
        keys = self.pots.keys()
        return [(self.pots[x] if x in keys else False) for x in comparison_range]

    def run_generation(self, generations=1):

        for generation in range(1, generations + 1):
            next_generation = defaultdict(bool)

            pot_keys = self.pots.keys()
            search_min = min(pot_keys) - 2
            search_max = max(pot_keys) + 2

            for pot in range(search_min, search_max):
                comparison_pots = self._get_comparison_pots(pot)
                for rule in self.rules:
                    if all([ai == bi for ai, bi in zip(rule.pattern, comparison_pots)]):
                        next_generation[pot] = rule.result
                        break
            self.pots = next_generation

    def calculate_plant_sum(self):
        plant_sum = 0
        plant_count = 0

        for plant in self.pots.keys():
            if self.pots[plant]:
                plant_sum += plant
                plant_count += 1

        return plant_sum, plant_count


def plant_str_to_bool(string_state):
    boolean_states = []

    for state in string_state:
        if state == '.':
            boolean_states.append(False)
        if state == '#':
            boolean_states.append(True)

    return boolean_states


def bool_to_plant_str(input_list):
    string_states = []

    boolean_states = input_list

    if type(boolean_states) is bool:
        boolean_states = [boolean_states]

    for boolean_state in boolean_states:
        string_states.append('#' if boolean_state else '.')

    return ''.join(string_states)


def parse_input():
    """
    Parse input.txt to list of tuple(player count, final marble)

    :return: list of tuples
    """

    tracker = None

    with open('test.txt', 'r') as txt:
        for line in txt:
            match_initial_state = STATE_REGEX.match(line.strip())
            match_rule = RULE_REGEX.match(line.strip())

            if match_initial_state:
                tracker = PlantTracker(match_initial_state.group('initial_state'))

            if match_rule:
                tracker.add_rule(Rule(match_rule.group('pattern'), match_rule.group('result')))

    return tracker


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def main():
    tracker = parse_input()

    tracker.run_generation(generations=20)

    print(f'Part One: {tracker.calculate_plant_sum()}')


if __name__ == '__main__':
    main()
