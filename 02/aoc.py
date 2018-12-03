#!/usr/bin/python
from collections import defaultdict, Counter


def process_container_deltas(all_containers, container):
    """
    Finds another container that is Off-by-One from provided container

    :param all_containers: List of all container IDs
    :param container: Specific container we are testing against
    :return: Common characters in off-by-one containers (or None if not off-by-one)
    """

    for test in all_containers:
        delta = [item for index, item in enumerate(list(container)) if item != list(test)[index]]

        if len(delta) == 1:
            return container.replace(delta[0], '')

    return None


def parse_input():

    checksum_segments = defaultdict(int)
    off_by_one_commonality = None
    all_containers = []

    with open('input.txt', 'r') as txt:

        # Process list for Part 1
        for line in txt:
            line = line.strip()
            all_containers.append(line)

            char_frequency = Counter(line)
            frequencies = defaultdict(bool, {v: True for k, v in char_frequency.items()})

            for x in [2, 3]:
                if frequencies[x]:
                    checksum_segments[x] += 1

    # Process list for Part 2
    for container in all_containers:
        off_by_one_commonality = process_container_deltas(all_containers, container)

        if off_by_one_commonality:
            break

    return checksum_segments[2] * checksum_segments[3], off_by_one_commonality


if __name__ == '__main__':
    part_one, part_two = parse_input()

    print(f'Part One: {part_one}\nPart Two: {part_two}')
