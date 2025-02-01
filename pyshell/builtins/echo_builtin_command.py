from typing import List

from pyshell.builtin_command import BuiltinCommand


class EchoBuiltinCommand(BuiltinCommand):
    def __init__(self):
        super().__init__("echo")

    def execute_command(self, arguments: List[str], stdout, stderr):
        print(" ".join(arguments), file=stdout)
        return 0
