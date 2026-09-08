"""Foundational base classes and AdminData elements."""

from __future__ import annotations

import datetime
import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, NamedTuple, Union

from autosar.xml.base import ARObject
import autosar.xml.enumeration as ar_enum

if TYPE_CHECKING:
    from autosar.xml.elements.documentation import (
        Date,
        LanguagePlainText,
        MultiLanguageOverviewParagraph,
        MultiLanguagePlainText,
        MultilanguageLongName,
        RevisionLabelString,
    )
    from autosar.xml.elements.package import PackageCollection

SingleLanguageText = tuple[ar_enum.Language, str]


# Helper classes


class NumericalValue:
    """Wrapper for numerical value."""

    def __init__(self,
                 value: int | float | str,
                 value_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        self._value = self._validate_value(value)
        if isinstance(value, str):
            if value.startswith("0x"):
                value_format = ar_enum.ValueFormat.HEXADECIMAL
            elif value.startswith("0b"):
                value_format = ar_enum.ValueFormat.BINARY
        self.value_format = value_format

    @property
    def value(self):
        """Value property."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = self._validate_value(value)

    def _validate_value(self, value: Any) -> int | float | str:
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            try:
                return int(value, 0)
            except ValueError:
                return float(value)
        else:
            raise TypeError(f"Unexpected type for value {str(type(value))}")


class PositiveIntegerValue:
    """Wrapper for positive value."""

    def __init__(self,
                 value: int,
                 value_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        self._value = self._validate_value(value)
        self.value_format = value_format

    @property
    def value(self):
        """Value property."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = self._validate_value(value)

    def _validate_value(self, value: int | str) -> int:
        if isinstance(value, str):
            try:
                value = int(value, 0)
            except ValueError as err:
                raise TypeError("Unable to convert to integer") from err
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Value must be a positive integer")
            return value
        else:
            raise TypeError(f"Unexpected type for value {str(type(value))}")


# Base classes


class Referrable(ARObject):
    """Group AR:REFERRABLE."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name  # .SHORT-NAME
        self.parent: Union[CollectableElement, PackageCollection, None] = None

    @property
    def short_name(self) -> str:
        """Alias for "name"."""
        return self.name

    def root_collection(self) -> Union[PackageCollection, None]:
        """Return root package collection object or None if it can't be found.

        A package collection can be either a Workspace or a Document object depending
        on how the packages/elements was created initially.
        """
        elem = self
        while elem.parent is not None:
            elem = elem.parent
        from autosar.xml.elements.package import PackageCollection
        if isinstance(elem, PackageCollection):
            return elem
        return None


class MultiLanguageReferrable(Referrable):
    """Group AR:MULTILANGUAGE-REFERRABLE."""

    def __init__(self,
                 name: str,
                 long_name: Union[MultilanguageLongName, None] = None) -> None:
        super().__init__(name)
        self.long_name: MultilanguageLongName | None = None
        if long_name is not None:
            from autosar.xml.elements.documentation import MultilanguageLongName
            if isinstance(long_name, MultilanguageLongName):
                self.long_name = long_name
            else:
                raise TypeError(
                    f'long_name: Expected type "MultilanguageLongName", got "{str(type(long_name))}"')


class Identifiable(MultiLanguageReferrable):
    """Group AR:IDENTIFIABLE."""

    def __init__(self,
                 name: str,
                 desc: Union[MultiLanguageOverviewParagraph, tuple[ar_enum.Language, str], str, None] = None,
                 category: str | None = None,
                 uuid: str | None = None,
                 admin_data: AdminData | SpecialDataGroup | list[SpecialDataGroup] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.desc: MultiLanguageOverviewParagraph | None = None
        self.category: str | None = None
        self.introduction = None
        self.annotations = None
        self.uuid: str | None = None
        self.admin_data: AdminData | None = None
        if desc is not None:
            from autosar.xml.elements.documentation import MultiLanguageOverviewParagraph
            if isinstance(desc, MultiLanguageOverviewParagraph):
                self.desc = desc
            elif isinstance(desc, str):
                self.desc = MultiLanguageOverviewParagraph.make(ar_enum.Language.FOR_ALL, desc)
            elif isinstance(desc, tuple) and len(desc) == 2:
                self.desc = MultiLanguageOverviewParagraph.make(*desc)
            else:
                raise TypeError(f"Invalid type for argument 'desc': {str(type(desc))}")
        self._assign_optional('category', category, str)
        self._assign_optional('uuid', uuid, str)
        if admin_data is not None:
            if isinstance(admin_data, AdminData):
                self.admin_data = admin_data
            elif isinstance(admin_data, (SpecialDataGroup, Iterable)):
                self.admin_data = AdminData(admin_data)
            else:
                expected_type = "AdminData"
                actual_type = str(type(admin_data))
                raise TypeError(f"admin_data: Expected type {expected_type}. Got {actual_type}")

    def update_ref_parts(self, ref_parts: list[str]):
        """Utility method used for generating reference strings."""
        ref_parts.append(self.name)
        if self.parent is None:
            ref_parts.append(None)
        else:
            self.parent.update_ref_parts(ref_parts)

    def _calc_ref_string(self) -> str | None:
        """Calculate reference string based on parent tree.

        If a missing parent is detected during tree-traversal
        the function as a whole will returns None.
        """
        if self.parent is None:
            return None
        ref_parts: list[str] = [self.name]
        self.parent.update_ref_parts(ref_parts)
        if ref_parts[-1] is None:
            return None
        return '/'.join(reversed(ref_parts))


class CollectableElement(Identifiable):
    """Group AR:COLLECTABLE-ELEMENT.

    Meta-class that identifies either an
    AR:PACKAGE or AR-ELEMENT.
    Both types can be placed inside another
    package.
    """


class ARElement(CollectableElement):
    """Group AR:AR-ELEMENT.

    Base class for all package-elements.
    """


# Utility functions


def make_unique_name_in_list(elements: list[Referrable], base_name: str):
    """Attempt to find a unique name in the list of elements.

    This function can modify names in the given list.
    If an element with the name base_name already exists in the list it will
    append "_0" to the existing element and any newly added element will have
    its suffix automatically increased by 1.
    Returns a new name which is guaranteed to be unique in the given list.
    """
    has_index = False
    highest_index = 0
    unpatched_elem: Referrable | None = None
    expr = re.compile(base_name + r'_(\d+)')
    for element in elements:
        result = expr.match(element.name)
        if result is not None:
            has_index = True
            index = int(result.group(1))
            highest_index = max(highest_index, index)
        elif element.name == base_name:
            unpatched_elem = element
    if unpatched_elem is not None:
        unpatched_elem.name = '_'.join([unpatched_elem.name, '0'])
    if has_index or unpatched_elem is not None:
        return '_'.join([base_name, str(highest_index + 1)])
    else:
        return base_name


# --- Admin data elements


class SpecialDataElement(NamedTuple):
    """Complex type AR:SD.

    Tag variants: 'SD'
    """

    text: str
    gid: str | None = None


class SpecialDataValue(NamedTuple):
    """Complex type AR:SDF.

    Tag variants: 'SDF'
    """

    value: int | float
    gid: str | None = None


SpecialDataGroupContent = Union[str,
                                int,
                                float,
                                tuple[str, str],
                                tuple[int | float, str],
                                SpecialDataElement,
                                "SpecialDataGroup",
                                dict]


class SpecialDataGroup(ARObject):
    """Complex type AR:SDG.

    Tag variants: 'SDG'

    The content can be one of:
    1. string: simple SD element with text and no GID.
        XML: <SD>content</SD>
    2. int or float: An SDF element with a numerical value.
        XML: <SDF>value</SDF>
    3. tuple[str, str]: SD element with GID as first element and content as second element.
       XML: <SD GID="content[0]>content[1]</SD>
    4. tuple[str, int | float]: SDF element with GID as first element and value as second element.
       XML: <SDF GID="content[1]>content[0]</SDF>
    5. An instance of SpecialDataElement which is the named tuple version of (3) above
    6. An instance of SpecialDataValue which is the named tuple version of (4) above
    7. A dictionary representing a nested SpecialDataGroup (<SDG> inside <SDG>)
    8. A list of any combination of (1) to (7) above
    """

    def __init__(self,
                 gid: str | None = None,
                 content: SpecialDataGroupContent | None = None,
                 caption: str | None = None,) -> None:
        super().__init__()
        # GID attribute
        self.gid: str | None = None
        # .SDG-CAPTION
        self.caption: str | None = None
        # SDG-CONTENTS
        self.content: list[SpecialDataElement | SpecialDataGroup] = []
        self._assign_optional("gid", gid, str)
        self._assign_optional("caption", caption, str)
        if content is not None:
            if isinstance(content, list):
                for elem in content:
                    self.append_content(elem)
            else:
                self.append_content(content)

    def append_content(self, content: SpecialDataGroupContent) -> None:
        """Add new content to internal content list.

        When adding nested content (SpecialDataGroup inside SpecialDataGroup) use the dict type.
        Valid dictionary keys are:
        - gid: str
        - caption: str
        - content: str | tuple[str, str] | SpecialDataElement | list | dict
        """
        if isinstance(content, dict):
            child_gid = content.get("gid")
            child_content = content.get("content")
            child_caption = content.get("caption")
            nested = SpecialDataGroup(child_gid, child_content, child_caption)
            self.content.append(nested)
        elif isinstance(content, (SpecialDataElement, SpecialDataGroup)):
            self.content.append(content)
        elif isinstance(content, str):
            self.content.append(SpecialDataElement(content))
        elif isinstance(content, (int, float)):
            self.content.append(SpecialDataValue(content))
        elif isinstance(content, tuple):
            if len(content) != 2:
                raise ValueError("content: Length of tuple must be exactly 2")
            if not isinstance(content[0], str):
                expected_type = "string"
                actual_type = str(type(content[0]))
                raise TypeError(f"content: First tuple element must be of type {expected_type}. Got {actual_type}")
            if isinstance(content[1], str):
                self.content.append(SpecialDataElement(content[1], gid=content[0]))
            elif isinstance(content[1], (int, float)):
                self.content.append(SpecialDataValue(content[1], gid=content[0]))
            else:
                expected_type = "string, int or float"
                actual_type = str(type(content[1]))
                raise TypeError(f"content: Second tuple element must be of type {expected_type}. Got {actual_type}")
        else:
            raise TypeError(f"content: Unsupported type '{str(type(content))}'")


class Modification(ARObject):
    """Complex type AR:MODIFICATION.

    Tag variants: 'MODIFICATION'
    """

    def __init__(self,
                 change: MultiLanguageOverviewParagraph | tuple[ar_enum.Language, str] | None = None,
                 reason: MultiLanguageOverviewParagraph | tuple[ar_enum.Language, str] | None = None) -> None:
        super().__init__()
        # .CHANGE
        self.change: MultiLanguageOverviewParagraph | None = None
        # .REASON
        self.reason: MultiLanguageOverviewParagraph | None = None
        expected_type = "MultiLanguageOverviewParagraph or tuple[enum Language, str]"
        if change is not None:
            from autosar.xml.elements.documentation import MultiLanguageOverviewParagraph
            if isinstance(change, MultiLanguageOverviewParagraph):
                self.change = change
            elif isinstance(change, tuple):
                self.change = MultiLanguageOverviewParagraph(change)
            else:
                actual_change_type = str(type(change))
                raise TypeError(f"change: Expected type {expected_type}, got {actual_change_type}")
        if reason is not None:
            from autosar.xml.elements.documentation import MultiLanguageOverviewParagraph
            if isinstance(reason, MultiLanguageOverviewParagraph):
                self.reason = reason
            elif isinstance(reason, tuple):
                self.reason = MultiLanguageOverviewParagraph(reason)
            else:
                actual_reason_type = str(type(reason))
                raise TypeError(f"reason: Expected type {expected_type}, got {actual_reason_type}")


ModificationsArgumentType = Union[tuple[ar_enum.Language, str],
                                  list[tuple[ar_enum.Language, str]],
                                  Modification,
                                  list[Modification]]


class DocRevision(ARObject):
    """Complex type AR:DOC-REVISION.

    Tag variants: 'DOC-REVISION'
    """

    def __init__(self,
                 revision_label: str | RevisionLabelString | None = None,
                 revision_label_p1: str | RevisionLabelString | None = None,
                 revision_label_p2: str | RevisionLabelString | None = None,
                 state: str | None = None,
                 issued_by: str | None = None,
                 date: str | Date | datetime.date | datetime.datetime | None = None,
                 modifications: ModificationsArgumentType | None = None
                 ) -> None:
        super().__init__()
        # .REVISION-LABEL
        self.revision_label: str | RevisionLabelString | None = None
        # .REVISION-LABEL-P-1
        self.revision_label_p1: str | RevisionLabelString | None = None
        # .REVISION-LABEL-P-2
        self.revision_label_p2: str | RevisionLabelString | None = None
        # .STATE
        self.state: str | None = None
        # .ISSUED-BY
        self.issued_by: str | None = None
        # .DATE
        self.date: Date | None = None
        # .MODIFICATIONS
        self.modifications: list[Modification] = []
        revision_error = "{0}: Expected str or RevisionLabelString. Got {1}"
        if revision_label is not None:
            from autosar.xml.elements.documentation import RevisionLabelString
            if isinstance(revision_label, RevisionLabelString):
                self.revision_label = revision_label
            elif isinstance(revision_label, str):
                self.revision_label = RevisionLabelString(revision_label)
            else:
                raise TypeError(revision_error.format("revision_label", str(type(revision_label))))
        if revision_label_p1 is not None:
            from autosar.xml.elements.documentation import RevisionLabelString
            if isinstance(revision_label_p1, RevisionLabelString):
                self.revision_label_p1 = revision_label_p1
            elif isinstance(revision_label_p1, str):
                self.revision_label_p1 = RevisionLabelString(revision_label_p1)
            else:
                raise TypeError(revision_error.format("revision_label_p1", str(type(revision_label_p1))))
        if revision_label_p2 is not None:
            from autosar.xml.elements.documentation import RevisionLabelString
            if isinstance(revision_label_p2, RevisionLabelString):
                self.revision_label_p2 = revision_label_p2
            elif isinstance(revision_label_p2, str):
                self.revision_label_p2 = RevisionLabelString(revision_label_p2)
            else:
                raise TypeError(revision_error.format("revision_label_p2", str(type(revision_label_p2))))
        self._assign_optional_strict("state", state, str)
        self._assign_optional_strict("issued_by", issued_by, str)
        if date is not None:
            from autosar.xml.elements.documentation import Date
            if isinstance(date, Date):
                self.date = date
            elif isinstance(date, (str, datetime.date, datetime.datetime)):
                self.date = Date(date)
            else:
                raise TypeError(f"date: Expected type str, Date, date or datetime. Got {str(type(date))}")
        if modifications is not None:
            if isinstance(modifications, (tuple, Modification)):
                self.append_modification(modifications)
            elif isinstance(modifications, Iterable):
                for modification in modifications:
                    self.append_modification(modification)
            else:
                raise TypeError(f"modifications: Expected tuple, Modification or list. Got {str(type(modifications))}")

    def append_modification(self, modification: tuple[ar_enum.Language, str] | Modification) -> None:
        """Append modification to internal list of modifications."""
        if isinstance(modification, Modification):
            self.modifications.append(modification)
        elif isinstance(modification, tuple) and len(modification) == 2:
            from autosar.xml.elements.documentation import MultiLanguageOverviewParagraph
            self.modifications.append(Modification(change=MultiLanguageOverviewParagraph(modification)))
        else:
            expected_type = "tuple[enum 'Language', str] or Modification"
            actual_type = str(type(modification))
            raise TypeError(f"modification: Expected {expected_type}. Got {actual_type}")


UsedLanguageArgtype = Union["MultiLanguagePlainText",
                            SingleLanguageText,
                            "LanguagePlainText",
                            list[SingleLanguageText],
                            list["LanguagePlainText"],
                            ar_enum.Language,
                            list[ar_enum.Language]]


class AdminData(ARObject):
    """Complex type AR:ADMIN-DATA.

    Tag variants: 'ADMIN-DATA'
    """

    def __init__(self,
                 sdgs: SpecialDataGroup | list[SpecialDataGroup] | None = None,
                 language: ar_enum.Language | None = None,
                 used_languages: UsedLanguageArgtype | None = None,
                 doc_revisions: DocRevision | list[DocRevision] | None = None,
                 gid: str | None = None,
                 content: SpecialDataGroupContent | None = None,
                 ) -> None:
        """Initialize AdminData.

        You can use the `sdgs` parameter for full support of special data groups.
        Alternatively, use the `gid` and `content` parameters to conveniently
        create AdminData with a single special data group.
        """
        super().__init__()
        # .SDGS
        self.sdgs: list[SpecialDataGroup] = []
        # .LANGUAGE
        self.language: ar_enum.Language | None = None
        # .USED-LANGUAGES
        self.used_languages: MultiLanguagePlainText | None = None
        # .DOC-REVISIONS
        self.doc_revisions: list[DocRevision] = []

        self._assign_optional("language", language, ar_enum.Language)
        if used_languages is not None:
            from autosar.xml.elements.documentation import LanguagePlainText, MultiLanguagePlainText

            if isinstance(used_languages, MultiLanguagePlainText):
                self.used_languages = used_languages
            elif isinstance(used_languages, (tuple, LanguagePlainText)):
                self.used_languages = MultiLanguagePlainText(used_languages)
            elif isinstance(used_languages, ar_enum.Language):
                part = SingleLanguageText(used_languages)
                self.used_languages = MultiLanguagePlainText(part)
            elif isinstance(used_languages, Iterable):
                elements = []
                for element in used_languages:
                    if isinstance(element, (tuple, LanguagePlainText)):
                        elements.append(element)
                    elif isinstance(element, ar_enum.Language):
                        elements.append(LanguagePlainText(element))
                    else:
                        raise TypeError(f"used_languages: Failed to add part from type {str(type(element))}")
                self.used_languages = MultiLanguagePlainText(elements)
            else:
                raise TypeError(f"used_languages: Unsupported type {str(type(used_languages))}")

        if doc_revisions is not None:
            if isinstance(doc_revisions, Iterable):
                for revision in doc_revisions:
                    self.append_doc_revision(revision)
            else:
                self.append_doc_revision(doc_revisions)

        if sdgs is None:
            if gid is not None or content is not None:
                self.append_special_data_group(SpecialDataGroup(gid, content))
        else:
            if isinstance(sdgs, Iterable):
                for sdg in sdgs:
                    self.append_special_data_group(sdg)
            else:
                self.append_special_data_group(sdgs)

    def append_doc_revision(self, revision: DocRevision) -> None:
        """Append a DocRevision to this AdminData object."""
        if isinstance(revision, DocRevision):
            self.doc_revisions.append(revision)
        else:
            raise TypeError(f"revision: Expected type DocRevision. Got {str(type(revision))}")

    def append_special_data_group(self, sdg: SpecialDataGroup) -> None:
        """Append a special data grouup to this AdminData object."""
        if isinstance(sdg, SpecialDataGroup):
            self.sdgs.append(sdg)
        else:
            raise TypeError(f"sdg: Expected type SpecialDataGroup. Got {str(type(sdg))}")


__all__ = [
    "NumericalValue",
    "PositiveIntegerValue",
    "Referrable",
    "MultiLanguageReferrable",
    "Identifiable",
    "CollectableElement",
    "ARElement",
    "make_unique_name_in_list",
    "SpecialDataElement",
    "SpecialDataValue",
    "SpecialDataGroupContent",
    "SpecialDataGroup",
    "Modification",
    "ModificationsArgumentType",
    "DocRevision",
    "UsedLanguageArgtype",
    "AdminData",
    "SingleLanguageText",
]
