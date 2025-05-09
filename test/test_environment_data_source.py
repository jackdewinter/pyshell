"""Module to provide tests for the EnvironmentDataSource class.
"""

from test.patches import set_environment_simulating_execution_in_ps1

from pyshell.data_sources.environment_data_source import EnvironmentDataSource


def test_environment_data_source_name() -> None:
    """Test to verify that the data source is properly named."""

    # Arrange
    data_source = EnvironmentDataSource()

    # Act
    generated_name = data_source.name

    # Assert
    assert generated_name == "environment"


def test_environment_data_source_get_dynamic_dependencies() -> None:
    """Test to verify that the correct dependencies are set up for the data source."""

    # Arrange
    data_source = EnvironmentDataSource()

    # Act
    generated_dependencies = data_source.get_dynamic_dependencies()

    # Assert
    assert len(generated_dependencies) == 0


def test_environment_data_source_get_property_where_environment_variable_exists() -> (
    None
):
    """Test to verify that an existing environment variable shows up in the data source."""

    # Arrange
    data_source = EnvironmentDataSource()
    env_variable_name = "IS_PYSHELL_PS1"
    expected_value = "1"

    # Act
    with set_environment_simulating_execution_in_ps1():
        property_value = data_source.get_property(env_variable_name)

    # Assert
    assert expected_value == property_value


def test_environment_data_source_get_property_where_environment_variable_not_exists() -> (
    None
):
    """Test to verify that a non-existing environment variable is not accessable from the data source."""

    # Arrange
    data_source = EnvironmentDataSource()
    env_variable_name = "IS_PYSHELL_PS1"
    expected_value = ""

    # Act
    with set_environment_simulating_execution_in_ps1(set_to_active=False):
        property_value = data_source.get_property(env_variable_name)

    # Assert
    assert expected_value == property_value
