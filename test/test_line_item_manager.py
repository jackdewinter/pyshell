"""Tests for the LineItemManager module
"""

from test.utils import assert_that_exception_is_raised

from application_properties import ApplicationProperties

from pyshell.line_item_manager import LineItemManager, PropertyItem, TextItem


def test_line_item_manager_register_empty() -> None:
    """Test to verify that we respond nicely if no line items are registered."""

    # Arrange
    line_item_manager = LineItemManager()

    # Act
    required_items = line_item_manager.get_properties_required_for_items()

    # Assert
    assert not required_items


def test_line_item_manager_register_text_item() -> None:
    """Test to verify that we respond nicely with only test items."""

    # Arrange
    line_item_manager = LineItemManager()
    line_item_manager.register_item(TextItem("bob"))

    # Act
    required_items = line_item_manager.get_properties_required_for_items()

    # Assert
    assert not required_items


def test_line_item_manager_generate_text_item() -> None:
    """Test to verify that we generate a simple line from only text items."""

    # Arrange
    line_item_manager = LineItemManager()
    line_item_manager.register_item(TextItem("bob"))
    value_cache = {}

    # Act
    generated_line = line_item_manager.generate(value_cache)

    # Assert
    assert generated_line == "bob"


def test_line_item_manager_register_property_item() -> None:
    """Test to verify that any property items registered results in required items."""

    # Arrange
    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("system", "full_cwd"))

    # Act
    required_items = line_item_manager.get_properties_required_for_items()

    # Assert
    assert len(required_items) == 1
    assert required_items[0].source_name == "system"
    assert required_items[0].item_name == "full_cwd"


def test_line_item_manager_generate_property_item_in_cache() -> None:
    """Test to verify that any property items with matching properties in the cache are output properly."""

    # Arrange
    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("system", "full_cwd"))
    value_cache = {"system.full_cwd": "abc"}

    # Act
    generated_line = line_item_manager.generate(value_cache)

    # Assert
    assert generated_line == "abc"


def test_line_item_manager_generate_property_item_not_in_cache() -> None:
    """Test to verify that any property items with matching properties not in the cache are output properly."""

    # Arrange
    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("system", "not_in_cache"))
    value_cache = {"system.full_cwd": "abc"}

    # Act
    generated_line = line_item_manager.generate(value_cache)

    # Assert
    assert generated_line == ""


def test_line_item_manager_from_properties_unknown_type() -> None:
    """Test to verify that each item must have a type."""

    # Arrange
    line_item_manager = LineItemManager()
    properties = ApplicationProperties()
    properties.load_from_dict({"items": {"bob": {"type": "unknown"}}})

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "Property 'items.bob' has a type of 'unknown' which is not supported.",
        line_item_manager.from_properties,
        properties,
    )
