

class ProgramHalted(BaseException):
    pass


class WaitingForInput(BaseException):
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
