from collections import defaultdict
from queue import Queue
from exceptions import ProgramHalted, InvalidOpCode
from instruction import BasicInstructionSet


class IntcodeProgram:

    class IOScheme:
        CONSOLE = 1
        QUEUE = 2


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

    def __init__(self, io_scheme=IOScheme.CONSOLE, **kwargs):
        self._memory = defaultdict(int)
        self._instructions = []
        self._next_instruction = 0
        self._relative_base_offset = 0
        self._input_queue = None
        self._output_queue = None

        if io_scheme == IntcodeProgram.IOScheme.QUEUE:
            self._input_queue = kwargs['input_queue'] if 'input_queue' in kwargs else Queue()
            self._output_queue = kwargs['output_queue'] if 'output_queue' in kwargs else Queue()

        self._initialize_instruction_set()

    def _initialize_instruction_set(self):
        for instruction in BasicInstructionSet.get():
            self._instructions.append(instruction)

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
        if not self._input_queue:
            raise Exception(f'Queue invalid for current IOScheme')
        self._input_queue.put(value)

    def get_output(self, block=True):
        if not self._output_queue:
            raise Exception(f'Queue invalid for current IOScheme')
        return self._output_queue.get(block=block)

    def link_output_to(self, other):
        if not self._output_queue or not other._input_queue:
            raise Exception(f'Queue invalid for current IOScheme')
        if not isinstance(other, IntcodeProgram):
            raise Exception(f'link_output_to requires another IntcodeProgram instance')
        other._input_queue = self._output_queue

    def execute_next(self):
        extended_opcode = self.get_memory_address(self._next_instruction)
        instruction = self.get_instruction_by_opcode(extended_opcode)

        execution_context = IntcodeProgram.ExecutionContext(
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
