#!/usr/bin/python
import copy
import os
import re
from operator import itemgetter

LINE_PATTERN = r'Step (?P<current>\w) must be finished before step (?P<after>\w) can begin.'
LINE_REGEX = re.compile(LINE_PATTERN)


class Step:
    BASE_STEP_TIME = 60

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

    def list_non_blocked(self):
        return [key for key in iter(self.next_steps.values())]

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

    def seconds(self):
        return ord(self.name) - 64 + Step.BASE_STEP_TIME

    def __str__(self):
        return f'{self.name} -> {[k for k, v in self.next_steps.items()]}'


def parse_input():
    """
    Parse input.txt to string

    :return: head Step with only non-dependent next_steps defined
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


class Worker:
    """
    Class to track the multiple workers used in Part Two
    """

    def __init__(self, num):
        self.num = num
        self.ready_time = 0
        self.step = None

    def __str__(self):
        return f'#{self.num} @{self.step.name if self.step else "_"} >{self.ready_time}'


def get_multi_worker_time(head, num_workers=1):
    """
    Step through all next_steps with num_workers parallelism and determine total run time

    :param head: Step object containing next_steps
    :param num_workers: int number or workers to run in parallel
    :return: int: total time taken to complete all steps with num_workers
    """
    head = copy.deepcopy(head)
    workers = {}
    current_time = 0

    # Generate desired workers
    for w in range(1, num_workers + 1):
        workers[w] = Worker(w)

    still_work_to_do = True
    while still_work_to_do:

        # For any step that is now complete, add its next_steps to the head and free up worker
        for worker in workers.values():
            if current_time >= worker.ready_time:
                if worker.step:
                    head.add_applicable_steps(worker.step)
                    worker.step = None

        # Process all steps with no prerequisites
        non_blocked = head.list_non_blocked()
        for available in non_blocked.copy():

            # Determine if the available step needs a currently running step to be completed first
            has_no_prerequisites = True
            for worker in workers.values():
                if worker.step and worker.step.is_prerequisite_to(available):
                    has_no_prerequisites = False

            # Find open worker, assign them the available step, and remove it from the list of available steps
            if has_no_prerequisites:
                for worker in workers.values():

                    if current_time >= worker.ready_time:
                        worker.ready_time = current_time + available.seconds()
                        worker.step = available

                        non_blocked.remove(available)
                        head.next_steps.pop(available.name)
                        break

        if os.environ.get('DEBUG', False):
            print(f'{current_time}:\t{";  ".join([str(x) for x in workers.values()])}')

        still_work_to_do = bool([x.num for x in workers.values() if x.step])
        current_time += 1

    return current_time - 1


def get_correct_order(head):
    """
    Step through all next_steps starting with head and generate step order
    :param head: Step object containing next_steps
    :return: str: appropriate step order
    """
    head = copy.deepcopy(head)
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
    seconds = get_multi_worker_time(head, 5)

    print(f'Part One: {order}')
    print(f'Part Two: {seconds}')


if __name__ == '__main__':
    main()
