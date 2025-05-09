"""Module to provide tests for the GitDataSource class.
"""

import os
import subprocess
from typing import List, Optional

from pyshell.data_sources.git_data_source import GitDataSource
from pyshell.file_path_helpers import FilePathHelpers


def get_exec(
    subprocess_args: List[str],
    working_directory: Optional[str] = None,
    expecting_failure=False,
):
    """Call a subprocess and wait for its return."""
    exec_result = subprocess.run(  # nosec subprocess_without_shell_equals_true
        subprocess_args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=not expecting_failure,
        cwd=working_directory,
    )
    return exec_result.returncode, exec_result.stdout, exec_result.stderr


def get_exec_success(
    subprocess_args: List[str], working_directory: Optional[str] = None
):
    """Call a subprocess and wait for its return, expecting success."""
    return_code, stdout, stderr = get_exec(subprocess_args, working_directory)
    assert return_code == 0
    assert stderr == ""
    return stdout


def get_exec_failure(
    subprocess_args: List[str], working_directory: Optional[str] = None
):
    """Call a subprocess and wait for its return, expecting a failure."""
    return_code, stdout, stderr = get_exec(subprocess_args, working_directory, True)
    assert return_code != 0
    return return_code, stdout, stderr


def get_branch_for_directory(
    working_directory: Optional[str] = None, expecting_failure=False
) -> str:
    """Given a working directory, invoke the correct command line to get current Git branch, if any."""
    if expecting_failure:
        generated_text = get_exec_failure(
            ["git", "branch", "--no-color"], working_directory
        )
        return generated_text
    generated_text = get_exec_success(
        ["git", "branch", "--no-color"], working_directory
    )
    split_stdout = generated_text.split("\n")
    for next_line in split_stdout:
        if next_line.startswith("* "):
            return next_line[2:]
    return ""


def test_git_data_source_name() -> None:
    """Test to verify that the data source is properly named."""

    # Arrange
    data_source = GitDataSource()

    # Act
    generated_name = data_source.name

    # Assert
    assert generated_name == "git"


def test_git_data_source_get_dynamic_dependencies() -> None:
    """Test to verify that the correct dependencies are set up for the data source."""

    # Arrange
    data_source = GitDataSource()

    # Act
    generated_dependencies = data_source.get_dynamic_dependencies()

    # Assert
    assert len(generated_dependencies) == 1
    assert generated_dependencies[0].local_item_name == "git.root_directory"
    assert (
        generated_dependencies[0].destination_property_path.full_name
        == "project.root_directory"
    )


def test_git_data_source_git_installed() -> None:
    """Test to verify that git is installed on the system to run tests on."""

    # Arrange

    # Act
    generated_version = get_exec_success(["git", "-v"])

    # Assert
    assert generated_version.startswith("git version "), generated_version


def test_git_data_source_get_property_unknown() -> None:
    """Test to verify that asking for a property that does not exist results in
    the empty string being returned."""

    # Arrange
    data_source = GitDataSource()

    # Act
    generated_value = data_source.get_property("unknown")

    # Assert
    assert generated_value == ""


def test_git_data_source_get_property_branch_root_directory() -> None:
    """Test to verify that the above helper method to get the branch and asking
    the data source for the branch turn the same value."""

    # Arrange
    data_source = GitDataSource()
    git_branch = get_branch_for_directory()

    # Act
    generated_value = data_source.get_property("branch")

    # Assert
    assert git_branch == generated_value


def test_git_data_source_get_property_branch_tests_directory() -> None:
    """Test to verify that changing to the 'tests' directory within the repository
    gets the same branch results as at the root."""

    # Arrange
    data_source = GitDataSource()
    root_path = os.getcwd()
    tests_path = os.path.join(root_path, "test")
    assert os.path.isdir(tests_path)
    try:
        os.chdir(tests_path)
        git_branch = get_branch_for_directory(tests_path)
    finally:
        os.chdir(root_path)

    # Act
    generated_value = data_source.get_property("branch")

    # Assert
    assert git_branch == generated_value


def test_git_data_source_get_property_branch_sub_root_directory() -> None:
    """Test to verify that going to the directory below the repository's root directory
    does not yield any branch.  Note in 99% of situations, this is a valid test."""

    # Arrange
    data_source = GitDataSource()
    root_path = os.getcwd()
    sub_root_path = os.path.join(root_path, "..")
    assert os.path.isdir(sub_root_path)
    sub_root_path = os.path.abspath(sub_root_path)
    try:
        os.chdir(sub_root_path)
        ret_code, std_out, std_err = get_branch_for_directory(
            sub_root_path, expecting_failure=True
        )
    finally:
        os.chdir(root_path)
    assert ret_code == 128
    assert std_out == ""
    assert std_err.startswith(
        "fatal: not a git repository (or any of the parent directories)"
    )

    # Act
    try:
        os.chdir(sub_root_path)
        generated_value = data_source.get_property("branch")
    finally:
        os.chdir(root_path)

    # Assert
    assert generated_value == ""


def test_git_data_source_get_property_root_directory_root_directory() -> None:
    """Test to verify that asking for the Git root directory in the root directory
    of the repository returns itself."""

    # Arrange
    data_source = GitDataSource()
    root_path = FilePathHelpers.normalize_path(os.getcwd())

    # Act
    generated_value = data_source.get_property("root_directory")

    # Assert
    assert root_path == generated_value


def test_git_data_source_get_property_root_directory_tests_directory() -> None:
    """Test to verify that changing to the 'tests' directory within the repository
    will still properly return the git root directory."""

    # Arrange
    data_source = GitDataSource()
    root_path = os.getcwd()
    normalized_root_path = FilePathHelpers.normalize_path(root_path)

    tests_path = os.path.join(root_path, "test")
    assert os.path.isdir(tests_path)
    try:
        os.chdir(tests_path)

        # Act
        generated_value = data_source.get_property("root_directory")
    finally:
        os.chdir(root_path)

    # Assert
    assert normalized_root_path == generated_value


def test_git_data_source_get_property_root_directory_sub_root_directory() -> None:
    """Test to verify that changing to the directory below the root directory will
    respond with the root directory being the same as the current directory."""

    # Arrange
    data_source = GitDataSource()
    root_path = os.getcwd()
    tests_path = os.path.join(root_path, "..")
    assert os.path.isdir(tests_path)
    tests_path = os.path.abspath(tests_path)
    try:
        os.chdir(tests_path)
        ret_code, std_out, std_err = get_branch_for_directory(
            tests_path, expecting_failure=True
        )
    finally:
        os.chdir(root_path)
    assert ret_code == 128
    assert std_out == ""
    assert std_err.startswith(
        "fatal: not a git repository (or any of the parent directories)"
    )

    # Act
    try:
        os.chdir(tests_path)
        generated_value = data_source.get_property("root_directory")
    finally:
        os.chdir(root_path)

    # Assert
    assert generated_value == ""
