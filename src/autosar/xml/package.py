"""
Classes related to AUTOSAR Packages
"""
from typing import Any
from autosar.xml.element import CollectableElement, ARElement

# Package


class Package(CollectableElement):
    """
    AR:PACKAGE
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.elements = []
        self.packages = []
        self.role: str | None = None  # TODO: change to enum type
        self._element_map = {}
        self._package_map = {}

    def append(self, item: Any):
        """
        Appends package to this document and
        appropriately updates reference links
        """
        if isinstance(item, Package):
            package: Package = item
            if package.name in self._package_map:
                raise ValueError(
                    f"Package with SHORT-NAME '{package.name}' already exists in package '{self.name}")
            package.parent = self
            self.packages.append(package)
            self._package_map[package.name] = package
        elif isinstance(item, ARElement):
            elem: ARElement = item
            if elem.name in self._element_map:
                raise ValueError(
                    f"Element with SHORT-NAME '{elem.name}' already exists in package '{self.name}'")
            elem.parent = self
            self.elements.append(elem)
            self._element_map[elem.name] = elem
        else:
            raise TypeError(f"Invalid type {str(type(item))}")

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used generating XML references
        """
        ref_parts.append(self.name)
        self.parent.update_ref_parts(ref_parts)

    def find_from_parts(self, ref_parts: list) -> Any:
        """
        Utility function that finds inner elements
        from a list of reference parts.
        """
        if not ref_parts:
            return None
        short_name = ref_parts.pop(0)
        item = self._element_map.get(short_name, None)
        if item is not None:
            if len(ref_parts) > 0:
                return item.find_from_parts(ref_parts)
        else:
            item = self._package_map.get(short_name, None)
            if item is not None and len(ref_parts) > 0:
                return item.find_from_parts(ref_parts)
        return item
