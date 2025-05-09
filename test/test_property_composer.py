"""Module to provide tests for the PropertyComposer class.
"""

from pyshell.data_sources.base_data_source import (
    ComposerPriorityLevel,
    PropertyComposer,
    PropertyPath,
)


def test_property_composer_basic_no_default() -> None:
    """Test to verify that a basic composer with no default dependency has no reigstered properties."""

    # Arrange
    expected_name = "basic"
    default_dependency = None

    property_composer = PropertyComposer(expected_name, default_dependency)

    # Act
    composer_name = property_composer.dependency_name

    # Assert
    assert expected_name == composer_name
    assert len(property_composer.registered_properties) == 0


def test_property_composer_basic_with_default() -> None:
    """Test to verify that a composer with a default dependency will return exactly one property."""

    # Arrange
    expected_name = "basic"
    default_dependency = PropertyPath.from_one("system.full_cwd")

    # Act
    property_composer = PropertyComposer(expected_name, default_dependency)

    # Assert
    assert expected_name == property_composer.dependency_name

    registered_properties = property_composer.registered_properties
    assert len(registered_properties) == 1
    assert registered_properties[0] == default_dependency


def test_property_composer_basic_with_default_and_single_dependency() -> None:
    """Test to verify that a composer with a default and a single new dependecy will
    be propertly ordered."""

    # Arrange
    expected_name = "basic"
    default_dependency = PropertyPath.from_one("system.full_cwd")
    new_dependency = PropertyPath.from_one("git.root_directory")

    # Act
    property_composer = PropertyComposer(expected_name, default_dependency)
    property_composer.add_dependency(new_dependency)

    # Assert
    registered_properties = property_composer.registered_properties
    assert len(registered_properties) == 2
    assert registered_properties[0] == new_dependency
    assert registered_properties[1] == default_dependency


def test_property_composer_basic_with_default_and_multiple_dependencies_same_level_part_1() -> (
    None
):
    """Test to verify that when properties are added at the same level(default level)
    in this case, the entries at the same priority level are sorted alphabetically."""

    # Arrange
    expected_name = "basic"
    default_dependency = PropertyPath.from_one("system.full_cwd")
    new_dependency_one = PropertyPath.from_one("another.root_directory")
    new_dependency_two = PropertyPath.from_one("git.root_directory")

    # Act
    property_composer = PropertyComposer(expected_name, default_dependency)
    property_composer.add_dependency(new_dependency_one)
    property_composer.add_dependency(new_dependency_two)

    # Assert
    registered_properties = property_composer.registered_properties
    assert len(registered_properties) == 3
    assert registered_properties[0] == new_dependency_one
    assert registered_properties[1] == new_dependency_two
    assert registered_properties[2] == default_dependency


def test_property_composer_basic_with_default_and_multiple_dependencies_same_level_part_2() -> (
    None
):
    """Test to verify that when properties are added at the same level(default level)
    in this case, the entries at the same priority level are sorted alphabetically.
    Note, this is the same as the prior test, just with new_dependency_one and new_dependeny_two
    reveresed."""

    # Arrange
    expected_name = "basic"
    default_dependency = PropertyPath.from_one("system.full_cwd")
    new_dependency_one = PropertyPath.from_one("git.root_directory")
    new_dependency_two = PropertyPath.from_one("another.root_directory")

    # Act
    property_composer = PropertyComposer(expected_name, default_dependency)
    property_composer.add_dependency(new_dependency_one)
    property_composer.add_dependency(new_dependency_two)

    # Assert
    registered_properties = property_composer.registered_properties
    assert len(registered_properties) == 3
    assert registered_properties[0] == new_dependency_two
    assert registered_properties[1] == new_dependency_one
    assert registered_properties[2] == default_dependency


def test_property_composer_basic_with_default_and_multiple_dependencies_different_level() -> (
    None
):
    """Test to verify that the composer presents the dependcies sorted by
    priority level above all else."""

    # Arrange
    expected_name = "basic"
    default_dependency = PropertyPath.from_one("system.full_cwd")
    new_dependency_one = PropertyPath.from_one("another.root_directory")
    new_dependency_two = PropertyPath.from_one("git.root_directory")

    # Act
    property_composer = PropertyComposer(expected_name, default_dependency)
    property_composer.add_dependency(new_dependency_one, ComposerPriorityLevel.LOW)
    property_composer.add_dependency(new_dependency_two, ComposerPriorityLevel.NORMAL)

    # Assert
    registered_properties = property_composer.registered_properties
    assert len(registered_properties) == 3
    assert registered_properties[0] == new_dependency_two
    assert registered_properties[1] == new_dependency_one
    assert registered_properties[2] == default_dependency
