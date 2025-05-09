"""
Module for tests for the PropertyItem class.
"""

from test.utils import assert_that_exception_is_raised

from application_properties import ApplicationProperties

from pyshell.line_item_manager import PropertyItem


def test_line_item_property_basic_properties() -> None:
    """Test to verify that we can create property items with required information."""

    # Arrange
    data_source = "system"
    data_item = "user_name"

    # Act
    line_item = PropertyItem(data_source, data_item)

    # Assert
    assert line_item.data_source_name == data_source
    assert line_item.data_item_name == data_item


def test_line_item_property_extended_properties() -> None:
    """Test to verify that we can create property items with extended information."""

    # Arrange
    data_source = "system"
    data_item = "user_name"
    text_prefix = "["
    text_suffix = "]"

    # Act
    line_item = PropertyItem(data_source, data_item, text_prefix, text_suffix)

    # Assert
    assert line_item.data_source_name == data_source
    assert line_item.data_item_name == data_item
    assert line_item.prefix == text_prefix
    assert line_item.suffix == text_suffix


def test_line_item_property_from_properties_basic_good() -> None:
    """Test to verify that we can generate a line segement from a line item."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
            }
        }
    )

    cached_values = {f"{data_source}.{data_item}": "barney"}
    expected_text = "barney"

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text


def test_line_item_property_from_properties_extended_good() -> None:
    """Test to verify that we can generate a line segement from a line item with suffix and prefix."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
            }
        }
    )
    cached_values = {f"{data_source}.{data_item}": "barney"}
    expected_text = "[barney]"

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text


def test_line_item_property_from_properties_no_type() -> None:
    """Test to verify that an object with no type property will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
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
        "A value for property 'bob.type' must be provided.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_from_properties_bad_type() -> None:
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
        "Property 'bob.type' must be present and set to 'property'.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_from_properties_no_data_source() -> None:
    """Test to verify that an object with no data_source property will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_sourcex": data_source,
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
        "A value for property 'bob.data_source' must be provided.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_from_properties_no_data_item() -> None:
    """Test to verify that an object with no data_item property will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_itemx": data_item,
                "prefix": "[",
                "suffix": "]",
            }
        }
    )

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "A value for property 'bob.data_item' must be provided.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_from_properties_extra_items() -> None:
    """Test to verify that an object with extra properties will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "other_item": "blah",
            }
        }
    )

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "One or more properties, such as 'bob.other_item' are not defined as part of the component 'bob'.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_from_properties_integer_data_source() -> None:
    """Test to verify that an object with extra properties will generate an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = 1
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
            }
        }
    )

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "Property 'bob.data_source' is present, but not defined as a string.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_extended_default_display_modifier() -> None:
    """Test to verify that the display modifier has a good default."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
            }
        }
    )
    cached_values = {f"{data_source}.{data_item}": "barney"}
    expected_text = "[barney]"

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text


def test_line_item_property_extended_explicit_display_modifier_bad() -> None:
    """Test to verify that a bad display modifier generates an error."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
                "display_modifier": "this_is_a_bad_value",
            }
        }
    )

    # Act
    # Assert
    assert_that_exception_is_raised(
        ValueError,
        "Property 'bob.display_modifier' cannot be assigned the value 'THIS_IS_A_BAD_VALUE'.",
        PropertyItem.from_properties,
        ap,
        "bob",
    )


def test_line_item_property_extended_explicit_display_modifier_always_with_present() -> (
    None
):
    """Test to verify that the always display modifier with a present value works."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
                "display_modifier": "always",
            }
        }
    )
    cached_values = {f"{data_source}.{data_item}": "barney"}
    expected_text = "[barney]"

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text


def test_line_item_property_extended_explicit_display_modifier_always_with_empty() -> (
    None
):
    """Test to verify that the always display modifier with an empty value works."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
                "display_modifier": "always",
            }
        }
    )
    cached_values = {f"{data_source}.{data_item}": ""}
    expected_text = "[]"

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text


def test_line_item_property_extended_explicit_display_modifier_not_empty_with_present() -> (
    None
):
    """Test to verify that the not empty display modifier with a present value works."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
                "display_modifier": "not_empty",
            }
        }
    )
    cached_values = {f"{data_source}.{data_item}": "barney"}
    expected_text = "[barney]"

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text


def test_line_item_property_extended_explicit_display_modifier_not_empty_with_empty() -> (
    None
):
    """Test to verify that the not empty display modifier with an empty value works."""

    # Arrange
    ap = ApplicationProperties()
    data_source = "system"
    data_item = "user_name"
    ap.load_from_dict(
        {
            "bob": {
                "type": "property",
                "data_source": data_source,
                "data_item": data_item,
                "prefix": "[",
                "suffix": "]",
                "display_modifier": "not_empty",
            }
        }
    )
    cached_values = {f"{data_source}.{data_item}": ""}
    expected_text = ""

    # Act
    line_item = PropertyItem.from_properties(ap, "bob")
    line_output = line_item.generate_line_segements(cached_values)

    # Assert
    assert line_output == expected_text
