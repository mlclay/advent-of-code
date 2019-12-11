#!/usr/bin/python3
from intcode import IntcodeProgram


def main():
    program = IntcodeProgram(io_scheme=IntcodeProgram.IOScheme.CONSOLE)
    program.initialize_memory_from_file('input.txt')

    program.run_to_end()


if __name__ == '__main__':
    main()
