"""Module to provide tests for the ProjectDataSource class.
"""

from pyshell.data_sources.base_data_source import ComposerPriorityLevel, PropertyPath
from pyshell.data_sources.project_data_source import ProjectDataSource


def test_project_data_source_name() -> None:
    """Test to verify that the name of the data source is correct."""

    # Arrange
    data_source = ProjectDataSource()

    # Act
    generated_name = data_source.name

    # Assert
    assert generated_name == "project"


def test_project_data_source_get_property_unknown() -> None:
    """Test to verify that asking the data source for an unknown property results in an empty string."""

    # Arrange
    data_source = ProjectDataSource()

    # Act
    generated_value = data_source.get_property("unknown")

    # Assert
    assert generated_value == ""


def test_project_data_source_get_property_dependencies_unknown() -> None:
    """Test to verify that asking for the dependencies with a given name that is not recognized returns an empty list."""

    # Arrange
    data_source = ProjectDataSource()

    # Act
    generated_value = data_source.get_property_dependencies("unknown")

    # Assert
    assert not generated_value


def test_project_data_source_get_property_dependencies_root_directory_no_dynamic() -> (
    None
):
    """Test to verify that the 'root_directory' property composer defaults to the 'system.full_cwd' directory."""

    # Arrange
    data_source = ProjectDataSource()

    # Act
    generated_value = data_source.get_property_dependencies("root_directory")

    # Assert
    assert generated_value == [PropertyPath.from_one("system.full_cwd")]


def test_project_data_source_get_property_dependencies_root_directory_bad_dynamic() -> (
    None
):
    """Test to verify that trying to register against an unknown composer name results in an empty
    list of properties, as no composer is there to collect the property dependencies."""

    # Arrange
    data_source = ProjectDataSource()

    # Act
    data_source.register_dynamic_dependency(
        "unknown", PropertyPath.from_one("system.x"), ComposerPriorityLevel.NORMAL
    )
    generated_value = data_source.get_property_dependencies("unknown")

    # Assert
    assert generated_value == []


def test_project_data_source_get_property_dependencies_root_directory_good_dynamic() -> (
    None
):
    """Test to verify that adding to the 'root_directory' composer properly will result in the
    property path being added to the composer's list."""

    # Arrange
    data_source = ProjectDataSource()

    # Act
    data_source.register_dynamic_dependency(
        "root_directory",
        PropertyPath.from_one("system.root_directory"),
        ComposerPriorityLevel.NORMAL,
    )
    generated_value = data_source.get_property_dependencies("root_directory")

    # Assert
    assert generated_value == [
        PropertyPath.from_one("system.root_directory"),
        PropertyPath.from_one("system.full_cwd"),
    ]
