from test import runners

def test_false_command_simple() -> None:
    """
    Test to make sure that we can invoke a false command.
    """

    # Arrange
    supplied_input = """false"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

