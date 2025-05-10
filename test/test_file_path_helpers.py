"""Module to provide tests for the FilePathHelpers class.

Note: the mock_abspath_impl is only as complicated as it need to be to provide
for testing that will work on Linux and Windows systems.
"""

# pylint: disable=unused-import
from test.patches import (  # noqa: F401
    lock_and_clear_file_path_helpers_singleton,
    mock_abspath_impl,
    mock_subprocess_run_df_error_impl,
    mock_subprocess_run_df_impl,
)

from pyshell.file_path_helpers import FilePathHelpers

# pylint: enable=unused-import


def test_normalize_path_windows_long_path(mock_abspath) -> None:
    """Test to verify that we can process a windows file path that is "long"."""

    # Arrange
    _ = mock_abspath
    windows_file_path = "c:\\fred\\barney"
    expected_file_path = "C:\\fred\\barney"

    # Act
    normalized_path = FilePathHelpers.normalize_path(windows_file_path)

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_short_path(mock_abspath) -> None:
    """Test to verify that we can process a windows file path that is short."""

    # Arrange
    _ = mock_abspath
    windows_file_path = "c:\\"
    expected_file_path = "C:\\"

    # Act
    normalized_path = FilePathHelpers.normalize_path(windows_file_path)

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_linux_linux_long_path(mock_abspath) -> None:
    """Test to verify that we can process a linux file path that is "long"."""

    # Arrange
    _ = mock_abspath
    windows_file_path = "/fred/barney"
    expected_file_path = "/fred/barney"

    # Act
    normalized_path = FilePathHelpers.normalize_path(windows_file_path)

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_linux_short_path(mock_abspath) -> None:
    """Test to verify that we can process a linux file path that is "short"."""

    # Arrange
    _ = mock_abspath
    windows_file_path = "/"
    expected_file_path = "/"

    # Act
    normalized_path = FilePathHelpers.normalize_path(windows_file_path)

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_mounts_normal(
    mock_abspath, mock_subprocess_run_df
) -> None:
    """Test to verify that a Windows matching path on the root mount will match.

    Note that this is based off the mount table under mock_subprocess_run_df_impl."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df
    windows_file_path = "c:\\fred\\barney"
    expected_file_path = "/c/fred/barney"

    # Act
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_mounts_longest(
    mock_abspath, mock_subprocess_run_df
) -> None:
    """Test to verify that a Windows matching path with the longest match will win.

    Note that this is based off the mount table under mock_subprocess_run_df_impl."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df
    windows_file_path = "C:\\Users\\brmay\\AppData\\Local\\Temp\\fred\\barney"
    expected_file_path = "/tmp/fred/barney"

    # Act
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_mounts_space_in_path(
    mock_abspath, mock_subprocess_run_df
) -> None:
    """Test to verify that a Windows matching path where the windows path has a space.

    Note that this is based off the mount table under mock_subprocess_run_df_impl."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df
    windows_file_path = "C:\\Program Files\\Git\\usr"
    expected_file_path = "/usr"

    # Act
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_mounts_space_in_mount(
    mock_abspath, mock_subprocess_run_df
) -> None:
    """Test to verify that a Windows matching path where the mount name has a space.

    Note that this is based off the mount table under mock_subprocess_run_df_impl."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df
    windows_file_path = "C:\\enlistments\\pyshell"
    expected_file_path = "/my enlistments/pyshell"

    # Act
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_mounts_bad_retcode(
    mock_abspath, mock_subprocess_run_df_error
) -> None:
    """Test to verify that getting a bad return code from df when trying to determine the
    mount points will not cause an error."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df_error
    windows_file_path = "C:\\enlistments\\pyshell"
    expected_file_path = "C:\\enlistments\\pyshell"

    # Act
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )

    # Assert
    assert expected_file_path == normalized_path


def test_normalize_path_windows_mounts_returns_same_results_over_multiple_calls(
    mock_abspath, mock_subprocess_run_df
) -> None:
    """Test to verify that the same path will return the same results over multiple calls."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df
    windows_file_path = "C:\\enlistments\\pyshell"
    expected_file_path = "/my enlistments/pyshell"

    # Act
    # Assert
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )
        assert expected_file_path == normalized_path

        normalized_path2 = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )
        assert expected_file_path == normalized_path2


def test_normalize_path_windows_mounts_only_replaces_if_mounted(
    mock_abspath, mock_subprocess_run_df
) -> None:
    """Test to verify that specific mount points are only replaced if they are mounted."""

    # Arrange
    _ = mock_abspath, mock_subprocess_run_df
    windows_file_path = "F:\\enlistments\\pyshell"
    expected_file_path = "F:\\enlistments\\pyshell"

    # Act
    with lock_and_clear_file_path_helpers_singleton():
        normalized_path = FilePathHelpers.normalize_path(
            windows_file_path, change_to_posix=True
        )

    # Assert
    assert expected_file_path == normalized_path
