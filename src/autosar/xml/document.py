
"""
Classes related to AUTOSAR Documents (a.k.a. ARXML files)
"""
from typing import Any
from autosar.xml.package import Package

class DocumentMeta:
    """
    Helper class for holding information about XML schema
    """
    def __init__(self) -> None:
        self.schema_version : int = 50

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
    def __init__(self, packages : list[Package] | None = None) -> None:
        super().__init__()
        self.file_info_comment = None #.FILE-INFO-COMMENT
        self.admin_data = None #.ADMIN-DATA
        self.introduction = None #.INTRODUCTION
        self.packages = [] #.PACKAGES
        self._package_map = {} #internal package map
        if packages is not None:
            for package in packages:
                self.append(package)

    def append(self, package : Package):
        """
        Appends package to this document and
        appropriately updates reference links
        """
        if isinstance(package, Package):
            if package.name in self._package_map:
                raise ValueError(f"Package with SHORT-NAME '{package.name}' already exists")
            package.parent = self
            self.packages.append(package)
            self._package_map[package.name] = package

    def find(self, ref :str) -> Any:
        """
        Find items using a reference string
        """
        if ref[0]=='/': #remove initial '/' if it exists
            ref=ref[1:]
        return self.find_from_parts(ref.split('/'))

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used generating XML references
        """
        ref_parts.append('')

    def find_from_parts(self, ref_parts: list) -> Any:
        """
        Utility function that finds inner elements
        from a list of reference parts.
        """
        if not ref_parts:
            return None
        short_name = ref_parts.pop(0)
        package = self._package_map.get(short_name, None)
        if package is not None and len(ref_parts) > 0:
            return package.find_from_parts(ref_parts)
        return package
