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
            f'sleepiest_minute: {self.sleepiest_minute()}; '
        )

    def track_sleep(self, fell_asleep, wakes_up):
        for minute in range(fell_asleep, wakes_up):
            self.asleep[minute] += 1
        self.total_asleep += (wakes_up - fell_asleep)

    def sleepiest_minute(self):
        minute, count = sorted(self.asleep.items(), key=lambda kv: kv[1], reverse=True)[0]
        return minute


def get_duty_log():
    guard_duties = []

    with open('input.txt', 'r') as txt:
        for line in txt:
            guard_duties.append(line.strip())

    guard_duties.sort()

    return guard_duties


def parse_duty_log(duty_log):
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
    return sorted(guards.values(), key=operator.attrgetter('total_asleep'), reverse=True)[0]


def main():
    duty_log = get_duty_log()
    guards = parse_duty_log(duty_log)

    sleepiest = find_sleepiest_guard(guards)

    print(f'Part One: {sleepiest.id_ * sleepiest.sleepiest_minute()}')


if __name__ == '__main__':
    main()
