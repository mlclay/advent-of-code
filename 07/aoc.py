#!/usr/bin/python
from operator import itemgetter
import re

LINE_PATTERN = r'Step (?P<current>\w) must be finished before step (?P<after>\w) can begin.'
LINE_REGEX = re.compile(LINE_PATTERN)


class Step:
    
    def __init__(self, name):
        self.name = name
        self.next_steps = {}

    def add_step(self, step):
        """
        Add a Step to next_steps, preserving alphabetical order by step name

        :param step: Step that must happen after this
        """
        self.next_steps[step.name] = step
        self.next_steps = {k: v for k, v in sorted(self.next_steps.items(), key=itemgetter(0))}

    def get_next(self):
        """
        Get the next step to run after this.  Add that step's next_steps to the current list of steps to do

        :return: Next Step to do
        """
        items = next(iter(self.next_steps.keys()))
        do_next = self.next_steps.pop(items)

        self.add_applicable_steps(do_next)

        return do_next

    def add_applicable_steps(self, other):
        """
        Take next_steps from another Step and add them to this list of next_steps if they don't have any prereqs left

        :param other: Other Step to scan next_steps from
        """
        may_add = []
        for step in other.next_steps.values():
            if not self.is_prerequisite_to(step):
                may_add.append(step)

        will_add = []
        for might in may_add:
            should_add = True
            for step in other.next_steps.values():
                if step.is_prerequisite_to(might):
                    should_add = False
            if should_add:
                will_add.append(might)

        for add in will_add:
            self.add_step(add)

    def is_prerequisite_to(self, other):
        """
        Does this next_steps contain the other Step?

        :param other: Step to compare self's next_steps against
        :return: boolean: is this step a prerequisite to the other Step
        """
        for step in self.next_steps.values():
            if step.name == other.name:
                return True

        for step in self.next_steps.values():
            if step.is_prerequisite_to(other):
                return True

        return False

    def __str__(self):
        return f'{self.name} -> {[k for k, v in self.next_steps.items()]}'


def parse_input():
    """
    Parse input.txt to string

    :return: list of tuples defining X,Y coordinates
    """
    all_steps = {}
    head = Step('_HEAD_')

    with open('input.txt', 'r') as txt:
        for line in txt:
            match = LINE_REGEX.match(line)

            current_name = match.group('current')
            after_name = match.group('after')

            if current_name in all_steps.keys():
                current = all_steps[current_name]
            else:
                current = Step(current_name)
                all_steps[current_name] = current

            if after_name in all_steps.keys():
                after = all_steps[after_name]
            else:
                after = Step(after_name)
                all_steps[after_name] = after

            current.add_step(after)

    has_prerequisite = []
    for v in all_steps.values():
        has_prerequisite.extend([b.name for b in v.next_steps.values()])

    for no_prerequisite in [all_steps[step] for step in all_steps.keys() if step not in has_prerequisite]:
        head.add_step(no_prerequisite)

    return head


def get_correct_order(head):
    """
    Step through all next_steps starting with head and generate step order

    :param head: Step object containing next_steps
    :return: str: appropriate step order
    """
    order = []
    do_next = head.get_next()

    while do_next:
        order.append(do_next.name)
        if len(head.next_steps.keys()):
            do_next = head.get_next()
        else:
            do_next = None

    return "".join(order)


def main():
    head = parse_input()

    order = get_correct_order(head)

    print(f'First Step: {order}')


if __name__ == '__main__':
    main()
