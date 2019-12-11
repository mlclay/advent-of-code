#!/usr/bin/python3
from queue import Queue, Empty
from exceptions import InvalidOpCode, InvalidParameterMode, ProgramHalted, WaitingForInput


class Instruction:

    class ParameterMode:
        POSITION = 0
        IMMEDIATE = 1
        RELATIVE = 2

    class ParameterReturnType:
        INTERPRET = 0
        LITERAL = 1

    def __init__(self, opcode, parameter_count):
        self.opcode = opcode
        self.parameter_count = parameter_count
        self.parameter_return_type = [Instruction.ParameterReturnType.INTERPRET for _ in range(0, parameter_count)]

    def __eq__(self, other):
        if isinstance(other, int):
            if other >= 100:
                other = int(str(other)[-2:])
            return self.opcode == other
        if isinstance(other, Instruction):
            return self.opcode == other.opcode
        raise InvalidOpCode(other)

    def method(self, context):
        raise NotImplementedError()

    @staticmethod
    def update_execution_pointer(context):
        context.execution_pointer += len(context.instruction_parameters) + 1

    def get_parameter_values(self, context):
        parameter_values = []

        for num, parameter in enumerate(context.instruction_parameters):
            mode = parameter['mode']
            value = parameter['value']
            return_type = self.parameter_return_type[num]

            if mode == Instruction.ParameterMode.POSITION:
                if return_type == Instruction.ParameterReturnType.INTERPRET:
                    parameter_values.append(context.program_memory[value])
                else:
                    parameter_values.append(value)
            elif mode == Instruction.ParameterMode.IMMEDIATE:
                parameter_values.append(value)
            elif mode == Instruction.ParameterMode.RELATIVE:
                if return_type == Instruction.ParameterReturnType.INTERPRET:
                    parameter_values.append(context.program_memory[context.relative_base + value])
                else:
                    parameter_values.append(context.relative_base + value)
            else:
                raise InvalidParameterMode(mode)

        return parameter_values

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
            print(f'Executing {self.__class__.__name__} with {context.instruction_parameters}')

        self.method(context)


class AddInstruction(Instruction):

    def __init__(self):
        super().__init__(1, 3)
        self.parameter_return_type[2] = Instruction.ParameterReturnType.LITERAL

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[2]] = parameter_values[0] + parameter_values[1]
        if context.debug:
            print(f'Put {context.program_memory[parameter_values[2]]} in to {parameter_values[2]}')
        self.update_execution_pointer(context)


class MultiplyInstruction(Instruction):

    def __init__(self):
        super().__init__(2, 3)
        self.parameter_return_type[2] = Instruction.ParameterReturnType.LITERAL

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        context.program_memory[parameter_values[2]] = parameter_values[0] * parameter_values[1]
        if context.debug:
            print(f'Put {context.program_memory[parameter_values[2]]} in to {parameter_values[2]}')
        self.update_execution_pointer(context)


class StoreInputInstruction(Instruction):

    def __init__(self):
        super().__init__(3, 1)
        self.parameter_return_type[0] = Instruction.ParameterReturnType.LITERAL

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        if context.input_queue:
            try:
                context.program_memory[parameter_values[0]] = context.input_queue.get(block=False)
            except Empty:
                raise WaitingForInput()
        else:
            context.program_memory[parameter_values[0]] = int(input(f'BOOST needs input: '))
        if context.debug:
            print(f'Put {context.program_memory[parameter_values[0]]} in to {parameter_values[0]}')
        self.update_execution_pointer(context)


class OutputInstruction(Instruction):

    def __init__(self):
        super().__init__(4, 1)

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        if context.output_queue:
            context.output_queue.put(parameter_values[0])
        else:
            print(f'[DIAGNOSTIC] {parameter_values[0]}')
        self.update_execution_pointer(context)


class JmpNEZInstruction(Instruction):

    def __init__(self):
        super().__init__(5, 2)

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        if context.debug:
            print(f'Jumping to {parameter_values[1]} if {parameter_values[0]} != 0')
        if parameter_values[0] != 0:
            context.execution_pointer = parameter_values[1]
        else:
            self.update_execution_pointer(context)


class JmpEQZInstruction(Instruction):

    def __init__(self):
        super().__init__(6, 2)

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        if context.debug:
            print(f'Jumping to {parameter_values[1]} if {parameter_values[0]} == 0')
        if parameter_values[0] == 0:
            context.execution_pointer = parameter_values[1]
        else:
            self.update_execution_pointer(context)


class LessThanInstruction(Instruction):

    def __init__(self):
        super().__init__(7, 3)
        self.parameter_return_type[2] = Instruction.ParameterReturnType.LITERAL

    def method(self, context):
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


class EqualToInstruction(Instruction):

    def __init__(self):
        super().__init__(8, 3)
        self.parameter_return_type[2] = Instruction.ParameterReturnType.LITERAL

    def method(self, context):
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


class UpdateRelativeBaseInstruction(Instruction):

    def __init__(self):
        super().__init__(9, 1)

    def method(self, context):
        parameter_values = self.get_parameter_values(context)
        context.relative_base += parameter_values[0]
        self.update_execution_pointer(context)


class HaltInstruction(Instruction):

    def __init__(self):
        super().__init__(99, 0)

    def method(self, context):
        raise ProgramHalted


class BasicInstructionSet:

    @staticmethod
    def get():
        return [
            AddInstruction(),
            MultiplyInstruction(),
            StoreInputInstruction(),
            OutputInstruction(),
            JmpNEZInstruction(),
            JmpEQZInstruction(),
            LessThanInstruction(),
            EqualToInstruction(),
            UpdateRelativeBaseInstruction(),
            HaltInstruction(),
        ]
