#!/usr/bin/env python3
"""Diagnostic script to inspect XML tag variants and git release introduction history.

Usage:
    python dev_utils/wiki/inspect_tags.py
"""

from __future__ import annotations
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys

# Ensure src is on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import autosar.xml.element as element  # noqa: E402 # pylint: disable=wrong-import-position


def main() -> None:
    """Run tag diagnostic and release history analysis."""
    script_dir = Path(__file__).parent.resolve()
    dev_utils_dir = script_dir.parent
    cache_path = dev_utils_dir / ".implementation_cache.json"
    wiki_path = script_dir / "xml_index.md"

    print("=" * 80)
    print("AUTOSAR XML Tag Index Diagnostic & Git History Inspector")
    print("=" * 80)

    # 1. Read dev_utils/wiki/xml_index.md if present
    wiki_rows = []
    if wiki_path.exists():
        with open(wiki_path, "r", encoding="utf-8") as f:
            wiki_content = f.read()

        for line in wiki_content.splitlines():
            if (line.startswith("|")
                    and not line.startswith("|---")
                    and not line.startswith("| XML Tag Name")
                    and not line.startswith("| ---")):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 4:
                    wiki_rows.append({
                        "tag": parts[0],
                        "version": parts[1],
                        "category": parts[2],
                        "class": parts[3]
                    })
        print(f"Loaded {len(wiki_rows)} tag rows from {wiki_path.name}.")

    # 2. Get git release tags
    git_tags = ["v0.5.0", "v0.5.1", "v0.5.2", "v0.5.3", "v0.5.4", "v0.5.5", "v0.5.6"]
    try:
        raw_tags = subprocess.check_output(
            ["git", "tag", "-l", "v0.5.*"],
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="ignore"
        ).splitlines()
        if raw_tags:
            git_tags = [t.strip() for t in raw_tags if t.strip()]
    except Exception:
        pass

    tag_classes = {}
    for t in git_tags:
        try:
            content = subprocess.check_output(
                ["git", "show", f"{t}:src/autosar/xml/element.py"],
                cwd=str(REPO_ROOT),
                encoding="utf-8",
                errors="ignore"
            )
            classes = set(re.findall(r"^class\s+([A-Za-z0-9_]+)", content, flags=re.MULTILINE))
            tag_classes[t] = classes
        except Exception:
            continue

    # 3. Read cache or inspect element.py
    classes_dict = {}
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
            classes_dict = cache.get("classes", {})

    all_element_classes = [
        cls for name, cls in inspect.getmembers(element, inspect.isclass)
        if cls.__module__ == "autosar.xml.element"
    ]

    total_with_tags = 0
    total_tag_variants = 0
    package_elements_count = 0
    child_elements_count = 0
    classes_without_tags = []

    for cls in all_element_classes:
        cname = cls.__name__
        cinfo = classes_dict.get(cname, {})
        tags = cinfo.get("tag_variants", [])
        is_pkg = cinfo.get("package_element", False)

        if not tags:
            # Check docstring directly
            doc = inspect.getdoc(cls) or ""
            m = re.search(r"Tag [Vv]ariants?:\s*(.+)", doc)
            if not m:
                classes_without_tags.append(cname)
                continue

        total_with_tags += 1
        total_tag_variants += len(tags)
        if is_pkg:
            package_elements_count += len(tags)
        else:
            child_elements_count += len(tags)

    print(f"\nTotal Python classes in autosar.xml.element: {len(all_element_classes)}")
    print(f"Classes implementing XML tags:              {total_with_tags}")
    print(f"Total XML Tag variants mapped:              {total_tag_variants}")
    print(f"  - Package Element tags:                   {package_elements_count}")
    print(f"  - Child Element tags:                     {child_elements_count}")
    print(f"Classes without tag variants (base/helper): {len(classes_without_tags)}")
    print(f"\nGit release versions scanned: {', '.join(git_tags)}\n")


if __name__ == "__main__":
    main()
