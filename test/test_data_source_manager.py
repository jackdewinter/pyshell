"""
Tests for the DataSourceManager module.
"""

from test.test_data_sources import OtherTestDataSource, SimpleTestDataSource

from pyshell.data_source_manager import DataSourceManager
from pyshell.data_sources.base_data_source import PropertyPath
from pyshell.line_item_manager import LineItemManager, PropertyItem, TextItem
from pyshell.pyshell_exception import PyShellException


def test_data_source_register_good() -> None:
    """Test to validate the simple registration of a data source."""
    # Arrange
    data_source_manager = DataSourceManager()

    # Act
    # Assert
    data_source_manager.register_data_source(SimpleTestDataSource())


def test_data_source_register_repeat() -> None:
    """Test to validate that registering a data source name twice fails."""

    # Arrange
    data_source_manager = DataSourceManager()
    data_source_manager.register_data_source(SimpleTestDataSource())

    # Act
    try:
        data_source_manager.register_data_source(SimpleTestDataSource())

        # Assert
        assert False, "Should have had an exception by now."  # noqa: B011
    except PyShellException as this_exception:
        assert (
            str(this_exception)
            == "A data source with name 'simple_test' has already been registered."
        )


def test_data_source_evaluate_before_registration_complete() -> None:
    """Test to validate that we cannot call evaluate before the registration is complete."""

    # Arrange
    data_source_manager = DataSourceManager()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(TextItem("bob"))
    line_item_manager.register_item(TextItem("barney"))
    value_cache = {}

    # Act
    try:
        data_source_manager.evaluate(value_cache, line_item_manager)

        # Assert
        assert False, "Should have thrown exception by now."  # noqa: B011
    except PyShellException as this_exception:
        assert (
            str(this_exception)
            == "Registration must be completed before evaluation can begin."
        )


def test_data_source_evaluate_only_text_items() -> None:
    """Test to validate that if we use only text items, we need no data sources."""

    # Arrange
    data_source_manager = DataSourceManager()
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(TextItem("bob"))
    line_item_manager.register_item(TextItem("barney"))
    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert not value_cache, "No value were asked for, as just text items."


def test_data_source_evaluate_one_simple_property_item_present() -> None:
    """Test to validate that we can ask a data source for a simple property
    that returns a value right away.
    """

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "static_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"simple_test.static_a": "a"}

    assert len(simple_data_source.audit_trail) == 2

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "static_a"
    assert simple_data_source.audit_trail[0][2] == []

    assert simple_data_source.audit_trail[1][0] == "get_property"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "static_a"
    assert simple_data_source.audit_trail[1][2] == "a"


def test_data_source_evaluate_one_simple_property_item_not_present() -> None:
    """Test to validate that we can ask for an item that is not present and it will return
    and empty string."""

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "not_present"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"simple_test.not_present": ""}

    assert len(simple_data_source.audit_trail) == 2

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "not_present"
    assert simple_data_source.audit_trail[0][2] == []

    assert simple_data_source.audit_trail[1][0] == "get_property"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "not_present"
    assert simple_data_source.audit_trail[1][2] == ""


def test_data_source_evaluate_double_simple_property_item_present() -> None:
    """Test to validate that even though there are two property items
    that are asking for the same property value, it is only evaluated
    once.
    """

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "static_a"))
    line_item_manager.register_item(PropertyItem("simple_test", "static_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"simple_test.static_a": "a"}

    assert len(simple_data_source.audit_trail) == 2

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "static_a"
    assert simple_data_source.audit_trail[0][2] == []

    assert simple_data_source.audit_trail[1][0] == "get_property"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "static_a"
    assert simple_data_source.audit_trail[1][2] == "a"


def test_data_source_evaluate_redirect_property_present() -> None:
    """Test to validate that we can redirect to a property value that
    is present and both the current property and the property redirect to
    will get that value.
    """

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "redirect_to_static_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {
        "simple_test.static_a": "a",
        "simple_test.redirect_to_static_a": "a",
    }

    assert len(simple_data_source.audit_trail) == 3

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "redirect_to_static_a"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(source_name="simple_test", item_name="static_a")
    ]

    assert simple_data_source.audit_trail[1][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "static_a"
    assert simple_data_source.audit_trail[1][2] == []

    assert simple_data_source.audit_trail[2][0] == "get_property"
    assert len(simple_data_source.audit_trail[2]) == 3
    assert simple_data_source.audit_trail[2][1] == "static_a"
    assert simple_data_source.audit_trail[2][2] == "a"


def test_data_source_evaluate_redirect_property_other_source_not_present() -> None:
    """Test to validate that we can redirect to a data source that is not present,
    with both properties evaluating to an empty string."""

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "other_test_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"simple_test.other_test_a": "", "other_test.a": ""}

    assert len(simple_data_source.audit_trail) == 1

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "other_test_a"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(source_name="other_test", item_name="a")
    ]


def test_data_source_evaluate_redirect_property_other_source_present() -> None:
    """Test to validate that we can redirect to a data source that is present,
    with both properties evaluating to the same value."""

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.register_data_source(OtherTestDataSource())
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "other_test_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"simple_test.other_test_a": "a", "other_test.a": "a"}

    assert len(simple_data_source.audit_trail) == 1

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "other_test_a"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(source_name="other_test", item_name="a")
    ]


def test_data_source_evaluate_redirect_property_not_present() -> None:
    """Test to verify that we can redirect to a property with an item name that i
    not present, with both properties evaluating to an empty string."""

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(
        PropertyItem("simple_test", "redirect_to_not_present_property")
    )

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {
        "simple_test.redirect_to_not_present_property": "",
        "simple_test.not_present_property": "",
    }

    assert len(simple_data_source.audit_trail) == 3

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "redirect_to_not_present_property"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(source_name="simple_test", item_name="not_present_property")
    ]

    assert simple_data_source.audit_trail[1][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "not_present_property"
    assert simple_data_source.audit_trail[1][2] == []

    assert simple_data_source.audit_trail[2][0] == "get_property"
    assert len(simple_data_source.audit_trail[2]) == 3
    assert simple_data_source.audit_trail[2][1] == "not_present_property"
    assert simple_data_source.audit_trail[2][2] == ""


def test_data_source_evaluate_redirect_property_simple_cyclic() -> None:
    """Test to verify that we can handle a redirection that immmediately cycles back
    on itself.
    """

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "self_cyclic"))

    value_cache = {}

    # Act
    try:
        data_source_manager.evaluate(value_cache, line_item_manager)

        # Assert
        assert False, "Should have cycled by now"  # noqa: B011
    except PyShellException as this_exception:
        assert (
            str(this_exception)
            == "Dependency cycle encountered: simple_test.self_cyclic->simple_test.self_cyclic"
        )

    assert not value_cache

    assert len(simple_data_source.audit_trail) == 1

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "self_cyclic"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(source_name="simple_test", item_name="self_cyclic")
    ]


def test_data_source_evaluate_redirect_property_longer_cyclic() -> None:
    """Test to verify we can handle redirection with a longer cycle between property values."""

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "long_cycle_1"))

    value_cache = {}

    # Act
    try:
        data_source_manager.evaluate(value_cache, line_item_manager)

        # Assert
        assert False, "Should have cycled by now"  # noqa: B011
    except PyShellException as this_exception:
        assert (
            str(this_exception)
            == "Dependency cycle encountered: simple_test.long_cycle_1->simple_test.long_cycle_2->simple_test.long_cycle_3->simple_test.long_cycle_1"
        )

    assert not value_cache

    assert len(simple_data_source.audit_trail) == 3

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "long_cycle_1"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(source_name="simple_test", item_name="long_cycle_2")
    ]

    assert simple_data_source.audit_trail[1][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "long_cycle_2"
    assert simple_data_source.audit_trail[1][2] == [
        PropertyPath(source_name="simple_test", item_name="long_cycle_3")
    ]

    assert simple_data_source.audit_trail[2][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[2]) == 3
    assert simple_data_source.audit_trail[2][1] == "long_cycle_3"
    assert simple_data_source.audit_trail[2][2] == [
        PropertyPath(source_name="simple_test", item_name="long_cycle_1")
    ]


def test_data_source_evaluate_redirect_property_mutiple_paths_to_same_end() -> None:
    """Test to verify that multiple paths to the same property are fine."""

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(
        PropertyItem("simple_test", "multiple_same_dependencies")
    )

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {
        "simple_test.redirect_to_not_present_property": "",
        "simple_test.not_present_property": "",
        "simple_test.multiple_same_dependencies": "",
    }

    assert len(simple_data_source.audit_trail) == 4

    assert simple_data_source.audit_trail[0][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "multiple_same_dependencies"
    assert simple_data_source.audit_trail[0][2] == [
        PropertyPath(
            source_name="simple_test", item_name="redirect_to_not_present_property"
        ),
        PropertyPath(
            source_name="simple_test", item_name="redirect_to_not_present_property"
        ),
    ]

    assert simple_data_source.audit_trail[1][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "redirect_to_not_present_property"
    assert simple_data_source.audit_trail[1][2] == [
        PropertyPath(source_name="simple_test", item_name="not_present_property")
    ]

    assert simple_data_source.audit_trail[2][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[2]) == 3
    assert simple_data_source.audit_trail[2][1] == "not_present_property"
    assert simple_data_source.audit_trail[2][2] == []

    assert simple_data_source.audit_trail[3][0] == "get_property"
    assert len(simple_data_source.audit_trail[3]) == 3
    assert simple_data_source.audit_trail[3][1] == "not_present_property"
    assert simple_data_source.audit_trail[3][2] == ""


def test_data_source_evaluate_redirect_dynamic_present() -> None:
    """Test to verify that we can register a dynamic dependency, and if
    it is accepted on the other side, can be referenced.
    """

    # Arrange
    data_source_manager = DataSourceManager()
    simple_data_source = SimpleTestDataSource()
    data_source_manager.register_data_source(simple_data_source)
    data_source_manager.register_data_source(
        OtherTestDataSource(use_property_dependency=True)
    )
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "dynamic_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"other_test.a": "a", "simple_test.dynamic_a": "a"}

    assert len(simple_data_source.audit_trail) == 2

    assert simple_data_source.audit_trail[0][0] == "register"
    assert len(simple_data_source.audit_trail[0]) == 3
    assert simple_data_source.audit_trail[0][1] == "dynamic_a"
    assert simple_data_source.audit_trail[0][2] == PropertyPath(
        source_name="other_test", item_name="a"
    )

    assert simple_data_source.audit_trail[1][0] == "get_property_dependencies"
    assert len(simple_data_source.audit_trail[1]) == 3
    assert simple_data_source.audit_trail[1][1] == "dynamic_a"
    assert simple_data_source.audit_trail[1][2] == [
        PropertyPath(source_name="other_test", item_name="a")
    ]


def test_data_source_evaluate_redirect_dynamic_not_present() -> None:
    """Test to verify that we can register a dynamic dependency, and if
    it is NOT accepted on the other side, can be referenced but will return
    the empty value.
    """

    # Arrange
    data_source_manager = DataSourceManager()
    data_source_manager.register_data_source(
        OtherTestDataSource(use_property_dependency=True)
    )
    data_source_manager.registration_completed()

    line_item_manager = LineItemManager()
    line_item_manager.register_item(PropertyItem("simple_test", "dynamic_a"))

    value_cache = {}

    # Act
    data_source_manager.evaluate(value_cache, line_item_manager)

    # Assert
    assert value_cache == {"simple_test.dynamic_a": ""}
