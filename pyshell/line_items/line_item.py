"""Module for the LineItem class that defined the basics of elements to display to the user.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from application_properties import ApplicationProperties


@dataclass(frozen=True)
class LineItem(ABC):
    """Information regarding an item to display to the user."""

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Get the name of the current line item."""

    @staticmethod
    @abstractmethod
    def from_properties(
        properties: ApplicationProperties, property_prefix: str
    ) -> "LineItem":
        """Create an instance of the PropertyItem class from loaded application properties."""

    @abstractmethod
    def generate_line_segements(self, value_cache: Dict[str, str]) -> str:
        """Given already cached values, generate text that represents
        this item.
        """

    @staticmethod
    def _get_component(
        properties: ApplicationProperties,
        all_properties_under_prefix: List[str],
        property_prefix: str,
        property_name: str,
        is_required: bool = False,
    ) -> str:

        default_value = None
        full_property_name = property_prefix + properties.separator + property_name
        dict_value = properties.get_string_property(
            full_property_name, is_required=is_required, default_value=default_value
        )
        if full_property_name in all_properties_under_prefix:
            if dict_value is None:
                raise ValueError(
                    f"Property '{full_property_name}' is present, but not defined as a string."
                )
            property_name_index = all_properties_under_prefix.index(full_property_name)
            del all_properties_under_prefix[property_name_index]
        return dict_value

    @staticmethod
    def _get_components_start(
        properties: ApplicationProperties, property_prefix: str, expected_type: str
    ) -> None:
        type_name = property_prefix + ".type"
        item_type = properties.get_string_property(type_name, is_required=True)
        if item_type != expected_type:
            raise ValueError(
                f"Property '{type_name}' must be present and set to '{expected_type}'."
            )

    @staticmethod
    def _get_components_done(
        all_properties_under_prefix: List[str], property_prefix: str
    ) -> None:
        type_index = all_properties_under_prefix.index(property_prefix + "." + "type")
        del all_properties_under_prefix[type_index]
        if all_properties_under_prefix:
            raise ValueError(
                f"One or more properties, such as '{all_properties_under_prefix[0]}' are not defined as part of the component '{property_prefix}'."
            )
