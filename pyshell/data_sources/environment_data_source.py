import os

from pyshell.data_sources.base_data_source import BaseDataSource


class EnvironmentDataSource(BaseDataSource):
    """Data source for readonly access to environment variables."""

    def __init__(self) -> None:
        super().__init__(name="environment")

    def get_property(self, property_name: str) -> str:
        """Get the property from the data source that is associated with the given property name."""

        return os.environ[property_name]
