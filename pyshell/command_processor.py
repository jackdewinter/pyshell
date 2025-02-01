import os
import sys

from pyshell.builtins.echo_builtin_command import EchoBuiltinCommand
from pyshell.builtins.exit_builtin_command import ExitBuiltinCommand
from pyshell.builtins.false_builtin_command import FalseBuiltinCommand
from pyshell.builtins.true_builtin_command import TrueBuiltinCommand
from pyshell.environment_processor import EnvironmentProcessor
from pyshell.extended_cmd import ExtendedCmd, Separator


class CommandProcessor(ExtendedCmd):
    __builtins = [
        ExitBuiltinCommand(),
        EchoBuiltinCommand(),
        TrueBuiltinCommand(),
        FalseBuiltinCommand(),
    ]

    def __init__(self, script_input=None, stdin=None, stderr=None, stdout=None):

        self.__env = EnvironmentProcessor()

        stdout = stdout if stdout is not None else sys.stdout
        stderr = stderr if stderr is not None else sys.stderr

        super().__init__(stdout, stderr, supplied_input=script_input)

        self.__builtins_map = {}
        for i in CommandProcessor.__builtins:
            self.__builtins_map[i.name] = i

        self.__last_return_code = 0

    def collect_and_process_commands(self) -> int:
        super().command_loop()
        return self.__last_return_code

    def set_return_code(self, return_code):
        self.__last_return_code = return_code

    def process_completed_command_line(self, arguments):

        current_separator = Separator(";")
        continue_processing = True
        while continue_processing and arguments:
            j = 0
            while j < len(arguments):
                if isinstance(arguments[j], Separator):
                    break
                j += 1

            next_set_of_arguments = arguments[:j]

            if current_separator.xx == ";":
                can_execute = True
            elif current_separator.xx == "&&":
                can_execute = not self.__last_return_code
            elif current_separator.xx == "||":
                can_execute = self.__last_return_code
            else:
                assert False, f"Unknown separator {current_separator}"

            if can_execute:
                if next_set_of_arguments[0] in self.__builtins_map:
                    builtin_command = self.__builtins_map[next_set_of_arguments[0]]
                    command_result = builtin_command.execute_command(
                        next_set_of_arguments[1:], self.stdout, self.stderr
                    )
                else:
                    print(f"{arguments[0]}: command not found", file=self.stderr)
                    command_result = 1
                if isinstance(command_result, int):
                    self.__last_return_code = command_result
                    continue_processing = True
                else:
                    assert command_result is not None
                    self.__last_return_code = command_result[0]
                    assert command_result[1]
                    continue_processing = False
            if continue_processing:
                if j < len(arguments):
                    current_separator = arguments[j]
                    arguments = arguments[j + 1 :]
                else:
                    arguments = []
        return continue_processing
