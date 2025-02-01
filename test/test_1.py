import os
import sys
from test import runners

# https://docs.pytest.org/en/latest/goodpractices.html#tests-outside-application-code
sys.path.insert(0, os.path.abspath("pyshell"))  # isort:skip
# pylint: disable=wrong-import-position


def test_command_line_separator_single_semi_colon_no_leading_space_no_trailing_space() -> (
    None
):
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly.
    """

    # Arrange
    supplied_input = """echo 1;echo 2"""

    expected_output = "1\n2"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_single_semi_colon_with_leading_space_with_trailing_space() -> (
    None
):
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly.
    """

    # Arrange
    supplied_input = """echo 1 ; echo 2"""

    expected_output = "1\n2"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_exit_as_middle_part() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly
    and parse, but do not execute a command after an exit command.
    """

    # Arrange
    supplied_input = """echo 1 ; exit 1; echo 2"""

    expected_output = "1"
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_valid_semicolon_at_end() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    it is the last character in the line.
    """

    # Arrange
    supplied_input = """echo 1 ; echo 2; echo 3;"""

    expected_output = "1\n2\n3"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_invalid_semicolon_at_start() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    it is the first character in the line.
    """

    # Arrange
    supplied_input = """;echo 1"""

    expected_output = "bash: syntax error near unexpected token `;`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_invalid_semicolons_at_start() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    they are the first characters in the line.
    """

    # Arrange
    supplied_input = """;;echo 1"""

    expected_output = "bash: syntax error near unexpected token `;;`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_invalid_semicolons_in_middle() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    they are in the middle of the line.
    """

    # Arrange
    supplied_input = """echo 1;;echo 2"""

    expected_output = "bash: syntax error near unexpected token `;;`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_invalid_semicolons_at_end() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    they are in the end of the line.
    """

    # Arrange
    supplied_input = """echo 1;echo 2;;"""

    expected_output = "bash: syntax error near unexpected token `;;`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_only_whitespace_between_them() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    they are in the middle of the line with only whitespace between them.
    """

    # Arrange
    supplied_input = """echo 1; ;echo 2;"""

    expected_output = "bash: syntax error near unexpected token `;`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_semi_colons_with_only_whitespace_between_them_at_end() -> (
    None
):
    """
    Test to make sure that the processor (with echo for help) processes the semi-colon separator properly if
    they are at the end of the line with only whitespace between them.
    """

    # Arrange
    supplied_input = """echo 1;echo 2; ;"""

    expected_output = "bash: syntax error near unexpected token `;`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_true_statement_followed_by_if_true_operator() -> None:
    """
    Test to make sure that the processor (with echo for help) processes if a statement that returns true (0)
    is followed by the if true operator.
    """

    # Arrange
    supplied_input = """true && echo 1"""

    expected_output = "1"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_false_statement_followed_by_if_true_operator() -> None:
    """
    Test to make sure that the processor (with echo for help) processes if a statement that returns false (non-0)
    is followed by the if true operator.
    """

    # Arrange
    supplied_input = """false && echo 1"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_true_statement_followed_by_if_false_operator() -> None:
    """
    Test to make sure that the processor (with echo for help) processes if a statement that returns true (0)
    is followed by the if false operator.
    """

    # Arrange
    supplied_input = """true || echo 1"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_false_statement_followed_by_if_false_operator() -> None:
    """
    Test to make sure that the processor (with echo for help) processes if a statement that returns false (non-0)
    is followed by the if false operator.
    """

    # Arrange
    supplied_input = """false || echo 1"""

    expected_output = "1"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_true_statement_followed_by_double_if_true_operator() -> (
    None
):
    """
    Test to make sure that the processor (with echo for help) processes if a statement that returns true (0)
    is followed by two true operators.
    """

    # Arrange
    supplied_input = """true && && echo 1"""

    expected_output = "bash: syntax error near unexpected token `&&`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_command_line_separator_true_statement_followed_by_double_if_false_operator() -> (
    None
):
    """
    Test to make sure that the processor (with echo for help) processes if a statement that returns true (0)
    is followed by two false operators.
    """

    # Arrange
    supplied_input = """true || || echo 1"""

    expected_output = "bash: syntax error near unexpected token `||`"
    expected_error = ""
    expected_return_code = 2

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
