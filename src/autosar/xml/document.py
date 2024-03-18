
"""
AUTOSAR Document
"""
# pylint: disable=R0801
from autosar.base import DEFAULT_SCHEMA_VERSION
import autosar.xml.element as ar_element


class DocumentMeta:
    """
    Helper class for holding information about XML schema
    """

    def __init__(self, schema_version: int) -> None:
        self.schema_version = schema_version

    @property
    def schema_file(self) -> str:
        """
        Converts schema version integer to expected schema file name
        """
        return f'AUTOSAR_{self.schema_version:05d}.xsd'


class Document(ar_element.PackageCollection, DocumentMeta):
    """
    Implements AUTOSAR root description element
    """

    def __init__(self, packages: list[ar_element.Package] | None = None, schema_version=DEFAULT_SCHEMA_VERSION) -> None:
        ar_element.PackageCollection.__init__(self, packages)
        DocumentMeta.__init__(self, schema_version)
        self.file_info_comment = None  # .FILE-INFO-COMMENT
        self.admin_data = None  # .ADMIN-DATA
        self.introduction = None  # .INTRODUCTION
