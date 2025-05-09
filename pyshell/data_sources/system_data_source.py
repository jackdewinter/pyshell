"""Module to provide for a simple base class for system related data sources.
"""

import datetime
import os
import socket

from pyshell.data_sources.base_data_source import BaseDataSource, property_resolver
from pyshell.file_path_helpers import FilePathHelpers


class SystemDataSource(BaseDataSource):
    """Data source for simple system related data sources."""

    def __init__(self) -> None:
        super().__init__(name="system")

    def get_now(self) -> datetime.datetime:
        """Done to allow monkeypatching of datetime.now.  Must be public for tests to access it."""
        return datetime.datetime.now()

    @property_resolver("user_name")  # \u
    def __get_user_name(self) -> str:
        # https://stackoverflow.com/questions/842059/is-there-a-portable-way-to-get-the-current-username-in-python
        return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    @property_resolver("host_name")  # \h
    def __get_host_name(self) -> str:
        # https://stackoverflow.com/questions/4271740/how-can-i-use-python-to-get-the-system-hostname
        return socket.gethostname()

    @property_resolver("cwd")  # \W
    def __get_cwd(self) -> str:
        return os.path.basename(os.getcwd())

    @property_resolver("full_cwd")  # \w
    def __get_full_cwd(self) -> str:
        return FilePathHelpers.normalize_path(os.getcwd())

    @property_resolver("date")  # \d
    def __get_date(self) -> str:
        # https://stackoverflow.com/questions/17594298/date-time-formats-in-python
        # https://www.w3schools.com/python/python_datetime.asp
        return self.get_now().strftime("%m/%d/%y")

    @property_resolver("time_24")  # \t
    def __get_time_24(self) -> str:
        return self.get_now().strftime("%H:%M:%S")

    @property_resolver("time_12")  # \T
    def __get_time_12(self) -> str:
        return self.get_now().strftime("%I:%M:%S%p")
