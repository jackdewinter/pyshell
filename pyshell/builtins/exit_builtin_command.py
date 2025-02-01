import argparse
from typing import List

from pyshell.builtin_command import BuiltinCommand


class ExitBuiltinCommand(BuiltinCommand):
    def __init__(self):
        super().__init__("exit")

    def execute_command(self, arguments: List[str], stdout, stderr):
        if not arguments:
            return 0, True

        parser = argparse.ArgumentParser(
            description="Exit the shell.",
            add_help=False,
            prog="exit",
            epilog="Exits the shell with a status of `n`.  If `n` is omitted, the exit status is that of the last command executed.",
        )
        parser.add_argument(
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )
        parser.add_argument("n", help="Exit status to return from the shell.")
        try:
            parsed_arguments, _ = parser.parse_known_args(arguments)

            return_code = 2
            try:
                return_code = int(parsed_arguments.n)
            except ValueError:
                print(
                    f"base: exit: {parsed_arguments.n}: numeric argument required",
                    file=stderr,
                )
            return return_code, True
        except SystemExit:
            return 2
