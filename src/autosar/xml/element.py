"""
Classes related to AUTOSAR Elements
"""
import re
from collections.abc import Iterable
from typing import Any
from enum import Enum
import abc
import autosar.xml.enumeration as ar_enum


alignment_type_re = re.compile(
    r"[1-9][0-9]*|0[xX][0-9a-fA-F]*|0[bB][0-1]+|0[0-7]*|UNSPECIFIED|UNKNOWN|BOOLEAN|PTR")

# Base classes


class ARObject:
    """
    Base class for all AUTOSAR objects
    """

    @property
    def is_empty(self) -> bool:
        """
        True if no value has been set (everything is None)
        """
        for value in vars(self).values():
            if isinstance(value, list):
                if len(value) > 0:
                    return False
            else:
                if value is not None:
                    return False
        return True

    def _accepted_params(self, params: set):
        """
        Acceped kwarg names during init
        """
        params.update(['tag'])

    def _consume(self, kwargs: dict, attr_name: str | tuple[str, ...], type_name: type) -> None:
        """
        Consume value of primitive type from kwargs and assign to object attribute based on attr_name
        """
        if isinstance(attr_name, tuple):
            target = attr_name[0]
            alternatives = list(attr_name[1:])
        else:
            target = attr_name
            alternatives = None
        if target in kwargs:
            self._assign(target, kwargs[target], type_name)
        elif alternatives is not None:
            for alternative in alternatives:
                if alternative in kwargs:
                    self._assign(target, kwargs[alternative], type_name)
                    break

    def _assign(self, attr_name: str, value: Any, type_name: type) -> None:
        """
        Assign single value to attribute with type check.
        This is a simplified version of _consume.
        """
        if issubclass(type_name, Enum):
            self._set_attr_with_strict_type(attr_name, value, type_name)
        else:
            self._set_attr_with_implicit_cast(attr_name, value, type_name)

    def _assign_optional(self, attr_name: str, value: Any, type_name: type) -> None:
        if value is not None:
            self._assign(attr_name, value, type_name)

    def _set_attr_with_strict_type(self, attr_name: str, value: Any, type_class: type) -> None:
        """
        Sets object attribute only if the value is matches given type-class
        """
        if isinstance(value, type_class):
            setattr(self, attr_name, value)
        else:
            raise TypeError(
                f"Invalid type for parameter '{attr_name}'. Expected type {str(type_class)}, got {str(type(value))}")

    def _set_attr_with_implicit_cast(self, attr_name: str, value: Any, type_class: type) -> None:
        """
        Sets object attribute only if it can be converted to given type.
        """
        if type_class is int:
            new_value = int(value)
        elif type_class is str:
            new_value = str(value)
        elif type_class is float:
            new_value = float(value)
        elif type_class is SwAddrMethodRef:
            if isinstance(value, str):
                new_value = SwAddrMethodRef(value)
            elif isinstance(value, SwAddrMethodRef):
                new_value = value
            else:
                raise TypeError(
                    f"Invalid type '{str(type(value))}'. Expected one of (str, SwAddrMethodRef)")
        elif type_class is SwBaseTypeRef:
            if isinstance(value, str):
                new_value = SwBaseTypeRef(value)
            elif isinstance(value, SwBaseTypeRef):
                new_value = value
            else:
                raise TypeError(
                    f"Invalid type '{str(type(value))}'. Expected one of (str, SwBaseTypeRef)")
        else:
            raise NotImplementedError(type_class)
        setattr(self, attr_name, new_value)

    def _consume_alignment(self, kwargs: dict) -> None:
        """
        Special consume-function for AR:ALIGNMENT-TYPE
        """
        value = kwargs.get('alignment', None)
        if value is not None:
            if isinstance(value, int):
                alignment = value
            elif isinstance(value, str):
                match = alignment_type_re.match(value)
                if match is not None:
                    alignment = value
                else:
                    raise ValueError(f"Invalid alignment value '{value}'")
            else:
                raise TypeError(f"Invalid type for parameter 'alignment'"
                                f". Expected (int, str), got '{str(type(value))}'")
            setattr(self, 'alignment', alignment)

    def _check_params(self, class_name: str, kwargs: dict, accepted_params: set[str]):
        for key in kwargs.keys():
            if key not in accepted_params:
                raise TypeError(
                    f"'{key}'is an invalid keyword argument for {class_name}")


class MultiLanguageReferrable(ARObject):
    """
    Combines Complex-types AR:REFFERABLE and AR:MULTILANGUAGE-REFFERABLE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        self.name = name  # .SHORT-NAME
        self.long_name: MultilanguageLongName | None = None  # .LONG-NAME
        self.parent: 'CollectableElement' = None
        long_name = kwargs.get('long_name', None)
        if long_name is not None:
            if isinstance(long_name, MultilanguageLongName):
                self.long_name = long_name
            else:
                raise TypeError(
                    f'long_name: Expected type "MultilanguageLongName", got "{str(type(long_name))}"')

    def _accepted_params(self, params: set):
        """
        Acceped key names in kwargs during init
        """
        super()._accepted_params(params)
        params.update(['short_name', 'long_name', 'parent'])

    @property
    def short_name(self) -> str | None:
        """
        Alias for .name
        """
        return self.name


class Identifiable(MultiLanguageReferrable):
    """
    Complex-type AR:IDENTIFIABLE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.desc: dict[str, str] | None = None
        self.category = None
        self.admin_data = None
        self.introduction = None
        self.annotations = None
        self.uuid = None
        self._consume(kwargs, 'desc', str)
        self._consume(kwargs, 'category', str)
        self._consume(kwargs, 'uuid', str)

    def _accepted_params(self, params: set):
        """
        Acceped kwarg names during init
        """
        super()._accepted_params(params)
        params.update(['desc', 'category', 'uuid'])


class CollectableElement(Identifiable):
    """
    AR:COLLECTABLE-ELEMENT

    Meta-class that identify either an
    AR:PACKAGE or AR-ELEMENT.
    Both types can be places inside another
    package.

    Type Abstract
    """


class ARElement(CollectableElement):
    """
    AR:AR-ELEMENT

    Base class for all package-elements

    Type: Abstract
    """
# AdminData


class AdminData(ARObject):
    """
    Complex-type AR:ADMIN-DATA
    Type: Concrete
    Tag variants: 'ADMIN-DATA'
    """

    def __init__(self, data: dict | None = None) -> None:
        self.data = data

# Reference classes


class BaseRef(ARObject, abc.ABC):
    """
    Complex-type AR:REF
    Type: Abstract
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes | None = None) -> None:
        self.value = value
        self.dest = dest

    @abc.abstractmethod
    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """
        Subset of ar_enum.IdentifiableSubTypes defining
        which enum valuesa are acceptable for child
        """

    def __str__(self) -> str:
        return self.value


class SwAddrMethodRef(BaseRef):
    """
    SwAddrMethod Reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        return {ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD}


class SwBaseTypeRef(BaseRef):
    """
    SwBaseType Reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.SW_BASE_TYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        return {ar_enum.IdentifiableSubTypes.SW_BASE_TYPE}


class DataConstraintRef(BaseRef):
    """
    DataConstraint Reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.DATA_CONSTR)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        return {ar_enum.IdentifiableSubTypes.DATA_CONSTR}

# Documentation Elements


class Break(ARObject):
    """
    Complex-type AR:BR
    Type: Concrete
    Tag variants: BR

    Same function as the html element.

    """


class EmphasisText(ARObject):
    """
    Complex-type AR:EMPHASIS-TEXT
    Type: Concrete
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
    Complex-type AR:INDEX-ENTRY
    Type: Concrete
    Tag variants: IE

    Index Entry

    Limitations: Doesn't support sub-elements as seen in XML schema.
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Text content


class TechnicalTerm(ARObject):
    """
    Complex-type AR:TT
    Type: Concrete
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
    Complex-type AR:SUPSCRIPT
    Type: Concrete
    Tag variants: SUB

    Subscript is based on the same Complex-type

    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content


class Superscript(ARObject):
    """
    Complex-type AR:SUPSCRIPT
    Type: Concrete
    Tag variants: SUP

    Superscript
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content


class LanguageSpecific(ARObject):
    """
    Complex-type AR:LANGUAGE-SPECIFIC
    Type: Abstract
    """

    def __init__(self, language: ar_enum.Language) -> None:
        assert isinstance(language, ar_enum.Language)
        self.language = language  # Attribute @L


class MixedContentForLongName(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-LONG-NAME
    Type: Abstract
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
            raise TypeError('Unsupported element type: '+str(type(part)))


class MixedContentForOverviewParagraph(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-OVERVIEW-PARAGRAPH
    Type: Abstract
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | TT | E | SUP | SUB | IE
        # Unsupported elements:
        # FT : AR:SL-OVERVIEW-PARAGRAPH
        # TRACE-REF: Complex-type
        # XREF: AR:-XREF-TARGET

    def append(self, part: str | TechnicalTerm | EmphasisText | Subscript | Subscript):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, TechnicalTerm, EmphasisText, Subscript, Subscript, IndexEntry)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: '+str(type(part)))


class LanguageLongName(MixedContentForLongName):
    """
    Complex-type AR:L-LONG-NAME
    Type: Concrete
    Tag: L-4

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
    Complex-type AR:MULTILANGUAGE-LONG-NAME
    Type: Concrete
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
    Complex-type AR:L-OVERVIEW-PARAGRAPH
    Type: Concrete
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
    Complex-type AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
    Type: Concrete
    Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
    """

    def __init__(self,
                 paragraph: None | tuple[ar_enum.Language,
                                         str] | LanguageOverviewParagraph = None) -> None:
        self.elements: list[LanguageOverviewParagraph] = []
        if paragraph is not None:
            if isinstance(paragraph, LanguageOverviewParagraph):
                self.append(paragraph)
            elif isinstance(paragraph, tuple):
                self.append(LanguageOverviewParagraph(
                    paragraph[0], paragraph[1]))
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


class DocumentViewSelectable(ARObject):
    """
    Group AR:DOCUMENT-VIEW-SELECTABLE
    Type: Abstract

    Experiment with named attributes for this class while keeping
    Unknown parent attributes hidden in kwargs

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

    def _accepted_params(self, params: set):
        """
        Acceped key names in kwargs during init
        """
        super()._accepted_params(params)
        params.update(['semantic_information', 'view'])


class Paginateable(DocumentViewSelectable):
    """
    Group AR:PAGINATEABLE
    Type: Abstract

    Experiment with named attributes for this class while keeping
    Unknown parent attributes hidden in kwargs
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

    def _accepted_params(self, params: set):
        """
        Acceped key names in kwargs during init
        """
        super()._accepted_params(params)
        params.update(['page_break', 'keep_with_previous'])


class MixedContentForParagraph(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-PARAGRAPH
    Type: Abstract
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
        if isinstance(part, (str, Break, EmphasisText, IndexEntry, Subscript, Subscript,  TechnicalTerm)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: '+str(type(part)))


class LanguageParagraph(MixedContentForParagraph):
    """
    Complex-type AR:L-PARAGRAPH
    Type: Concrete
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
    Complex-type AR:MULTI-LANGUAGE-PARAGRAPH
    Type: Concrete
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

    def accepted_params(self) -> set[str]:
        """
        Acceped parameter names in kwargs
        """
        params = {'help_entry', 'paragraph'}
        super()._accepted_params(params)


class MixedContentForVerbatim(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-VERBATIM
    Type: Abstract

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
            raise TypeError('Unsupported element type: '+str(type(part)))


class LanguageVerbatim(MixedContentForVerbatim):
    """
    Complex-type AR:L-VERBATIM
    Type: Concrete
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
    Complex-type AR:MULTI-LANGUAGE-VERBATIM
    Type: Concrete
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

    def accepted_params(self) -> set[str]:
        """
        Acceped parameter names in kwargs
        """
        params = {'element', 'help_entry', 'allow_break', 'page_wide', 'float'}
        super()._accepted_params(params)


class DocumentationBlock(ARObject):
    """
    Complex-type AR:DOCUMENTATION-BLOCK
    Type: Concrete
    Tag Variants: 'INTRODUCTION', 'DEF', 'VALUE', 'ANNOTATION-TEXT', 'REMARK'
                  'COND', 'DESCRICPTION', 'RATIONALE', 'DEPENDENCIES', 'USE-CASE',
                  'CONFLICTS', 'SUPPORTING-MATERIAL', 'SW-GENERIC-AXIS-DESC'
    """

    def __init__(self,
                 element: MultiLanguageParagraph | MultiLanguageVerbatim | list[Any] | None = None) -> None:
        self.elements: list[MultiLanguageParagraph |
                            MultiLanguageVerbatim] = []
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
    Type: Abstract
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
    Complex-type AR:ANNOTATION
    Type: Concrete
    """

    def __init__(self,  # pylint: disable=useless-parent-delegation
                 label: MultilanguageLongName | None = None,
                 origin: str | None = None,
                 text: DocumentationBlock | None = None) -> None:
        super().__init__(label, origin, text)

# DataPrototypes


class DataPrototype(Identifiable):
    """
    AR:DATA-PROTOTYPE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.data_def_props = None  # .SW-DATA-DEF-PROPS


class AutosarDataPrototype(DataPrototype):
    """
    AR:AUTOSAR-DATA-PROTOTYPE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.type_ref = None  # .TYPE-TREF


class VariableDataPrototype(AutosarDataPrototype):
    """
    AR:VARIABLE-DATA-PROTOTYPE
    Type: Concrete
    """

    def __init__(self, name: str,  **kwargs) -> None:
        super().__init__(name, kwargs)
        self.init_value = None  # .INIT-VALUE
        # .VARIATION-POINT not supported

# Data Dictionary Elements


class BaseType(ARElement):
    """
    Merge of Complex-types AR:BASE-TYPE, AR:BASE-TYPE-DEFINITION
    AR:BASE-TYPE-DIRECT-DEFINITION
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.size: int | None = None  # .BASE-TYPE-SIZE
        self.max_size: int | None = None  # .MAX-BASE-TYPE-SIZE
        self.encoding: str | None = None  # .BASE-TYPE-ENCODING
        self.alignment: int | None = None  # .MEM-ALIGNMENT
        self.byte_order: ar_enum.ByteOrder | None = None  # .BYTE-ORDER
        self.native_declaration: str | None = None  # .NATIVE-DECLARATION


class SwBaseType(BaseType):
    """
    Complex-type AR:SW-BASE-TYPE
    Type: Concrete
    Tag variants: SW-BASE-TYPE
    """

    def __init__(self, name: str,
                 size: int | None = None,
                 max_size: int | None = None,
                 encoding: str | None = None,
                 alignment: int | None = None,
                 byte_order: ar_enum.ByteOrder | None = None,
                 native_declaration: str | None = None,
                 **kwargs) -> None:
        self._check_params(self.__class__.__name__,
                           kwargs, self.accepted_params())
        super().__init__(name, kwargs)
        self.size = size
        self.max_size = max_size
        self.encoding = encoding
        self.alignment = alignment
        self.byte_order = byte_order
        self.native_declaration = native_declaration

    def accepted_params(self) -> set[str]:
        """
        Accepted kwarg parameter names during init
        """
        params = set()
        super()._accepted_params(params)
        return params

    def ref(self) -> SwAddrMethodRef:
        """
        Reference
        """
        ref_parts: list[str] = [self.name]
        self.parent.update_ref_parts(ref_parts)
        value = '/'.join(reversed(ref_parts))
        return SwAddrMethodRef(value)


class SwBitRepresentation(ARObject):
    """
    SW-BIT-REPRESENTATION
    Type: Concrete
    """

    def __init__(self,
                 position: int | None = None,
                 num_bits: int | None = None) -> None:
        super().__init__()
        self.position: int | None = None
        self.num_bits: int | None = None
        self._assign_optional('position', position, int)
        self._assign_optional('num_bits', num_bits, int)


class SwDataDefPropsConditional(ARObject):
    """
    Merge of Complex-types AR:SW-DATA-DEF-PROPS-CONDITIONAL and
    AR:SW-DATA-DEF-PROPS-CONTENT
    Type: Concrete
    Tag Variants: SW-DATA-DEF-PROPS-CONDITIONAL
    """

    def __init__(self,
                 bit_representation: SwBitRepresentation | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 **kwargs) -> None:
        # .DISPLAY-PRESENTATION
        self.display_presentation: ar_enum.DisplayPresentation | None = None
        self.step_size: float | None = None  # .STEP-SIZE : AR:FLOAT
        # .SW-VALUE-BLOCK-SIZE-MULTS not supported as it seems related to VariantHandling
        self.annotations: list[Annotation] = []  # .ANNOTATIONS
        self.sw_addr_method_ref = None  # .SW-ADDR-METHOD-REF
        self.alignment = None  # .SW-ALIGNMENT
        self.base_type_ref = None  # .BASE-TYPE-REF
        self.bit_representation: SwBitRepresentation | None = None  # .SW-BIT-REPRESENTATION
        self.calibration_access: ar_enum.SwCalibrationAccess | None = None  # .SW-CALIBRATION-ACCESS
        self.value_block_size = None  # .SW-VALUE-BLOCK-SIZE
        self.calprm_axis_set = None  # .SW-CALPRM-AXIS-SET
        self.text_props = None  # .SW-TEXT-PROPS
        self.comparision_variables = None  # .SW-COMPARISON-VARIABLES
        self.compu_method_ref = None
        self.data_constraint_ref = None
        self.data_dependency = None  # .SW-DATA-DEPENDENCY
        self.display_format = None  # DISPLAY-FORMAT
        self.implementation_data_type_ref = None  # .IMPLEMENTATION-DATA-TYPE-REF
        self.host_variable = None  # .SW-HOST-VARIABLE (Complex content)
        self.impl_policy = None  # .SW-IMPL-POLICY
        self.additional_native_type_qualifier = None  # .ADDITIONAL-NATIVE-TYPE-QUALIFIER
        self.intended_resolution = None  # .SW-INTENDED-RESOLUTION
        self.interpolation_method = None  # .SW-INTENDED-METHOD
        self.invalid_value = None  # .INVALID-VALUE
        self.mc_function = None  # .MC-FUNCTION
        self.is_virtual = None  # .IS-VIRTUAL
        # .SW-POINTER-TARGET-PROPS (Complex content)
        self.sw_pointer_target_props = None
        self.sw_record_layout_ref = None  # .SW-RECORD-LAYOUT-REF
        self.sw_record_layout_ref_dest = None  # .SW-RECORD-LAYOUT-REF.dest
        self.sw_refresh_timing = None  # .SW-REFRESH-TIMING (Complex content)
        self.unit_ref = None  # .UNIT-REF
        self.value_axis_data_type_ref = None  # .VALUE-AXIS-DATA-TYPE-REF
        self.value_axis_data_type_ref_dest = None  # .VALUE-AXIS-DATA-TYPE-REF.DEST

        self._check_params(self.__class__.__name__,
                           kwargs, self.accepted_params())

        self._consume(kwargs, 'display_presentation',
                      ar_enum.DisplayPresentation)
        self._consume(kwargs, 'step_size', float)
        annotations = kwargs.get('annotations', None)
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
        self._consume(kwargs, 'sw_addr_method_ref', SwAddrMethodRef)
        self._consume_alignment(kwargs)
        self._consume(kwargs, 'base_type_ref', SwBaseTypeRef)
        if bit_representation is not None:
            if not isinstance(bit_representation, SwBitRepresentation):
                raise TypeError(f"param bit_representation: Invalid type '{str(type(bit_representation))}'."
                                " Expected 'SwBitRepresentation'")
            self.bit_representation = bit_representation
        self._assign_optional('calibration_access', calibration_access, ar_enum.SwCalibrationAccess)

    def accepted_params(self) -> set[str]:
        """
        Accepted parameter names in kwargs during init
        """
        return {'display_presentation',
                'step_size',
                'annotations',
                'sw_addr_method_ref',
                'alignment',
                'base_type_ref',
                'bit_representation'
                }


class SwAddrMethod(ARElement):
    """
    Complex-type AR:SW-ADDR-METHOD
    Type: Concrete:
    Tag Variants: SW-ADDR-METHOD
    """

    def __init__(self, name: str, **kwargs) -> None:
        self._check_params(self.__class__.__name__,
                           kwargs, self.accepted_params())
        super().__init__(name, kwargs)
        self.memory_allocation_keyword_policy = None  # .MEMORY-ALLOCATION-KEYWORD-POLICY
        self.options = []  # .OPTIONS
        self.section_initialization_policy = None  # .SECTION-INITIALIZATION-POLICY
        self.section_type = None  # .SECTION-TYPE

    def accepted_params(self) -> set[str]:
        """
        Accepted kwarg parameters during init
        """
        params = {'memory_allocation_keyword_policy',
                  'options',
                  'section_initialization_policy',
                  'section_type'}
        super()._accepted_params(params)
        return params

    def ref(self) -> SwAddrMethodRef:
        """
        Reference
        """
        ref_parts: list[str] = [self.name]
        self.parent.update_ref_parts(ref_parts)
        value = '/'.join(reversed(ref_parts))
        return SwAddrMethodRef(value)


class SwDataDefProps(ARObject):
    """
    SW-DATA-DEF-PROPS
    Type: Concrete
    """

    def __init__(self, variant: "SwDataDefPropsConditional" = None) -> None:
        super().__init__()
        self.variants = []  # .SW-DATA-DEF-PROPS-VARIANTS
        if variant is not None:
            if isinstance(variant, SwDataDefPropsConditional):
                self.variants.append(variant)
            else:
                raise ValueError(
                    "value of 'variant' must be of type SwDataDefPropsConditional")


# !!UNFINISHED!! Data Types

class ARDataType(ARElement):
    """
    Element AUTOSAR-DATA-TYPE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.sw_data_def_props: None | SwDataDefProps = kwargs.get(
            'sw_data_def_props', None)

    def accepted_params(self) -> set[str]:
        "Acceped names in kwargs during init"
        params = {'sw_data_def_props'}
        super()._accepted_params(params)
        return params


class ImplementationDataType(ARDataType):
    """
    IMPLEMENTATION-DATA-TYPE
    Type: Concrete
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        self._check_params(self.__class__.__name__,
                           kwargs, self.accepted_params())
        super().__init__(name, kwargs)

    def accepted_params(self) -> set[str]:
        "Acceped names in kwargs during init"
        params = {'dynamic_array_size_profile',
                  'is_struct_with_optional_element',
                  'sub_elements',
                  'sympol_props',
                  'type_emitter'
                  'sw_data_def_props'}
        super()._accepted_params(params)
        return params

# !!UNFINISHED!! Port Interfaces


class PortInterface(ARElement):
    """
    Implements AR:PORT-INTERFACE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.is_service: None | bool = None
        self.namespaces = None
        self.service_kind: None | ar_enum.ServiceKind = None


class DataInterface(PortInterface):
    """
    AR-DATA-INTERFACE
    IsAbstract: True

    Base class for data-concerned interfaces (as opposed to operations-based)
    """


class SenderReceiverInterface(DataInterface):
    """
    AR-SENDER-RECEIVER-INTERFACE
    Type: Concrete

    Base class for data-concerned interfaces (as opposed to operations-based)
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, kwargs)
        self.data_elements = []  # .DATA-ELEMENTS
        self.invalidation_policies = None  # .INVALIDATION-POLICYS
        # .META-DATA-ITEM-SETS not supported

# !!UNFINISHED!! Component Types


class SoftwareComponentType(ARElement):
    """
    Implements AR:SW-COMPONENT-TYPE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.documentations = None  # AR:SW-COMPONENT-DOCUMENTATIONS
        self.consistency_needs = None  # AR:CONSISTENCY-NEEDSS
        self.ports = None  # AR:PORTS
        self.port_groups = None  # AR:PORT_GROUPS
        self.swc_mapping_constraint_refs = None  # AR:SWC-MAPPING-CONSTRAINT-REFS
        self.unit_group_refs = None  # AR:UNIT-GROUP-REFS


class AtomicSoftwareComponentType(SoftwareComponentType):
    """
    Implements AR:ATOMIC-SW-COMPONENT-TYPE
    Type: Abstract
    """

    def __init__(self, name: str, kwargs: dict) -> None:
        super().__init__(name, kwargs)
        self.internal_behaviors = None  # AR:INTERNAL-BEHAVIORS
        self.symbol_props = None  # AR:SYMBOL-PROPS


class ApplicationSoftwareComponentType(AtomicSoftwareComponentType):
    """
    Implements AR:APPLICATION-SW-COMPONENT-TYPE
    Type: Concrete
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, kwargs)
