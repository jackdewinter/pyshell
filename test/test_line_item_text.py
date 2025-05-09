"""
Module for tests for the TextItem class.
"""

from test.utils import assert_that_exception_is_raised

from application_properties import ApplicationProperties

from pyshell.line_item_manager import TextItem


def test_line_item_text_basic_properties() -> None:
    """Test to verify that we can generate a basic line item."""

    # Arrange
    text_to_display = "abc"

    # Act
    line_item = TextItem(text_to_display)

    # Assert
    assert line_item.text == text_to_display


def test_line_item_text_basic_generate_line_segments() -> None:
    """Test to verify that we can generate a basic line segment from a direct instantiation."""

    # Arrange
    text_to_display = "abc"

    # Act
    line_item = TextItem(text_to_display)
    line_output = line_item.generate_line_segements({})

    # Assert
    assert line_output == text_to_display


def test_line_item_text_from_properties_good() -> None:
    """Test to verify that we can load a simple line item from a dictionary."""

    # Arrange
    ap = ApplicationProperties()
    text_to_display = "abc"
    ap.load_from_dict({"bob": {"type": "text", "text": text_to_display}})

    # Act
    line_item = TextItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements({})

    # Assert
    assert line_output == text_to_display


def test_line_item_text_from_properties_object_not_string() -> None:
    """Test to verify that we cannot load string values from a complex dictioary."""

    # Arrange
    ap = ApplicationProperties()
    ap.load_from_dict({"bob": {"type": "text", "text": {"bob": "fred"}}})

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "A value for property 'bob.text' must be provided.",
        TextItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_text_from_properties_not_present() -> None:
    """Test to verify that we cannot load properties from a property that is present, but empty."""

    # Arrange
    ap = ApplicationProperties()
    ap.load_from_dict({"bob": {}})

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "A value for property 'bob.type' must be provided.",
        TextItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_text_from_properties_extra_present() -> None:
    """Test to verify that we cannot load properties where there is an extra item present."""

    # Arrange
    ap = ApplicationProperties()
    ap.load_from_dict({"bob": {"type": "text", "text": "bob", "test": "barney"}})

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "One or more properties, such as 'bob.test' are not defined as part of the component 'bob'.",
        TextItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_text_from_properties_integer_not_string() -> None:
    """Test to verify that all properties we load must be strings."""

    # Arrange
    ap = ApplicationProperties()
    text_to_display = 1
    ap.load_from_dict({"bob": {"type": "text", "text": text_to_display}})

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "Property 'bob.text' is present, but not defined as a string.",
        TextItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_text_from_properties_no_type() -> None:
    """Test to verify that an object with no type property will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    text_to_use = "abc"
    ap.load_from_dict({"bob": {"text": text_to_use}})

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "A value for property 'bob.type' must be provided.",
        TextItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_text_from_properties_bad_type() -> None:
    """Test to verify that an object with a bad type property will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "something",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
            }
        }
    )

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "Property 'bob.type' must be present and set to 'text'.",
        TextItem.from_properties,
        ap,
        "bob",
    )
