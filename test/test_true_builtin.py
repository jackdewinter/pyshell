from test import runners

def test_true_command_simple() -> None:
    """
    Test to make sure that we can invoke a true command.
    """

    # Arrange
    supplied_input = """true"""

    expected_output = ""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)

