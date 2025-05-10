"""Classes required to exress data sources.
"""

import subprocess  # nosec blacklist
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar


@dataclass(frozen=True)
class PropertyPath:
    """Encapsulation of the parts of a property."""

    source_name: str
    "Name of the data source that contains the property."
    item_name: str
    "Name of the property within the data source."

    @staticmethod
    def from_one(one_name: str) -> "PropertyPath":
        """From a "source.item" format, create a PropertyPath object."""
        two_names = one_name.split(".")
        return PropertyPath(two_names[0], two_names[1])

    @property
    def full_name(self) -> str:
        """Get the full name of the property228."""
        return f"{self.source_name}.{self.item_name}"


@dataclass(frozen=True)
class PropertyDependency:
    """Encapsulation required for any dependency on another property."""

    local_item_name: str
    "Local name of the item within the current data source."
    destination_property_path: PropertyPath
    "Full path to the destination property."


class ComposerPriorityLevel(Enum):
    """Priority to associate to a property path within a composer list."""

    HIGHEST = 0
    HIGH = 25
    NORMAL = 50
    LOW = 75
    LOWEST = 100


@dataclass
class ComposerItem:
    """Combination of the property path to use and the priority level to use within the composer."""

    property_path: PropertyPath
    "Path to the property to be considered to represent this composer."
    priority_level: ComposerPriorityLevel
    "Priority level to use when resolving priority amoung multiple property paths."


@dataclass(frozen=False)
class PropertyComposer:
    """Property composer to use as a "sink" for other data sources wanting to broadcast
    their information into another data source.
    """

    dependency_name: str
    "Name of the dependency to serve as a 'sink'."

    def __init__(
        self, dependency_name: str, default_property_path: Optional[PropertyPath]
    ) -> None:
        self.dependency_name = dependency_name
        self.__registered_properties: List[ComposerItem] = []
        if default_property_path:
            self.__registered_properties.append(
                ComposerItem(default_property_path, ComposerPriorityLevel.LOWEST)
            )

    def add_dependency(
        self,
        remote_property_path: PropertyPath,
        priority_level: ComposerPriorityLevel = ComposerPriorityLevel.NORMAL,
    ) -> None:
        """Add a new path/priority pair to the list for this composer."""
        self.__registered_properties.insert(
            0, ComposerItem(remote_property_path, priority_level)
        )

    @property
    def registered_properties(self) -> List[PropertyPath]:
        """Generate a list of registered properties, sorted by priority level and full name."""
        sorted_data = sorted(
            self.__registered_properties,
            key=lambda x: (x.priority_level.value, x.property_path.full_name),
        )
        property_list: List[PropertyPath] = []
        property_list.extend(i.property_path for i in sorted_data)
        return property_list


all_property_resolvers = {}
"""Global list of property resolvers across all data sources.
This is required as this list is created when the data sources are initialized.
"""


@dataclass(frozen=True)
class NameFunctionPair:
    """Name/function pairs used to resolve properties."""

    name: str
    "Local item name associated with the property."
    function: Any
    "Function used to resolve the property value."


# https://medium.com/@ashley.e.shultz/type-hinting-a-decorator-that-changes-function-arguments-d603a6631c3c
P = TypeVar("P", bound=Callable[[Any], str])


def property_resolver(property_name: str) -> Callable[[P], P]:
    "Decorator to mark the encapsulated function with a property name to refer to it by."

    def decorator(function: P) -> P:
        function._register = NameFunctionPair(property_name, function)  # type: ignore
        return function

    return decorator


class RegisteringType(type):
    """Base class/metaclass used to collect information about functions marked
    as property resolvers.
    """

    def __init__(
        cls: "RegisteringType",
        name: str,
        bases: "BaseDataSource",
        attrs: Dict[str, "BaseDataSource"],
    ) -> None:  # sourcery skip: instance-method-first-arg-name
        for key, val in attrs.items():
            resolver_function = getattr(val, "_register", None)
            if resolver_function is not None:
                all_property_resolvers[f"{name}.{key}"] = resolver_function


class BaseDataSource(metaclass=RegisteringType):
    """Base data source class."""

    def __init__(
        self,
        name: str,
        dependencies_to_inject: Optional[List[PropertyDependency]] = None,
        property_composers: Optional[List[PropertyComposer]] = None,
    ) -> None:
        self.__name = name
        self.__property_resolvers: Dict[str, Callable[["BaseDataSource"], str]] = {}
        self.__property_composers: Dict[str, PropertyComposer] = {}

        self.__resolve_registered_properties()
        self.__dependencies_to_inject = (
            dependencies_to_inject if dependencies_to_inject is not None else []
        )
        property_composers = (
            property_composers if property_composers is not None else []
        )
        for i in property_composers:
            self.__property_composers[i.dependency_name] = i

    @property
    def name(self) -> str:
        """Name associated with the data source."""
        return self.__name

    def __resolve_registered_properties(
        child_instance: "BaseDataSource",
    ) -> None:  # sourcery skip: instance-method-first-arg-name
        child_class_prefix = f"{child_instance.__class__.__name__}."
        for (
            full_function_name,
            property_name_function_pair,
        ) in all_property_resolvers.items():
            if full_function_name.startswith(child_class_prefix):
                child_instance.__property_resolvers[
                    property_name_function_pair.name
                ] = property_name_function_pair.function

    def get_property(self, property_name: str) -> str:
        """Get the property from the data source that is associated with the given property name."""
        return self._resolve_property(property_name) or ""

    def get_dynamic_dependencies(self) -> List[PropertyDependency]:
        """Get a list of any dynmanic dependencies to be set up."""
        return self.__dependencies_to_inject

    def get_property_dependencies(self, property_name: str) -> List[PropertyPath]:
        """Get the property dependencies from the data source that is associated with the given property name."""
        _ = property_name
        selected_composer = self.__property_composers.get(property_name, None)
        return selected_composer.registered_properties if selected_composer else []

    def register_dynamic_dependency(  # noqa: B027
        self,
        property_name: str,
        property_path: PropertyPath,
        priority_level: ComposerPriorityLevel,
    ) -> None:
        """Regsiter a property name and the dynamic dependency to another data source's property."""
        if selected_composer := self.__property_composers.get(property_name, None):
            selected_composer.add_dependency(property_path, priority_level)
        return

    def _resolve_property(self, property_name: str) -> Optional[str]:
        property_resolver_function = self.__property_resolvers.get(property_name, None)
        return property_resolver_function(self) if property_resolver_function else None

    def _execute_subprocess(
        self,
        subprocess_args: List[str],
        check_for_success: bool = True,
        use_shell: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Function to execute a shell process to return more information."""

        return subprocess.run(  # nosec subprocess_without_shell_equals_true
            subprocess_args,
            text=True,
            shell=use_shell,  # nosec subprocess_popen_with_shell_equals_true
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check_for_success,
        )
