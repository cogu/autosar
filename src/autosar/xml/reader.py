"""
ARXML reader module
"""
import os
import re
import sys

from typing import Iterable, Any, Union
import lxml.etree as ElementTree
import autosar.base as ar_base
import autosar.xml.document as ar_document
import autosar.xml.exception as ar_exception
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum

# Type aliases

MultiLanguageOverviewParagraph = ar_element.MultiLanguageOverviewParagraph

ValueSpeficationElement = Union[ar_element.TextValueSpecification,
                                ar_element.NumericalValueSpecification,
                                ar_element.NotAvailableValueSpecification,
                                ar_element.ArrayValueSpecification,
                                ar_element.RecordValueSpecification,
                                ar_element.ApplicationValueSpecification,
                                ar_element.ConstantReference]

# Helper classes


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
            tag = str(child_elem.tag)
            if tag not in self.elements:
                self.elements[tag] = WrappedElement(child_elem)

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


# Reader class


class Reader:
    """
    ARXML Reader class
    """

    def __init__(self,
                 warn_on_unprocessed_element: bool = True,
                 use_full_path_on_warning: bool = False,
                 schema_version: int = ar_base.DEFAULT_SCHEMA_VERSION) -> None:
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
            # CompuMethod
            'COMPU-METHOD': self._read_compu_method,

            # DataType and DataDictionary elements
            'APPLICATION-ARRAY-DATA-TYPE': self._read_application_array_data_type,
            'APPLICATION-RECORD-DATA-TYPE': self._read_application_record_data_type,
            'APPLICATION-PRIMITIVE-DATA-TYPE': self._read_application_primitive_data_type,
            'SW-BASE-TYPE': self._read_sw_base_type,
            'SW-ADDR-METHOD': self._read_sw_addr_method,
            'IMPLEMENTATION-DATA-TYPE': self._read_implementation_data_type,
            'DATA-TYPE-MAPPING-SET': self._read_data_type_mapping_set,


            # Constraint elements
            'DATA-CONSTR': self._read_data_constraint,

            # Port interface
            'SENDER-RECEIVER-INTERFACE': self._read_sender_receiver_interface,

            # Unit elements
            'UNIT': self._read_unit,

            # Constant elements
            'CONSTANT-SPECIFICATION': self._read_constant_specification,
        }
        # Value specification elements
        self.switcher_value_specification = {
            'TEXT-VALUE-SPECIFICATION': self._read_text_value_specification,
            'NUMERICAL-VALUE-SPECIFICATION': self._read_numerical_value_specification,
            'NOT-AVAILABLE-VALUE-SPECIFICATION': self._read_not_available_value_specification,
            'ARRAY-VALUE-SPECIFICATION': self._read_array_value_specification,
            'RECORD-VALUE-SPECIFICATION': self._read_record_value_specification,
            'APPLICATION-VALUE-SPECIFICATION': self._read_application_value_specification,
            'CONSTANT-REFERENCE': self._read_constant_reference,
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
            'DISPLAY-NAME': self._read_single_language_unit_names,
            'SUP': self._read_superscript,
            'SUB': self._read_subscript,
            'TT': self._read_technical_term,
            'VERBATIM': self._read_multi_language_verbatim,
            # CompuMethod elements
            'COMPU-INTERNAL-TO-PHYS': self._read_computation,
            'COMPU-RATIONAL-COEFFS': self._read_compu_rational,
            'COMPU-SCALE': self._read_compu_scale,
            # Constraint elements
            'SCALE-CONSTR': self._read_scale_constraint,
            'INTERNAL-CONSTRS': self._read_internal_constraint,
            'PHYS-CONSTRS': self._read_physical_constraint,
            'DATA-CONSTR-RULE': self._read_data_constraint_rule,
            # DataType and DataDictionary elements
            'BASE-TYPE-REF': self._read_sw_base_type_ref,
            'SW-BIT-REPRESENTATION': self._read_sw_bit_representation,
            'SW-DATA-DEF-PROPS-CONDITIONAL': self._read_sw_data_def_props_conditional,
            'SW-TEXT-PROPS': self._read_sw_text_props,
            'SW-POINTER-TARGET-PROPS': self._read_sw_pointer_target_props,
            'SYMBOL-PROPS': self._read_symbol_props,
            'IMPLEMENTATION-DATA-TYPE-ELEMENT': self._read_implementation_data_type_element,
            'APPLICATION-RECORD-ELEMENT': self._read_application_record_element,
            'DATA-TYPE-MAP': self._read_data_type_map,
            'SW-ARRAYSIZE': self._read_value_list,
            # CalibrationData elements
            'SW-VALUES-PHYS': self._read_sw_values,
            'SW-AXIS-CONT': self._read_sw_axis_cont,
            'SW-VALUE-CONT': self._read_sw_value_cont,
            # Reference elements
            'PHYSICAL-DIMENSION-REF': self._read_physical_dimension_ref,
            'APPLICATION-DATA-TYPE-REF': self._read_application_data_type_ref,
            'CONSTANT-REF': self._read_constant_ref,
            # Port interface element
            'INVALIDATION-POLICY': self._read_invalidation_policy,
        }
        self.switcher_all = {}
        self.switcher_all.update(self.switcher_collectable)
        self.switcher_all.update(self.switcher_value_specification)
        self.switcher_all.update(self.switcher_non_collectable)
        self._switcher_type_name = {
            "ApplicationArrayElement": self._read_application_array_element,
            "VariableDataPrototype": self._read_variable_data_prototype,
        }

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

    def read_str(self, xml: str) -> None | ar_document.Document:
        """
        Reads ARXML document from string.
        """
        self.observed_unsupported_elements = set()
        self.document = None
        self.xml_root = ElementTree.fromstring(bytes(xml, encoding="utf-8"))
        self.file_path = ""
        self.file_base_name = ""
        self._clean_namespace('http://autosar.org/schema/r4.0')
        self._read_root_element()
        self._read_packages()
        return self.document

    def read_str_elem(self, xml: str, type_name: str | None = None) -> None | ar_element.ARObject:
        """
        Reads a concrete ARXML element from string.
        This is primarily used for unit-testing.
        """
        self.observed_unsupported_elements = set()
        elem = ElementTree.fromstring(xml)
        if type_name is not None:
            read_method = self._switcher_type_name.get(type_name, None)
        else:
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
                if self.file_path is not None:
                    file = self.file_path if self.use_full_path_on_warning else self.file_base_name
                    print(f"{file}({xml_elem.sourceline}): Unprocessed element <{xml_elem.tag}>", file=sys.stderr)
                else:
                    print(f"Unprocessed element <{xml_elem.tag}>", file=sys.stderr)

    def _raise_parse_error(self, element: ElementTree.Element, message: str):
        """
        Raises an ARXML parse error with message
        """
        file = self.file_path if self.use_full_path_on_warning else self.file_base_name
        header = f"{file}({element.sourceline}): "
        raise ar_exception.ParseError(header + message)

    def _clean_namespace(self, namespace: str) -> None:
        """
        Removes XML namespace in place.
        """
        wrapped = '{' + namespace + '}'
        wrapped_len = len(wrapped)
        for elem in self.xml_root.iter():
            if isinstance(elem.tag, str) and elem.tag.startswith(wrapped):
                elem.tag = elem.tag[wrapped_len:]

    def _read_boolean(self, value: str) -> bool:
        """
        Reads simpleType AR:BOOLEAN--SIMPLE
        """
        if value in ('0', 'false'):
            return False
        elif value in ('1', 'true'):
            return True
        else:
            raise ar_exception.ParseError('Not a boolean value: ' + str(value))

    def _read_number(self, text: str) -> int | float:
        """
        Attempts to convert text to either int or float
        """
        try:
            value = int(text)
        except ValueError:
            try:
                value = float(text)
            except ValueError as exc:
                raise ar_exception.ParseError(f"Not a number: {text}") from exc
        return value

    def _read_integer(self, text: str) -> int:
        """
        Reads AR:INTEGER
        """
        try:
            value = int(text, 0)
        except ValueError as exc:
            raise ar_exception.ParseError(f"Failed to parse integer: {text}") from exc
        return value

    # Abstract base classes

    def _read_referrable(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:REFERRABLE
        Type: Abstract
        """
        short_name = element_map.get('SHORT-NAME')
        if short_name is not None:
            data['name'] = short_name.text
        else:
            raise ar_exception.ParseError(
                "Missing required element SHORT-NAME")
        xml_long_name = element_map.get('LONG-NAME')
        if xml_long_name is not None:
            data['long_name'] = self._read_multi_language_long_name(
                xml_long_name)

    def _read_multi_language_referrable(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:MULTILANGUAGE-REFERRABLE
        Type: Abstract
        """
        xml_long_name = element_map.get('LONG-NAME')
        if xml_long_name is not None:
            data['long_name'] = self._read_multi_language_long_name(xml_long_name)

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
                    self.schema_file = 'AUTOSAR_' + match.group(1) + '.xsd'
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

    def _read_package(self, elem: ElementTree.Element) -> ar_element.Package:
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        package = ar_element.Package(**data)
        self._read_package_group(child_elements, package)
        self._report_unprocessed_elements(child_elements)
        return package

    def _read_package_group(self, element_map: ChildElementMap, package: ar_element.Package) -> None:
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

    def _read_package_elements(self, package: ar_element.Package, xml_elements: ElementTree.Element) -> None:
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

    def _read_sub_packages(self, package: ar_element.Package, xml_packages: ElementTree.Element) -> None:
        """
        Reads AR:AR-PACKAGE.ELEMENTS
        Type: Utility
        """
        for xml_child_package in xml_packages.findall('./AR-PACKAGE'):
            child_package = self._read_package(xml_child_package)
            assert isinstance(child_package, ar_element.Package)
            package.append(child_package)

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
                                                xml_elem: ElementTree.Element) -> MultiLanguageOverviewParagraph:
        """
        Reads complexType AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
        """
        assert xml_elem.tag in {'DESC', 'ITEM-LABEL', 'CHANGE', 'REASON'}
        elem = MultiLanguageOverviewParagraph()
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

    def _read_single_language_unit_names(self, xml_element: ElementTree.Element) -> ar_element.SingleLanguageUnitNames:
        """
        Reads complex type AR:SINGLE-LANGUAGE-UNIT-NAMES
        Type: concrete
        Tag variants: 'PRM-UNIT' | 'UNIT-DISPLAY-NAME' | 'UNIT-DISPLAY-NAME' | 'DISPLAY-NAME'
        """
        elem = ar_element.SingleLanguageUnitNames()
        self._read_mixed_content_for_unit_names(xml_element, elem)
        return elem

    def _read_mixed_content_for_unit_names(self,
                                           xml_element: ElementTree.Element,
                                           elem: ar_element.SingleLanguageUnitNames) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-UNIT-NAMES
        Type: Abstract
        """
        if xml_element.text:
            elem.append(xml_element.text)
        for xml_child_elem in xml_element.findall('./*'):
            if xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_element.text)

    # CompuMethod elements

    def _read_compu_method(self, xml_element: ElementTree.Element) -> ar_element.CompuMethod:
        """
        Reads Complex type AR:COMPU-METHOD
        Type: Concrete
        Tag variants: 'COMPU-METHOD'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_compu_method_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompuMethod(**data)

    def _read_compu_method_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group type AR:COMPU-METHOD
        Type: Abstract
        Tag variants: 'COMPU-METHOD'
        """
        xml_child = child_elements.get("DISPLAY-FORMAT")
        if xml_child is not None:
            data["display_format"] = xml_child.text
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        xml_child = child_elements.get("COMPU-INTERNAL-TO-PHYS")
        if xml_child is not None:
            data["int_to_phys"] = self._read_computation(xml_child)
        xml_child = child_elements.get("COMPU-PHYS-TO-INTERNAL")
        if xml_child is not None:
            data["phys_to_int"] = self._read_computation(xml_child)

    def _read_computation(self, xml_element: ElementTree.Element) -> ar_element.Computation:
        """
        Reads AR:COMPUTATION
        Type: Concrete
        Tag variants: 'COMPU-INT-TO-PHYS', 'COMPU-PHYS-TO-INT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('COMPU-SCALES')
        if xml_child is not None:
            data["compu_scales"] = self._read_compu_scales(xml_child)
        xml_child = child_elements.get('COMPU-DEFAULT-VALUE')
        if xml_child is not None:
            data["default_value"] = self._read_compu_const(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.Computation(**data)

    def _read_compu_scales(self, xml_element: ElementTree.Element) -> list[ar_element.CompuScale]:
        """
        Reads AR:COMPU-SCALES
        Type: Concrete
        Tag variants: 'COMPU-SCALES'
        """
        compu_scales = []
        for xml_child in xml_element.findall("./COMPU-SCALE"):
            compu_scales.append(self._read_compu_scale(xml_child))
        return compu_scales

    def _read_compu_scale(self, xml_element: ElementTree.Element) -> list[ar_element.CompuScale]:
        """
        Reads AR:COMPU-SCALE
        Type: Concrete
        Tag variants: 'COMPU-SCALE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text
        xml_child = child_elements.get("SYMBOL")
        if xml_child is not None:
            data["symbol"] = xml_child.text
        xml_child = child_elements.get("DESC")
        if xml_child is not None:
            data["desc"] = self._read_multi_language_overview_paragraph(xml_child)
        xml_child = child_elements.get("MASK")
        if xml_child is not None:
            data["mask"] = int(xml_child.text)
        xml_child = child_elements.get("LOWER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["lower_limit"] = limit
            data["lower_limit_type"] = interval_type
        xml_child = child_elements.get("UPPER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["upper_limit"] = limit
            data["upper_limit_type"] = interval_type
        xml_child = child_elements.get("COMPU-INVERSE-VALUE")
        if xml_child is not None:
            data["inverse_value"] = self._read_compu_const(xml_child)
        compu_const_xml = child_elements.get("COMPU-CONST")
        compu_rational_xml = child_elements.get("COMPU-RATIONAL-COEFFS")
        if (compu_const_xml is not None) and (compu_rational_xml is not None):
            raise ar_exception.ParseError("Can't define both COMPU-CONST and COMPU-RATIONAL-COEFFS"
                                          "in the same COMPU-SCALE element")
        if compu_const_xml is not None:
            data["content"] = self._read_compu_const(compu_const_xml)
        elif compu_rational_xml is not None:
            data["content"] = self._read_compu_rational(compu_rational_xml)
        child_elements.skip("VARIATION-POINT")  # Not supported
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompuScale(**data)

    def _read_limit(self, xml_element: ElementTree.Element) -> tuple[int | float, ar_enum.IntervalType]:
        interval_type = xml_element.attrib.get("INTERVAL-TYPE")
        if interval_type is not None:
            interval_type = ar_enum.xml_to_enum("IntervalType", interval_type)
        else:
            # If the attribute is missing the interval shall be considered as "CLOSED"
            interval_type = ar_enum.IntervalType.CLOSED
        limit = self._read_number(xml_element.text)
        return limit, interval_type

    def _read_compu_const(self, xml_element: ElementTree.Element) -> ar_element.CompuConst:
        """
        Reads AR:COMPU-CONST
        Type: Concrete
        Tag variants: 'COMPU-CONST'
        """
        v_xml = xml_element.find("V")
        vt_xml = xml_element.find("VT")
        if (v_xml is not None) and (vt_xml is not None):
            raise ar_exception.ParseError("Can't define both V and VT"
                                          "in the same COMPU-CONST element")
        if v_xml is not None:
            value = self._read_number(v_xml.text)
        elif vt_xml is not None:
            value = vt_xml.text
        else:
            raise ar_exception.ParseError("COMPU-CONST without value isn't supported")
        return ar_element.CompuConst(value)

    def _read_compu_rational(self, xml_element: ElementTree.Element) -> ar_element.CompuRational:
        """
        Reads AR:COMPU-RATIONAL-COEFFS
        Type: Concrete
        Tag variants: 'COMPU-RATIONAL-COEFFS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('COMPU-NUMERATOR')
        if xml_child is not None:
            data['numerator'] = self._read_compu_numerator_denominator_values(xml_child)
        xml_child = child_elements.get('COMPU-DENOMINATOR')
        if xml_child is not None:
            data['denominator'] = self._read_compu_numerator_denominator_values(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompuRational(**data)

    def _read_compu_numerator_denominator_values(self, xml_element: ElementTree.Element) -> tuple:
        """
        Reads AR:COMPU-NOMINATOR-DENOMINATOR
        Type: Concrete
        Tag variants: 'COMPU-NUMERATOR' | 'COMPU-DENOMINATOR'
        """
        values = []
        for xml_child in xml_element.findall('./V'):
            num_val = ar_element.NumericalValue(xml_child.text)
            values.append(num_val.value)
        return tuple(values)

    # Constraint elements

    def _read_data_constraint(self, xml_element: ElementTree.Element) -> ar_element.DataConstraint:
        """
        Writes complex type AR:DATA-CONSTRS
        Type: Concrete
        Tag variants: 'DATA-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_data_constraint_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataConstraint(**data)

    def _read_data_constraint_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group type AR:DATA-CONSTRS
        Type: Abstract
        """
        xml_child = child_elements.get("DATA-CONSTR-RULES")
        if xml_child is not None:
            rules = []
            for xml_data_constr_rule in xml_child.findall("./DATA-CONSTR-RULE"):
                rules.append(self._read_data_constraint_rule(xml_data_constr_rule))
            data["rules"] = rules

    def _read_data_constraint_rule(self, xml_element: ElementTree.Element) -> ar_element.DataConstraintRule:
        """
        Writes complex type AR:INTERNAL-CONSTRS
        Type: Concrete
        Tag variants: 'INTERNAL-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONSTR-LEVEL")
        if xml_child is not None:
            data["level"] = int(xml_child.text)
        xml_child = child_elements.get("PHYS-CONSTRS")
        if xml_child is not None:
            data["physical"] = self._read_physical_constraint(xml_child)
        xml_child = child_elements.get("INTERNAL-CONSTRS")
        if xml_child is not None:
            data["internal"] = self._read_internal_constraint(xml_child)
        return ar_element.DataConstraintRule(**data)

    def _read_internal_constraint(self, xml_element: ElementTree.Element) -> ar_element.InternalConstraint:
        """
        Writes complex type AR:INTERNAL-CONSTRS
        Type: Concrete
        Tag variants: 'INTERNAL-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_constraint_base(child_elements, data)
        return ar_element.InternalConstraint(**data)

    def _read_physical_constraint(self, xml_element: ElementTree.Element) -> ar_element.PhysicalConstraint:
        """
        Writes complex type AR:PHYS-CONSTRS
        Type: Concrete
        Tag variants: 'PHYS-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_constraint_base(child_elements, data)
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        return ar_element.PhysicalConstraint(**data)

    def _read_constraint_base(self, child_elements: ChildElementMap, data: dict[str, Any]) -> None:
        """
        Reads elements common for both AR:INTERNAL-CONSTRS and AR:PHYS-CONSTRS
        Type: Abstract
        """
        xml_child = child_elements.get("LOWER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["lower_limit"] = limit
            data["lower_limit_type"] = interval_type
        xml_child = child_elements.get("UPPER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["upper_limit"] = limit
            data["upper_limit_type"] = interval_type
        xml_child = child_elements.get("SCALE-CONSTRS")
        if xml_child is not None:
            data["scale_constr"] = self._read_scale_constraints(xml_child)
        xml_child = child_elements.get("MAX-GRADIENT")
        if xml_child is not None:
            data["max_gradient"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("MAX-DIFF")
        if xml_child is not None:
            data["max_diff"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("MONOTONY")
        if xml_child is not None:
            data["monotony"] = ar_enum.xml_to_enum("Monotony", xml_child.text)

    def _read_scale_constraints(self, xml_element: ElementTree.Element) -> list[ar_element.ScaleConstraint]:
        """
        Reads SCALE-CONSTRS (list of AR:SCALE-CONSTR)
        Type: Concrete
        Tag variant: Not applicable
        """
        scale_constrs = []
        for xml_child in xml_element.findall('./SCALE-CONSTR'):
            props_conditional = self._read_scale_constraint(
                xml_child)
            scale_constrs.append(props_conditional)
        return scale_constrs

    def _read_scale_constraint(self, xml_element: ElementTree.Element) -> ar_element.ScaleConstraint:
        """
        Writes complex type AR:SCALE-CONSTR
        Type: Concrete
        Tag variants: 'SCALE-CONSTR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text
        xml_child = child_elements.get("DESC")
        if xml_child is not None:
            data["desc"] = self._read_multi_language_overview_paragraph(xml_child)
        xml_child = child_elements.get("LOWER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["lower_limit"] = limit
            data["lower_limit_type"] = interval_type
        xml_child = child_elements.get("UPPER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["upper_limit"] = limit
            data["upper_limit_type"] = interval_type
        return ar_element.ScaleConstraint(**data)

    # Unit elements

    def _read_unit(self, xml_element: ElementTree.Element) -> ar_element.Unit:
        """
        Reads Complex type AR:UNIT
        Type: Concrete
        Tag variants: 'UNIT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_unit_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.Unit(**data)

    def _read_unit_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-ADDR-METHOD
        Type: Utility
        """
        xml_child = child_elements.get("DISPLAY-NAME")
        if xml_child is not None:
            data["display_name"] = self._read_single_language_unit_names(xml_child)
        xml_child = child_elements.get("FACTOR-SI-TO-UNIT")
        if xml_child is not None:
            data["factor"] = float(xml_child.text)
        xml_child = child_elements.get("OFFSET-SI-TO-UNIT")
        if xml_child is not None:
            data["offset"] = float(xml_child.text)
        xml_child = child_elements.get("PHYSICAL-DIMENSION-REF")
        if xml_child is not None:
            data["physical_dimension_ref"] = self._read_physical_dimension_ref(xml_child)

    # Data type elements

    def _read_sw_addr_method(self, xml_element: ElementTree.Element) -> ar_element.SwAddrMethod:
        """
        Reads Complex type AR:SW-ADDR-METHOD
        Type: Concrete
        Tag variants: 'SW-ADDR-METHOD'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_addr_method_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwAddrMethod(**data)

    def _read_sw_addr_method_group(self, child_elements: ChildElementMap, _: dict) -> None:
        """
        Reads group AR:SW-ADDR-METHOD
        Type: Utility
        """
        child_elements.skip('MEMORY-ALLOCATION-KEYWORD-POLICY')  # Not implemented
        child_elements.skip('OPTIONS')  # Not implemented
        child_elements.skip('SECTION-INITIALIZATION-POLICY')  # Not implemented
        child_elements.skip('SECTION-TYPE')  # Not Implemented

    def _read_sw_base_type(self, xml_element: ElementTree.Element) -> ar_element.SwBaseType:
        """
        Reads Complex-type AR:SW-BASE-TYPE
        Type: Concrete
        Tag variants: 'SW-BASE-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_base_type(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwBaseType(**data)

    def _read_base_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads groups AR:BASE-TYPE and AR:BASE-TYPE-DIRECT-DEFINITION
        Type: Abstract
        """
        xml_child: ElementTree.Element | None = None
        xml_child = child_elements.get('BASE-TYPE-SIZE')
        if xml_child is not None:
            data['size'] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get('MAX-BASE-TYPE-SIZE')
        if xml_child is not None:
            data['max_size'] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get('BASE-TYPE-ENCODING')
        if xml_child is not None:
            data['encoding'] = str(xml_child.text)
        xml_child = child_elements.get('MEM-ALIGNMENT')
        if xml_child is not None:
            data['alignment'] = ar_element.PositiveIntegerValue(xml_child.text).value
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
            data['position'] = int(bit_position.text)
        number_of_bits = child_elements.get('NUMBER-OF-BITS')
        if number_of_bits is not None:
            data['num_bits'] = int(number_of_bits.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwBitRepresentation(**data)

    def _read_sw_data_def_props(self, xml_element: ElementTree.Element) -> ar_element.SwDataDefProps:
        """
        Reads complex type AR:SW-DATA-DEF-PROPS
        Type: Concrete
        Tag Variants: 'SW-DATA-DEF-PROPS', 'NETWORK-REPRESENTATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SW-DATA-DEF-PROPS-VARIANTS")
        if xml_child is not None:
            data['variants'] = self._read_sw_data_def_props_variants(xml_child)
        return ar_element.SwDataDefProps(**data)

    def _read_sw_data_def_props_variants(self,
                                         xml_elem: ElementTree.Element) -> list[ar_element.SwDataDefPropsConditional]:
        """
        Reads SW-DATA-DEF-PROPS-VARIANTS
        Type: Concrete
        """
        variants = []
        for xml_child in xml_elem.findall('./SW-DATA-DEF-PROPS-CONDITIONAL'):
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
        child_elements = ChildElementMap(xml_elem)
        self._read_sw_data_def_props_content(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwDataDefPropsConditional(**data)

    def _read_sw_data_def_props_content(self, child_elements: ChildElementMap, data: dict[str, Any]) -> None:
        """
        Reads Group SW-DATA-DEF-PROPS-CONTENT
        Type: Abstract
        """
        xml_child: ElementTree.Element = child_elements.get('DISPLAY-PRESENTATION')
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
            data['sw_addr_method_ref'] = self._read_sw_addr_method_ref(
                xml_child)
        xml_child = child_elements.get('SW-ALIGNMENT')
        if xml_child is not None:
            try:
                sw_alignment = int(xml_child.text, 0)
            except ValueError:
                sw_alignment = xml_child.text
            data['alignment'] = sw_alignment
        xml_child = child_elements.get('BASE-TYPE-REF')
        if xml_child is not None:
            data['base_type_ref'] = self._read_sw_base_type_ref(xml_child)
        xml_child = child_elements.get('SW-BIT-REPRESENTATION')
        if xml_child is not None:
            data['bit_representation'] = self._read_sw_bit_representation(
                xml_child)
        xml_child = child_elements.get('SW-CALIBRATION-ACCESS')
        if xml_child is not None:
            data['calibration_access'] = ar_enum.xml_to_enum('SwCalibrationAccess',
                                                             xml_child.text)
        xml_child = child_elements.get('SW-TEXT-PROPS')
        if xml_child is not None:
            data['text_props'] = self._read_sw_text_props(xml_child)
        xml_child = child_elements.get('COMPU-METHOD-REF')
        if xml_child is not None:
            data['compu_method_ref'] = self._read_compu_method_ref(xml_child)
        xml_child = child_elements.get('DATA-CONSTR-REF')
        if xml_child is not None:
            data['data_constraint_ref'] = self._read_data_constraint_ref(xml_child)
        xml_child = child_elements.get('DISPLAY-FORMAT')
        if xml_child is not None:
            data['display_format'] = xml_child.text
        xml_child = child_elements.get('IMPLEMENTATION-DATA-TYPE-REF')
        if xml_child is not None:
            data['impl_data_type_ref'] = self._read_impl_data_type_ref(xml_child)
        xml_child = child_elements.get('SW-IMPL-POLICY')
        if xml_child is not None:
            data['impl_policy'] = ar_enum.xml_to_enum('SwImplPolicy', xml_child.text)
        xml_child = child_elements.get('ADDITIONAL-NATIVE-TYPE-QUALIFIER')
        if xml_child is not None:
            data['additional_native_type_qualifier'] = xml_child.text
        xml_child = child_elements.get('SW-INTENDED-RESOLUTION')
        if xml_child is not None:
            data['intended_resolution'] = self._read_number(xml_child.text)
        xml_child = child_elements.get('SW-INTERPOLATION-METHOD')
        if xml_child is not None:
            data['interpolation_method'] = xml_child.text
        xml_child = child_elements.get('SW-IS-VIRTUAL')
        if xml_child is not None:
            data['is_virtual'] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get('SW-POINTER-TARGET-PROPS')
        if xml_child is not None:
            data['ptr_target_props'] = self._read_sw_pointer_target_props(xml_child)
        xml_child = child_elements.get('UNIT-REF')
        if xml_child is not None:
            data['unit_ref'] = self._read_unit_ref(xml_child)

    def _read_sw_text_props(self, xml_element: ElementTree.Element) -> ar_element.SwBitRepresentation:
        """
        Reads AR:SW-TEXT-PROPS
        Type: Concrete
        Tag variants: 'SW-TEXT-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('ARRAY-SIZE-SEMANTICS')
        if xml_child is not None:
            data['array_size_semantics'] = ar_enum.xml_to_enum('ArraySizeSemantics', xml_child.text)
        xml_child = child_elements.get('SW-MAX-TEXT-SIZE')
        if xml_child is not None:
            data['max_text_size'] = self._read_integer(xml_child.text)
        xml_child = child_elements.get('BASE-TYPE-REF')
        if xml_child is not None:
            data['base_type_ref'] = self._read_sw_base_type_ref(xml_child)
        xml_child = child_elements.get('SW-FILL-CHARACTER')
        if xml_child is not None:
            data['fill_char'] = self._read_integer(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwTextProps(**data)

    def _read_sw_pointer_target_props(self, xml_element: ElementTree.Element) -> ar_element.SwPointerTargetProps:
        """
        Reads AR:SW-POINTER-TARGET-PROPS
        Type: Concrete
        Tag variants: 'SW-POINTER-TARGET-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('TARGET-CATEGORY')
        if xml_child is not None:
            data['target_category'] = xml_child.text
        xml_child = child_elements.get('SW-DATA-DEF-PROPS')
        if xml_child is not None:
            data['sw_data_def_props'] = self._read_sw_data_def_props(xml_child)
        xml_child = child_elements.get('FUNCTION-POINTER-SIGNATURE-REF')
        if xml_child is not None:
            data['function_ptr_signature_ref'] = self._read_function_ptr_signature_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwPointerTargetProps(**data)

    def _read_symbol_props(self, xml_element: ElementTree.Element) -> ar_element.SymbolProps:
        """
        Reads complex type AR:SYMBOL-PROPS
        Type: Concrete
        Tag variants: 'SYMBOL-PROPS', 'EVENT-SYMBOL-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_implementation_props(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SymbolProps(**data)

    def _read_implementation_props(self,
                                   child_elements: ChildElementMap,
                                   data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION-PROPS
        Type: Abstract
        """
        xml_child = child_elements.get('SYMBOL')
        if xml_child is not None:
            data['symbol'] = xml_child.text

    def _read_implementation_data_type_element(self,
            xml_element: ElementTree.Element) -> ar_element.ImplementationDataTypeElement:  # noqa E128
        """
        Reads complex type AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
        Type: Concrete
        Tag variants: 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_implementation_data_type_element_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ImplementationDataTypeElement(**data)

    def _read_implementation_data_type_element_group(self,
                                                     child_elements: ChildElementMap,
                                                     data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
        Type: Abstract
        """
        xml_child = child_elements.get("ARRAY-IMPL-POLICY")
        if xml_child is not None:
            data["array_impl_policy"] = ar_enum.xml_to_enum("ArrayImplPolicy", xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE")
        if xml_child is not None:
            data["array_size"] = int(xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE-HANDLING")
        if xml_child is not None:
            data["array_size_handling"] = ar_enum.xml_to_enum("ArraySizeHandling", xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE-SEMANTICS")
        if xml_child is not None:
            data["array_size_semantics"] = ar_enum.xml_to_enum("ArraySizeSemantics", xml_child.text)
        xml_child = child_elements.get("IS-OPTIONAL")
        if xml_child is not None:
            data["is_optional"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("SUB-ELEMENTS")
        if xml_child is not None:
            sub_elements = []
            for sub_element_xml in xml_child.findall("./IMPLEMENTATION-DATA-TYPE-ELEMENT"):
                sub_elements.append(self._read_implementation_data_type_element(sub_element_xml))
            data["sub_elements"] = sub_elements
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)
        child_elements.skip("VARIATION-POINT")  # Not supported

    def _read_implementation_data_type(self, xml_element: ElementTree.Element) -> ar_element.ImplementationDataType:
        """
        Reads complex type AR:IMPLEMENTATION-DATA-TYPE
        Type: Concrete
        Tag Variants: 'IMPLEMENTATION-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._read_implementation_data_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ImplementationDataType(**data)

    def _read_implementation_data_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION-DATA-TYPE
        Type: Abstract
        """
        xml_child = child_elements.get("DYNAMIC-ARRAY-SIZE-PROFILE")
        if xml_child is not None:
            data["dynamic_array_size_profile"] = xml_child.text
        xml_child = child_elements.get("IS-STRUCT-WITH-OPTIONAL-ELEMENT")
        if xml_child is not None:
            data["is_struct_with_optional_element"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("SUB-ELEMENTS")
        if xml_child is not None:
            sub_elements = []
            for sub_element_xml in xml_child.findall("./IMPLEMENTATION-DATA-TYPE-ELEMENT"):
                sub_elements.append(self._read_implementation_data_type_element(sub_element_xml))
            data["sub_elements"] = sub_elements
        xml_child = child_elements.get("SYMBOL-PROPS")
        if xml_child is not None:
            data["symbol_props"] = self._read_symbol_props(xml_child)
        xml_child = child_elements.get("TYPE-EMITTER")
        if xml_child is not None:
            data["type_emitter"] = xml_child.text

    def _read_autosar_data_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AUTOSAR-DATA-TYPE
        Type: Abstract
        """
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)

    def _read_data_prototype(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:DATA-PROTOTYPE
        Type: Abstract
        """
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)

    def _read_application_primitive_data_type(
            self,
            xml_element: ElementTree.Element) -> ar_element.ApplicationPrimitiveDataType:
        """
        Reads complex type AR:APPLICATION-PRIMITIVE-DATA-TYPE
        Type: Concrete
        Tag variants: 'APPLICATION-PRIMITIVE-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationPrimitiveDataType(**data)

    def _read_application_composite_element_data_prototype(
            self,
            child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE
        Type: Abstract
        """
        xml_child = child_elements.get("TYPE-TREF")
        if xml_child is not None:
            data["type_ref"] = self._read_application_data_type_ref(xml_child)

    def _read_autosar_data_prototype(
            self,
            child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AUTOSAR-DATA-PROTOTYPE
        Type: Abstract
        """
        xml_child = child_elements.get("TYPE-TREF")
        if xml_child is not None:
            data["type_ref"] = self._read_autosar_data_type_ref(xml_child)

    def _read_application_array_element(self, xml_element: ElementTree.Element) -> ar_element.ApplicationArrayElement:
        """
        Reads complex type AR:APPLICATION-ARRAY-ELEMENT
        Type: Concrete
        Tag variants: 'ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_application_composite_element_data_prototype(child_elements, data)
        self._read_application_array_element_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationArrayElement(**data)

    def _read_application_array_element_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads complex type AR:APPLICATION-ARRAY-ELEMENT
        Type: Abstract
        """
        xml_child = child_elements.get("ARRAY-SIZE-HANDLING")
        if xml_child is not None:
            data["array_size_handling"] = ar_enum.xml_to_enum("ArraySizeHandling", xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE-SEMANTICS")
        if xml_child is not None:
            data["array_size_semantics"] = ar_enum.xml_to_enum("ArraySizeSemantics", xml_child.text)
        xml_child = child_elements.get("INDEX-DATA-TYPE-REF")
        if xml_child is not None:
            data["index_data_type_ref"] = self._read_index_data_type_ref(xml_child)
        xml_child = child_elements.get("MAX-NUMBER-OF-ELEMENTS")
        if xml_child is not None:
            data["max_number_of_elements"] = int(xml_child.text)

    def _read_application_record_element(self, xml_element: ElementTree.Element) -> ar_element.ApplicationRecordElement:
        """
        Reads complex type AR:APPLICATION-RECORD-ELEMENT
        Type: Concrete
        Tag variants: 'APPLICATION-RECORD-ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_application_composite_element_data_prototype(child_elements, data)
        self._read_application_record_element_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationRecordElement(**data)

    def _read_application_record_element_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads complex type AR:APPLICATION-RECORD-ELEMENT
        Type: Abstract
        """
        xml_child = child_elements.get("IS-OPTIONAL")
        if xml_child is not None:
            data["is_optional"] = self._read_boolean(xml_child.text)

    def _read_application_array_data_type(
            self,
            xml_element: ElementTree.Element) -> ar_element.ApplicationArrayDataType:
        """
        Reads complex type AR:APPLICATION-ARRAY-DATA-TYPE
        Type: Concrete
        Tag variants: 'APPLICATION-ARRAY-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._read_application_array_data_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationArrayDataType(**data)

    def _read_application_array_data_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-ARRAY-DATA-TYPE
        """
        xml_child = child_elements.get("DYNAMIC-ARRAY-SIZE-PROFILE")
        if xml_child is not None:
            data["dynamic_array_size_profile"] = xml_child.text
        xml_child = child_elements.get("ELEMENT")
        if xml_child is not None:
            data["element"] = self._read_application_array_element(xml_child)

    def _read_application_record_data_type(
            self,
            xml_element: ElementTree.Element) -> ar_element.ApplicationRecordDataType:
        """
        Reads complex type AR:APPLICATION-RECORD-DATA-TYPE
        Type: Concrete
        Tag variants: 'APPLICATION-RECORD-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._read_application_record_data_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationRecordDataType(**data)

    def _read_application_record_data_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-RECORD-DATA-TYPE
        """
        xml_child = child_elements.get("ELEMENTS")
        if xml_child is not None:
            elements = []
            for xml_record_element in xml_child.findall("./APPLICATION-RECORD-ELEMENT"):
                elements.append(self._read_application_record_element(xml_record_element))
            data["elements"] = elements

    def _read_data_type_map(self, xml_element: ElementTree.Element) -> ar_element.DataTypeMap:
        """
        Reads AR:DATA-TYPE-MAP
        Type: Concrete
        Tag variants: 'DATA-TYPE-MAP'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("APPLICATION-DATA-TYPE-REF")
        if xml_child is not None:
            data["appl_data_type_ref"] = self._read_application_data_type_ref(xml_child)
        xml_child = child_elements.get("IMPLEMENTATION-DATA-TYPE-REF")
        if xml_child is not None:
            data["impl_data_type_ref"] = self._read_impl_data_type_ref(xml_child)
        return ar_element.DataTypeMap(**data)

    def _read_data_type_mapping_set(self, xml_element: ElementTree.Element) -> ar_element.DataTypeMappingSet:
        """
        Reads AR:DATA-TYPE-MAPPING-SET
        Type: Concrete
        Tag variants: 'DATA-TYPE-MAPPING-SET'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_read_data_type_mapping_set_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.DataTypeMappingSet(**data)
        return element

    def _read_read_data_type_mapping_set_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:DATA-TYPE-MAPPING-SET
        Type: Abstract
        """
        xml_child = child_elements.get("DATA-TYPE-MAPS")
        if xml_child is not None:
            data_type_maps = []
            for xml_data_type_map_element in xml_child.findall("./DATA-TYPE-MAP"):
                data_type_maps.append(self._read_data_type_map(xml_data_type_map_element))
            data["data_type_maps"] = data_type_maps

    def _read_value_list(self, xml_element: ElementTree.Element) -> ar_element.ValueList:
        """
        Reads complex-type AR:VALUE-LIST
        Type: Concrete
        Tag variants: 'SW-ARRAYSIZE'
        """
        values = []
        data = {"values": values}
        for xml_value in xml_element.findall("./V"):
            number = ar_element.NumericalValue(xml_value.text)
            if number.value_format in (ar_enum.ValueFormat.HEXADECIMAL,
                                       ar_enum.ValueFormat.BINARY,
                                       ar_enum.ValueFormat.SCIENTIFIC):
                values.append(number)
            else:
                values.append(number.value)
        element = ar_element.ValueList(**data)
        return element

    def _read_variable_data_prototype(self, elem: ElementTree.Element) -> ar_element.VariableDataPrototype:
        """
        Reads complex-type AR:VARIABLE-DATA-PROTOTYPE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_autosar_data_prototype(child_elements, data)
        self._read_variable_data_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.VariableDataPrototype(**data)

    def _read_variable_data_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:VARIABLE-DATA-PROTOTYPE
        """
        xml_child = child_elements.get('INIT-VALUE')
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        child_elements.skip('VARIATION-POINT')  # Not supported

    # Reference elements

    def _read_compu_method_ref(self, xml_elem: ElementTree.Element) -> ar_element.CompuMethodRef:
        """
        Reads AR:COMPU-METHOD-REF
        Type: Concrete
        Tag Variants: 'COMPU-METHOD-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'COMPU-METHOD':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'COMPU-METHOD', got '{data['dest']}'")
        return ar_element.CompuMethodRef(xml_elem.text)

    def _read_data_constraint_ref(self, xml_elem: ElementTree.Element) -> ar_element.DataConstraintRef:
        """
        Reads AR:DATA-CONSTR-REF
        Type: Concrete
        Tag Variants: 'DATA-CONSTR-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'DATA-CONSTR':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'DATA-CONSTR', got '{data['dest']}'")
        return ar_element.DataConstraintRef(xml_elem.text)

    def _read_function_ptr_signature_ref(self, xml_elem: ElementTree.Element) -> ar_element.FunctionPtrSignatureRef:
        """
        Reads AR:FUNCTION-POINTER-SIGNATURE-REF
        Type: Concrete
        Tag Variants: 'FUNCTION-POINTER-SIGNATURE-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'BSW-MODULE-ENTRY':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'BSW-MODULE-ENTRY', got '{data['dest']}'")
        return ar_element.FunctionPtrSignatureRef(xml_elem.text)

    def _read_impl_data_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.ImplementationDataTypeRef:
        """
        Reads AR:IMPLEMENTATION-DATA-TYPE-REF
        Type: Concrete
        Tag Variants: 'IMPLEMENTATION-DATA-TYPE-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'IMPLEMENTATION-DATA-TYPE':
            raise ar_exception.ParseError(f"Invalid value for DEST. "
                                          f"Expected 'IMPLEMENTATION-DATA-TYPE', got '{data['dest']}'")
        return ar_element.ImplementationDataTypeRef(xml_elem.text)

    def _read_sw_base_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.SwAddrMethodRef:
        """
        Reads AR:SW-BASE-TYPE-REF
        Type: Concrete
        Tag Variants: 'SW-BASE-TYPE-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-BASE-TYPE':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'SW-BASE-TYPE', got '{data['dest']}'")
        return ar_element.SwBaseTypeRef(xml_elem.text)

    def _read_sw_addr_method_ref(self, xml_elem: ElementTree.Element) -> ar_element.SwAddrMethodRef:
        """
        Reads AR:SW-ADDR-METHOD-REF
        Type: Concrete
        Tag variants: 'SW-ADDR-METHOD-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-ADDR-METHOD':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'SW-ADDR-METHOD', got '{data['dest']}'")
        return ar_element.SwAddrMethodRef(xml_elem.text)

    def _read_unit_ref(self, xml_elem: ElementTree.Element):
        """
        Reads AR:UNIT-REF
        Type: Concrete
        Tag variants: 'UNIT-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'UNIT':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'UNIT', got '{data['dest']}'")
        return ar_element.UnitRef(xml_elem.text)

    def _read_physical_dimension_ref(self, xml_elem: ElementTree.Element) -> ar_element.PhysicalDimensionRef:
        """
        Reads PHYSICAL-DIMENSION-REF
        Type: Concrete
        Tag variants: 'PHYSICAL-DIMENSION-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'PHYSICAL-DIMENSION':
            msg = f"Invalid value for DEST. Expected 'PHYSICAL-DIMENSION', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.PhysicalDimensionRef(xml_elem.text)

    def _read_index_data_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.IndexDataTypeRef:
        """
        Reads reference to IndexDataType
        Type: Concrete
        Tag variants: 'INDEX-DATA-TYPE-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'APPLICATION-PRIMITIVE-DATA-TYPE':
            msg = f"Invalid value for DEST. Expected 'APPLICATION-PRIMITIVE-DATA-TYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.IndexDataTypeRef(xml_elem.text)

    def _read_application_data_type_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.ApplicationDataTypeRef:
        """
        Reads reference to ApplicationDataType
        Type: Concrete
        Tag variants: 'TYPE-TREF', 'APPLICATION-DATA-TYPE-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.ApplicationDataTypeRef(xml_elem.text, dest_enum)

    def _read_autosar_data_type_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.AutosarDataTypeRef:
        """
        Reads reference to AutosarDataType
        Type: Concrete
        Tag variants: 'TYPE-TREF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.AutosarDataTypeRef(xml_elem.text, dest_enum)

    def _read_constant_ref(self,
                           xml_elem: ElementTree.Element
                           ) -> ar_element.ConstantRef:
        """
        Reads reference to ConstantSpecification
        Type: Concrete
        Tag variants: 'CONSTANT-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'CONSTANT-SPECIFICATION':
            msg = f"Invalid value for DEST. Expected 'CONSTANT-SPECIFICATION', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ConstantRef(xml_elem.text)

    def _read_variable_data_prototype_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.VariableDataPrototypeRef:
        """
        Reads reference to VariableDataPrototype
        Type: Concrete
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'VARIABLE-DATA-PROTOTYPE':
            msg = f"Invalid value for DEST. Expected 'VARIABLE-DATA-PROTOTYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.VariableDataPrototypeRef(xml_elem.text)

    def _read_base_ref_attributes(self, attr: dict, data: dict) -> None:
        """
        Reads DEST attribute
        """
        data['dest'] = attr.get('DEST', None)
        if data['dest'] is None:
            raise ar_exception.ParseError("Missing required attribute 'DEST'")

    # Constant and value specifications

    def _read_text_value_specification(self,
                                       xml_element: ElementTree.Element) -> ar_element.TextValueSpecification:
        """
        Reads complex-type AR:TEXT-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'TEXT-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_text_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.TextValueSpecification(**data)
        return element

    def _read_text_value_specification_group(self,
                                             child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:TEXT-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("VALUE")
        if xml_child is not None:
            data["value"] = xml_child.text

    def _read_numerical_value_specification(self,
                                            xml_element: ElementTree.Element
                                            ) -> ar_element.NumericalValueSpecification:
        """
        Reads complex-type AR:NUMERICAL-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'NUMERICAL-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_numerical_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.NumericalValueSpecification(**data)
        return element

    def _read_numerical_value_specification_group(self,
                                                  child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NUMERICAL-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("VALUE")
        if xml_child is not None:
            data["value"] = ar_element.NumericalValue(xml_child.text).value

    def _read_not_available_value_specification(self,
                                                xml_element: ElementTree.Element
                                                ) -> ar_element.NotAvailableValueSpecification:
        """
        Reads complex-type AR:NOT-AVAILABLE-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'NOT-AVAILABLE-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_not_available_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.NotAvailableValueSpecification(**data)
        return element

    def _read_not_available_value_specification_group(self,
                                                      child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NOT-AVAILABLE-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("DEFAULT-PATTERN")
        if xml_child is not None:
            wrapped_value = ar_element.PositiveIntegerValue(xml_child.text)
            data["default_pattern"] = wrapped_value.value
            # TODO: Add support for retaining used number format

    def _read_array_value_specification(self,
                                        xml_element: ElementTree.Element) -> ar_element.ArrayValueSpecification:
        """
        Reads complex-type AR:ARRAY-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'ARRAY-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_array_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.ArrayValueSpecification(**data)
        return element

    def _read_array_value_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ARRAY-VALUE-SPECIFICATION
        """
        xml_elements = child_elements.get("ELEMENTS")
        if xml_elements is not None:
            elements = []
            for xml_child_elem in xml_elements.findall('./*'):
                element = self._read_value_specification_element(xml_child_elem)
                elements.append(element)
            data["elements"] = elements

    def _read_record_value_specification(self,
                                         xml_element: ElementTree.Element) -> ar_element.RecordValueSpecification:
        """
        Reads complex-type AR:RECORD-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'RECORD-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_record_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.RecordValueSpecification(**data)
        return element

    def _read_record_value_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:RECORD-VALUE-SPECIFICATION
        """
        xml_elements = child_elements.get("FIELDS")
        if xml_elements is not None:
            fields = []
            for xml_child_elem in xml_elements.findall('./*'):
                field = self._read_value_specification_element(xml_child_elem)
                fields.append(field)
            data["fields"] = fields

    def _read_value_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text

    def _read_application_value_specification(self,
                                              xml_element: ElementTree.Element
                                              ) -> ar_element.ApplicationValueSpecification:
        """
        Reads complex-type AR:APPLICATION-VALUE-SPECIFICATION
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_application_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.ApplicationValueSpecification(**data)
        return element

    def _read_application_value_specification_group(self,
                                                    child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("CATEGORY")
        if xml_child is not None:
            data["category"] = xml_child.text
        xml_child = child_elements.get("SW-AXIS-CONTS")
        if xml_child is not None:
            elements = []
            for xml_grand_child in xml_child.findall("./SW-AXIS-CONT"):
                elements.append(self._read_sw_axis_cont(xml_grand_child))
            data["sw_axis_conts"] = elements
        xml_child = child_elements.get("SW-VALUE-CONT")
        if xml_child is not None:
            data["sw_value_cont"] = self._read_sw_value_cont(xml_child)

    def _read_value_specification_element(self,
                                          xml_element: ElementTree.Element) -> ValueSpeficationElement:
        """
        Reads any ValueSpecificationElement
        """
        read_method = self.switcher_value_specification.get(xml_element.tag, None)
        if read_method is not None:
            return read_method(xml_element)
        else:
            raise KeyError(f"Found no reader for '{xml_element.tag}'")

    def _read_constant_specification(self,
                                     xml_element: ElementTree.Element) -> ar_element.ConstantSpecification:
        """
        Reads complex type AR:CONSTANT-SPECIFICATION
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_constant_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ConstantSpecification(**data)

    def _read_constant_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CONSTANT-SPECIFICATION
        """
        xml_child = child_elements.get("VALUE-SPEC")
        if xml_child is not None:
            xml_grand_child = xml_child.find("./*")
            if xml_grand_child is not None:
                data["value"] = self._read_value_specification_element(xml_grand_child)

    def _read_constant_reference(self,
                                 xml_element: ElementTree.Element
                                 ) -> ar_element.ConstantReference:
        """
        Reads complex-type AR:CONSTANT-REFERENCE
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_constant_reference_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.ConstantReference(**data)
        return element

    def _read_constant_reference_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CONSTANT-REFERENCE
        """
        xml_child = child_elements.get("CONSTANT-REF")
        if xml_child is not None:
            data["constant_ref"] = self._read_constant_ref(xml_child)

    # CalibrationData elements

    def _read_sw_values(self,
                        xml_element: ElementTree.Element) -> ar_element.SwValues:
        """
        Reads complex-type AR:SW-VALUES
        Type: Concrete
        Tag variants: 'SW-VALUES-PHYS'
        """
        data = {}
        child_elements = list(xml_element.findall("./*"))
        self._read_sw_values_group(child_elements, data)
        element = ar_element.SwValues(**data)
        return element

    def _read_sw_values_group(self,
                              xml_child_list: list[ElementTree.Element],
                              data: dict) -> None:
        """
        Reads group AR:SW-VALUES
        Type: Abstract

        XML elements not supported:

        - VTF
        - VF
        """
        values = []
        data["values"] = values
        for xml_child in xml_child_list:
            if xml_child.tag == "VT":
                values.append(xml_child.text)
            elif xml_child.tag == "V":
                number = ar_element.NumericalValue(xml_child.text)
                if number.value_format in (ar_enum.ValueFormat.HEXADECIMAL,
                                           ar_enum.ValueFormat.BINARY,
                                           ar_enum.ValueFormat.SCIENTIFIC):
                    values.append(number)
                else:
                    values.append(number.value)
            elif xml_child.tag == "VG":
                values.append(self._read_value_group(xml_child))
            elif xml_child.tag in ("VTF", "VG"):
                continue  # Not supported, skip
            else:
                print(f"Unprocessed child element in VALUE-GROUP: <{xml_child.tag}>", file=sys.stderr)

    def _read_value_group(self, xml_element: ElementTree.Element) -> ar_element.ValueGroup:
        """
        Reads complex-type AR:VALUE-GROUP
        """
        data = {}
        child_elements = list(xml_element.findall("./*"))
        if len(child_elements) > 0 and child_elements[0].tag == 'LABEL':
            data["label"] = self._read_multi_language_long_name(child_elements.pop(0))
        self._read_sw_values_group(child_elements, data)
        element = ar_element.ValueGroup(**data)
        return element

    def _read_sw_axis_cont(self, xml_element: ElementTree.Element) -> ar_element.SwAxisCont:
        """
        Reads complex-type AR:SW-AXIS-CONT
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_sw_axis_cont_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.SwAxisCont(**data)
        return element

    def _read_sw_axis_cont_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-AXIS-CONT
        """
        xml_child = child_elements.get("CATEGORY")
        if xml_child is not None:
            data["category"] = ar_enum.xml_to_enum("CalibrationAxisCategory", xml_child.text)
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        xml_child = child_elements.get("UNIT-DISPLAY-NAME")
        if xml_child is not None:
            data["unit_display_name"] = self._read_single_language_unit_names(xml_child)
        xml_child = child_elements.get("SW-AXIS-INDEX")
        if xml_child is not None:
            try:
                value = int(xml_child.text)
            except ValueError:
                value = xml_child.text
            data["sw_axis_index"] = value
        xml_child = child_elements.get("SW-ARRAYSIZE")
        if xml_child is not None:
            data["sw_array_size"] = self._read_value_list(xml_child)
        xml_child = child_elements.get("SW-VALUES-PHYS")
        if xml_child is not None:
            data["sw_values_phys"] = self._read_sw_values(xml_child)

    def _read_sw_value_cont(self, xml_element: ElementTree.Element) -> ar_element.SwValueCont:
        """
        Reads complex-type AR:SW-VALUE-CONT
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_sw_value_cont_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.SwValueCont(**data)
        return element

    def _read_sw_value_cont_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-VALUE-CONT
        """
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        xml_child = child_elements.get("UNIT-DISPLAY-NAME")
        if xml_child is not None:
            data["unit_display_name"] = self._read_single_language_unit_names(xml_child)
        xml_child = child_elements.get("SW-ARRAYSIZE")
        if xml_child is not None:
            data["sw_array_size"] = self._read_value_list(xml_child)
        xml_child = child_elements.get("SW-VALUES-PHYS")
        if xml_child is not None:
            data["sw_values_phys"] = self._read_sw_values(xml_child)

    # Port interface elements

    def _read_port_interface(self, xml_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PORT-INTERFACE
        Type: Abstract
        """
        inner_elem = xml_elements.get('IS-SERVICE')
        if inner_elem is not None:
            data['is_service'] = self._read_boolean(inner_elem.text)
        xml_elements.skip('NAMESPACES')  # Not supported
        xml_elements.skip('SERVICE-KIND')  # Implement later

    def _read_sender_receiver_interface(self, xml_element: ElementTree.Element) -> ar_element.SenderReceiverInterface:
        """
        Reads complex type AR:SENDER-RECEIVER-INTERFACE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        self._read_sender_receiver_interface_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SenderReceiverInterface(**data)

    def _read_sender_receiver_interface_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AR-SENDER-RECEIVER-INTERFACE
        Type: Abstract
        """
        xml_child = child_elements.get('DATA-ELEMENTS')
        if xml_child is not None:
            data_elements = []
            data["data_elements"] = data_elements
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'VARIABLE-DATA-PROTOTYPE':
                    element = self._read_variable_data_prototype(xml_grand_child)
                    data_elements.append(element)
        xml_child = child_elements.get('INVALIDATION-POLICYS')
        if xml_child is not None:
            policies = []
            data["invalidation_policies"] = policies
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'INVALIDATION-POLICY':
                    policy = self._read_invalidation_policy(xml_grand_child)
                    policies.append(policy)
        child_elements.skip("META-DATA-ITEM-SETS")  # Not supported

    def _read_invalidation_policy(self, xml_element: ElementTree.Element) -> ar_element.InvalidationPolicy:
        """
        Reads complex-type AR:INVALIDATION-POLICY
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("DATA-ELEMENT-REF")
        if xml_child is not None:
            data["data_element_ref"] = self._read_variable_data_prototype_ref(xml_child)
        xml_child = child_elements.get("HANDLE-INVALID")
        if xml_child is not None:
            data["handle_invalid"] = ar_enum.xml_to_enum("HandleInvalid", xml_child.text)
        return ar_element.InvalidationPolicy(**data)
