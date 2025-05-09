"""Module to capture the TextItem class, responsible for showing plain text to the user.
"""

from dataclasses import dataclass
from typing import Dict

from application_properties import ApplicationProperties

from pyshell.line_items.line_item import LineItem


@dataclass(frozen=True)
class TextItem(LineItem):
    """Item to display that is based on static text."""

    text: str

    @staticmethod
    def get_name() -> str:
        return "text"

    def generate_line_segements(self, value_cache: Dict[str, str]) -> str:
        _ = value_cache
        return self.text

    @staticmethod
    def from_properties(
        properties: ApplicationProperties, property_prefix: str
    ) -> "TextItem":
        """Create an instance of the TextItem class from loaded application properties."""

        all_properties_under_prefix = properties.property_names_under(property_prefix)

        LineItem._get_components_start(properties, property_prefix, "text")

        text_value = LineItem._get_component(
            properties,
            all_properties_under_prefix,
            property_prefix,
            "text",
            is_required=True,
        )

        LineItem._get_components_done(all_properties_under_prefix, property_prefix)
        return TextItem(text_value)
