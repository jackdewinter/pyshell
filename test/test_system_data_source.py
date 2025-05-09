"""Module to provides tests for the SystemDataSource class.
"""

# pylint: disable=unused-import
import os
import socket
from datetime import datetime
from test.patches import (  # noqa: F401
    GMT_AFTERNOON_TIMESTAMP,
    GMT_MORNING_TIMESTAMP,
    mock_gethostname_impl,
    mock_system_time_in_afternoon_gmt_impl,
    mock_system_time_in_morning_gmt_impl,
    set_environment_simulating_user_name,
)

import pytest

from pyshell.data_sources.system_data_source import SystemDataSource
from pyshell.file_path_helpers import FilePathHelpers

# pylint: enable=unused-import


def test_system_data_source_name() -> None:
    """Test to verify that the data source is named properly."""

    # Arrange
    data_source = SystemDataSource()

    # Act
    generated_name = data_source.name

    # Assert
    assert generated_name == "system"


def test_system_data_source_now() -> None:
    """Test to verify that the "unchanged" get_now function returns a current timestamp."""

    # Arrange
    data_source = SystemDataSource()
    current_now = datetime.now()

    # Act
    generated_now = data_source.get_now()

    # Assert
    assert (current_now.timestamp() - generated_now.timestamp()) < 1.00


def test_system_data_source_get_property_dependencies() -> None:
    """Test to verify that getting any named property dependencies returns an empty list."""

    # Arrange
    data_source = SystemDataSource()

    # Act
    generated_dependencies = data_source.get_property_dependencies("")

    # Assert
    assert not generated_dependencies


def test_system_data_source_get_dynamic_dependencies() -> None:
    """Test to verify that this data source returns no dynamic dependencies."""

    # Arrange
    data_source = SystemDataSource()

    # Act
    generated_dependencies = data_source.get_dynamic_dependencies()

    # Assert
    assert not generated_dependencies


def test_system_data_source_get_property_unknown() -> None:
    """Test to verify that an unknown property returns an empty string."""

    # Arrange
    data_source = SystemDataSource()

    # Act
    generated_dependencies = data_source.get_property("unknown")

    # Assert
    assert not generated_dependencies


def test_system_data_source_get_property_user_name() -> None:
    """Test to verify that, by mocking out the user name, we can ask for the user_name property
    and get the right result."""

    # Arrange
    data_source = SystemDataSource()
    user_name_to_test_for = "bob"

    # Act
    with set_environment_simulating_user_name(user_name_to_test_for):
        generated_dependencies = data_source.get_property("user_name")

    # Assert
    assert generated_dependencies == user_name_to_test_for


def test_system_data_source_get_property_hostname(mock_gethostname) -> None:
    """Test to verify that we can get the system's name and it is the same as asking for the "host_name" property."""

    # Arrange
    _ = mock_gethostname
    data_source = SystemDataSource()
    current_hostname = socket.gethostname()

    # Act
    generated_dependencies = data_source.get_property("host_name")

    # Assert
    assert generated_dependencies == current_hostname


def test_system_data_source_get_property_cwd() -> None:
    """Test to verify that the current directory's basename is the same as reported by "cwd"."""

    # Arrange
    data_source = SystemDataSource()
    current_directory = os.path.basename(os.getcwd())

    # Act
    generated_dependencies = data_source.get_property("cwd")

    # Assert
    assert generated_dependencies == current_directory


def test_system_data_source_get_property_full_cwd() -> None:
    """Test to verify that the normalized current directoy is the same as reported by "full_cwd"."""

    # Arrange
    data_source = SystemDataSource()
    current_directory = FilePathHelpers.normalize_path(os.getcwd())

    # Act
    generated_dependencies = data_source.get_property("full_cwd")

    # Assert
    assert generated_dependencies == current_directory


def test_system_data_source_get_property_time_24_in_gmt_morning(
    mock_system_time_in_morning_gmt,
) -> None:
    """Test to verify that a 24-hour time in GMT morning is what is returned by the "time_24" property."""

    # Arrange
    _ = mock_system_time_in_morning_gmt
    data_source = SystemDataSource()
    time_in_gmt_morning = datetime.fromtimestamp(GMT_MORNING_TIMESTAMP).strftime(
        "%H:%M:%S"
    )

    # Act
    generated_dependencies = data_source.get_property("time_24")

    # Assert
    assert generated_dependencies == time_in_gmt_morning


def test_system_data_source_get_property_time_24_in_gmt_afternoon(
    mock_system_time_in_afternoon_gmt,
) -> None:
    """Test to verify that a 24-hour time in GMT afternoon is what is returned by the "time_24" property."""

    # Arrange
    _ = mock_system_time_in_afternoon_gmt
    data_source = SystemDataSource()
    time_in_gmt_morning = datetime.fromtimestamp(GMT_AFTERNOON_TIMESTAMP).strftime(
        "%H:%M:%S"
    )

    # Act
    generated_dependencies = data_source.get_property("time_24")

    # Assert
    assert generated_dependencies == time_in_gmt_morning


def test_system_data_source_get_property_time_12_in_gmt_morning(
    mock_system_time_in_morning_gmt,
) -> None:
    """Test to verify that a 12-hour time in GMT morning is what is returned by the "time_12" property."""

    # Arrange
    _ = mock_system_time_in_morning_gmt
    data_source = SystemDataSource()
    time_in_gmt_morning = datetime.fromtimestamp(GMT_MORNING_TIMESTAMP).strftime(
        "%I:%M:%S%p"
    )

    # Act
    generated_dependencies = data_source.get_property("time_12")

    # Assert
    assert generated_dependencies == time_in_gmt_morning


def test_system_data_source_get_property_time_12_in_gmt_afternoon(
    mock_system_time_in_afternoon_gmt,
) -> None:
    """Test to verify that a 12-hour time in GMT afternoon is what is returned by the "time_12" property."""

    # Arrange
    _ = mock_system_time_in_afternoon_gmt
    data_source = SystemDataSource()
    time_in_gmt_morning = datetime.fromtimestamp(GMT_AFTERNOON_TIMESTAMP).strftime(
        "%I:%M:%S%p"
    )

    # Act
    generated_dependencies = data_source.get_property("time_12")

    # Assert
    assert generated_dependencies == time_in_gmt_morning


def test_system_data_source_get_property_date_in_gmt_morning(
    mock_system_time_in_morning_gmt,
) -> None:
    """Test to verify that a date according to GMT morning produces the correct result for the "data" property."""

    # Arrange
    _ = mock_system_time_in_morning_gmt
    data_source = SystemDataSource()
    time_in_gmt_morning = datetime.fromtimestamp(GMT_MORNING_TIMESTAMP).strftime(
        "%m/%d/%y"
    )

    # Act
    generated_dependencies = data_source.get_property("date")

    # Assert
    assert generated_dependencies == time_in_gmt_morning


def test_system_data_source_get_property_date_in_gmt_afternoon(
    mock_system_time_in_afternoon_gmt,
) -> None:
    """Test to verify that a date according to GMT afternoon produces the correct result for the "data" property."""

    # Arrange
    _ = mock_system_time_in_afternoon_gmt
    data_source = SystemDataSource()
    time_in_gmt_morning = datetime.fromtimestamp(GMT_AFTERNOON_TIMESTAMP).strftime(
        "%m/%d/%y"
    )

    # Act
    generated_dependencies = data_source.get_property("date")

    # Assert
    assert generated_dependencies == time_in_gmt_morning


@pytest.fixture(name="mock_abspath")
def mock_abspath_impl(monkeypatch):
    """Mock for our own os.path.abspath that can somewhat handle windows and linux."""

    def mock_return(file_path):
        is_first_character_alpha = file_path and (
            (file_path[0] >= "a" and file_path[1] <= "z")
            or (file_path[0] >= "A" and file_path[1] <= "Z")
        )
        if (
            len(file_path) >= 3
            and is_first_character_alpha
            and file_path[1] == ":"
            and file_path[2] == "\\"
        ):
            pass
        elif file_path[0] == "/":
            pass
        else:
            raise AssertionError()
        return file_path

    monkeypatch.setattr(os.path, "abspath", mock_return)
