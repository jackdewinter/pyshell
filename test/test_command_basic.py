import io
import os
import sys

from pyshell.command_processor import CommandProcessor
from test import runners
from test.pytest_execute import InProcessResult, SystemState


# https://docs.pytest.org/en/latest/goodpractices.html#tests-outside-application-code
sys.path.insert(0, os.path.abspath("pyshell"))  # isort:skip
# pylint: disable=wrong-import-position


def test_command_line_with_baskslash_before_single_quotes() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the backslash character to escape a single quote character.
    """

    # Arrange
    supplied_input = """echo \\'abcdefghi\\'"""

    expected_output = "'abcdefghi'"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_baskslash_before_double_quotes() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the backslash character to escape a double quote character.
    """

    # Arrange
    supplied_input = "echo \\\"abcdefghi\\\""

    expected_output = "\"abcdefghi\""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_baskslash_at_end_of_line() -> None:
    """
    Test to make sure that the processor (with echo for help) processes the backslash character to escape the end of line.
    """

    # Arrange
    supplied_input = "echo abcdefghi\\\njkl"

    expected_output = "abcdefghijkl"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_single_quotes_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes single quote characters around a complete 'word'.
    """

    # Arrange
    supplied_input = """echo 'abcdefghi'"""

    expected_output = "abcdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_single_quotes_within() -> None:
    """
    Test to make sure that the processor (with echo for help) processes single quote characters within a complete 'word'.
    """

    # Arrange
    supplied_input = """echo abc'def'ghi"""

    expected_output = "abcdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_single_quotes_and_backslash_within() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a backslash within single quote characters as just another character.
    """

    # Arrange
    supplied_input = """echo 'abc\\defghi'"""

    expected_output = "abc\\defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_single_quotes_and_double_quotes_within() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote within single quote characters as just another character.
    """

    # Arrange
    supplied_input = """echo 'abc\"defghi'"""

    expected_output = "abc\"defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_single_quotes_spanning_lines() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a single quote string that spans lines
    """

    # Arrange
    supplied_input = """echo 'abcdef\nghi'"""

    expected_output = "abcdef\nghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_single_quotes_no_close() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a single quote with no matching close single quote as an error.
    """

    # Arrange
    supplied_input = """echo 'abcdefghi"""

    expected_output = ""
    expected_error = "bash: unexpected EOF while looking for matching `'`"
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes double quote characters around a complete 'word'.
    """

    # Arrange
    supplied_input = "echo \"abcdefghi\""

    expected_output = "abcdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_within() -> None:
    """
    Test to make sure that the processor (with echo for help) processes double quote characters within a 'word'.
    """

    # Arrange
    supplied_input = "echo abc\"def\"ghi"

    expected_output = "abcdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_no_close() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote with no matching close double quote as an error.
    """

    # Arrange
    supplied_input = """echo \"abcdefghi"""

    expected_output = ""
    expected_error = "bash: unexpected EOF while looking for matching `\"`"
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_spanning_lines() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote string that spans lines
    """

    # Arrange
    supplied_input = """echo \"abcdef\nghi\""""

    expected_output = "abcdef\nghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_and_backslash_backslash() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote string containing a backslash-backslash combo.
    """

    # Arrange
    supplied_input = "echo \"abc\\\\defghi\""

    expected_output = "abc\\defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_and_backslash_double_quote() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote string containing a backslash-double quote combo.
    """

    # Arrange
    supplied_input = "echo \"abc\\\"defghi\""

    expected_output = "abc\"defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_and_backslash_newline() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote string containing a backslash-newline combo.
    """

    # Arrange
    supplied_input = "echo \"abc\\\ndefghi\""

    expected_output = "abc\ndefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_double_quotes_and_backslash_other() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a double quote string containing a backslash-other combo
    where other is not one of the special characters.
    """

    # Arrange
    supplied_input = "echo \"abc\\qdefghi\""

    expected_output = "abc\\qdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes ansi quote sequences around a complete 'word'.
    """

    # Arrange
    supplied_input = "echo $'abcdefghi'"

    expected_output = "abcdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_within() -> None:
    """
    Test to make sure that the processor (with echo for help) processes ansi quote sequences within a 'word'.
    """

    # Arrange
    supplied_input = "echo abc$'def'ghi"

    expected_output = "abcdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_no_close() -> None:
    """
    Test to make sure that the processor (with echo for help) processes ansi quote sequences with no matching close single quote as an error.
    """

    # Arrange
    supplied_input = """echo $'abcdefghi"""

    expected_output = ""
    expected_error = "bash: unexpected EOF while looking for matching `'`"
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_spanning_lines() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi quote string that spans lines
    """

    # Arrange
    supplied_input = """echo abc$'def\nghi'"""

    expected_output = "abcdef\nghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_backslash() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-backslash combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\\\defghi'"

    expected_output = "abc\\defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_single_quote() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-single quote combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\'defghi'"

    expected_output = "abc'defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_double_quote() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-double quote combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\\"defghi'"

    expected_output = "abc\"defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_question_mark() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-question mark combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\?defghi'"

    expected_output = "abc?defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_alert() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-alert combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\adefghi'"

    expected_output = "abc\adefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_backspace() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-backspace combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\bdefghi'"

    expected_output = "abc\bdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_formfeed() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-formfeed combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\fdefghi'"

    expected_output = "abc\fdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_newline() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-newline combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\ndefghi'"

    expected_output = "abc\ndefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_carriage_return() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-carriage return combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\rdefghi'"

    expected_output = "abc\rdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_horizontal_tab() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-horizontal tab combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\tdefghi'"

    expected_output = "abc\tdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_special_vertical_tab() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-special-veritcal tab combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\vdefghi'"

    expected_output = "abc\vdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_newline() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-newline combo.
    """

    # Arrange
    supplied_input = "echo $'abc\\\ndefghi'"

    expected_output = "abc\\\ndefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_other() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-other.
    """

    # Arrange
    supplied_input = "echo $'abc\\qdefghi'"

    expected_output = "abc\\qdefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_octal_one_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-octal with one digit alone.
    """

    # Arrange
    supplied_input = "echo $'abc\\7defghi'"

    expected_output = "abc\x07defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_octal_one_at_end_of_line() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-octal with one digit at the end of a line.
    """

    # Arrange
    supplied_input = "echo $'abc\\7\ndefghi'"

    expected_output = "abc\x07\ndefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_octal_two_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-octal with two digits alone.
    """

    # Arrange
    supplied_input = "echo $'abc\\42defghi'"

    expected_output = "abc\"defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_octal_three_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-octal with three digits alone.
    """

    # Arrange
    supplied_input = "echo $'abc\\042defghi'"

    expected_output = "abc\"defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_octal_four_alone() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-octal with four digits, only taking the first 3.
    """

    # Arrange
    supplied_input = "echo $'abc\\0420defghi'"

    expected_output = "abc\"0defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_hex_one() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-2 digit hex, with one digit.
    """

    # Arrange
    supplied_input = "echo $'abc\\xaxefghi'"

    expected_output = "abc\nxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_hex_two() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-2 digit hex, with two digits.
    """

    # Arrange
    supplied_input = "echo $'abc\\x0axefghi'"

    expected_output = "abc\nxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
def test_command_line_with_ansi_quotes_and_backslash_hex_three() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-2 digit hex, with three digits.
    """

    # Arrange
    supplied_input = "echo $'abc\\x0aaxefghi'"

    expected_output = "abc\naxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_small_u_one() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-small unicode, with one digit.
    """

    # Arrange
    supplied_input = "echo $'abc\\uaxefghi'"

    expected_output = "abc\nxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_small_u_four() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-2 digit hex, with two digits.
    """

    # Arrange
    supplied_input = "echo $'abc\\u000axefghi'"

    expected_output = "abc\nxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_small_u_five() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-2 digit hex, with three digits.
    """

    # Arrange
    supplied_input = "echo $'abc\\u000aaxefghi'"

    expected_output = "abc\naxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_big_u_one() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-big unicode, with one digit.
    """

    # Arrange
    supplied_input = "echo $'abc\\Uaxefghi'"

    expected_output = "abc\nxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_big_u_eight() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-big unicode, with eight digits.
    """

    # Arrange
    supplied_input = "echo $'abc\\U0000000axefghi'"

    expected_output = "abc\nxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_backslash_big_u_nine() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-big unicode, with nine digits.
    """

    # Arrange
    supplied_input = "echo $'abc\\U0000000aaxefghi'"

    expected_output = "abc\naxefghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_control_letter() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-control with a letter.
    """

    # Arrange
    supplied_input = "echo $'abc\\cadefghi'"

    expected_output = "abc\x01defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_control_number() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-control with a number.
    """

    # Arrange
    supplied_input = "echo $'abc\\c0defghi'"

    expected_output = "abc\x10defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

def test_command_line_with_ansi_quotes_and_non_ascii_character() -> None:
    """
    Test to make sure that the processor (with echo for help) processes a ansi string containing a backslash-control with a number.
    """

    # Arrange
    supplied_input = "echo $'abc\\c®defghi'"

    expected_output = "abc\\c®defghi"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
