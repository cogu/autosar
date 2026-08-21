#!/usr/bin/env python3
"""Scan AUTOSAR Python codebase and cache implemented XML complexTypes, groups, enums, and tag variants.

This script parses class docstrings and code annotations in `src/autosar/xml/` using AST,
mapping each Python class to its corresponding AUTOSAR XML Schema (XSD) complexType,
group, enumeration, and XML tag variants. The results are saved to `dev_utils/.implementation_cache.json`.

Usage:
    python dev_utils/refresh_implementation.py
"""

# pylint: disable=duplicate-code
import ast
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure UTF-8 output encoding across platforms
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (ValueError, OSError, AttributeError):
        pass

DEFAULT_RELEASE_VERSION = "v0.5.6"


def get_default_cache_path() -> str:
    """Return the absolute path to .implementation_cache.json in dev_utils."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, ".implementation_cache.json")


def _extract_category(raw_comment: str) -> str:
    """Extract and format category name from a grouping comment line (e.g. '# --- Port interface elements').

    Stops at the word 'element' or 'elements' (ignoring any subsequent text) and CamelCases preceding words.
    """
    text = raw_comment.lstrip('# -').strip()
    parts = re.split(r'\belements?\b', text, flags=re.IGNORECASE)
    before_elements = parts[0].strip()
    words = re.findall(r'[A-Za-z0-9]+', before_elements)
    category = ''.join(w.capitalize() for w in words)
    return category or "CommonStructure"


def _extract_tag_variants(doc: str) -> List[str]:
    """Extract XML tag variant strings from class docstring supporting multi-line definitions."""
    m = re.search(r"Tag [Vv]ariants?:\s*(.+)", doc, re.DOTALL)
    if not m:
        return []
    rest = m.group(1)
    lines = rest.splitlines()
    variant_lines: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            break
        # Tag variant lines contain quotes or '|'
        if "'" in stripped or '"' in stripped or "|" in stripped:
            variant_lines.append(stripped)
        else:
            break

    combined = " ".join(variant_lines)
    # Extract all quoted strings
    quoted = re.findall(r"['\"]([A-Z0-9\-_]+)['\"]", combined)
    if quoted:
        return quoted
    # Fallback to split by |
    parts = [p.strip(" '\"\t\r\n") for p in combined.split("|")]
    return [p for p in parts if p]


def _get_git_class_versions(repo_root: str) -> Dict[str, str]:
    """Resolve earliest git release tag containing each class in element.py."""
    git_tags = ['v0.5.0', 'v0.5.1', 'v0.5.2', 'v0.5.3', 'v0.5.4', 'v0.5.5', 'v0.5.6']
    tag_classes: Dict[str, Set[str]] = {}

    try:
        raw_tags = subprocess.check_output(
            ['git', 'tag', '-l', 'v0.5.*'],
            cwd=repo_root,
            encoding='utf-8',
            errors='ignore'
        ).splitlines()
        if raw_tags:
            # Sort version tags if needed
            git_tags = [t.strip() for t in raw_tags if t.strip()]
    except Exception:
        pass

    for t in git_tags:
        try:
            content = subprocess.check_output(
                ['git', 'show', f'{t}:src/autosar/xml/element.py'],
                cwd=repo_root,
                encoding='utf-8',
                errors='ignore'
            )
            classes = set(re.findall(r'^class\s+([A-Za-z0-9_]+)', content, flags=re.MULTILINE))
            tag_classes[t] = classes
        except Exception:
            continue

    return tag_classes, git_tags


def _is_package_element(
    class_name: str,
    classes_bases: Dict[str, List[str]],
    visited: Optional[Set[str]] = None
) -> bool:
    """Determine recursively if a class inherits from ARElement or CollectableElement."""
    if visited is None:
        visited = set()
    if class_name in visited:
        return False
    visited.add(class_name)

    if class_name in ('ARElement', 'CollectableElement'):
        return True

    for base in classes_bases.get(class_name, []):
        if _is_package_element(base, classes_bases, visited):
            return True
    return False


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
                        'not supported', 'not fully implemented',
                        'removed', 'obsolete'
                    ])
                    known = implemented + unsupported + unimplemented
                    if not is_unsupported and tag not in known:
                        implemented.append(tag)
                    elif is_unsupported and tag not in known:
                        unsupported.append(tag)

    return implemented, unsupported, unimplemented


def parse_element_file(filepath: str, repo_root: Optional[str] = None) -> Dict[str, Any]:
    """Parse src/autosar/xml/element.py and extract class definitions and docstring mappings."""
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(filepath), "..", "..", ".."))

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    tree = ast.parse(code)
    lines = code.splitlines()

    # Map line number to active section category
    sec_by_line: Dict[int, str] = {}
    curr_category = "CommonStructure"
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('# ---'):
            curr_category = _extract_category(stripped)
        sec_by_line[i] = curr_category

    tag_classes, git_tags = _get_git_class_versions(repo_root)

    # Collect class inheritance map
    classes_bases: Dict[str, List[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes_bases[node.name] = [b.id for b in node.bases if isinstance(b, ast.Name)]

    classes: Dict[str, Any] = {}
    complex_types: Dict[str, str] = {}  # XSD complexType name -> Python class name
    groups: Dict[str, str] = {}         # XSD group name -> Python class name
    tag_variants: Dict[str, str] = {}   # XML tag variant -> Python class name

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        doc = ast.get_docstring(node) or ""
        bases = classes_bases.get(node.name, [])

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

        # 3. Tag variants
        variants = _extract_tag_variants(doc)

        # 4. Constructor sub-element comments inspection
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else start_line + 50
        class_lines = lines[start_line - 1:end_line]

        implemented_subelements, unsupported_subelements, unimplemented_subelements = _extract_subelements(class_lines)

        # 5. Category & Package Element status & Version
        category = sec_by_line.get(node.lineno, "CommonStructure")
        package_elem = _is_package_element(node.name, classes_bases)

        since_ver = None
        for t in git_tags:
            if node.name in tag_classes.get(t, set()):
                since_ver = t
                break
        if since_ver is None:
            since_ver = git_tags[-1] if git_tags else DEFAULT_RELEASE_VERSION

        class_info = {
            "name": node.name,
            "line": node.lineno,
            "bases": bases,
            "complex_types": ct_matches,
            "groups": grp_matches,
            "tag_variants": variants,
            "category": category,
            "package_element": package_elem,
            "since_version": since_ver,
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
    elem_data = parse_element_file(element_py, repo_root=repo_root)

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
    print(f"  Mapped Tag Variants:        {len(elem_data['tag_variants'])}")
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
