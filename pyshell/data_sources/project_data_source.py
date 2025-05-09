"""Module to provide for the Project related data source items.
"""

from typing import List

from pyshell.data_sources.base_data_source import (
    BaseDataSource,
    PropertyComposer,
    PropertyPath,
)


class ProjectDataSource(BaseDataSource):
    """Data source for project related information."""

    def __init__(self) -> None:
        property_composers: List[PropertyComposer] = [
            PropertyComposer("root_directory", PropertyPath.from_one("system.full_cwd"))
        ]
        super().__init__(name="project", property_composers=property_composers)
