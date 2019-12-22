#!/usr/bin/python3
from queue import Queue, Empty

from intcode import IntcodeProgram
from exceptions import WaitingForInput, ProgramHalted


def draw_output(program):
    while True:
        try:
            output = program.get_output(block=False)
            try:
                character = chr(output)
                print(character, end='')
            except ValueError:
                return output
        except Empty:
            break


def survey_hull(program):
    springscript = [
        'NOT A J',
        'NOT B T',
        'OR T J',
        'NOT C T',
        'OR T J',
        'AND D J',
        'WALK'
    ]

    for spring_instruction in springscript:
        for character in spring_instruction:
            program.queue_input(ord(character))
        program.queue_input(10)

    try:
        program.run_to_end()

    except ProgramHalted:
        print('Program Complete')

    hull_damage = draw_output(program)

    print(f'Part One: {hull_damage}')


def main():
    input_queue = Queue()
    output_queue = Queue()
    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.QUEUE,
                             input_queue=input_queue,
                             output_queue=output_queue)
    program.initialize_memory_from_file('input.txt')

    survey_hull(program)


if __name__ == '__main__':
    main()
