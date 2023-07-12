
"""
AUTOSAR Document
"""

from typing import Any
import autosar.xml.element as ar_element


class DocumentMeta:
    """
    Helper class for holding information about XML schema
    """

    def __init__(self) -> None:
        self.schema_version: int = 50

    @property
    def schema_file(self) -> str:
        """
        Converts schema version integer to expected schema file name
        """
        return f'AUTOSAR_{self.schema_version:05d}.xsd'


class Document(DocumentMeta):
    """
    Implements AUTOSAR root description element
    """

    def __init__(self, packages: list[ar_element.Package] | None = None) -> None:
        super().__init__()
        self.file_info_comment = None  # .FILE-INFO-COMMENT
        self.admin_data = None  # .ADMIN-DATA
        self.introduction = None  # .INTRODUCTION
        self.packages = []  # .PACKAGES
        self._package_map = {}  # internal package map
        if packages is not None:
            for package in packages:
                self.append(package)

    def append(self, package: ar_element.Package):
        """
        Appends package to this document and
        appropriately updates reference links
        """
        if isinstance(package, ar_element.Package):
            if package.name in self._package_map:
                raise ValueError(
                    f"Package with SHORT-NAME '{package.name}' already exists")
            package.parent = self
            self.packages.append(package)
            self._package_map[package.name] = package

    def find(self, ref: str) -> Any:
        """
        Finds item by reference
        """
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        package = self._package_map.get(parts[0], None)
        if (package is not None) and (len(parts[2]) > 0):
            return package.find(parts[2])
        return package

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used generating XML references
        """
        ref_parts.append('')
