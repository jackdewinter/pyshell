"""Module to provide monkey patches to use throughout the tests.
"""

import io
import os
import socket
import subprocess
from contextlib import contextmanager
from datetime import datetime
from test.pytest_execute import InProcessResult, SystemState
from threading import Lock
from typing import List

import pytest

from pyshell.application_configuration_helper import ApplicationConfigurationHelper
from pyshell.data_sources.system_data_source import SystemDataSource
from pyshell.file_path_helpers import FilePathHelpers

GMT_MORNING_TIMESTAMP = 1735689600 + 10 * 60 + 5
GMT_AFTERNOON_TIMESTAMP = 1735689600 + 12 * 60 * 60 + 10 * 60 + 5

MOCK_HOST_NAME = "scaramouche"

MOCK_GIT_BRANCH_NAME = "branch/unknown"


@pytest.fixture(name="mock_system_time_in_morning_gmt")
def mock_system_time_in_morning_gmt_impl(monkeypatch):
    """Mock to set the get_now response from the SystemDataSource to 2025-01-01 in the afternoon."""

    def mock_return(self):
        _ = self
        return datetime.fromtimestamp(GMT_MORNING_TIMESTAMP)

    monkeypatch.setattr(SystemDataSource, "get_now", mock_return)


@pytest.fixture(name="mock_system_time_in_afternoon_gmt")
def mock_system_time_in_afternoon_gmt_impl(monkeypatch):
    """Mock to set the get_now response from the SystemDataSource to 2025-01-01 in the afternoon."""

    def mock_return(self):
        _ = self
        return datetime.fromtimestamp(GMT_AFTERNOON_TIMESTAMP)

    monkeypatch.setattr(SystemDataSource, "get_now", mock_return)


@pytest.fixture(name="mock_gethostname")
def mock_gethostname_impl(monkeypatch):
    """Mock for our own socket.gethostname to override the local system name."""

    def mock_return():
        return MOCK_HOST_NAME

    monkeypatch.setattr(socket, "gethostname", mock_return)


@pytest.fixture(name="mock_subprocess_run_git_branch")
def mock_subprocess_run_git_branch_impl(monkeypatch):
    """Mock for our own os.path.abspath that can somewhat handle windows and linux."""

    def mock_return(cargs: List[str], *args, **kwargs):

        _ = args
        if cargs[0] == "git" and cargs[1] == "branch":
            out_text = f"* {MOCK_GIT_BRANCH_NAME}"
            out_error = ""
        else:
            out_text = ""
            out_error = ""

        std_output = out_text if "text" in kwargs else io.StringIO(out_text)
        std_error = out_error if "text" in kwargs else io.StringIO(out_error)
        return InProcessResult(0, std_output, std_error)

    monkeypatch.setattr(subprocess, "run", mock_return)


@pytest.fixture(name="mock_subprocess_run_df")
def mock_subprocess_run_df_impl(monkeypatch):
    """Mock for running df as part of the tests and returning a known set of values."""

    def mock_return(cargs: List[str], *args, **kwargs):

        _ = args
        if cargs[0] == "df" and cargs[1] == "-a":
            out_text = """Filesystem                        1K-blocks     Used Available Use% Mounted on
C:/Program Files/Git              997702652 88888796 908813856   9% /
C:/Program Files/Git/usr/bin              -        -         -    - /bin
C:/enlistments                            -        -         -    - /my enlistments
C:/Users/brmay/AppData/Local/Temp         -        -         -    - /tmp
C:                                        -        -         -    - /c
"""
            out_error = ""
        else:
            out_text = ""
            out_error = ""

        std_output = out_text if "text" in kwargs else io.StringIO(out_text)
        std_error = out_error if "text" in kwargs else io.StringIO(out_error)
        return InProcessResult(0, std_output, std_error)

    monkeypatch.setattr(subprocess, "run", mock_return)


@pytest.fixture(name="mock_subprocess_run_df_error")
def mock_subprocess_run_df_error_impl(monkeypatch):
    """Mock for running df as part of the tests and returning a known set of values."""

    def mock_return(cargs: List[str], *args, **kwargs):

        _ = args
        if cargs[0] == "df" and cargs[1] == "-a":
            out_text = ""
            out_error = "Some error message"
            error_code = 1
        else:
            out_text = ""
            out_error = ""
            error_code = 0

        std_output = out_text if "text" in kwargs else io.StringIO(out_text)
        std_error = out_error if "text" in kwargs else io.StringIO(out_error)
        return InProcessResult(error_code, std_output, std_error)

    monkeypatch.setattr(subprocess, "run", mock_return)


@pytest.fixture(name="mock_is_file_for_default_configuration")
def mock_is_file_for_default_configuration_impl(monkeypatch):
    """Mock for the os.path.isfile builtin, returning false if it is default configuration."""

    def mock_return(file_path):
        return FilePathHelpers.normalize_path(
            ApplicationConfigurationHelper.DEFAULT_CONFIGURATION_PATH
        ) != FilePathHelpers.normalize_path(file_path)

    monkeypatch.setattr(os.path, "isfile", mock_return)


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


@contextmanager
def set_environment_simulating_execution_in_ps1(set_to_active: bool = True):
    """Provide for a context manager that simulates being executed from PS1."""

    try:
        previous_value = os.environ["IS_PYSHELL_PS1"]
    except KeyError:
        previous_value = ""

    saved_state = SystemState()
    try:
        os.environ["IS_PYSHELL_PS1"] = "1" if set_to_active else ""
        yield
    finally:
        saved_state.restore()
        os.environ["IS_PYSHELL_PS1"] = previous_value


@contextmanager
def set_environment_simulating_user_name(user_name: str):
    """Provide for a context manager that simulates the user name."""

    if os.name.lower() == "nt":
        user_env_var_name = "USERNAME"
    else:
        user_env_var_name = "USER"

    try:
        previous_value = os.environ[user_env_var_name]
    except KeyError:
        previous_value = ""

    saved_state = SystemState()
    try:
        os.environ[user_env_var_name] = user_name
        yield
    finally:
        saved_state.restore()
        os.environ[user_env_var_name] = previous_value


__file_path_helpers_singleton_lock = Lock()


@contextmanager
def lock_and_clear_file_path_helpers_singleton():
    """Provide for a context manager that locks the FilePathHelpers singleton."""
    with __file_path_helpers_singleton_lock:
        try:
            FilePathHelpers.clear_mount_points()
            yield
        finally:
            pass
