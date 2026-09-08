"""Package elements."""

from __future__ import annotations

from collections.abc import Iterator
import re
from typing import TYPE_CHECKING, Any

from autosar.xml.base import BaseRef
from autosar.xml.elements._base import ARElement, CollectableElement
import autosar.xml.exception as ar_except
from autosar.xml.reference import PackageRef

if TYPE_CHECKING:
    from autosar.xml.elements.port_interface import PortInterface


class Package(CollectableElement):
    """
    Complex type AR:AR-PACKAGE
    Tag variants: 'AR-PACKAGE'
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.elements: list[ARElement] = []
        self.packages: list[Package] = []
        self._collection_map = {}

    def append(self, item: CollectableElement):
        """
        Append element or sub-package
        """
        if isinstance(item, Package):
            package: Package = item
            if package.name in self._collection_map:
                raise ar_except.DuplicateElement(
                    f"Package with SHORT-NAME '{package.name}' already exists in package '{self.name}")
            package.parent = self
            self.packages.append(package)
            self._collection_map[package.name] = package
        elif isinstance(item, ARElement):
            elem: ARElement = item
            if elem.name in self._collection_map:
                raise ar_except.DuplicateElement(
                    f"Element with SHORT-NAME '{elem.name}' already exists in package '{self.name}'")
            elem.parent = self
            self.elements.append(elem)
            self._collection_map[elem.name] = elem
        else:
            raise TypeError(f"Invalid type {str(type(item))}")

    def make_packages(self, ref: str) -> "Package":
        """
        Recursively creates sub-packages
        """
        if ref.startswith('/'):
            raise ValueError("Reference string can't start with '/'")
        parts = ref.partition('/')
        package = self._collection_map.get(parts[0], None)
        if package is None:
            package = self.create_package(parts[0])
        elif not isinstance(package, Package):
            raise KeyError(f"Item with name '{parts[0]}' already exists but isn't a package")
        if len(parts[2]) > 0:
            return package.make_packages(parts[2])
        else:
            return package

    def create_package(self, name: str, **kwargs) -> "Package":
        """
        Creates new sub-package
        """
        if name in self._collection_map:
            return ValueError(f"Package with name '{name}' already exists")
        package = Package(name, **kwargs)
        self._collection_map[name] = package
        self.packages.append(package)
        package.parent = self
        return package

    def find(self, ref: str) -> Any:
        """
        Finds item by reference
        """
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        item = self._collection_map.get(parts[0], None)
        if item is not None:
            if len(parts[2]) > 0:
                return item.find(parts[2])
        return item

    def filter(self, *names: str) -> Iterator[ARElement]:
        """
        Yields all elements whose short-name matches any of the names in
        argument list
        """
        for elem in self.elements:
            if elem.name in names:
                yield elem

    def filter_regex(self, pattern: str | re.Pattern) -> Iterator[ARElement]:
        """
        Yields all elements whose short-name matches the given regex pattern
        """
        regex: re.Pattern = None
        if isinstance(pattern, str):
            regex = re.compile(pattern)
        elif isinstance(pattern, re.Pattern):
            regex = pattern
        else:
            raise TypeError(f"pattern: Invalid type '{str(type(pattern))}'")
        for elem in self.elements:
            if regex.match(elem.name):
                yield elem

    def ref(self) -> PackageRef:
        """
        Returns a reference to this package or
        None if the package is not a sub-package or a root package
        in a document/workspace
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else PackageRef(ref_str)


class BehaviorSettings:
    """
    Enables users to customize settings in SwcInternalBehavior such as naming conventions.
    """

    def __init__(self) -> None:

        # Events
        self.background_event_prefix: str | None = None  # BackgroundEvent name prefix
        self.data_receive_error_event_prefix: str | None = None  # DataReceiveErrorEvent name prefix
        self.data_receive_event_prefix: str | None = None  # DataReceivedEvent name prefix
        self.init_event_prefix: str | None = None  # InitEvent name prefix
        self.operation_invoked_event_prefix: str | None = None  # OperationInvokedEvent name prefix
        self.os_task_execution_event_prefix: str | None = None  # OsTaskExecutionEvent name prefix
        self.swc_mode_manager_error_event_prefix: str | None = None  # SwcModeManagerErrorEvent name prefix
        self.swc_mode_switch_event_prefix: str | None = None  # SwcModeSwitchEvent name prefix
        self.timing_event_prefix: str | None = None  # TimingEvent name prefix
        self.external_trigger_event_prefix: str | None = None  # ExternalTriggerOccurredEvent name prefix
        self.internal_trigger_event_prefix: str | None = None  # InternalTriggerOccurredEvent name prefix
        # Runnables
        self.data_read_access_prefix: str | None = None  # DATA-READ-ACCESS name prefix
        # (DATA-RECEIVE-POINT-BY-ARGUMENT and DATA-RECEIVE-POINT-BY-VALUE) name prefix
        self.data_receive_point_prefix: str | None = None
        self.data_send_point_prefix: str | None = None  # DATA-SEND-POINT name prefix
        self.data_write_access_prefix: str | None = None  # DATA-WRITE-ACCESSS name prefix
        self.external_triggering_point_prefix: str | None = None  # EXTERNAL-TRIGGERING-POINT name prefix
        self.internal_triggering_point_prefix: str | None = None  # INTERNAL-TRIGGERING-POINT name prefix
        self.mode_access_point_prefix: str | None = None  # MODE-ACCESS-POINT name prefix
        self.mode_switch_point_prefix: str | None = None  # MODE-SWITCH-POINT name prefix
        self.parameter_access_prefix: str | None = None  # PARAMETER-ACCESS name prefix
        self.read_local_variable_prefix: str | None = None  # READ-LOCAL-VARIABLE name prefix
        self.server_call_point_prefix: str | None = None  # SERVER-CALL-POINT name prefix
        self.wait_point_prefix: str | None = None  # WAIT_POINT name prefix
        self.write_local_variable_prefix: str | None = None  # WRITTEN-LOCAL-VARIABLE name prefix

    def set_value(self, name: str, value: str):
        """
        Updates a single value with error check
        """
        if hasattr(self, name):
            if not isinstance(value, str):
                raise TypeError(f"value: Expected string type. Got {str(type(value))}")
            setattr(self, name, value)
        else:
            raise KeyError(f"name: Invalid name '{name}'")

    def update(self, value_map: dict[str, str]):
        """
        Updates multiple values using keys in value_map, with error-check
        """
        for name, value in value_map.items():
            self.set_value(name, value)

    def set_default(self):
        """
        Set default values (Not yet implemented)
        """

    def get_value(self, name: str) -> str:
        """
        Returns named value only if it's not None
        """
        value = getattr(self, name)
        if value is None:
            raise ValueError(f"{name} is not set in behavior settings")
        return value


class PackageCollection:
    """
    Base class that maintains a collection of AUTOSAR packages
    """

    def __init__(self, packages: list[Package] | None = None,
                 behavior_settings: BehaviorSettings | None = None) -> None:
        self.parent = None
        self.behavior_settings = behavior_settings
        self.packages: list[Package] = []  # .PACKAGES
        self._package_dict = {}  # internal package map
        if packages is not None:
            for package in packages:
                self.append(package)

    def append(self, package: Package):
        """
        Appends package to this document and
        appropriately updates reference links
        """
        if isinstance(package, Package):
            if package.name in self._package_dict:
                raise ValueError(
                    f"Package with SHORT-NAME '{package.name}' already exists")
            package.parent = self
            self.packages.append(package)
            self._package_dict[package.name] = package

    def find(self, ref: str | BaseRef) -> Any:
        """
        Finds item by reference
        """
        if isinstance(ref, BaseRef):
            ref = str(ref)
        if not isinstance(ref, str):
            raise TypeError("ref: Must be either a string or a valid reference class."
                            f"Got '{str(type(ref))}'")
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        package = self._package_dict.get(parts[0], None)
        if (package is not None) and (len(parts[2]) > 0):
            return package.find(parts[2])
        return package

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used generating XML references
        """
        ref_parts.append('')

    def create_package(self, name: str, **kwargs) -> Package:
        """
        Creates new package in collection
        """
        if name in self._package_dict:
            return ValueError(f"Package with name '{name}' already exists")
        package = Package(name, **kwargs)
        self.append(package)
        return package

    def make_packages(self, *refs: str) -> Package | list[Package]:
        """
        Recursively creates packages from reference(s)
        Returns a list of created packages.
        If only one argument is given it will return that package (not a list).
        """
        result = []
        for ref in refs:
            if ref.startswith('/'):
                ref = ref[1:]
            parts = ref.partition('/')
            package = self._package_dict.get(parts[0], None)
            if package is None:
                package = self.create_package(parts[0])
            if len(parts[2]) > 0:
                package = package.make_packages(parts[2])
            result.append(package)
        return result[0] if len(result) == 1 else result

    def get_valid_behavior_settings(self) -> BehaviorSettings:
        """
        Verifies that behavior_settings is a proper object before returning it
        """
        if not isinstance(self.behavior_settings, BehaviorSettings):
            raise ValueError("Object doesn't seem to be a proper workspace")
        return self.behavior_settings

    def get_port_interface(self, ref: str | BaseRef) -> "PortInterface":
        """
        Find port inteface from reference
        """
        port_interface = self.find(ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(f"Invalid port interface reference: '{str(port_interface)}'")
        return port_interface


__all__ = [
    "Package",
    "BehaviorSettings",
    "PackageCollection",
]
