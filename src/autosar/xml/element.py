"""
Classes related to AUTOSAR XML Elements
"""

import re
from collections import OrderedDict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, Union, NamedTuple


from autosar.base import split_ref, split_ref_strict, Searchable
from autosar.xml.base import ARObject, BaseRef
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except
from autosar.xml.reference import (SwBaseTypeRef,  # noqa F401
                                   PackageRef,
                                   CompuMethodRef,
                                   FunctionPtrSignatureRef,
                                   ImplementationDataTypeRef,
                                   SwAddrMethodRef,
                                   DataConstraintRef,
                                   PhysicalDimensionRef,
                                   UnitRef,
                                   IndexDataTypeRef,
                                   ApplicationDataTypeRef,
                                   ApplicationCompositeElementDataPrototypeRef,
                                   AutosarDataTypeRef,
                                   ConstantRef,
                                   VariableDataPrototypeRef,
                                   ParameterDataPrototypeRef,
                                   ApplicationErrorRef,
                                   ModeDeclarationRef,
                                   ModeDeclarationGroupRef,
                                   ModeDeclarationGroupPrototypeRef,
                                   AutosarDataPrototypeRef,
                                   E2EProfileCompatibilityPropsRef,
                                   ClientServerOperationRef,
                                   PortPrototypeRef,
                                   AbstractImplementationDataTypeElementRef,
                                   DataPrototypeRef,
                                   PortInterfaceRef,
                                   SwComponentTypeRef,
                                   SwComponentPrototypeRef,
                                   SwcInternalBehaviorRef,
                                   SwcImplementationRef,
                                   ExclusiveAreaRef,
                                   ExclusiveAreaNestingOrderRef,
                                   AbstractRequiredPortPrototypeRef,
                                   AbstractProvidedPortPrototypeRef,
                                   RunnableEntityRef,
                                   VariableAccessRef,
                                   ModeSwitchPointRef,
                                   AsynchronousServerCallPointRef,
                                   AsynchronousServerCallResultPointRef,
                                   TriggerRef,
                                   InternalTriggeringPointRef,
                                   RteEventRef,
                                   DataTypeMappingSetRef,
                                   ArgumentDataPrototypeRef,
                                   ApplicationArrayElementRef,
                                   ApplicationRecordElementRef,
                                   )


alignment_type_re = re.compile(
    r"[1-9][0-9]*|0[xX][0-9a-fA-F]*|0[bB][0-1]+|0[0-7]*|UNSPECIFIED|UNKNOWN|BOOLEAN|PTR")

display_format_str_re = re.compile(
    r"%[ \-+#]?[0-9]*(\.[0-9]+)?[diouxXfeEgGcs]")

# Type aliases

BaseReference = BaseRef  # This line is simply here to suppress an unused import warning

ValueSpecificationElement = Union["TextValueSpecification",
                                  "NumericalValueSpecification",
                                  "NotAvailableValueSpecification",
                                  "ArrayValueSpecification",
                                  "RecordValueSpecification",
                                  "ApplicationValueSpecification",
                                  "ConstantReference"]

PortPrototypeElement = Union["ProvidePortPrototype",
                             "RequirePortPrototype",
                             "PRPortPrototype"]

SwConnectorElement = Union["AssemblySwConnector",
                           "DelegationSwConnector",
                           "PassThroughSwConnector"]

InitValueArgType = Union["int",
                         "float",
                         "str",
                         "list",
                         "tuple",
                         "ValueSpecificationElement",
                         "ConstantRef"]

# Helper classes


class NumericalValue:
    """
    Wrapper for numerical value
    """

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
        """Value property"""
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
    """
    Wrapper for positive value
    """

    def __init__(self,
                 value: int,
                 value_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        self._value = self._validate_value(value)
        self.value_format = value_format

    @property
    def value(self):
        """Value property"""
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
    """
    Group AR:REFERRABLE
    """

    def __init__(self, name: str) -> None:
        self.name: str = name  # .SHORT-NAME
        self.parent: Union["CollectableElement", "PackageCollection", None] = None

    @property
    def short_name(self) -> str:
        """
        Alias for "name"
        """
        return self.name

    def root_collection(self) -> Union["PackageCollection", None]:
        """
        Returns the root package collection object or None if it can't be found.
        A package collection can be either a Workspace or a Document object depending
        on how the packages/elements was created initially.
        """
        elem = self
        while elem.parent is not None:
            elem = elem.parent
        if isinstance(elem, PackageCollection):
            return elem
        return None


class MultiLanguageReferrable(Referrable):
    """
    Group AR:MULTILANGUAGE-REFERRABLE
    """

    def __init__(self,
                 name: str,
                 long_name: Union["MultilanguageLongName", None] = None) -> None:
        super().__init__(name)
        self.long_name: MultilanguageLongName | None = None
        if long_name is not None:
            if isinstance(long_name, MultilanguageLongName):
                self.long_name = long_name
            else:
                raise TypeError(
                    f'long_name: Expected type "MultilanguageLongName", got "{str(type(long_name))}"')


class Identifiable(MultiLanguageReferrable):
    """
    Group AR:IDENTIFIABLE
    """

    def __init__(self,
                 name: str,
                 desc: Union["MultiLanguageOverviewParagraph", tuple[ar_enum.Language, str], str, None] = None,
                 category: str | None = None,
                 uuid: str | None = None,
                 admin_data: Union["AdminData", None] = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.desc: MultiLanguageOverviewParagraph | None = None
        self.category = None
        self.admin_data = None
        self.introduction = None
        self.annotations = None
        self.uuid = None
        self.admin_data: Union["AdminData", None] = None
        if desc is not None:
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

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used for generating reference strings
        """
        ref_parts.append(self.name)
        if self.parent is None:
            ref_parts.append(None)
        else:
            self.parent.update_ref_parts(ref_parts)

    def _calc_ref_string(self) -> str | None:
        """
        Calculates reference string based on parent tree
        If a missing parent is detected during tree-traversal
        the function as a whole will returns None
        """
        if self.parent is None:
            return None
        ref_parts: list[str] = [self.name]
        self.parent.update_ref_parts(ref_parts)
        if ref_parts[-1] is None:
            return None
        return '/'.join(reversed(ref_parts))


class CollectableElement(Identifiable):
    """
    Group AR:COLLECTABLE-ELEMENT

    Meta-class that identifies either an
    AR:PACKAGE or AR-ELEMENT.
    Both types can be placed inside another
    package.
    """


class ARElement(CollectableElement):
    """
    Group AR:AR-ELEMENT

    Base class for all package-elements
    """

# Utility functions


def make_unique_name_in_list(elements: list[Referrable], base_name: str):
    """
    Attempts to find a unique name in the list of elements.
    This function can modify names in the given list.
    If an element with the name base_name already exists in the list it will
    append "_0" to the existing element and any newly added element will have
    its suffix automatically increased by 1.
    Returns a new name which is guaranteed to be unique in the given list
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


# Common structure elements

class SpecialDataElement(NamedTuple):
    """
    Special data element:
    Tag variant: 'SD'
    """
    text: str
    gid: str | None = None


class SpecialDataValue(NamedTuple):
    """
    Numerical special data element:
    Tag variant: 'SDF'
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
    """
    Complex type: AR:SDG
    Tag variants: 'SDG'

    The content can be one of:
    1. string: simple SD element with text and no GID.
        XML: <SD>content</SD>
    2. int or float: An SDF element with a numerical value.
        XML: <SDF>value</SDF>
    3. tuple[str, str]: SD element with text as first element and GID as second element.
       XML: <SD GID="content[1]>content[0]</SD>
    4. tuple[str, int | float]: SDF element with value as first element and GID as second element.
       XML: <SDF GID="content[1]>content[0]</SDF>
    5. An instance of SpecialDataElement which is the named tuple version of (3) above
    6. An instance of SpecialDataValue which is the named tuple version of (4) above
    7. A dictionary representing a nested SpecialDataGroup (<SDG> inside <SDG>)
    8. A list of any combination of (1) to (7) above
    """
    def __init__(self,
                 gid: str | None = None,
                 caption: str | None = None,
                 content: SpecialDataGroupContent | None = None) -> None:
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
        """
        Adds new content to internal content list.

        When adding nested content (SpecialDataGroup inside SpecialDataGroup) use the dict type.
        Valid dictionary keys are:
        - gid: str
        - caption: str
        - content: str | tuple[str, str] | SpecialDataElement | list | dict
        """
        if isinstance(content, dict):
            gid = content.get("gid")
            caption = content.get("caption")
            content = content.get("content")
            nested = SpecialDataGroup(gid, caption, content)
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
            if not isinstance(content[1], str):
                msg1 = "content: Second tuple element must be of type string."
                msg2 = f" Got {str(type(content[1]))}"
                raise TypeError(msg1 + msg2)
            if isinstance(content[0], str):
                self.content.append(SpecialDataElement(content[0], content[1]))
            elif isinstance(content[0], (int, float)):
                self.content.append(SpecialDataValue(content[0], content[1]))
            else:
                msg1 = "content: First tuple element must be of type string, int or float."
                msg2 = f" Got {str(type(content[0]))}"
                raise TypeError(msg1 + msg2)
        else:
            raise TypeError(f"content: Unsupported type '{str(type(content))}'")


class AdminData(ARObject):
    """
    Complex type AR:ADMIN-DATA
    Tag variants: 'ADMIN-DATA'
    """

    def __init__(self, data: dict | None = None) -> None:
        self.data = data


class DataFilter(ARObject):
    """
    Complex type AR:DATA-FILTER
    Tag variants: 'FILTER' | 'DATA-FILTER'
    """

    def __init__(self,
                 data_filter_type: ar_enum.DataFilterType | None = None,
                 min_val: int | None = None,
                 max_val: int | None = None,
                 mask: int | None = None,
                 offset: int | None = None,
                 period: int | None = None,
                 x: int | None = None,                # pylint: disable=C0103
                 ) -> None:
        super().__init__()
        self.data_filter_type: ar_enum.DataFilterType | None = None
        self.min_val: int | None = None
        self.max_val: int | None = None
        self.mask: int | None = None
        self.offset: int | None = None
        self.period: int | None = None
        self.x: int | None = None                     # pylint: disable=C0103
        self._assign_optional("data_filter_type", data_filter_type, ar_enum.DataFilterType)  # .DATA-FILTER-TYPE
        self._assign_optional("mask", mask, int)  # .MASK
        self._assign_optional("max_val", max_val, int)  # .MAX
        self._assign_optional("min_val", min_val, int)  # .MIN
        self._assign_optional("offset", offset, int)  # .OFFSET
        self._assign_optional("period", period, int)  # .PERIOD
        self._assign_optional("x", x, int)  # .X


class EngineeringObject(ARObject):
    """
    Group AR:ENGINEERING-OBJECT
    """

    def __init__(self,
                 label: str | None = None,
                 category: str | None = None) -> None:
        super().__init__()
        self.label: str | None = None  # .SHORT-LABEL
        self.category: str | None = None  # .CATEGORY
        self._assign_optional_strict("label", label, str)
        self._assign_optional_strict("category", category, str)


class AutosarEngineeringObject(EngineeringObject):
    """
    Complex type AR:AUTOSAR-ENGINEERING-OBJECT
    Tag variants: 'AUTOSAR-ENGINEERING-OBJECT' | 'ARTIFACT-DESCRIPTOR'

    Same constructor as parent class
    """


class Code(Identifiable):
    """
    Complex type AR:CODE
    Tag variants: 'CODE'
    """

    def __init__(self,
                 name: str,
                 artifact_descriptors: AutosarEngineeringObject | list[AutosarEngineeringObject] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.artifact_descriptors: list[AutosarEngineeringObject] = []  # .
        # .CALLBACK-HEADER-REFS not yet supported
        if artifact_descriptors is not None:
            if isinstance(artifact_descriptors, AutosarEngineeringObject):
                self.append_artifact_descriptor(artifact_descriptors)
            else:
                for artifact_descriptor in artifact_descriptors:
                    self.append_artifact_descriptor(artifact_descriptor)

    def append_artifact_descriptor(self, artifact_descriptor: AutosarEngineeringObject) -> None:
        """
        Appends artifact_descriptor to internal list of descriptors
        """
        if isinstance(artifact_descriptor, AutosarEngineeringObject):
            self.artifact_descriptors.append(artifact_descriptor)
        else:
            raise TypeError("artifact_descriptor must be of type AutosarEngineeringObject")


class Implementation(ARElement):
    """
    Group AR:IMPLEMENTATION
    """

    def __init__(self,
                 name: str,
                 code_descriptors: Code | list[Code] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .BUILD-ACTION-MANIFEST-REF-CONDITIONAL not yet supported
        self.code_descriptors: list[Code] = []  # .CODE-DESCRIPTORS
        # .COMPILERS not yet supported
        # .GENERATED-ARTIFACTS not yet supported
        # .HW-ELEMENT-REFS not yet supported
        # .LINKERS not yet supported
        # .MC-SUPPORT not yet supported
        # .PROGRAMMING-LANGUAGE not yet supported
        # .REQUIRED-ARTIFACTS not yet supported
        # .REQUIRED-GENERATOR-TOOLS not yet supported
        # .RESOURCE-CONSUMPTION not yet supported
        # .SW-VERSION not yet supported
        # .SWC-BSW-MAPPING-REF not yet supported
        # .USED-CODE-GENERATOR not yet supported
        # .VENDOR-ID not yet supported
        if code_descriptors is not None:
            if isinstance(code_descriptors, Code):
                self.append_code_descriptor(code_descriptors)
            else:
                for code_descriptor in code_descriptors:
                    self.append_code_descriptor(code_descriptor)

    def append_code_descriptor(self, code_descriptors: Code) -> None:
        """
        Appends code descriptor to internal list of descriptors
        """
        if isinstance(code_descriptors, Code):
            self.code_descriptors.append(code_descriptors)
        else:
            raise TypeError("code_descriptors must be of type Code")


# --- Documentation Elements


class Break(ARObject):
    """
    Complex type AR:BR
    Tag variants: BR

    Same function as the html element.
    """


class EmphasisText(ARObject):
    """
    Complex type AR:EMPHASIS-TEXT
    Tag variants: E

    Emphasized text

    Limitations: No support for child-elements. Type for argument elements must be string.
    """

    def __init__(self,
                 elements: None | list | str = None,
                 color: str = None,
                 font: ar_enum.EmphasisFont = None,
                 type: ar_enum.EmphasisType = None) -> None:  # pylint: disable=redefined-builtin
        self.elements = []
        self.color = color  # Attribute @COLOR
        self.font = font  # Attribute @FONT
        self.type = type  # Attribute @TYPE
        if elements is not None:
            if isinstance(elements, str):
                self.elements.append(elements)
            else:
                raise NotImplementedError("List of elements not yet supported")


class IndexEntry(ARObject):
    """
    Complex type AR:INDEX-ENTRY
    Tag variants: IE

    Index Entry

    Limitations: Doesn't support sub-elements as seen in XML schema.
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Text content


class TechnicalTerm(ARObject):
    """
    Complex type AR:TT
    Tag variants: TT

    Technical Term

    """

    def __init__(self,
                 text: str,
                 tex_render: str = None,
                 type: str = None) -> None:  # pylint: disable=redefined-builtin
        self.tex_render = tex_render  # attribute @TEX-RENDER
        self.type = type  # attribute @TYPE
        self.text = text  # Text content


class Subscript(ARObject):
    """
    Complex type AR:SUPSCRIPT
    Tag variants: SUB

    Subscript is based on the same Complex type as superscript

    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content


class Superscript(ARObject):
    """
    Complex type AR:SUPSCRIPT
    Tag variants: SUP

    Superscript
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content

    def __str__(self) -> str:
        """
        Convert to basic string
        """
        return "^" + self.text


class LanguageSpecific(ARObject):
    """
    Complex type AR:LANGUAGE-SPECIFIC
    """

    def __init__(self, language: ar_enum.Language) -> None:
        assert isinstance(language, ar_enum.Language)
        self.language = language  # Attribute @L


class MixedContentForLongName(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-LONG-NAME
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | TT | E | SUP | SUB | IE

    def append(self, part: str | TechnicalTerm | EmphasisText | Subscript | Subscript):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, TechnicalTerm, EmphasisText, Subscript, Subscript, IndexEntry)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class MixedContentForOverviewParagraph(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-OVERVIEW-PARAGRAPH
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | TT | E | SUP | SUB | IE
        # Unsupported elements:
        # FT : AR:SL-OVERVIEW-PARAGRAPH
        # TRACE-REF: Complex type
        # XREF: AR:-XREF-TARGET

    def append(self, part: str | TechnicalTerm | EmphasisText | Subscript | Subscript):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, TechnicalTerm, EmphasisText, Subscript, Subscript, IndexEntry)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class LanguageLongName(MixedContentForLongName):
    """
    Complex type AR:L-LONG-NAME
    Tag variants: L-4

    Longname for a specific language.

    The parts parameter can be a single string or a list of mixed types.

    Accepted mixed types:
    * strings
    * TechnicalTerm
    * EmphasisText
    * Subscript
    * Subscript
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultilanguageLongName(ARObject):
    """
    Complex type AR:MULTILANGUAGE-LONG-NAME
    Tag variants: 'LABEL' | 'LONG-NAME'
    """

    def __init__(self,
                 long_name: None | tuple[ar_enum.Language,
                                         str] | LanguageLongName = None) -> None:
        self.elements: list[LanguageLongName] = []
        if long_name is not None:
            if isinstance(long_name, LanguageLongName):
                self.append(long_name)
            elif isinstance(long_name, tuple):
                self.append(LanguageLongName(long_name[0], long_name[1]))
            else:
                raise TypeError('Invalid type for long_name. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageLongName,'
                                f' got "{str(type(long_name))}"')

    def append(self, long_name: LanguageLongName) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(long_name, LanguageLongName)
        self.elements.append(long_name)


class LanguageOverviewParagraph(MixedContentForOverviewParagraph):
    """
    Complex type AR:L-OVERVIEW-PARAGRAPH
    Tag variants: 'L-2'

    Overview paragraph for specific language

    The parts parameter can be a single string or a list of mixed types.

    Accepted mixed types:
    * strings
    * TechnicalTerm
    * EmphasisText
    * Subscript
    * Subscript
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultiLanguageOverviewParagraph(ARObject):
    """
    Complex type AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
    Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
    """

    def __init__(self,
                 paragraph: None | tuple[ar_enum.Language,
                                         str] | LanguageOverviewParagraph = None) -> None:
        self.elements: list[LanguageOverviewParagraph] = []
        if paragraph is not None:
            if isinstance(paragraph, LanguageOverviewParagraph):
                self.append(paragraph)
            elif isinstance(paragraph, tuple) and len(paragraph) == 2:
                self.append(LanguageOverviewParagraph(*paragraph))
            else:
                raise TypeError('Invalid type for paragraph. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageOverviewParagraph,'
                                f' got "{str(type(paragraph))}"')

    def append(self, paragraph: LanguageOverviewParagraph) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(paragraph, LanguageOverviewParagraph)
        self.elements.append(paragraph)

    @classmethod
    def make(cls, language: ar_enum.Language, paragraph: str):
        """
        #convenience-method

        Simplified creation method that uses a simple string as paragraph text
        """
        return cls(LanguageOverviewParagraph(language, paragraph))


class DocumentViewSelectable(ARObject):
    """
    Group AR:DOCUMENT-VIEW-SELECTABLE
    """

    def __init__(self,
                 semantic_information: None | str = None,
                 view: None | str = None) -> None:
        self.semantic_information = semantic_information  # Attribute 'SI'
        self.view = view  # Attribute 'VIEW'
        if semantic_information is not None and (not isinstance(semantic_information, str)):
            raise TypeError(
                f"semantic_information: Expected type 'str', got '{str(type(semantic_information))}'")
        if view is not None and (not isinstance(view, str)):
            raise TypeError(
                f"view: Expected type 'str', got '{str(type(view))}'")


class Paginateable(DocumentViewSelectable):
    """
    Group AR:PAGINATEABLE
    """

    def __init__(self,
                 page_break: None | ar_enum.PageBreak = None,
                 keep_with_previous: None | ar_enum.KeepWithPrevious = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.page_break = page_break  # Attribute 'BREAK'
        self.keep_with_previous = keep_with_previous  # Attribute 'KEEP-WITH-PREVIOUS'
        if (page_break is not None) and (not isinstance(page_break, ar_enum.PageBreak)):
            raise TypeError(
                f"page_break: Expected type 'PageBreak', got '{str(type(page_break))}'")
        if (keep_with_previous is not None) and (not isinstance(keep_with_previous, ar_enum.KeepWithPrevious)):
            raise TypeError(
                f"page_break: Expected type 'PageBreak', got '{str(type(keep_with_previous))}'")


class MixedContentForParagraph(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-PARAGRAPH
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | BR | E | IE | SUB | SUP | TT
        # Unsupported elements:
        # FT : AR:SL-OVERVIEW-PARAGRAPH
        # STD: AR:STD
        # TRACE-REF : Specialization of AR:REF
        # XDOC: AR:XDOC
        # XFILE: AR:XFILE
        # XREF: AR:XREF
        # XREF-TARGET: AR:-XREF-TARGET

    def append(self,
               part: str | Break | EmphasisText | IndexEntry | Subscript | Subscript | TechnicalTerm):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, Break, EmphasisText, IndexEntry, Subscript, Subscript, TechnicalTerm)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class LanguageParagraph(MixedContentForParagraph):
    """
    Complex type AR:L-PARAGRAPH
    Tag variants: 'L-1'

    Paragraph for specific language

    The parts parameter can be a single string or a list of mixed types.

    Accepted mixed types:
    * strings
    * Break
    * EmphasisText
    * TechnicalTerm
    * Subscript
    * Subscript
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultiLanguageParagraph(Paginateable):
    """
    Complex type AR:MULTI-LANGUAGE-PARAGRAPH
    Tag variants: 'P'
    """

    def __init__(self,
                 paragraph: None | tuple[ar_enum.Language,
                                         str] | LanguageParagraph = None,
                 help_entry: None | str = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.help_entry = help_entry  # Attribute 'HELP-ENTRY'
        self.elements: list[LanguageParagraph] = []
        if paragraph is not None:
            if isinstance(paragraph, LanguageParagraph):
                self.append(paragraph)
            elif isinstance(paragraph, tuple):
                self.append(LanguageParagraph(paragraph[0], paragraph[1]))
            else:
                raise TypeError('Invalid type for paragraph. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageParagraph,'
                                f' got "{str(type(paragraph))}"')

    def append(self, paragraph: LanguageParagraph) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(paragraph, LanguageParagraph)
        self.elements.append(paragraph)


class MixedContentForVerbatim(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-VERBATIM

    This includes AR:WHITESPACE-CONTROLLED as it
    does not have any attributes or elements of its
    own.
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | BR | E | TT
        # Unsupported elements:
        # XREF: AR:XREF

    def append(self,
               part: str | Break | EmphasisText | TechnicalTerm):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, Break, EmphasisText, TechnicalTerm)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class LanguageVerbatim(MixedContentForVerbatim):
    """
    Complex type AR:L-VERBATIM
    Tag variants: 'L-5'
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultiLanguageVerbatim(Paginateable):
    """
    Complex type AR:MULTI-LANGUAGE-VERBATIM
    Tag variants: 'VERBATIM'
    """

    def __init__(self,
                 element: None | tuple[ar_enum.Language,
                                       str] | LanguageVerbatim = None,
                 allow_break: None | str = None,
                 float: None | ar_enum.Float = None,  # pylint: disable=redefined-builtin
                 page_wide: None | ar_enum.PageWide = None,
                 help_entry: None | str = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.allow_break = allow_break  # Attribute 'ALLOW-BREAK'
        self.float = float  # Attribte 'FLOAT'
        self.page_wide = page_wide  # Attribute 'PGWIDE'
        self.help_entry = help_entry  # Attribute 'HELP-ENTRY'
        self.elements: list[LanguageVerbatim] = []
        if element is not None:
            if isinstance(element, LanguageVerbatim):
                self.append(element)
            elif isinstance(element, tuple):
                self.append(LanguageVerbatim(element[0], element[1]))
            else:
                raise TypeError('Invalid type for element. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageVerbatim,'
                                f' got "{str(type(element))}"')

    def append(self, paragraph: LanguageVerbatim) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(paragraph, LanguageVerbatim)
        self.elements.append(paragraph)


class MixedContentForUnitNames(ARObject):
    """
    Group MIXED-CONTENT-FOR-UNIT-NAMES
    """

    def __init__(self) -> None:
        self.parts = []  # Unbounded list of str | SUB | SUP

    def append(self,
               part: str | Break | EmphasisText | TechnicalTerm):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, Subscript, Superscript)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class SingleLanguageUnitNames(MixedContentForUnitNames):
    """
    Complex type AR:SINGLE-LANGUAGE-UNIT-NAMES
    Tag variants: 'PRM-UNIT' | 'UNIT-DISPLAY-NAME' | 'DISPLAY-NAME'
    """

    def __init__(self, parts: str | list | None = None) -> None:
        super().__init__()
        if parts is not None:
            if isinstance(parts, Iterable):
                for part in parts:
                    self.append(part)
            else:
                self.append(parts)

    def __str__(self) -> str:
        """
        Convert to string if the unit name has simple
        type (at most one part of type str).
        """
        result = []
        for part in self.parts:
            if isinstance(part, str):
                result.append(part)
            elif isinstance(part, Superscript):
                result.append(str(part))
            else:
                raise ValueError("Unable to convert to string from multiple parts")
        return "".join(result)


class DocumentationBlock(ARObject):
    """
    Complex type AR:DOCUMENTATION-BLOCK
    Tag Variants: 'INTRODUCTION', 'DEF', 'VALUE', 'ANNOTATION-TEXT', 'REMARK'
                  'COND', 'DESCRICPTION', 'RATIONALE', 'DEPENDENCIES', 'USE-CASE',
                  'CONFLICTS', 'SUPPORTING-MATERIAL', 'SW-GENERIC-AXIS-DESC'
    """

    def __init__(self,
                 element: MultiLanguageParagraph | MultiLanguageVerbatim | list[Any] | None = None) -> None:
        self.elements: list[MultiLanguageParagraph | MultiLanguageVerbatim] = []
        if element is not None:
            if isinstance(element, Iterable):
                for elem in element:
                    self.append(elem)
            else:
                self.append(element)

    def append(self, element: MultiLanguageParagraph | MultiLanguageVerbatim) -> None:
        """
        Appends new element with type check
        """
        assert isinstance(element,
                          (MultiLanguageParagraph,
                           MultiLanguageVerbatim))
        self.elements.append(element)


class GeneralAnnotation(ARObject):
    """
    Group AR:GENERAL-ANNOTATION
    """

    def __init__(self,
                 label: MultilanguageLongName | None = None,
                 origin: str | None = None,
                 text: DocumentationBlock | None = None) -> None:
        super().__init__()
        self.label = label  # .LABEL
        self.origin = origin  # .ANNOTATION-ORIGIN
        self.text = text  # .ANNOTATION-TEXT


class Annotation(GeneralAnnotation):
    """
    Complex type AR:ANNOTATION
    Tag variants: 'ANNOTATION'
    """

    def __init__(self,  # pylint: disable=useless-parent-delegation
                 label: MultilanguageLongName | None = None,
                 origin: str | None = None,
                 text: DocumentationBlock | None = None) -> None:
        super().__init__(label, origin, text)


class Describable(ARObject):
    """
    Group AR:DESCRIBABLE
    """

    def __init__(self,
                 desc: Union["MultiLanguageOverviewParagraph", tuple[ar_enum.Language, str], str, None] = None,
                 category: str | None = None,
                 introduction: DocumentationBlock | None = None,
                 admin_data: AdminData | None = None
                 ) -> None:
        super().__init__()
        self.desc: MultiLanguageOverviewParagraph | None = None  # .DESC
        self.category: str | None = None  # .CATEGORY
        self.introduction: DocumentationBlock | None = None  # .INTRODUCTION
        self.admin_data: AdminData | None = None  # .ADMIN-DATA
        if desc is not None:
            if isinstance(desc, MultiLanguageOverviewParagraph):
                self.desc = desc
            elif isinstance(desc, str):
                self.desc = MultiLanguageOverviewParagraph.make(ar_enum.Language.FOR_ALL, desc)
            elif isinstance(desc, tuple) and len(desc) == 2:
                self.desc = MultiLanguageOverviewParagraph.make(*desc)
            else:
                raise TypeError(f"Invalid type for argument 'desc': {str(type(desc))}")
        self._assign_optional('category', category, str)
        self._assign_optional_strict('introduction', introduction, DocumentationBlock)
        self._assign_optional_strict('admin_data', admin_data, AdminData)


# --- Computation method elements


class CompuRational(ARObject):
    """
    Complex type AR:COMPU-RATIONAL-COEFFS
    Tag variants: 'COMPU-RATIONAL-COEFFS'
    """

    def __init__(self,
                 numerator: tuple[int | float] | list[int | float] | None,
                 denominator: tuple[int | float] | list[int | float] | None = None) -> None:
        if numerator is not None:
            if not isinstance(numerator, (tuple, list)):
                raise TypeError("Parameter for 'numerator' must be either a list or a tuple")
            self.numerator = tuple(numerator)
        else:
            self.numerator = None
        if denominator is not None:
            if not isinstance(denominator, (tuple, list)):
                raise TypeError("Parameter for 'denominator' must be either a list or a tuple")
            self.denominator = tuple(denominator)
        else:
            self.denominator = None


class CompuConst(ARObject):
    """
    Complex type AR:COMPU-CONST
    Tag variant: 'COMPU-DEFAULT-VALUE' | 'COMPU-INVERSE-VALUE' | 'COMPU-CONST'

    Handles AR:COMPU-CONST-NUMERIC-CONTENT and AR:COMPU-CONST-TEXT-CONTENT
    dynamically.
    """

    def __init__(self, value: int | float | str):
        self.value = value


class CompuScale(ARObject):
    """
    Complex type AR:COMPU-SCALE
    Tag variants: 'COMPU-SCALE'
    """

    def __init__(self,
                 content: CompuConst | CompuRational | None = None,
                 lower_limit: int | float | str | None = None,
                 upper_limit: int | float | str | None = None,
                 label: str | None = None,
                 symbol: str | None = None,
                 desc: MultiLanguageOverviewParagraph | None = None,
                 mask: int | None = None,
                 inverse_value: CompuConst | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        self.content = content                      # CHOICE(COMPU-SCALE-CONSTANT-CONTENTS, COMPU-SCALE-RATIONAL-FORMULA) # noqa E501 pylint: disable=C0301
        self.lower_limit = lower_limit              # .LOWER-LIMIT
        self.upper_limit = upper_limit              # .UPPER-LIMIT
        self.label = label                          # .SHORT-LABEL
        self.symbol = symbol                        # .SYMBOL
        self.desc = desc                            # .DESC
        self.mask = mask                            # .MASK
        self.inverse_value: CompuConst | None = None  # .COMPU-INVERSE-VALUE
        if inverse_value is not None:
            if isinstance(inverse_value, CompuConst):
                self.inverse_value = inverse_value
            elif isinstance(inverse_value, (int, float, str)):
                self.inverse_value = CompuConst(inverse_value)
            else:
                raise TypeError(f"Invalid type for 'inverse_value': {str(type(inverse_value))}")
        self.lower_limit_type = lower_limit_type    # .LOWER-LIMIT@INTERVAL-TYPE
        self.upper_limit_type = upper_limit_type    # .UPPER-LIMIT@INTERVAL-TYPE
        # .VARIATION-POINT not supported

    @property
    def content_type(self) -> ar_enum.CompuScaleContent:
        """
        What kind of content does this CompuScale have?
        """
        if isinstance(self.content, CompuConst):
            return ar_enum.CompuScaleContent.CONSTANT
        elif isinstance(self.content, CompuRational):
            return ar_enum.CompuScaleContent.RATIONAL
        else:
            return ar_enum.CompuScaleContent.NONE


class Computation(ARObject):
    """
    Complex Type: AR:COMPU
    Tag variants: 'COMPU-INTERNAL-TO-PHYS' | 'COMPU-PHYS-TO-INTERNAL'
    """

    def __init__(self,
                 compu_scales: list[CompuScale] | None = None,
                 default_value: CompuConst | int | float | str | None = None) -> None:

        self.compu_scales = compu_scales
        self.default_value: CompuConst | int | float | str | None = None  # .COMPU-DEFAULT-VALUE
        if isinstance(default_value, CompuConst):
            self.default_value = default_value
        elif isinstance(default_value, (int, float, str)):
            self.default_value = CompuConst(default_value)

    @classmethod
    def make_value_table(cls: "Computation",
                         elements: list[Any],
                         default_value: CompuConst | int | float | str | None = None,
                         auto_label: bool = True):
        """
        #convenience-method

        Creates new CompuConst-based computation using values from a list.

        When elements is a list of strings:
            Creates one CompuScale per list item and automatically calculates lower and upper limits.
            Enumeration starts counting from zero and increments by one until the end of the list.

        When elements is a list of tuples:
            If 2-tuple: First element is both lower_limit and upper_limit, second element is text value.
            If 3-tuple: First element is lower_limit, second element is upper_limit, third element is text value.

        auto_label: automatically creates a <SHORT-LABEL> based on the text value.

        """
        compu_scales = []
        for i, elem in enumerate(elements):
            label = None
            if isinstance(elem, str):
                lower_limit, upper_limit, value = i, i, elem
            elif isinstance(elem, tuple):
                if len(elem) == 2:
                    lower_limit, upper_limit, value = (elem[0], elem[0], elem[1])
                elif len(elem) == 3:
                    lower_limit, upper_limit, value = elem
                else:
                    raise ValueError(f"Invalid length of tuple: {len(elem)}")
            else:
                raise TypeError(f"Invalid type of element: {str(type(elem))}")
            if auto_label and isinstance(value, str):
                label = value
            compu_scales.append(CompuScale(CompuConst(value), lower_limit, upper_limit, label))
        return cls(compu_scales, default_value)

    @classmethod
    def make_rational(cls: "Computation",
                      scaling_factor: int | float = 1,
                      offset: int | float = 0,
                      lower_limit: int | float | str | None = None,
                      upper_limit: int | float | str | None = None,
                      default_value: CompuConst | int | float | str | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        """
        #convenience-method

        Creates a new Computation instance with one COMPU-SCALE containing numerator
        and denominator.

        """
        numerator = [offset, float(scaling_factor)]
        denominator = [1]
        compu_scales = [CompuScale(CompuRational(numerator, denominator),
                                   lower_limit,
                                   upper_limit,
                                   lower_limit_type=lower_limit_type,
                                   upper_limit_type=upper_limit_type)]
        return cls(compu_scales, default_value)


class CompuMethod(ARElement):
    """
    Complex Type: AR:COMPU-METHOD
    Tag Variants: 'COMPU-METHOD'
    """

    def __init__(self, name: str,
                 int_to_phys: Computation | None = None,
                 phys_to_int: Computation | None = None,
                 unit_ref: UnitRef | None = None,
                 display_format: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.int_to_phys = int_to_phys        # .COMPU-INTERNAL-TO-PHYS
        self.phys_to_int = phys_to_int        # .COMPU-PHYS-TO-INTERNAL
        self.unit_ref = unit_ref              # .UNIT-REF
        self.display_format = display_format  # .DISPLAY-FORMAT

    def ref(self) -> CompuMethodRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else CompuMethodRef(ref_str)


# Constraint elements


class LimitObject(ARObject):
    """
    Base class for elements that has upper and lower limits
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:

        self.lower_limit = lower_limit              # .LOWER-LIMIT
        self.upper_limit = upper_limit              # .UPPER-LIMIT
        self.lower_limit_type = lower_limit_type    # .LOWER-LIMIT@INTERVAL-TYPE
        self.upper_limit_type = upper_limit_type    # .UPPER-LIMIT@INTERVAL-TYPE

    @property
    def is_empty(self) -> bool:
        """Overrides is_empty from base class"""
        return self.is_empty_with_ignore({"lower_limit_type", "upper_limit_type"})

    def check_value(self, value: int | float) -> bool:
        """
        Checks if given value is inside the constraint limits
        """
        if self.lower_limit_type == ar_enum.IntervalType.CLOSED:
            if value < self.lower_limit:
                return False
        elif value <= self.lower_limit:
            return False
        if self.upper_limit_type == ar_enum.IntervalType.CLOSED:
            if value > self.upper_limit:
                return False
        elif value >= self.upper_limit:
            return False
        return True


class ScaleConstraint(LimitObject):
    """
    AR:SCALE-CONSTR
    Tag variants: 'SCALE-CONSTR'
    """

    def __init__(self,
                 label: str | None = None,
                 desc: MultiLanguageOverviewParagraph | None = None,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 validity: ar_enum.ScaleConstraintValidity | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit, upper_limit, lower_limit_type, upper_limit_type)
        self.label = label
        self.desc = desc
        self.validity = validity


class ConstraintBase(LimitObject):
    """
    Base class for data constraint rules
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 scale_constrs: list[ScaleConstraint] | None = None,
                 max_gradient: int | float | None = None,
                 max_diff: int | float | None = None,
                 monotony: ar_enum.Monotony | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit, upper_limit, lower_limit_type, upper_limit_type)
        self.scale_constrs = list(scale_constrs) if scale_constrs else []
        self.max_gradient = max_gradient
        self.max_diff = max_diff
        self.monotony = monotony


class InternalConstraint(ConstraintBase):
    """
    AR:INTERNAL-CONSTRS
    Tag variants: 'INTERNAL-CONSTRS'
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 scale_constr: list[ScaleConstraint] | None = None,
                 max_gradient: int | float | None = None,
                 max_diff: int | float | None = None,
                 monotony: ar_enum.Monotony | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit,
                         upper_limit,
                         scale_constr,
                         max_gradient,
                         max_diff,
                         monotony,
                         lower_limit_type,
                         upper_limit_type)


class PhysicalConstraint(ConstraintBase):
    """
    AR:PHYS-CONSTRS
    Tag variants: 'PHYS-CONSTRS'
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 scale_constr: list[ScaleConstraint] | None = None,
                 max_gradient: int | float | None = None,
                 max_diff: int | float | None = None,
                 monotony: ar_enum.Monotony | None = None,
                 unit_ref: UnitRef | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit,
                         upper_limit,
                         scale_constr,
                         max_gradient,
                         max_diff,
                         monotony,
                         lower_limit_type,
                         upper_limit_type)
        self.unit_ref = unit_ref


class DataConstraintRule(ARObject):
    """
    AR:DATA-CONSTR-RULE
    Tag variants: 'DATA-CONSTR-RULE'
    """

    def __init__(self,
                 internal: InternalConstraint | None = None,
                 physical: PhysicalConstraint | None = None,
                 level: int | None = None) -> None:
        self.internal = internal   # .INTERNAL-CONSTRS
        self.physical = physical   # .PHYS-CONSTRS
        self.level = level         # .CONSTR-LEVEL


class DataConstraint(ARElement):
    """
    AR:DATA-CONSTR
    Tag variants: 'DATA-CONSTR'
    """

    def __init__(self, name: str,
                 rules: list[DataConstraintRule] | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.rules = []
        if rules is not None:
            for rule in rules:
                assert isinstance(rule, DataConstraintRule)
            self.rules.extend(rules)

    def ref(self) -> DataConstraintRef:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else DataConstraintRef(ref_str)

    @classmethod
    def make_physical(cls: "DataConstraint",
                      name: str,
                      lower_limit: int | float | None = None,
                      upper_limit: int | float | None = None,
                      scale_constr: list[ScaleConstraint] | None = None,
                      max_gradient: int | float | None = None,
                      max_diff: int | float | None = None,
                      monotony: ar_enum.Monotony | None = None,
                      unit_ref: UnitRef | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      **kwargs) -> "DataConstraint":
        """
        #convenience-method

        Creates a DataConstraint which contains a single physical constraint.
        """
        rule = DataConstraintRule(physical=PhysicalConstraint(lower_limit,
                                                              upper_limit,
                                                              scale_constr,
                                                              max_gradient,
                                                              max_diff,
                                                              monotony,
                                                              unit_ref,
                                                              lower_limit_type,
                                                              upper_limit_type))
        return cls(name, [rule], **kwargs)

    @classmethod
    def make_internal(cls: "DataConstraint",
                      name: str,
                      lower_limit: int | float | None = None,
                      upper_limit: int | float | None = None,
                      scale_constr: list[ScaleConstraint] | None = None,
                      max_gradient: int | float | None = None,
                      max_diff: int | float | None = None,
                      monotony: ar_enum.Monotony | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      **kwargs) -> "DataConstraint":
        """
        #convenience-method

        Creates a DataConstraint that contains a single internal constraint.
        """
        rule = DataConstraintRule(internal=InternalConstraint(lower_limit,
                                                              upper_limit,
                                                              scale_constr,
                                                              max_gradient,
                                                              max_diff,
                                                              monotony,
                                                              lower_limit_type,
                                                              upper_limit_type))
        return cls(name, [rule], **kwargs)

# Unit elements


class Unit(ARElement):
    """
    Complex type AR:UNIT
    Tag variants: 'UNIT'
    """

    def __init__(self, name: str,
                 display_name: str | SingleLanguageUnitNames | None = None,
                 factor: float | None = None,
                 offset: float | None = None,
                 physical_dimension_ref: str | PhysicalDimensionRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.display_name: SingleLanguageUnitNames | None = None  # .DISPLAY-NAME
        self.physical_dimension_ref: PhysicalDimensionRef | None = None  # .PHYSICAL-DIMENSION-REF
        self.factor: float | None = None  # .FACTOR-SI-TO-UNIT
        self.offset: float | None = None  # .OFFSET-SI-TO-UNIT
        if display_name is not None:
            if isinstance(display_name, str):
                self.display_name = SingleLanguageUnitNames(display_name)
            elif isinstance(display_name, SingleLanguageUnitNames):
                self.display_name = display_name
            else:
                raise TypeError(f"display_name: Invalid type '{str(type(display_name))}'")
        if physical_dimension_ref is not None:
            if isinstance(physical_dimension_ref, str):
                self.physical_dimension_ref = PhysicalDimensionRef(display_name)
            elif isinstance(physical_dimension_ref, PhysicalDimensionRef):
                self.physical_dimension_ref = physical_dimension_ref
            else:
                raise TypeError(f"physical_dimension_ref: Invalid type '{str(type(physical_dimension_ref))}'")
        self._assign_optional('factor', factor, float)
        self._assign_optional('offset', offset, float)

    def ref(self) -> UnitRef:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else UnitRef(ref_str)


# --- DataDictionary and DataType elements


class BaseType(ARElement):
    """
    Merge of Complex types AR:BASE-TYPE, AR:BASE-TYPE-DEFINITION,
    AR:BASE-TYPE-DIRECT-DEFINITION
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.size: int | None = None  # .BASE-TYPE-SIZE
        self.max_size: int | None = None  # .MAX-BASE-TYPE-SIZE
        self.encoding: str | None = None  # .BASE-TYPE-ENCODING
        self.alignment: int | None = None  # .MEM-ALIGNMENT
        self.byte_order: ar_enum.ByteOrder | None = None  # .BYTE-ORDER
        self.native_declaration: str | None = None  # .NATIVE-DECLARATION


class SwBaseType(BaseType):
    """
    Complex type AR:SW-BASE-TYPE
    Tag variants: SW-BASE-TYPE
    """

    def __init__(self,
                 name: str,
                 size: int | None = None,
                 max_size: int | None = None,
                 encoding: str | None = None,
                 alignment: int | None = None,
                 byte_order: ar_enum.ByteOrder | None = None,
                 native_declaration: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.size = size
        self.max_size = max_size
        self.encoding = encoding
        self.alignment = alignment
        self.byte_order = byte_order
        self.native_declaration = native_declaration

    def ref(self) -> SwBaseTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwBaseTypeRef(ref_str)


class SwBitRepresentation(ARObject):
    """
    Complex Type AR:SW-BIT-REPRESENTATION
    Tag variants: SW-BIT-REPRESENTATION
    """

    def __init__(self,
                 position: int | None = None,
                 num_bits: int | None = None) -> None:
        super().__init__()
        self.position: int | None = None
        self.num_bits: int | None = None
        self._assign_optional('position', position, int)
        self._assign_optional('num_bits', num_bits, int)


class SwTextProps(ARObject):
    """
    Complex type AR:SW-TEXT-PROPS
    Tag Variants: 'SW-TEXT-PROPS'
    """

    def __init__(self,
                 array_size_semantics: ar_enum.ArraySizeSemantics | None = None,
                 max_text_size: int | None = None,
                 base_type_ref: SwBaseTypeRef | str | None = None,
                 fill_char: int | None = None,
                 ):
        self.array_size_semantics: ar_enum.ArraySizeSemantics | None = None   # .ARRAY-SIZE-SEMANTICS
        self.max_text_size: int | None = None                                 # .SW-MAX-TEXT-SIZE
        self.base_type_ref: SwBaseTypeRef | str | None = None                 # .BASE-TYPE-REF
        self.fill_char: int | None = None                                     # .FILL-CHAR
        self._assign_optional('array_size_semantics', array_size_semantics, ar_enum.ArraySizeSemantics)
        self._assign_optional('max_text_size', max_text_size, int)
        self._assign_optional('base_type_ref', base_type_ref, SwBaseTypeRef)
        self._assign_optional('fill_char', fill_char, int)


class SwPointerTargetProps(ARObject):
    """
    Complex type AR:SW-POINTER-TARGET-PROPS
    Tag Variants: 'SW-POINTER-TARGET-PROPS'
    """

    def __init__(self,
                 target_category: str | None = None,
                 sw_data_def_props: Union["SwDataDefProps", "SwDataDefPropsConditional", None] = None,
                 function_ptr_signature_ref: FunctionPtrSignatureRef | None = None
                 ) -> None:
        self.target_category: str | None = None  # .TARGET-CATEGORY
        self.sw_data_def_props: Union["SwDataDefProps", None] = None  # .SW-DATA-DEF-PROPS
        self.function_ptr_signature_ref: FunctionPtrSignatureRef | None = None  # .FUNCTION-POINTER-SIGNATURE-REF
        self._assign_optional("target_category", target_category, str)
        self._assign_optional("function_ptr_signature_ref", function_ptr_signature_ref, FunctionPtrSignatureRef)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class SwDataDefPropsConditional(ARObject):
    """
    Merge of Complex types AR:SW-DATA-DEF-PROPS-CONDITIONAL and
    AR:SW-DATA-DEF-PROPS-CONTENT
    Tag Variants: SW-DATA-DEF-PROPS-CONDITIONAL
    """

    def __init__(self,  # pylint: disable=R0917
                 display_presentation: ar_enum.DisplayPresentation | None = None,
                 step_size: float | None = None,
                 annotations: Annotation | list[Annotation] | None = None,
                 sw_addr_method_ref: str | SwAddrMethodRef | None = None,
                 base_type_ref: SwBaseTypeRef | None = None,
                 compu_method_ref: str | CompuMethodRef | None = None,
                 data_constraint_ref: str | DataConstraintRef | None = None,
                 impl_data_type_ref: str | ImplementationDataTypeRef | None = None,
                 unit_ref: str | UnitRef | None = None,
                 alignment: int | float | None = None,
                 bit_representation: SwBitRepresentation | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 text_props: SwTextProps | None = None,
                 display_format: str | None = None,
                 impl_policy: ar_enum.SwImplPolicy | None = None,
                 additional_native_type_qualifier: str | None = None,
                 intended_resolution: int | float | None = None,
                 interpolation_method: str | None = None,
                 is_virtual: bool | None = None,
                 ptr_target_props: SwPointerTargetProps | None = None
                 ) -> None:
        # .DISPLAY-PRESENTATION
        self.display_presentation: ar_enum.DisplayPresentation | None = None
        self.step_size: float | None = None  # .STEP-SIZE : AR:FLOAT
        # .SW-VALUE-BLOCK-SIZE-MULTS not supported.
        self.annotations: list[Annotation] = []  # .ANNOTATIONS
        self.sw_addr_method_ref: SwAddrMethodRef | None = None  # .SW-ADDR-METHOD-REF
        self.alignment: int | str | None = None  # .SW-ALIGNMENT
        self.base_type_ref: SwBaseTypeRef | None = None  # .BASE-TYPE-REF
        self.bit_representation: SwBitRepresentation | None = None  # .SW-BIT-REPRESENTATION
        self.calibration_access: ar_enum.SwCalibrationAccess | None = None  # .SW-CALIBRATION-ACCESS
        # .SW-VALUE-BLOCK-SIZE not supported.
        # .SW-CALPRM-AXIS-SET not yet supported. Low on priority list.
        self.text_props: SwTextProps | None = None  # .SW-TEXT-PROPS
        # .SW-COMPARISON-VARIABLES not yet supported. Low on priority list.
        self.compu_method_ref: CompuMethodRef | None = None
        self.data_constraint_ref: DataConstraintRef | None = None
        # .SW-DATA-DEPENDENCY not yet supported. Low on priority list.
        self.display_format: str | None = None  # .DISPLAY-FORMAT
        self.impl_data_type_ref: ImplementationDataTypeRef | None = None  # .IMPLEMENTATION-DATA-TYPE-REF
        # .SW-HOST-VARIABLE not yet supported. Low on priority list.
        self.impl_policy: ar_enum.SwImplPolicy | None = None  # .SW-IMPL-POLICY
        self.additional_native_type_qualifier: str | None = None  # .ADDITIONAL-NATIVE-TYPE-QUALIFIER
        self.intended_resolution: int | float | None = None  # .SW-INTENDED-RESOLUTION
        self.interpolation_method: str | None = None  # .SW-INTERPOLATION-METHOD
        # .INVALID-VALUE not yet supported.
        # .MC-FUNCTION not yet supported. Low on priority list.
        self.is_virtual: bool | None = None  # .IS-VIRTUAL
        self.ptr_target_props: SwPointerTargetProps | None = None  # .SW-POINTER-TARGET-PROPS
        # .SW-RECORD-LAYOUT-REF not yet supported. Low on priority list.
        # .SW-REFRESH-TIMING not yet supported. Low on priority list.
        self.unit_ref = None  # .UNIT-REF
        # .VALUE-AXIS-DATA-TYPE-REF not yet supported. Low on priority list.

        self._assign_optional('display_presentation', display_presentation, ar_enum.DisplayPresentation)
        self._assign_optional('step_size', step_size, float)
        if annotations is not None:
            if isinstance(annotations, Annotation):
                self.annotations.append(annotations)
            elif isinstance(annotations, Iterable):
                for annotation in annotations:
                    if not isinstance(annotation, Annotation):
                        raise TypeError(
                            f"Param annotations: Expected type 'Annotation', got '{str(type(annotation))}'")
                    self.annotations.append(annotation)
            else:
                raise TypeError(
                    "Param annotations: "
                    f"Expected type 'Annotation' or list[Annotation], got '{str(type(annotations))}'")
        self._assign_optional('sw_addr_method_ref', sw_addr_method_ref, SwAddrMethodRef)
        self._assign_int_or_str_pattern_optional('alignment', alignment, alignment_type_re)
        self._assign_optional('base_type_ref', base_type_ref, SwBaseTypeRef)
        if bit_representation is not None:
            if not isinstance(bit_representation, SwBitRepresentation):
                raise TypeError(f"bit_representation: Invalid type '{str(type(bit_representation))}'."
                                " Expected 'SwBitRepresentation'")
            self.bit_representation = bit_representation
        self._assign_optional('calibration_access', calibration_access, ar_enum.SwCalibrationAccess)
        if text_props is not None:
            if not isinstance(text_props, SwTextProps):
                raise TypeError(f"text_props: Invalid type '{str(type(text_props))}'."
                                " Expected 'SwTextProps'")
            self.text_props = text_props
        self._assign_optional('compu_method_ref', compu_method_ref, CompuMethodRef)
        self._assign_optional('data_constraint_ref', data_constraint_ref, DataConstraintRef)
        self._assign_optional('impl_data_type_ref', impl_data_type_ref, ImplementationDataTypeRef)
        self._assign_optional('unit_ref', unit_ref, UnitRef)
        self._assign_int_or_str_pattern_optional('display_format', display_format, display_format_str_re)
        self._assign_optional('impl_policy', impl_policy, ar_enum.SwImplPolicy)
        self._assign_optional('additional_native_type_qualifier',
                              additional_native_type_qualifier, str)
        if intended_resolution is not None:
            if isinstance(intended_resolution, (int, float)):
                self.intended_resolution = intended_resolution
            else:
                raise TypeError(f"Invalid type '{str(type(intended_resolution))}' for paramater 'intended_resolution'")
        self._assign_optional('interpolation_method', interpolation_method, str)
        self._assign_optional('is_virtual', is_virtual, bool)
        if ptr_target_props is not None:
            self._set_attr_with_strict_type('ptr_target_props', ptr_target_props, SwPointerTargetProps)

    @property
    def is_queued(self) -> bool:
        """
        Returns True if impl_policy is set to QUEUED
        """
        if self.impl_policy is not None and self.impl_policy == ar_enum.SwImplPolicy.QUEUED:
            return True
        return False


class SwDataDefProps(ARObject):
    """
    Complex type AR:SW-DATA-DEF-PROPS
    Tag variants: 'SW-DATA-DEF-PROPS' | 'NETWORK-REPRESENTATION' |
                  'NETWORK-REPRESENTATION-PROPS' | 'PHYSICAL-PROPS'
    """

    def __init__(self, variants: SwDataDefPropsConditional | list[SwDataDefPropsConditional] | None = None) -> None:
        super().__init__()
        self.variants: list[SwDataDefPropsConditional] = []  # .SW-DATA-DEF-PROPS-VARIANTS
        if variants is not None:
            if isinstance(variants, list):
                for variant in variants:
                    self.append(variant)
            elif isinstance(variants, SwDataDefPropsConditional):
                self.append(variants)
            else:
                raise TypeError("variant must be one of (SwDataDefPropsConditional, list[SwDataDefPropsConditional])")

    def __getitem__(self, index: int) -> SwDataDefPropsConditional:
        """
        Accessor of variants list
        """
        return self.variants[index]

    def __len__(self) -> int:
        """
        Length of variants list
        """
        return len(self.variants)

    def __iter__(self):
        """
        Iterator of variants list
        """
        return iter(self.variants)

    def append(self, variant: SwDataDefPropsConditional):
        """
        Appends SW-DATA-DEF-PROPS-CONDITIONAL to variants list
        """
        if isinstance(variant, SwDataDefPropsConditional):
            self.variants.append(variant)
        else:
            raise TypeError("variant must be of type SwDataDefPropsConditional")


class AutosarDataType(ARElement):
    """
    Group AR:AUTOSAR-DATA-TYPE
    """

    def __init__(self,
                 name: str,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.sw_data_def_props: SwDataDefProps | None = None
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class ImplementationProps(Referrable):
    """
    Group AR:IMPLEMENTATION-PROPS
    """

    def __init__(self,
                 name: str,
                 symbol: str | None = None) -> None:
        super().__init__(name)
        self.symbol: str | None = None
        self._assign_optional('symbol', symbol, str)


class SymbolProps(ImplementationProps):
    """
    Complex type AR:SYMBOL-PROPS
    Tag Variants: 'SYMBOL-PROPS', 'EVENT-SYMBOL-PROPS'

    Base class already supports everything we need
    """


class ImplementationDataTypeElement(Identifiable):
    """
    Complex type AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
    Tag variants: 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
    """

    def __init__(self,
                 name: str,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 array_size: int | None = None,
                 array_impl_policy: ar_enum.ArrayImplPolicy | None = None,
                 array_size_handling: ar_enum.ArraySizeHandling | None = None,
                 array_size_semantics: ar_enum.ArraySizeSemantics | None = None,
                 sub_elements: list["ImplementationDataTypeElement"] | None = None,
                 is_optional: bool | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.array_size: int | None = None                                      # .ARRAY-SIZE
        self.array_impl_policy: ar_enum.ArrayImplPolicy | None = None           # .ARRAY-IMPL-POLICY
        self.array_size_handling: ar_enum.ArraySizeHandling | None = None       # .ARRAY-SIZE-HANDLING
        self.array_size_semantics: ar_enum.ArraySizeSemantics | None = None     # .ARRAY-SIZE-SEMANTICS
        self.is_optional: bool | None = None                                    # .IS-OPTIONAL
        self.sub_elements: list["ImplementationDataTypeElement"] | None = []    # .SUB-ELEMENTS
        self.sw_data_def_props: SwDataDefProps | None = None                    # .SW-DATA-DEF-PROPS
        self._assign_optional_positive_int("array_size", array_size)
        self._assign_optional("array_impl_policy", array_impl_policy, ar_enum.ArrayImplPolicy)
        self._assign_optional("array_size_handling", array_size_handling, ar_enum.ArraySizeHandling)
        self._assign_optional("array_size_semantics", array_size_semantics, ar_enum.ArraySizeSemantics)
        self._assign_optional("is_optional", is_optional, bool)
        if sub_elements is not None:
            for elem in sub_elements:
                self.append(elem)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")

    def append(self, elem: "ImplementationDataTypeElement") -> None:
        """
        Appends elem to sub_element list
        """
        if isinstance(elem, ImplementationDataTypeElement):
            self.sub_elements.append(elem)
        else:
            raise TypeError("'elem' must be of type ImplementationDataTypeElement")

    def ref(self) -> AbstractImplementationDataTypeElementRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return AbstractImplementationDataTypeElementRef(ref_str,
                                                        ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE_ELEMENT)


class ImplementationDataType(AutosarDataType):
    """
    Complex type AR:IMPLEMENTATION-DATA-TYPE
    Tag Variants: 'IMPLEMENTATION-DATA-TYPE'

    Skip parent class AbstractImplementationDataType since it doesn't have any properties
    of its own.
    """

    def __init__(self,
                 name: str,
                 dynamic_array_size_profile: str | None = None,
                 is_struct_with_optional_element: bool | None = None,
                 sub_elements: list[ImplementationDataTypeElement] | None = None,
                 symbol_props: SymbolProps | None = None,
                 type_emitter: str | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.dynamic_array_size_profile: str | None = None                  # .DYNAMIC-ARRAY-SIZE-PROFILE
        self.is_struct_with_optional_element: bool | None = None            # .IS-STRUCT-WITH-OPTIONAL-ELEMENT
        self.sub_elements: list[ImplementationDataTypeElement] = []         # .SUB-ELEMENTS
        self.symbol_props: SymbolProps | None = None                        # .SYMBOL-PROPS
        self.type_emitter: str | None = None                                # .TYPE-EMITTER
        self._assign_optional('dynamic_array_size_profile', dynamic_array_size_profile, str)
        self._assign_optional('is_struct_with_optional_element', is_struct_with_optional_element, bool)
        self._assign_optional('type_emitter', type_emitter, str)
        if sub_elements is not None:
            for elem in sub_elements:
                self.append(elem)
        if symbol_props is not None:
            if isinstance(symbol_props, SymbolProps):
                self.symbol_props = symbol_props
            else:
                raise TypeError("'symbol_props' must be of type SymbolProps")

    def append(self, elem: ImplementationDataTypeElement) -> None:
        """
        Appends elem to sub_element list
        """
        if isinstance(elem, ImplementationDataTypeElement):
            self.sub_elements.append(elem)
        else:
            raise TypeError("'elem' must be of type ImplementationDataTypeElement")

    def ref(self) -> ImplementationDataTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ImplementationDataTypeRef(ref_str)

    def find(self, ref: str) -> Any:
        """
        Finds item by reference
        """
        assert "/" not in ref
        return self._find_by_name(self.sub_elements, ref)


class DataPrototype(Identifiable):
    """
    Group AR:DATA-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.sw_data_def_props: SwDataDefProps | None = None  # .SW-DATA-DEF-PROPS
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class AutosarDataPrototype(DataPrototype):
    """
    Group AR:AUTOSAR-DATA-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 type_ref: AutosarDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: AutosarDataTypeRef | None = None  # .TYPE-TREF
        if type_ref is not None:
            self._assign_optional("type_ref", type_ref, AutosarDataTypeRef)


class VariableDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:VARIABLE-DATA-PROTOTYPE
    Tag variants: 'VARIABLE-DATA-PROTOTYPE' | 'BULK-NV-BLOCK' | 'RAM-BLOCK'
    """

    def __init__(self,
                 name: str,
                 init_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        # .VARIATION-POINT not supported
        self._assign_optional_strict("init_value", init_value, ValueSpecification)

    def ref(self) -> VariableDataPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else VariableDataPrototypeRef(ref_str)

    @property
    def is_queued(self) -> bool:
        """
        Returns True if internal sw_data_def_props has its impl_policy is set to QUEUED
        """
        if self.sw_data_def_props is not None and len(self.sw_data_def_props.variants) > 0:
            return self.sw_data_def_props.variants[0].is_queued
        return False


class ParameterDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:PARAMETER-DATA-PROTOTYPE
    Tag variants: 'PARAMETER-DATA-PROTOTYPE' | 'ROM-BLOCK'
    """

    def __init__(self,
                 name: str,
                 init_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        # .VARIATION-POINT not supported
        self._assign_optional_strict("init_value", init_value, ValueSpecification)

    def ref(self) -> ParameterDataPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ParameterDataPrototypeRef(ref_str)


class ArgumentDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:ARGUMENT-DATA-PROTOTYPE
    Tag variants: 'ARGUMENT-DATA-PROTOTYPE'
    """

    def __init__(self,
                 name: str,
                 direction: ar_enum.ArgumentDirection | None = None,
                 server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.direction: ar_enum.ArgumentDirection | None = None  # .DIRECTION
        self.server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None  # .SERVER-ARGUMENT-IMPL-POLICY
        # .TYPE-BLUEPRINTS not supported
        # .VARIATION-POINT not supported
        self._assign_optional("direction", direction, ar_enum.ArgumentDirection)
        self._assign_optional("server_arg_impl_policy", server_arg_impl_policy, ar_enum.ServerArgImplPolicy)

    def ref(self) -> ArgumentDataPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ArgumentDataPrototypeRef(ref_str)


class ApplicationDataType(AutosarDataType):
    """
    Group AR:APPLICATION-DATA-TYPE
    """


class ApplicationCompositeDataType(ApplicationDataType):
    """
    Group AR:APPLICATION-COMPOSITE-DATA-TYPE
    """

    @property
    def is_composite(self):
        """Returns true if this is a composite data type"""
        return True


class ApplicationPrimitiveDataType(ApplicationDataType):
    """
    Complex type AR:APPLICATION-PRIMITIVE-DATA-TYPE
    Tag variants: 'APPLICATION-PRIMITIVE-DATA-TYPE'
    """

    @property
    def is_composite(self):
        """Returns true if this is a composite data type"""
        return False

    def ref(self) -> ApplicationDataTypeRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationDataTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)


class ApplicationCompositeElementDataPrototype(DataPrototype):
    """
    Group AR:APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 type_ref: ApplicationDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: ApplicationDataTypeRef | None = None  # .TYPE-TREF
        self._assign_optional_strict('type_ref', type_ref, ApplicationDataTypeRef)


class ApplicationArrayElement(ApplicationCompositeElementDataPrototype):
    """
    Complex type AR:APPLICATION-ARRAY-ELEMENT
    Tag variants: 'ELEMENT'
    """

    def __init__(self,
                 name: str,
                 max_number_of_elements: int | None = None,
                 array_size_handling: ar_enum.ArraySizeHandling | None = None,
                 array_size_semantics: ar_enum.ArraySizeSemantics | None = None,
                 index_data_type_ref: IndexDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.array_size_handling: ar_enum.ArraySizeHandling | None = None     # .ARRAY-SIZE-HANDLING
        self.array_size_semantics: ar_enum.ArraySizeSemantics | None = None   # .ARRAY-SIZE-SEMANTICS
        self.max_number_of_elements: int | None = None                        # ."MAX-NUMBER-OF-ELEMENTS
        self.index_data_type_ref: IndexDataTypeRef | None = None              # .INDEX-DATA-TYPE-REF
        self._assign_optional("array_size_handling", array_size_handling, ar_enum.ArraySizeHandling)
        self._assign_optional("array_size_semantics", array_size_semantics, ar_enum.ArraySizeSemantics)
        self._assign_optional_positive_int("max_number_of_elements", max_number_of_elements)
        self._assign_optional("index_data_type_ref", index_data_type_ref, IndexDataTypeRef)

    def ref(self) -> ApplicationArrayElementRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationArrayElementRef(ref_str)


class ApplicationArrayDataType(ApplicationCompositeDataType):
    """
    Complex type AR:APPLICATION-ARRAY-DATA-TYPE
    Tag variants: 'APPLICATION-ARRAY-DATA-TYPE'
    """

    def __init__(self,
                 name: str,
                 dynamic_array_size_profile: str | None = None,
                 element: ApplicationArrayElement | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.dynamic_array_size_profile: str | None = None                  # .DYNAMIC-ARRAY-SIZE-PROFILE
        self.element: ApplicationArrayElement | None = None                 # .ELEMENT
        self._assign_optional('dynamic_array_size_profile', dynamic_array_size_profile, str)
        self._assign_optional_strict('element', element, ApplicationArrayElement)

    def ref(self) -> ApplicationDataTypeRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationDataTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE)


class ApplicationRecordElement(ApplicationCompositeElementDataPrototype):
    """
    Complex type AR:APPLICATION-RECORD-ELEMENT
    Tag variants: 'APPLICATION-RECORD-ELEMENT'
    """

    def __init__(self,
                 name: str,
                 is_optional: bool | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.is_optional: bool | None = None  # .IS-OPTIONAL
        self._assign_optional('is_optional', is_optional, bool)

    def ref(self) -> ApplicationRecordElementRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationRecordElementRef(ref_str)


class ApplicationRecordDataType(ApplicationCompositeDataType):
    """
    Complex type AR:APPLICATION-RECORD-DATA-TYPE
    Tag variants: 'APPLICATION-RECORD-DATA-TYPE'
    """

    def __init__(self,
                 name: str,
                 elements: ApplicationRecordElement | list[ApplicationRecordElement] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.elements: list[ApplicationRecordElement] = []
        if elements is not None:
            if isinstance(elements, ApplicationRecordElement):
                self.append(elements)
            elif isinstance(elements, list):
                self.extend(elements)

    def append(self, element: ApplicationRecordElement) -> None:
        """
        Appends element to elements list
        """
        if isinstance(element, ApplicationRecordElement):
            self.elements.append(element)
        else:
            raise TypeError("'element' must be of type ApplicationRecordElement")

    def extend(self, elements: list[ApplicationRecordElement]) -> None:
        """
        Extends elements to elements list
        """
        for element in elements:  # We want to type-check each element before adding to internal list
            self.append(element)

    def ref(self) -> ApplicationDataTypeRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationDataTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE)


class DataTypeMap(ARObject):
    """
    Complex type AR:DATA-TYPE-MAP
    Tag variants: 'DATA-TYPE-MAP'
    """

    def __init__(self,
                 appl_data_type_ref: ApplicationDataTypeRef | None = None,
                 impl_data_type_ref: ImplementationDataTypeRef | None = None,
                 ) -> None:
        self.appl_data_type_ref = appl_data_type_ref   # .APPLICATION-DATA-TYPE-REF
        self.impl_data_type_ref = impl_data_type_ref   # .IMPLEMENTATION-DATA-TYPE-REF


class DataTypeMappingSet(ARElement):
    """
    Complex type AR:DATA-TYPE-MAPPING-SET
    Tag variants: 'DATA-TYPE-MAPPING-SET'
    """

    def __init__(self,
                 name: str,
                 data_type_maps: DataTypeMap | list[DataTypeMap] | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.data_type_maps: list[DataTypeMap] = []  # .DATA-TYPE-MAPS
        self.mode_request_type_maps = []  # .MODE-REQUEST-TYPE-MAPS (Not yet implemented)
        if data_type_maps is not None:
            if isinstance(data_type_maps, DataTypeMap):
                self.append(data_type_maps)
            elif isinstance(data_type_maps, list):
                for data_type_map in data_type_maps:
                    self.append(data_type_map)
            else:
                raise TypeError(f'data_type_maps: Invalid type "{str(type(data_type_maps))}"')

    def append(self, element: DataTypeMap) -> None:
        """
        Appends element to one of the inner lists based on parameter type
        Currently, appending to mode_request_type_maps isn't
        implemented.
        """
        if isinstance(element, DataTypeMap):
            self.data_type_maps.append(element)
        else:
            raise TypeError(f'Unexpected type: "{str(type(element))}"')

    def ref(self) -> DataTypeMappingSetRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return DataTypeMappingSetRef(ref_str)


class ValueList(ARObject):
    """
    Complex type AR:VALUE-LIST
    Tag variants: 'SW-ARRAYSIZE'
    """

    def __init__(self, values: list[int | float | NumericalValue] | None = None) -> None:
        self.values = []
        if values is not None:
            if isinstance(values, (int, float)):
                self.append(values)
            else:
                for value in values:
                    self.append(value)

    def append(self, value: int | float | NumericalValue) -> None:
        """
        Adds value to list of values
        """
        if isinstance(value, (int, float, NumericalValue)):
            self.values.append(value)
        else:
            raise TypeError(f"Invalid type for value: {str(type(value))}")


# --- Auxillary Objects


class SwAddrMethod(ARElement):
    """
    Complex type AR:SW-ADDR-METHOD
    Tag Variants: 'SW-ADDR-METHOD'
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.memory_allocation_keyword_policy = None  # .MEMORY-ALLOCATION-KEYWORD-POLICY
        self.options = []  # .OPTIONS
        self.section_initialization_policy = None  # .SECTION-INITIALIZATION-POLICY
        self.section_type = None  # .SECTION-TYPE

    def ref(self) -> SwAddrMethodRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwAddrMethodRef(ref_str)

# --- Calibration data elements


SwValueElement = Union[int, float, str, NumericalValue, "ValueGroup"]  # Type alias


class SwValues(ARObject):
    """
    Complex type AR:SW-VALUES
    Tag variants: 'SW-VALUES-PHYS'
    """

    def __init__(self,
                 values: list[SwValueElement] | None = None) -> None:
        self.values = []
        if values is not None:
            if isinstance(values, (int, float, str, NumericalValue, ValueGroup)):
                self.append(values)
            elif isinstance(values, list):
                for value in values:
                    self.append(value)

    def append(self, value: SwValueElement) -> None:
        """
        Appends value to list of values
        XML elements not supported:

        - VTF
        - VF
        """
        if isinstance(value, (int, float, str, NumericalValue, ValueGroup)):
            self.values.append(value)
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")


class ValueGroup(SwValues):
    """
    Complex type AR:VALUE-GROUP
    Tag variants: 'VG'
    """

    def __init__(self,
                 label: str | MultilanguageLongName | tuple[ar_enum.Language, str] | LanguageLongName | None = None,
                 values: SwValues | None = None) -> None:
        self.label: MultilanguageLongName | None = None
        super().__init__(values)
        if label is not None:
            if isinstance(label, MultilanguageLongName):
                self.label = label
            elif isinstance(label, (tuple, LanguageLongName)):
                self.label = MultilanguageLongName(label)
            else:
                raise TypeError(f"Invalid type for 'label': {str(type(label))}")


class SwAxisCont(ARObject):
    """
    Complex type AR:SW-AXIS-CONT
    Tag variants: 'SW-AXIS-CONT'
    """

    def __init__(self,
                 category: ar_enum.CalibrationAxisCategory | None = None,
                 unit_ref: UnitRef | None = None,
                 unit_display_name: SingleLanguageUnitNames | None = None,
                 sw_axis_index: int | str | None = None,
                 sw_array_size: ValueList | None = None,
                 sw_values_phys: SwValues | None = None) -> None:
        self.category: ar_enum.CalibrationAxisCategory = None  # .CATEGORY
        self.unit_ref: UnitRef = None  # .UNIT-REF
        self.unit_display_name: SingleLanguageUnitNames = None  # .UNIT-DISPLAY_NAME
        self.sw_axis_index: int | str = None  # .SW-AXIS-INDEX
        self.sw_array_size: ValueList = None  # .SW-ARRAYSIZE
        self.sw_values_phys: SwValues = None  # .SW-VALUES-PHYS
        self._assign_optional('category', category, ar_enum.CalibrationAxisCategory)
        self._assign_optional_strict('unit_ref', unit_ref, UnitRef)
        self._assign_optional_strict('unit_display_name', unit_display_name, SingleLanguageUnitNames)
        if sw_axis_index is not None:
            if isinstance(sw_axis_index, (int, str)):
                self.sw_axis_index = sw_axis_index
            else:
                error_msg = "Invalid type for parameter 'sw_axis_index'. Expected 'int' or 'str', "
                raise TypeError(error_msg + f"got '{str(type(sw_axis_index))}'")
        self._assign_optional_strict('sw_array_size', sw_array_size, ValueList)
        self._assign_optional_strict('sw_values_phys', sw_values_phys, SwValues)


class SwValueCont(ARObject):
    """
    Complex type AR:SW-VALUE-CONT
    Tag variants: 'SW-VALUE-CONT'
    """

    def __init__(self,
                 unit_ref: UnitRef | None = None,
                 unit_display_name: SingleLanguageUnitNames | None = None,
                 sw_array_size: ValueList | None = None,
                 sw_values_phys: SwValues | None = None) -> None:
        self.unit_ref: UnitRef = None  # .UNIT-REF
        self.unit_display_name: SingleLanguageUnitNames = None  # .UNIT-DISPLAY_NAME
        self.sw_array_size: ValueList = None  # .SW-ARRAYSIZE
        self.sw_values_phys: SwValues = None  # .SW-VALUES-PHYS
        self._assign_optional_strict('unit_ref', unit_ref, UnitRef)
        self._assign_optional_strict('unit_display_name', unit_display_name, SingleLanguageUnitNames)
        self._assign_optional_strict('sw_array_size', sw_array_size, ValueList)
        self._assign_optional_strict('sw_values_phys', sw_values_phys, SwValues)


# --- Constant and value specifications


class ValueSpecification(ARObject):
    """
    Group AR:VALUE-SPECIFCATION
    Base class for value specifications
    """

    def __init__(self, label: str | None = None) -> None:
        self.label = label  # .SHORT-LABEL
        # .VARIATION-POINT not supported

    @classmethod
    def make_value_with_check(cls,
                              value: InitValueArgType | None = None,
                              ) -> ValueSpecificationElement | None:
        """
        #convenience-method

        Wrapper for checking and creating init values based on different value types

        The main differences compared to make_value are:
        * Returns None if input value is None.
        * Can create ConstantReference objects if given ConstantRef input.
        """
        if value is not None:
            if isinstance(value, ValueSpecification):
                return value  # Already a proper init-value
            elif isinstance(value, ConstantRef):
                return ConstantReference(value)  # Wrap inside constant reference
            elif isinstance(value, (int, float, str, list, tuple)):
                return cls.make_value(value)  # Attempt to create a new value based on raw python data
            else:
                raise TypeError(f"Unsupported type: {str(type(value))}")
        return None

    @classmethod
    def make_value(cls, data: Any) -> ValueSpecificationElement:
        """
        #convenience-method

        Builds value specification based on Python data
        Format 1 - data is not a tuple:
          value = data
        Format 2 - data is 2-tuple:
          label = data[0]
          value = data[1]
        Format 3 - data is a 3-tuple:
          label = data[0]
          value = None
          default_pattern = data[2]
          This format is used only when creating NotAvailableValueSpecification

        The type of 'value' can be one of:

        1. scalar value (int, float, str)
        2. list: (used for array and record values)
           When using list, the first list-element must contain a string which acts as a
           marker indicating what kind of element you want to create.
           - "A" or "ARRAY": Will use remaining list elements to create an ArrayValueSpecification
           - "R" or "RECORD": Will use remaining list elements to create an RecordValueSpecification
        3. None: used for creating NotAvailableValueSpecification
        """
        label = None
        default_pattern = None
        if isinstance(data, tuple):
            if not isinstance(data[0], str):
                raise TypeError("First tuple element must be a string")
            if len(data) == 2:
                label, value = data
            elif len(data) == 3:
                label, value, default_pattern = data
            else:
                raise ValueError(f"Too many elements in tuple: {repr(data)}")
        else:
            value = data
        return ValueSpecification._make_from_args(label, value, default_pattern)

    @classmethod
    def _make_from_args(cls, label: str | None,
                        value: Any,
                        default_pattern: int | None = None) -> ValueSpecificationElement:
        if isinstance(value, (int, float)):
            return NumericalValueSpecification(label, value)
        elif isinstance(value, str):
            return TextValueSpecification(label, value)
        elif value is None:
            return NotAvailableValueSpecification(label, default_pattern)
        elif isinstance(value, list):
            if not isinstance(value[0], str):
                raise TypeError("First element of a list must be a string")
            if value[0].upper() in ("A", "ARRAY"):
                return ValueSpecification._make_array_value_spefication(label, value[1:])
            elif value[0].upper() in ("R", "RECORD"):
                return ValueSpecification._make_record_value_spefication(label, value[1:])
            else:
                raise ValueError(f"Invalid element type: {str(type(value[0]))}")
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")

    @classmethod
    def _make_array_value_spefication(cls, label: str | None, values: list) -> "ArrayValueSpecification":
        elements = []
        for value in values:
            elements.append(ValueSpecification.make_value(value))
        return ArrayValueSpecification(label, elements)

    @classmethod
    def _make_record_value_spefication(cls, label: str | None, values: list) -> "RecordValueSpecification":
        fields = []
        for value in values:
            fields.append(ValueSpecification.make_value(value))
        return RecordValueSpecification(label, fields)


class TextValueSpecification(ValueSpecification):
    """
    Complex type AR:TEXT-VALUE-SPECIFICATION
    Tag variants: 'TEXT-VALUE-SPECIFICATION'
    """

    def __init__(self, label: str | None = None, value: str | None = None) -> None:
        super().__init__(label)
        self.value = None if value is None else str(value)


class NumericalValueSpecification(ValueSpecification):
    """
    Complex type AR:NUMERICAL-VALUE-SPECIFICATION
    Tag variants: 'NUMERICAL-VALUE-SPECIFICATION'
    """

    def __init__(self, label: str | None = None, value: int | float | None = None) -> None:
        super().__init__(label)
        self.value = value


class NotAvailableValueSpecification(ValueSpecification):
    """
    Complex type AR:NOT-AVAILABLE-VALUE-SPECIFICATION
    Tag variants: 'NOT-AVAILABLE-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 label: str | None = None,
                 default_pattern: int | None = None,
                 default_pattern_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        super().__init__(label)
        if isinstance(default_pattern, int) and default_pattern < 0:
            raise ValueError("default_pattern must be a positive integer")
        self.default_pattern = default_pattern
        self.default_pattern_format = default_pattern_format  # Currently not used


class ArrayValueSpecification(ValueSpecification):
    """
    Complex type AR:ARRAY-VALUE-SPECIFICATION
    Tag variants: 'ARRAY-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 label: str | None = None,
                 elements: list[ValueSpecificationElement] | None = None
                 ) -> None:
        super().__init__(label)
        self.elements: list[ValueSpecificationElement] = []
        if elements is not None:
            if isinstance(elements, ValueSpecification):
                self.append(elements)
            elif isinstance(elements, list):
                for element in elements:
                    self.append(element)

    def append(self, element: ValueSpecificationElement):
        """
        Appends element to array specification
        """
        if not isinstance(element, ValueSpecification):
            raise TypeError(f"Invalid type for 'element': {str(type(element))}")
        self.elements.append(element)


class RecordValueSpecification(ValueSpecification):
    """
    Complex type AR:RECORD-VALUE-SPECIFICATION
    Tag variants: 'RECORD-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 label: str | None = None,
                 fields: list[ValueSpecificationElement] | None = None
                 ) -> None:
        super().__init__(label)
        self.fields: list[ValueSpecificationElement] = []
        if fields is not None:
            if isinstance(fields, ValueSpecification):
                self.append(fields)
            elif isinstance(fields, list):
                for field in fields:
                    self.append(field)

    def append(self, field: ValueSpecificationElement):
        """
        Appends field to record specification
        """
        if not isinstance(field, ValueSpecification):
            raise TypeError(f"Invalid type for 'field': {str(type(field))}")
        self.fields.append(field)


class ApplicationValueSpecification(ValueSpecification):
    """
    Complex type AR:APPLICATION-VALUE-SPECIFICATION
    Tag variants: APPLICATION-VALUE-SPECIFICATION
    """

    def __init__(self,
                 label: str | None = None,
                 category: str | None = None,
                 sw_axis_conts: SwAxisCont | list[SwAxisCont] | None = None,
                 sw_value_cont: SwValueCont | None = None
                 ) -> None:
        super().__init__(label)
        self.category: str = None
        self.sw_axis_conts: list[SwAxisCont] = []
        self.sw_value_cont: SwValueCont = None
        self._assign_optional_strict("category", category, str)
        self._assign_optional_strict("sw_value_cont", sw_value_cont, SwValueCont)
        if sw_axis_conts is not None:
            if isinstance(sw_axis_conts, SwAxisCont):
                self.sw_axis_conts.append(sw_axis_conts)
            elif isinstance(sw_axis_conts, list):
                for elem in sw_axis_conts:
                    if isinstance(elem, SwAxisCont):
                        self.sw_axis_conts.append(elem)
                    else:
                        error_msg = "sw_axis_conts: Elements in list must of type SwAxisCont."
                        raise TypeError(error_msg + f" Got {str(type(elem))}")
            else:
                error_msg = "sw_axis_conts: argument must be either SwAxisCont or list[SwAxisCont]."
                raise TypeError(error_msg + f" Got {str(type(sw_axis_conts))}")


class ConstantSpecification(ARElement):
    """
    Complex type AR:CONSTANT-SPECIFICATION
    Tag Variants: 'CONSTANT-SPECIFICATION'
    """

    def __init__(self, name: str, value: ValueSpecificationElement | None = None, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.value: ValueSpecificationElement = None  # .VALUE-SPEC
        if value is not None:
            if isinstance(value, ValueSpecification):
                self.value = value
            else:
                error_msg = "Invalid type for parameter 'value'. Expected a subclass of ValueSpecification,"
                raise TypeError(error_msg + f" got {str(type(value))}")

    def ref(self) -> ConstantRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ConstantRef(ref_str)

    @classmethod
    def make_constant(cls,
                      name: str,
                      value: tuple[str, Any] | Any,
                      **kwargs) -> "ConstantSpecification":
        """
        Creates a new constant object and populates it from Python data.

        #convenience-method
        """
        value = ValueSpecification.make_value(value)
        return cls(name, value, **kwargs)


class ConstantReference(ValueSpecification):
    """
    Complex type AR:CONSTANT-REFERENCE
    Tag variants 'CONSTANT-REFERENCE'

    It's easy to confuse this with the ConstantRef class.
    This class is just a wrapper around an instance of ConstantRef.
    """

    def __init__(self,
                 constant_ref: ConstantRef | str | None = None,
                 label: str | None = None) -> None:
        self.constant_ref: ConstantRef = None
        super().__init__(label)
        if constant_ref is not None:
            if isinstance(constant_ref, str):
                self.constant_ref = ConstantRef(constant_ref)
            elif isinstance(constant_ref, ConstantRef):
                self.constant_ref = constant_ref
            else:
                raise ar_except.AssignmentTypeError("constant_ref", ("ConstantRef", "str"), constant_ref)


# --- Package (Partly implemented)


class Package(CollectableElement):
    """
    AR:AR-PACKAGE
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
        self.swc_mode_manager_error_event_prefix: str | None = None  # SwcModeManagerErrorEvent name prefix
        self.swc_mode_switch_event_prefix: str | None = None  # SwcModeSwitchEvent name prefix
        self.timing_event_prefix: str | None = None  # TimingEvent name prefix
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

# --- ModeDeclaration elements


class ModeDeclaration(Identifiable):
    """
    Complex type AR:MODE-DECLARATION
    Tag variants: 'MODE-DECLARATION'
    """

    def __init__(self,
                 name: str,
                 value: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.value: int | None = None  # .VALUE
        # .VARIATION-POINT not supported
        self._assign_optional_positive_int("value", value)

    def ref(self) -> ModeDeclarationRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeDeclarationRef(ref_str)


class ModeErrorBehavior(ARObject):
    """
    Complex type AR:MODE-ERROR-BEHAVIOR
    Tag variants: 'MODE-MANAGER-ERROR-BEHAVIOR' | 'MODE-USER-ERROR-BEHAVIOR'
    """

    def __init__(self,
                 default_mode_ref: ModeDeclarationRef | None = None,
                 error_reaction_policy: ar_enum.ModeErrorReactionPolicy | None = None
                 ) -> None:
        self.default_mode_ref: ModeDeclarationRef | None = None
        self.error_reaction_policy: ar_enum.ModeErrorReactionPolicy | None = None
        self._assign_optional("default_mode_ref", default_mode_ref, ModeDeclarationRef)
        self._assign_optional("error_reaction_policy", error_reaction_policy, ar_enum.ModeErrorReactionPolicy)


class ModeTransition(Identifiable):
    """
    Complex type AR:MODE-TRANSITION
    tag variants: 'MODE-TRANSITION'
    """

    def __init__(self,
                 name: str,
                 entered_mode_ref: ModeDeclarationRef | None = None,
                 exited_mode_ref: ModeDeclarationRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.entered_mode_ref: ModeDeclarationRef | None = None
        self.exited_mode_ref: ModeDeclarationRef | None = None
        self._assign_optional("entered_mode_ref", entered_mode_ref, ModeDeclarationRef)
        self._assign_optional("exited_mode_ref", exited_mode_ref, ModeDeclarationRef)


MODE_DECLARATION_TYPES = ModeDeclaration | list[ModeDeclaration] | list[str] | list[tuple[str, int]]


class ModeDeclarationGroup(ARElement):
    """
    Complex type AR:MODE-DECLARATION-GROUP
    Tag variants: 'MODE-DECLARATION-GROUP'
    """

    def __init__(self,
                 name: str,
                 mode_declarations: MODE_DECLARATION_TYPES | None = None,
                 initial_mode_ref: ModeDeclarationRef | None = None,
                 mode_manager_error_behavior: ModeErrorBehavior | None = None,
                 mode_transitions: ModeTransition | list[ModeTransition] | None = None,
                 mode_user_error_behavior: ModeErrorBehavior | None = None,
                 on_transition_value: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.initial_mode_ref: ModeDeclarationRef | None = None  # .INITIAL-MODE-REF
        self.mode_declarations: list[ModeDeclaration] = []  # .MODE-DECLARATIONS
        self.mode_manager_error_behavior: ModeErrorBehavior | None = None  # .MODE-MANAGER-ERROR-BEHAVIOR
        self.mode_transitions: list[ModeTransition] = []  # .MODE-TRANSITIONS
        self.mode_user_error_behavior: ModeErrorBehavior | None = None  # .MODE-USER-ERROR-BEHAVIOR
        self.on_transition_value: int | None = None  # .ON-TRANSITION-VALUE
        self._assign_optional("initial_mode_ref", initial_mode_ref, ModeDeclarationRef)
        self._assign_optional_strict("mode_manager_error_behavior", mode_manager_error_behavior, ModeErrorBehavior)
        self._assign_optional_strict("mode_user_error_behavior", mode_user_error_behavior, ModeErrorBehavior)
        self._assign_optional_positive_int("on_transition_value", on_transition_value)

        expected_types = "Expected 'ModeDeclaration', list[ModeDeclaration], list[str], list[tuple[str,int]]"
        if mode_declarations is not None:
            if isinstance(mode_declarations, ModeDeclaration):
                self.append_mode_declaratation(mode_declarations)
            elif isinstance(mode_declarations, list):
                for mode_declaration in mode_declarations:
                    if isinstance(mode_declaration, ModeDeclaration):
                        self.append_mode_declaratation(mode_declaration)
                    elif isinstance(mode_declaration, str):
                        self.create_mode_declaration(mode_declaration)
                    elif isinstance(mode_declaration, tuple):
                        self.create_mode_declaration(*mode_declaration)
                    else:
                        err_msg = f"Invalid type '{str(type(mode_declaration))}'"
                        raise TypeError(err_msg + ". " + expected_types)
            else:
                err_msg = f"mode_declarations: Invalid type '{str(type(mode_declarations))}'"
                raise TypeError(err_msg + ". " + expected_types)

        if mode_transitions is not None:
            if isinstance(mode_transitions, ModeTransition):
                self.append_mode_transition(mode_transitions)
            elif isinstance(mode_transitions, list):
                for mode_transition in mode_transitions:
                    self.append_mode_transition(mode_transition)
            else:
                msg = f"operations: Invalid type '{str(type(mode_transitions))}'"
                raise TypeError(msg + ". Expected 'ModeTransition' or list[ModeTransition]")

    def find(self, name: str) -> ModeDeclaration | ModeTransition | None:
        """
        Finds and returns sub-item based on short name
        """
        for mode_declaration in self.mode_declarations:
            if mode_declaration.name == name:
                return mode_declaration
        for mode_transition in self.mode_transitions:
            if mode_transition.name == name:
                return mode_transition
        return None

    def append_mode_declaratation(self, mode_declaration: ModeDeclaration) -> None:
        """
        Appends mode declaratopm to internal list of mode declarations
        """
        if isinstance(mode_declaration, ModeDeclaration):
            mode_declaration.parent = self
            self.mode_declarations.append(mode_declaration)
        else:
            msg = f"mode_declaration: Invalid type '{str(type(mode_declaration))}'"
            raise TypeError(msg + ". Expected 'ModeDeclaration'")

    def create_mode_declaration(self,
                                name: str,
                                value: int | None = None,
                                **kwargs) -> ModeDeclaration:
        """
        #convenience-method

        Adds a new mode declaration to this group
        """
        mode_declaration = ModeDeclaration(name, value, **kwargs)
        self.append_mode_declaratation(mode_declaration)
        return mode_declaration

    def append_mode_transition(self, mode_transition: ModeTransition) -> None:
        """
        Appends mode transition to internal list of transitions
        """
        if isinstance(mode_transition, ModeTransition):
            mode_transition.parent = mode_transition
            self.mode_transitions.append(mode_transition)
        else:
            msg = f"mode_transition: Invalid type '{str(type(mode_transition))}'"
            raise TypeError(msg + ". Expected 'ModeTransition'")

    def ref(self) -> ModeDeclarationGroupRef | None:
        """
        Returns a reference to this element or None if the element is
        not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeDeclarationGroupRef(ref_str)


class ModeDeclarationGroupPrototype(Identifiable):
    """
    Complex type AR:MODE-DECLARATION-GROUP-PROTOTYPE
    Tag variants: 'MODE-DECLARATION-GROUP-PROTOTYPE' | 'MODE-GROUP'
                  | 'PROCESS-STATE-MACHINE' | 'STATE-MACHINE'
    """

    def __init__(self,
                 name: str,
                 type_ref: ModeDeclarationGroupRef | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.calibration_access: ar_enum.SwCalibrationAccess | None = None  # .SW-CALIBRATION-ACCESS
        self.type_ref: ModeDeclarationGroupRef | None = None  # .TYPE-TREF
        self._assign_optional('calibration_access', calibration_access, ar_enum.SwCalibrationAccess)
        self._assign_optional('type_ref', type_ref, ModeDeclarationGroupRef)

    def ref(self) -> ModeDeclarationGroupPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeDeclarationGroupPrototypeRef(ref_str)


class ModeRequestTypeMap(ARObject):
    """
    Complex type AR:MODE-REQUEST-TYPE-MAP
    Tag variants: 'MODE-REQUEST-TYPE-MAP'
    """
    def __init__(self,
                 implementation_data_type: ImplementationDataTypeRef | None = None,
                 mode_group: ModeDeclarationGroupRef | None = None) -> None:
        # .IMPLEMENTATION-DATA-TYPE-REF
        self.implementation_data_type: ImplementationDataTypeRef | None = None
        # .MODE-GROUP-REF
        self.mode_group: ModeDeclarationGroupRef | None = None
        self._assign_optional('implementation_data_type', implementation_data_type, ImplementationDataTypeRef)
        self._assign_optional('mode_group', mode_group, ModeDeclarationGroupRef)


# --- Port Interface elements


class PortInterface(ARElement):
    """
    Group AR:PORT-INTERFACE
    """

    def __init__(self,
                 name: str,
                 is_service: bool | None = None,
                 service_kind: ar_enum.ServiceKind | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.is_service: bool | None = None  # .IS-SERVICE
        # .NAMESPACES not supported
        self.service_kind: ar_enum.ServiceKind | None = None  # .SERVICE-KIND
        self._assign_optional_strict("is_service", is_service, bool)
        self._assign_optional_strict("service_kind", service_kind, ar_enum.ServiceKind)


class DataInterface(PortInterface):
    """
    Group AR-DATA-INTERFACE

    Base class for data-based interfaces (as opposed to operations-based)
    """


class InvalidationPolicy(ARObject):
    """
    Complex type AR:INVALIDATION-POLICY
    Tag variants: 'INVALIDATION-POLICY'
    """

    def __init__(self,
                 data_element_ref: VariableDataPrototypeRef | None = None,
                 handle_invalid: ar_enum.HandleInvalid | None = None) -> None:
        self.data_element_ref: VariableDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        self.handle_invalid: ar_enum.HandleInvalid | None = None  # .HANDLE-INVALID
        self._assign_optional("data_element_ref", data_element_ref, VariableDataPrototypeRef)
        self._assign_optional("handle_invalid", handle_invalid, ar_enum.HandleInvalid)


class SenderReceiverInterface(DataInterface):
    """
    Complex type AR:SENDER-RECEIVER-INTERFACE
    Tag variants: 'SENDER-RECEIVER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 data_elements: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 invalidation_policies: InvalidationPolicy | list[InvalidationPolicy] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.data_elements: list[VariableDataPrototype] = []  # .DATA-ELEMENTS
        self.invalidation_policies: list[InvalidationPolicy] = []  # .INVALIDATION-POLICYS
        # .META-DATA-ITEM-SETS not supported
        if data_elements is not None:
            if isinstance(data_elements, VariableDataPrototype):
                self.append_data_element(data_elements)
            elif isinstance(data_elements, list):
                for data_element in data_elements:
                    self.append_data_element(data_element)
            else:
                msg = f"data_elements: Invalid type '{str(type(data_element))}'"
                raise TypeError(msg + ". Expected 'VariableDataPrototype' or list[VariableDataPrototype]")
        if invalidation_policies is not None:
            if isinstance(invalidation_policies, InvalidationPolicy):
                self.append_invalidation_policy(invalidation_policies)
            elif isinstance(invalidation_policies, list):
                for invalidation_policy in invalidation_policies:
                    self.append_invalidation_policy(invalidation_policy)
            else:
                msg = f"data_elements: Invalid type '{str(type(invalidation_policies))}'"
                raise TypeError(msg + ". Expected 'InvalidationPolicy' or list[InvalidationPolicy]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)

    def append_data_element(self, data_element: VariableDataPrototype):
        """
        Appends data element to internal list of elements
        """
        if isinstance(data_element, VariableDataPrototype):
            self.data_elements.append(data_element)
            data_element.parent = self
        else:
            msg = f"data_element: Invalid type '{str(type(data_element))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototype'")

    def append_invalidation_policy(self, invalidation_policy: InvalidationPolicy):
        """
        Appends invalidation policy to internal list of policies
        """
        if isinstance(invalidation_policy, InvalidationPolicy):
            self.invalidation_policies.append(invalidation_policy)
        else:
            msg = f"invalidation_policy: Invalid type '{str(type(invalidation_policy))}'"
            raise TypeError(msg + ". Expected 'InvalidationPolicy'")

    def create_data_element(self,
                            name: str,
                            init_value: ValueSpecificationElement | None = None,
                            **kwargs) -> VariableDataPrototype:
        """
        #convenience-method

        Adds a new data element to this port interface
        """
        data_element = VariableDataPrototype(name, init_value, **kwargs)
        self.append_data_element(data_element)
        return data_element

    def create_invalidation_policy(self,
                                   data_element_ref: VariableDataPrototypeRef | str,
                                   handle_invalid: ar_enum.HandleInvalid) -> InvalidationPolicy:
        """
        #convenience-method

        Adds a new invalidation policy to this port interface
        """
        if isinstance(data_element_ref, str):
            data_element_ref = VariableDataPrototypeRef(data_element_ref)
        elif not isinstance(data_element_ref, VariableDataPrototypeRef):
            msg = f"data_element_ref: Invalid type '{str(type(data_element_ref))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototypeRef' or 'str'")
        if not isinstance(handle_invalid, ar_enum.HandleInvalid):
            msg = f"handle_invalid: Invalid type '{str(type(data_element_ref))}'"
            raise TypeError(msg + ". Expected 'HandleInvalid'")
        invalidation_policy = InvalidationPolicy(data_element_ref, handle_invalid)
        self.append_invalidation_policy(invalidation_policy)
        return invalidation_policy


class NvDataInterface(DataInterface):
    """
    Complex type AR:NV-DATA-INTERFACE
    Tag variants: 'NV-DATA-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 data_elements: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.data_elements: list[VariableDataPrototype] = []  # .NV-DATAS
        if data_elements is not None:
            if isinstance(data_elements, VariableDataPrototype):
                self.append_data_element(data_elements)
            elif isinstance(data_elements, list):
                for data_element in data_elements:
                    self.append_data_element(data_element)
            else:
                msg = f"nv_datas: Invalid type '{str(type(data_elements))}'"
                raise TypeError(msg + ". Expected 'VariableDataPrototype' or list[VariableDataPrototype]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE)

    def append_data_element(self, nv_data: VariableDataPrototype):
        """
        Appends data element to internal list of data elements
        """
        if isinstance(nv_data, VariableDataPrototype):
            self.data_elements.append(nv_data)
            nv_data.parent = self
        else:
            msg = f"nv_data: Invalid type '{str(type(nv_data))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototype'")

    def create_data_element(self,
                            name: str,
                            init_value: ValueSpecificationElement | None = None,
                            **kwargs) -> VariableDataPrototype:
        """
        #convenience-method

        Adds a new data element to this port interface
        """
        data_element = VariableDataPrototype(name, init_value, **kwargs)
        self.append_data_element(data_element)
        return data_element


class ParameterInterface(DataInterface):
    """
    Complex type AR:PARAMETER-INTERFACE
    Tag variants: 'PARAMETER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 parameters: ParameterDataPrototype | list[ParameterDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.parameters: list[ParameterDataPrototype] = []  # .PARAMETERS
        if parameters is not None:
            if isinstance(parameters, ParameterDataPrototype):
                self.append_parameter(parameters)
            elif isinstance(parameters, list):
                for parameter in parameters:
                    self.append_parameter(parameter)
            else:
                msg = f"parameters: Invalid type '{str(type(parameters))}'"
                raise TypeError(msg + ". Expected 'ParameterDataPrototype' or list[ParameterDataPrototype]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE)

    def append_parameter(self, parameter: ParameterDataPrototype):
        """
        Appends parameter to internal list of parameters
        """
        if isinstance(parameter, ParameterDataPrototype):
            self.parameters.append(parameter)
            parameter.parent = self
        else:
            msg = f"parameter: Invalid type '{str(type(parameter))}'"
            raise TypeError(msg + ". Expected 'ParameterDataPrototype'")

    def create_parameter(self,
                         name: str,
                         init_value: ValueSpecificationElement | None = None,
                         **kwargs) -> ParameterDataPrototype:
        """
        #convenience-method

        Adds a new parameter to this port interface
        """
        data_element = ParameterDataPrototype(name, init_value, **kwargs)
        self.append_parameter(data_element)
        return data_element


class ApplicationError(Identifiable):
    """
    Complex type AR:APPLICATION-ERROR
    Tag variants: 'APPLICATION-ERROR'
    """

    def __init__(self,
                 name: str,
                 error_code: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.error_code: int | None = None
        self._assign_optional_strict("error_code", error_code, int)

    def ref(self) -> ApplicationErrorRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationErrorRef(ref_str)


PossibleErrorRefsTypes = ApplicationErrorRef | list[ApplicationErrorRef] | str | list[str]


class ClientServerOperation(Identifiable):
    """
    Complex type AR:CLIENT-SERVER-OPERATION
    Tag variants: 'CLIENT-SERVER-OPERATION'
    """

    def __init__(self,
                 name: str,
                 arguments: ArgumentDataPrototype | list[ArgumentDataPrototype] | None = None,
                 diag_arg_integrity: bool | None = None,
                 fire_and_forget: bool | None = None,
                 possible_error_refs: PossibleErrorRefsTypes | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.arguments: list[ArgumentDataPrototype] = []  # .ARGUMENTS
        self.diag_arg_integrity: bool | None = None  # .DIAG-ARG-INTEGRITY
        self.fire_and_forget: bool | None = None  # .FIRE-AND-FORGET
        # .POSSIBLE-AP-ERROR-REFS not supported
        # .POSSIBLE-AP-ERROR-SET-REFS not supported
        self.possible_error_refs: list[ApplicationErrorRef] = []  # .POSSIBLE-ERROR-REFS
        # .VARIATION-POINT not supported

        self._assign_optional_strict("diag_arg_integrity", diag_arg_integrity, bool)
        self._assign_optional_strict("fire_and_forget", fire_and_forget, bool)
        if arguments is not None:
            if isinstance(arguments, ArgumentDataPrototype):
                self.append_argument(arguments)
            elif isinstance(arguments, list):
                for argument in arguments:
                    self.append_argument(argument)
            else:
                msg = f"parameters: Invalid type '{str(type(arguments))}'"
                raise TypeError(msg + ". Expected 'ArgumentDataPrototype' or list[ArgumentDataPrototype]")

        if possible_error_refs is not None:
            if isinstance(possible_error_refs, ApplicationErrorRef):
                self.append_possible_error_ref(possible_error_refs)
            elif isinstance(possible_error_refs, str):
                self.append_possible_error_ref(ApplicationErrorRef(possible_error_refs))
            elif isinstance(possible_error_refs, list):
                for possible_error_ref in possible_error_refs:
                    self.append_possible_error_ref(possible_error_ref)
            else:
                msg = f"possible_error_refs: Invalid type '{str(type(possible_error_refs))}'"
                raise TypeError(msg + ". Expected 'ApplicationErrorRef' or list[ApplicationErrorRef]")

    def ref(self) -> ClientServerOperationRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ClientServerOperationRef(ref_str)

    def append_argument(self, argument: ArgumentDataPrototype) -> None:
        """
        Appends argument to internal list of arguments
        """
        if isinstance(argument, ArgumentDataPrototype):
            self.arguments.append(argument)
        else:
            msg = f"argument: Invalid type '{str(type(argument))}'"
            raise TypeError(msg + ". Expected 'ArgumentDataPrototype'")

    def create_argument(self,
                        name: str,
                        direction: ar_enum.ArgumentDirection | None = None,
                        server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                        **kwargs) -> ArgumentDataPrototype:
        """
        #convenience-method

        Adds a new argument to this operation
        """
        argument = ArgumentDataPrototype(name, direction, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def create_in_argument(self,
                           name: str,
                           server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                           **kwargs) -> ArgumentDataPrototype:
        """
        #convenience-method

        Adds a new in-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.IN, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def create_inout_argument(self,
                              name: str,
                              server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                              **kwargs) -> ArgumentDataPrototype:
        """
        #convenience-method

        Adds a new inout-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.INOUT, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def create_out_argument(self,
                            name: str,
                            server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                            **kwargs) -> ArgumentDataPrototype:
        """
        #convenience-method

        Adds a new out-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.OUT, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def append_possible_error_ref(self, possible_error_ref: ApplicationErrorRef) -> None:
        """
        Appends error reference to internal list of possible errors for this operation
        """
        if isinstance(possible_error_ref, ApplicationErrorRef):
            self.possible_error_refs.append(possible_error_ref)
        else:
            msg = f"argument: Invalid type '{str(type(possible_error_ref))}'"
            raise TypeError(msg + ". Expected 'ApplicationErrorRef'")

    def create_possible_error_ref(self, value: str) -> ApplicationErrorRef:
        """
        #convenience-method

        Adds a new possible error reference to this operation
        """
        possible_error_ref = ApplicationErrorRef(value)
        self.append_possible_error_ref(possible_error_ref)
        return possible_error_ref


class ClientServerInterface(PortInterface):
    """
    Complex type AR:CLIENT-SERVER-INTERFACE
    Tag variants: 'CLIENT-SERVER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 operations: ClientServerOperation | list[ClientServerOperation] | None = None,
                 possible_errors: ApplicationError | list[ApplicationError] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.operations: list[ClientServerOperation] = []
        self.possible_errors: list[ApplicationError] = []

        if operations is not None:
            if isinstance(operations, ClientServerOperation):
                self.append_operation(operations)
            elif isinstance(operations, list):
                for operation in operations:
                    self.append_operation(operation)
            else:
                msg = f"operations: Invalid type '{str(type(operations))}'"
                raise TypeError(msg + ". Expected 'ClientServerOperation' or list[ClientServerOperation]")

        if possible_errors is not None:
            if isinstance(possible_errors, ApplicationError):
                self.append_operation(possible_errors)
            elif isinstance(possible_errors, list):
                for possible_error in possible_errors:
                    self.append_possible_errors(possible_error)
            else:
                msg = f"possible_errors: Invalid type '{str(type(possible_errors))}'"
                raise TypeError(msg + ". Expected 'ApplicationError' or list[ApplicationError]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE)

    def append_operation(self, operation: ClientServerOperation) -> None:
        """
        Appends operation to internal list of operations
        """
        if isinstance(operation, ClientServerOperation):
            self.operations.append(operation)
            operation.parent = self
        else:
            msg = f"operation: Invalid type '{str(type(operation))}'"
            raise TypeError(msg + ". Expected 'ClientServerOperation'")

    def append_possible_errors(self, possible_error: ApplicationError) -> None:
        """
        Appends possible error to internal list of possible errors
        """
        if isinstance(possible_error, ApplicationError):
            possible_error.parent = self
            self.possible_errors.append(possible_error)
        else:
            msg = f"operation: Invalid type '{str(type(possible_error))}'"
            raise TypeError(msg + ". Expected 'ApplicationError'")

    def create_operation(self,
                         name: str,
                         arguments: ArgumentDataPrototype | list[ArgumentDataPrototype] | None = None,
                         diag_arg_integrity: bool | None = None,
                         fire_and_forget: bool | None = None,
                         possible_error_refs: ApplicationErrorRef | list[ApplicationErrorRef] | None = None,
                         **kwargs) -> ClientServerOperation:
        """
        #convenience-method

        Adds a new operation to this port interface
        """
        operation = ClientServerOperation(name, arguments, diag_arg_integrity, fire_and_forget, possible_error_refs,
                                          **kwargs)
        self.append_operation(operation)
        return operation

    def create_possible_error(self,
                              name: str,
                              error_code: int | None = None,
                              **kwargs) -> ApplicationError:
        """
        #convenience-method

        Adds a new possible error in this port interface
        """
        possible_error = ApplicationError(name, error_code, **kwargs)
        self.append_possible_errors(possible_error)
        return possible_error


class ModeSwitchInterface(PortInterface):
    """
    Complex type AR:MODE-SWITCH-INTERFACE
    Tag variants: 'MODE-SWITCH-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 mode_group: ModeDeclarationGroupPrototype | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MODE-GROUP
        self.mode_group: ModeDeclarationGroupPrototype | None = None

        self._assign_optional_strict("mode_group", mode_group, ModeDeclarationGroupPrototype)

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE)

    def create_mode_group(self,
                          name: str,
                          type_ref: ModeDeclarationGroupRef | None = None,
                          calibration_access: ar_enum.SwCalibrationAccess | None = None,
                          **kwargs) -> ModeDeclarationGroupPrototype:
        """
        #convenience-method

        Adds a new mode declaration group to this port interface

        Note that this class only supports up to one mode group. Calling this method a second time
        will overwrite the previous value.
        """
        self.mode_group = ModeDeclarationGroupPrototype(name, type_ref, calibration_access, **kwargs)
        self.mode_group.parent = self
        return self.mode_group

# --- System Template Elements


class E2EProfileCompatibilityProps(ARElement):
    """
    Complex type AR:E-2-E-PROFILE-COMPATIBILITY-PROPS
    Tag variants: 'E-2-E-PROFILE-COMPATIBILITY-PROPS'
    """

    def __init__(self,
                 name: str,
                 transit_to_invalid_extended: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.transit_to_invalid_extended: bool | None = None  # .TRANSIT-TO-INVALID-EXTENDED
        self._assign_optional_strict("transit_to_invalid_extended", transit_to_invalid_extended, bool)

    def ref(self) -> E2EProfileCompatibilityPropsRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return E2EProfileCompatibilityPropsRef(ref_str)


class EndToEndTransformationComSpecProps(Describable):
    """
    Complex type AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
    Tag variants: 'END-TO-END-TRANSFORMATION-COM-SPEC-PROPS'
    """

    def __init__(self,  # pylint: disable=R0917
                 clear_from_valid_to_invalid: bool | None = None,
                 disable_e2e_check: bool | None = None,
                 disable_e2e_state_machine: bool | None = None,
                 e2e_profile_compatibility_props_ref: E2EProfileCompatibilityPropsRef | None = None,
                 max_delta_counter: int | None = None,
                 max_error_state_init: int | None = None,
                 max_error_state_invalid: int | None = None,
                 max_error_state_valid: int | None = None,
                 max_no_new_repeated_data: int | None = None,
                 min_ok_state_init: int | None = None,
                 min_ok_state_invalid: int | None = None,
                 min_ok_state_valid: int | None = None,
                 sync_counter_init: int | None = None,
                 window_size: int | None = None,
                 window_size_init: int | None = None,
                 window_size_invalid: int | None = None,
                 window_size_valid: int | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.clear_from_valid_to_invalid: bool | None = None  # .CLEAR-FROM-VALID-TO-INVALID
        self.disable_e2e_check: bool | None = None  # .DISABLE-END-TO-END-CHECK
        self.disable_e2e_state_machine: bool | None = None  # .DISABLE-END-TO-END-STATE-MACHINE
        # .E-2-E-PROFILE-COMPATIBILITY-PROPS-REF
        self.e2e_profile_compatibility_props_ref: E2EProfileCompatibilityPropsRef | None = None
        self.max_delta_counter: int | None = None  # .MAX-DELTA-COUNTER
        self.max_error_state_init: int | None = None  # .MAX-ERROR-STATE-INIT
        self.max_error_state_invalid: int | None = None   # .MAX-ERROR-STATE-INVALID
        self.max_error_state_valid: int | None = None   # .MAX-ERROR-STATE-VALID
        self.max_no_new_repeated_data: int | None = None   # .MAX-NO-NEW-OR-REPEATED-DATA
        self.min_ok_state_init: int | None = None   # .MIN-OK-STATE-INIT
        self.min_ok_state_invalid: int | None = None   # .MIN-OK-STATE-INVALID
        self.min_ok_state_valid: int | None = None   # .MIN-OK-STATE-VALID
        self.sync_counter_init: int | None = None   # .SYNC-COUNTER-INIT
        self.window_size: int | None = None   # .WINDOW-SIZE
        self.window_size_init: int | None = None   # .WINDOW-SIZE-INIT
        self.window_size_invalid: int | None = None   # .WINDOW-SIZE-INVALID
        self.window_size_valid: int | None = None   # .WINDOW-SIZE-VALID
        self._assign_optional_strict("clear_from_valid_to_invalid", clear_from_valid_to_invalid, bool)
        self._assign_optional_strict("disable_e2e_check", disable_e2e_check, bool)
        self._assign_optional_strict("disable_e2e_state_machine", disable_e2e_state_machine, bool)
        self._assign_optional("e2e_profile_compatibility_props_ref",
                              e2e_profile_compatibility_props_ref, E2EProfileCompatibilityPropsRef)
        self._assign_optional_positive_int("max_delta_counter", max_delta_counter)
        self._assign_optional_positive_int("max_error_state_init", max_error_state_init)
        self._assign_optional_positive_int("max_error_state_invalid", max_error_state_invalid)
        self._assign_optional_positive_int("max_error_state_valid", max_error_state_valid)
        self._assign_optional_positive_int("max_no_new_repeated_data", max_no_new_repeated_data)
        self._assign_optional_positive_int("min_ok_state_init", min_ok_state_init)
        self._assign_optional_positive_int("min_ok_state_invalid", min_ok_state_invalid)
        self._assign_optional_positive_int("min_ok_state_valid", min_ok_state_valid)
        self._assign_optional_positive_int("sync_counter_init", sync_counter_init)
        self._assign_optional_positive_int("window_size", window_size)
        self._assign_optional_positive_int("window_size_init", window_size_init)
        self._assign_optional_positive_int("window_size_invalid", window_size_invalid)
        self._assign_optional_positive_int("window_size_valid", window_size_valid)


# --- SoftwareComponent elements


class ModeSwitchedAckRequest(ARObject):
    """
    Complex type AR:MODE-SWITCHED-ACK-REQUEST
    Tag variants: 'MODE-SWITCHED-ACK'
    """

    def __init__(self, timeout: float | None = None) -> None:
        super().__init__()
        self.timeout: float | None = None
        self._assign_optional("timeout", timeout, float)


class TransmissionAcknowledgementRequest(ARObject):
    """
    Complex type AR:TRANSMISSION-ACKNOWLEDGEMENT-REQUEST
    Tag variants: 'TRANSMISSION-ACKNOWLEDGE'
    """

    def __init__(self,
                 timeout: float | int | None = None) -> None:
        super().__init__()
        self.timeout: float | None = None  # .TIMEOUT
        self._assign_optional("timeout", timeout, float)


class TransmissionComSpecProps(ARObject):
    """
    Complex type AR:TRANSMISSION-COM-SPEC-PROPS
    Tag variants: 'TRANSMISSION-PROPS'

    This only exists in AUTOSAR 4.6 or newer (schema version >= 49)
    """

    def __init__(self,
                 data_update_period: float | int | None = None,
                 minimum_send_interval: float | int | None = None,
                 transmission_mode: ar_enum.TransmissionMode | None = None
                 ) -> None:
        super().__init__()
        self.data_update_period: float | int | None = None  # .DATA-UPDATE-PERIOD
        self.minimum_send_interval: float | int | None = None  # .MINIMUM-SEND-INTERVAL
        self.transmission_mode: ar_enum.TransmissionMode | None = None  # .TRANSMISSION-MODE
        self._assign_optional("data_update_period", data_update_period, float)
        self._assign_optional("minimum_send_interval", minimum_send_interval, float)
        self._assign_optional("transmission_mode", transmission_mode, ar_enum.TransmissionMode)


class ProvidePortComSpec(ARObject):
    """
    Group AR:P-PORT-COM-SPEC
    """

    @classmethod
    def make_from_port_interface(cls, port_interface: PortInterface, **kwargs) -> "ProvidePortComSpec":
        """
        #convenience-method

        Creates P-PORT com-spec from port interface

        For SenderReceiverInterface:
        If interface has a single element: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple elements: kwargs is a dict of dict where
                                            outer dict keys are element names and each value
                                            is another dict containing key-value pairs for one com-spec

        For ClientServerInterface:
        If interface has a single operation: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple operations: kwargs is a dict of dict where
                                              outer dict keys are operation names and each value
                                              is another dict containing key-value pairs for one com-spec

        For ModeSwitchInterface:
        kwargs is a dict with key-value pairs for one com-spec
        Note: Avoid manually setting the mode_group_ref option, it will be automatically set for you.
        """
        if isinstance(port_interface, SenderReceiverInterface):
            if len(port_interface.data_elements) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one element")
            if len(port_interface.data_elements) == 1:
                data_element: VariableDataPrototype = port_interface.data_elements[0]
                if data_element.is_queued:
                    return QueuedSenderComSpec(data_element_ref=data_element.ref(), **kwargs)
                else:
                    return cls.make_non_queued_sender_com_spec(data_element_ref=data_element.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for element_name, value in kwargs.items():
                    unprocessed.add(element_name)
                    if not isinstance(value, dict):
                        msg = f"{port_interface.name}.{element_name}: Expected dict type, got {str(type(value))}"
                        raise TypeError(msg)
                for data_element in port_interface.data_elements:
                    if data_element.name in unprocessed:
                        unprocessed.remove(data_element.name)
                        com_spec_args = kwargs[data_element.name]
                        if data_element.is_queued:
                            com_spec = QueuedSenderComSpec(data_element_ref=data_element.ref(),
                                                           **com_spec_args)
                        else:
                            com_spec = cls.make_non_queued_sender_com_spec(data_element_ref=data_element.ref(),
                                                                           **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    element_names = ', '.join(list(unprocessed))
                    msg = f"{port_interface.name}: Data element(s) not found in port interface: '{element_names}'"
                    raise ValueError(msg)
                return com_spec_list
        if isinstance(port_interface, ClientServerInterface):
            if len(port_interface.operations) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one operation")
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
                return ServerComSpec(operation_ref=operation.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for operation_name in kwargs:
                    unprocessed.add(operation_name)
                for operation in port_interface.operations:
                    if operation.name in unprocessed:
                        unprocessed.remove(operation.name)
                        com_spec_args = kwargs[operation.name]
                        com_spec = ServerComSpec(operation_ref=operation.ref(), **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    operations = ', '.join(list(unprocessed))
                    raise ValueError(f"{port_interface.name}: Operation(s) not found in port interface: '{operations}'")
                return com_spec_list
        elif isinstance(port_interface, ModeSwitchInterface):
            if port_interface.mode_group is None:
                raise ValueError(f"{port_interface.name}: Port interface doesn't have a mode group set")
            assert port_interface.mode_group.ref() is not None
            return ModeSwitchSenderComSpec(mode_group_ref=port_interface.mode_group.ref(), **kwargs)
        else:
            raise NotImplementedError(str(type(port_interface)))

    @classmethod
    def make_non_queued_sender_com_spec(cls,
                                        init_value: InitValueArgType | None = None,
                                        **kwargs
                                        ) -> "NonqueuedSenderComSpec":
        """
        #convenience-method

        Convenience method for creating NonqueuedSenderComSpec
        """
        init_value = ValueSpecification.make_value_with_check(init_value)
        return NonqueuedSenderComSpec(init_value=init_value, **kwargs)


class SenderComSpec(ProvidePortComSpec):
    """
    Group AR:SENDER-COM-SPEC
    """

    def __init__(self,
                 data_element_ref: AutosarDataPrototypeRef | VariableDataPrototypeRef | None = None,
                 handle_out_of_range: ar_enum.HandleOutOfRange | None = None,
                 network_representation: SwDataDefProps | None = None,
                 transmission_acknowledge: TransmissionAcknowledgementRequest | float | None = None,
                 tranmsission_props: TransmissionComSpecProps | None = None,
                 uses_end_to_end_protection: bool | None = None
                 ) -> None:
        super().__init__()
        # .COMPOSITE-NETWORK-REPRESENTATIONS not supported
        self.data_element_ref: AutosarDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        # .DATA-UPDATE-PERIOD not supported (Status Removed)
        self.handle_out_of_range: ar_enum.HandleOutOfRange | None = None  # .HANDLE-OUT-OF-RANGE
        self.network_representation: SwDataDefProps | None = None  # .NETWORK-REPRESENTATION
        # .SENDER-INTENT not supported (Adaptive Platform)
        self.transmission_acknowledge: TransmissionAcknowledgementRequest | None = None  # .TRANSMISSION-ACKNOWLEDGE
        self.tranmsission_props: TransmissionComSpecProps | None = None  # .TRANSMISSION-PROPS
        self.uses_end_to_end_protection: bool | None = None  # .USES-END-TO-END-PROTECTION
        if data_element_ref is not None:
            if isinstance(data_element_ref, AutosarDataPrototypeRef):
                self.data_element_ref = data_element_ref
            elif isinstance(data_element_ref, VariableDataPrototypeRef):
                self.data_element_ref = AutosarDataPrototypeRef(data_element_ref.value,
                                                                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
            else:
                raise ar_except.AssignmentTypeError("data_element_ref",
                                                    ("AutosarDataPrototypeRef", "VariableDataPrototypeRef"),
                                                    data_element_ref)
        self._assign_optional("handle_out_of_range", handle_out_of_range, ar_enum.HandleOutOfRange)
        self._assign_optional_strict("network_representation", network_representation, SwDataDefProps)
        self._assign_optional_strict("tranmsission_props", tranmsission_props, TransmissionComSpecProps)
        self._assign_optional("uses_end_to_end_protection", uses_end_to_end_protection, bool)
        if transmission_acknowledge is not None:
            if isinstance(transmission_acknowledge, (int, float)):
                self.transmission_acknowledge = TransmissionAcknowledgementRequest(transmission_acknowledge)
            elif isinstance(transmission_acknowledge, TransmissionAcknowledgementRequest):
                self.transmission_acknowledge = transmission_acknowledge
            else:
                msg_part1 = f"Invalid type '{str(type(transmission_acknowledge))}'"
                msg_part2 = "Expected (TransmissionAcknowledgementRequest, float)"
                raise TypeError(f"transmission_acknowledge: {msg_part1}. {msg_part2}.")


class ModeSwitchSenderComSpec(ProvidePortComSpec):
    """
    Complex type AR:MODE-SWITCH-SENDER-COM-SPEC
    Tag variants: 'MODE-SWITCH-SENDER-COM-SPEC'
    """

    def __init__(self,
                 mode_group_ref: str | ModeDeclarationGroupPrototypeRef | None = None,
                 enhanced_mode_api: bool | None = None,
                 mode_switched_ack: ModeSwitchedAckRequest | float | None = None,
                 queue_length: int | None = None
                 ) -> None:
        super().__init__()
        self.mode_group_ref: ModeDeclarationGroupPrototypeRef | None = None  # .ENHANCED-MODE-API
        self.enhanced_mode_api: bool | None = None  # .MODE-GROUP-REF
        self.mode_switched_ack: ModeSwitchedAckRequest | None = None  # .MODE-SWITCHED-ACK
        self.queue_length = None  # .QUEUE-LENGTH
        self._assign_optional("mode_group_ref", mode_group_ref, ModeDeclarationGroupPrototypeRef)
        self._assign_optional("enhanced_mode_api", enhanced_mode_api, bool)
        if mode_switched_ack is not None:
            if isinstance(mode_switched_ack, (int, float)):
                self.mode_switched_ack = ModeSwitchedAckRequest(mode_switched_ack)
            elif isinstance(mode_switched_ack, ModeSwitchedAckRequest):
                self.mode_switched_ack = mode_switched_ack
            else:
                msg = f"Invalid type. Expected (ModeSwitchedAckRequest, str), got '{str(type(mode_switched_ack))}'"
                raise TypeError("mode_switched_ack: " + msg)
        self._assign_optional_positive_int("queue_length", queue_length)


class QueuedSenderComSpec(SenderComSpec):
    """
    Complex type AR:QUEUED-SENDER-COM-SPEC
    Tag variants: 'QUEUED-SENDER-COM-SPEC'

    Doesn't need its own constuctor, we can use the one defined by base class
    """


class NonqueuedSenderComSpec(SenderComSpec):
    """
    Complex type AR:NONQUEUED-SENDER-COM-SPEC
    Tag variants: 'NONQUEUED-SENDER-COM-SPEC'
    """

    def __init__(self,
                 init_value: ValueSpecificationElement | None = None,
                 data_filter: DataFilter | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.data_filter: DataFilter | None = None  # .DATA-FILTER
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self._assign_optional_strict("data_filter", data_filter, DataFilter)
        self._assign_optional_strict("init_value", init_value, ValueSpecification)


class NvProvideComSpec(ProvidePortComSpec):
    """
    Complex type AR:NV-PROVIDE-COM-SPEC
    Tag variants: 'NV-PROVIDE-COM-SPEC'
    """

    def __init__(self,
                 variable_ref: VariableDataPrototypeRef | None = None,
                 ram_block_init_value: ValueSpecificationElement | None = None,
                 rom_block_init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.ram_block_init_value: ValueSpecificationElement | None = None  # .RAM-BLOCK-INIT-VALUE
        self.rom_block_init_value: ValueSpecificationElement | None = None  # .RAM-BLOCK-INIT-VALUE
        self.variable_ref: VariableDataPrototypeRef | None = None         # .VARIABLE-REF
        self._assign_optional_strict("ram_block_init_value", ram_block_init_value, ValueSpecification)
        self._assign_optional_strict("rom_block_init_value", rom_block_init_value, ValueSpecification)
        self._assign_optional("variable_ref", variable_ref, VariableDataPrototypeRef)


class ParameterProvideComSpec(ProvidePortComSpec):
    """
    Complex type AR:PARAMETER-PROVIDE-COM-SPEC
    Tag variants: 'PARAMETER-PROVIDE-COM-SPEC'
    """

    def __init__(self,
                 parameter_ref: ParameterDataPrototypeRef | str | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.parameter_ref: VariableDataPrototypeRef | None = None  # .PARAMETER-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("parameter_ref", parameter_ref, ParameterDataPrototypeRef)


EndToEndTransformationComSpecPropsArgTypes = Union[EndToEndTransformationComSpecProps,
                                                   list[EndToEndTransformationComSpecProps]]


class ServerComSpec(ProvidePortComSpec):
    """
    Complex type AR:SERVER-COM-SPEC
    Tag variants: 'SERVER-COM-SPEC'
    """

    def __init__(self,
                 operation_ref: ClientServerOperationRef | None = None,
                 queue_length: int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None
                 ) -> None:
        super().__init__()
        # .GETTER-REF not supported (Adaptive Platform)
        self.operation_ref: ClientServerOperationRef | None = None  # .OPERATION-REF
        self.queue_length: int | None = None  # .QUEUE-LENGTH
        # .SETTER-REF not supported (Adaptive Platform)
        # .TRANSFORMATION-COM-SPEC-PROPSS
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        # USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet supported under transformation_com_spec_props
        self._assign_optional("operation_ref", operation_ref, ClientServerOperationRef)
        self._assign_optional_positive_int("queue_length", queue_length)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(props)
        else:
            raise TypeError("props must be of type EndToEndTransformationComSpecProps")


class ReceptionComSpecProps(ARObject):
    """
    Complex type AR:RECEPTION-COM-SPEC-PROPS
    Tag variants: 'RECEPTION-PROPS'
    """

    def __init__(self,
                 data_update_period: float | None = None,
                 timeout: float | None = None,
                 ) -> None:
        super().__init__()
        self.data_update_period: float | None = None  # .DATA-UPDATE-PERIOD
        self.timeout: float | None = None  # .TIMEOUT
        self._assign_optional("data_update_period", data_update_period, float)
        self._assign_optional("timeout", timeout, float)


class RequirePortComSpec(ARObject):
    """
    Group AR:R-PORT-COM-SPEC
    """

    @classmethod
    def make_from_port_interface(cls, port_interface: PortInterface, **kwargs) -> "RequirePortComSpec":
        """
        #convenience-method

        Creates R-PORT com-spec from port-interface

        For SenderReceiverInterface:
        If interface has a single element: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple elements: kwargs is a dict of dict where
                                            outer dict keys are element names and each value
                                            is another dict containing key-value pairs for one com-spec

        Note: Avoid manually setting the data_element_ref option, it will be automatically set for you.

        For ClientServerInterface:
        If interface has a single operation: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple operations: kwargs is a dict of dict where
                                              outer dict keys are operation names and each value
                                              is another dict containing key-value pairs for one com-spec
        Note: Avoid manually setting the operation_ref option, it will be automatically set for you.

        For ModeSwitchInterface:
        kwargs is a dict with key-value pairs for one com-spec
        Note: Avoid manually setting the mode_group_ref option, it will be automatically set for you.
        """
        if isinstance(port_interface, SenderReceiverInterface):
            if len(port_interface.data_elements) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one element")
            if len(port_interface.data_elements) == 1:
                data_element: VariableDataPrototype = port_interface.data_elements[0]
                if data_element.is_queued:
                    assert data_element.ref() is not None
                    return QueuedReceiverComSpec(data_element_ref=data_element.ref(), **kwargs)
                else:
                    return cls.make_non_queued_receiver_com_spec(data_element_ref=data_element.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for element_name, value in kwargs.items():
                    unprocessed.add(element_name)
                    if not isinstance(value, dict):
                        msg = f"{port_interface.name}.{element_name}: Expected dict type, got {str(type(value))}"
                        raise TypeError(msg)
                for data_element in port_interface.data_elements:
                    if data_element.name in unprocessed:
                        unprocessed.remove(data_element.name)
                        com_spec_args = kwargs[data_element.name]
                        assert data_element.ref() is not None
                        if data_element.is_queued:
                            com_spec = QueuedReceiverComSpec(data_element_ref=data_element.ref(),
                                                             **com_spec_args)
                        else:
                            com_spec = cls.make_non_queued_receiver_com_spec(data_element_ref=data_element.ref(),
                                                                             **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    element_names = ', '.join(list[unprocessed])
                    msg = f"{port_interface.name}: Data element(s) not found in port interface: '{element_names}'"
                    raise ValueError(msg)
                return com_spec_list
        elif isinstance(port_interface, ClientServerInterface):
            if len(port_interface.operations) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one operation")
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
                return ClientComSpec(operation_ref=operation.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for operation_name in kwargs:
                    unprocessed.add(operation_name)
                for operation in port_interface.operations:
                    if operation.name in unprocessed:
                        unprocessed.remove(operation.name)
                        com_spec_args = kwargs[operation.name]
                        assert operation.ref() is not None
                        com_spec = ClientComSpec(operation_ref=operation.ref(), **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    operations = ', '.join(list[unprocessed])
                    raise ValueError(f"{port_interface.name}: Operation(s) not found in port interface: '{operations}'")
                return com_spec_list
        elif isinstance(port_interface, ModeSwitchInterface):
            if port_interface.mode_group is None:
                raise ValueError(f"{port_interface.name}: Port interface doesn't have a mode group set")
            assert port_interface.mode_group.ref() is not None
            return ModeSwitchReceiverComSpec(mode_group_ref=port_interface.mode_group.ref(), **kwargs)
        else:
            raise NotImplementedError(str(type(port_interface)))

    @classmethod
    def make_non_queued_receiver_com_spec(cls,
                                          init_value: InitValueArgType | None = None,
                                          **kwargs
                                          ) -> "NonqueuedReceiverComSpec":
        """
        #convenience-method

        Convenience method for creating NonqueuedReceiverComSpec
        """
        init_value = ValueSpecification.make_value_with_check(init_value)
        return NonqueuedReceiverComSpec(init_value=init_value, **kwargs)


class ReceiverComSpec(RequirePortComSpec):
    """
    Group AR:RECEIVER-COM-SPEC
    """

    def __init__(self,
                 data_element_ref: AutosarDataPrototypeRef | VariableDataPrototypeRef | None = None,
                 handle_out_of_range: ar_enum.HandleOutOfRange | None = None,
                 handle_out_of_range_status: ar_enum.HandleOutOfRangeStatus | None = None,
                 max_delta_counter_init: int | None = None,
                 max_no_new_repeated_data: int | None = None,
                 network_representation: SwDataDefProps | None = None,
                 reception_props: ReceptionComSpecProps | None = None,
                 replace_with: Union["VariableAccess", None] = None,
                 sync_counter_init: int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None,
                 uses_end_to_end_protection: bool | None = None
                 ) -> None:
        super().__init__()
        # .COMPOSITE-NETWORK-REPRESENTATIONS not supported
        self.data_element_ref: AutosarDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        # .DATA-UPDATE-PERIOD not supported (Status Removed)
        # .EXTERNAL-REPLACEMENT-REF not supported (Status Removed)
        self.handle_out_of_range: ar_enum.HandleOutOfRange | None = None  # .HANDLE-OUT-OF-RANGE
        self.handle_out_of_range_status: ar_enum.HandleOutOfRangeStatus | None = None  # .HANDLE-OUT-OF-RANGE-STATUS
        self.max_delta_counter_init: int | None = None   # .MAX-DELTA-COUNTER-INIT
        self.max_no_new_repeated_data: int | None = None   # .MAX-NO-NEW-OR-REPEATED-DATA
        self.network_representation: SwDataDefProps | None = None  # .NETWORK-REPRESENTATION
        # .RECEIVER-INTENT not supported (adaptive platform)
        self.reception_props: ReceptionComSpecProps | None = None  # .RECEPTION-PROPS
        self.replace_with: VariableAccess | None = None  # .REPLACE-WITH
        self.sync_counter_init: int | None = None   # .SYNC-COUNTER-INIT
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        self.uses_end_to_end_protection: bool | None = None  # .USES-END-TO-END-PROTECTION
        if data_element_ref is not None:
            if isinstance(data_element_ref, AutosarDataPrototypeRef):
                self.data_element_ref = data_element_ref
            elif isinstance(data_element_ref, VariableDataPrototypeRef):
                self.data_element_ref = AutosarDataPrototypeRef(data_element_ref.value,
                                                                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
            else:
                raise ar_except.AssignmentTypeError("data_element_ref",
                                                    ("AutosarDataPrototypeRef", "VariableDataPrototypeRef"),
                                                    data_element_ref)

        self._assign_optional("handle_out_of_range", handle_out_of_range, ar_enum.HandleOutOfRange)
        self._assign_optional("handle_out_of_range_status", handle_out_of_range_status, ar_enum.HandleOutOfRangeStatus)
        self._assign_optional_positive_int("max_delta_counter_init", max_delta_counter_init)
        self._assign_optional_positive_int("max_no_new_repeated_data", max_no_new_repeated_data)
        self._assign_optional_strict("network_representation", network_representation, SwDataDefProps)
        self._assign_optional_strict("reception_props", reception_props, ReceptionComSpecProps)
        self._assign_optional_strict("replace_with", replace_with, VariableAccess)
        self._assign_optional_positive_int("sync_counter_init", sync_counter_init)
        self._assign_optional("uses_end_to_end_protection", uses_end_to_end_protection, bool)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, com_spec_props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(com_spec_props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(com_spec_props)
        else:
            raise TypeError("com_spec_props must be of type EndToEndTransformationComSpecProps")


class QueuedReceiverComSpec(ReceiverComSpec):
    """
    Complex type AR:QUEUED-RECEIVER-COM-SPEC
    Tag variants: 'QUEUED-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 queue_length: int | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.queue_length: int | None = None  # .QUEUE-LENGTH
        self._assign_optional_positive_int("queue_length", queue_length)


class NonqueuedReceiverComSpec(ReceiverComSpec):
    """
    Complex type AR:NONQUEUED-RECEIVER-COM-SPEC
    Tag variants: 'NONQUEUED-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 alive_timeout: int | float | None = None,
                 enable_update: bool | None = None,
                 data_filter: DataFilter | None = None,
                 handle_data_status: bool | None = None,
                 handle_never_received: bool | None = None,
                 handle_timeout_type: ar_enum.HandleTimeout | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 timeout_substitution_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.alive_timeout: int | float | None = None  # .ALIVE-TIMEOUT
        self.enable_update: bool | None = None  # .ENABLE-UPDATE
        self.data_filter: DataFilter | None = None  # .FILTER
        self.handle_data_status: bool | None = None  # .HANDLE-DATA-STATUS
        self.handle_never_received: bool | None = None  # .HANDLE-NEVER-RECEIVED
        self.handle_timeout_type: ar_enum.HandleTimeout | None = None  # .HANDLE-TIMEOUT-TYPE
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.timeout_substitution_value: ValueSpecificationElement | None = None  # .TIMEOUT-SUBSTITUTION-VALUE
        self._assign_optional("alive_timeout", alive_timeout, float)
        self._assign_optional("enable_update", enable_update, bool)
        self._assign_optional_strict("data_filter", data_filter, DataFilter)
        self._assign_optional("handle_data_status", handle_data_status, bool)
        self._assign_optional("handle_never_received", handle_never_received, bool)
        self._assign_optional("handle_timeout_type", handle_timeout_type, ar_enum.HandleTimeout)
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional_strict("timeout_substitution_value", timeout_substitution_value, ValueSpecification)


class NvRequireComSpec(RequirePortComSpec):
    """
    Complex type AR:NV-REQUIRE-COM-SPEC
    Tag variants: 'NV-REQUIRE-COM-SPEC'
    """

    def __init__(self,
                 variable_ref: VariableDataPrototypeRef | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.variable_ref: VariableDataPrototypeRef | None = None  # .VARIABLE-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("variable_ref", variable_ref, VariableDataPrototypeRef)


class ParameterRequireComSpec(RequirePortComSpec):
    """
    Complex type AR:PARAMETER-REQUIRE-COM-SPEC
    Tag variants: 'PARAMETER-REQUIRE-COM-SPEC'
    """

    def __init__(self,
                 parameter_ref: ParameterDataPrototypeRef | str | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.parameter_ref: VariableDataPrototypeRef | None = None  # .PARAMETER-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("parameter_ref", parameter_ref, ParameterDataPrototypeRef)


class ModeSwitchReceiverComSpec(RequirePortComSpec):
    """
    Complex type AR:MODE-SWITCH-RECEIVER-COM-SPEC
    Tag variants: 'MODE-SWITCH-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 mode_group_ref: str | ModeDeclarationGroupPrototypeRef | None = None,
                 enhanced_mode_api: bool | None = None,
                 supports_async: bool | None = None,
                 ) -> None:
        super().__init__()
        self.mode_group_ref: ModeDeclarationGroupPrototypeRef | None = None  # .ENHANCED-MODE-API
        self.enhanced_mode_api: bool | None = None  # .MODE-GROUP-REF
        self.supports_async: bool | None = None  # .SUPPORTS-ASYNCHRONOUS-MODE-SWITCH
        self._assign_optional("mode_group_ref", mode_group_ref, ModeDeclarationGroupPrototypeRef)
        self._assign_optional("enhanced_mode_api", enhanced_mode_api, bool)
        self._assign_optional("supports_async", supports_async, bool)


class ClientComSpec(RequirePortComSpec):
    """
    Complex type AR:CLIENT-COM-SPEC
    Tag variants: 'CLIENT-COM-SPEC'
    """

    def __init__(self,
                 operation_ref: ClientServerOperationRef | None = None,
                 e2e_call_respone_timeout: float | int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None
                 ) -> None:
        super().__init__()
        # .CLIENT-INTENT not supported (Adaptive Platform)
        # .GETTER-REF not supported (Adaptive Platform)
        self.operation_ref: ClientServerOperationRef | None = None  # .OPERATION-REF
        self.e2e_call_respone_timeout: float | None = None  # .END-TO-END-CALL-RESPONSE-TIMEOUT
        # .SETTER-REF not supported (Adaptive Platform)
        # .TRANSFORMATION-COM-SPEC-PROPSS
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        # USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet supported under transformation_com_spec_props
        self._assign_optional("operation_ref", operation_ref, ClientServerOperationRef)
        self._assign_optional("e2e_call_respone_timeout", e2e_call_respone_timeout, float)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(props)
        else:
            raise TypeError("props must be of type EndToEndTransformationComSpecProps")


class PortPrototype(Identifiable):
    """
    Group AR:PORT-PROTOTYPE
    """
    # .CLIENT-SERVER-ANNOTATIONS not supported
    # .DELEGATED-PORT-ANNOTATION not supported
    # .IO-HW-ABSTRACTION-SERVER-ANNOTATIONS not supported
    # .MODE-PORT-ANNOTATIONS not supported
    # .NV-DATA-PORT-ANNOTATIONS not supported
    # .PARAMETER-PORT-ANNOTATIONS not supported
    # .PORT-PROTOTYPE-PROPS not supported
    # .SENDER-RECEIVER-ANNOTATIONS not supported
    # .TRIGGER-PORT-ANNOTATIONS not supported
    # .VARIATION-POINT not supported


class ProvidePortPrototype(PortPrototype):
    """
    Complex type AR:P-PORT-PROTOTYPE
    Tag variants: 'P-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.com_spec: list[ProvidePortComSpec] = []  # .PROVIDED-COM-SPECS
        self.port_interface_ref: PortInterfaceRef | None = None  # .PROVIDED-INTERFACE-TREF
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        if com_spec is not None:
            if isinstance(com_spec, ProvidePortComSpec):
                self.append_com_spec(com_spec)
            elif isinstance(com_spec, (list, tuple)):
                for com_spec_elem in com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("com_spec must be of a type derived from ProvidePortComSpec")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: ProvidePortComSpec) -> None:
        """
        Adds comspec to internal list of com-specs
        """
        if isinstance(com_spec, ProvidePortComSpec):
            self.com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of a type derived from ProvidePortComSpec")


class RequirePortPrototype(PortPrototype):
    """
    Complex type AR:R-PORT-PROTOTYPE
    Tag variants: 'R-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                 allow_unconnected: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.com_spec: list[RequirePortComSpec] = []  # .REQUIRED-COM-SPECS
        self.allow_unconnected: bool | None = None  # .MAY-BE-UNCONNECTED
        self.port_interface_ref: PortInterfaceRef | None = None  # .REQUIRED-INTERFACE-TREF
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        self._assign_optional("allow_unconnected", allow_unconnected, bool)
        if com_spec is not None:
            if isinstance(com_spec, RequirePortComSpec):
                self.append_com_spec(com_spec)
            elif isinstance(com_spec, (list, tuple)):
                for com_spec_elem in com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                msg = "com_spec: Needs be of a type derived from RequirePortComSpec."
                raise TypeError(msg + f" Got {str(type(com_spec))}")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: RequirePortComSpec) -> None:
        """
        Adds comspec to internal list of com-specs
        """
        if isinstance(com_spec, RequirePortComSpec):
            self.com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of type RequirePortComSpec")


class PRPortPrototype(PortPrototype):
    """
    Complex type AR:PR-PORT-PROTOTYPE
    Tag variants: 'PR-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE and AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 provided_com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                 required_com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.port_interface_ref: PortInterfaceRef | None = None
        self.provided_com_spec: list[ProvidePortComSpec] = []
        self.required_com_spec: list[RequirePortComSpec] = []
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        if provided_com_spec is not None:
            if isinstance(provided_com_spec, ProvidePortComSpec):
                self.append_com_spec(provided_com_spec)
            elif isinstance(required_com_spec, (list, tuple)):
                for com_spec_elem in provided_com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("provided_com_spec must be of a type derived from ProvidePortComSpec")
        if required_com_spec is not None:
            if isinstance(required_com_spec, RequirePortComSpec):
                self.append_com_spec(required_com_spec)
            elif isinstance(required_com_spec, (list, tuple)):
                for com_spec_elem in required_com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("required_com_spec must be of a type derived from RequirePortComSpec")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: ProvidePortComSpec | RequirePortComSpec) -> None:
        """
        Append com-spec to internal list(s) of com-specs
        """
        if isinstance(com_spec, ProvidePortComSpec):
            self.provided_com_spec.append(com_spec)
        elif isinstance(com_spec, RequirePortComSpec):
            self.required_com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of either type ProvidePortComSpec, RequirePortComSpec")


class SwComponentType(ARElement, Searchable):
    """
    Group AR:SW-COMPONENT-TYPE
    """

    def __init__(self,
                 name: str,
                 ports: PortPrototypeElement | list[PortPrototypeElement] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .SW-COMPONENT-DOCUMENTATIONS not supported
        # .CONSISTENCY-NEEDSS not supported
        self.ports: list[PortPrototypeElement] = []  # .PORTS
        # .PORT_GROUPS not yet supported
        # .SWC-MAPPING-CONSTRAINT-REFS not yet supported
        # .UNIT-GROUP-REFS not yet supported
        if ports is not None:
            if isinstance(ports, PortPrototype):
                self.append_port(ports)
            elif isinstance(ports, list):
                for port in ports:
                    self.append_port(port)
            else:
                msg_part_1 = "ports: Type must be ProvidePortPrototype, RequirePortPrototype, PRPortPrototype"
                msg_part_2 = " or a list of those types."
                raise TypeError(msg_part_1 + msg_part_2 + f" Got {str(type(ports))}")

    def append_port(self, port: PortPrototypeElement):
        """
        Adds port to internal list of ports
        """
        if isinstance(port, PortPrototype):
            port.parent = self
            self.ports.append(port)
        else:
            msg = "port type must be one of: ProvidePortPrototype, RequirePortPrototype, PRPortPrototype."
            raise TypeError(msg + f" Got {str(type(port))}")

    @property
    def provide_ports(self) -> Iterator[ProvidePortPrototype]:
        """
        P-PORTS
        """
        for port in self.ports:
            if isinstance(port, ProvidePortPrototype):
                yield port

    @property
    def require_ports(self) -> Iterator[RequirePortPrototype]:
        """
        R-PORTS
        """
        for port in self.ports:
            if isinstance(port, RequirePortPrototype):
                yield port

    @property
    def pr_ports(self) -> Iterator[PRPortPrototype]:
        """
        PR-PORTS
        """
        for port in self.ports:
            if isinstance(port, PRPortPrototype):
                yield port

    def find(self, ref: str) -> Identifiable | None:
        """
        Searches port names for a match in ref
        """
        parts = ref.partition('/')
        for elem in self.ports:
            if elem.name == parts[0]:
                return elem
        return None

    def create_p_port(self,
                      name: str,
                      port_interface: PortInterface | None = None,
                      com_spec: dict | list[tuple[str, dict]] | ProvidePortComSpec | list[ProvidePortComSpec] | None = None,  # noqa E501 pylint: disable=C0301
                      **kwargs) -> ProvidePortPrototype:
        """
        #convenience-method

        Creates a new provide-port and adds it to the internal list of ports
        """
        if com_spec is not None:
            if isinstance(com_spec, dict):
                com_spec = ProvidePortComSpec.make_from_port_interface(port_interface, **com_spec)
                assert com_spec is not None
            elif isinstance(com_spec, Iterable):
                processed = []
                unprocessed = {}
                for elem in com_spec:
                    if isinstance(elem, ProvidePortComSpec):
                        processed.append(elem)
                    elif isinstance(elem, tuple):
                        if not len(elem) == 2:
                            raise NotImplementedError("Com-spec element must be a 2-tuple containing [str, dict]. "
                                                      f"Got tuple with length {len(elem)}")
                        unprocessed[elem[0]] = elem[1]
                    else:
                        raise TypeError(f"Unsupported type in com-spec element: {str(type(elem))}")
                if len(unprocessed):
                    processed.extend(ProvidePortComSpec.make_from_port_interface(port_interface, **unprocessed))
                com_spec = processed
            else:
                com_spec = None  # Clear when not implemented
        port = ProvidePortPrototype(name, port_interface.ref(), com_spec, **kwargs)
        self.append_port(port)
        return port

    def create_provide_port(self,
                            name: str,
                            port_interface: PortInterface | None = None,
                            com_spec: dict | list[tuple[str, dict]] | ProvidePortComSpec | list[ProvidePortComSpec] | None = None,  # noqa E501 pylint: disable=C0301
                            **kwargs) -> ProvidePortPrototype:
        """
        #convenience-method

        Alias for create_p_port
        """
        return self.create_p_port(name, port_interface, com_spec, **kwargs)

    def create_r_port(self,
                      name: str,
                      port_interface: PortInterface,
                      com_spec: dict | list[dict] | RequirePortComSpec | list[RequirePortComSpec] | None = None,
                      allow_unconnected: bool | None = None,
                      **kwargs) -> RequirePortPrototype:
        """
        #convenience-method

        Creates a new require-port and adds it to the internal list of ports
        """
        if com_spec is not None:
            if isinstance(com_spec, dict):
                com_spec = RequirePortComSpec.make_from_port_interface(port_interface, **com_spec)
                assert com_spec is not None
            elif isinstance(com_spec, Iterable):
                processed = []
                unprocessed = {}
                for elem in com_spec:
                    if isinstance(elem, RequirePortComSpec):
                        processed.append(elem)
                    elif isinstance(elem, tuple):
                        if not len(elem) == 2:
                            raise NotImplementedError("Com-spec element must be a 2-tuple containing [str, dict]. "
                                                      f"Got tuple with length {len(elem)}")
                        unprocessed[elem[0]] = elem[1]
                    else:
                        raise TypeError(f"Unsupported type in com-spec element: {str(type(elem))}")
                if len(unprocessed):
                    processed.extend(RequirePortComSpec.make_from_port_interface(port_interface, **unprocessed))
                com_spec = processed
            else:
                com_spec = None  # Clear when not implemented
        port = RequirePortPrototype(name, port_interface.ref(), com_spec, allow_unconnected, **kwargs)
        self.append_port(port)
        return port

    def create_require_port(self,
                            name: str,
                            port_interface: PortInterface,
                            com_spec: dict | list[dict] | RequirePortComSpec | list[RequirePortComSpec] | None = None,
                            allow_unconnected: bool | None = None,
                            **kwargs) -> RequirePortPrototype:
        """
        #convenience-method

        Alias for create_r_port
        """
        return self.create_r_port(name, port_interface, com_spec, allow_unconnected, **kwargs)

    def create_pr_port(self,
                       name: str,
                       port_interface: PortInterface | None = None,
                       provided_com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                       required_com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                       **kwargs) -> PRPortPrototype:
        """
        #convenience-method

        Creates a new pr-port and adds it to the internal list of ports
        """
        if provided_com_spec is not None:
            if isinstance(provided_com_spec, dict):
                provided_com_spec = ProvidePortComSpec.make_from_port_interface(port_interface, **provided_com_spec)
                assert provided_com_spec is not None
        if required_com_spec is not None:
            if isinstance(required_com_spec, dict):
                required_com_spec = RequirePortComSpec.make_from_port_interface(port_interface, **required_com_spec)
                assert required_com_spec is not None
        port = PRPortPrototype(name, port_interface.ref(), provided_com_spec, required_com_spec, **kwargs)
        self.append_port(port)
        return port

    def find_r_port(self, port_name: str) -> RequirePortPrototype | PRPortPrototype | None:
        """
        Finds r-port by name
        """
        for port in self.ports:
            if isinstance(port, (RequirePortPrototype, PRPortPrototype)) and port.name == port_name:
                return port
        return None

    def find_p_port(self, port_name: str) -> ProvidePortPrototype | PRPortPrototype | None:
        """
        Finds p-port by name
        """
        for port in self.ports:
            if isinstance(port, (ProvidePortPrototype, PRPortPrototype)) and port.name == port_name:
                return port
        return None

    def get_data_element_in_port(self,
                                 port: RequirePortPrototype | ProvidePortPrototype,
                                 data_element_name: str | None = None,
                                 ) -> VariableDataPrototype | None:
        """
        Finds data element in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, SenderReceiverInterface):
            if not data_element_name:
                if not len(port_interface.data_elements) == 1:
                    msg = "data_element_name: Undefined value is not allowed when "\
                          "the port interface has more than one data element"
                    raise ValueError(msg)
                return port_interface.data_elements[0]
            else:
                for elem in port_interface.data_elements:
                    if elem.name == data_element_name:
                        return elem
        else:
            raise TypeError(f"Only SenderReceiverInterface is currently supported, got {str(type(port_interface))}")
        return None

    def get_operation_in_port(self,
                              port: PortPrototype,
                              operation_name: str
                              ) -> ClientServerOperation:
        """
        Finds client-server operation in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, ClientServerInterface):
            if not operation_name:
                if not len(port_interface.operations) == 1:
                    msg = "operation_name: Undefined value is not allowed when "\
                          "the port interface has more than one operation"
                    raise ValueError(msg)
                return port_interface.operations[0]
            else:
                for operation in port_interface.operations:
                    if operation.name == operation_name:
                        return operation
        else:
            raise TypeError(f"port: '{port.name}' doesn't reference port with ClientServerInterface")
        return None

    def get_mode_declaration_group_in_port(self,
                                           port: PortPrototype,
                                           ) -> ModeDeclarationGroupPrototype | None:
        """
        Finds mode declaration group in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, ModeSwitchInterface):
            return port_interface.mode_group
        else:
            raise TypeError(f"port: Expected a port referencing a ModeSwitchInterface, got {str(type(port_interface))}")
        return None


class AtomicSoftwareComponentType(SwComponentType):
    """
    Group AR:ATOMIC-SW-COMPONENT-TYPE
    """

    def __init__(self,
                 name: str,
                 internal_behavior: Union["SwcInternalBehavior", None] = None,
                 symbol_props: SymbolProps | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self._internal_behavior: SwcInternalBehavior | None = None
        self.symbol_props = None  # AR:SYMBOL-PROPS
        self._assign_optional_strict("_internal_behavior", internal_behavior, SwcInternalBehavior)
        self._assign_optional_strict("symbol_props", symbol_props, SymbolProps)

    @property
    def internal_behavior(self) -> Union["SwcInternalBehavior", None]:
        """
        Internal behavior getter
        """
        return self._internal_behavior

    @internal_behavior.setter
    def internal_behavior(self, value: Union["SwcInternalBehavior", None]):
        """
        Internal behavior setter
        """
        self._internal_behavior = value
        if value is not None:
            value.parent = self

    def create_internal_behavior(self, name: str = None, **kwargs) -> "SwcInternalBehavior":
        """
        Creates an empty internal behavior object and adds it to the component.
        If the name argument is left as None, a default name will be created based on the name of
        the software component

        #convenience-method
        """
        if name is None:
            name = self.name + "_InternalBehavior"
        self.internal_behavior = SwcInternalBehavior(name, **kwargs)
        self.internal_behavior.parent = self
        return self.internal_behavior


class ApplicationSoftwareComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:APPLICATION-SW-COMPONENT-TYPE
    Tag variants: 'APPLICATION-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE)


class SwComponentPrototype(Identifiable):
    """
    Complex type AR:SW-COMPONENT-PROTOTYPE
    Tag variants: 'SW-COMPONENT-PROTOTYPE'
    """

    def __init__(self,
                 name: str,
                 type_ref: SwComponentTypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: SwComponentTypeRef | None = None
        self._assign_optional_strict("type_ref", type_ref, SwComponentTypeRef)

    def ref(self) -> SwComponentPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwComponentPrototypeRef(ref_str)


class PortInCompositionTypeInstanceRef(ARObject):
    """
    Merge of complex types AR:P-PORT-IN-COMPOSITION-INSTANCE-REF
    and R-PORT-IN-COMPOSITION-INSTANCE-REF
    Tag variants: 'PROVIDER-IREF' | 'P-PORT-IN-COMPOSITION-INSTANCE-REF' |
                  'REQUESTER-IREF'| 'R-PORT-IN-COMPOSITION-INSTANCE-REF'
    """

    def __init__(self,
                 component_ref: SwComponentPrototypeRef | None = None,
                 port_ref: PortPrototypeRef | None = None,
                 ) -> None:
        super().__init__()
        self.component_ref: SwComponentPrototypeRef | None = None  # .CONTEXT-COMPONENT-REF
        self.port_ref: PortPrototypeRef | None = None  # .TARGET-P-PORT-REF or .TARGET-R-PORT-REF
        self._assign_optional_strict("component_ref", component_ref, SwComponentPrototypeRef)
        self._assign_optional_strict("port_ref", port_ref, PortPrototypeRef)


class SwConnector(Identifiable):
    """
    Group AR:SW-CONNECTOR
    """

    def __init__(self,
                 name: str,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MAPPING-REF not yet supported
        # .VARIATION-POINT not supported


class AssemblySwConnector(SwConnector):
    """
    Complex type AR:ASSEMBLY-SW-CONNECTOR
    Tag variants: 'ASSEMBLY-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 provide_port: PortInCompositionTypeInstanceRef | None = None,
                 require_port: PortInCompositionTypeInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.provide_port: PortInCompositionTypeInstanceRef | None = None  # .PROVIDER-IREF
        self.require_port: PortInCompositionTypeInstanceRef | None = None  # .REQUESTER-IREF
        self._assign_optional_strict("provide_port", provide_port, PortInCompositionTypeInstanceRef)
        self._assign_optional_strict("require_port", require_port, PortInCompositionTypeInstanceRef)


class DelegationSwConnector(SwConnector):
    """
    Complex type AR:DELEGATION-SW-CONNECTOR
    Tag variants: 'DELEGATION-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 inner_port: PortInCompositionTypeInstanceRef | None = None,
                 outer_port: PortPrototypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.inner_port: PortInCompositionTypeInstanceRef | None = None  # .INNER-PORT-IREF
        self.outer_port: PortPrototypeRef | None = None  # .OUTER-PORT-REF"
        self._assign_optional_strict("inner_port", inner_port, PortInCompositionTypeInstanceRef)
        self._assign_optional_strict("outer_port", outer_port, PortPrototypeRef)

    @property
    def xml_tag(self) -> str | None:
        """
        Returns a suitable XML-tag for inner_port_ref based on port reference type.
        Raises exception is port reference isn't set or if port-reference contains invalid value
        """
        if self.inner_port.port_ref is not None:
            if self.inner_port.port_ref.is_provide_port_ref:
                return "P-PORT-IN-COMPOSITION-INSTANCE-REF"
            if self.inner_port.port_ref.is_require_port_ref:
                return "R-PORT-IN-COMPOSITION-INSTANCE-REF"
        return None


class PassThroughSwConnector(SwConnector):
    """
    Complex type AR:PASS-THROUGH-SW-CONNECTOR
    Tag variants: 'PASS-THROUGH-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 provide_port: PortPrototypeRef | None = None,
                 require_port: PortPrototypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.provide_port: PortPrototypeRef | None = None  # .PROVIDED-OUTER-PORT-REF
        self.require_port: PortPrototypeRef | None = None  # .REQUIRED-OUTER-PORT-REF
        # .SERVICE-INTERFACE-ELEMENT-MAPPING-REFS not yet supported
        self._assign_optional_strict("provide_port", provide_port, PortPrototypeRef)
        self._assign_optional_strict("require_port", require_port, PortPrototypeRef)


class CompositionSwComponentType(SwComponentType, Searchable):
    """
    Complex type AR:COMPOSITION-SW-COMPONENT-TYPE
    Tag variants: 'COMPOSITION-SW-COMPONENT-TYPE'
    """

    def __init__(self,
                 name: str,
                 components: SwComponentPrototype | list[SwComponentPrototype] | None = None,
                 connectors: SwConnectorElement | list[SwConnectorElement] = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.components: list[SwComponentPrototype] = []  # .COMPONENTS
        self.connectors: list[SwConnectorElement] = []  # .CONNECTORS
        # .CONSTANT-VALUE-MAPPING-REFS not yet supported
        # .DATA-TYPE-MAPPING-REFS not yet supported
        # .INSTANTIATION-RTE-EVENT-PROPSS not yet supported
        if components is not None:
            if isinstance(components, SwComponentPrototype):
                self.append_component(components)
            elif isinstance(components, list):
                for component in components:
                    self.append_component(component)
            else:
                raise TypeError(f"components: Invalid type '{str(type(components))}'")
        if connectors is not None:
            if isinstance(connectors, (AssemblySwConnector, DelegationSwConnector, PassThroughSwConnector)):
                self.append_connector(connectors)
            elif isinstance(connectors, list):
                for connector in connectors:
                    self.append_connector(connector)
            else:
                raise TypeError(f"components: Invalid type '{str(type(connectors))}'")

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.COMPOSITION_SW_COMPONENT_TYPE)

    def append_component(self, component: SwComponentPrototype) -> None:
        """
        Appends components prototype to internal list
        """
        if isinstance(component, SwComponentPrototype):
            component.parent = self
            self.components.append(component)
        else:
            raise TypeError(f"component: Invalid type {(str(type(component)))}")

    def append_connector(self, connector: SwConnectorElement) -> None:
        """
        Appends components prototype to internal list
        """
        if isinstance(connector, (AssemblySwConnector, DelegationSwConnector, PassThroughSwConnector)):
            connector.parent = self
            self.connectors.append(connector)
        else:
            raise TypeError(f"connector: Invalid type {(str(type(connector)))}")

    def find(self, ref: str) -> Identifiable | None:
        """
        Searches components and connectors for a match in ref
        """
        parts = ref.partition('/')
        for elem in self.components:
            if elem.name == parts[0]:
                return elem
        for elem in self.connectors:
            if elem.name == parts[0]:
                return elem
        return super().find(ref)

    def create_component_prototype(self,
                                   component_type: SwComponentType,
                                   name: str = None,
                                   **kwargs) -> SwComponentPrototype:
        """
        #convenience-method

        Creates a new SwComponentPrototype object from the source SwComponentType and adds it
        to the internal list of components.
        By default the created SwComponentPrototype will have the same name as the source
        SwComponentType. The optional name argument can be used to give it a different name.
        """
        if name is None:
            name = component_type.name
        component_prototype = SwComponentPrototype(name, component_type.ref(), **kwargs)
        self.append_component(component_prototype)
        return component_prototype

    def create_connector(self,
                         port_ref1: str,
                         port_ref2: str,
                         workspace: Searchable) -> None:
        """
        #convenience-method

        Creates a connector between two ports in the composition
        port_ref1 and port_ref2 can be of any of these formats:
        * 'component_name/port_name' - references a port of an inner component
        * 'port_name' - references a port in the composition itself

        Depending on the combination of ports this function automatically determines
        the type of connector to create which can be one of:
        * AssemblySwConnector
        * DelegationSwConnector
        * PassThroughSwConnector
        """
        assert workspace is not None
        port1, component1 = self._analyze_port_ref(workspace, port_ref1)
        port2, component2 = self._analyze_port_ref(workspace, port_ref2)

        if component1 is None and component2 is None:
            return self._create_pass_through_connector(port1, port2)
        elif component1 is None:
            return self._create_delegation_connector(component2, port2, port1)
        elif component2 is None:
            return self._create_delegation_connector(component1, port1, port2)
        else:
            requester_component: SwComponentPrototype = None
            provider_component: SwComponentPrototype = None
            provide_port: PortPrototype = None
            require_port: PortPrototype = None
            if isinstance(port1, RequirePortPrototype) and isinstance(port2, ProvidePortPrototype):
                requester_component, provider_component = component1, component2
                require_port, provide_port = port1, port2
            elif isinstance(port1, ProvidePortPrototype) and isinstance(port2, RequirePortPrototype):
                requester_component, provider_component = component2, component1
                require_port, provide_port = port2, port1
            elif isinstance(port1, RequirePortPrototype) and isinstance(port2, RequirePortPrototype):
                raise ValueError('cannot create assembly connector between two require-ports')
            else:
                raise ValueError('cannot create assembly connector between two provide-ports')
            return self._create_assembly_connector(provider_component, provide_port,
                                                   requester_component, require_port)

    def _analyze_port_ref(self,
                          workspace: Searchable,
                          port_ref: str) -> tuple[PortPrototype, Union[SwComponentPrototype, None]]:
        """
        Analyze port reference string and attempts to determine what component
        and port are referenced.
        """
        port: PortPrototype | None = None
        port_name: str | None = None
        parts = split_ref(port_ref)
        if len(parts) > 1:
            if len(parts) == 2:  # Format is 'component_name/port_name'?
                port_name = parts[1]
                for elem in self.components:
                    if elem.name == parts[0]:
                        component = workspace.find(str(elem.type_ref))
                        if component is None:
                            raise ValueError(f"Invalid reference: {elem.type_ref}")
                        if not isinstance(component, SwComponentType):
                            msg = f"Reference is not a valid SwComponentType: {elem.type_ref}"
                            raise ValueError(msg)
                        port = component.find(port_name)
                        if (port is None) or (not isinstance(port, PortPrototype)):
                            msg = f"Component '{component.name}' does not seem to have a port with name '{port_name}'"
                            raise ValueError(msg)
                        return port, elem
            else:
                raise ValueError(f"Invalid format: '{port_ref}'")
        else:  # Format is 'port_name'
            # Leaving component as None here is a reminder to the caller to create a delegation or a
            # pass-through connector
            port_name = parts[0]
            port = self.find(port_name)
            if (port is None) or (not isinstance(port, PortPrototype)):
                msg = f"Component '{self.name}' does not seem to have a port with name '{port_name}'"
                raise ValueError(msg)
        return port, None

    def _create_assembly_connector(self,
                                   provider_component: SwComponentPrototype,
                                   provide_port: PortPrototype,
                                   requester_component: SwComponentPrototype,
                                   require_port: PortPrototype) -> AssemblySwConnector:
        """
        Internal helper function for creating assembly connector
        """
        connector_name = '_'.join([provider_component.name,
                                   provide_port.name,
                                   requester_component.name,
                                   require_port.name])
        provider_iref = PortInCompositionTypeInstanceRef(provider_component.ref(), provide_port.ref())
        requester_iref = PortInCompositionTypeInstanceRef(requester_component.ref(), require_port.ref())
        connector = AssemblySwConnector(connector_name, provider_iref, requester_iref)
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.append_connector(connector)
        return connector

    def _create_delegation_connector(self,
                                     inner_component: SwComponentPrototype,
                                     inner_port: PortPrototype,
                                     outer_port: PortPrototype) -> DelegationSwConnector:
        if isinstance(outer_port, ProvidePortPrototype):
            connector_name = '_'.join([inner_component.name, inner_port.name, outer_port.name])
        else:
            connector_name = '_'.join([outer_port.name, inner_component.name, inner_port.name])
        inner_port_iref = PortInCompositionTypeInstanceRef(inner_component.ref(), inner_port.ref())
        connector = DelegationSwConnector(connector_name, inner_port_iref, outer_port.ref())
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.connectors.append(connector)
        return connector

    def _create_pass_through_connector(self,
                                       provide_port: ProvidePortPrototype,
                                       require_port: RequirePortPrototype) -> PassThroughSwConnector:
        connector_name = '_'.join([provide_port.name, require_port.name])
        connector = PassThroughSwConnector(connector_name, provide_port.ref(), require_port.ref())
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.connectors.append(connector)
        return connector


class ModeGroupInAtomicSwcInstanceRef(ARObject):
    """
    Group AR:MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
    Abstract base class
    """


class POperationInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:P-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'OPERATION-IREF'
    """

    def __init__(self,
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_provided_operation: ClientServerOperationRef | str | None = None,
                 ) -> None:
        # .CONTEXT-P-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractProvidedPortPrototypeRef | None = None
        # .TARGET-PROVIDED-OPERATION-REF
        self.target_provided_operation: ClientServerOperationRef | None = None
        self._assign_optional("context_port", context_port, AbstractProvidedPortPrototypeRef)
        self._assign_optional("target_provided_operation", target_provided_operation, ClientServerOperationRef)


class PModeGroupInAtomicSwcInstanceRef(ModeGroupInAtomicSwcInstanceRef):
    """
    Complex type AR:P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF' | 'MODE-GROUP-IREF' |
                  'SWC-MODE-GROUP-IREF'
    """

    def __init__(self,
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_mode_group: ModeDeclarationGroupPrototypeRef | str | None = None,
                 ) -> None:
        # .CONTEXT-P-PORT-REF
        self.context_port: AbstractProvidedPortPrototypeRef | None = None
        # .TARGET-MODE-GROUP-REF
        self.target_mode_group: ModeDeclarationGroupPrototypeRef | None = None

        self._assign_optional("context_port", context_port, AbstractProvidedPortPrototypeRef)
        self._assign_optional("target_mode_group",
                              target_mode_group,
                              ModeDeclarationGroupPrototypeRef)


class PTriggerInAtomicSwcTypeInstanceRef(ARObject):
    """
    Complex type AR:P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF' | 'SWC-TRIGGER-IREF' |
                  'TRIGGER-IREF'
    """

    def __init__(self,
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_trigger: TriggerRef | str | None = None,
                 ) -> None:
        # .CONTEXT-P-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractProvidedPortPrototypeRef | None = None
        # .TARGET-TRIGGER-REF
        self.target_trigger: TriggerRef | None = None

        self._assign_optional("context_port", context_port, AbstractProvidedPortPrototypeRef)
        self._assign_optional("target_trigger", target_trigger, TriggerRef)


class ROperationInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'OPERATION-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_required_operation: ClientServerOperationRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-REQUIRED-OPERATION-REF
        self.target_required_operation: ClientServerOperationRef | None = None
        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_required_operation", target_required_operation, ClientServerOperationRef)


class RModeInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-MODE-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'DISABLED-MODE-IREF' | 'MODE-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | None = None,
                 target_mode_declaration: ModeDeclarationRef | None = None,
                 ) -> None:
        # .CONTEXT-PORT-REF
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | None = None
        # .TARGET-MODE-DECLARATION-REF
        self.target_mode_declaration: ModeDeclarationRef | None = None
        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("context_mode_declaration_group_prototype",
                              context_mode_declaration_group_prototype,
                              ModeDeclarationGroupPrototypeRef)
        self._assign_optional("target_mode_declaration", target_mode_declaration, ModeDeclarationRef)


class RModeGroupInAtomicSwcInstanceRef(ModeGroupInAtomicSwcInstanceRef):
    """
    Complex type AR:R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_mode_group: ModeDeclarationGroupPrototypeRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-MODE-GROUP-REF
        self.target_mode_group: ModeDeclarationGroupPrototypeRef | None = None

        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_mode_group", target_mode_group, ModeDeclarationGroupPrototypeRef)


class RVariableInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-VARIABLE-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'DATA-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_data_element: VariableDataPrototypeRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-DATA-ELEMENT-REF
        self.target_data_element: VariableDataPrototypeRef | None = None

        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_data_element", target_data_element, VariableDataPrototypeRef)


class RTriggerInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-TRIGGER-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'TRIGGER-IREF' | 'REQUIRED-TRIGGER-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_trigger: TriggerRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-TRIGGER-REF
        self.target_trigger: TriggerRef | None = None

        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_trigger", target_trigger, TriggerRef)


# --- SWC internal behavior elements


class ArVariableInImplementationDataInstanceRef(ARObject):
    """
    Complex type AR:AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
    Tag variants: 'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE' | 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
    """

    ContextDataPrototypeArgType = Union[AbstractImplementationDataTypeElementRef,
                                        list[AbstractImplementationDataTypeElementRef]]

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | None = None,
                 root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None,
                 context_data_prototype_refs: ContextDataPrototypeArgType | None = None,
                 target_data_prototype_ref: AbstractImplementationDataTypeElementRef | None = None
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROOT-VARIABLE-DATA-PROTOTYPE-REF
        self.root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REFS
        self.context_data_prototype_refs: list[AbstractImplementationDataTypeElementRef] = []
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype_ref: AbstractImplementationDataTypeElementRef | None = None

        self._assign_optional_strict("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional_strict("root_variable_data_prototype_ref",
                                     root_variable_data_prototype_ref,
                                     VariableDataPrototypeRef)
        self._assign_optional_strict("target_data_prototype_ref",
                                     target_data_prototype_ref,
                                     AbstractImplementationDataTypeElementRef)
        if context_data_prototype_refs is not None:
            if isinstance(context_data_prototype_refs, AbstractImplementationDataTypeElementRef):
                self.append_context_data_protype_ref(context_data_prototype_refs)
            elif isinstance(context_data_prototype_refs, list):
                for context_data_prototype_ref in context_data_prototype_refs:
                    self.append_context_data_protype_ref(context_data_prototype_ref)

    def append_context_data_protype_ref(self, context_data_prototype_ref: AbstractImplementationDataTypeElementRef):
        """
        Appends datatype reference to internal list of context data type references
        """
        if isinstance(context_data_prototype_ref, AbstractImplementationDataTypeElementRef):
            self.context_data_prototype_refs.append(context_data_prototype_ref)
        else:
            raise TypeError("context_data_prototype_ref must be of type AbstractImplementationDataTypeElementRef")


class VariableInAtomicSWCTypeInstanceRef(ARObject):
    """
    Complex type AR:VARIABLE-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'AUTOSAR-VARIABLE-IREF'
    """

    ContextDataPrototypeArgType = Union[ApplicationCompositeElementDataPrototypeRef,
                                        list[ApplicationCompositeElementDataPrototypeRef]]

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | None = None,
                 root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None,
                 context_data_prototype_refs: ContextDataPrototypeArgType | None = None,
                 target_data_prototype_ref: DataPrototypeRef | None = None,
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROOT-VARIABLE-DATA-PROTOTYPE-REF
        self.root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REF
        self.context_data_prototype_refs: list[ApplicationCompositeElementDataPrototypeRef] = []
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype_ref: DataPrototypeRef | None = None

        self._assign_optional("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional("root_variable_data_prototype_ref",
                              root_variable_data_prototype_ref, VariableDataPrototypeRef)
        self._assign_optional("target_data_prototype_ref", target_data_prototype_ref, DataPrototypeRef)
        if context_data_prototype_refs is not None:
            if isinstance(context_data_prototype_refs, ApplicationCompositeElementDataPrototypeRef):
                self.append_context_data_protype_ref(context_data_prototype_refs)
            elif isinstance(context_data_prototype_refs, list):
                for context_data_prototype_ref in context_data_prototype_refs:
                    self.append_context_data_protype_ref(context_data_prototype_ref)

    def append_context_data_protype_ref(self, context_data_prototype_ref: ApplicationCompositeElementDataPrototypeRef):
        """
        Appends datatype reference to internal list of context data type references
        """
        if isinstance(context_data_prototype_ref, ApplicationCompositeElementDataPrototypeRef):
            self.context_data_prototype_refs.append(context_data_prototype_ref)
        else:
            raise TypeError("context_data_prototype_ref must be of type AbstractImplementationDataTypeElementRef")


class AutosarVariableRef(ARObject):
    """
    Complex type AR:AUTOSAR-VARIABLE-REF
    Tag variants: 'VARIABLE-INSTANCE' | 'NV-RAM-BLOCK-ELEMENT' | 'READ-NV-DATA' |
                  'WRITTEN-NV-DATA' | 'WRITTEN-READ-NV-DATA' | 'USED-DATA-ELEMENT' |
                  'AUTOSAR-VARIABLE' | 'ACCESSED-VARIABLE'
    """

    def __init__(self,
                 ar_variable_in_impl_datatype: ArVariableInImplementationDataInstanceRef | None = None,
                 ar_variable_iref: VariableInAtomicSWCTypeInstanceRef | None = None,
                 local_variable_ref: VariableDataPrototypeRef | None = None
                 ) -> None:
        super().__init__()
        # .AUTOSAR-VARIABLE-IN-IMPL-DATATYPE
        self.ar_variable_in_impl_datatype: ArVariableInImplementationDataInstanceRef | None = None
        # .AUTOSAR-VARIABLE-IREF
        self.ar_variable_iref: VariableInAtomicSWCTypeInstanceRef | None = None
        # .LOCAL-VARIABLE-REF
        self.local_variable_ref: VariableDataPrototypeRef | None = None
        self._assign_optional_strict("ar_variable_in_impl_datatype",
                                     ar_variable_in_impl_datatype,
                                     ArVariableInImplementationDataInstanceRef)
        self._assign_optional_strict("ar_variable_iref",
                                     ar_variable_iref,
                                     VariableInAtomicSWCTypeInstanceRef)
        self._assign_optional_strict("local_variable_ref",
                                     local_variable_ref,
                                     VariableDataPrototypeRef)


class VariableAccess(Identifiable):
    """
    Complex type AR:VARIABLE-ACCESS
    Tag variants: 'REPLACE-WITH' | 'VARIABLE-ACCESS'
    """

    def __init__(self,
                 name: str,
                 accessed_variable: AutosarVariableRef | None = None,
                 scope: ar_enum.VariableAccessScope | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ACCESSED-VARIABLE
        self.accessed_variable: AutosarVariableRef | None = None
        # .SCOPE
        self.scope: ar_enum.VariableAccessScope | None = None

        # .VARIATION-POINT not supported
        self._assign_optional_strict("accessed_variable", accessed_variable, AutosarVariableRef)
        self._assign_optional("scope", scope, ar_enum.VariableAccessScope)

    @classmethod
    def make_from_port(cls,
                       name: str,
                       port_prototype_ref: PortPrototypeRef,
                       target_data_prototype_ref: DataPrototypeRef,
                       **kwargs) -> "VariableAccess":
        """
        #convenience-method

        Simplified creation method for use with VariableInAtomicSWCTypeInstanceRef
        """
        variable_iref = VariableInAtomicSWCTypeInstanceRef(port_prototype_ref=port_prototype_ref,
                                                           target_data_prototype_ref=target_data_prototype_ref)
        autosar_variable_ref = AutosarVariableRef(ar_variable_iref=variable_iref)
        return cls(name, autosar_variable_ref, **kwargs)

    @classmethod
    def make_from_port_with_args(cls,
                                 name: str,
                                 port_prototype_ref: PortPrototypeRef,
                                 target_data_prototype_ref: DataPrototypeRef,
                                 args: dict[str, Any] | None) -> "VariableAccess":
        """
        #convenience-method

        Same as make_from_port but allows extra arguments to be given as an optional dictionary
        """
        if args is not None:
            return cls.make_from_port(name, port_prototype_ref, target_data_prototype_ref, **args)
        else:
            return cls.make_from_port(name, port_prototype_ref, target_data_prototype_ref)

    def ref(self) -> VariableAccessRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return VariableAccessRef(ref_str)


class SwcImplementation(Implementation):
    """
    Complex type AR:SWC-IMPLEMENTATION
    Tag variants: 'SWC-IMPLEMENTATION'
    """

    def __init__(self,
                 name: str,
                 behavior_ref: SwcInternalBehaviorRef | None = None,
                 code_descriptors: Code | list[Code] | None = None,
                 required_rte_vendor: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, code_descriptors, **kwargs)
        self.behavior_ref: SwcInternalBehaviorRef | None = None
        # .PER-INSTANCE-MEMORY-SIZES not yet supported
        self.required_rte_vendor: str | None = None
        self._assign_optional("behavior_ref", behavior_ref, SwcInternalBehaviorRef)
        self._assign_optional_strict("required_rte_vendor", required_rte_vendor, str)

    def ref(self) -> SwcImplementationRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwcImplementationRef(ref_str)


class ExecutableEntityActivationReason(ImplementationProps):
    """
    Complex type AR:EXECUTABLE-ENTITY-ACTIVATION-REASON
    Tag variants: 'EXECUTABLE-ENTITY-ACTIVATION-REASON'
    """

    def __init__(self,
                 name: str,
                 bit_position: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.bit_position: int | None = None
        self._assign_optional_positive_int("bit_position", bit_position)


class ExclusiveAreaRefConditional(ARObject):
    """
    Complex type AR:EXCLUSIVE-AREA-REF-CONDITIONAL
    Tag variants: 'EXCLUSIVE-AREA-REF-CONDITIONAL'
    """

    def __init__(self,
                 exclusive_area: ExclusiveAreaRef | str | None = None) -> None:
        self.exclusive_area: ExclusiveAreaRef | None = None  # .EXCLUSIVE-AREA-REF
        self._assign_optional("exclusive_area", exclusive_area, ExclusiveAreaRef)


ActivationReasonArgumentType = ExecutableEntityActivationReason | list[ExecutableEntityActivationReason] | None
CanEnterLeaveArgumentType = Union[ExclusiveAreaRefConditional,
                                  list[ExclusiveAreaRefConditional],
                                  ExclusiveAreaRef,
                                  list[ExclusiveAreaRef],
                                  str,
                                  list[str],
                                  None]

ExclusiveAreaNestingOrderArgumentType = ExclusiveAreaNestingOrderRef | list[ExclusiveAreaNestingOrderRef] | None
RunsInsidesArgumentType = Union[ExclusiveAreaRefConditional,
                                list[ExclusiveAreaRefConditional],
                                ExclusiveAreaRef,
                                list[ExclusiveAreaRef],
                                str,
                                None]

ExclusiveAreaElementArgumentType = ExclusiveAreaRefConditional | ExclusiveAreaRef | str


class ExecutableEntity(Identifiable):
    """
    Group AR:EXECUTABLE-ENTITY
    """

    def __init__(self,
                 name: str,
                 activation_reasons: ActivationReasonArgumentType = None,
                 can_enter_leave: CanEnterLeaveArgumentType = None,
                 exclusive_area_nesting_order: ExclusiveAreaNestingOrderArgumentType = None,
                 minimum_start_interval: int | float | None = None,
                 reentrancy_level: ar_enum.ReentrancyLevel | None = None,
                 runs_insides: RunsInsidesArgumentType = None,
                 sw_addr_method: str | SwAddrMethodRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.activation_reasons: list[ExecutableEntityActivationReason] = []  # .ACTIVATION-REASONS
        # .CAN-ENTERS or CAN-ENTER-EXCLUSIVE-AREA-REFS depending on schema version
        self.can_enter_leave: list[ExclusiveAreaRefConditional] = []
        self.exclusive_area_nesting_order: list[ExclusiveAreaNestingOrderRef] = []  # .EXCLUSIVE-AREA-NESTING-ORDER-REFS
        self.minimum_start_interval: float | None = None  # .MINIMUM-START-INTERVAL
        self.reentrancy_level: ar_enum.ReentrancyLevel | None = None  # .REENTRANCY-LEVEL
        # .RUNS-INSIDES or .RUNS-INSIDE-EXCLUSIVE-AREA-REFS depending on schema version
        self.runs_insides: list[ExclusiveAreaRefConditional] = []
        self.sw_addr_method: str | SwAddrMethodRef | None = None  # .SW-ADDR-METHOD-REF

        if activation_reasons is not None:
            if isinstance(activation_reasons, list):
                for activation_reason in activation_reasons:
                    self.append_activation_reason(activation_reason)
            else:
                self.append_activation_reason(activation_reasons)
        if can_enter_leave is not None:
            if isinstance(can_enter_leave, list):
                for elem in can_enter_leave:
                    self.append_can_enter_leave(elem)
            else:
                self.append_can_enter_leave(can_enter_leave)
        if exclusive_area_nesting_order is not None:
            if isinstance(exclusive_area_nesting_order, ExclusiveAreaNestingOrderRef):
                self.append_exclusive_area_nesting_order(exclusive_area_nesting_order)
            elif isinstance(exclusive_area_nesting_order, list):
                for elem in exclusive_area_nesting_order:
                    self.append_exclusive_area_nesting_order(elem)
        self._assign_optional("minimum_start_interval", minimum_start_interval, float)
        self._assign_optional("reentrancy_level", reentrancy_level, ar_enum.ReentrancyLevel)
        if runs_insides is not None:
            if isinstance(runs_insides, list):
                for elem in runs_insides:
                    self.append_runs_insides(elem)
            else:
                self.append_runs_insides(runs_insides)
        self._assign_optional('sw_addr_method', sw_addr_method, SwAddrMethodRef)

    def append_activation_reason(self, activation_reason: ExecutableEntityActivationReason) -> None:
        """
        Appends activation_reason to internal list of activation reasons
        """
        if isinstance(activation_reason, ExecutableEntityActivationReason):
            self.activation_reasons.append(activation_reason)
        else:
            raise TypeError("activation_reason must be of type ExecutableEntityActivationReason")

    def append_can_enter_leave(self, value: ExclusiveAreaElementArgumentType) -> None:
        """
        The executable entity can enter/leave the referenced exclusive area through explicit API calls
        """
        if isinstance(value, ExclusiveAreaRefConditional):
            self.can_enter_leave.append(value)
        elif isinstance(value, (ExclusiveAreaRef, str)):
            self.can_enter_leave.append(ExclusiveAreaRefConditional(value))
        else:
            raise TypeError("value: Invalid type. Expected one of ExclusiveAreaRefConditional, ExclusiveAreaRef, str.")

    def append_exclusive_area_nesting_order(self, exclusive_area_nesting_order: ExclusiveAreaNestingOrderRef) -> None:
        """
        Appends exclusive area reference to internal list of nesting orders
        """
        if isinstance(exclusive_area_nesting_order, ExclusiveAreaNestingOrderRef):
            self.exclusive_area_nesting_order.append(exclusive_area_nesting_order)
        else:
            raise TypeError("exclusive_area_nesting_order must be of type ExclusiveAreaRefConditional")

    def append_runs_insides(self, value: ExclusiveAreaElementArgumentType) -> None:
        """
        The executable entity runs completely inside the referenced exclusive area
        """
        if isinstance(value, ExclusiveAreaRefConditional):
            self.runs_insides.append(value)
        elif isinstance(value, (ExclusiveAreaRef, str)):
            self.runs_insides.append(ExclusiveAreaRefConditional(value))
        else:
            raise TypeError("value: Invalid type. Expected one of ExclusiveAreaRefConditional, ExclusiveAreaRef, str.")


class RunnableEntityArgument(ARObject):
    """
    Complex type AR:RUNNABLE-ENTITY-ARGUMENT
    Tag variants: 'RUNNABLE-ENTITY-ARGUMENT'
    """

    def __init__(self, symbol: str | None = None) -> None:
        super().__init__()
        # .SYMBOL
        self.symbol: str | None = None
        self._assign_optional_strict("symbol", symbol, str)


class AbstractAccessPoint(Identifiable):
    """
    Group AR:ABSTRACT-ACCESS-POINT
    """

    def __init__(self,
                 name: str,
                 return_value_provision: ar_enum.RteApiReturnValueProvision | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .RETURN-VALUE-PROVISION
        self.return_value_provision: ar_enum.RteApiReturnValueProvision | None = None

        self._assign_optional("return_value_provision", return_value_provision, ar_enum.RteApiReturnValueProvision)


class ServerCallPoint(AbstractAccessPoint):
    """
    Group AR:SERVER-CALL-POINT
    """

    def __init__(self,
                 name: str,
                 operation: ROperationInAtomicSwcInstanceRef | None = None,
                 timeout: int | float | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .OPERATION-IREF
        self.operation: ROperationInAtomicSwcInstanceRef | None = None
        # .TIMEOUT
        self.timeout: float | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("operation", operation, ROperationInAtomicSwcInstanceRef)
        self._assign_optional('timeout', timeout, float)


class AsynchronousServerCallPoint(ServerCallPoint):
    """
    Complex type: AR:ASYNCHRONOUS-SERVER-CALL-POINT
    Tag variants: 'ASYNCHRONOUS-SERVER-CALL-POINT'
    Use constructor from base class
    """

    def ref(self) -> AsynchronousServerCallPointRef:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else AsynchronousServerCallPointRef(ref_str)


class AsynchronousServerCallResultPoint(AbstractAccessPoint):
    """
    Complex type: AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT
    Tag variants: 'ASYNCHRONOUS-SERVER-CALL-RESULT-POINT'
    """

    def __init__(self,
                 name: str,
                 async_server_call_point: AsynchronousServerCallPointRef | str | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .ASYNCHRONOUS-SERVER-CALL-POINT-REF
        self.async_server_call_point: AsynchronousServerCallPointRef | None = None

        self._assign_optional("async_server_call_point", async_server_call_point, AsynchronousServerCallPointRef)

    def ref(self) -> AsynchronousServerCallResultPointRef:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else AsynchronousServerCallResultPointRef(ref_str)


class SynchronousServerCallPoint(ServerCallPoint):
    """
    Complex type: AR:SYNCHRONOUS-SERVER-CALL-POINT
    Tag variants: 'SYNCHRONOUS-SERVER-CALL-POINT'
    """

    def __init__(self,
                 name: str,
                 called_from_within_exclusive_area: ExclusiveAreaNestingOrderRef | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .CALLED-FROM-WITHIN-EXCLUSIVE-AREA-REF
        self.called_from_within_exclusive_area: ExclusiveAreaNestingOrderRef | None = None

        self._assign_optional("called_from_within_exclusive_area",
                              called_from_within_exclusive_area,
                              ExclusiveAreaNestingOrderRef)


class ExternalTriggeringPointIdent(AbstractAccessPoint):
    """
    Complex type AR:EXTERNAL-TRIGGERING-POINT-IDENT
    Tag variants: 'IDENT'
    Use constructor from base class
    """


class ExternalTriggeringPoint(ARObject):
    """
    Complex type AR:EXTERNAL-TRIGGERING-POINT
    Tag variants: 'EXTERNAL-TRIGGERING-POINT'
    """

    def __init__(self,
                 ident: ExternalTriggeringPointIdent | None = None,
                 trigger: PTriggerInAtomicSwcTypeInstanceRef | None = None
                 ) -> None:
        super().__init__()
        # .IDENT
        self.ident: ExternalTriggeringPointIdent | None = None
        # .TRIGGER-IREF
        self.trigger: PTriggerInAtomicSwcTypeInstanceRef | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("ident", ident, ExternalTriggeringPointIdent)
        self._assign_optional_strict("trigger", trigger, PTriggerInAtomicSwcTypeInstanceRef)


class InternalTriggeringPoint(AbstractAccessPoint):
    """
    Complex type AR:INTERNAL-TRIGGERING-POINT
    Tag variants: 'INTERNAL-TRIGGERING-POINT'
    """

    def __init__(self, name: str, sw_impl_policy: ar_enum.SwImplPolicy | None = None, **kwargs):
        super().__init__(name, **kwargs)

        # .SW-IMPL-POLICY
        self.sw_impl_policy: ar_enum.SwImplPolicy | None = None
        # .VARIATION-POINT

        self._assign_optional("sw_impl_policy", sw_impl_policy, ar_enum.SwImplPolicy)


class ModeAccessPointIdent(AbstractAccessPoint):
    """
    Complex type AR:MODE-ACCESS-POINT-IDENT
    Tag variants: 'IDENT'
    Use constructor from base class
    """

    @classmethod
    def make_with_args(cls, name: str, args: dict[str, Any] | None) -> "ModeAccessPointIdent":
        """
        #convenienct-method

        Enables creation of ModeAccessPointIdent by giving extra arguments as an optional dictionary
        """
        return cls(name, **args) if args is not None else cls(name)


class ModeAccessPoint(ARObject):
    """
    Complex type AR:MODE-ACCESS-POINT
    Tag variants: 'MODE-ACCESS-POINT'
    """

    def __init__(self,
                 ident: ModeAccessPointIdent | None = None,
                 mode_group: PModeGroupInAtomicSwcInstanceRef | RModeGroupInAtomicSwcInstanceRef | None = None
                 ) -> None:
        super().__init__()
        # .IDENT
        self.ident: ModeAccessPointIdent | None = None
        # .MODE-GROUP-IREF
        self.mode_group: PModeGroupInAtomicSwcInstanceRef | RModeGroupInAtomicSwcInstanceRef | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("ident", ident, ModeAccessPointIdent)
        if mode_group is not None:
            if isinstance(mode_group, ModeGroupInAtomicSwcInstanceRef):
                self.mode_group = mode_group
            else:
                msg_part_1 = "Invalid type for parameter 'mode_group'. "
                msg_part_2 = "Expected types PModeGroupInAtomicSwcInstanceRef or RModeGroupInAtomicSwcInstanceRef, "
                msg_part_3 = f"got {str(type(mode_group))}"
                raise TypeError(msg_part_1 + msg_part_2 + msg_part_3)


class ModeSwitchPoint(AbstractAccessPoint):
    """
    Complex Type AR:MODE-SWITCH-POINT
    Tag variants: 'MODE-SWITCH-POINT'
    """

    def __init__(self,
                 name: str,
                 mode_group: PModeGroupInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MODE-GROUP-IREF
        self.mode_group: PModeGroupInAtomicSwcInstanceRef | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("mode_group", mode_group, PModeGroupInAtomicSwcInstanceRef)

    def ref(self) -> ModeSwitchPointRef:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeSwitchPointRef(ref_str)


class ParameterInAtomicSwcTypeInstanceRef(ARObject):
    """
    Complex type AR:PARAMETER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'AUTOSAR-PARAMETER-IREF'
    """

    def __init__(self,
                 port_prototype: PortPrototypeRef | None = None,
                 root_parameter_data_prototype: DataPrototypeRef | None = None,
                 context_data_prototype: ApplicationCompositeElementDataPrototypeRef | None = None,
                 target_data_prototype: DataPrototypeRef | None = None
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype: PortPrototypeRef | None = None
        # .ROOT-PARAMETER-DATA-PROTOTYPE-REF
        self.root_parameter_data_prototype: DataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REF
        self.context_data_prototype: ApplicationCompositeElementDataPrototypeRef | None = None
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype: DataPrototypeRef | None = None

        self._assign_optional("port_prototype", port_prototype, PortPrototypeRef)
        self._assign_optional("root_parameter_data_prototype", root_parameter_data_prototype, DataPrototypeRef)
        self._assign_optional("context_data_prototype",
                              context_data_prototype, ApplicationCompositeElementDataPrototypeRef)
        self._assign_optional("target_data_prototype", target_data_prototype, DataPrototypeRef)


class AutosarParameterRef(ARObject):
    """
    Complex type AR:AUTOSAR-PARAMETER-REF
    Tag variants: 'PARAMETER-INSTANCE' | 'ACCESSED-PARAMETER' | 'USED-PARAMETER-ELEMENT' | 'AR-PARAMETER'
    """

    def __init__(self,
                 autosar_parameter: ParameterInAtomicSwcTypeInstanceRef | None = None,
                 local_parameter: DataPrototypeRef | None = None) -> None:
        super().__init__()
        # .AUTOSAR-PARAMETER-IREF
        self.autosar_parameter: ParameterInAtomicSwcTypeInstanceRef | None = None
        # .LOCAL-PARAMETER-REF
        self.local_parameter: DataPrototypeRef | None = None

        self._assign_optional_strict("autosar_parameter", autosar_parameter, ParameterInAtomicSwcTypeInstanceRef)
        self._assign_optional("local_parameter", local_parameter, DataPrototypeRef)


class ParameterAccess(AbstractAccessPoint):
    """
    Complex type AR:PARAMETER-ACCESS
    Tag variants: 'PARAMETER-ACCESS'
    """

    def __init__(self,
                 name: str,
                 accessed_parameter: AutosarParameterRef | None = None,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)

        # .ACCESSED-PARAMETER
        self.accessed_parameter: AutosarParameterRef | None = None
        # .SW-DATA-DEF-PROPS
        self.sw_data_def_props: SwDataDefProps | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("accessed_parameter", accessed_parameter, AutosarParameterRef)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("sw_data_def_props: Type must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class WaitPoint(Identifiable):
    """
    Complex type AR:WAIT-POINT
    Tag variants: 'WAIT-POINT'
    """

    def __init__(self,
                 name: str,
                 trigger: RteEventRef | None = None,
                 timeout: int | float | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .TIMEOUT
        self.timeout: float | None = None
        # .TRIGGER-REF
        self.trigger: RteEventRef | None = None

        self._assign_optional("trigger", trigger, RteEventRef)
        self._assign_optional("timeout", timeout, float)


AsyncServerCallResultPointArgumentType = AsynchronousServerCallResultPoint | list[AsynchronousServerCallResultPoint]
ServerCallPointArgumentType = Union[AsynchronousServerCallPoint,
                                    SynchronousServerCallPoint,
                                    list[AsynchronousServerCallPoint | SynchronousServerCallPoint]]


@dataclass
class PortAccessOptions:
    """
    Internal class used for creating port access
    """

    access: ar_enum.PortAccess = ar_enum.PortAccess.EXPLICIT
    result: ar_enum.ReadResult = ar_enum.ReadResult.BY_ARGUMENT
    mode: ar_enum.ModeAccess | None = None
    call: ar_enum.CallPoint = ar_enum.CallPoint.SYNC


class RunnableEntity(ExecutableEntity):
    """
    Complex type AR:RUNNABLE-ENTITY
    Tag variants: 'RUNNABLE-ENTITY'
    """

    def __init__(self,
                 name: str,
                 argument: RunnableEntityArgument | list[RunnableEntityArgument] | None = None,
                 async_server_call_result_point: AsyncServerCallResultPointArgumentType | None = None,
                 can_be_invoked_concurrently: bool | None = None,
                 data_read_access: VariableAccess | list[VariableAccess] | None = None,
                 data_receive_point_by_argument: VariableAccess | list[VariableAccess] | None = None,
                 data_receive_point_by_value: VariableAccess | list[VariableAccess] | None = None,
                 data_send_point: VariableAccess | list[VariableAccess] | None = None,
                 data_write_access: VariableAccess | list[VariableAccess] | None = None,
                 external_triggering_point: ExternalTriggeringPoint | list[ExternalTriggeringPoint] | None = None,
                 internal_triggering_point: InternalTriggeringPoint | list[InternalTriggeringPoint] | None = None,
                 mode_access_point: ModeAccessPoint | list[ModeAccessPoint] | None = None,
                 mode_switch_point: ModeSwitchPoint | list[ModeSwitchPoint] | None = None,
                 parameter_access: ParameterAccess | list[ParameterAccess] | None = None,
                 read_local_variable: VariableAccess | list[VariableAccess] | None = None,
                 write_local_variable: VariableAccess | list[VariableAccess] | None = None,
                 server_call_point: ServerCallPointArgumentType | None = None,
                 wait_point: WaitPoint | list[WaitPoint] | None = None,
                 symbol: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ARGUMENTS
        self.argument: list[RunnableEntityArgument] = []
        # .ASYNCHRONOUS-SERVER-CALL-RESULT-POINTS
        self.async_server_call_result_point: list[AsynchronousServerCallResultPoint] = []
        # .CAN-BE-INVOKED-CONCURRENTLY
        self.can_be_invoked_concurrently: bool | None = None
        # .DATA-READ-ACCESSS
        self.data_read_access: list[VariableAccess] = []
        # .DATA-RECEIVE-POINT-BY-ARGUMENTS
        self.data_receive_point_by_argument: list[VariableAccess] = []
        # .DATA-RECEIVE-POINT-BY-VALUES
        self.data_receive_point_by_value: list[VariableAccess] = []
        # .DATA-SEND-POINTS
        self.data_send_point: list[VariableAccess] = []
        # .DATA-WRITE-ACCESSS
        self.data_write_access: list[VariableAccess] = []
        # .EXTERNAL-TRIGGERING-POINTS
        self.external_triggering_point: list[ExternalTriggeringPoint] = []
        # .INTERNAL-TRIGGERING-POINTS
        self.internal_triggering_point: list[InternalTriggeringPoint] = []
        # .MODE-ACCESS-POINTS
        self.mode_access_point: list[ModeAccessPoint] = []
        # .MODE-SWITCH-POINTS
        self.mode_switch_point: list[ModeSwitchPoint] = []
        # .PARAMETER-ACCESSS
        self.parameter_access: list[ParameterAccess] = []
        # .READ-LOCAL-VARIABLES
        self.read_local_variable: list[VariableAccess] = []
        # .SERVER-CALL-POINTS
        self.server_call_point: list[AsynchronousServerCallPoint | SynchronousServerCallPoint] = []
        # .SYMBOL
        self.symbol: str | None = None
        # .WAIT-POINTS
        self.wait_point: list[WaitPoint] = []
        # .WRITTEN-LOCAL-VARIABLES (We use a different name in our variable)
        self.write_local_variable: list[VariableAccess] = []

        # Simple arguments
        self._assign_optional("can_be_invoked_concurrently", can_be_invoked_concurrently, bool)
        self._assign_optional_strict("symbol", symbol, str)

        # Complex arguments
        if argument is not None:
            if isinstance(argument, Iterable):
                for elem in argument:
                    self.append_argument(elem)
            else:
                self.append_argument(argument)

        if async_server_call_result_point is not None:
            if isinstance(async_server_call_result_point, Iterable):
                for elem in async_server_call_result_point:
                    self.append_async_server_call_result_point(elem)
            else:
                self.append_async_server_call_result_point(async_server_call_result_point)

        if data_read_access is not None:
            if isinstance(data_read_access, Iterable):
                for elem in data_read_access:
                    self.append_data_read_access(elem)
            else:
                self.append_data_read_access(data_read_access)

        if data_receive_point_by_argument is not None:
            if isinstance(data_receive_point_by_argument, Iterable):
                for elem in data_receive_point_by_argument:
                    self.append_data_receive_point_by_argument(elem)
            else:
                self.append_data_receive_point_by_argument(data_receive_point_by_argument)

        if data_receive_point_by_value is not None:
            if isinstance(data_receive_point_by_value, Iterable):
                for elem in data_receive_point_by_value:
                    self.append_data_receive_point_by_value(elem)
            else:
                self.append_data_receive_point_by_value(data_receive_point_by_value)

        if data_send_point is not None:
            if isinstance(data_send_point, Iterable):
                for elem in data_send_point:
                    self.append_data_send_point(elem)
            else:
                self.append_data_send_point(data_send_point)

        if data_write_access is not None:
            if isinstance(data_write_access, Iterable):
                for elem in data_write_access:
                    self.append_data_write_access(elem)
            else:
                self.append_data_write_access(data_write_access)

        if external_triggering_point is not None:
            if isinstance(external_triggering_point, Iterable):
                for elem in external_triggering_point:
                    self.append_external_triggering_point(elem)
            else:
                self.append_external_triggering_point(external_triggering_point)

        if internal_triggering_point is not None:
            if isinstance(internal_triggering_point, Iterable):
                for elem in internal_triggering_point:
                    self.append_internal_triggering_point(elem)
            else:
                self.append_internal_triggering_point(internal_triggering_point)

        if mode_access_point is not None:
            if isinstance(mode_access_point, Iterable):
                for elem in mode_access_point:
                    self.append_mode_access_point(elem)
            else:
                self.append_mode_access_point(mode_access_point)

        if mode_switch_point is not None:
            if isinstance(mode_switch_point, Iterable):
                for elem in mode_switch_point:
                    self.append_mode_switch_point(elem)
            else:
                self.append_mode_switch_point(mode_switch_point)

        if parameter_access is not None:
            if isinstance(parameter_access, Iterable):
                for elem in parameter_access:
                    self.append_parameter_access(elem)
            else:
                self.append_parameter_access(parameter_access)

        if read_local_variable is not None:
            if isinstance(read_local_variable, Iterable):
                for elem in read_local_variable:
                    self.append_read_local_variable(elem)
            else:
                self.append_read_local_variable(read_local_variable)

        if write_local_variable is not None:
            if isinstance(write_local_variable, Iterable):
                for elem in write_local_variable:
                    self.append_write_local_variable(elem)
            else:
                self.append_write_local_variable(write_local_variable)

        if server_call_point is not None:
            if isinstance(server_call_point, Iterable):
                for elem in server_call_point:
                    self.append_server_call_point(elem)
            else:
                self.append_server_call_point(server_call_point)

        if wait_point is not None:
            if isinstance(wait_point, Iterable):
                for elem in wait_point:
                    self.append_wait_point(elem)
            else:
                self.append_wait_point(wait_point)

    def ref(self) -> RunnableEntityRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else RunnableEntityRef(ref_str)

    def create_port_access(self,
                           elements: str | list[str] | tuple[str, dict] | list[tuple[str, dict]]
                           ) -> None:
        """
        #convenience-method

        Attempts to automatically create new port access points based on SWC port names.
        Before this function can be used you must first setup the necessary name prefixes in the
        BehaviorSeettings object (see unit tests for examples).

        Arguments:
        elements: list of strings (See below).
                  Optionally each element can be of type tuple[str, dict] where the the dict is used
                  as additional arguments for during the access point creation.

        SenderReceiver and NvData Interfaces:
            String formats:
                1. "<prefix>:<port-name>/<element-name>"
                2. "<prefix>:<port-name>
                3. "<port-name>/<element-name>"
                4. "<port-name>"
            Accepted Prefixes:
                * "ARGUMENT" | "ARG" (default for r-port): Explicit read. Value is returned by argument.
                * "VALUE" | "VAL" : Explicit read. Value is returned by function return.
                * "READ" : Implicit read.
                * "WRITE" : Implicit write.
                * "SEND" (defalt for p-port) : Explicit write.

        ClientServer Interface:
            String formats:
                1. "<prefix>:<port-name>/<operation-name>"
                2. "<port-name>/<operation-name>"
            Accepted Prefixes:
                * "ASYNC" : Asynchronous call point
                * "SYNC" (default) : Synchronous call point

        ModeSwitch Interface:
            String formats:
                1. "<prefix>:<port-name>"
                2. "<port-name>"
            Accepcted prefixes:
                * "ACCESS" (default) : ModeAccessPoint
                * "SWITCH" :  ModeSwitchpoint

        """
        behavior = self.get_valid_parent()
        swc = behavior.get_valid_parent()
        workspace: PackageCollection = swc.root_collection()
        if workspace is None:
            raise ValueError("Runnable doesn't seem to belong to a root collection")
        settings = workspace.get_valid_behavior_settings()
        if isinstance(elements, (str, tuple)):
            elements = [elements]
        for elem in elements:
            if isinstance(elem, tuple):
                text, access_point_args = elem
            else:
                text, access_point_args = elem, None
            options = PortAccessOptions()
            parts = text.partition(":")
            if parts[1] == ":":
                self._parse_port_access_prefix(parts[0].upper(), options)
                port_arg = parts[2].lstrip()
            else:
                port_arg = parts[0]
            ref = port_arg.partition("/")
            port_name = ref[0]
            port: PortPrototypeElement = swc.find(port_name)
            if port is None:
                raise ValueError(f"Invalid port name: {port_name}")
            port_interface = workspace.get_port_interface(port.port_interface_ref)
            self._create_port_access_internal(port, port_interface, ref[2], settings, options, access_point_args)

    def _parse_port_access_prefix(self, text: str, options: PortAccessOptions) -> None:
        """
        Parses port access prefix
        """
        if text == 'ASYNC':
            options.call = ar_enum.CallPoint.ASYNC
        elif text == "SYNC":
            options.call = ar_enum.CallPoint.SYNC
        elif text in ["READ", "WRITE"]:
            options.access = ar_enum.PortAccess.IMPLICIT
        elif text in ["ARGUMENT", "ARG"]:
            options.access = ar_enum.PortAccess.EXPLICIT
            options.result = ar_enum.ReadResult.BY_ARGUMENT
        elif text in ["VALUE", "VAL"]:
            options.access = ar_enum.PortAccess.EXPLICIT
            options.result = ar_enum.ReadResult.BY_VALUE
        elif text == "SEND":
            options.access = ar_enum.PortAccess.EXPLICIT
        elif text == "ACCESS":
            options.mode = ar_enum.ModeAccess.ACCESS
        elif text == "SWITCH":
            options.mode = ar_enum.ModeAccess.SWITCH
        else:
            raise ValueError(f"Unrecognized access option: '{text}'")

    def _create_port_access_internal(self,
                                     port: PortPrototypeElement,
                                     port_interface: PortInterface,
                                     element_name: str,
                                     settings: BehaviorSettings,
                                     options: PortAccessOptions,
                                     access_point_args: dict[str, Any] | None) -> None:
        """
        Helper function for creating port access
        """
        if isinstance(port_interface, (SenderReceiverInterface, NvDataInterface)):
            self._create_data_based_port_access(port, port_interface, element_name,
                                                settings, options.access, options.result, access_point_args)
        elif isinstance(port_interface, ModeSwitchInterface):
            self._create_mode_based_port_access(port, port_interface, element_name,
                                                settings, options.mode, access_point_args)
        elif isinstance(port_interface, ParameterInterface):
            self._create_parameter_port_access(port, port_interface, element_name, settings, access_point_args)
        elif isinstance(port_interface, ClientServerInterface):
            self._create_client_server_port_access(port, port_interface, element_name,
                                                   settings, options.call, access_point_args)
        else:
            raise NotImplementedError(str(type(port_interface)))

    def _create_data_based_port_access(self,
                                       port: PortPrototypeElement,
                                       port_interface: SenderReceiverInterface | NvDataInterface,
                                       element_name: str,
                                       settings: BehaviorSettings,
                                       access_type: ar_enum.PortAccess,
                                       result_type: ar_enum.ReadResult,
                                       access_point_args: dict[str, Any] | None) -> None:
        """
        Automatically create port access for SenderReceiverInterface or NvDataInterface
        """
        data_element = None
        if len(element_name) == 0:
            if len(port_interface.data_elements) == 1:
                data_element = port_interface.data_elements[0]
        else:
            for element in port_interface.data_elements:
                if element.name == element_name:
                    data_element = element
        if data_element is None:
            raise RuntimeError(f"Unable to find a matching data element '{element_name}' "
                               f"in port interface '{port_interface.name}'")
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if isinstance(port, RequirePortPrototype):
            if access_type == ar_enum.PortAccess.IMPLICIT:
                if name is None:
                    name = "_".join([settings.get_value("data_read_access_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                self.append_data_read_access(variable_access)
            else:
                if name is None:
                    name = "_".join([settings.get_value("data_receive_point_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                if result_type == ar_enum.ReadResult.BY_VALUE:
                    self.append_data_receive_point_by_value(variable_access)
                else:
                    self.append_data_receive_point_by_argument(variable_access)
        elif isinstance(port, ProvidePortPrototype):
            if access_type == ar_enum.PortAccess.IMPLICIT:
                if name is None:
                    name = "_".join([settings.get_value("data_write_access_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                self.append_data_write_access(variable_access)
            else:
                if name is None:
                    name = "_".join([settings.get_value("data_send_point_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                self.append_data_send_point(variable_access)
        else:
            raise TypeError(f"Type not supported: {str(type(port))}")

    def _create_mode_based_port_access(self,
                                       port: PortPrototypeElement,
                                       port_interface: ModeSwitchInterface,
                                       mode_group_name: str,
                                       settings: BehaviorSettings,
                                       access_type: ar_enum.ModeAccess | None,
                                       access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for mode-based interfaces.

        access_point_args:
            For ModeAccess it's used as additional arguments for the internal ModeAccessPointIdent object.
            For ModeSwitchPoint it's used as additional arguments for the ModeSwitchPoint object.
        """
        mode_group = None
        if len(mode_group_name) != 0:
            if mode_group_name == port_interface.mode_group.name:
                mode_group = port_interface.mode_group
        else:
            mode_group = port_interface.mode_group
        if mode_group is None:
            raise RuntimeError(f"Unable to find a ModeDeclarationGroupPrototype named '{mode_group_name}' "
                               f"in port interface '{port_interface.name}'")
        name: str | None = None
        access_point = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if isinstance(port, RequirePortPrototype):
            mode_group_iref = RModeGroupInAtomicSwcInstanceRef(port.ref(), mode_group.ref())
            if access_type is None:
                access_point = ModeAccessPoint(mode_group=mode_group_iref)
            elif access_type == ar_enum.ModeAccess.ACCESS:
                if name is None:
                    name = "_".join([settings.get_value("mode_access_point_prefix"), port.name, mode_group.name])
                ident = ModeAccessPointIdent.make_with_args(name, access_point_args)
                access_point = ModeAccessPoint(ident=ident, mode_group=mode_group_iref)
        elif isinstance(port, ProvidePortPrototype):
            mode_group_iref = PModeGroupInAtomicSwcInstanceRef(port.ref(), mode_group.ref())
            if access_type is None:
                access_point = ModeAccessPoint(mode_group=mode_group_iref)
            elif access_type == ar_enum.ModeAccess.ACCESS:
                if name is None:
                    name = "_".join([settings.get_value("mode_access_point_prefix"), port.name, mode_group.name])
                ident = ModeAccessPointIdent.make_with_args(name, access_point_args)
                access_point = ModeAccessPoint(ident=ident, mode_group=mode_group_iref)
            else:
                if name is None:
                    name = "_".join([settings.get_value("mode_switch_point_prefix"), port.name, mode_group.name])
                if access_point_args is not None:
                    switch_point = ModeSwitchPoint(name, mode_group_iref, **access_point_args)
                else:
                    switch_point = ModeSwitchPoint(name, mode_group_iref)
                self.append_mode_switch_point(switch_point)
        if access_point:
            self.append_mode_access_point(access_point)

    def _create_parameter_port_access(self,
                                      port: PortPrototypeElement,
                                      port_interface: ParameterInterface,
                                      parameter_name: str,
                                      settings: BehaviorSettings,
                                      access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for parameter interface
        """
        target_data = None
        if len(parameter_name) == 0:
            if len(port_interface.parameters) == 1:
                target_data = port_interface.parameter[0]
        else:
            for element in port_interface.parameters:
                if element.name == parameter_name:
                    target_data = element
        if target_data is None:
            raise RuntimeError(f"Unable to find a matching parameter element '{parameter_name}' "
                               f"in port interface '{port_interface.name}'")
        parameter_iref = ParameterInAtomicSwcTypeInstanceRef(port_prototype=port.ref(),
                                                             target_data_prototype=target_data.ref())
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if name is None:
            name = "_".join([settings.get_value("parameter_access_prefix"),
                            port.name,
                            target_data.name])
        if access_point_args is not None:
            parameter_access = ParameterAccess(name,
                                               AutosarParameterRef(autosar_parameter=parameter_iref),
                                               **access_point_args)
        else:
            parameter_access = ParameterAccess(name, AutosarParameterRef(autosar_parameter=parameter_iref))
        self.append_parameter_access(parameter_access)

    def _create_client_server_port_access(self,
                                          port: PortPrototypeElement,
                                          port_interface: ClientServerInterface,
                                          operation_name: str,
                                          settings: BehaviorSettings,
                                          call_type: ar_enum.CallPoint,
                                          access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for client-server interfaces
        """
        operation = None
        if len(operation_name) == 0:
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
        else:
            for element in port_interface.operations:
                if element.name == operation_name:
                    operation = element
        if operation is None:
            raise RuntimeError(f"Unable to find a matching operation '{operation_name}' "
                               f"in port interface '{port_interface.name}'")
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if isinstance(port, (RequirePortPrototype, PRPortPrototype)):
            access_point = None
            if name is None:
                name = "_".join([settings.get_value("server_call_point_prefix"), port.name, operation.name])
            operation_iref = ROperationInAtomicSwcInstanceRef(port.ref(), operation.ref())
            if access_point_args is not None:
                if call_type == ar_enum.CallPoint.ASYNC:
                    access_point = AsynchronousServerCallPoint(name, operation_iref, **access_point_args)
                else:
                    access_point_args["operation"] = operation_iref
                    access_point = SynchronousServerCallPoint(name, **access_point_args)
            else:
                if call_type == ar_enum.CallPoint.ASYNC:
                    access_point = AsynchronousServerCallPoint(name, operation_iref)
                else:
                    access_point = SynchronousServerCallPoint(name, operation=operation_iref)
            if access_point:
                self.append_server_call_point(access_point)

    def append_argument(self, argument: RunnableEntityArgument) -> None:
        """
        Adds additional argument to the RunnableEntity
        """
        if isinstance(argument, RunnableEntityArgument):
            self.argument.append(argument)
        else:
            raise TypeError(f"argument: Expected type RunnableEntityArgument, got '{str(type(argument))}'")

    def append_async_server_call_result_point(self,
                                              result_point: AsynchronousServerCallResultPoint
                                              ) -> None:
        """
        A server call result point allows a runnable to fetch the result of an asynchronous server call.
        """
        if isinstance(result_point, AsynchronousServerCallResultPoint):
            make_unique_name_in_list(self.async_server_call_result_point, result_point.name)
            self.async_server_call_result_point.append(result_point)
            result_point.parent = self
        else:
            raise TypeError("result_point: Expected type AsynchronousServerCallResultPoint, "
                            f"got '{str(type(result_point))}'")

    def append_data_read_access(self, element: VariableAccess) -> None:
        """
        Implicit read access to data element of a sender-receiver port or nv-data port.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_read_access, element.name)
            self.data_read_access.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_receive_point_by_argument(self, element: VariableAccess) -> None:
        """
        Explicit read access to data element of a sender-receiver port or nv-data port.
        The result is passed back to the application by means of an argument in the function signature.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_receive_point_by_argument, element.name)
            self.data_receive_point_by_argument.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_receive_point_by_value(self, element: VariableAccess) -> None:
        """
        Explicit read access to data element of a sender-receiver port or nv-data port.
        The result is passed back to the application by means of the return value.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_receive_point_by_value, element.name)
            self.data_receive_point_by_value.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_send_point(self, element: VariableAccess) -> None:
        """
        Explicit write access to data element of a sender-receiver port or nv-data.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_send_point, element.name)
            self.data_send_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_write_access(self, element: VariableAccess) -> None:
        """
        Implicit write access to data element of a sender-receiver port or nv-data port.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_write_access, element.name)
            self.data_write_access.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_external_triggering_point(self, element: ExternalTriggeringPoint) -> None:
        """
        External triggering point
        """
        if isinstance(element, ExternalTriggeringPoint):
            self.external_triggering_point.append(element)
            if element.ident is not None:
                element.ident.parent = self
        else:
            raise TypeError(f"element: Expected type ExternalTriggeringPoint, got '{str(type(element))}'")

    def append_internal_triggering_point(self, element: InternalTriggeringPoint) -> None:
        """
        Internal triggering point
        """
        if isinstance(element, InternalTriggeringPoint):
            make_unique_name_in_list(self.internal_triggering_point, element.name)
            self.internal_triggering_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type InternalTriggeringPoint, got '{str(type(element))}'")

    def append_mode_access_point(self, element: ModeAccessPoint) -> None:
        """
        Mode access point
        """
        if isinstance(element, ModeAccessPoint):
            self.mode_access_point.append(element)
            if element.ident is not None:
                element.ident.parent = self
        else:
            raise TypeError(f"element: Expected type ModeAccessPoint, got '{str(type(element))}'")

    def append_mode_switch_point(self, element: ModeSwitchPoint) -> None:
        """
        Mode switch point
        """
        if isinstance(element, ModeSwitchPoint):
            make_unique_name_in_list(self.mode_switch_point, element.name)
            self.mode_switch_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type ModeSwitchPoint, got '{str(type(element))}'")

    def append_parameter_access(self, element: ParameterAccess) -> None:
        """
        Read access to parameter which may either be local or within a PortPrototype.
        """
        if isinstance(element, ParameterAccess):
            make_unique_name_in_list(self.parameter_access, element.name)
            self.parameter_access.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type ParameterAccess, got '{str(type(element))}'")

    def append_read_local_variable(self, element: VariableAccess) -> None:
        """
        Read access to a local variable in the role of ImplicitInterRunnableVariable or ExplicitInterRunnableVariable.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.read_local_variable, element.name)
            self.read_local_variable.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_write_local_variable(self, element: VariableAccess) -> None:
        """
        Write access to a local varaible in the role of ImplicitInterRunnableVariable or ExplicitInterRunnableVariable.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.write_local_variable, element.name)
            self.write_local_variable.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_server_call_point(self, element: AsynchronousServerCallPoint | SynchronousServerCallPoint) -> None:
        """
        Access to call a server operation of a client-server port.
        """
        if isinstance(element, ServerCallPoint):
            make_unique_name_in_list(self.server_call_point, element.name)
            self.server_call_point.append(element)
            element.parent = self
        else:
            raise TypeError("element: Expected type AsynchronousServerCallPoint or SynchronousServerCallPoint, "
                            f"got '{str(type(element))}'")

    def append_wait_point(self, element: WaitPoint) -> None:
        """
        WaitPoint associated with the RunnableEntity
        """
        if isinstance(element, WaitPoint):
            make_unique_name_in_list(self.wait_point, element.name)
            self.wait_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type WaitPoint, got '{str(type(element))}'")

    def get_valid_parent(self) -> "SwcInternalBehavior":
        """
        Verifies that this object has valid SwcInternalBehavior as parent before returning it
        """
        if self.parent is None or not isinstance(self.parent, SwcInternalBehavior):
            raise RuntimeError("Runnable object doesn't have a valid parent")
        return self.parent


class RteEvent(Identifiable):
    """
    Group AR:RTE-EVENT
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | None = None,
                 disabled_modes: RModeInAtomicSwcInstanceRef | list[RModeInAtomicSwcInstanceRef] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DISABLED-MODE-IREFS
        self.disabled_modes: list[RModeInAtomicSwcInstanceRef] = []
        # .START-ON-EVENT-REF
        self.start_on_event: RunnableEntityRef | None = None

        if disabled_modes is not None:
            if isinstance(disabled_modes, RModeInAtomicSwcInstanceRef):
                self.append_disabled_mode(disabled_modes)
            elif isinstance(disabled_modes, list):
                for disabled_mode in disabled_modes:
                    self.append_disabled_mode(disabled_mode)
        self._assign_optional("start_on_event", start_on_event, RunnableEntityRef)

    def append_disabled_mode(self, disabled_mode: RModeInAtomicSwcInstanceRef) -> None:
        """
        Adds reference to the modes that disable the event
        """
        if isinstance(disabled_mode, RModeInAtomicSwcInstanceRef):
            self.disabled_modes.append(disabled_mode)
        else:
            raise TypeError("disabled_mode must be of type RModeInAtomicSwcInstanceRef")


class AsynchronousServerCallReturnsEvent(RteEvent):
    """
    Complex type AR:ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT
    Tag variants: 'ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: AsynchronousServerCallResultPointRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: AsynchronousServerCallResultPointRef | None = None
        self._assign_optional("event_source", event_source, AsynchronousServerCallResultPointRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_RETURNS_EVENT)


class BackgroundEvent(RteEvent):
    """
    Complex Type AR:BACKGROUND-EVENT
    Tag variants: 'BACKGROUND-EVENT'
    Inherits constructor from base-class
    """

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.BACKGROUND_EVENT)


class DataReceiveErrorEvent(RteEvent):
    """
    Complex Type AR:DATA-RECEIVE-ERROR-EVENT
    Tag variants: 'DATA-RECEIVE-ERROR-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 data: RVariableInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .DATA-IREF
        self.data: RVariableInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("data", data, RVariableInAtomicSwcInstanceRef)

    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             target_data_element: VariableDataPrototypeRef | str | None = None,
             **kwargs) -> "DataReceiveErrorEvent":
        """
        #convenience-method

        Simplified creation method that automatically creates
        and uses the necessary RVariableInAtomicSwcInstanceRef object
        """
        data = RVariableInAtomicSwcInstanceRef(context_port, target_data_element)
        return cls(name, start_on_event, data, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_RECEIVE_ERROR_EVENT)


class DataReceivedEvent(RteEvent):
    """
    Complex Type AR:DATA-RECEIVED-EVENT
    Tag variants: 'DATA-RECEIVED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 data: RVariableInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .DATA-IREF
        self.data: RVariableInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("data", data, RVariableInAtomicSwcInstanceRef)

    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             target_data_element: VariableDataPrototypeRef | str | None = None,
             **kwargs) -> "DataReceivedEvent":
        """
        #convenience-method

        Simplified creation method that automatically creates
        and uses the necessary RVariableInAtomicSwcInstanceRef object
        """
        data = RVariableInAtomicSwcInstanceRef(context_port, target_data_element)
        return cls(name, start_on_event, data, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_RECEIVED_EVENT)


class DataSendCompletedEvent(RteEvent):
    """
    Complex Type AR:DATA-SEND-COMPLETED-EVENT
    Tag variants: 'DATA-SEND-COMPLETED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: VariableAccessRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: VariableAccessRef | None = None
        self._assign_optional("event_source", event_source, VariableAccessRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_SEND_COMPLETED_EVENT)


class DataWriteCompletedEvent(RteEvent):
    """
    Complex Type AR:DATA-WRITE-COMPLETED-EVENT
    Tag variants: 'DATA-WRITE-COMPLETED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: VariableAccessRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: VariableAccessRef | None = None
        self._assign_optional("event_source", event_source, VariableAccessRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_WRITE_COMPLETED_EVENT)


class ExternalTriggerOccurredEvent(RteEvent):
    """
    Complex Type AR:EXTERNAL-TRIGGER-OCCURRED-EVENT
    Tag variants: 'EXTERNAL-TRIGGER-OCCURRED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 trigger: RTriggerInAtomicSwcInstanceRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .TRIGGER-IREF
        self.trigger: RTriggerInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("trigger", trigger, RTriggerInAtomicSwcInstanceRef)

    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             target_trigger: TriggerRef | str | None = None,
             **kwargs) -> "ExternalTriggerOccurredEvent":
        """
        #convenience-method
        """
        trigger = RTriggerInAtomicSwcInstanceRef(context_port, target_trigger)
        return cls(name, start_on_event, trigger, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.EXTERNAL_TRIGGER_OCCURRED_EVENT)


class InitEvent(RteEvent):
    """
    Complex Type AR:INIT-EVENT
    Tag variants: 'INIT-EVENT'
    Inherits constructor from base-class
    """

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.INIT_EVENT)


class InternalTriggerOccurredEvent(RteEvent):
    """
    Complex type AR:INTERNAL-TRIGGER-OCCURRED-EVENT
    Tag variants: 'INTERNAL-TRIGGER-OCCURRED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: InternalTriggeringPointRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: InternalTriggeringPointRef | None = None
        self._assign_optional("event_source", event_source, InternalTriggeringPointRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.INTERNAL_TRIGGER_OCCURRED_EVENT)


class ModeSwitchedAckEvent(RteEvent):
    """
    Complex type AR:MODE-SWITCHED-ACK-EVENT
    Tag variants: 'MODE-SWITCHED-ACK-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: ModeSwitchPointRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: ModeSwitchPointRef | None = None
        self._assign_optional("event_source", event_source, ModeSwitchPointRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.MODE_SWITCHED_ACK_EVENT)


class OperationInvokedEvent(RteEvent):
    """
    Complex type AR:OPERATION-INVOKED-EVENT
    Tag variants: 'OPERATION-INVOKED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 operation: POperationInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .OPERATION-IREF
        self.operation: POperationInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("operation", operation, POperationInAtomicSwcInstanceRef)

    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractProvidedPortPrototypeRef | None = None,
             target_provided_operation: ClientServerOperationRef | str | None = None,
             **kwargs) -> "OperationInvokedEvent":
        """
        #convenience-method

        Simplified creation method that automatically creates
        and uses the necessary POperationInAtomicSwcInstanceRef object
        """
        operation = POperationInAtomicSwcInstanceRef(context_port, target_provided_operation)
        return cls(name, start_on_event, operation, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.OPERATION_INVOKED_EVENT)


SwcModeSwitchEventModeType = Union[RModeInAtomicSwcInstanceRef,
                                   tuple[RModeInAtomicSwcInstanceRef, RModeInAtomicSwcInstanceRef],
                                   None]


class SwcModeManagerErrorEvent(RteEvent):
    """
    Complex type AR:SWC-MODE-MANAGER-ERROR-EVENT
    Tag variants: 'SWC-MODE-MANAGER-ERROR-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 mode_group: PModeGroupInAtomicSwcInstanceRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .MODE-GROUP-IREF
        self.mode_group: PModeGroupInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("mode_group", mode_group, PModeGroupInAtomicSwcInstanceRef)

    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractProvidedPortPrototypeRef | None = None,
             context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | str | None = None,
             **kwargs) -> "SwcModeManagerErrorEvent":
        """
        #convenience-method
        """
        mode_group = PModeGroupInAtomicSwcInstanceRef(context_port, context_mode_declaration_group_prototype)
        return cls(name, start_on_event, mode_group, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.SWC_MODE_MANAGER_ERROR_EVENT)


class SwcModeSwitchEvent(RteEvent):
    """
    Complex type AR:SWC-MODE-SWITCH-EVENT
    Tag variants: 'SWC-MODE-SWITCH-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 activation: ar_enum.ModeActivationKind | None = None,
                 mode: SwcModeSwitchEventModeType = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .ACTIVATION
        self.activation: ar_enum.ModeActivationKind | None = None
        # .MODE-IREFS
        self.mode: SwcModeSwitchEventModeType = None

        self._assign_optional("activation", activation, ar_enum.ModeActivationKind)
        if mode is not None:
            if isinstance(mode, RModeInAtomicSwcInstanceRef):
                self.mode = mode
            elif isinstance(mode, tuple):
                if (isinstance(mode[0], RModeInAtomicSwcInstanceRef) and  # noqa W504
                        isinstance(mode[1], RModeInAtomicSwcInstanceRef)):
                    self.mode = mode
                else:
                    raise TypeError("Both values of mode tuple must be of type RModeInAtomicSwcInstanceRef")
            else:
                msg_part1 = "Invalid type for parameter 'mode'. "
                msg_part2 = "Expected types are RModeInAtomicSwcInstanceRef or tuple of same type."
                msg_part3 = f"Got {str(type(mode))}"
                raise TypeError(msg_part1 + msg_part2 + msg_part3)

    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             activation: ar_enum.ModeActivationKind | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | None = None,
             target_mode_declaration: ModeDeclarationRef | None = None,
             **kwargs) -> "SwcModeSwitchEvent":
        """
        #convenience-method

        Only suitable for ON-ENTRY and ON-EXIT activation types.
        For ON-TRANSITION activation, use the class constructor instead.

        """
        mode = RModeInAtomicSwcInstanceRef(context_port,
                                           context_mode_declaration_group_prototype,
                                           target_mode_declaration)
        return cls(name, start_on_event, activation, mode, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.SWC_MODE_SWITCH_EVENT)


class TimingEvent(RteEvent):
    """
    Complex type AR:TIMING-EVENT
    Tag variants: 'TIMING-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 period: int | float | None = None,
                 offset: int | float | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .OFFSET
        self.offset: int | float | None = None
        # .PERIOD
        self.period: int | float | None = None

        self._assign_optional("offset", offset, float)
        self._assign_optional("period", period, float)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.TIMING_EVENT)


class TransformerHardErrorEvent(RteEvent):
    """
    Complex type AR:TRANSFORMER-HARD-ERROR-EVENT
    Tag variants: 'TRANSFORMER-HARD-ERROR-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 operation: POperationInAtomicSwcInstanceRef | None = None,
                 required_trigger: RTriggerInAtomicSwcInstanceRef | None = None,
                 trigger: PTriggerInAtomicSwcTypeInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .OPERATION-IREF
        self.operation: POperationInAtomicSwcInstanceRef | None = None
        # .REQUIRED-TRIGGER-IREF
        self.required_trigger: RTriggerInAtomicSwcInstanceRef | None = None
        # .TRIGGER-IREF
        self.trigger: PTriggerInAtomicSwcTypeInstanceRef | None = None

        self._assign_optional_strict("operation", operation, POperationInAtomicSwcInstanceRef)
        self._assign_optional_strict("required_trigger", required_trigger, RTriggerInAtomicSwcInstanceRef)
        self._assign_optional_strict("trigger", trigger, PTriggerInAtomicSwcTypeInstanceRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.TRANSFORMER_HARD_ERROR_EVENT)


class PortDefinedArgumentValue(ARObject):
    """
    Complex type AR:PORT-DEFINED-ARGUMENT-VALUE
    Tag variantS: 'PORT-DEFINED-ARGUMENT-VALUE'
    """

    def __init__(self,
                 value: ValueSpecificationElement | None = None,
                 value_type: ImplementationDataTypeRef | str | None = None) -> None:
        super().__init__()
        # .VALUE
        self.value: ValueSpecificationElement | None = None
        # .VALUE-TYPE-TREF
        self.value_type: ImplementationDataTypeRef | None = None

        self._assign_optional_strict("value", value, ValueSpecification)
        self._assign_optional("value_type", value_type, ImplementationDataTypeRef)


class SwcSupportedFeature(ARObject):
    """
    Base class for supported features
    """


class CommunicationBufferLocking(SwcSupportedFeature):
    """
    Complex type AR:COMMUNICATION-BUFFER-LOCKING
    Tag variantS: 'COMMUNICATION-BUFFER-LOCKING'
    """

    def __init__(self,
                 support_buffer_locking: ar_enum.SupportBufferLocking | None = None) -> None:
        super().__init__()
        # .SUPPORT-BUFFER-LOCKING
        self.support_buffer_locking: ar_enum.SupportBufferLocking = None

        self._assign_optional("support_buffer_locking", support_buffer_locking, ar_enum.SupportBufferLocking)


PortDefinedArgumentValueArgType = PortDefinedArgumentValue | list[PortDefinedArgumentValue] | None
SwcSupportedFeatureArgType = SwcSupportedFeature | list[SwcSupportedFeature] | None


class PortApiOption(ARObject):
    """
    Complex type AR:PORT-API-OPTION
    Tag variants: 'PORT-API-OPTION'
    """

    def __init__(self,
                 port: PortPrototypeRef | None = None,
                 enable_take_address: bool | None = None,
                 indirect_api: bool | None = None,
                 error_handling: ar_enum.DataTransformationErrorHandling | None = None,
                 port_arg_values: PortDefinedArgumentValueArgType = None,
                 supported_features: SwcSupportedFeatureArgType = None,
                 transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None
                 ) -> None:
        super().__init__()
        # .ENABLE-TAKE-ADDRESS
        self.enable_take_address: bool | None = None
        # .ERROR-HANDLING
        self.error_handling: ar_enum.DataTransformationErrorHandling | None = None
        # .INDIRECT-API
        self.indirect_api: bool | None = None
        # .PORT-ARG-VALUES
        self.port_arg_values: list[PortDefinedArgumentValue] = []
        # .PORT-REF
        self.port: PortPrototypeRef | None = port
        # .SUPPORTED-FEATURES
        self.supported_features: list[SwcSupportedFeature] = []
        # .TRANSFORMER-STATUS-FORWARDING
        self.transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None
        # .VARIATION-POINT not supported

        self._assign_optional("enable_take_address", enable_take_address, bool)
        self._assign_optional("error_handling", error_handling, ar_enum.DataTransformationErrorHandling)
        self._assign_optional("indirect_api", indirect_api, bool)
        self._assign_optional("port", port, PortPrototypeRef)
        self._assign_optional("transformer_status_forwarding",
                              transformer_status_forwarding,
                              ar_enum.DataTransformationStatusForwarding)
        if port_arg_values is not None:
            if isinstance(port_arg_values, list):
                for port_arg_value in port_arg_values:
                    self.append_port_arg_value(port_arg_value)
            else:
                self.append_port_arg_value(port_arg_values)
        if supported_features is not None:
            if isinstance(supported_features, list):
                for supported_feature in supported_features:
                    self.append_supported_feature(supported_feature)
            else:
                self.append_supported_feature(supported_features)

    def append_port_arg_value(self, port_arg_value: PortDefinedArgumentValue) -> None:
        """
        Adds PortDefinedArgumentValue to internal list
        """
        if isinstance(port_arg_value, PortDefinedArgumentValue):
            self.port_arg_values.append(port_arg_value)
        else:
            raise TypeError("port_arg_value must be of type PortDefinedArgumentValue")

    def append_supported_feature(self, supported_feature: SwcSupportedFeature) -> None:
        """
        Adds PortDefinedArgumentValue to internal list
        """
        if isinstance(supported_feature, (CommunicationBufferLocking,)):
            self.supported_features.append(supported_feature)
        else:
            raise TypeError("supported_feature must be of type CommunicationBufferLocking")


class ExclusiveArea(Identifiable):
    """
    Complex Type AR:EXCLUSIVE-AREA
    Tag variants: 'EXCLUSIVE-AREA'
    Inherits constructor from parent class
    """

    def ref(self) -> ExclusiveAreaRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ExclusiveAreaRef(ref_str)


class InternalBehavior(Identifiable):
    """
    Group AR:INTERNAL-BEHAVIOR
    Implementation is very limited for now
    """
    def __init__(self,
                 name: str,
                 data_type_mappings: str | DataTypeMappingSetRef | list[DataTypeMappingSetRef] | None = None,
                 exclusive_areas: ExclusiveArea | list[ExclusiveArea] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CONSTANT-MEMORYS (not yet implemented)
        # .CONSTANT-VALUE-MAPPING-REFS (not yet implemented)
        # .DATA-TYPE-MAPPING-REFS
        self.data_type_mappings: list[DataTypeMappingSetRef] = []
        # .EXCLUSIVE-AREAS
        self.exclusive_areas: list[ExclusiveArea] = []
        # .EXCLUSIVE-AREA-NESTING-ORDERS (not yet implemented)
        # .STATIC-MEMORYS (not yet implemented)

        if data_type_mappings is not None:
            if isinstance(data_type_mappings, str):
                data_type_mappings = DataTypeMappingSetRef(data_type_mappings)
            if isinstance(data_type_mappings, Iterable):
                for mapping_set in data_type_mappings:
                    self.append_data_type_mapping(mapping_set)
            else:
                self.append_data_type_mapping(data_type_mappings)
        if exclusive_areas is not None:
            if isinstance(exclusive_areas, Iterable):
                for exclusive_area in exclusive_areas:
                    self.append_exclusive_area(exclusive_area)
            else:
                self.append_exclusive_area(exclusive_areas)

    def create_exclusive_area(self, name: str, **kwargs) -> ExclusiveArea:
        """
        Adds a new ExclusiveArea to this object

        #convenience-method
        """
        exclusive_area = ExclusiveArea(name, **kwargs)
        self.append_exclusive_area(exclusive_area)
        return exclusive_area

    def append_data_type_mapping(self, mapping_set: DataTypeMappingSetRef) -> None:
        """
        Adds runnable to internal list of runnables
        """
        if isinstance(mapping_set, DataTypeMappingSetRef):
            self.data_type_mappings.append(mapping_set)
        else:
            raise TypeError(f"mapping_set must be of type DataTypeMappingSetRef. Got {str(type(mapping_set))}")

    def append_exclusive_area(self, exclusive_area: ExclusiveArea) -> None:
        """
        Adds runnable to internal list of runnables
        """
        if isinstance(exclusive_area, ExclusiveArea):
            self.exclusive_areas.append(exclusive_area)
            exclusive_area.parent = self
        else:
            raise TypeError(f"exclusive_area must be of type ExclusiveArea. Got {str(type(exclusive_area))}")


ModeSwitchEventArgsReturnType = tuple[RequirePortPrototype, ModeDeclarationGroupPrototype, ModeDeclaration]


class SwcInternalBehavior(InternalBehavior):
    """
    Complex type AR:SWC-INTERNAL-BEHAVIOR
    Tag variants: 'SWC-INTERNAL-BEHAVIOR'

    Implementation is very limited for now
    """

    def __init__(self,
                 name: str,
                 events: RteEvent | list[RteEvent] | None = None,
                 runnables: RunnableEntity | list[RunnableEntity] | None = None,
                 port_api_options: PortApiOption | list[PortApiOption] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .AR-TYPED-PER-INSTANCE-MEMORYS (not yet implemented)
        # .EVENTS
        self.events: list[RteEvent] = []
        # .EXCLUSIVE-AREA-POLICYS (not yet implemented)
        # .EXPLICIT-INTER-RUNNABLE-VARIABLES (not yet implemented)
        # .HANDLE-TERMINATION-AND-RESTART (not yet implemented)
        # .INCLUDED-DATA-TYPE-SETS (not yet implemented)
        # .INCLUDED-MODE-DECLARATION-GROUP-SETS (not yet implemented)
        # .INSTANTIATION-DATA-DEF-PROPSS (not yet implemented)
        # .PER-INSTANCE-MEMORYS (not yet implemented)
        # .PER-INSTANCE-PARAMETERS (not yet implemented)
        # .PORT-API-OPTIONS
        self.port_api_options: OrderedDict[PortApiOption] = OrderedDict()
        # .RUNNABLES
        self.runnables: list[RunnableEntity] = []
        # .SERVICE-DEPENDENCYS (not yet implemented)
        # .SHARED-PARAMETERS (not yet implemented)
        # .SUPPORTS-MULTIPLE-INSTANTIATION (not yet implemented)
        # .VARIATION-POINT-PROXYS (not supported)
        # .VARIATION-POINT (not supported)

        if events is not None:
            if isinstance(events, Iterable):
                for event in events:
                    self.append_event(event)
            else:
                self.append_event(events)

        if runnables is not None:
            if isinstance(runnables, Iterable):
                for runnable in runnables:
                    self.append_runnable(runnable)
            else:
                self.append_runnable(runnables)

        if port_api_options is not None:
            if isinstance(port_api_options, Iterable):
                for port_api_option in port_api_options:
                    self.append_port_api_option(port_api_option)
            else:
                self.append_port_api_option(port_api_options)

    def get_valid_parent(self) -> SwComponentType:
        """
        Verifies that this object has valid SoftwareComponent as parent before returning it
        """
        if self.parent is None or not isinstance(self.parent, SwComponentType):
            raise RuntimeError("Behavior object doesn't have a valid parent")
        return self.parent

    def get_valid_behavior_settings(self) -> BehaviorSettings:
        """
        Verifies that the root collection has a valid behavior_settings object and returns it
        """
        swc = self.get_valid_parent()
        workspace = swc.root_collection()
        if workspace is None:
            raise ValueError("SWC doesn't seem to belong to a root collection")
        return workspace.get_valid_behavior_settings()

    def ref(self) -> SwcInternalBehaviorRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwcInternalBehaviorRef(ref_str)

    def append_runnable(self, runnable: RunnableEntity) -> None:
        """
        Adds runnable to internal list of runnables
        """
        if isinstance(runnable, RunnableEntity):
            runnable.parent = self
            self.runnables.append(runnable)
        else:
            raise TypeError(f"runnable must be of type RunnableEntity. Got {str(type(runnable))}")

    def append_event(self, event: RteEvent) -> None:
        """
        Adds event to internal list of events
        """
        if isinstance(event, RteEvent):
            event.parent = self
            self.events.append(event)
        else:
            raise TypeError(f"event must derive from RteEvent. Got {str(type(event))}")

    def append_port_api_option(self, element: PortApiOption) -> None:
        """
        Generation options for port-related calls in the RTE.
        """
        if isinstance(element, PortApiOption):
            if element.port is not None:
                parts = str(element.port).split("/")
                self.port_api_options[parts[-1]] = element
        else:
            raise TypeError(f"element: Expected type PortApiOption, got '{str(type(element))}'")

    def create_runnable(self,
                        name: str,
                        can_be_invoked_concurrently: bool | None = None,
                        minimum_start_interval: int | float | None = None,
                        symbol: str | None = "",
                        activation_reasons: ActivationReasonArgumentType = None,
                        can_enter_leave: CanEnterLeaveArgumentType = None,
                        exclusive_area_nesting_order: ExclusiveAreaNestingOrderArgumentType = None,
                        reentrancy_level: ar_enum.ReentrancyLevel | None = None,
                        runs_insides: RunsInsidesArgumentType = None,
                        sw_addr_method: str | SwAddrMethodRef | None = None,
                        **kwargs) -> RunnableEntity:
        """
        Adds a new RunnableEntity to this behavior object

        symbol: If the symbol argument is an empty string (default value), it will generate a symbol
                identcal to the the name argument.
                If you don't want a symbol at all, explicitly pass the value None as argument for symbol.

        can_enter_leave: If argument type is str or list[str] then it expects each string to be the
                         short-name of an existing exclusive area.

        #convenience-method
        """
        if isinstance(symbol, str) and len(symbol) == 0:
            symbol = name
        if can_enter_leave is not None:
            names: dict[str, bool] = {}
            if isinstance(can_enter_leave, str):
                names[can_enter_leave] = False
            elif isinstance(can_enter_leave, Iterable):
                for elem in can_enter_leave:
                    if isinstance(elem, str):
                        names[elem] = False
            if names:
                exclusive_area_refs: ExclusiveAreaRef = []
                for area in self.exclusive_areas:
                    if area.name in names:
                        names[area.name] = True  # Marks it as handled
                        exclusive_area_refs.append(area.ref())
                for key, value in names.items():
                    if not value:
                        raise ValueError(f"can_enter_leave: '{key}' does not name an exclusive area in "
                                         "this SwcInternalBehavior object")
                can_enter_leave = exclusive_area_refs

        data = {"can_be_invoked_concurrently": can_be_invoked_concurrently,
                "minimum_start_interval": minimum_start_interval,
                "symbol": symbol,
                "activation_reasons": activation_reasons,
                "can_enter_leave": can_enter_leave,
                "exclusive_area_nesting_order": exclusive_area_nesting_order,
                "reentrancy_level": reentrancy_level,
                "runs_insides": runs_insides,
                "sw_addr_method": sw_addr_method
                }
        data.update(kwargs)
        runnable = RunnableEntity(name, **data)
        self.append_runnable(runnable)
        runnable.parent = self
        return runnable

    def find_runnable(self, name: str) -> RunnableEntity | None:
        """
        Find runnable by name. Returns None if no runnable is found.
        """
        for runnable in self.runnables:
            if runnable.name == name:
                return runnable
        return None

    def _make_unique_event_name(self, event_name: str) -> str:
        """
        Checks if event_name is unique in internal event list.
        If not, then it automatically starts to add an integer-based name suffix ("_0", "_1" etc.).
        Calling this function could potentially invalidate existing event references.
        Note: Not yet implemented
        """
        return make_unique_name_in_list(self.events, event_name)

    def create_background_event(self,
                                runnable_name: str,
                                event_name: str | None = None,
                                **kwargs
                                ) -> BackgroundEvent:
        """
        Adds a new BackgroundEvent to this SwcInternalBehavior object.

        #convenience-method
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.background_event_prefix:
                event_name = behavior_settings.background_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " background_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = BackgroundEvent(unique_event_name, runnable.ref(), **kwargs)
        self.append_event(event)
        return event

    def create_data_receive_error_event(self,
                                        runnable_name: str,
                                        port_data_element: str,
                                        event_name: str | None = None,
                                        **kwargs
                                        ) -> DataReceiveErrorEvent:
        """
        Adds a new DataReceiveErrorEvent to this SwcInternalBehavior object
        port_data_element is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.

        #convenience-method
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(port_data_element)
        if len(name_parts) == 1:
            port_name, data_element_name = name_parts[0], None
        else:
            port_name, data_element_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"port_data_element: '{port_data_element}' does not name an existing R-PORT or PR-PORT")
        target_data_element = swc.get_data_element_in_port(context_port, data_element_name)
        if target_data_element is None:
            msg = f"port_data_element: '{port_data_element}' does not name an existing data element in port interface"
            raise ValueError(msg)
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.data_receive_error_event_prefix:
                event_name = "_".join([behavior_settings.data_receive_error_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       target_data_element.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " data_receive_error_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = DataReceiveErrorEvent.make(unique_event_name,
                                           runnable.ref(),
                                           context_port.ref(),
                                           target_data_element.ref(),
                                           **kwargs)
        self.append_event(event)
        return event

    def create_data_received_event(self,
                                   runnable_name: str,
                                   data_element_ref: str,
                                   event_name: str | None = None,
                                   **kwargs
                                   ) -> DataReceivedEvent:
        """
        Adds a new DataReceivedEvent to this SwcInternalBehavior object
        data_element_ref is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.

        #convenience-method
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(data_element_ref)
        if len(name_parts) == 1:
            port_name, data_element_name = name_parts[0], None
        else:
            port_name, data_element_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"data_element_ref: '{data_element_ref}' does not name an existing R-PORT or PR-PORT")
        target_data_element = swc.get_data_element_in_port(context_port, data_element_name)
        if target_data_element is None:
            msg = f"data_element_ref: '{data_element_ref}' does not name an existing data element in port interface"
            raise ValueError(msg)
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.data_receive_event_prefix:
                event_name = "_".join([behavior_settings.data_receive_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       target_data_element.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " data_receive_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = DataReceivedEvent.make(unique_event_name,
                                       runnable.ref(),
                                       context_port.ref(),
                                       target_data_element.ref(),
                                       **kwargs)
        self.append_event(event)
        return event

    def create_data_send_completed_event(self,
                                         runnable_name: str,
                                         data_element_ref: str,
                                         event_name: str | None = None,
                                         **kwargs
                                         ) -> DataSendCompletedEvent:
        """
        Adds a new DataSendCompletedEvent to this SwcInternalBehavior object
        data_element_ref is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.
        The given runnable must have a data send point referencing the port and data element.
        Note: Unable to complete implementation. Requires support for port-access in runnables.

        #convenience-method
        """
        raise NotImplementedError("References to data send points are not yet supported")

    def create_data_write_completed_event(self,
                                          runnable_name: str,
                                          data_element_ref: str,
                                          event_name: str | None = None,
                                          **kwargs
                                          ) -> DataWriteCompletedEvent:
        """
        Adds a new DataWriteCompletedEvent to this SwcInternalBehavior object
        data_element_ref is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.
        The given runnable must have a data send point referencing the port and data element.
        Note: Not implemented due to lack of support for data write access

        #convenience-method
        """
        raise NotImplementedError("References to data write access are not yet supported")

    def create_init_event(self,
                          runnable_name: str,
                          event_name: str | None = None,
                          **kwargs
                          ) -> InitEvent:
        """
        Adds a new InitEvent to this SwcInternalBehavior object

        #convenience-method
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.init_event_prefix:
                event_name = behavior_settings.init_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " init_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = InitEvent(unique_event_name, runnable.ref(), **kwargs)
        self.append_event(event)
        return event

    def create_operation_invoked_event(self,
                                       runnable_name: str,
                                       operation_ref: str,
                                       event_name: str | None = None,
                                       **kwargs
                                       ) -> OperationInvokedEvent:
        """
        Adds a new OperationInvokedEvent to this object
        operation_ref is a string with format <PortName>/<OperationName>

        #convenience-method
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(operation_ref)
        if len(name_parts) == 1:
            port_name, operation_name = name_parts[0], None
        else:
            port_name, operation_name = name_parts[0], name_parts[1]
        context_port = swc.find_p_port(port_name)
        if context_port is None:
            raise ValueError(f"port_name: '{port_name}' does not name an existing P-PORT or PR-PORT")
        target_provided_operation = swc.get_operation_in_port(context_port, operation_name)
        if target_provided_operation is None:
            raise ValueError(f"operation_ref: '{operation_ref}' does not name a valid operation in port interface")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.operation_invoked_event_prefix:
                event_name = "_".join([behavior_settings.operation_invoked_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       target_provided_operation.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " operation_invoked_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = OperationInvokedEvent.make(unique_event_name,
                                           runnable.ref(),
                                           context_port.ref(),
                                           target_provided_operation.ref(),
                                           **kwargs)
        self.append_event(event)
        return event

    def create_swc_mode_manager_error_event(self,
                                            runnable_name: str,
                                            port_name: str,
                                            event_name: str | None = None,
                                            **kwargs
                                            ) -> SwcModeManagerErrorEvent:
        """
        Adds a new SwcModeManagerErrorEvent to this object

        #convenience-method
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        context_port = swc.find_p_port(port_name)
        if context_port is None:
            raise ValueError(f"port_name: '{port_name}' does not name an existing P-PORT or PR-PORT")
        context_mode_declaration_group = swc.get_mode_declaration_group_in_port(context_port)
        if context_mode_declaration_group is None:
            msg = f"port_name: '{port_name}' does not name a valid ModeDeclarationGroupPrototype in port interface"
            raise ValueError(msg)
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.swc_mode_manager_error_event_prefix:
                event_name = "_".join([behavior_settings.swc_mode_manager_error_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       context_mode_declaration_group.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " swc_mode_manager_error_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = SwcModeManagerErrorEvent.make(unique_event_name,
                                              runnable.ref(),
                                              context_port.ref(),
                                              context_mode_declaration_group.ref(),
                                              **kwargs)
        self.append_event(event)
        return event

    def create_swc_mode_mode_switch_event(self,
                                          runnable_name: str,
                                          mode_ref: str | list[str] | tuple[str, str],
                                          activation: ar_enum.ModeActivationKind | None = None,
                                          event_name: str | None = None,
                                          **kwargs
                                          ) -> SwcModeSwitchEvent:
        """
        Adds a new SwcModeSwitchEvent to this SwcInternalBehavior object.
        mode_ref is a string with format '<PortName>/<ModeDeclarationName>'.
        mode_ref can also be a 2-element list or a 2-tuple containing strings with same format as above.
        The second version is used for creating events for specific mode transitions.

        #convenience-method
        """
        swc = self.get_valid_parent()
        workspace = swc.root_collection()
        assert workspace is not None
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.swc_mode_switch_event_prefix:
                event_name = behavior_settings.swc_mode_switch_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " swc_mode_switch_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        expected_formats = "Expected formats: '<PortName>', '<PortName>/<ModeDeclarationName>', tuple[str, str]"
        if isinstance(mode_ref, str):
            if len(mode_ref) == 0:
                raise ValueError("mode_ref: Invalid argument. " + expected_formats)
            context_port, context_mode_declaration_group, target_mode_declaration = (
                self._get_swc_mode_switch_event_args(workspace, swc, mode_ref))
            event = SwcModeSwitchEvent.make(unique_event_name,
                                            runnable.ref(),
                                            activation,
                                            context_port.ref(),
                                            context_mode_declaration_group.ref(),
                                            target_mode_declaration.ref(),
                                            **kwargs)
        elif isinstance(mode_ref, (list, tuple)):
            if len(mode_ref) != 2:
                raise ValueError("mode_ref: Must be exactly two elements in tuple or list")
            instance_refs = []
            for ref in mode_ref:
                if isinstance(ref, str):
                    if len(ref) == 0:
                        raise ValueError("mode_ref: Invalid argument. " + expected_formats)
                    context_port, context_mode_declaration_group, target_mode_declaration = (
                        self._get_swc_mode_switch_event_args(workspace, swc, ref))
                    instance_refs.append(RModeInAtomicSwcInstanceRef(context_port.ref(),
                                                                     context_mode_declaration_group.ref(),
                                                                     target_mode_declaration.ref()))
                else:
                    raise TypeError(f"mode_ref: Invalid type '{str(type(ref))}'. " + expected_formats)
            event = SwcModeSwitchEvent(unique_event_name,
                                       runnable.ref(),
                                       activation,
                                       (instance_refs[0], instance_refs[1]),
                                       **kwargs)
        else:
            raise TypeError(f"mode_ref: Unsupported type '{str(type(mode_ref))}'")
        self.append_event(event)
        return event

    def create_timing_event(self,
                            runnable_name: str,
                            period: int | float | None = None,
                            offset: int | float | None = None,
                            event_name: str | None = None,
                            **kwargs) -> TimingEvent:
        """
        Adds a new TimingEvent to this object

        #convenience-method
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.timing_event_prefix:
                event_name = behavior_settings.timing_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " timing_event_prefix is not set in behavior settings"
                raise RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = TimingEvent(unique_event_name, runnable.ref(), period, offset, **kwargs)
        self.append_event(event)
        return event

    def _get_swc_mode_switch_event_args(self,
                                        workspace: PackageCollection,
                                        swc: AtomicSoftwareComponentType,
                                        mode_ref: str
                                        ) -> ModeSwitchEventArgsReturnType:
        """
        Helper function for create_swc_mode_switch_event
        """
        name_parts = split_ref_strict(mode_ref)
        if len(name_parts) != 2:
            raise ValueError("mode_ref: Formatting error, expected <PortName>/<ModeDeclarationName>")
        port_name, mode_declaration_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"mode_ref: '{mode_ref}' does not name an existing R-PORT or PR-PORT")
        context_mode_declaration_group = swc.get_mode_declaration_group_in_port(context_port)
        if context_mode_declaration_group is None:
            msg = f"mode_ref: '{mode_ref}' does not name a valid ModeDeclarationGroupPrototype in port interface"
            raise ValueError(msg)
        target_mode_declaration_group: ModeDeclarationGroup | None
        target_mode_declaration_group = workspace.find(context_mode_declaration_group.type_ref)
        if target_mode_declaration_group is None:
            raise ar_except.InvalidReferenceError(str(context_mode_declaration_group.type_ref))
        target_mode_declaration: ModeDeclaration | None = target_mode_declaration_group.find(mode_declaration_name)
        if target_mode_declaration is None:
            raise ValueError(f"mode_ref: '{mode_ref}' does not name a valid mode declaration in ModeDeclarationGroup")
        return context_port, context_mode_declaration_group, target_mode_declaration

    def create_port_api_options(self,
                                port_name: str | list[str],
                                enable_take_address: bool | None = None,
                                indirect_api: bool | None = None,
                                error_handling: ar_enum.DataTransformationErrorHandling | None = None,
                                port_arg_values: PortDefinedArgumentValueArgType = None,
                                supported_features: SwcSupportedFeatureArgType = None,
                                transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None
                                ) -> None:
        """
        Creates and adds new port-api-options to this SwcInternalBehavior object

        port_name: Name of the port to create options for. It can also be a list of names in case you want to use
                   identical options for multiple ports.
                   Special value is "*" which creates one options object per port found in parent SWC.

        #convenience-method
        """
        swc = self.get_valid_parent()
        # names of ports to process.
        # The bool is used to check if it has been handled or not
        ports_to_process: dict[str, bool] = {}
        if isinstance(port_name, str):
            if port_name == "*":
                for port in swc.ports:
                    ports_to_process[port.name] = False
            else:
                ports_to_process[port_name] = False
        elif isinstance(port_name, Iterable):
            for name in port_name:
                ports_to_process[name] = False
        else:
            raise TypeError(f"port_name: Expected type string or list of string. Got {str(type(port_name))}")
        if len(ports_to_process):
            for port in sorted(swc.ports, key=lambda x: x.name.lower()):
                if port.name in ports_to_process:
                    ports_to_process[port.name] = True
                    option = self._create_port_api_option_internal(port,
                                                                   enable_take_address,
                                                                   indirect_api,
                                                                   error_handling,
                                                                   port_arg_values,
                                                                   supported_features,
                                                                   transformer_status_forwarding)
                    self.append_port_api_option(option)
            for key, value in ports_to_process.items():
                if not value:
                    raise ValueError(f"port_name: '{key}' is not a valid port name in SWC '{swc.name}'")

    def _create_port_api_option_internal(self,
                                         port: PortPrototypeElement,
                                         enable_take_address: bool | None = None,
                                         indirect_api: bool | None = None,
                                         error_handling: ar_enum.DataTransformationErrorHandling | None = None,
                                         port_arg_values: PortDefinedArgumentValueArgType = None,
                                         supported_features: SwcSupportedFeatureArgType = None,
                                         transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None # noqa E501 pylint: disable=C0301
                                         ) -> PortApiOption:
        """
        Creates a single PortApiOption object. The port argument must be a valid port in parent SWC.
        """
        if not isinstance(port, PortPrototype):
            raise TypeError("port: argument must be a valid port")
        if port.ref() is None:
            msg = f"port {port.name} must have a valid reference. Make sure the parent SWC is part of a package"
            raise ValueError(msg)
        return PortApiOption(port.ref(),
                             enable_take_address,
                             indirect_api,
                             error_handling,
                             port_arg_values,
                             supported_features,
                             transformer_status_forwarding)
