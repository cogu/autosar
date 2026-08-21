#!/usr/bin/env python3
"""Generates the GitHub Wiki XML Tag Index page directly from .implementation_cache.json.

Usage:
    python dev_utils/wiki/generate_wiki_page.py
    python dev_utils/wiki/generate_wiki_page.py --refresh
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List
import jinja2
from tabulate import tabulate

WIKI_COLUMNS = ["XML Tag Name", "Implemented", "Element Category", "Python Class Name"]


def load_cache(cache_path: Path, refresh: bool = False) -> Dict[str, Any]:
    """Load JSON implementation cache, optionally forcing a refresh."""
    if refresh or not cache_path.exists():
        # Import dynamically from parent directory
        import sys
        dev_utils_dir = str(cache_path.parent)
        if dev_utils_dir not in sys.path:
            sys.path.insert(0, dev_utils_dir)
        import refresh_implementation  # type: ignore # pylint: disable=import-error
        print(f"Refreshing cache: {cache_path}...")
        return refresh_implementation.refresh_cache(output_path=str(cache_path))

    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_table_rows(cache_data: Dict[str, Any]) -> tuple[List[List[str]], List[List[str]]]:
    """Extract and partition tag rows into Package Elements and Child Elements from cache."""
    classes = cache_data.get("classes", {})
    pkg_rows: List[List[str]] = []
    child_rows: List[List[str]] = []

    for class_name, class_info in classes.items():
        variants: List[str] = class_info.get("tag_variants", [])
        if not variants:
            continue

        category = class_info.get("category", "CommonStructure")
        version = class_info.get("since_version", "v0.5.6")
        is_pkg = class_info.get("package_element", False)

        for tag in variants:
            row = [tag, version, category, class_name]
            if is_pkg:
                pkg_rows.append(row)
            else:
                child_rows.append(row)

    # Sort alphabetically by XML Tag Name, then Python Class Name
    pkg_rows.sort(key=lambda r: (r[0], r[3]))
    child_rows.sort(key=lambda r: (r[0], r[3]))

    return pkg_rows, child_rows


def generate_markdown(template_path: Path, pkg_rows: List[List[str]], child_rows: List[List[str]]) -> str:
    """Render the Jinja2 template with tabulated Markdown tables."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template file '{template_path}' not found.")

    pkg_table = tabulate(pkg_rows, headers=WIKI_COLUMNS, tablefmt="github")
    child_table = tabulate(child_rows, headers=WIKI_COLUMNS, tablefmt="github")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template(template_path.name)
    rendered = template.render(
        package_elements_table=pkg_table,
        child_elements_table=child_table
    )
    return rendered


def main() -> None:
    """CLI entry point for wiki generator."""
    script_dir = Path(__file__).parent.resolve()
    dev_utils_dir = script_dir.parent

    default_cache = dev_utils_dir / ".implementation_cache.json"
    default_template = script_dir / "templates" / "xml_index.md.jinja2"
    default_output = script_dir / "xml_index.md"

    parser = argparse.ArgumentParser(
        description="Generate GitHub Wiki XML Index Markdown from .implementation_cache.json"
    )
    parser.add_argument("--cache", type=Path, default=default_cache, help="Path to .implementation_cache.json")
    parser.add_argument("--template", type=Path, default=default_template, help="Path to Jinja2 template")
    parser.add_argument("--output", type=Path, default=default_output, help="Path to output markdown file")
    parser.add_argument("--refresh", action="store_true", help="Force refresh cache before generating markdown")

    args = parser.parse_args()

    print(f"Loading implementation cache from: {args.cache}...")
    cache_data = load_cache(args.cache, refresh=args.refresh)

    pkg_rows, child_rows = extract_table_rows(cache_data)
    total_rows = len(pkg_rows) + len(child_rows)
    print(f"Extracted {len(pkg_rows)} Package Elements and {len(child_rows)} Child Elements (Total: {total_rows}).")

    print(f"Rendering Jinja2 template: {args.template}...")
    markdown_content = generate_markdown(args.template, pkg_rows, child_rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown_content, encoding="utf-8")
    print(f"Successfully generated: {args.output}")


if __name__ == "__main__":
    main()
