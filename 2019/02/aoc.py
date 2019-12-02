#!/usr/bin/python3


class InstructionSet:

    class Halt(Exception):
        pass

    class InvalidOpCode(Exception):
        def __init__(self, opcode, instruction_offset):
            self.opcode = opcode
            self.instruction_offset = instruction_offset

        def __str__(self):
            return f'Invalid OpCode [{self.opcode}] encountered at offset {self.instruction_offset}'

    class OpCodes:
        ADD = 1
        MUL = 2
        HALT = 99

    def __init__(self):
        self._int_codes = {}
        self._next_instruction = 0

    def __str__(self):
        return ','.join([str(x) for x in self._int_codes.values()])

    def add_int_code(self, position, code):
        self._int_codes[position] = int(code)

    def get_int_code(self, position):
        return self._int_codes[position]

    @property
    def next_instruction(self):
        next_instruction = self._next_instruction
        self._next_instruction += 4
        return next_instruction

    def run(self):
        instruction_offset = self.next_instruction

        opcode = self._int_codes[instruction_offset]

        if opcode == InstructionSet.OpCodes.HALT:
            raise InstructionSet.Halt

        arg1_position = self._int_codes[instruction_offset + 1]
        arg2_position = self._int_codes[instruction_offset + 2]
        result_position = self._int_codes[instruction_offset + 3]

        if opcode == InstructionSet.OpCodes.ADD:
            self._int_codes[result_position] = self._int_codes[arg1_position] + self._int_codes[arg2_position]
        elif opcode == InstructionSet.OpCodes.MUL:
            self._int_codes[result_position] = self._int_codes[arg1_position] * self._int_codes[arg2_position]
        else:
            raise InstructionSet.InvalidOpCode(opcode, instruction_offset)


def parse_input():
    """
    Parse input.txt to an InstructionSet
    """
    instruction_set = InstructionSet()

    with open('input.txt', 'r') as txt:
        for position, code in enumerate(txt.read().strip().split(',')):
            instruction_set.add_int_code(position, code)

    return instruction_set


def main():
    instruction_set = parse_input()

    instruction_set.add_int_code(1, 12)
    instruction_set.add_int_code(2, 2)

    try:
        while True:
            instruction_set.run()
    except InstructionSet.Halt:
        pass
    except InstructionSet.InvalidOpCode as exc:
        print(exc)

    print(f'Part One: {instruction_set.get_int_code(0)}')


if __name__ == '__main__':
    main()
