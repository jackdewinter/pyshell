from dataclasses import dataclass
from enum import Enum
from typing import Dict

from application_properties import ApplicationProperties

from pyshell.line_items.line_item import LineItem


class ItemDisplayModifier(Enum):
    ALWAYS = 0
    NOT_EMPTY = 1


@dataclass(frozen=True)
class PropertyItem(LineItem):
    """Item to display that is based on a property from a data source."""

    data_source_name: str
    data_item_name: str
    prefix: str = ""
    suffix: str = ""
    display_modifier: ItemDisplayModifier = ItemDisplayModifier.ALWAYS

    @staticmethod
    def get_name() -> str:
        return "property"

    def generate_line_segements(self, value_cache: Dict[str, str]) -> str:
        full_data_source_name = f"{self.data_source_name}.{self.data_item_name}"
        if full_data_source_name in value_cache:
            cache_value = value_cache[full_data_source_name]
            if self.display_modifier == ItemDisplayModifier.ALWAYS or (
                self.display_modifier == ItemDisplayModifier.NOT_EMPTY and cache_value
            ):
                return self.prefix + cache_value + self.suffix
        return ""

    @staticmethod
    def from_properties(
        properties: ApplicationProperties, property_prefix: str
    ) -> "PropertyItem":
        """Create an instance of the PropertyItem class from loaded application properties."""

        all_properties_under_prefix = properties.property_names_under(property_prefix)

        LineItem._get_components_start(properties, property_prefix, "property")

        data_source = LineItem._get_component(
            properties,
            all_properties_under_prefix,
            property_prefix,
            "data_source",
            is_required=True,
        )
        data_item = LineItem._get_component(
            properties,
            all_properties_under_prefix,
            property_prefix,
            "data_item",
            is_required=True,
        )
        text_prefix = (
            LineItem._get_component(
                properties,
                all_properties_under_prefix,
                property_prefix,
                "prefix",
                is_required=False,
            )
            or ""
        )
        text_suffix = (
            LineItem._get_component(
                properties,
                all_properties_under_prefix,
                property_prefix,
                "suffix",
                is_required=False,
            )
            or ""
        )
        display_modifier_text = (
            LineItem._get_component(
                properties,
                all_properties_under_prefix,
                property_prefix,
                "display_modifier",
                is_required=False,
            )
            or ""
        )
        if display_modifier_text:
            try:
                display_modifier = ItemDisplayModifier[display_modifier_text.upper()]
            except KeyError:
                raise ValueError(
                    f"Property '{property_prefix}.display_modifier' cannot be assigned the value '{display_modifier_text.upper()}'."
                )
        else:
            display_modifier = ItemDisplayModifier.ALWAYS

        LineItem._get_components_done(all_properties_under_prefix, property_prefix)
        return PropertyItem(
            data_source_name=data_source,
            data_item_name=data_item,
            prefix=text_prefix,
            suffix=text_suffix,
            display_modifier=display_modifier,
        )
