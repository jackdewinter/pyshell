"""Module to contain the test data sources.
"""

from typing import List

from pyshell.data_sources.base_data_source import (
    BaseDataSource,
    ComposerPriorityLevel,
    PropertyDependency,
    PropertyPath,
)


class SimpleTestDataSource(BaseDataSource):
    """Class to encompass a simple data source implementation.

    Note that for simplicity and observabilty concerns, the functions are
    processed long-hand, instead of using the BaseDataSource and its helper
    functions.
    """

    def __init__(self):
        super().__init__("simple_test")
        self.audit_trail = []
        self.__dynamic_dependencies = {}

    def register_dynamic_dependency(
        self,
        property_name: str,
        property_path: PropertyPath,
        priority_level: ComposerPriorityLevel,
    ) -> None:
        self.audit_trail.append(("register", property_name, property_path))

        if property_name not in self.__dynamic_dependencies:
            self.__dynamic_dependencies[property_name] = []
        self.__dynamic_dependencies[property_name].append(property_path)

    def get_property_dependencies(self, property_name: str) -> List[PropertyPath]:
        return_value = []
        if property_name == "redirect_to_static_a":
            return_value = [PropertyPath(self.name, "static_a")]
        if property_name == "redirect_to_not_present_property":
            return_value = [PropertyPath(self.name, "not_present_property")]
        if property_name == "self_cyclic":
            return_value = [PropertyPath(self.name, "self_cyclic")]
        if property_name == "long_cycle_1":
            return_value = [PropertyPath(self.name, "long_cycle_2")]
        if property_name == "long_cycle_2":
            return_value = [PropertyPath(self.name, "long_cycle_3")]
        if property_name == "long_cycle_3":
            return_value = [PropertyPath(self.name, "long_cycle_1")]
        if property_name == "multiple_same_dependencies":
            return_value = [
                PropertyPath(self.name, "redirect_to_not_present_property"),
                PropertyPath(self.name, "redirect_to_not_present_property"),
            ]
        if property_name == "other_test_a":
            return_value = [PropertyPath("other_test", "a")]
        if property_name in self.__dynamic_dependencies:
            return_value = self.__dynamic_dependencies[property_name]

        self.audit_trail.append(
            ("get_property_dependencies", property_name, return_value)
        )
        return return_value

    def get_property(self, property_name: str) -> str:
        """Get the property from the data source that is associated with the given property name."""

        return_value = ""
        if property_name == "static_a":
            return_value = "a"

        self.audit_trail.append(("get_property", property_name, return_value))
        return return_value


class OtherTestDataSource(BaseDataSource):
    """Class to provide for a second data source, allowing for cross data source testing."""

    def __init__(self, use_property_dependency=False):
        super().__init__("other_test")
        self.__use_property_dependency = use_property_dependency

    def get_dynamic_dependencies(self) -> List[PropertyDependency]:
        return (
            [PropertyDependency("a", PropertyPath.from_one("simple_test.dynamic_a"))]
            if self.__use_property_dependency
            else []
        )

    def get_property(self, property_name: str) -> str:
        """Get the property from the data source that is associated with the given property name."""

        return_value = ""
        if property_name == "a":
            return_value = "a"

        return return_value
