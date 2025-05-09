"""Module containing class that deal with items to display to the user. 
"""

from collections import OrderedDict
from typing import Dict, List

from application_properties import ApplicationProperties

from pyshell.data_sources.base_data_source import PropertyPath
from pyshell.line_items.line_item import LineItem
from pyshell.line_items.property_item import PropertyItem
from pyshell.line_items.text_item import TextItem


class LineItemManager:
    """Class to handle interaction with the line items."""

    def __init__(self) -> None:
        self.__line_items: List[LineItem] = []
        self.__available_line_items = [TextItem, PropertyItem]

        self.__line_item_name_to_type_map = {}
        for next_line_item_type in self.__available_line_items:
            get_name_function_result = getattr(  # noqa: B009
                next_line_item_type, "get_name"
            )()
            self.__line_item_name_to_type_map[get_name_function_result] = (
                next_line_item_type
            )

    def register_item(self, new_line_item: LineItem) -> None:
        """Register a new line item for the display."""
        self.__line_items.append(new_line_item)

    def get_properties_required_for_items(self) -> List[PropertyPath]:
        """Get any properties that are required by the items being managed."""
        required_properties = []
        for next_line_item in self.__line_items:
            if isinstance(next_line_item, PropertyItem):
                required_properties.append(
                    PropertyPath(
                        next_line_item.data_source_name, next_line_item.data_item_name
                    )
                )
        return required_properties

    def from_properties(self, properties: ApplicationProperties) -> None:
        """Load a list of line items from the "items" field in the configuration."""

        found_items = OrderedDict()
        for next_property_name in properties.property_names_under("items"):
            split_property_name = next_property_name.split(".")
            root_property_name = split_property_name[0] + "." + split_property_name[1]
            if root_property_name not in found_items:
                found_items[root_property_name] = ""

        for next_property_name in found_items.keys():
            property_type = properties.get_string_property(
                next_property_name + ".type", is_required=True
            )
            line_item_type = self.__line_item_name_to_type_map.get(property_type, None)
            if line_item_type is not None:
                new_item = getattr(line_item_type, "from_properties")(  # noqa: B009
                    properties, next_property_name
                )
            else:
                raise ValueError(
                    f"Property '{next_property_name}' has a type of '{property_type}' which is not supported."
                )
            self.register_item(new_item)

    def generate(self, values_cache: Dict[str, str]) -> str:
        """Generate the display line based on the Line Items and the value cache."""
        line_segments = []
        for next_line_item in self.__line_items:
            line_segments.append(next_line_item.generate_line_segements(values_cache))
        return "".join(line_segments)
