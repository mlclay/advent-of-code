#!/usr/bin/python3
from collections import defaultdict
from queue import Queue, Empty


class Instruction:

    class Method:

        class ParameterMode:
            POSITION = 0
            IMMEDIATE = 1
            RELATIVE = 2

        class ParameterReturnType:
            INTERPRET = 0
            LITERAL = 1

        def __call__(self, context):
            self._set_parameter_return_type(context)
            return self._handler(context)

        def _set_parameter_return_type(self, context):
            for parameter in context.instruction_parameters:
                parameter['return_type'] = Instruction.Method.ParameterReturnType.INTERPRET

        def _handler(self, context):
            raise NotImplementedError()

        @staticmethod
        def update_execution_pointer(context):
            context.execution_pointer += len(context.instruction_parameters) + 1

        def get_parameter_values(self, context):
            parameter_values = []

            for parameter in context.instruction_parameters:
                mode = parameter['mode']
                value = parameter['value']
                return_type = parameter['return_type']

                if mode == Instruction.Method.ParameterMode.POSITION:
                    if return_type == Instruction.Method.ParameterReturnType.INTERPRET:
                        parameter_values.append(context.program_memory[value])
                    else:
                        parameter_values.append(value)
                elif mode == Instruction.Method.ParameterMode.IMMEDIATE:
                    parameter_values.append(value)
                elif mode == Instruction.Method.ParameterMode.RELATIVE:
                    if return_type == Instruction.Method.ParameterReturnType.INTERPRET:
                        parameter_values.append(context.program_memory[context.relative_base + value])
                    else:
                        parameter_values.append(context.relative_base + value)
                else:
                    raise InvalidParameterMode(mode)

            return parameter_values

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

        # ParameterMode modes are RtL
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
        if context.debug:
            print(f'Executing {self.method.__class__.__name__} with {context.instruction_parameters}')
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

    class ExecutionContext:
        def __init__(self,
                     extended_opcode=None,
                     execution_pointer=None,
                     program_memory=None,
                     instruction_parameters=None,
                     input_queue=None,
                     output_queue=None,
                     relative_base=0):
            self.extended_opcode = extended_opcode
            self.execution_pointer = execution_pointer
            self.program_memory = program_memory
            self.instruction_parameters = instruction_parameters
            self.input_queue = input_queue
            self.output_queue = output_queue
            self.relative_base = relative_base
            self.debug = False

        def __str__(self):
            return f'Execution Context: ' \
                   f'[{self.extended_opcode}] @{self.execution_pointer} with {self.instruction_parameters}'

    def __init__(self):
        self._memory = defaultdict(int)
        self._instructions = []
        self._next_instruction = 0
        self._relative_base_offset = 0
        self._initialize_instruction_set()
        self._input_queue = Queue()
        self._output_queue = Queue()

    def _initialize_instruction_set(self):
        self._instructions.append(Instruction(1, 3, AddMethod()))
        self._instructions.append(Instruction(2, 3, MulMethod()))
        self._instructions.append(Instruction(3, 1, StoreInputMethod()))
        self._instructions.append(Instruction(4, 1, OutputAddressMethod()))
        self._instructions.append(Instruction(5, 2, JmpTrueMethod()))
        self._instructions.append(Instruction(6, 2, JmpFalseMethod()))
        self._instructions.append(Instruction(7, 3, LessThanMethod()))
        self._instructions.append(Instruction(8, 3, EqualsMethod()))
        self._instructions.append(Instruction(9, 1, UpdateRelativeBaseMethod()))
        self._instructions.append(Instruction(99, 0, HaltMethod()))

    def __str__(self):
        return ','.join([str(x) for x in self._memory.values()])

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

    def queue_input(self, value):
        self._input_queue.put(value)

    def get_output(self):
        return self._output_queue.get()

    def link_output_to(self, other):
        if not isinstance(other, Program):
            raise Exception(f'link_output_to requires another Program instance')
        other._input_queue = self._output_queue

    def execute_next(self):
        extended_opcode = self.get_memory_address(self._next_instruction)
        instruction = self.get_instruction_by_opcode(extended_opcode)

        execution_context = Program.ExecutionContext(
            extended_opcode=extended_opcode,
            execution_pointer=self._next_instruction,
            program_memory=self._memory,
            input_queue=self._input_queue,
            output_queue=self._output_queue,
            relative_base=self._relative_base_offset,
        )

        instruction.execute(execution_context)

        self._next_instruction = execution_context.execution_pointer
        self._relative_base_offset = execution_context.relative_base

    def run_to_end(self):
        try:
            while True:
                self.execute_next()
        except ProgramHalted:
            pass
        except InvalidOpCode as exc:
            print(exc)


class AddMethod(Instruction.Method):
    def _set_parameter_return_type(self, context):
        super()._set_parameter_return_type(context)
        context.instruction_parameters[2]['return_type'] = Instruction.Method.ParameterReturnType.LITERAL

    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[2]] = parameter_values[0] + parameter_values[1]
        if context.debug:
            print(f'Put {context.program_memory[parameter_values[2]]} in to {parameter_values[2]}')
        self.update_execution_pointer(context)


class MulMethod(Instruction.Method):
    def _set_parameter_return_type(self, context):
        super()._set_parameter_return_type(context)
        context.instruction_parameters[2]['return_type'] = Instruction.Method.ParameterReturnType.LITERAL

    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[2]] = parameter_values[0] * parameter_values[1]
        if context.debug:
            print(f'Put {context.program_memory[parameter_values[2]]} in to {parameter_values[2]}')
        self.update_execution_pointer(context)


class StoreInputMethod(Instruction.Method):
    def _set_parameter_return_type(self, context):
        super()._set_parameter_return_type(context)
        context.instruction_parameters[0]['return_type'] = Instruction.Method.ParameterReturnType.LITERAL

    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        # context.program_memory[parameter_values[0]] = context.input_queue.get()
        context.program_memory[parameter_values[0]] = int(input(f'BOOST needs input: '))
        if context.debug:
            print(f'Put {context.program_memory[parameter_values[0]]} in to {parameter_values[0]}')
        self.update_execution_pointer(context)


class OutputAddressMethod(Instruction.Method):
    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        # context.output_queue.put(parameter_values[0])
        print(f'[DIAGNOSTIC] {parameter_values[0]}')
        self.update_execution_pointer(context)


class JmpTrueMethod(Instruction.Method):
    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        if context.debug:
            print(f'Jumping to {parameter_values[1]} if {parameter_values[0]} != 0')
        if parameter_values[0] != 0:
            context.execution_pointer = parameter_values[1]
        else:
            self.update_execution_pointer(context)


class JmpFalseMethod(Instruction.Method):
    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        if context.debug:
            print(f'Jumping to {parameter_values[1]} if {parameter_values[0]} == 0')
        if parameter_values[0] == 0:
            context.execution_pointer = parameter_values[1]
        else:
            self.update_execution_pointer(context)


class LessThanMethod(Instruction.Method):
    def _set_parameter_return_type(self, context):
        super()._set_parameter_return_type(context)
        context.instruction_parameters[2]['return_type'] = Instruction.Method.ParameterReturnType.LITERAL

    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        if parameter_values[0] < parameter_values[1]:
            if context.debug:
                print(f'Put 1 in {parameter_values[2]} because {parameter_values[0]} < {parameter_values[1]}')
            context.program_memory[parameter_values[2]] = 1
        else:
            if context.debug:
                print(f'Put 0 in {parameter_values[2]} because {parameter_values[0]} >= {parameter_values[1]}')
            context.program_memory[parameter_values[2]] = 0
        self.update_execution_pointer(context)


class EqualsMethod(Instruction.Method):
    def _set_parameter_return_type(self, context):
        super()._set_parameter_return_type(context)
        context.instruction_parameters[2]['return_type'] = Instruction.Method.ParameterReturnType.LITERAL

    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        if parameter_values[0] == parameter_values[1]:
            if context.debug:
                print(f'Put 1 in {parameter_values[2]} because {parameter_values[0]} == {parameter_values[1]}')
            context.program_memory[parameter_values[2]] = 1
        else:
            if context.debug:
                print(f'Put 0 in {parameter_values[2]} because {parameter_values[0]} != {parameter_values[1]}')
            context.program_memory[parameter_values[2]] = 0
        self.update_execution_pointer(context)


class UpdateRelativeBaseMethod(Instruction.Method):
    def _handler(self, context):
        parameter_values = self.get_parameter_values(context)
        context.relative_base += parameter_values[0]
        self.update_execution_pointer(context)


class HaltMethod(Instruction.Method):
    def _handler(self, context):
        raise ProgramHalted


def main():
    program = Program()
    program.initialize_memory_from_file('input.txt')

    program.run_to_end()


if __name__ == '__main__':
    main()
