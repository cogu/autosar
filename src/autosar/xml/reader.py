"""
ARXML reader module
"""
import os
import re
import sys

from typing import Iterable, Any
import lxml.etree as ElementTree
import autosar.xml.document as ar_document
import autosar.xml.exception as ar_exception
import autosar.xml.element as ar_element
import autosar.xml.package as ar_package
import autosar.xml.enumeration as ar_enum

DEFAULT_SCHEMA_VERSION = 50


class WrappedElement:
    """
    Wrapped XML Element
    """

    def __init__(self, elem: ElementTree.Element) -> None:
        self._elem = elem
        self.is_accessed: bool = False

    @property
    def elem(self) -> ElementTree.Element:
        """
        Returns element with some book-keeping
        """
        self.is_accessed = True
        return self._elem


class ChildElementMap:
    """
    Container for ARXML child elements
    """

    def __init__(self, elem: ElementTree.Element) -> None:
        self.elements: dict[str, WrappedElement] = {}
        for child_elem in elem.findall('./*'):
            self.elements[str(child_elem.tag)] = WrappedElement(child_elem)

    def get(self, tag: str) -> ElementTree.Element:
        """
        Returns unwrapped element if it exists
        """
        wrapped = self.elements.get(tag, None)
        if wrapped is not None:
            return wrapped.elem
        return None

    def skip(self, tag: str) -> None:
        """
        Touches element but does not return it.
        This is used to skip elements that are not implemented
        but where we don't want to warn about them not being
        supported.
        """
        wrapped = self.elements.get(tag, None)
        if wrapped is not None:
            wrapped.is_accessed = True

    def values(self) -> Iterable[WrappedElement]:
        """
        Returns values of inner dict
        """
        return self.elements.values()


class Reader:
    """
    ARXML Reader class
    """

    def __init__(self,
                 warn_on_unprocessed_element: bool = True,
                 use_full_path_on_warning: bool = False,
                 schema_version: int = DEFAULT_SCHEMA_VERSION) -> None:
        self.xml_root: ElementTree.Element = None
        self.file_path: str = None
        self.file_base_name: str = None
        self.warn_on_unprocessed_element = warn_on_unprocessed_element
        self.use_full_path_on_warning = use_full_path_on_warning
        self.observed_unsupported_elements = None
        self.schema_file: str = ''
        self.schema_version = schema_version
        self.document: ar_document.Document = None
        self.switcher_collectable = {  # Collectable elements
            'SENDER-RECEIVER-INTERFACE': self._read_sender_receiver_interface,
            'SW-BASE-TYPE': self._read_sw_base_type,
            'SW-ADDR-METHOD': self._read_sw_addr_method,
            'IMPLEMENTATION-DATA-TYPE': self._read_implementation_data_type,
        }
        self.switcher_non_collectable = {  # Non-collectable, used only for unit testing
            # Documentation elements
            'ANNOTATION': self._read_annotation,
            'ANNOTATION-TEXT': self._read_documentation_block,
            'BR': self._read_break,
            'DESC': self._read_multi_language_overview_paragraph,
            'E': self._read_emphasis_text,
            'IE': self._read_index_entry,
            'L-4': self._read_language_long_name,
            'L-1': self._read_language_paragraph,
            'L-5': self._read_language_verbatim,
            'LABEL': self._read_multi_language_long_name,
            'LONG-NAME': self._read_multi_language_long_name,
            'P': self._read_multi_language_paragraph,
            'SUP': self._read_superscript,
            'SUB': self._read_subscript,
            'TT': self._read_technical_term,
            'VERBATIM': self._read_multi_language_verbatim,
            # DataDictionary elements
            'BASE-TYPE-REF': self._read_sw_base_type_ref,
            'SW-DATA-DEF-PROPS-CONDITIONAL': self._read_sw_data_def_props_conditional,

        }
        self.switcher_all = {}
        self.switcher_all.update(self.switcher_collectable)
        self.switcher_all.update(self.switcher_non_collectable)

    def read_file(self, file_path: str) -> ar_document.Document:
        """
        Reads ARXML document file
        """
        self.document = None
        self.xml_root = ElementTree.ElementTree().parse(file_path)
        self.file_path = file_path
        self.file_base_name = os.path.basename(file_path)
        self.observed_unsupported_elements = set()
        self._clean_namespace('http://autosar.org/schema/r4.0')
        self._read_root_element()
        self._read_packages()
        return self.document

    def read_str_elem(self, xml: str) -> None | ar_element.ARObject:
        """
        Reads a concrete ARXML element from string.
        This is primarily used for unit-testing.
        """
        self.observed_unsupported_elements = set()
        elem = ElementTree.fromstring(xml)
        read_method = self.switcher_all.get(elem.tag, None)
        if read_method is not None:
            return read_method(elem)
        else:
            raise NotImplementedError(f"Found no reader for '{elem.tag}'")

    # Utility methods

    def _report_unprocessed_elements(self, xml_elements: ChildElementMap):
        """
        Reports about unprocessed child elements
        """
        for xml_elem in [x.elem for x in xml_elements.values() if not x.is_accessed]:
            assert xml_elem is not None
            self._report_unprocessed_element(xml_elem)

    def _report_unprocessed_element(self, xml_elem: ElementTree.Element):
        """
        Reports about a single child element
        """
        if xml_elem.tag not in self.observed_unsupported_elements:
            self.observed_unsupported_elements.add(xml_elem.tag)
            if self.warn_on_unprocessed_element:
                file = self.file_path if self.use_full_path_on_warning else self.file_base_name
                print(
                    f"{file}({xml_elem.sourceline}): Unprocessed element <{xml_elem.tag}>", file=sys.stderr)

    def _raise_parse_error(self, element: ElementTree.Element, message: str):
        """
        Raises an ARXML parse error with message
        """
        file = self.file_path if self.use_full_path_on_warning else self.file_base_name
        header = f"{file}({element.sourceline}): "
        raise ar_exception.ParseError(header+message)

    def _clean_namespace(self, namespace: str) -> None:
        """
        Removes XML namespace in place.
        """
        wrapped = '{'+namespace+'}'
        wrapped_len = len(wrapped)
        for elem in self.xml_root.iter():
            if isinstance(elem.tag, str) and elem.tag.startswith(wrapped):
                elem.tag = elem.tag[wrapped_len:]

    def _read_boolean(self, value: str) -> bool:
        """
        Reads simpleType AR:BOOLEAN--SIMPLE
        """
        if value == '0' or 'false':
            return False
        elif value == '1' or 'true':
            return True
        else:
            raise ar_exception.ParseError('Not a boolean value: '+str(value))

    # Abstract base classes

    def _read_referrable(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads groups AR:REFERRABLE and AR:MULTILANGUAGE-REFFERABLE
        Type: Abstract
        """
        short_name = element_map.get('SHORT-NAME')
        if short_name is not None:
            data['short_name'] = short_name.text
        else:
            raise ar_exception.ParseError(
                "Missing required element SHORT-NAME")
        xml_long_name = element_map.get('LONG-NAME')
        if xml_long_name is not None:
            data['long_name'] = self._read_multi_language_long_name(
                xml_long_name)

    def _read_identifiable(self, element_map: ChildElementMap, attr: dict, data: dict) -> None:
        """
        Reads group AR:IDENTIFIABLE
        Type: Abstract
        """
        self._read_identifiable_attributes(attr, data)
        xml_child: ElementTree.Element | None = None
        xml_child = element_map.get('DESC')
        if xml_child is not None:
            data['desc'] = self._read_multi_language_overview_paragraph(
                xml_child)
        xml_child = element_map.get('CATEGORY')
        if xml_child is not None:
            data['category'] = xml_child.text
        xml_child = element_map.get('ADMIN-DATA')
        if xml_child is not None:
            data['admin_data'] = self._read_admin_data(xml_child)
        xml_child = element_map.get('INTRODUCTION')
        if xml_child is not None:
            data['introduction'] = self._read_documentation_block(xml_child)
        xml_child = element_map.get('ANNOTATIONS')
        if xml_child is not None:
            data['annotations'] = self._read_annotations(xml_child)

    def _read_identifiable_attributes(self, attr: dict, data: dict) -> None:
        uuid = attr.get('UUID', None)
        if uuid is not None:
            data['uuid'] = uuid

    # AdminData

    # These read methods needs additional refactoring before they are useful

    def _read_admin_data(self, xml_element: ElementTree.Element) -> ar_element.AdminData:
        """
        Reads Complex-type AR:ADMIN-DATA
        Type: Concrete
        """
        data = {}
        element_map = ChildElementMap(xml_element)
        element_map.skip('LANGUAGE')  # Implement later
        element_map.skip('USED-LANGUAGES')  # Implement later
        element_map.skip('DOC-REVISIONS')  # Implement later
        xml_sdgs = element_map.get('SDGS')
        if xml_sdgs:
            data['data'] = self._read_admin_data_sdgs(xml_sdgs)
        return ar_element.AdminData(**data)

    def _read_admin_data_sdgs(self, xml_element: ElementTree.Element) -> list:
        """
        Reads Complex-type AR:SDGS
        """
        data = []
        for xml_child in xml_element.findall('./SDG'):
            sdg = self._read_admin_data_sdg(xml_child)
            data.append(sdg)
        return data

    def _read_admin_data_sdg(self, xml_element: ElementTree.Element) -> dict[str, dict]:
        """
        Reads Complex-type AR:SDG
        """
        group_key = xml_element.attrib['GID']
        xml_sd = xml_element.find('./SD')
        special_data = self._read_admin_data_sd(xml_sd)
        return {group_key: special_data}

    def _read_admin_data_sd(self, xml_element: ElementTree.Element) -> dict[str, str]:
        """
        Reads Complex-type AR:SD
        """
        key = xml_element.attrib['GID']
        value = xml_element.text
        return {key: value}

    # AUTOSAR Document

    def _read_root_element(self) -> None:
        self._read_schema_version()
        self.document = ar_document.Document()
        self.document.schema_version = self.schema_version
#        for xml_node in self.xml_root.findall('./*'):
#            if xml_node.tag == 'FILE-INFO-COMMENT':
#                self._read_file_info_comment(xml_node, self.document)

    def _read_schema_version(self) -> None:
        for key in self.xml_root.attrib.keys():
            if key.endswith('schemaLocation'):
                match = re.search(r'AUTOSAR_(\d+).xsd',
                                  self.xml_root.attrib[key])
                if match is not None:
                    self.schema_file = 'AUTOSAR_'+match.group(1)+'.xsd'
                    self.schema_version = int(match.group(1))

    # def _read_file_info_comment(self, xml_node, parent):
    #     """
    #     Parse AR:FILE-INFO-COMMENT
    #     """
    #     sdg_list = self._read_special_data_groups(xml_node)

    # def _read_special_data_groups(self, xml_node : ElementTree.Element) -> dict:
    #     """
    #     Reads AR:SDGS
    #     """
    #     result = {}
    #     for xml_elem in xml_node.findall('SDGS/SDG'):
    #         BUILD A Dictionary containing other dictionaries
    #

    # AUTOSAR Package

    def _read_packages(self):
        for xml_node in self.xml_root.findall('./AR-PACKAGES/*'):
            if xml_node.tag == 'AR-PACKAGE':
                package = self._read_package(xml_node)
                self.document.append(package)

    def _read_package(self, elem: ElementTree.Element) -> ar_package.Package:
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        package = ar_package.Package(data['short_name'], **data)
        self._read_package_group(child_elements, package)
        self._report_unprocessed_elements(child_elements)
        return package

    def _read_package_group(self, element_map: ChildElementMap, package: ar_package.Package) -> None:
        """
        Reads group AR:AR-PACKAGE
        Type: Utility
        """
        # REFERECE-BASES not implemented
        xml_elements = element_map.get('ELEMENTS')
        xml_packages = element_map.get('AR-PACKAGES')
        # VARIATION-POINT will not be supported
        if xml_elements is not None:
            self._read_package_elements(package, xml_elements)
        if xml_packages is not None:
            self._read_sub_packages(package, xml_packages)

    def _read_package_elements(self, package: ar_package.Package, xml_elements: ElementTree.Element) -> None:
        """
        Reads AR:AR-PACKAGE.ELEMENTS
        Type: Utility
        """
        for xml_child_elem in xml_elements.findall('./*'):
            read_method = self.switcher_collectable.get(
                xml_child_elem.tag, None)
            if read_method is not None:
                element = read_method(xml_child_elem)
                assert isinstance(element, ar_element.ARElement)
                package.append(element)
            else:
                self._report_unprocessed_element(xml_child_elem)

    def _read_sub_packages(self, package: ar_package.Package, xml_packages: ElementTree.Element) -> None:
        """
        Reads AR:AR-PACKAGE.ELEMENTS
        Type: Utility
        """
        for xml_child_package in xml_packages.findall('./PACKAGE'):
            child_package = self._read_package(xml_child_package)
            assert isinstance(child_package, ar_package.Package)
            package.packages.append(child_package)

    # References

    def _read_sw_base_type_reference(self, xml_elem: ElementTree.Element):
        dest_text = xml_elem.attrib['DEST']
        dest_enum = ar_enum.xml_to_enum(
            'IdentifableSubTypes', dest_text, self.schema_version)
        if dest_enum != ar_enum.IdentifiableSubTypes.SW_BASE_TYPE:
            self._raise_parse_error(
                xml_elem, f"Invalid DEST attribute '{dest_text}'. Expected 'SW-BASE-TYPE'")
        return ar_element.SwBaseTypeRef(xml_elem.text)

    # Documentation elements

    def _read_annotation(self, xml_elem: ElementTree.Element) -> ar_element.Annotation:
        """
        Reads Complex-type AR:ANNOTATION
        """
        data = {}
        self._read_general_annotation(xml_elem, data)
        elem = ar_element.Annotation(**data)
        return elem

    def _read_annotations(self, xml_elem: ElementTree.Element) -> list[ar_element.Annotation]:
        """
        Reads unbounded list of AR:ANNOTATION
        """
        elements = []
        for xml_child in xml_elem.findall('./ANNOTATION'):
            elements.append(self._read_annotation(xml_child))
        return elements

    def _read_general_annotation(self, xml_elem: ElementTree.Element, data: dict) -> None:
        """
        Reads Group AR:GENERAL-ANNOTATION
        """
        xml_label = xml_elem.find('./LABEL')
        xml_origin = xml_elem.find('./ANNOTATION-ORIGIN')
        xml_text = xml_elem.find('./ANNOTATION-TEXT')

        if xml_label is not None:
            data['label'] = self._read_multi_language_long_name(xml_label)
        if xml_origin is not None:
            data['origin'] = xml_origin.text
        if xml_text is not None:
            data['text'] = self._read_documentation_block(xml_text)

    def _read_break(self, xml_elem: ElementTree.Element) -> ar_element.Break:  # pylint: disable=unused-argument
        """
        Reads complexType AR:BR
        Type: Concrete
        """
        return ar_element.Break()

    def _read_documentation_block(self, xml_elem: ElementTree.Element) -> ar_element.DocumentationBlock:
        """
        Reads complexType AR:DOCUMENTATION-BLOCK
        Type: Concrete
        """
        elem = ar_element.DocumentationBlock()
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'P':
                elem.append(
                    self._read_multi_language_paragraph(xml_child_elem))
            elif xml_child_elem.tag == 'VERBATIM':
                elem.append(self._read_multi_language_verbatim(xml_child_elem))
            else:
                self._report_unprocessed_element(xml_child_elem)
        return elem

    def _read_emphasis_text(self, elem: ElementTree.Element) -> ar_element.EmphasisText:
        """
        Reads complexType AR:EMPHASIS-TEXT
        We only support plain elements for now. No nesting (mixed-content) supported.

        Type: Concrete
        """
        data = {}
        self._read_emphasis_text_attr(elem.attrib, data)
        if len(elem.findall('./*')) > 0:
            raise NotImplementedError(
                "Nesting inside <E> elements not yet supported")
        data['elements'] = elem.text
        return ar_element.EmphasisText(**data)

    def _read_emphasis_text_attr(self, attrib: dict, data: dict) -> None:
        """
        Reads attributeGroup AR:EMPHASIS-TEXT
        """
        if 'COLOR' in attrib:
            data['color'] = str(attrib['COLOR'])
        if 'FONT' in attrib:
            data['font'] = ar_enum.xml_to_enum(
                'EmphasisFont', attrib['FONT'], self.schema_version)
        if 'TYPE' in attrib:
            data['type'] = ar_enum.xml_to_enum(
                'EmphasisType', attrib['TYPE'], self.schema_version)

    def _read_index_entry(self, elem: ElementTree.Element) -> ar_element.IndexEntry:
        """
        Reads complexType AR:INDEX-ENTRY
        Limitations: Doesn't support child-elements even though it's allowed in the scehema
        Type: Concrete
        """
        return ar_element.IndexEntry(elem.text)

    def _read_technical_term(self,
                             elem: ElementTree.Element) -> ar_element.TechnicalTerm:
        """
        Reads complexType AR:TT
        Type: Concrete
        """
        data = {}
        self._read_technical_term_attr(elem.attrib, data)
        if len(elem.findall('./*')) > 0:
            self._raise_parse_error(
                elem, 'Child elements in "AR:TT" not allowed')
        data['text'] = elem.text
        return ar_element.TechnicalTerm(**data)

    def _read_technical_term_attr(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from attribute group AR:TT
        """
        if 'TEX-RENDER' in attrib:
            data['tex_render'] = str(attrib['TEX-RENDER'])
        if 'TYPE' in attrib:
            data['type'] = str(attrib['TYPE'])

    def _read_superscript(self, elem: ElementTree.Element) -> ar_element.TechnicalTerm:
        """
        Reads complexType AR:SUPSCRIPT for tag SUP
        Type: Concrete
        """
        return ar_element.Superscript(elem.text)

    def _read_subscript(self, elem: ElementTree.Element) -> ar_element.TechnicalTerm:
        """
        Reads complexType AR:SUPSCRIPT for tag SUB
        Type: Concrete
        """
        return ar_element.Subscript(elem.text)

    def _read_multi_language_long_name(self, xml_elem: ElementTree.Element) -> ar_element.MultilanguageLongName:
        """
        Reads complexType AR:MULTILANGUAGE-LONG-NAME
        Type: Concrete
        Tag variants: 'LABEL' | 'LONG-NAME'
        """
        assert xml_elem.tag in {'LONG-NAME', 'LABEL'}
        elem = ar_element.MultilanguageLongName()
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-4':
                elem.append(self._read_language_long_name(xml_child_elem))
        return elem

    def _read_language_long_name(self, xml_elem: ElementTree.Element) -> ar_element.LanguageLongName:
        """
        Reads complexType AR:L-LONG-NAME (L-4 tags)
        Type: Concrete
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageLongName(data['language'])
        self._read_mixed_content_for_long_name(xml_elem, elem)
        return elem

    def _read_language_specific_attr(self, attrib: dict, data: dict) -> None:
        """
        Reads attributeGroup AR:LANGUAGE-SPECIFIC
        """
        data['language'] = ar_enum.xml_to_enum(
            'Language', attrib['L'])  # L is a mandatory attribute

    def _read_mixed_content_for_long_name(self,
                                          xml_elem: ElementTree.Element,
                                          elem: ar_element.LanguageLongName) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-LONG-NAME

        This includes reading mixed content from L-LONG-NAME or
        SINGLE-LANGUAGE-LONG-NAME

        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            elif xml_child_elem.tag == 'IE':
                elem.append(self._read_index_entry(xml_child_elem))
            elif xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_multi_language_overview_paragraph(self,
                                            xml_elem: ElementTree.Element) -> ar_element.MultiLanguageOverviewParagraph:
        """
        Reads complexType AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
        """
        assert xml_elem.tag in {'DESC', 'ITEM-LABEL', 'CHANGE', 'REASON'}
        elem = ar_element.MultiLanguageOverviewParagraph()
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-2':
                elem.append(
                    self._read_language_overview_paragraph(xml_child_elem))
        return elem

    def _read_language_overview_paragraph(self,
                                          xml_elem: ElementTree.Element) -> ar_element.LanguageOverviewParagraph:
        """
        Reads complexType AR:L-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'L-2'
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageOverviewParagraph(data['language'])
        self._read_mixed_content_for_overview_paragraph(xml_elem, elem)
        return elem

    def _read_mixed_content_for_overview_paragraph(self,
                                                   xml_elem: ElementTree.Element,
                                                   elem: ar_element.LanguageOverviewParagraph) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-OVERVIEW-PARAGRAPH

        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'BR':
                elem.append(self._read_break(xml_child_elem))
            elif xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            elif xml_child_elem.tag == 'IE':
                elem.append(self._read_index_entry(xml_child_elem))
            elif xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            elif xml_child_elem.tag in {'FT', 'TRACE-REF', 'XREF'}:
                # These elements are not yet supported
                self._report_unprocessed_element(xml_child_elem)
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_language_paragraph(self, xml_elem: ElementTree.Element) -> ar_element.LanguageParagraph:
        """
        Reads complexType AR:L-PARAGRAPH
        Type: Concrete
        Tag variants: 'L-1'
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageParagraph(data['language'])
        self._read_mixed_content_for_paragraph(xml_elem, elem)
        return elem

    def _read_language_verbatim(self, xml_elem: ElementTree.Element) -> ar_element.LanguageVerbatim:
        """
        Reads complexType AR:L-VERBATIM
        Type: Concrete
        Tag variants: 'L-5'
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageVerbatim(data['language'])
        self._read_mixed_content_for_verbatim(xml_elem, elem)
        return elem

    def _read_mixed_content_for_paragraph(self,
                                          xml_elem: ElementTree.Element,
                                          elem: ar_element.LanguageParagraph) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-PARAGRAPH
        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'BR':
                elem.append(self._read_break(xml_child_elem))
            elif xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            elif xml_child_elem.tag == 'IE':
                elem.append(self._read_index_entry(xml_child_elem))
            elif xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            elif xml_child_elem.tag in {'FT',
                                        'STD',
                                        'TRACE-REF',
                                        'XDOC',
                                        'XFILE',
                                        'XREF',
                                        'XREF-TARGET'}:
                # These elements are not yet supported
                self._report_unprocessed_element(xml_child_elem)
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_mixed_content_for_verbatim(self,
                                         xml_elem: ElementTree.Element,
                                         elem: ar_element.LanguageVerbatim) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-VERBATIM
        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'BR':
                elem.append(self._read_break(xml_child_elem))
            elif xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            elif xml_child_elem.tag in {'XREF'}:
                # These elements are not yet supported
                self._report_unprocessed_element(xml_child_elem)
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_multi_language_paragraph(self,
                                       xml_elem: ElementTree.Element) -> ar_element.MultiLanguageParagraph:
        """
        Reads complexType AR:MULTI-LANGUAGE-PARAGRAPH
        Type: Concrete
        Tag variants: 'P'
        """
        attr = {}
        self._read_document_view_selectable_attrib(xml_elem.attrib, attr)
        self._read_paginateable_attrib(xml_elem.attrib, attr)
        self._read_multi_language_paragraph_attrib(xml_elem.attrib, attr)
        elem = ar_element.MultiLanguageParagraph(**attr)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-1':
                elem.append(self._read_language_paragraph(xml_child_elem))
        return elem

    def _read_document_view_selectable_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:DOCUMENT-VIEW-SELECTABLE
        """
        if 'SI' in attrib:
            data['semantic_information'] = str(attrib['SI'])
        if 'VIEW' in attrib:
            data['view'] = str(attrib['VIEW'])

    def _read_paginateable_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:PAGINATEABLE
        """
        if 'BREAK' in attrib:
            data['page_break'] = ar_enum.xml_to_enum(
                'PageBreak', attrib['BREAK'])
        if 'KEEP-WITH-PREVIOUS' in attrib:
            data['keep_with_previous'] = ar_enum.xml_to_enum(
                'KeepWithPrevious', attrib['KEEP-WITH-PREVIOUS'])

    def _read_multi_language_paragraph_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:MULTI-LANGUAGE-PARAGRAPH
        """
        if 'HELP-ENTRY' in attrib:
            data['help_entry'] = str(attrib['HELP-ENTRY'])

    def _read_multi_language_verbatim(self,
                                      xml_elem: ElementTree.Element) -> ar_element.MultiLanguageVerbatim:
        """
        Reads complexType AR:MULTI-LANGUAGE-VERBATIM
        Type: Concrete
        Tag variants: 'VERBATIM'
        """
        attr = {}
        self._read_document_view_selectable_attrib(xml_elem.attrib, attr)
        self._read_paginateable_attrib(xml_elem.attrib, attr)
        self._read_multi_language_verbatim_attrib(xml_elem.attrib, attr)
        elem = ar_element.MultiLanguageVerbatim(**attr)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-5':
                elem.append(self._read_language_verbatim(xml_child_elem))
        return elem

    def _read_multi_language_verbatim_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:MULTI-LANGUAGE-VERBATIM
        """
        if 'ALLOW-BREAK' in attrib:
            data['allow_break'] = str(attrib['ALLOW-BREAK'])
        if 'FLOAT' in attrib:
            data['float'] = ar_enum.xml_to_enum('Float', attrib['FLOAT'])
        if 'HELP-ENTRY' in attrib:
            data['help_entry'] = str(attrib['HELP-ENTRY'])
        if 'PGWIDE' in attrib:
            data['page_wide'] = ar_enum.xml_to_enum(
                'PageWide', attrib['PGWIDE'])

    # DataDictionary Elements

    def _read_sw_addr_method(self, xml_element: ElementTree.Element) -> ar_element.SwAddrMethod:
        """
        Reads Complex-type AR:SW-ADDR-METHOD
        Type: Concrete
        Tag variants: 'SW-ADDR-METHOD'
        """
        data = {}
        element_map = ChildElementMap(xml_element)
        self._read_referrable(element_map, data)
        self._read_identifiable(element_map, xml_element.attrib, data)
        self._read_sw_addr_method_group(element_map, data)
        self._report_unprocessed_elements(element_map)
        return ar_element.SwAddrMethod(data['short_name'], **data)

    def _read_sw_addr_method_group(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-ADDR-METHOD
        Type: Utility
        """
        element_map.skip('MEMORY-ALLOCATION-KEYWORD-POLICY')  # Not implemented
        element_map.skip('OPTIONS')  # Not implemented
        element_map.skip('SECTION-INITIALIZATION-POLICY')  # Not implemented
        element_map.skip('SECTION-TYPE')  # Not Implemented

    def _read_sw_base_type(self, xml_element: ElementTree.Element) -> ar_element.SwBaseType:
        """
        Reads Complex-type AR:SW-BASE-TYPE
        Type: Concrete
        Tag variants: 'SW-BASE-TYPE'
        """
        data = {}
        element_map = ChildElementMap(xml_element)
        self._read_referrable(element_map, data)
        self._read_identifiable(element_map, xml_element.attrib, data)
        self._read_base_type(element_map, data)
        self._report_unprocessed_elements(element_map)
        return ar_element.SwBaseType(data['short_name'], **data)

    def _read_base_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads groups AR:BASE-TYPE and AR:BASE-TYPE-DIRECT-DEFINITION
        Type: Abstract
        """
        xml_child: ElementTree.Element | None = None
        xml_child = child_elements.get('BASE-TYPE-SIZE')
        if xml_child is not None:
            data['size'] = int(xml_child.text)  # TODO: Verify positive integer
        xml_child = child_elements.get('MAX-BASE-TYPE-SIZE')
        if xml_child is not None:
            # TODO: Verify positive integer
            data['max_size'] = int(xml_child.text)
        xml_child = child_elements.get('BASE-TYPE-ENCODING')
        if xml_child is not None:
            data['encoding'] = str(xml_child.text)
        xml_child = child_elements.get('MEM-ALIGNMENT')
        if xml_child is not None:
            # TODO: Verify positive integer
            data['alignment'] = int(xml_child.text)
        xml_child = child_elements.get('BYTE-ORDER')
        if xml_child is not None:
            data['byte_order'] = ar_enum.xml_to_enum(
                'ByteOrder', xml_child.text)
        xml_child = child_elements.get('NATIVE-DECLARATION')
        if xml_child is not None:
            data['native_declaration'] = str(xml_child.text)

    def _read_sw_bit_representation(self, xml_element: ElementTree.Element) -> ar_element.SwBitRepresentation:
        """
        Reads AR:SW-BIT-REPRESENTATION
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        bit_position = child_elements.get('BIT-POSITION')
        if bit_position is not None:
            data['bit_position'] = int(bit_position.text)
        number_of_bits = child_elements.get('NUMBER-OF-BITS')
        if number_of_bits is not None:
            data['number_of_bits'] = int(number_of_bits.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwBitRepresentation(**data)

    def _read_sw_data_def_props(self, xml_elem: ElementTree.Element) -> ar_element.SwDataDefProps:
        """
        Reads SW-DATA-DEF-PROPS
        Type: Concrete
        """
        xml_child = xml_elem.find('./SW-DATA-DEF-PROPS-VARIANTS')
        sw_data_def_props_variants = ar_element.SwDataDefProps()
        if xml_child is not None:
            variants = self._read_sw_data_def_props_variants(xml_child)
            sw_data_def_props_variants.variants.extend(variants)
        return sw_data_def_props_variants

    def _read_sw_data_def_props_variants(self,
                                         xml_elem: ElementTree.Element) -> list[ar_element.SwDataDefPropsConditional]:
        """
        Reads SW-DATA-DEF-PROPS-VARIANTS
        Type: Concrete
        """
        variants = []
        for xml_child in xml_elem.findall('./SW-DATA-DEF_PROPS_CONDITIONAL'):
            props_conditional = self._read_sw_data_def_props_conditional(
                xml_child)
            variants.append(props_conditional)
        return variants

    def _read_sw_data_def_props_conditional(self,
                                            xml_elem: ElementTree.Element) -> ar_element.SwDataDefPropsConditional:
        """
        Reads complexType AR:SW-DATA-DEF-PROPS-CONDITIONAL
        Type: Concrete
        Tag variants: 'AR:SW-DATA-DEF-PROPS-CONDITIONAL'
        """
        data = {}
        self._read_sw_data_def_props_content(xml_elem, data)
        return ar_element.SwDataDefPropsConditional(**data)

    def _read_sw_data_def_props_content(self, xml_elem: ElementTree.Element, data: dict[str, Any]) -> None:
        """
        Reads Group SW-DATA-DEF-PROPS-CONTENT
        Type: Abstract
        """
        child_elements = ChildElementMap(xml_elem)
        xml_child: ElementTree.Element | None = None
        xml_child = child_elements.get('DISPLAY-PRESENTATION')
        if xml_child is not None:
            data['display_presentation'] = ar_enum.xml_to_enum(
                'DisplayPresentation', xml_child.text)
        xml_child = child_elements.get('STEP-SIZE')
        if xml_child is not None:
            data['step_size'] = float(xml_child.text)
        # Variant-handling not supported
        child_elements.skip('SW-VALUE-BLOCK-SIZE-MULTS')
        xml_child = child_elements.get('ANNOTATIONS')
        if xml_child is not None:
            data['annotations'] = self._read_annotations(xml_child)
        xml_child = child_elements.get('SW-ADDR-METHOD-REF')
        if xml_child is not None:
            data['sw_addr_method_ref'] = self._read_sw_addr_method_ref(xml_child)
        xml_child = child_elements.get('SW-ALIGNMENT')
        if xml_child is not None:
            try:
                sw_alignment = int(xml_child.text,0)
            except ValueError:
                sw_alignment = xml_child.text
            data['alignment'] = sw_alignment
        xml_child = child_elements.get('BASE-TYPE-REF')
        if xml_child is not None:
            data['base_type_ref'] = self._read_sw_base_type_ref(xml_child)
        # sw_bit_representation = child_elements.find('SW-BIT-REPRESENTATION')
        # if sw_bit_representation is not None:
        #     data['sw_bit_representation'] = self._read_sw_bit_representation(
        #         sw_bit_representation)
        # sw_calibration_access = child_elements.find('SW-CALIBRATION-ACCESS')
        # if sw_calibration_access is not None:
        #     data['sw_calibration_access'] = ar_enum.xml_to_enum('SwCalibrationAccess',
        #                                                         sw_calibration_access.text,
        #                                                         self.schema_version)
        self._report_unprocessed_elements(child_elements)

    # Reference elements

    def _read_sw_base_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.SwAddrMethodRef:
        """
        Reads complex-type AR:SW-BASE-TYPE-REF

        Note: the name of this complex-type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-BASE-TYPE':
            raise ar_exception.ParseError(
                f"Invalid value for DEST. Expected 'SW-BASE-TYPE', got '{data['dest']}'")
        return ar_element.SwBaseTypeRef(xml_elem.text)

    def _read_sw_addr_method_ref(self, xml_elem: ElementTree.Element) -> ar_element.SwAddrMethodRef:
        """
        Reads complex-type AR:SW-ADDR-METHOD-REF
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-ADDR-METHOD':
            raise ar_exception.ParseError(
                f"Invalid value for DEST. Expected 'SW-ADDR-METHOD', got '{data['dest']}'")
        return ar_element.SwAddrMethodRef(xml_elem.text)

    def _read_base_ref_attributes(self, attr: dict, data: dict) -> None:
        data['dest'] = attr.get('DEST', None)
        if data['dest'] is None:
            raise ar_exception.ParseError("Missing required attribute 'DEST'")

    # UNFINISHED ELEMENTS - NEEDS REFACTORING

    def _read_sender_receiver_interface(self, xml_element: ElementTree.Element) -> None:
        """
        Element-Type: Concrete
        """
        data = {}
        element_map = ChildElementMap(xml_element)
        self._read_referrable(element_map, data)
        self._read_identifiable(element_map, xml_element.attrib, data)
        self._read_port_interface(element_map, data)
        self._read_sender_receiver_interface_group(element_map, data)
        self._report_unprocessed_elements(element_map)

    def _read_port_interface(self, xml_elements: ChildElementMap, data: dict) -> None:
        """
        Reads AR:PORTINTERFACE
        Element-Type: Abstract
        """
        inner_elem = xml_elements.get('IS-SERVICE')
        if inner_elem is not None:
            data['is_service'] = self._read_boolean(inner_elem.text)
        xml_elements.skip('NAMESPACES')  # Not supported
        xml_elements.skip('SERVICE-KIND')  # Implement later

    def _read_sender_receiver_interface_group(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads AR:PORTINTERFACE
        Element-Type: Concrete
        """
        xml_data_elements = element_map.get('DATA-ELEMENTS')
        invalidation_policys = element_map.skip(
            'INVALIDATION-POLICYS')  # Implement later
        # META-DATA-ITEM-SETS not supported

        if xml_data_elements is not None:
            data_elements = self._read_data_elements(xml_data_elements)
            data['data_elements'] = data_elements

    def _read_data_elements(self, xml_elem: ElementTree.Element) -> list:
        data_elements = []
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'VARIABLE-DATA-PROTOTYPE':
                child_data = self._read_variable_data_prototype(xml_child_elem)
                data_elements.append(child_data)
        return data_elements

    def _read_variable_data_prototype(self, elem: ElementTree.Element) -> dict:
        """
        Reads VARIABLE-DATA-PROTOTYPE
        Element-Type: Concrete dict
        """
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_autosar_data_prototype(child_elements, data)
        self._read_variable_data_prototype_elem(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return data

    def _read_data_prototype(self, xml_elements: ChildElementMap, data: dict) -> None:
        xml_sw_data_def_props = xml_elements.find('SW-DATA-DEF-PROPS')
        if xml_sw_data_def_props is not None:
            pass

    def _read_autosar_data_prototype(self, xml_elements: ChildElementMap, data: dict) -> None:
        xml_type_tref = xml_elements.find('TYPE-TREF')
        if xml_type_tref is not None:
            pass

    def _read_variable_data_prototype_elem(self, xml_elements: ChildElementMap, data: dict) -> None:
        xml_init_value = xml_elements.find('INIT-VALUE')
        if xml_init_value is not None:
            pass
        xml_elements.skip('VARIATION-POINT')  # Not supported

    def _read_implementation_data_type(self, xml_element: ElementTree.Element) -> None:
        """
        Element-Type: Concrete
        """
        data = {}
        elemept_map = ChildElementMap(xml_element)
        self._read_referrable(elemept_map, data)
        self._read_identifiable(elemept_map, xml_element.attrib, data)
        self._read_autosar_data_type(elemept_map, data)
        self._read_implementation_data_type_group(elemept_map, data)
        self._report_unprocessed_elements(elemept_map)

    def _read_autosar_data_type(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Pases AUTOSAR-DATA-TYPE
        Type: Abstract
        """
        xml_sw_data_def_props = element_map.find('SW-DATA-DEF-PROPS')
        if xml_sw_data_def_props is not None:
            data['sw_data_def_props'] = self._read_sw_data_def_props(
                xml_sw_data_def_props)

    def _read_implementation_data_type_group(self, element_map: ChildElementMap, data: dict) -> None:
        xml_init_value = element_map.find('INIT-VALUE')
        if xml_init_value is not None:
            pass
