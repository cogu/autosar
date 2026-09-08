"""Documentation elements."""

from __future__ import annotations

from collections.abc import Iterable
import datetime
import re
from typing import Any, Union

from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import AdminData, SingleLanguageText
import autosar.xml.enumeration as ar_enum

date_re = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2})(T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|([+\-][0-9]{2}:[0-9]{2})))?")

revision_label_string_re = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+([\._;].*)?")


class Break(ARObject):
    """
    Complex type AR:BR
    Tag variants: 'BR'

    Same function as the html element.
    """


class Date(ARObject):
    """
    Complex type AR:DATE
    Tag variants: 'DATE'

    Examples:
    2009-07-23
    2009-07-23T14:38:00+01:00
    2009-07-23T13:38:00Z
    """

    def __init__(self, value: str | datetime.datetime | datetime.date) -> None:
        self.value: datetime.date | datetime.datetime
        if isinstance(value, str):
            self.value = self._create_from_string(value)
        elif isinstance(value, (datetime.date, datetime.datetime)):
            self.value = value
        else:
            raise TypeError(f"value: Expected string or datetime object. Got {str(type(value))}")

    def _create_from_string(self, value: str) -> datetime.date | datetime.datetime:
        match = date_re.match(value)
        if match is None or len(match.group(0)) != len(value):
            raise ValueError(f"Date string '{value}' doesn't pass regular expression check")
        if match.lastindex == 1:
            return datetime.date.fromisoformat(value)
        text = value
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(text)

    def __str__(self) -> str:
        """Convert to ISO format date/time string."""
        text = self.value.isoformat()
        if text.endswith("+00:00"):
            text = text[:-6] + "Z"
        return text


class RevisionLabelString(ARObject):
    """
    Complex type AR:REVISION-LABEL-STRING
    Tag variants: 'AR-RELEASE-VERSION' | 'ECU-EXTRACT-VERSION' | 'ECUC-DEF-EDITION' |
                  'PRODUCT-RELEASE' | 'REVISION-LABEL' | 'REVISION-LABEL-P-1' |
                  'REVISION-LABEL-P-2' | 'SW-VERSION' | 'SYSTEM-VERSION'
    """

    def __init__(self, value: str):
        match = revision_label_string_re.match(value)
        if match is None or len(match.group(0)) != len(value):
            raise ValueError(f"RevisionLabelString string '{value}' doesn't pass regular expression check")
        self.value = value

    def __str__(self) -> str:
        """Convert to string representation."""
        return self.value


class EmphasisText(ARObject):
    """
    Complex type AR:EMPHASIS-TEXT
    Tag variants: 'E'

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
    Tag variants: 'IE'

    Index Entry

    Limitations: Doesn't support sub-elements as seen in XML schema.
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Text content


class TechnicalTerm(ARObject):
    """
    Complex type AR:TT
    Tag variants: 'TT'

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
    Tag variants: 'SUB'

    Subscript is based on the same Complex type as superscript

    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content


class Superscript(ARObject):
    """
    Complex type AR:SUPSCRIPT
    Tag variants: 'SUP'

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
    Group AR:LANGUAGE-SPECIFIC
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
    Tag variants: 'L-4'

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
    Tag variants: 'CHANGE' | 'DESC' | 'ITEM-LABEL' | 'REASON'
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

    @convenience_function
    @classmethod
    def make(cls, language: ar_enum.Language, paragraph: str):
        """

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
    Group AR:MIXED-CONTENT-FOR-UNIT-NAMES
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
    Tag variants: 'DISPLAY-NAME' | 'PRM-UNIT' | 'UNIT-DISPLAY-NAME'
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
    Tag variants: 'ANNOTATION-TEXT' | 'BLUEPRINT-CONDITION' | 'BLUEPRINT-DERIVATION-GUIDE' |
                  'BLUEPRINT-MAPPING-GUIDE' | 'COND' | 'CONFLICTS' | 'DEF' | 'DEPENDENCIES' |
                  'DESCRIPTION' | 'INTRODUCTION' | 'MSR-QUERY-RESULT-P-2' | 'RATIONALE' |
                  'REMARK' | 'SUPPORTING-MATERIAL' | 'SW-GENERIC-AXIS-DESC' | 'USE-CASE' |
                  'VALUE'
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


class LanguagePlainText(LanguageSpecific):
    """
    Complex type AR:L-PLAIN-TEXT
    Tag variants: 'L-10'
    """

    def __init__(self, language: ar_enum.Language, text: str = "") -> None:
        super().__init__(language)
        self.text = text


LanguagePlainTextArgType = SingleLanguageText | LanguagePlainText | list[SingleLanguageText] | list[LanguagePlainText]


class MultiLanguagePlainText(ARObject):
    """
    Complex type AR:MULTI-LANGUAGE-PLAIN-TEXT
    Tag variants: 'GENERIC-MATH' | 'TEX-MATH' | 'USED-LANGUAGES'
    """

    def __init__(self,
                 elements: LanguagePlainTextArgType | None = None) -> None:
        super().__init__()
        self.elements: list[LanguagePlainText] = []
        if elements:
            if isinstance(elements, (tuple, LanguagePlainText)):
                self.append(elements)
            elif isinstance(elements, Iterable):
                for part in elements:
                    self.append(part)
            else:
                expected_type = "tuple[enum Language, str], LanguagePlainText or list"
                actual_type = str(type(elements))
                raise TypeError(f"elements: Expected {expected_type}. Got {actual_type}")

    def append(self, element: SingleLanguageText | LanguagePlainText) -> None:
        """
        Append element to internal list of elements
        """
        if isinstance(element, tuple):
            self.elements.append(LanguagePlainText(*element))
        elif isinstance(element, LanguagePlainText):
            self.elements.append(element)
        else:
            expected_type = "tuple[enum Language, str] or LanguagePlainText"
            actual_type = str(type(element))
            raise TypeError(f"element: Expected type {expected_type}, got {actual_type}")


__all__ = [
    "date_re",
    "revision_label_string_re",
    "Break",
    "Date",
    "RevisionLabelString",
    "EmphasisText",
    "IndexEntry",
    "TechnicalTerm",
    "Subscript",
    "Superscript",
    "LanguageSpecific",
    "MixedContentForLongName",
    "MixedContentForOverviewParagraph",
    "LanguageLongName",
    "MultilanguageLongName",
    "LanguageOverviewParagraph",
    "MultiLanguageOverviewParagraph",
    "DocumentViewSelectable",
    "Paginateable",
    "MixedContentForParagraph",
    "LanguageParagraph",
    "MultiLanguageParagraph",
    "MixedContentForVerbatim",
    "LanguageVerbatim",
    "MultiLanguageVerbatim",
    "MixedContentForUnitNames",
    "SingleLanguageUnitNames",
    "DocumentationBlock",
    "GeneralAnnotation",
    "Annotation",
    "Describable",
    "LanguagePlainText",
    "MultiLanguagePlainText",
    "LanguagePlainTextArgType",
]
