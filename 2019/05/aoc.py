#!/usr/bin/python3


class Instruction:

    class Method:

        class Parameter:
            MODE_POSITION = 0
            MODE_IMMEDIATE = 1

        def __init__(self):
            self.last_parameter_immediate = True

        def __call__(self, context):
            raise NotImplementedError()

        @staticmethod
        def update_execution_pointer(context):
            context.execution_pointer += len(context.instruction_parameters) + 1

        def get_parameter_values(self, context):
            parameter_values = []

            if self.last_parameter_immediate and context.instruction_parameters:
                context.instruction_parameters[-1]['mode'] = Instruction.Method.Parameter.MODE_IMMEDIATE

            for parameter in context.instruction_parameters:
                mode = parameter['mode']
                value = parameter['value']

                if mode == Instruction.Method.Parameter.MODE_POSITION:
                    parameter_values.append(context.program_memory[value])
                elif mode == Instruction.Method.Parameter.MODE_IMMEDIATE:
                    parameter_values.append(value)
                else:
                    raise InvalidParameterMode(mode)

            return parameter_values

    class ExecutionContext:
        def __init__(self,
                     extended_opcode=None,
                     execution_pointer=None,
                     program_memory=None,
                     instruction_parameters=None):
            self.extended_opcode = extended_opcode
            self.execution_pointer = execution_pointer
            self.program_memory = program_memory
            self.instruction_parameters = instruction_parameters

        def __str__(self):
            return f'Execution Context: ' \
                   f'[{self.extended_opcode}] @{self.execution_pointer} with {self.instruction_parameters}'

    def __init__(self, opcode, parameter_count, method):
        self.opcode = opcode
        self.parameter_count = parameter_count
        self.method = method

        if not isinstance(self.method, Instruction.Method):
            raise Exception(f'Provided method not of class Instruction.Method')

    def __eq__(self, other):
        if isinstance(other, int):
            if other >= 100:
                other = int(str(other)[-2:])
            return self.opcode == other
        if isinstance(other, Instruction):
            return self.opcode == other.opcode
        raise InvalidOpCode(other)

    def parse_extended_opcode(self, extended_opcode):
        if extended_opcode < 100:
            return [0 for _ in range(0, self.parameter_count)]
        # Default parameter mode is 0 for each parameter, if not provided
        extended_opcode = '0' * self.parameter_count + str(extended_opcode)

        # Remove the opcode from the parameters
        extended_opcode = extended_opcode[:-2]

        # Parameter modes are RtL
        extended_opcode = extended_opcode[::-1]

        # Don't return excess default modes
        extended_opcode = extended_opcode[:self.parameter_count]

        return [int(x) for x in extended_opcode]

    def execute(self, context):
        parameter_modes = self.parse_extended_opcode(context.extended_opcode)
        context.instruction_parameters = []
        if self.parameter_count >= 1:
            for index in range(0, self.parameter_count):
                context.instruction_parameters.append({
                    'value': context.program_memory[context.execution_pointer + index + 1],
                    'mode': parameter_modes[index],
                })
        self.method(context)


class ProgramHalted(BaseException):
    pass


class InvalidOpCode(BaseException):
    def __init__(self, opcode, instruction_pointer=None):
        self.opcode = opcode
        self.instruction_pointer = instruction_pointer

    def __str__(self):
        return f'Invalid OpCode [{self.opcode}] encountered' \
               f'{f" at pointer {self.instruction_pointer}" if self.instruction_pointer else ""}'


class InvalidParameterMode(BaseException):
    def __init__(self, parameter_mode):
        self.parameter_mode = parameter_mode

    def __str__(self):
        return f'Invalid ParameterMode [{self.parameter_mode}] encountered'


class Program:

    def __init__(self):
        self._memory = {}
        self._instructions = []
        self._next_instruction = 0

    def __str__(self):
        return ','.join([str(x) for x in self._memory.values()])

    def add_instruction(self, instruction):
        self._instructions.append(instruction)

    def get_instruction_by_opcode(self, opcode):
        try:
            return self._instructions[self._instructions.index(opcode)]
        except KeyError:
            raise InvalidOpCode(opcode)
        except ValueError:
            raise InvalidOpCode(opcode)

    def initialize_memory_from_file(self, file_name):
        with open(file_name, 'r') as txt:
            for position, code in enumerate(txt.read().strip().split(',')):
                self.set_memory_address(position, code)

    def dump_memory(self):
        return dict(self._memory)

    def load_memory(self, memory):
        if not isinstance(memory, dict):
            raise Exception('Failed loading invalid memory')
        self._memory.update(memory)
        self._next_instruction = 0

    def set_memory_address(self, address, code):
        self._memory[address] = int(code)

    def get_memory_address(self, address):
        return self._memory[address]

    def execute_next(self):
        extended_opcode = self.get_memory_address(self._next_instruction)
        instruction = self.get_instruction_by_opcode(extended_opcode)

        execution_context = Instruction.ExecutionContext(extended_opcode=extended_opcode,
                                                         execution_pointer=self._next_instruction,
                                                         program_memory=self._memory)

        instruction.execute(execution_context)

        self._next_instruction = execution_context.execution_pointer

    def run(self):
        try:
            while True:
                self.execute_next()
        except ProgramHalted:
            pass
        except InvalidOpCode as exc:
            print(exc)


class AddMethod(Instruction.Method):
    def __call__(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[2]] = parameter_values[0] + parameter_values[1]
        self.update_execution_pointer(context)


class MulMethod(Instruction.Method):
    def __call__(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[2]] = parameter_values[0] * parameter_values[1]
        self.update_execution_pointer(context)


class StoreInputMethod(Instruction.Method):
    def __call__(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[0]] = int(input('TEST execution requires input: '))
        self.update_execution_pointer(context)


class OutputAddressMethod(Instruction.Method):
    def __call__(self, context):
        self.last_parameter_immediate = False
        parameter_values = self.get_parameter_values(context)
        print(f'[Diagnostic]: {parameter_values[0]}')
        self.update_execution_pointer(context)


class JmpTrueMethod(Instruction.Method):
    def __call__(self, context):
        self.last_parameter_immediate = False
        parameter_values = self.get_parameter_values(context)
        if parameter_values[0] != 0:
            context.execution_pointer = parameter_values[1]
        else:
            self.update_execution_pointer(context)


class JmpFalseMethod(Instruction.Method):
    def __call__(self, context):
        self.last_parameter_immediate = False
        parameter_values = self.get_parameter_values(context)
        if parameter_values[0] == 0:
            context.execution_pointer = parameter_values[1]
        else:
            self.update_execution_pointer(context)


class LessThanMethod(Instruction.Method):
    def __call__(self, context):
        parameter_values = self.get_parameter_values(context)
        if parameter_values[0] < parameter_values[1]:
            context.program_memory[parameter_values[2]] = 1
        else:
            context.program_memory[parameter_values[2]] = 0
        self.update_execution_pointer(context)


class EqualsMethod(Instruction.Method):
    def __call__(self, context):
        parameter_values = self.get_parameter_values(context)
        if parameter_values[0] == parameter_values[1]:
            context.program_memory[parameter_values[2]] = 1
        else:
            context.program_memory[parameter_values[2]] = 0
        self.update_execution_pointer(context)


class HaltMethod(Instruction.Method):
    def __call__(self, context):
        raise ProgramHalted


def main():
    program = Program()

    program.add_instruction(Instruction(1, 3, AddMethod()))
    program.add_instruction(Instruction(2, 3, MulMethod()))
    program.add_instruction(Instruction(3, 1, StoreInputMethod()))
    program.add_instruction(Instruction(4, 1, OutputAddressMethod()))
    program.add_instruction(Instruction(5, 2, JmpTrueMethod()))
    program.add_instruction(Instruction(6, 2, JmpFalseMethod()))
    program.add_instruction(Instruction(7, 3, LessThanMethod()))
    program.add_instruction(Instruction(8, 3, EqualsMethod()))
    program.add_instruction(Instruction(99, 0, HaltMethod()))

    program.initialize_memory_from_file('input.txt')

    program.run()


if __name__ == '__main__':
    main()
