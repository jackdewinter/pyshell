"""
Tests for the mainline of the application.
"""

# pylint: disable=unused-import
import os
import string
from test.patches import (  # noqa: F401
    MOCK_GIT_BRANCH_NAME,
    mock_gethostname_impl,
    mock_is_file_for_default_configuration_impl,
    mock_subprocess_run_git_branch_impl,
    set_environment_simulating_user_name,
)
from test.pytest_execute import InProcessExecution
from test.utils import create_temporary_configuration_file, read_contents_of_text_file

import pytest
from typing_extensions import override

from pyshell.__main__ import main
from pyshell.file_path_helpers import FilePathHelpers
from pyshell.main import PyShell

# pylint: enable=unused-import


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


def test_mainline_no_command() -> None:
    """
    Test to verify that not supplying a command will print out the help.
    """

    # Arrange
    application_runner = ApplicationMainline()

    expected_output = """usage: main.py [-h] [--config CONFIGURATION_FILE] [--set SET_CONFIGURATION]
               [--strict-config] [--stack-trace]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE]
               {init,run,version} ...

Lint any found Markdown files.

positional arguments:
  {init,run,version}
    init                Initialize the...
    run                 Initialize the...
    version             Version of the application.

options:
  -h, --help            show this help message and exit
  --config, -c CONFIGURATION_FILE
                        path to the configuration file to use
  --set, -s SET_CONFIGURATION
                        manually set an individual configuration property
  --strict-config       throw an error if configuration is bad, instead of
                        assuming default
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


def test_mainline_help_command() -> None:
    """
    Test to that asking for the help command will print out the help.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["--help"]

    expected_output = """usage: main.py [-h] [--config CONFIGURATION_FILE] [--set SET_CONFIGURATION]
               [--strict-config] [--stack-trace]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE]
               {init,run,version} ...

Lint any found Markdown files.

positional arguments:
  {init,run,version}
    init                Initialize the...
    run                 Initialize the...
    version             Version of the application.

options:
  -h, --help            show this help message and exit
  --config, -c CONFIGURATION_FILE
                        path to the configuration file to use
  --set, -s SET_CONFIGURATION
                        manually set an individual configuration property
  --strict-config       throw an error if configuration is bad, instead of
                        assuming default
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        minimum level required to log messages
  --log-file LOG_FILE   destination file for log messages"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_log_level_unknown() -> None:
    """
    Test to verify that asking for an unknown (literally) log-level will result
    in an error and output of the available options.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["--log-level", "unknown"]

    expected_output = ""
    expected_error = """usage: main.py [-h] [--config CONFIGURATION_FILE] [--set SET_CONFIGURATION]
               [--strict-config] [--stack-trace]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE]
               {init,run,version} ...
main.py: error: argument --log-level: invalid validate_log_level_type value: 'unknown'"""
    expected_return_code = 2

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_log_level_debug() -> None:
    """
    Test to verify that we can invoke the "init" command to produce text
    that we need to insert into the .bashrc file.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["--log-level", "DEBUG", "init"]

    expected_output = """export PS1="\\$(IS_PYSHELL_PS1=1 /c/Users/jack/.virtualenvs/pyshell-lw4-13FC/Scripts/python.exe /c/enlistments/pyshell/main.py run)"
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_log_file() -> None:
    """
    Test to verify tht we can specify a valid log file name and log level.
    """

    # Arrange
    application_runner = ApplicationMainline()
    with create_temporary_configuration_file("") as configuration_file_name:
        arguments_to_use = [
            "--log-file",
            configuration_file_name,
            "--log-level",
            "DEBUG",
            "init",
        ]

        expected_output = """export PS1="\\$(IS_PYSHELL_PS1=1 /c/Users/jack/.virtualenvs/pyshell-lw4-13FC/Scripts/python.exe /c/enlistments/pyshell/main.py run)"
"""
        expected_error = ""
        expected_return_code = 0

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

        # Assert
        execute_result.assert_results(
            expected_output, expected_error, expected_return_code
        )

        ss = read_contents_of_text_file(configuration_file_name)
        assert "Logging subsystem setup completed." in ss
        assert "Processing command: init" in ss
        assert "Command 'init' completed successfully." in ss


def test_mainline_log_file_bad() -> None:
    """
    Test to verify that specifying a bad name for a log file will be
    caught and result in an error.
    """

    # Arrange
    application_runner = ApplicationMainline()
    assert os.name.lower() == "nt"

    available_drive_letters = [
        f"{d}:" for d in string.ascii_uppercase if os.path.exists(f"{d}:")
    ]
    for i in range(2, 26):
        x = chr(ord("A") + i) + ":"
        if x in available_drive_letters:
            continue
        x = x + "/"
        g = os.path.isdir(x)
        if not g:
            break
    temp_log_file = x + "\\" + "bad_out.log"
    arguments_to_use = ["--log-file", temp_log_file, "--log-level", "DEBUG", "init"]

    expected_output = ""
    expected_error = "Unexpected Error(ApplicationLoggingException): Failure initializing logging subsystem."
    expected_return_code = 1

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_stack_trace() -> None:
    """
    Test to verify that a stack trace will print a proper log of what
    happened to cause the exception that was thrown.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["--stack-trace", "-x-exception", "init"]

    expected_output = ""
    expected_error = """Unexpected Error(PyShellException): Test exception."""
    expected_additional_error = [
        "Exception: Test exception.",
        "Traceback (most recent call last):",
    ]
    expected_return_code = 1

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(
        expected_output,
        expected_error,
        expected_return_code,
        additional_error=expected_additional_error,
    )


def test_mainline_unknown() -> None:
    """
    Test to verify that invoking an 'unknown' (literally) command will result in
    an error and the list of valid choices.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["unknown"]

    expected_output = ""
    expected_error = """usage: main.py [-h] [--config CONFIGURATION_FILE] [--set SET_CONFIGURATION]
               [--strict-config] [--stack-trace]
               [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
               [--log-file LOG_FILE]
               {init,run,version} ...
main.py: error: argument primary_subparser: invalid choice: 'unknown' (choose from init, run, version)
"""
    expected_return_code = 2

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_unknown_via_module() -> None:
    """
    Test to verify that we can invoke the application through its module.
    """

    # Arrange
    application_runner = ApplicationMainline(use_module=True, use_main=True)
    arguments_to_use = ["unknown"]

    expected_output = ""
    expected_error = """usage: __main.py__ [-h] [--config CONFIGURATION_FILE]
                   [--set SET_CONFIGURATION] [--strict-config] [--stack-trace]
                   [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                   [--log-file LOG_FILE]
                   {init,run,version} ...
__main.py__: error: argument primary_subparser: invalid choice: 'unknown' (choose from init, run, version)
"""
    expected_return_code = 2

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


@pytest.mark.skip
def test_mainline_unknown_via_direct_arguments() -> None:
    """
    Test to verify that we can invoke the application using direct arguments.
    Not useful now, but maybe useful later.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["unknown"]

    expected_output = ""
    expected_error = """usage: run_pytest_script.py [-h] [--stack-trace]
                            [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                            [--log-file LOG_FILE]
                            {init,run,version} ...
run_pytest_script.py: error: argument primary_subparser: invalid choice: 'unknown' (choose from 'init', 'run', 'version')
"""
    expected_return_code = 2

    # Act
    execute_result = application_runner.invoke_main(
        arguments=arguments_to_use, use_direct_arguments=True
    )

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_version() -> None:
    """
    Test to verify that we can get the version number of the application.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["version"]

    expected_output = """0.1.0
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_init() -> None:
    """
    Test to verify that we can invoke the init command.
    """

    # Arrange
    application_runner = ApplicationMainline()
    arguments_to_use = ["init"]

    expected_output = """export PS1="\\$(IS_PYSHELL_PS1=1 /c/Users/jack/.virtualenvs/pyshell-lw4-13FC/Scripts/python.exe /c/enlistments/pyshell/main.py run)"
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_run(
    mock_gethostname,
    mock_subprocess_run_git_branch,
    mock_is_file_for_default_configuration,
) -> None:
    """
    Test to verify that we can execute a simple run command.
    """

    # Arrange
    _ = (
        mock_gethostname,
        mock_subprocess_run_git_branch,
        mock_is_file_for_default_configuration,
    )
    application_runner = ApplicationMainline()
    arguments_to_use = ["run"]
    user_name_to_test_for = "galileo"
    host_name_to_test_for = "scaramouche"
    current_directory = FilePathHelpers.normalize_path(os.getcwd())

    expected_output = f"""[{user_name_to_test_for}@{host_name_to_test_for}] [{current_directory}] br[{MOCK_GIT_BRANCH_NAME}] prd[{current_directory}]
$\a""".replace(
        "\a", " "
    )
    expected_error = ""
    expected_return_code = 0

    # Act
    with set_environment_simulating_user_name(user_name_to_test_for):
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
