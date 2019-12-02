#!/usr/bin/python3


class Instruction:
    def __init__(self, opcode, parameter_count, method):
        self.opcode = opcode
        self.parameter_count = parameter_count
        self.method = method

    def __eq__(self, other):
        if isinstance(other, int):
            return self.opcode == other
        if isinstance(other, Instruction):
            return self.opcode == other.opcode
        raise InvalidOpCode(other)

    def execute(self, memory, memory_offset):
        parameters = []
        if self.parameter_count >= 1:
            for index in range(1, self.parameter_count + 1):
                parameters.append(memory[memory_offset + index])
        self.method(memory, parameters)

    def next_instruction_pointer(self, instruction_pointer):
        return instruction_pointer + self.parameter_count + 1


class ProgramHalted(BaseException):
    pass


class InvalidOpCode(BaseException):
    def __init__(self, opcode, instruction_pointer=None):
        self.opcode = opcode
        self.instruction_pointer = instruction_pointer

    def __str__(self):
        return f'Invalid OpCode [{self.opcode}] encountered' \
               f'{f" at pointer {self.instruction_pointer}" if self.instruction_pointer else ""}'


class Program:

    def __init__(self):
        self._memory = {}
        self._instructions = {}
        self._next_instruction = 0

    def __str__(self):
        return ','.join([str(x) for x in self._memory.values()])

    def add_instruction(self, instruction):
        self._instructions[instruction.opcode] = instruction

    def get_instruction_by_opcode(self, opcode):
        try:
            return self._instructions[opcode]
        except KeyError:
            raise InvalidOpCode(opcode)

    def initialize_memory_from_file(self, file_name):
        with open(file_name, 'r') as txt:
            for position, code in enumerate(txt.read().strip().split(',')):
                self.set_memory_address(position, code)

    def set_memory_address(self, address, code):
        self._memory[address] = int(code)

    def get_memory_address(self, address):
        return self._memory[address]

    def run(self):
        instruction = self.get_instruction_by_opcode(self.get_memory_address(self._next_instruction))

        instruction.execute(self._memory, self._next_instruction)

        self._next_instruction = instruction.next_instruction_pointer(self._next_instruction)


ADD_INSTRUCTION = Instruction(1, 3, lambda memory, parameters: memory.update(
    {(parameters[2]): memory[parameters[0]] + memory[parameters[1]]}
))
MUL_INSTRUCTION = Instruction(2, 3, lambda memory, parameters: memory.update(
    {(parameters[2]): memory[parameters[0]] * memory[parameters[1]]}
))
HALT_INSTRUCTION = Instruction(99, 0, lambda memory, parameters=(): (_ for _ in parameters).throw(ProgramHalted))


def main():

    program = Program()

    program.add_instruction(ADD_INSTRUCTION)
    program.add_instruction(MUL_INSTRUCTION)
    program.add_instruction(HALT_INSTRUCTION)

    program.initialize_memory_from_file('input.txt')

    # Reset program state after "1202 program alarm"
    program.set_memory_address(1, 12)
    program.set_memory_address(2, 2)

    try:
        while True:
            program.run()
    except ProgramHalted:
        pass
    except InvalidOpCode as exc:
        print(exc)

    print(f'Part One: {program.get_memory_address(0)}')


if __name__ == '__main__':
    main()
