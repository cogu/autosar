#!/usr/bin/env python3
"""AUTOSAR XML Schema (XSD) Sub-Element & Dependency Explorer.

This utility helps track what classes need to be implemented in Python for a given
AUTOSAR complex type sub-element in Classic Platform (CP). It traverses child
complex types in the XSD, detects dependencies, checks docstring implementation
status from `element.py`, extracts canonical class names from schema `mmt.qualifiedName`
tags, tracks schema deprecation/status tags (`atp.Status`), filters out Adaptive
Platform (AP) only elements, and computes a bottom-up implementation order (leaves first).

Usage:
    python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR/AR-TYPED-PER-INSTANCE-MEMORYS
    python dev_utils/explore_subelement.py VARIABLE-DATA-PROTOTYPE/SW-DATA-DEF-PROPS
    python dev_utils/explore_subelement.py VARIABLE-DATA-PROTOTYPE/INIT-VALUE
    python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR
    python dev_utils/explore_subelement.py VARIABLE-DATA-PROTOTYPE/INIT-VALUE --all-standards
"""

import argparse
# pylint: disable=duplicate-code
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple
import lxml.etree as ET

# Ensure dev_utils is in sys.path for local imports
_DEV_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
if _DEV_UTILS_DIR not in sys.path:
    sys.path.insert(0, _DEV_UTILS_DIR)
# pyrefly: ignore [missing-import]
import refresh_implementation  # noqa: E402

# Ensure UTF-8 output encoding across platforms
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (ValueError, OSError, AttributeError):
        pass

# XML Schema Namespaces
NS = {
    'xsd': 'http://www.w3.org/2001/XMLSchema',
    'AR': 'http://autosar.org/schema/r4.0'
}

# Explicit mapping of AUTOSAR XML schema types that map directly to Python primitives.
# You can add or customize additional elements in this dictionary as needed.
PRIMITIVE_TYPES: Dict[str, str] = {
    # String primitives
    'IDENTIFIER': 'str',
    'C-IDENTIFIER': 'str',
    'SYMBOL-STRING': 'str',
    'VERBATIM-STRING': 'str',
    'CATEGORY-STRING': 'str',
    'DISPLAY-FORMAT-STRING': 'str',
    'NATIVE-DECLARATION-STRING': 'str',
    'CSE-CODE-TYPE-STRING': 'str',
    'ANY-VERSION-STRING': 'str',
    'STRING': 'str',
    'URL': 'str',
    'URI-STRING': 'str',
    'TT': 'str',
    'SD': 'str',
    'SDF': 'str',
    'REVISION-LABEL-STRING': 'str',
    'SECTION-NAME-STRING': 'str',
    'BYTE-VALUE-LEAD-STRING': 'str',
    # Integer primitives
    'INTEGER': 'int',
    'POSITIVE-INTEGER': 'int',
    'POSITIVE-INTEGER-VALUE': 'int',
    'AXIS-INDEX-TYPE': 'int',
    'ALIGNMENT-TYPE': 'int',
    'TIME-VALUE': 'float',
    'NUMERICAL-VALUE': 'int | float',
    'LIMIT-VALUE': 'int | float',
    # Boolean primitives
    'BOOLEAN': 'bool',
    # Float primitives
    'FLOAT': 'float',
    'DOUBLE': 'float',
    # Variant primitive wrappers
    'NUMERICAL-VALUE-VARIATION-POINT': 'int | float',
    'INTEGER-VALUE-VARIATION-POINT': 'int',
    'POSITIVE-INTEGER-VALUE-VARIATION-POINT': 'int',
    'UNLIMITED-INTEGER-VALUE-VARIATION-POINT': 'int',
    'FLOAT-VALUE-VARIATION-POINT': 'float',
    'BOOLEAN-VALUE-VARIATION-POINT': 'bool',
    'TIME-VALUE-VALUE-VARIATION-POINT': 'float',
    'NAME-TOKEN-VALUE-VARIATION-POINT': 'str',
    'LIMIT': 'int | float | str',
}

# Substrings in XSD package comments for elements ignored / not supported by design
IGNORED_SCHEMA_PATTERNS = [
    'Templates::GenericStructure::VariantHandling',
    'Templates::SWComponentTemplate::SwcInternalBehavior::VariantHandling',
    'Templates::CommonStructure::StandardizationTemplate',
]


def parse_appinfo_tags(elem: Optional[ET._Element]) -> Dict[str, str]:
    """Extract key-value pairs from <xsd:appinfo source="tags"> inside an XSD element."""
    tags: Dict[str, str] = {}
    if elem is None:
        return tags
    for app in elem.xpath('./xsd:annotation/xsd:appinfo[@source="tags"]', namespaces=NS):
        text = app.text or ''
        matches = re.findall(r'([a-zA-Z0-9_.]+)=(?:"([^"]*)"|([^;]+))', text)
        for k, v1, v2 in matches:
            tags[k] = v1 if v1 != '' else v2
    return tags


def get_atp_status(elem: Optional[ET._Element]) -> Optional[str]:
    """Extract atp.Status tag ('draft', 'candidate', 'obsolete', 'removed', 'valid') if present."""
    if elem is None:
        return None
    tags = parse_appinfo_tags(elem)
    return tags.get('atp.Status')


def is_classic_platform(elem: Optional[ET._Element]) -> bool:
    """Return False if element/type is explicitly restricted to Adaptive Platform (AP) only."""
    if elem is None:
        return True
    tags = parse_appinfo_tags(elem)
    if 'mmt.RestrictToStandards' in tags:
        standards = [s.strip() for s in tags['mmt.RestrictToStandards'].split(',')]
        if 'CP' not in standards and standards == ['AP']:
            return False
    return True


def get_qualified_name(elem: Optional[ET._Element], default_name: str = "") -> str:
    """Extract canonical class/property name from mmt.qualifiedName."""
    if elem is None:
        return default_name
    tags = parse_appinfo_tags(elem)
    qname = tags.get('mmt.qualifiedName')
    if qname:
        return qname
    return default_name


class SchemaInspector:
    """Inspects AUTOSAR XSD schemas and tracks type dependencies with atp.Status support."""

    def __init__(self,
                 xsd_path: str,
                 refresh: bool = False,
                 classic_only: bool = True,
                 include_ignored: bool = False,
                 include_deprecated: bool = False):
        """Initialize schema inspector and index XSD types, groups, and status tags."""
        self.xsd_path = os.path.abspath(xsd_path)
        self.classic_only = classic_only
        self.include_ignored = include_ignored
        self.include_deprecated = include_deprecated
        if not os.path.exists(self.xsd_path):
            raise FileNotFoundError(f"Schema file not found: {self.xsd_path}")

        print(f"Loading XML Schema: {self.xsd_path}")
        self.tree = ET.parse(self.xsd_path)
        self.root = self.tree.getroot()

        # Build lookup tables for groups, complexTypes, and simpleTypes
        self.groups: Dict[str, ET._Element] = {}
        for g in self.root.findall('xsd:group', NS):
            name = g.attrib.get('name')
            if name:
                self.groups[name] = g

        self.complex_types: Dict[str, ET._Element] = {}
        for ct in self.root.findall('xsd:complexType', NS):
            name = ct.attrib.get('name')
            if name:
                self.complex_types[name] = ct

        self.simple_types: Dict[str, ET._Element] = {}
        for st in self.root.findall('xsd:simpleType', NS):
            name = st.attrib.get('name')
            if name:
                self.simple_types[name] = st

        # Index atp.Status on types, groups, and simpleTypes
        self.type_status: Dict[str, str] = {}
        for name, ct in self.complex_types.items():
            st = get_atp_status(ct)
            if st:
                self.type_status[name] = st
        for name, grp in self.groups.items():
            st = get_atp_status(grp)
            if st and name not in self.type_status:
                self.type_status[name] = st
        for name, st_el in self.simple_types.items():
            st = get_atp_status(st_el)
            if st and name not in self.type_status:
                self.type_status[name] = st

        # Index ignored types (VariantHandling & StandardizationTemplate / Blueprints) from XSD comments
        self.ignored_types: Set[str] = set()
        self.ignored_groups: Set[str] = set()
        self.ignored_categories: Dict[str, str] = {}
        self._index_ignored_schema_types()

        mode_str = "Classic Platform (CP only)" if self.classic_only else "All Standards (CP + AP)"
        print(f"Schema indexed: {len(self.complex_types)} complexTypes, "
              f"{len(self.groups)} groups, {len(self.simple_types)} simpleTypes. [{mode_str}]")
        print(f"Status tags found: {len(self.type_status)} types/groups with explicit atp.Status")
        print(f"Ignored by design: {len(self.ignored_types)} complexTypes, {len(self.ignored_groups)} groups "
              f"(VariantHandling & StandardizationTemplate/Blueprints)\n")

        self._load_python_cache(force_refresh=refresh)

    def _index_ignored_schema_types(self):
        """Index types and groups matching VariantHandling or StandardizationTemplate comments."""
        for ct in self.complex_types.values():
            name = ct.attrib.get('name')
            if not name:
                continue
            prev = ct.getprevious()
            if prev is not None and callable(prev.tag):
                text = prev.text or ''
                for pat in IGNORED_SCHEMA_PATTERNS:
                    if pat in text:
                        self.ignored_types.add(name)
                        self.ignored_categories[name] = 'Blueprint' if 'StandardizationTemplate' in pat else 'Variant'
                        break

        for g in self.groups.values():
            name = g.attrib.get('name')
            if not name:
                continue
            prev = g.getprevious()
            if prev is not None and callable(prev.tag):
                text = prev.text or ''
                for pat in IGNORED_SCHEMA_PATTERNS:
                    if pat in text:
                        self.ignored_groups.add(name)
                        self.ignored_categories[name] = 'Blueprint' if 'StandardizationTemplate' in pat else 'Variant'
                        break

    def get_type_status(self, type_name: str) -> Optional[str]:
        """Return atp.Status for an AUTOSAR type/group if explicitly tagged, else None (standard/valid)."""
        clean = type_name.replace('AR:', '')
        if clean in self.type_status:
            return self.type_status[clean]
        ct = self.complex_types.get(clean)
        st = get_atp_status(ct)
        if st:
            return st
        grp = self.groups.get(clean)
        st = get_atp_status(grp)
        if st:
            return st
        st_el = self.simple_types.get(clean)
        st = get_atp_status(st_el)
        if st:
            return st
        return None

    def get_effective_status(self,
                             elem: Optional[ET._Element],
                             type_name: Optional[str] = None,
                             parent_status: Optional[str] = None) -> Optional[str]:
        """Determine effective status considering element tag first, then referenced type, then parent status."""
        el_status = get_atp_status(elem)
        if el_status:
            return el_status
        if type_name:
            clean = type_name.replace('AR:', '')
            t_status = self.get_type_status(clean)
            if t_status:
                return t_status
        if parent_status in ('removed', 'obsolete'):
            return parent_status
        return None

    @staticmethod
    def is_deprecated_status(status: Optional[str]) -> bool:
        """Check if status is 'removed' or 'obsolete'."""
        return status in ('removed', 'obsolete')

    def is_ignored_type(self, type_name: str) -> bool:
        """Check if a type is ignored by design (VariantHandling, Blueprint, or deprecated unless requested)."""
        clean = type_name.replace('AR:', '')
        if clean in PRIMITIVE_TYPES:
            return False
        if clean in self.ignored_types or clean in self.ignored_groups:
            return True
        if clean in ('VARIATION-POINT', 'VARIATION-POINT-PROXY'):
            return True
        if not self.include_deprecated and self.is_deprecated_status(self.get_type_status(clean)):
            return True
        return False

    def get_ignored_category(self, type_name: str) -> str:
        """Return category string ('Removed', 'Obsolete', 'Blueprint', 'Variant') for an ignored type."""
        clean = type_name.replace('AR:', '')
        st = self.get_type_status(clean)
        if st and self.is_deprecated_status(st):
            return st.capitalize()
        return self.ignored_categories.get(clean, 'Variant')

    def _load_python_cache(self, force_refresh: bool = False):
        """Load docstring implementation mappings from cache or refresh them."""
        if force_refresh:
            self.cache = refresh_implementation.refresh_cache()
        else:
            self.cache = refresh_implementation.load_cached_implementations()

    def get_canonical_class_name(self, type_name: str) -> str:
        """Get canonical Python class name from mmt.qualifiedName tag in XSD."""
        clean = type_name.replace('AR:', '')
        ct = self.complex_types.get(clean)
        if ct is not None:
            qname = get_qualified_name(ct)
            if qname:
                return qname
        grp = self.groups.get(clean)
        if grp is not None:
            qname = get_qualified_name(grp)
            if qname:
                return qname
        return clean

    def is_standard_supported(self, elem: Optional[ET._Element]) -> bool:
        """Check if an element is supported given the current platform mode (CP vs All)."""
        if not self.classic_only:
            return True
        return is_classic_platform(elem)

    def _detect_simple_content_primitive(self, clean: str, ct: ET._Element) -> Optional[str]:
        sc = ct.find('xsd:simpleContent', NS)
        if sc is None:
            return None
        ext = sc.find('xsd:extension', NS)
        base = ext.attrib.get('base', '').replace('AR:', '') if ext is not None else ''

        if 'REF' in clean or 'REF' in base:
            return None
        if clean.endswith('-ENUM') or base.endswith('-ENUM--SIMPLE') or base.endswith('-ENUM'):
            return None

        base_clean = base.replace('--SIMPLE', '')
        if base_clean in PRIMITIVE_TYPES:
            return PRIMITIVE_TYPES[base_clean]

        rules = [
            (('INT', 'INDEX', 'COUNT'), 'int'),
            (('STRING', 'NAME', 'LABEL', 'TEXT'), 'str'),
            (('BOOL',), 'bool'),
            (('FLOAT', 'TIME'), 'float'),
        ]
        for keywords, ptype in rules:
            if any(w in clean for w in keywords):
                return ptype
        return 'str'

    def _detect_simple_type_primitive(self, clean: str, st: ET._Element) -> Optional[str]:
        if st.findall('xsd:restriction/xsd:enumeration', NS) or clean.endswith('-ENUM'):
            return None
        rest = st.find('xsd:restriction', NS)
        if rest is not None:
            base = rest.attrib.get('base', '')
            if 'integer' in base or 'int' in base:
                return 'int'
            if 'boolean' in base:
                return 'bool'
            if 'double' in base or 'float' in base:
                return 'float'
            return 'str'
        return None

    def detect_primitive_type(self, type_name: str) -> Optional[str]:
        """Check if an AUTOSAR type is a primitive value (str, int, float, bool) in Python."""
        clean = type_name.replace('AR:', '')
        if clean in PRIMITIVE_TYPES:
            return PRIMITIVE_TYPES[clean]

        ct = self.complex_types.get(clean)
        if ct is not None:
            res = self._detect_simple_content_primitive(clean, ct)
            if res is not None:
                return res

        st = self.simple_types.get(clean)
        if st is not None:
            return self._detect_simple_type_primitive(clean, st)

        return None

    def get_implementation_info(self, type_name: str) -> Optional[dict]:
        """Return implementation details for an AUTOSAR complexType, group, enum, or primitive."""
        clean = type_name.replace('AR:', '')

        # 1. Check if it's an implicit primitive type (str, int, float, bool)
        prim_type = self.detect_primitive_type(clean)
        if prim_type:
            return {
                'kind': 'primitive',
                'class_name': prim_type,
                'file': 'built-in',
                'line': None,
                'bases': [],
                'implemented_subelements': [],
                'unimplemented_subelements': [],
                'is_primitive': True
            }

        # 2. Check complex types in docstrings
        cls_name = self.cache.get('complex_types', {}).get(clean)
        if not cls_name:
            cls_name = self.cache.get('tag_variants', {}).get(clean)

        if cls_name:
            cls_info = self.cache.get('classes', {}).get(cls_name, {})
            return {
                'kind': 'complexType',
                'class_name': cls_name,
                'file': 'element.py',
                'line': cls_info.get('line'),
                'bases': cls_info.get('bases', []),
                'implemented_subelements': cls_info.get('implemented_subelements', []),
                'unimplemented_subelements': cls_info.get('unimplemented_subelements', []),
                'is_primitive': False
            }

        # 3. Check groups in docstrings
        grp_cls_name = self.cache.get('groups', {}).get(clean)
        if grp_cls_name:
            cls_info = self.cache.get('classes', {}).get(grp_cls_name, {})
            return {
                'kind': 'group',
                'class_name': grp_cls_name,
                'file': 'element.py',
                'line': cls_info.get('line'),
                'bases': cls_info.get('bases', []),
                'implemented_subelements': cls_info.get('implemented_subelements', []),
                'unimplemented_subelements': cls_info.get('unimplemented_subelements', []),
                'is_primitive': False
            }

        # 4. Check enumerations
        enum_cls_name = self.cache.get('type_to_enum', {}).get(clean)
        if not enum_cls_name:
            clean_no_enum = clean.replace('-ENUM', '').replace('--SIMPLE', '')
            enum_cls_name = self.cache.get('type_to_enum', {}).get(clean_no_enum)

        if enum_cls_name:
            enum_info = self.cache.get('enums', {}).get(enum_cls_name, {})
            return {
                'kind': 'enumeration',
                'class_name': enum_cls_name,
                'file': 'enumeration.py',
                'line': enum_info.get('line'),
                'bases': enum_info.get('bases', []),
                'implemented_subelements': [],
                'unimplemented_subelements': [],
                'is_primitive': False
            }

        # 5. Check references
        ref_cls_name = self.cache.get('type_to_ref', {}).get(clean)
        if not ref_cls_name:
            clean_no_subtypes = clean.replace('--SUBTYPES-ENUM', '')
            ref_cls_name = self.cache.get('type_to_ref', {}).get(clean_no_subtypes)

        if ref_cls_name:
            ref_info = self.cache.get('references', {}).get(ref_cls_name, {})
            return {
                'kind': 'reference',
                'class_name': ref_cls_name,
                'file': 'reference.py',
                'line': ref_info.get('line'),
                'bases': ref_info.get('bases', []),
                'implemented_subelements': [],
                'unimplemented_subelements': [],
                'is_primitive': False,
                'is_ref': True
            }

        return None

    def is_implemented(self, type_name: str) -> bool:
        """Check if an AUTOSAR type has a corresponding class or primitive mapping."""
        return self.get_implementation_info(type_name) is not None

    def get_complex_type_groups(self, ct_name: str) -> List[str]:
        """Return all group references declared in a complexType or group.

        Recursively resolves nested group references in forward declaration order.
        """
        ordered_groups: List[str] = []
        visited: Set[str] = set()

        def resolve_group(gname: str):
            if gname in visited:
                return
            visited.add(gname)
            grp = self.groups.get(gname)
            if grp is not None:
                for sub_g in grp.xpath('.//xsd:group', namespaces=NS):
                    ref = sub_g.attrib.get('ref', '').replace('AR:', '')
                    if ref and ref != gname:
                        resolve_group(ref)
            if gname not in ordered_groups:
                ordered_groups.append(gname)

        ct = self.complex_types.get(ct_name)
        if ct is not None:
            for g in ct.xpath('.//xsd:group', namespaces=NS):
                ref = g.attrib.get('ref', '').replace('AR:', '')
                if ref:
                    resolve_group(ref)
        else:
            resolve_group(ct_name)

        return ordered_groups

    def _find_direct_child_elements(self, container_elem: ET._Element) -> List[ET._Element]:
        """Find all xsd:element definitions under sequences and choices.

        Does not descend into inner complexTypes or group references.
        """
        elems: List[ET._Element] = []
        for child in container_elem:
            if not isinstance(child.tag, str) or child.tag.endswith('annotation'):
                continue
            tag = child.tag.replace('{http://www.w3.org/2001/XMLSchema}', '')
            if tag == 'element':
                elems.append(child)
            elif tag in ('sequence', 'choice'):
                elems.extend(self._find_direct_child_elements(child))
        return elems

    def _get_effective_cardinality(self, el: ET._Element, container_elem: ET._Element) -> Tuple[str, str, bool]:
        """Compute effective minOccurs, maxOccurs, and list status considering parent choices/sequences."""
        min_occurs = el.attrib.get('minOccurs', '1')
        max_occurs = el.attrib.get('maxOccurs', '1')

        curr = el.getparent()
        while curr is not None and curr != container_elem:
            tag = curr.tag.replace('{http://www.w3.org/2001/XMLSchema}', '') if isinstance(curr.tag, str) else ''
            if tag == 'choice':
                min_occurs = '0'
            if curr.attrib.get('minOccurs') == '0':
                min_occurs = '0'
            if curr.attrib.get('maxOccurs') == 'unbounded':
                max_occurs = 'unbounded'
            curr = curr.getparent()

        is_list = max_occurs == 'unbounded'
        return min_occurs, max_occurs, is_list

    def _extract_wrapper_inner_elements(self, el: ET._Element, is_wrapper_list: bool) -> List[dict]:
        """Extract inner elements defined within a wrapper element."""
        inner_elements = el.xpath('.//xsd:element', namespaces=NS)
        wrapper_status = get_atp_status(el)
        sub_elems = []
        for ie in inner_elements:
            if not self.is_standard_supported(ie):
                continue

            ie_name = ie.attrib.get('name', '')
            ie_type = ie.attrib.get('type', '').replace('AR:', '')
            ie_min, ie_max, ie_is_list = self._get_effective_cardinality(ie, el)
            ie_qname = get_qualified_name(ie)
            ie_status = self.get_effective_status(ie, ie_type if ie_type else None, parent_status=wrapper_status)

            if not ie_type:
                simple_ext = ie.xpath('./xsd:complexType/xsd:simpleContent/xsd:extension', namespaces=NS)
                if simple_ext:
                    base = simple_ext[0].attrib.get('base', '').replace('AR:', '')
                    dest_attr = simple_ext[0].xpath('./xsd:attribute[@name="DEST"]', namespaces=NS)
                    dest_type = dest_attr[0].attrib.get('type', '').replace('AR:', '') if dest_attr else ''
                    display_type = f"{base} -> {dest_type}" if dest_type else base
                    target_type = dest_type.replace('--SUBTYPES-ENUM', '') if dest_type else ''
                    sub_elems.append({
                        'name': ie_name,
                        'type': display_type,
                        'dest_type': dest_type,
                        'target_type': target_type,
                        'status': ie_status,
                        'is_complex': False,
                        'is_simple': False,
                        'is_ref': True,
                        'is_list': is_wrapper_list or ie_is_list,
                        'cardinality': f"{ie_min}..{ie_max}",
                        'sourceline': ie.sourceline,
                        'qualified_name': ie_qname
                    })
                    continue

            ie_ct = self.complex_types.get(ie_type)
            if ie_ct is not None and not self.is_standard_supported(ie_ct):
                continue

            ie_prim = self.detect_primitive_type(ie_type)
            sub_is_complex = False
            sub_is_simple = False
            sub_is_ref = False

            if ie_prim is not None:
                sub_is_simple = True
            elif ie_ct is not None:
                if ie_ct.findall('xsd:simpleContent', NS):
                    sub_is_ref = 'REF' in ie_type
                    sub_is_simple = not sub_is_ref
                else:
                    sub_is_complex = True
            elif ie_type in self.simple_types:
                sub_is_simple = True

            sub_elems.append({
                'name': ie_name,
                'type': ie_type,
                'status': ie_status,
                'is_complex': sub_is_complex,
                'is_simple': sub_is_simple,
                'is_ref': sub_is_ref,
                'is_list': is_wrapper_list or ie_is_list,
                'cardinality': f"{ie_min}..{ie_max}",
                'sourceline': ie.sourceline,
                'qualified_name': ie_qname
            })
        return sub_elems

    def extract_child_elements(self, container_elem: ET._Element) -> List[dict]:
        """Extract child element definitions from a group sequence/choice or element wrapper."""
        results = []
        elements = self._find_direct_child_elements(container_elem)
        for el in elements:
            if not self.is_standard_supported(el):
                continue

            el_name = el.attrib.get('name', '')
            el_type = el.attrib.get('type', '')
            min_occurs, max_occurs, is_list = self._get_effective_cardinality(el, container_elem)
            sourceline = el.sourceline
            qname = get_qualified_name(el)

            clean_type = el_type.replace('AR:', '') if el_type else ''
            el_status = self.get_effective_status(el, clean_type if clean_type else None)

            if clean_type:
                target_ct = self.complex_types.get(clean_type)
                if target_ct is not None and not self.is_standard_supported(target_ct):
                    continue

                prim = self.detect_primitive_type(clean_type)
                is_complex = False
                is_simple = False
                is_ref = False

                if prim is not None:
                    is_simple = True
                elif target_ct is not None:
                    if target_ct.findall('xsd:simpleContent', NS):
                        is_ref = 'REF' in clean_type
                        is_simple = not is_ref
                    else:
                        is_complex = True
                elif clean_type in self.simple_types:
                    is_simple = True

                results.append({
                    'name': el_name,
                    'type': clean_type,
                    'status': el_status,
                    'is_complex': is_complex,
                    'is_simple': is_simple,
                    'is_ref': is_ref,
                    'is_list': is_list,
                    'cardinality': f"{min_occurs}..{max_occurs}",
                    'sourceline': sourceline,
                    'qualified_name': qname,
                    'sub_elements': []
                })
            else:
                simple_ext = el.xpath('./xsd:complexType/xsd:simpleContent/xsd:extension', namespaces=NS)
                if simple_ext:
                    base = simple_ext[0].attrib.get('base', '').replace('AR:', '')
                    dest_attr = simple_ext[0].xpath('./xsd:attribute[@name="DEST"]', namespaces=NS)
                    dest_type = dest_attr[0].attrib.get('type', '').replace('AR:', '') if dest_attr else ''
                    results.append({
                        'name': el_name,
                        'type': f"{base} -> {dest_type}" if dest_type else base,
                        'status': el_status,
                        'is_complex': False,
                        'is_simple': False,
                        'is_ref': True,
                        'is_list': is_list,
                        'cardinality': f"{min_occurs}..{max_occurs}",
                        'sourceline': sourceline,
                        'qualified_name': qname,
                        'sub_elements': []
                    })
                else:
                    has_choice_unbounded = bool(el.xpath(
                        './/xsd:choice[@maxOccurs="unbounded"]', namespaces=NS))
                    has_seq_unbounded = bool(el.xpath(
                        './/xsd:sequence[@maxOccurs="unbounded"]', namespaces=NS))
                    is_wrapper_list = any([
                        is_list,
                        max_occurs == 'unbounded',
                        has_choice_unbounded,
                        has_seq_unbounded,
                    ])
                    sub_elems = self._extract_wrapper_inner_elements(el, is_wrapper_list)
                    results.append({
                        'name': el_name,
                        'type': f"(wrapper of {len(sub_elems)} type{'s' if len(sub_elems) > 1 else ''})",
                        'status': el_status,
                        'is_complex': False,
                        'is_simple': False,
                        'is_ref': False,
                        'is_list': is_wrapper_list,
                        'cardinality': f"{min_occurs}..{max_occurs}",
                        'sourceline': sourceline,
                        'qualified_name': qname,
                        'sub_elements': sub_elems
                    })
        return results

    def get_group_elements(self, group_name: str) -> List[dict]:
        """Extract elements defined in a group."""
        grp = self.groups.get(group_name)
        if grp is None or not self.is_standard_supported(grp):
            return []
        return self.extract_child_elements(grp)

    def list_children(self, complex_type_name: str, include_inherited: bool = True):
        """List all child elements for a given complex type organized by group with status indicators."""
        clean_name = complex_type_name.replace('AR:', '')
        ct = self.complex_types.get(clean_name)
        grp = self.groups.get(clean_name)

        ct_impl = self.get_implementation_info(clean_name)
        canonical_cls = self.get_canonical_class_name(clean_name)
        target_status = self.get_type_status(clean_name)

        print("=" * 80)
        print(f"AUTOSAR Complex Type Explorer: {clean_name}")
        print("=" * 80)
        print(f"ComplexType: {clean_name}" + (f" (line {ct.sourceline})" if ct is not None else " (not found)"))
        print(f"Group:       {clean_name}" + (f" (line {grp.sourceline})" if grp is not None else " (not found)"))
        if target_status:
            status_desc = f"{target_status.upper()}"
            if target_status in ('removed', 'obsolete'):
                status_desc += f" [DO NOT IMPLEMENT - {target_status} in schema]"
            elif target_status == 'draft':
                status_desc += " [DRAFT - evaluate necessity before implementing]"
            print(f"Status:      {status_desc}")
        print(f"Target Class:{canonical_cls} (from mmt.qualifiedName)")

        if ct_impl and not ct_impl.get('is_primitive'):
            print(f"Python:      {ct_impl['class_name']} ({ct_impl['file']}:{ct_impl['line']}) [Implemented]")
            if ct_impl.get('bases'):
                print(f"Bases:       {', '.join(ct_impl['bases'])}")
        else:
            print(f"Python:      No class mapping found in docstrings [TODO: class {canonical_cls}]")

        if grp is None and ct is None:
            print(f"\nError: Neither complexType nor group '{clean_name}' was found in schema.")
            return

        ct_groups = self.get_complex_type_groups(clean_name)
        if ct_groups and include_inherited:
            groups_to_check = list(reversed(ct_groups))
        else:
            groups_to_check = [clean_name]

        print("\nAvailable Child Elements:")
        print(f"{'Element Name':<38} {'Wiring Status':<20} {'Type / Details':<34} {'Card.':<6} {'Line':<6}")
        print("-" * 110)

        total_elements = 0
        for gname in groups_to_check:
            elements = self.get_group_elements(gname)
            if not elements:
                continue

            grp_impl = self.get_implementation_info(gname)
            grp_canonical = self.get_canonical_class_name(gname)
            grp_status = self.get_type_status(gname)
            if gname == clean_name:
                grp_label = f"--- Direct group: {gname}"
            else:
                grp_label = f"--- Inherited group: {gname}"

            if grp_impl and not grp_impl.get('is_primitive'):
                grp_label += f" ({grp_impl['class_name']} in {grp_impl['file']}:{grp_impl['line']})"
            elif grp_canonical:
                grp_label += f" (target: {grp_canonical})"
            if grp_status:
                grp_label += f" [{grp_status.upper()}]"
            grp_label += " ---"
            print(f"\n{grp_label}")

            for elem in elements:
                total_elements += 1
                ename = elem['name']
                etype = elem['type']
                estatus = elem.get('status')
                card = elem['cardinality']
                sline = elem['sourceline']

                status_str = ""
                owner_impl = grp_impl or ct_impl
                vp_names = ('VARIATION-POINT', 'VARIATION-POINT-PROXY', 'VARIATION-POINT-PROXYS')
                is_vp_ignored = self.is_ignored_type(etype) or ename in vp_names

                if estatus == 'removed':
                    status_str = "[REMOVED]"
                elif estatus == 'obsolete':
                    status_str = "[OBSOLETE]"
                elif is_vp_ignored:
                    status_str = "[Not supported]"
                elif owner_impl:
                    if ename in owner_impl.get('implemented_subelements', []):
                        status_str = "[Wired in init]" if not estatus else f"[Wired: {estatus}]"
                    elif ename in owner_impl.get('unsupported_subelements', []):
                        status_str = "[Not supported]"
                    elif ename in owner_impl.get('unimplemented_subelements', []):
                        status_str = "[Not in init]" if not estatus else f"[{estatus.capitalize()}]"
                    elif estatus:
                        status_str = f"[{estatus.capitalize()}]"
                elif estatus:
                    status_str = f"[{estatus.capitalize()}]"

                print(f"{ename:<38} {status_str:<20} {etype:<34} {card:<6} {sline:<6}")
                for sub in elem.get('sub_elements', []):
                    sub_name = f"  +-- {sub['name']}"
                    sub_type = sub['type']
                    sub_status_tag = sub.get('status')
                    sub_card = sub['cardinality']
                    sub_line = sub['sourceline']
                    sub_impl = self.get_implementation_info(sub.get('dest_type') or sub_type)

                    if sub_status_tag == 'removed':
                        sub_status = "[REMOVED]"
                    elif sub_status_tag == 'obsolete':
                        sub_status = "[OBSOLETE]"
                    elif self.is_ignored_type(sub_type) or sub['name'] in ('VARIATION-POINT', 'VARIATION-POINT-PROXY'):
                        sub_status = "[Not supported]"
                    elif sub.get('is_ref'):
                        if sub_impl:
                            sub_status = f"[{sub_impl['class_name']}]"
                        else:
                            target_t = sub.get('target_type') or sub_type
                            sub_canonical = self.get_canonical_class_name(target_t)
                            sub_status = f"[TODO Ref: {sub_canonical}]"
                    elif sub_impl:
                        if sub_status_tag == 'draft':
                            sub_status = f"[{sub_impl['class_name']}: Draft]"
                        else:
                            sub_status = f"[{sub_impl['class_name']}]"
                    else:
                        sub_canonical = self.get_canonical_class_name(sub_type)
                        if sub_status_tag == 'draft':
                            sub_status = f"[Draft: {sub_canonical}]"
                        elif sub_status_tag == 'candidate':
                            sub_status = f"[Cand.: {sub_canonical}]"
                        else:
                            sub_status = f"[TODO: {sub_canonical}]"
                    print(f"{sub_name:<38} {sub_status:<20} {sub_type:<34} {sub_card:<6} {sub_line:<6}")

        print(f"\nTotal child elements across {len(groups_to_check)} groups: {total_elements}")
        print("\nTo explore a sub-element dependency tree, run:")
        print(f"  python dev_utils/explore_subelement.py {clean_name}/<CHILD_NAME>\n")

    def traverse_subelement(self,
                            complex_type_name: str,
                            child_name: str,
                            include_inherited: bool = False,
                            max_depth: int = 20,
                            leaves_only: bool = False,
                            hide_primitives: bool = False):
        """Traverse child complex types starting from complex_type_name / child_name with status filtering."""
        clean_ct = complex_type_name.replace('AR:', '')
        clean_child = child_name.replace('AR:', '')

        ct = self.complex_types.get(clean_ct)
        grp = self.groups.get(clean_ct)
        ct_impl = self.get_implementation_info(clean_ct)
        canonical_cls = self.get_canonical_class_name(clean_ct)
        target_ct_status = self.get_type_status(clean_ct)

        print("=" * 80)
        print("AUTOSAR XSD Dependency Explorer")
        print("=" * 80)
        print(f"Target:        {clean_ct} / {clean_child}")
        print(f"ComplexType:   {clean_ct} (line {ct.sourceline if ct is not None else 'N/A'})")
        print(f"Group:         {clean_ct} (line {grp.sourceline if grp is not None else 'N/A'})")
        if target_ct_status:
            print(f"Parent Status: {target_ct_status.upper()}")
        print(f"Target Class:  {canonical_cls} (from mmt.qualifiedName)")
        if ct_impl and not ct_impl.get('is_primitive'):
            print(f"Python Class:  {ct_impl['class_name']} ({ct_impl['file']}:{ct_impl['line']}) [Implemented]")
            if ct_impl.get('bases'):
                print(f"Class Bases:   {', '.join(ct_impl['bases'])}")
        else:
            print(f"Python Class:  None found in docstrings [TODO: class {canonical_cls}]")
        print(f"Schema:        {self.xsd_path}")
        print("=" * 80)

        # Search for child_name across all group references declared by the complexType.
        ct_groups = self.get_complex_type_groups(clean_ct)
        if ct_groups:
            groups_to_search = list(reversed(ct_groups))
        else:
            groups_to_search = [clean_ct]

        target_element = None
        found_in_group = None
        for gname in groups_to_search:
            elems = self.get_group_elements(gname)
            for el in elems:
                if el['name'] == clean_child:
                    target_element = el
                    found_in_group = gname
                    break
            if target_element:
                break

        if not target_element:
            print(f"\nError: Element '{clean_child}' not found in '{clean_ct}' or its inherited groups.")
            print(f"Searched groups in sequence: {', '.join(groups_to_search)}")
            print("\nAvailable elements across searched groups:")
            for g in groups_to_search:
                g_elems = self.get_group_elements(g)
                if g_elems:
                    print(f"  In group '{g}':")
                    for el in g_elems:
                        print(f"    - {el['name']}")
            return

        # Report where the element was found
        grp_impl = self.get_implementation_info(found_in_group)
        sline = target_element['sourceline']
        el_status = target_element.get('status')
        if found_in_group == clean_ct:
            print(f"\nFound element '{clean_child}' (line {sline}) in direct group '{found_in_group}':")
        else:
            grp_desc = ""
            if grp_impl and not grp_impl.get('is_primitive'):
                grp_desc = f" (implemented by {grp_impl['class_name']} in {grp_impl['file']}:{grp_impl['line']})"
            print(f"\nFound element '{clean_child}' (line {sline}) in inherited base group '{found_in_group}'"
                  f"{grp_desc}:")

        print(f"  Type / Details: {target_element['type']}")
        if el_status:
            status_alert = f"  Status:         {el_status.upper()}"
            if el_status in ('removed', 'obsolete'):
                status_alert += f" [DO NOT IMPLEMENT - {el_status} in schema]"
            elif el_status == 'draft':
                status_alert += " [DRAFT - evaluate necessity before implementing]"
            print(status_alert)
        is_list_str = ' (unbounded list)' if target_element['is_list'] else ''
        print(f"  Cardinality:    {target_element['cardinality']}{is_list_str}")

        owner_impl = grp_impl or ct_impl
        if owner_impl:
            if clean_child in owner_impl.get('implemented_subelements', []):
                print(f"  Field Wiring:   Implemented in {owner_impl['class_name']}.__init__")
            elif clean_child in owner_impl.get('unimplemented_subelements', []):
                print(f"  Field Wiring:   Marked NOT YET IMPLEMENTED in {owner_impl['class_name']}.__init__")

        initial_types: List[Tuple[str, Optional[str]]] = []
        if target_element['is_complex']:
            if self.include_deprecated or not self.is_deprecated_status(el_status):
                initial_types.append((target_element['type'], el_status))
            else:
                print(f"\nTarget element is {el_status.upper()}. "
                      "Omitted from traversal by default (use --include-deprecated to force).")
        for sub in target_element.get('sub_elements', []):
            if sub['is_complex']:
                sub_st = sub.get('status')
                if self.include_deprecated or not self.is_deprecated_status(sub_st):
                    initial_types.append((sub['type'], sub_st))

        types_summary = (', '.join([t for t, _ in initial_types])
                         if initial_types else 'None (primitive/leaf/ref/deprecated)')
        print(f"  Referenced complex types: {types_summary}\n")

        ref_subs = [sub for sub in target_element.get('sub_elements', []) if sub.get('is_ref')]
        if target_element.get('is_ref'):
            ref_subs.append(target_element)

        if ref_subs:
            print("=" * 80)
            print("Target is a Reference Definition (not an owned child complex type):")
            print("=" * 80)
            for rsub in ref_subs:
                rname = rsub['name']
                rdest = rsub.get('dest_type') or rsub['type']
                rtarget = rsub.get('target_type') or rdest.replace('--SUBTYPES-ENUM', '').replace('AR:', '')
                r_canonical = self.get_canonical_class_name(rtarget)

                ref_impl = self.get_implementation_info(rdest) or self.get_implementation_info(rname)
                target_impl = self.get_implementation_info(rtarget)

                print(f"  Element Name:     {rname}")
                print(f"  Reference DEST:   {rdest}")
                print(f"  Target Type:      {rtarget} (class {r_canonical})")
                if ref_impl and ref_impl.get('kind') == 'reference':
                    ref_loc = f"({ref_impl['file']}:{ref_impl['line']})"
                    print(f"  Reference Class:  {ref_impl['class_name']} {ref_loc} [Implemented]")
                else:
                    print(f"  Reference Class:  [TODO: class {r_canonical}Ref in reference.py]")

                if target_impl and not target_impl.get('is_primitive'):
                    tgt_loc = f"({target_impl['file']}:{target_impl['line']})"
                    print(f"  Target Class:     {target_impl['class_name']} {tgt_loc} [Implemented]")
                else:
                    print(f"  Target Class:     [TODO: class {r_canonical} in element.py]")

                print("\n  To explore the referenced type's structure and dependencies, run:")
                print(f"    python dev_utils/explore_subelement.py {rtarget}\n")
            return

        if not initial_types:
            print("No child complex types to traverse.")
            return

        visited_nodes: Set[str] = set()
        dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        type_info: Dict[str, dict] = {}

        print("-" * 80)
        print("Dependency Tree Traversal:")
        print("-" * 80)

        def walk(type_name: str, depth: int, path: List[str]):
            impl_info = self.get_implementation_info(type_name)
            canonical = self.get_canonical_class_name(type_name)
            t_status = self.get_type_status(type_name)

            if impl_info:
                if impl_info.get('is_primitive'):
                    status_str = f"[Implicit: {impl_info['class_name']}]"
                else:
                    status_str = f"[{impl_info['class_name']} in {impl_info['file']}:{impl_info['line']}]"
            else:
                status_str = f"[TODO: {canonical}]"

            status_tag = ""
            if t_status == 'draft':
                status_tag = " [DRAFT]"
            elif t_status == 'candidate':
                status_tag = " [CANDIDATE]"
            elif t_status in ('removed', 'obsolete'):
                status_tag = f" [{t_status.upper()}]"

            ct_obj = self.complex_types.get(type_name)
            line_str = f"(xsd:{ct_obj.sourceline})" if ct_obj is not None else ""

            if type_name in path:
                indent = "  " * depth
                print(f"{indent}+-- [CYCLE] {type_name} {status_str}{status_tag}")
                return

            is_first_visit = type_name not in visited_nodes
            visited_nodes.add(type_name)

            indent = "  " * depth
            branch_sym = "+-- " if depth > 0 else ""
            if not is_first_visit:
                print(f"{indent}{branch_sym}{type_name} {line_str} {status_str}{status_tag} (see above)")
                return

            print(f"{indent}{branch_sym}{type_name} {line_str} {status_str}{status_tag}")

            if depth >= max_depth:
                print(f"{indent}  +-- [MAX DEPTH REACHED]")
                return

            # If it's a primitive type, no child elements exist to traverse
            if impl_info and impl_info.get('is_primitive'):
                return

            g_list = [type_name] if not include_inherited else self.get_complex_type_groups(type_name)
            if not g_list:
                g_list = [type_name]

            child_refs: List[Tuple[str, str, str, bool, Optional[str]]] = []

            for gname in g_list:
                elems = self.get_group_elements(gname)
                for el in elems:
                    ename = el['name']
                    est = el.get('status')
                    if el['is_complex']:
                        child_refs.append((ename, el['type'], 'complex', el['is_list'], est))
                    elif el['is_ref']:
                        child_refs.append((ename, el['type'], 'ref', el['is_list'], est))
                    elif el['is_simple']:
                        child_refs.append((ename, el['type'], 'simple', el['is_list'], est))
                    for sub in el.get('sub_elements', []):
                        sub_st = sub.get('status')
                        if sub['is_complex']:
                            child_refs.append(
                                (f"{ename}/{sub['name']}", sub['type'], 'complex', sub['is_list'], sub_st)
                            )
                        elif sub['is_simple']:
                            child_refs.append((f"{ename}/{sub['name']}", sub['type'], 'simple', sub['is_list'], sub_st))

            type_info[type_name] = {
                'sourceline': ct_obj.sourceline if ct_obj is not None else None,
                'implemented': impl_info is not None,
                'impl_info': impl_info,
                'status': t_status,
                'children': child_refs
            }

            for ename, ctype, kind, _, c_status in child_refs:
                effective_c_status = c_status or self.get_type_status(ctype)
                c_status_tag = ""
                if effective_c_status == 'draft':
                    c_status_tag = " [DRAFT]"
                elif effective_c_status == 'candidate':
                    c_status_tag = " [CANDIDATE]"

                if kind == 'complex':
                    if not self.include_deprecated and self.is_deprecated_status(effective_c_status):
                        child_indent = "  " * (depth + 1)
                        cat = self.get_ignored_category(ctype)
                        print(f"{child_indent}+-- [NOT SUPPORTED: {cat}] {ename} ({ctype})")
                    elif not self.include_ignored and self.is_ignored_type(ctype):
                        child_indent = "  " * (depth + 1)
                        cat = self.get_ignored_category(ctype)
                        print(f"{child_indent}+-- [NOT SUPPORTED: {cat}] {ename} ({ctype})")
                    else:
                        dependency_graph[type_name].add(ctype)
                        walk(ctype, depth + 1, path + [type_name])
                elif kind == 'ref':
                    child_indent = "  " * (depth + 1)
                    if not self.include_deprecated and self.is_deprecated_status(effective_c_status):
                        cat = effective_c_status.capitalize() if effective_c_status else "Deprecated"
                        print(f"{child_indent}+-- [NOT SUPPORTED: {cat} REF] {ename} -> {ctype}")
                    else:
                        print(f"{child_indent}+-- [REF] {ename} -> {ctype}{c_status_tag}")
                elif kind == 'simple':
                    prim = self.detect_primitive_type(ctype)
                    prim_label = f"({prim})" if prim else ""
                    if not hide_primitives:
                        child_indent = "  " * (depth + 1)
                        if not self.include_deprecated and self.is_deprecated_status(effective_c_status):
                            cat = effective_c_status.capitalize() if effective_c_status else "Deprecated"
                            print(f"{child_indent}+-- [NOT SUPPORTED: {cat}] {ename}: {ctype} {prim_label}")
                        else:
                            print(f"{child_indent}+-- [PRIMITIVE] {ename}: {ctype} {prim_label}{c_status_tag}")

        for init_t, _ in initial_types:
            walk(init_t, 0, [])

        print("\n" + "=" * 80)
        print("Bottom-Up Implementation Order (Leaves First):")
        print("=" * 80)
        print("Implement classes in this order so that all dependencies are ready beforehand:\n")

        topo_order = []
        visited_topo = set()

        def topo_dfs(node: str, visiting: Set[str]):
            if node in visiting:
                return
            if node in visited_topo:
                return
            visiting.add(node)
            for dep in sorted(dependency_graph.get(node, set())):
                topo_dfs(dep, visiting)
            visiting.remove(node)
            visited_topo.add(node)
            topo_order.append(node)

        for init_t, _ in initial_types:
            topo_dfs(init_t, set())

        implemented_count = 0
        pending_count = 0
        primitive_count = 0
        draft_pending_count = 0
        candidate_pending_count = 0
        deprecated_pending_count = 0
        leaf_unimplemented = []

        item_idx = 0
        for tname in topo_order:
            impl_info = self.get_implementation_info(tname)
            canonical = self.get_canonical_class_name(tname)
            t_status = self.get_type_status(tname)
            is_imp = impl_info is not None
            is_prim = impl_info.get('is_primitive', False) if impl_info else False

            status_tag = ""
            if t_status == 'draft':
                status_tag = " [DRAFT]"
            elif t_status == 'candidate':
                status_tag = " [CANDIDATE]"
            elif t_status in ('removed', 'obsolete'):
                status_tag = f" [{t_status.upper()}]"

            if is_prim:
                primitive_count += 1
                status = f"[✓ Implicit: {impl_info['class_name']}]"
            elif is_imp:
                implemented_count += 1
                status = f"[✓ {impl_info['class_name']}]"
            else:
                pending_count += 1
                if t_status == 'draft':
                    draft_pending_count += 1
                elif t_status == 'candidate':
                    candidate_pending_count += 1
                elif t_status in ('removed', 'obsolete'):
                    deprecated_pending_count += 1
                status = f"[✗ TODO: {canonical}]"

            deps = dependency_graph.get(tname, set())
            is_leaf = len(deps) == 0
            if is_leaf and not is_imp and not is_prim:
                leaf_unimplemented.append((tname, canonical, t_status))

            if leaves_only and not is_leaf:
                continue

            if hide_primitives and is_prim:
                continue

            item_idx += 1
            dep_names = [self.get_canonical_class_name(d) for d in sorted(deps)]
            dep_str = f"(depends on: {', '.join(dep_names)})" if dep_names else "(LEAF - no complex dependencies)"
            ct_obj = self.complex_types.get(tname)
            sline = f"xsd:{ct_obj.sourceline}" if ct_obj is not None else ""
            status_combined = f"{status}{status_tag}"
            print(f" {item_idx:2d}. {status_combined:<44} {tname:<42} {sline:<10} {dep_str}")

        print("\n" + "-" * 80)
        print("Summary:")
        print(f"  Total Complex Types in Graph: {len(topo_order)}")
        print(f"  Already Implemented Classes:  {implemented_count}")
        if primitive_count > 0:
            print(f"  Implicit Primitives (str/int):{primitive_count}")
        print(f"  Pending Classes to Implement: {pending_count}")
        valid_pending = pending_count - draft_pending_count - candidate_pending_count - deprecated_pending_count
        if pending_count > 0:
            print(f"    - Standard (Valid) Classes: {valid_pending}")
            if draft_pending_count > 0:
                print(f"    - Draft Classes (Evaluate): {draft_pending_count}")
            if candidate_pending_count > 0:
                print(f"    - Candidate (AP) Classes:   {candidate_pending_count}")
            if deprecated_pending_count > 0:
                print(f"    - Deprecated (DO NOT IMPL): {deprecated_pending_count}")
        if leaf_unimplemented:
            print(f"  Unimplemented Leaf Classes:   {len(leaf_unimplemented)} (start with these!)")
            for utype, ucls, ust in leaf_unimplemented:
                uct = self.complex_types.get(utype)
                usline = f"xsd:{uct.sourceline}" if uct is not None else ""
                ust_tag = f" [{ust.upper()}]" if ust else ""
                print(f"    - class {ucls:<36} ({utype}, {usline}){ust_tag}")
        print("-" * 80 + "\n")


def main():
    """Parse CLI arguments and run the schema inspector."""
    parser = argparse.ArgumentParser(
        description="Inspect AUTOSAR XML Schema (XSD) and traverse complex type dependencies."
    )
    parser.add_argument(
        "target",
        help="Target complex type and child, e.g. 'SWC-INTERNAL-BEHAVIOR/AR-TYPED-PER-INSTANCE-MEMORYS' "
             "or 'VARIABLE-DATA-PROTOTYPE/INIT-VALUE' or 'VARIABLE-DATA-PROTOTYPE'"
    )
    parser.add_argument(
        "--schema", "-s",
        default="doc/schema/AUTOSAR_00051.xsd",
        help="Path to AUTOSAR XSD schema file (default: doc/schema/AUTOSAR_00051.xsd)"
    )
    parser.add_argument(
        "--include-inherited", "-i",
        action="store_true",
        help="Also traverse elements inherited from base class groups in the complexType sequence"
    )
    parser.add_argument(
        "--max-depth", "-d",
        type=int,
        default=20,
        help="Maximum recursion depth for traversal (default: 20)"
    )
    parser.add_argument(
        "--leaves-only", "-l",
        action="store_true",
        help="Only display leaf types (types with no complex dependencies) in the bottom-up order"
    )
    parser.add_argument(
        "--hide-primitives", "-p",
        action="store_true",
        help="Hide implicit primitive types (str, int, float, bool) from the implementation order list"
    )
    parser.add_argument(
        "--all-standards", "-a",
        action="store_true",
        help="Include Adaptive Platform (AP) only elements in addition to Classic Platform (CP)"
    )
    parser.add_argument(
        "--include-ignored",
        action="store_true",
        help="Also traverse and include VariantHandling and Blueprint types instead of marking them [NOT SUPPORTED]"
    )
    parser.add_argument(
        "--include-deprecated",
        action="store_true",
        help="Also traverse and include deprecated (removed/obsolete) types instead of marking them [NOT SUPPORTED]"
    )
    parser.add_argument(
        "--refresh", "-r",
        action="store_true",
        help="Force re-parsing element.py and enumeration.py docstrings and update the cache"
    )

    args = parser.parse_args()

    xsd_path = args.schema
    if not os.path.isabs(xsd_path):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        candidate = os.path.join(repo_root, xsd_path)
        if os.path.exists(candidate):
            xsd_path = candidate

    inspector = SchemaInspector(
        xsd_path,
        refresh=args.refresh,
        classic_only=not args.all_standards,
        include_ignored=args.include_ignored,
        include_deprecated=args.include_deprecated
    )

    target = args.target.strip()
    if '/' in target:
        ct_name, child_name = target.split('/', 1)
        inspector.traverse_subelement(
            ct_name.strip(),
            child_name.strip(),
            include_inherited=args.include_inherited,
            max_depth=args.max_depth,
            leaves_only=args.leaves_only,
            hide_primitives=args.hide_primitives
        )
    elif ':' in target and not target.startswith('AR:'):
        ct_name, child_name = target.split(':', 1)
        inspector.traverse_subelement(
            ct_name.strip(),
            child_name.strip(),
            include_inherited=args.include_inherited,
            max_depth=args.max_depth,
            leaves_only=args.leaves_only,
            hide_primitives=args.hide_primitives
        )
    else:
        inspector.list_children(target, include_inherited=not args.include_inherited)


if __name__ == "__main__":
    main()
