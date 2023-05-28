"""
ARXML writer module
"""
from io import StringIO
from typing import TextIO
import math
import decimal
import autosar.xml.document as ar_document
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
# import autosar.xml.exception
import autosar.xml.package as ar_package

TupleList = list[tuple[str, str]]


class _XMLWriter:
    def __init__(self, indentation_step: int) -> None:
        self.file_path: str = None
        self.fh: TextIO = None  # pylint: disable=invalid-name
        self.indentation_char: str = ' '
        # Number of characters (spaces) per indendation
        self.indentation_step = indentation_step
        self.indentation_level: int = 0  # current indentation level
        self.indentation_str: str = ''
        self.tag_stack = []  # stack of tag names
        self.line_number: int = 0

    def _str_open(self):
        self.fh = StringIO()
        self.line_number = 1
        self.indentation_level = 0
        self.indentation_str = ''
        self.tag_stack.clear()

    def _open(self, file_path: str):
        self.fh = open(file_path, 'w', encoding='utf-8')
        self.file_path = file_path
        self.line_number = 1
        self.indentation_level = 0
        self.indentation_str = ''
        self.tag_stack.clear()

    def _close(self):
        self.fh.close()

    def _indent(self):
        self.indentation_level += 1
        self.indentation_str = self.indentation_char * \
            (self.indentation_level * self.indentation_step)

    def _dedent(self):
        self.indentation_level -= 1
        if self.indentation_level == 0:
            self.indentation_str = ''
        else:
            self.indentation_str = self.indentation_char * \
                (self.indentation_level * self.indentation_step)

    def _add_line(self, text):
        if self.line_number > 1:
            self.fh.write('\n')
        self.line_number += 1
        self.fh.write(self.indentation_str)
        self.fh.write(text)

    def _add_inline_text(self, text):
        self.fh.write(text)

    def _add_child(self, tag: str, attr: TupleList = None):
        if attr:
            self._add_line(f'<{tag} {self._attr_to_str(attr)}>')
        else:
            self._add_line(f'<{tag}>')
        self.tag_stack.append(tag)
        self._indent()

    def _leave_child(self):
        tag = self.tag_stack.pop()
        self._dedent()
        self._add_line(f'</{tag}>')

    def _begin_line(self, tag: str, attr: None | TupleList = None):
        if self.line_number > 1:
            self.fh.write('\n')
        self.line_number += 1
        self.fh.write(self.indentation_str)
        if attr is None or len(attr) == 0:
            text = f'<{tag}>'
        else:
            text = f'<{tag} {self._attr_to_str(attr)}>'
        self._add_inline_text(text)

    def _end_line(self, tag: str):
        text = f'</{tag}>'
        self.fh.write(text)

    def _add_content(self, tag: str, content: str = '', attr: TupleList = None, inline: bool = False):
        if attr:
            if content:
                text = f'<{tag} {self._attr_to_str(attr)}>{content}</{tag}>'
            else:
                text = f'<{tag} {self._attr_to_str(attr)}/>'
        else:
            if content:
                text = f'<{tag}>{content}</{tag}>'
            else:
                text = f'<{tag}/>'
        if inline:
            self._add_inline_text(text)
        else:
            self._add_line(text)

    def _attr_to_str(self, attr: TupleList) -> str:
        """
        Converts pairs (2-tuples) into attribute XML string
        """
        parts = [f'{elem[0]}="{elem[1]}"' for elem in attr]
        return ' '.join(parts)

    def _format_float(self, value: float) -> str:
        """
        Formats a float into a printable number string.
        The fractional part will automatically be stripped if possible
        """
        if math.isinf(value):
            return '-INF' if value < 0 else 'INF'
        elif math.isnan(value):
            return 'NaN'
        else:
            tmp = decimal.Decimal(str(value))
            return tmp.quantize(decimal.Decimal(1)) if tmp == tmp.to_integral() else tmp.normalize()


class Writer(_XMLWriter):
    """
    ARXML writer class
    """

    def __init__(self) -> None:
        super().__init__(indentation_step=2)
        # Elements found in AR:PACKAGE
        self.switcher_collectable = {
            # Package
            'Package': self._write_package,
            # DataDictionary Elements
            'SwBaseType': self._write_sw_base_type,
            'SwAddrMethod': self._write_sw_addr_method,
        }
        # Elements used only for unit test purposes
        self.switcher_non_collectable = {
            # Documentation elements
            'Annotation': self._write_annotation,
            'Break': self._write_break,
            'DocumentationBlock': self._write_documentation_block,
            'EmphasisText': self._write_emphasis_text,
            'IndexEntry': self._write_index_entry,
            'MultilanguageLongName': self._write_multi_language_long_name,
            'MultiLanguageOverviewParagraph': self._write_multi_language_overview_paragraph,
            'MultiLanguageParagraph': self._write_multi_language_paragraph,
            'MultiLanguageVerbatim': self._write_multi_language_verbatim,
            'LanguageLongName': self._write_language_long_name,
            'LanguageParagraph': self._write_language_paragraph,
            'LanguageVerbatim': self._write_language_verbatim,
            'Package': self._write_package,
            'Superscript': self._write_superscript,
            'Subscript': self._write_subscript,
            'TechnicalTerm': self._write_technical_term,
            # DataDictionary Elements
            'SwDataDefPropsConditional': self._write_sw_data_def_props_conditional,
            'SwBaseTypeRef': self._write_sw_base_type_ref,
            'SwBitRepresentation': self._write_sw_bit_represenation,
        }
        self.switcher_all = {}  # All concrete elements (used for unit testing)
        self.switcher_all.update(self.switcher_collectable)
        self.switcher_all.update(self.switcher_non_collectable)

    def write_str(self, document: ar_document.Document, skip_root_attr: bool = True) -> str:
        """
        Serializes the document to string.
        """
        self._str_open()
        self._write_document(document, skip_root_attr)
        return self.fh.getvalue()

    def write_file(self, document: ar_document.Document, file_path: str):
        """
        Serialized the document to file
        """
        self._open(file_path)
        self._write_document(document)
        self._close()

    def write_str_elem(self, elem: ar_element.ARObject, tag: str | None = None):
        """
        Writes single ARXML element as string
        """
        self._str_open()
        class_name = elem.__class__.__name__
        write_method = self.switcher_all.get(class_name, None)
        if write_method is not None:
            if tag is not None:
                write_method(elem, tag)
            else:
                write_method(elem)
        else:
            raise NotImplementedError(
                f"Found no writer for class {class_name}")
        return self.fh.getvalue()

    def write_file_elem(self, elem: ar_element.ARElement, file_path: str):
        """
        Writes single ARXML element to file
        """
        self._open(file_path)
        class_name = elem.__class__.__name__
        write_method = self.switcher_collectable.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for {class_name}")
        self._close()

    # Abstract base classes

    def _write_referrable(self, elem: ar_element.MultiLanguageReferrable):
        """
        Writes groups AR:REFERRABLE and AR:MULTILANGUAGE-REFFERABLE
        Type: Abstract
        """
        self._add_content('SHORT-NAME', elem.name)
        if elem.long_name is not None:
            self._write_multi_language_long_name(elem.long_name, 'LONG-NAME')

    def _collect_identifiable_attributes(self, elem: ar_element.Identifiable, attr: TupleList):
        if elem.uuid is not None:
            attr.append(('UUID', elem.uuid))
        if len(attr) > 0:
            return attr
        return None

    def _write_identifiable(self, elem: ar_element.Identifiable) -> None:
        """
        Writes group AR:IDENTIFIABLE
        Type: Abstract
        """
        if elem.desc:
            self._write_multi_language_overview_paragraph(elem.desc, 'DESC')
        if elem.category:
            self._add_content('CATEGORY', elem.category)
        if elem.admin_data:
            self._write_admin_data(elem.admin_data)
        if elem.introduction:
            self._write_documentation_block(elem.introduction, 'INTRODUCTION')
        if elem.annotations:
            self._write_annotations(elem.annotations)

    # AdminData

    def _write_admin_data(self, data: dict) -> None:
        """
        Writes Complex-type AR:ADMIN-DATA
        Type: Concrete
        Tag variants: 'ADMIN-DATA'
        """

    # AUTOSAR Document

    def _write_document(self, document: ar_document.Document, skip_root_attr: bool = False):
        self._add_line('<?xml version="1.0" encoding="utf-8"?>')
        if skip_root_attr:
            self._add_child("AUTOSAR")
        else:
            self._add_child("AUTOSAR", [('xsi:schemaLocation',
                                         f'http://autosar.org/schema/r4.0 {document.schema_file}'),
                                        ('xmlns', 'http://autosar.org/schema/r4.0'),
                                        ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')])
        if len(document.packages) > 0:
            self._write_packages(document.packages)
        self._leave_child()

    def _write_packages(self, packages: list[ar_package.Package]):
        self._add_child("AR-PACKAGES")
        for package in packages:
            self._write_package(package)
        self._leave_child()

    # AUTOSAR PACKAGE

    def _write_package(self, package: ar_package.Package) -> None:
        """
        Write AR-PACKAGE element
        Type: Concrete
        """
        attr: TupleList = []
        self._collect_identifiable_attributes(package, attr)
        self._add_child("AR-PACKAGE", attr)
        self._write_referrable(package)
        self._write_identifiable(package)
        if len(package.elements) > 0:
            self._write_package_elements(package)
        self._leave_child()

    def _write_package_elements(self, package: ar_package.Package) -> None:
        self._add_child('ELEMENTS')
        for elem in package.elements:
            class_name = elem.__class__.__name__
            write_method = self.switcher_collectable.get(class_name, None)
            if write_method is not None:
                write_method(elem)
            else:
                raise NotImplementedError(
                    f"Package: Found no writer for {class_name}")
        self._leave_child()

    # Documentation Elements

    def _write_annotation(self, elem: ar_element.Annotation) -> None:
        """
        Writes AR:ANNOTATION
        Type: Concrete
        """
        assert isinstance(elem, ar_element.Annotation)
        tag = 'ANNOTATION'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_general_annotation(elem)
            self._leave_child()

    def _write_annotations(self, elements: list[ar_element.Annotation]) -> None:
        """
        Writes an unbounded list of AR:ANNOTATION
        """
        tag = 'ANNOTATIONS'
        if elements:
            for elem in elements:
                self._add_child(tag)
                self._write_annotation(elem)
                self._leave_child()
        else:
            self._add_content(tag)

    def _write_break(self, elem: ar_element.Break, inline=True) -> None:
        """
        Writes AR:BR
        Type: Concrete
        """
        assert isinstance(elem, ar_element.Break)
        self._add_content('BR', '', inline=inline)

    def _write_documentation_block(self, elem: ar_element.DocumentationBlock, tag: str):
        """
        Writes AR:DOCUMENTATION-BLOCK
        Type: Concrete
        Tag Variants: Too many to list
        """
        assert isinstance(elem, ar_element.DocumentationBlock)
        if not elem.elements:
            self._add_content(tag)
        else:
            self._add_child(tag)
            for child_elem in elem.elements:
                if isinstance(child_elem, ar_element.MultiLanguageParagraph):
                    self._write_multi_language_paragraph(child_elem)
                elif isinstance(child_elem, ar_element.MultiLanguageVerbatim):
                    self._write_multi_language_verbatim(child_elem)
                else:
                    raise NotImplementedError(str(type(child_elem)))
            self._leave_child()

    def _write_emphasis_text(self, elem: ar_element.EmphasisText, inline=True):
        """
        Writes AR:EMPHASIS-TEXT
        Type: Concrete
        TagName: E
        """
        assert isinstance(elem, ar_element.EmphasisText)
        attr = self._collect_emphasis_text_attributes(elem)
        if len(elem.elements) == 1 and isinstance(elem.elements[0], str):
            self._add_content('E', elem.elements[0], attr, inline=inline)
        else:
            raise NotImplementedError(
                'EMPHASIS-TEXT currently supports single str element only')

    def _collect_emphasis_text_attributes(self, elem: ar_element.EmphasisText) -> None | TupleList:
        attr: TupleList = []
        if elem.color is not None:
            attr.append(('COLOR', elem.color))
        if elem.font is not None:
            attr.append(('FONT', ar_enum.enum_to_xml(elem.font)))
        if elem.type is not None:
            attr.append(('TYPE', ar_enum.enum_to_xml(elem.type)))
        if len(attr) > 0:
            return attr
        return None

    def _write_index_entry(self, elem: ar_element.IndexEntry, inline=True):
        """
        Writes IndexEntry (AR:INDEX-ENTRY)
        Type: Concrete
        """
        assert isinstance(elem, ar_element.IndexEntry)
        self._add_content('IE', elem.text, inline=inline)

    def _write_technical_term(self, elem: ar_element.TechnicalTerm, inline=True):
        """
        Writes AR:TT
        Type: Concrete
        TagName: TT
        """
        assert isinstance(elem, ar_element.TechnicalTerm)
        attr: TupleList = []
        self._collect_technical_term_attributes(elem, attr)
        self._add_content('TT', elem.text, attr, inline)

    def _collect_technical_term_attributes(self, elem: ar_element.TechnicalTerm, attr: TupleList):
        """
        Collects attributes from attributeGroup AR:TT
        """
        if elem.tex_render is not None:
            attr.append(('TEX-RENDER', elem.tex_render))
        if elem.type is not None:
            attr.append(('TYPE', elem.type))

    def _write_superscript(self, elem: ar_element.Superscript, inline=True):
        """
        Writes Superscript (AR:SUPSCRIPT)
        Type: Concrete
        """
        assert isinstance(elem, ar_element.Superscript)
        self._add_content('SUP', elem.text, inline=inline)

    def _write_subscript(self, elem: ar_element.Subscript, inline=True):
        """
        Writes Subscript (AR:SUPSCRIPT)
        Type: Concrete
        """
        assert isinstance(elem, ar_element.Subscript)
        self._add_content('SUB', elem.text, inline=inline)

    def _write_multi_language_long_name(self, elem: ar_element.MultilanguageLongName, tag: str) -> None:
        """
        Writes complexType AR:MULTILANGUAGE-LONG-NAME
        Type: Concrete
        Tag variants: 'LABEL' | 'LONG-NAME'
        """
        # assert isinstance(elem.tag, str)
        self._add_child(tag)
        for child_elem in elem.elements:
            self._write_language_long_name(child_elem)
        self._leave_child()

    def _write_language_long_name(self, elem: ar_element.LanguageLongName):
        """
        Writes complexType AR:L-LONG-NAME
        Type: Concrete
        """
        assert isinstance(elem, ar_element.LanguageLongName)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-4'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.IndexEntry):
                self._write_index_entry(part, inline=True)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part, inline=True)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: '+str(type(part)))
        self._end_line(tag)

    def _collect_language_specific_attr(self, elem: ar_element.LanguageSpecific, attr: TupleList) -> None:
        """
        Collects attributes from attributeGroup AR:LANGUAGE-SPECIFIC
        """
        attr.append(('L', ar_enum.enum_to_xml(elem.language))
                    )  # The L attribute is mandatory

    def _write_multi_language_overview_paragraph(self, elem: ar_element.MultiLanguageOverviewParagraph, tag: str) -> None:
        """
        Writes complexType AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
        """
        if tag not in {'DESC', 'ITEM-LABEL', 'CHANGE', 'REASON'}:
            raise ValueError('Invalid tag parameter: ' + tag)
        self._add_child(tag)
        for child_elem in elem.elements:
            self._write_language_overview_paragraph(child_elem)
        self._leave_child()

    def _write_multi_language_verbatim(self, elem: ar_element.MultiLanguageVerbatim) -> None:
        """
        Writes complexType AR:MULTI-LANGUAGE-VERBATIM
        Type: Concrete
        Tag variants: 'VERBATIM'
        """
        assert isinstance(elem, ar_element.MultiLanguageVerbatim)
        attr: TupleList = []
        self._collect_document_view_selectable_attributes(elem, attr)
        self._collect_paginateable_attributes(elem, attr)
        self._collect_multi_language_verbatim_attributes(elem, attr)
        self._add_child('VERBATIM', attr)
        for child_elem in elem.elements:
            self._write_language_verbatim(child_elem)
        self._leave_child()

    def _collect_multi_language_verbatim_attributes(self,
                                                    elem: ar_element.MultiLanguageVerbatim,
                                                    attr: TupleList):
        """
        Collects attributes from attributeGroup AR:MULTI-LANGUAGE-VERBATIM
        """
        if elem.allow_break is not None:
            attr.append(('ALLOW-BREAK', elem.allow_break))
        if elem.float is not None:
            attr.append(('FLOAT', ar_enum.enum_to_xml(elem.float)))
        if elem.help_entry is not None:
            attr.append(('HELP-ENTRY', elem.help_entry))
        if elem.page_wide is not None:
            attr.append(('PGWIDE', ar_enum.enum_to_xml(elem.page_wide)))

    def _write_language_overview_paragraph(self, elem: ar_element.LanguageOverviewParagraph) -> None:
        """
        Writes complexType AR:L-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'L-2'
        """
        assert isinstance(elem, ar_element.LanguageOverviewParagraph)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-2'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Break):
                self._write_break(part, inline=True)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.IndexEntry):
                self._write_index_entry(part, inline=True)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part, inline=True)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: '+str(type(part)))
        self._end_line(tag)

    def _write_language_paragraph(self, elem: ar_element.LanguageParagraph) -> None:
        """
        Writes complexType AR:L-PARAGRAPH
        Type: Concrete
        Tag variants: 'L-1'
        """
        assert isinstance(elem, ar_element.LanguageParagraph)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-1'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Break):
                self._write_break(part, inline=True)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.IndexEntry):
                self._write_index_entry(part, inline=True)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part, inline=True)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: '+str(type(part)))
        self._end_line(tag)

    def _write_language_verbatim(self, elem: ar_element.LanguageVerbatim) -> None:
        """
        Writes complexType AR:L-VERBATIM
        Type: Concrete
        Tag variants: 'L-5'
        """
        assert isinstance(elem, ar_element.LanguageVerbatim)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-5'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Break):
                self._write_break(part, inline=True)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: '+str(type(part)))
        self._end_line(tag)

    def _write_multi_language_paragraph(self, elem: ar_element.MultiLanguageParagraph) -> None:
        """
        Writes complexType AR:MULTI-LANGUAGE-PARAGRAPH
        Type: Concrete
        Tag variants: 'P'
        """
        assert isinstance(elem, ar_element.MultiLanguageParagraph)
        attr: TupleList = []
        self._collect_document_view_selectable_attributes(elem, attr)
        self._collect_paginateable_attributes(elem, attr)
        self._collect_multi_language_paragraph_attributes(elem, attr)
        self._add_child('P', attr)
        for child_elem in elem.elements:
            self._write_language_paragraph(child_elem)
        self._leave_child()

    def _collect_multi_language_paragraph_attributes(self,
                                                     elem: ar_element.MultiLanguageParagraph,
                                                     attr: TupleList):
        """
        Collects attributes from attributeGroup AR:MULTI-LANGUAGE-PARAGRAPH
        """
        if elem.help_entry is not None:
            attr.append(('HELP-ENTRY', elem.help_entry))

    def _collect_document_view_selectable_attributes(self,
                                                     elem: ar_element.DocumentViewSelectable,
                                                     attr: TupleList):
        """
        Collects attributes from attributeGroup AR:DOCUMENT-VIEW-SELECTABLE
        """
        if elem.semantic_information is not None:
            attr.append(('SI', elem.semantic_information))
        if elem.view is not None:
            attr.append(('VIEW', elem.view))

    def _collect_paginateable_attributes(self,
                                         elem: ar_element.Paginateable,
                                         attr: TupleList):
        """
        Collects attributes from attributeGroup AR:PAGINATEABLE
        """
        if elem.page_break is not None:
            attr.append(('BREAK', ar_enum.enum_to_xml(elem.page_break)))
        if elem.keep_with_previous is not None:
            attr.append(
                ('KEEP-WITH-PREVIOUS', ar_enum.enum_to_xml(elem.keep_with_previous)))

    def _write_general_annotation(self, elem: ar_element.GeneralAnnotation) -> None:
        """
        Writes Group AR:GENERAL-ANNOTATION
        """
        if elem.label is not None:
            self._write_multi_language_long_name(elem.label, 'LABEL')
        if elem.origin is not None:
            self._add_content('ANNOTATION-ORIGIN', str(elem.origin))
        if elem.text is not None:
            self._write_documentation_block(elem.text, 'ANNOTATION-TEXT')

    # DataDictionary elements

    def _write_sw_addr_method(self, elem: ar_element.SwAddrMethod) -> None:
        """
        Writes Complex-type AR:SW-ADDR-METHOD
        Type: Concrete
        Tag variants: 'SW-ADDR-METHOD'
        """
        assert isinstance(elem, ar_element.SwAddrMethod)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('SW-ADDR-METHOD', attr)
        self._write_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_addr_method_group(elem)
        self._leave_child()

    def _write_sw_addr_method_group(self, elem: ar_element.SwAddrMethod) -> None:
        """
        Writes group AR:SW-ADDR-METHOD
        """
        if elem.memory_allocation_keyword_policy:
            pass  # Not yet implemented
        if elem.options:
            pass  # Not yet implemented
        if elem.section_initialization_policy:
            pass  # Not yet implemented
        if elem.section_type:
            pass  # Not yet implemented

    def _write_sw_base_type(self, elem: ar_element.SwBaseType) -> None:
        """
        Writes Complex-type AR:SW-BASE-TYPE
        Type: Concrete
        Tag variants: 'SW-BASE-TYPE'
        """
        assert isinstance(elem, ar_element.SwBaseType)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('SW-BASE-TYPE', attr)
        self._write_referrable(elem)
        self._write_identifiable(elem)
        self._write_base_type(elem)
        self._leave_child()

    def _write_base_type(self, elem: ar_element.SwBaseType) -> None:
        """
        Writes groups AR:BASE-TYPE and AR:BASE-TYPE-DIRECT-DEFINITION
        """
        if elem.size is not None:
            self._add_content('BASE-TYPE-SIZE', int(elem.size))
        if elem.max_size is not None:
            self._add_content('MAX-BASE-TYPE-SIZE', int(elem.max_size))
        if elem.encoding is not None:
            self._add_content('BASE-TYPE-ENCODING', str(elem.encoding))
        if elem.alignment is not None:
            self._add_content('MEM-ALIGNMENT', int(elem.alignment))
        if elem.byte_order is not None:
            self._add_content(
                'BYTE-ORDER', ar_enum.enum_to_xml(elem.byte_order))
        if elem.native_declaration is not None:
            self._add_content('NATIVE-DECLARATION',
                              str(elem.native_declaration))

    def _write_sw_data_def_props_conditional(self, elem: ar_element.SwDataDefPropsConditional) -> None:
        """
        Writes Complex-type AR:SW-DATA-DEF-PROPS-CONDITIONAL
        Type: Concrete
        Tag variants: 'SW-DATA-DEF-PROPS-CONDITIONAL'
        """

        assert isinstance(elem, ar_element.SwDataDefPropsConditional)
        tag = 'SW-DATA-DEF-PROPS-CONDITIONAL'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sw_data_def_props_content(elem)
            self._leave_child()

    def _write_sw_data_def_props_content(self, elem: ar_element.SwDataDefPropsConditional) -> None:
        """
        Writes Group SW-DATA-DEF-PROPS-CONTENT
        Type: Abstract
        """
        if elem.display_presentation is not None:
            self._add_content('DISPLAY-PRESENTATION',
                              ar_enum.enum_to_xml(elem.display_presentation))
        if elem.step_size is not None:
            self._add_content('STEP-SIZE', self._format_float(elem.step_size))
        if elem.annotations:
            self._write_annotations(elem.annotations)
        if elem.sw_addr_method_ref is not None:
            self._write_sw_addr_method_ref(elem.sw_addr_method_ref)
        if elem.alignment is not None:
            self._add_content('SW-ALIGNMENT', elem.alignment)
        if elem.base_type_ref is not None:
            self._write_sw_base_type_ref(elem.base_type_ref)
        if elem.bit_representation is not None:
            self._write_sw_bit_represenation(elem.bit_representation)
        if elem.calibration_access is not None:
            self._add_content('SW-CALIBRATION-ACCESS',
                              ar_enum.enum_to_xml(elem.calibration_access))

    # Reference Elements

    def _collect_base_ref_attr(self,
                               elem: ar_element.BaseRef,
                               attr: TupleList) -> None:
        attr.append(('DEST', ar_enum.enum_to_xml(elem.dest)))

    def _write_sw_base_type_ref(self, elem: ar_element.SwBaseTypeRef) -> None:
        """
        Writes complex-type SW-BASE-TYPE-REF
        Type: Concrete
        Tag variants: 'AR:BASE-TYPE-REF'

        Note: The name of the complex-type is anonymous in the XML schema.

        """
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('BASE-TYPE-REF', elem.value, attr)

    def _write_sw_addr_method_ref(self, elem: ar_element.SwAddrMethodRef) -> None:
        """
        Writes complex-type AR:SW-ADDR-METHOD-REF
        Type: Concrete
        Tag variants: 'AR:SW-ADDR-METHOD-REF'
        """
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('SW-ADDR-METHOD-REF', elem.value, attr)

    def _collect_sw_addr_method_ref_attr(self,
                                         elem: ar_element.SwAddrMethodRef,
                                         attr: TupleList) -> None:
        attr.append(('DEST', ar_enum.enum_to_xml(elem.dest)))

    def _write_sw_bit_represenation(self, elem: ar_element.SwBitRepresentation) -> None:
        """
        Writes AR:SW-BIT-REPRESENTATION
        Type: Concrete
        Tag Variants: 'SW-BIT-REPRESENTATION'
        """
        tag = 'SW-BIT-REPRESENTATION'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.position is not None:
                self._add_content('BIT-POSITION', str(elem.position))
            if elem.num_bits is not None:
                self._add_content('NUMBER-OF-BITS', str(elem.num_bits))
            self._leave_child()
