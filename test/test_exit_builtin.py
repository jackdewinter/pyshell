from test import runners


def test_exit_command_simple() -> None:
    """
    Test to make sure that we can invoke the exit command.
    """

    # Arrange
    supplied_input = """exit"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_exit_command_with_argument_zero() -> None:
    """
    Test to make sure that we can invoke the exit command.
    """

    # Arrange
    supplied_input = """exit 0"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_exit_command_with_parameter_one() -> None:
    """
    Test to make sure that we can invoke the exit command with the argument 1.
    """

    # Arrange
    supplied_input = """exit 1"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_exit_command_with_parameter_alphanumeric() -> None:
    """
    Test to make sure that we can invoke the exit command with and alphanumeric value.
    """

    # Arrange
    supplied_input = """exit a1"""

    expected_output = ""
    expected_error = "base: exit: a1: numeric argument required"
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_exit_command_with_argument_help() -> None:
    """
    Test to make sure that we can invoke the exit command.
    """

    # Arrange
    supplied_input = """exit --help"""

    expected_output = """usage: exit [--help] n

Exit the shell.

positional arguments:
  n       Exit status to return from the shell.

optional arguments:
  --help  Show this help message and exit.

Exits the shell with a status of `n`. If `n` is omitted, the exit status is
that of the last command executed."""

    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
