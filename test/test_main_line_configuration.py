"""
Module for tests of the main line of the application.
"""

# pylint: disable=unused-import
import json
import os
import sys
from test.patches import (  # noqa: F401
    MOCK_GIT_BRANCH_NAME,
    MOCK_HOST_NAME,
    mock_gethostname_impl,
    mock_is_file_for_default_configuration_impl,
    mock_subprocess_run_git_branch_impl,
    set_environment_simulating_execution_in_ps1,
    set_environment_simulating_user_name,
)
from test.test_main_line import ApplicationMainline
from test.utils import create_temporary_configuration_file

import yaml

from pyshell.file_path_helpers import FilePathHelpers

# pylint: enable=unused-import


def test_mainline_configuration_default(
    mock_is_file_for_default_configuration,
    mock_gethostname,
    mock_subprocess_run_git_branch,
) -> None:
    """
    Test to make sure that we execute the "default" settings with the "run" command.
    """

    # Arrange
    _ = (
        mock_is_file_for_default_configuration,
        mock_gethostname,
        mock_subprocess_run_git_branch,
    )
    application_runner = ApplicationMainline()
    arguments_to_use = ["run"]
    user_name_to_test_for = "bob"
    current_directory = FilePathHelpers.normalize_path(os.getcwd())

    expected_output = f"""[{user_name_to_test_for}@{MOCK_HOST_NAME}] [{current_directory}] br[{MOCK_GIT_BRANCH_NAME}] prd[{current_directory}]
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


def test_mainline_configuration_empty() -> None:
    """
    Test to make sure that we simulate an empty configuration as if invoked from the PS1.
    The "cannot load configuration" message should be hidden and a "run from" message displayed
    along with the simple command line.
    """
    # Arrange
    application_runner = ApplicationMainline()
    with create_temporary_configuration_file("") as config_path:
        arguments_to_use = ["--config", config_path, "run"]

        main_file_path = os.path.join(
            os.path.basename(__file__), "..", "pyshell", "main.py"
        )
        assert os.path.isfile(main_file_path)
        main_file_path = os.path.abspath(main_file_path)

        expected_output = f"""An error occurred. To debug the error, run the command line:
  {sys.executable} {main_file_path} --config {config_path} run\n$\a""".replace(
            "\a", " "
        )
        expected_error = ""
        expected_return_code = 0

        # Act
        with set_environment_simulating_execution_in_ps1():
            execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_bad_configuration_invoked_from_ps1() -> None:
    """
    Test to make sure that we simulate an bad configuration as if invoked from the PS1.
    The "cannot load configuration" message should be hidden and a "run from" message displayed
    along with the simple command line.
    """

    # Arrange
    application_runner = ApplicationMainline()
    with create_temporary_configuration_file("abc") as config_path:
        arguments_to_use = ["--config", config_path, "run"]

        main_file_path = os.path.join(
            os.path.basename(__file__), "..", "pyshell", "main.py"
        )
        assert os.path.isfile(main_file_path)
        main_file_path = os.path.abspath(main_file_path)

        expected_output = f"""An error occurred. To debug the error, run the command line:
  {sys.executable} {main_file_path} --config {config_path} run\n$\a""".replace(
            "\a", " "
        )
        expected_error = ""
        expected_return_code = 0

        # Act
        with set_environment_simulating_execution_in_ps1():
            execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_bad_configuration_invoked_normally() -> None:
    """
    Test to make sure that we simulate a bad configuration when invoked normally.
    The "cannot load configuration" message should be visible and stop execution.
    """
    # Arrange
    application_runner = ApplicationMainline()
    with create_temporary_configuration_file("abc") as config_path:
        arguments_to_use = ["--config", config_path, "run"]

        expected_output = ""
        expected_error = f"""

Specified configuration file '{config_path}' was not parseable as a JSON, YAML, or TOML file."""
        expected_return_code = 1

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_missing_configuration_invoked_normally() -> None:
    """
    Test to make sure that we simulate a specified configuration file that does not exist.
    The "cannot load configuration" message should be visible and stop execution.
    """

    # Arrange
    application_runner = ApplicationMainline()
    config_path = os.path.join(os.getcwd(), "this-is-not-a-file")
    assert not os.path.isfile(config_path)
    arguments_to_use = ["--config", config_path, "run"]

    expected_output = ""
    expected_error = f"""

Specified configuration file `{FilePathHelpers.normalize_path(config_path)}` does not exist."""
    expected_return_code = 1

    # Act
    execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_json_configuration_invoked_normally() -> None:
    """
    Test to make sure that we simulate a specified, valid JSON configuration file invoked normally.
    The "cannot load configuration" message should be visible and stop execution.
    """

    # Arrange
    json_configuration = {
        "items": {
            "prompt": {"type": "text", "text": "\n--> "},
        }
    }

    application_runner = ApplicationMainline()
    with create_temporary_configuration_file(
        json.dumps(json_configuration)
    ) as config_path:
        arguments_to_use = ["--config", config_path, "run"]

        expected_output = "-->\a".replace("\a", " ")
        expected_error = ""
        expected_return_code = 0

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_yaml_configuration_invoked_normally() -> None:
    """
    Test to make sure that we simulate a specified, valid YAML configuration file invoked normally.
    The "cannot load configuration" message should be visible and stop execution.
    """

    # Arrange
    json_configuration = {
        "items": {
            "prompt": {"type": "text", "text": "\n--> "},
        }
    }

    application_runner = ApplicationMainline()
    with create_temporary_configuration_file(
        yaml.dump(json_configuration)
    ) as config_path:
        arguments_to_use = ["--config", config_path, "run"]

        expected_output = "-->\a".replace("\a", " ")
        expected_error = ""
        expected_return_code = 0

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_toml_configuration_invoked_normally() -> None:
    """
    Test to make sure that we simulate a specified, valid TOML configuration file invoked normally.
    The "cannot load configuration" message should be visible and stop execution.
    """

    # Arrange
    toml_configuration = """
[items]
prompt.type = "text"
prompt.text = \"\"\"abc
--> \"\"\"
"""

    application_runner = ApplicationMainline()
    with create_temporary_configuration_file(toml_configuration) as config_path:
        arguments_to_use = ["--config", config_path, "run"]

        expected_output = """abc
-->\a""".replace(
            "\a", " "
        )
        expected_error = ""
        expected_return_code = 0

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_json_configuration_with_command_line_override() -> None:
    """
    Test to make sure that we simulate a specified, valid JSON configuration file invoked normally,
    but with a command line override that provide for a "unknown type" error.  This will properly
    report tha the override was bad.
    """

    # Arrange
    json_configuration = {
        "items": {
            "prompt": {"type": "text", "text": "\n--> "},
        }
    }

    application_runner = ApplicationMainline()
    with create_temporary_configuration_file(
        json.dumps(json_configuration)
    ) as config_path:
        arguments_to_use = [
            "--config",
            config_path,
            "--set",
            "items.prompt.type=fred",
            "run",
        ]

        expected_output = ""
        expected_error = """Unexpected Error(ValueError): Property 'items.prompt' has a type of 'fred' which is not supported."""
        expected_return_code = 1

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_json_configuration_with_command_line_strict_mode() -> (
    None
):
    """
    Test to make sure that we simulate a command line override that provides for a
    strictly defined boolean value for the "strict-config" setting, which is always
    interpretted strictly.
    """

    # Arrange
    json_configuration = {
        "items": {
            "prompt": {"type": "text", "text": "\n--> "},
        }
    }

    application_runner = ApplicationMainline()
    with create_temporary_configuration_file(
        json.dumps(json_configuration)
    ) as config_path:
        arguments_to_use = [
            "--config",
            config_path,
            "--set",
            "mode.strict-config=$!True",
            "run",
        ]

        expected_output = "-->\a".replace("\a", " ")
        expected_error = ""
        expected_return_code = 0

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)


def test_mainline_configuration_json_configuration_with_command_line_strict_mode_bad_specifier() -> (
    None
):
    """
    Test to make sure that we simulate a command line override that provides for a
    loosely defined boolean value for the "strict-config" setting, which is always
    interpretted strictly.
    """

    # Arrange
    json_configuration = {
        "items": {
            "prompt": {"type": "text", "text": "\n--> "},
        }
    }

    application_runner = ApplicationMainline()
    with create_temporary_configuration_file(
        json.dumps(json_configuration)
    ) as config_path:
        arguments_to_use = [
            "--config",
            config_path,
            "--set",
            "mode.strict-config=True",
            "run",
        ]

        expected_output = ""
        expected_error = (
            "The value for property 'mode.strict-config' must be of type 'bool'."
        )
        expected_return_code = 1

        # Act
        execute_result = application_runner.invoke_main(arguments=arguments_to_use)

    # Assert
    execute_result.assert_results(expected_output, expected_error, expected_return_code)
