from test import runners


def test_echo_command_simple() -> None:
    """
    Test to make sure that we can invoke an echo command with a single parameter.
    """

    # Arrange
    supplied_input = """echo 1"""

    expected_output = "1"
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_result = runners.execute_script_with_direct_inline(supplied_input)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
