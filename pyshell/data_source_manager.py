"""Module to provide for the handling of data sources.
"""

from typing import Dict, List

from application_properties import ApplicationProperties

from pyshell.data_sources.base_data_source import (
    BaseDataSource,
    ComposerPriorityLevel,
    PropertyPath,
)
from pyshell.data_sources.git_data_source import GitDataSource
from pyshell.data_sources.project_data_source import ProjectDataSource
from pyshell.data_sources.system_data_source import SystemDataSource
from pyshell.line_item_manager import LineItemManager
from pyshell.pyshell_exception import PyShellException


class DataSourceManager:
    """Class for the handling of data sources."""

    def __init__(self) -> None:
        self.__data_sources: Dict[str, BaseDataSource] = {}
        self.__registration_completed = False

    def from_properties(self, properties: ApplicationProperties) -> None:
        """Use information from the properties to guide how the data sources are loaded.

        NOTE: currently marked for future support.
        """
        _ = properties
        self.register_data_source(SystemDataSource())
        self.register_data_source(GitDataSource())
        self.register_data_source(ProjectDataSource())
        self.registration_completed()

    def register_data_source(self, new_data_source: BaseDataSource) -> None:
        """Register a new data source with the manager."""
        if new_data_source.name in self.__data_sources:
            raise PyShellException(
                f"A data source with name '{new_data_source.name}' has already been registered."
            )
        self.__data_sources[new_data_source.name] = new_data_source

    def registration_completed(self) -> None:
        """Take care of any resolving connections.  This can only be accomplished
        once all data sources have been registered.
        """

        for _, next_data_source in self.__data_sources.items():
            for next_dependency in next_data_source.get_dynamic_dependencies():
                if (
                    next_dependency.destination_property_path.source_name
                    in self.__data_sources
                ):
                    self.__data_sources[
                        next_dependency.destination_property_path.source_name
                    ].register_dynamic_dependency(
                        next_dependency.destination_property_path.item_name,
                        PropertyPath(
                            next_data_source.name, next_dependency.local_item_name
                        ),
                        ComposerPriorityLevel.NORMAL,
                    )
        self.__registration_completed = True

    def __evaluate_single_property(
        self,
        value_cache: Dict[str, str],
        visitor_log: List[str],
        property_id: PropertyPath,
    ) -> str:

        # Check to see if we already have this in our cache. If so, use it.
        if property_id.full_name in value_cache:
            return value_cache[property_id.full_name]

        is_top_level = not visitor_log
        visitor_log.append(property_id.full_name)

        # Next, gather any dependencies for the property we want to get.  Note
        # that is there are no dependencies, we can simply grab the property
        # value and use it.
        if property_id.source_name not in self.__data_sources:
            value_cache[property_id.full_name] = ""
            return value_cache[property_id.full_name]
        data_dependencies = self.__data_sources[
            property_id.source_name
        ].get_property_dependencies(property_id.item_name)
        if not data_dependencies:
            value_cache[property_id.full_name] = self.__data_sources[
                property_id.source_name
            ].get_property(property_id.item_name)
            return value_cache[property_id.full_name]

        # For the more complex properties, we need to go through the dependencies
        # until we find a non-empty value.
        resolved_value = ""
        for next_dependency in data_dependencies:
            inner_property_id = PropertyPath(
                next_dependency.source_name, next_dependency.item_name
            )

            # Detect cycles.
            if inner_property_id.full_name in visitor_log:
                visitor_log.append(inner_property_id.full_name)
                raise PyShellException(
                    "Dependency cycle encountered: " + "->".join(visitor_log)
                )

            resolved_value = self.__evaluate_single_property(
                value_cache, visitor_log, inner_property_id
            )
            if resolved_value:
                break
            if is_top_level:
                visitor_log.clear()
        value_cache[property_id.full_name] = resolved_value
        return value_cache[property_id.full_name]

    def evaluate(
        self, value_cache: Dict[str, str], list_item_manager: LineItemManager
    ) -> None:
        """Evaluate the required properties from the line items and resolve the
        value of each property before we do anything else.
        """

        if not self.__registration_completed:
            raise PyShellException(
                "Registration must be completed before evaluation can begin."
            )

        required_properties = list_item_manager.get_properties_required_for_items()
        for property_to_resolve in required_properties:
            visitor_log: List[str] = []
            self.__evaluate_single_property(
                value_cache, visitor_log, property_to_resolve
            )
