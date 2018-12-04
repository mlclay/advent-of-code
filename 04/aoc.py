#!/usr/bin/python
import operator
import re
from collections import defaultdict
from datetime import datetime


class Guard:
    # [1518-01-01 00:03] Guard #1 begins shift
    # [1518-01-01 00:15] falls asleep
    # [1518-01-01 00:48] wakes up
    LINE_PATTERN = r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] ' \
                   r'(?:Guard #(?P<next>\d+))?' \
                   r'(?P<asleep>falls)?' \
                   r'(?P<awake>wakes)? *'
    LINE_REGEX = re.compile(LINE_PATTERN)

    def __init__(self, id_):
        self.id_ = int(id_)
        self.asleep = defaultdict(int)
        self.total_asleep = 0

    def __str__(self):
        return (
            f'ID: {self.id_}; '
            f'total_asleep: {self.total_asleep}; '
            f'sleepiest_minute: {self.sleepiest_minute_count()}; '
        )

    def track_sleep(self, fell_asleep, wakes_up):
        """
        Builds the dictionary tracking individual minutes asleep and calculates total time asleep

        :param fell_asleep: Minute guard fell asleep
        :param wakes_up: Minute guard woke up
        """
        for minute in range(fell_asleep, wakes_up):
            self.asleep[minute] += 1
        self.total_asleep += (wakes_up - fell_asleep)

    def sleepiest_minute_count(self):
        """
        Get the (minute, count) of the sleepiest this guard consistently is

        :return: tuple: (minute, count) of the sleepiest minute and how many days this guard slept on that minute
        """
        asleep_sorted_count = sorted(self.asleep.items(), key=lambda kv: kv[1], reverse=True)
        try:
            return asleep_sorted_count[0]
        except IndexError:
            return -1, -1


def get_duty_log():
    """
    Parse input.txt and build a sorted lit of input strings

    :return: list: timestamp sorted duty log
    """
    guard_duties = []

    with open('input.txt', 'r') as txt:
        for line in txt:
            guard_duties.append(line.strip())

    guard_duties.sort()

    return guard_duties


def parse_duty_log(duty_log):
    """
    Parse the duty logs and generate Guard objects, capture sleep patterns

    :param duty_log: timestamp sorted duty log
    :return: dictionary: Guard objects keyed by ID
    """
    guards = {}
    current_guard = None
    last_asleep = None

    for duty in duty_log:
        match = Guard.LINE_REGEX.match(duty)

        timestamp = match.group('timestamp')
        next_id = match.group('next')
        asleep = match.group('asleep')
        awake = match.group('awake')

        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')

        if next_id:
            last_asleep = None

            try:
                current_guard = guards[next_id]
            except KeyError:
                guards[next_id] = Guard(next_id)
                current_guard = guards[next_id]

        if asleep:
            last_asleep = timestamp.minute

        if awake:
            current_guard.track_sleep(last_asleep, timestamp.minute)

    return guards


def find_sleepiest_guard(guards):
    """
    Search Guards for the one that sleeps the most (total_asleep)

    :param guards: dictionary: All Guards
    :return: Guard: The sleepiest Guard
    """
    return sorted(guards.values(), key=operator.attrgetter('total_asleep'), reverse=True)[0]


def find_consistently_asleep_guard(guards):
    """
    Search Guards for the one that sleeps the most consistently

    :param guards: dictionary: All Guards
    :return: Guard: The Guard that sleeps more at one minute than any other Guard
    """
    return sorted(guards.values(), key=lambda guard: guard.sleepiest_minute_count()[1], reverse=True)[0]


def main():
    duty_log = get_duty_log()
    guards = parse_duty_log(duty_log)

    sleepiest = find_sleepiest_guard(guards)
    consistent = find_consistently_asleep_guard(guards)

    print(f'Part One: {sleepiest.id_ * sleepiest.sleepiest_minute_count()[0]}')
    print(f'Part Two: {consistent.id_ * consistent.sleepiest_minute_count()[0]}')


if __name__ == '__main__':
    main()
