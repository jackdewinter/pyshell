"""
Tests for the mainline of the application.
"""

import os
from test.pytest_execute import InProcessExecution

from typing_extensions import override

from pyshell.__main__ import main

from pyshell.main import PyShell  # isort:skip


class ApplicationMainline(InProcessExecution):
    """
    Class to provide for a local instance of an InProcessExecution class.
    """

    def __init__(self, use_module=False, use_main=False):
        super().__init__()
        self.__use_main = use_main

        self.__entry_point = "__main.py__" if use_module else "main.py"
        resource_directory = os.path.join(os.getcwd(), "test", "resources")
        assert os.path.exists(resource_directory)
        assert os.path.isdir(resource_directory)
        self.resource_directory = resource_directory

    @override
    def execute_main(self, direct_arguments=None):
        if self.__use_main:
            main()
        else:
            PyShell().main(direct_args=direct_arguments)

    @override
    def get_main_name(self):
        return self.__entry_point


def test_true_command_simple() -> None:
    """
    Test to make sure that we can invoke a true command.
    """

    # Arrange
    application_runner = ApplicationMainline()
    # supplied_arguments = """true"""

    expected_output = """usage: main.py [-h] [--stack-trace]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE]
               {init,version} ...

Lint any found Markdown files.

positional arguments:
  {init,version}
    init                Initialize the...
    version             Version of the application.

optional arguments:
  -h, --help            show this help message and exit
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        minimum level required to log messages
  --log-file LOG_FILE   destination file for log messages"""
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = application_runner.invoke_main(arguments=[])

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
