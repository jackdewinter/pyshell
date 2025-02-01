import argparse
from typing import List
from pyshell.builtin_command import BuiltinCommand


class FalseBuiltinCommand(BuiltinCommand):
    def __init__(self):
        super().__init__("false")

    def execute_command(self, arguments:List[str], stdout, stderr):
        return 1
