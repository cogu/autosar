#!/usr/bin/env python3
"""Scan AUTOSAR Python codebase and cache implemented XML complexTypes, groups, and enums.

This script parses class docstrings and code annotations in `src/autosar/xml/` using AST,
mapping each Python class to its corresponding AUTOSAR XML Schema (XSD) complexType,
group, or enumeration. The results are saved to `dev_utils/.implementation_cache.json`.

Usage:
    python dev_utils/refresh_implementation.py
"""

# pylint: disable=duplicate-code
import ast
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure UTF-8 output encoding across platforms
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (ValueError, OSError, AttributeError):
        pass


def get_default_cache_path() -> str:
    """Return the absolute path to .implementation_cache.json in dev_utils."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, ".implementation_cache.json")


def _extract_subelements(class_lines: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """Extract implemented, unsupported, and unimplemented subelements from class lines."""
    implemented: List[str] = []
    unsupported: List[str] = []
    unimplemented: List[str] = []

    for line in class_lines:
        m_unsupp = re.search(
            r'#\s*\.([A-Z0-9\-]+)\s*(?:\()?not\s+supported(?:\))?',
            line,
            re.IGNORECASE
        )
        m_unimpl = re.search(
            r'#\s*\.([A-Z0-9\-]+)\s*(?:\()?(?:not yet implemented|not yet supported|not fully implemented)(?:\))?',
            line,
            re.IGNORECASE
        )
        if m_unsupp:
            tag = m_unsupp.group(1)
            if tag not in unsupported:
                unsupported.append(tag)
        elif m_unimpl:
            tag = m_unimpl.group(1)
            if tag not in unimplemented:
                unimplemented.append(tag)
        else:
            m_impl = re.search(r'#\s*\.([A-Z0-9\-]+)\s*$', line)
            if m_impl:
                tag = m_impl.group(1)
                known = implemented + unsupported + unimplemented
                if tag not in known:
                    implemented.append(tag)
            else:
                m_inline = re.search(r'#\s*\.([A-Z0-9\-]+)', line)
                if m_inline:
                    tag = m_inline.group(1)
                    line_low = line.lower()
                    is_unsupported = any(p in line_low for p in [
                        'not yet implemented', 'not yet supported',
                        'not supported', 'not fully implemented'
                    ])
                    known = implemented + unsupported + unimplemented
                    if not is_unsupported and tag not in known:
                        implemented.append(tag)

    return implemented, unsupported, unimplemented


def parse_element_file(filepath: str) -> Dict[str, Any]:
    """Parse src/autosar/xml/element.py and extract class definitions and docstring mappings."""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    lines = code.splitlines()

    classes: Dict[str, Any] = {}
    complex_types: Dict[str, str] = {}  # XSD complexType name -> Python class name
    groups: Dict[str, str] = {}         # XSD group name -> Python class name
    tag_variants: Dict[str, str] = {}   # XML tag variant -> Python class name

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        doc = ast.get_docstring(node) or ""
        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]

        # 1. Complex Type patterns in docstrings
        ct_matches = re.findall(
            r'(?:Complex\s+[Tt]ypes?|complex\s+[Tt]ypes?)(?:\:)?\s+AR:([A-Z0-9\-]+)',
            doc
        )

        # Matches: "Merge of Complex types AR:A, AR:B and AR:C"
        merge_matches = re.findall(r'Merge of [Cc]omplex types\s+([^.\n]+)', doc)
        if merge_matches:
            for m in merge_matches:
                found_cts = re.findall(r'(?:AR:)?([A-Z0-9\-]+)', m)
                for fct in found_cts:
                    if fct not in ('AND', 'OR', 'OF') and fct not in ct_matches:
                        ct_matches.append(fct)

        # Matches: standalone "AR:XYZ" on first line of docstring
        standalone_ar = re.match(r'^\s*AR:([A-Z0-9\-]+)', doc)
        if standalone_ar:
            tag = standalone_ar.group(1)
            if tag not in ct_matches:
                ct_matches.append(tag)

        # 2. Group patterns in docstrings
        grp_matches = re.findall(r'Group\s+(?:AR:)?([A-Z0-9\-]+)', doc, re.IGNORECASE)

        # 3. Tag variants: 'VAR1' | 'VAR2'
        variants = []
        tv_match = re.search(r'Tag [Vv]ariants:\s*([^\n]+)', doc)
        if tv_match:
            variants = [t.strip("'\" ") for t in tv_match.group(1).split('|')]

        # 4. Constructor sub-element comments inspection
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else start_line + 50
        class_lines = lines[start_line - 1:end_line]

        implemented_subelements, unsupported_subelements, unimplemented_subelements = _extract_subelements(class_lines)

        class_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": bases,
            "complex_types": ct_matches,
            "groups": grp_matches,
            "tag_variants": variants,
            "implemented_subelements": implemented_subelements,
            "unsupported_subelements": unsupported_subelements,
            "unimplemented_subelements": unimplemented_subelements,
            "docstring": doc[:200]
        }

        classes[node.name] = class_info

        for ct in ct_matches:
            complex_types[ct] = node.name
        for grp in grp_matches:
            groups[grp] = node.name
        for var in variants:
            tag_variants[var] = node.name

    return {
        "classes": classes,
        "complex_types": complex_types,
        "groups": groups,
        "tag_variants": tag_variants
    }


def parse_enumeration_file(filepath: str) -> Dict[str, Any]:
    """Parse src/autosar/xml/enumeration.py and extract enumeration definitions and mappings."""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    enums: Dict[str, Any] = {}
    type_to_enum: Dict[str, str] = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        doc = ast.get_docstring(node) or ""
        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]

        # Match AR:XYZ, AR:XYZ--SIMPLE, XYZ-ENUM, etc.
        ar_matches = re.findall(r'AR:([A-Z0-9\-]+)(?:--SIMPLE)?', doc)
        enum_matches = re.findall(r'([A-Z0-9\-]+-ENUM)(?:--SIMPLE)?', doc)

        matched_types = list(set(ar_matches + enum_matches))

        enum_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": bases,
            "types": matched_types,
            "docstring": doc[:150]
        }

        enums[node.name] = enum_info

        for t in matched_types:
            type_to_enum[t] = node.name
            # Also store without -ENUM or --SIMPLE
            clean_t = t.replace("-ENUM", "").replace("--SIMPLE", "")
            if clean_t not in type_to_enum:
                type_to_enum[clean_t] = node.name

    return {
        "enums": enums,
        "type_to_enum": type_to_enum
    }


def refresh_cache(repo_root: Optional[str] = None, output_path: Optional[str] = None) -> dict:
    """Scan the autosar Python source code and refresh the JSON cache."""
    if repo_root is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, ".."))

    element_py = os.path.join(repo_root, "src", "autosar", "xml", "element.py")
    enum_py = os.path.join(repo_root, "src", "autosar", "xml", "enumeration.py")

    if not os.path.exists(element_py):
        raise FileNotFoundError(f"Cannot find element.py at {element_py}")

    print(f"Scanning element.py ({element_py})...")
    elem_data = parse_element_file(element_py)

    enum_data: Dict[str, Any] = {"enums": {}, "type_to_enum": {}}
    if os.path.exists(enum_py):
        print(f"Scanning enumeration.py ({enum_py})...")
        enum_data = parse_enumeration_file(enum_py)

    cache_data = {
        "classes": elem_data["classes"],
        "complex_types": elem_data["complex_types"],
        "groups": elem_data["groups"],
        "tag_variants": elem_data["tag_variants"],
        "enums": enum_data["enums"],
        "type_to_enum": enum_data["type_to_enum"]
    }

    if output_path is None:
        output_path = get_default_cache_path()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

    print(f"Cache saved to: {output_path}")
    print("\nSummary of Indexed Implementations:")
    print(f"  Classes in element.py:      {len(elem_data['classes'])}")
    print(f"  Mapped XML Complex Types:   {len(elem_data['complex_types'])}")
    print(f"  Mapped XML Groups:          {len(elem_data['groups'])}")
    print(f"  Enumerations indexed:       {len(enum_data['enums'])}")
    print(f"  Mapped XML Enum Types:      {len(enum_data['type_to_enum'])}\n")

    return cache_data


def load_cached_implementations(cache_path: Optional[str] = None) -> dict:
    """Load cached implementation dictionary. If missing, automatically build it."""
    if cache_path is None:
        cache_path = get_default_cache_path()

    if not os.path.exists(cache_path):
        print(f"Cache file '{cache_path}' not found. Generating now...")
        return refresh_cache(output_path=cache_path)

    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """Execute cache refresh CLI."""
    print("=" * 80)
    print("AUTOSAR Implementation Scanner & Cache Builder")
    print("=" * 80)
    refresh_cache()


if __name__ == "__main__":
    main()
