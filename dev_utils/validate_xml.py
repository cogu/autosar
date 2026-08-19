#!/usr/bin/env python3
"""AUTOSAR XML Schema Validator.

Validates AUTOSAR XML (*.arxml, *.xml) against schemas in doc/schema.
"""

# pylint: disable=duplicate-code
import argparse
import os
import sys
from typing import Dict, List, Optional, Set, Tuple
import lxml.etree as ET

SCHEMA_RELEASES = {
    '00048': {'release': 'R19-11', 'file': 'AUTOSAR_00048.xsd'},
    '00049': {'release': 'R20-11', 'file': 'AUTOSAR_00049.xsd'},
    '00050': {'release': 'R21-11', 'file': 'AUTOSAR_00050.xsd'},
    '00051': {'release': 'R22-11', 'file': 'AUTOSAR_00051.xsd'},
}

# Directories requiring specific schema versions (newer features)
DIRECTORY_SCHEMA_EXCEPTIONS = {
    # SenderComponent uses <CAN-ENTERS> introduced in AUTOSAR R21-11 (00050)
    'examples/xml/component': {
        'min_schema': '00050',
        'allowed': ['00050', '00051'],
        'reason': '<CAN-ENTERS> in RunnableEntity introduced in R21-11 (00050)'
    },
}

IGNORED_FILE_PATTERNS = {
    'xml_with_errors.arxml',
    'ProfileSettings.xml',
}


class SchemaValidator:
    """Loads and caches XSD schemas and validates XML files against them."""

    def __init__(self,
                 schema_dir: str,
                 requested_schemas: Optional[List[str]] = None):
        """Initialize validator with schema directory and target schemas."""
        self.schema_dir = os.path.abspath(schema_dir)
        if not os.path.isdir(self.schema_dir):
            raise FileNotFoundError(
                f"Schema directory not found: {self.schema_dir}")

        self.requested_schemas = (
            requested_schemas or list(SCHEMA_RELEASES.keys()))
        self._schema_cache: Dict[str, ET.XMLSchema] = {}

    def get_schema(self, version: str) -> ET.XMLSchema:
        """Load and compile an XMLSchema on demand and cache it."""
        if version not in self._schema_cache:
            info = SCHEMA_RELEASES.get(version)
            if not info:
                raise ValueError(f"Unknown schema version: {version}")
            xsd_path = os.path.join(self.schema_dir, info['file'])
            if not os.path.exists(xsd_path):
                raise FileNotFoundError(f"Schema file not found: {xsd_path}")

            tree = ET.parse(xsd_path)
            self._schema_cache[version] = ET.XMLSchema(tree)
        return self._schema_cache[version]

    def get_applicable_schemas(
        self, file_path: str
    ) -> Tuple[List[str], Optional[str]]:
        """Determine which schema versions apply based on exception rules."""
        norm_path = os.path.normpath(file_path).replace('\\', '/')

        for exc_dir, rule in DIRECTORY_SCHEMA_EXCEPTIONS.items():
            if exc_dir in norm_path:
                allowed = [
                    s for s in self.requested_schemas if s in rule['allowed']]
                return allowed, rule['reason']

        return list(self.requested_schemas), None

    def validate_file(self, file_path: str) -> List[Dict]:
        """Validate an XML file against all applicable schema versions."""
        applicable_schemas, skip_reason = self.get_applicable_schemas(
            file_path)

        try:
            doc = ET.parse(file_path)
        except (ET.XMLSyntaxError, OSError) as e:
            return [{
                'version': 'parse',
                'release': 'XML-Syntax',
                'valid': False,
                'error': f"XML syntax error: {str(e)}",
                'skip_reason': None
            }]

        results = []
        for ver in self.requested_schemas:
            info = SCHEMA_RELEASES[ver]
            if ver not in applicable_schemas:
                results.append({
                    'version': ver,
                    'release': info['release'],
                    'valid': True,
                    'skipped': True,
                    'skip_reason': skip_reason,
                    'error': None
                })
                continue

            schema = self.get_schema(ver)
            is_valid = schema.validate(doc)
            err_msg = None
            if not is_valid:
                err = schema.error_log.last_error
                if err:
                    err_msg = (
                        f"Line {err.line}, col {err.column}: {err.message}")
                else:
                    err_msg = "Schema validation failed."

            results.append({
                'version': ver,
                'release': info['release'],
                'valid': is_valid,
                'skipped': False,
                'skip_reason': None,
                'error': err_msg
            })

        return results


def is_autosar_xml(file_path: str) -> bool:
    """Quickly check if an XML file has an AUTOSAR root element."""
    if file_path.endswith('.arxml'):
        return True
    try:
        for _, elem in ET.iterparse(file_path, events=('start',)):
            tag = elem.tag
            return 'AUTOSAR' in tag
    except (ET.XMLSyntaxError, OSError, UnicodeDecodeError):
        return False
    return False


def _collect_dir_xml_files(dir_path: str, files_found: Set[str]) -> None:
    """Recursively collect valid AUTOSAR XML files from directory."""
    for root, _, files in os.walk(dir_path):
        for f in files:
            if not (f.endswith('.arxml') or f.endswith('.xml')):
                continue
            if f in IGNORED_FILE_PATTERNS:
                continue
            fpath = os.path.join(root, f)
            if is_autosar_xml(fpath):
                files_found.add(os.path.abspath(fpath))


def find_xml_files(targets: List[str], base_dir: str) -> List[str]:
    """Find all XML / ARXML files matching targets or search directories."""
    files_found: Set[str] = set()

    for target in targets:
        if os.path.isabs(target):
            full_path = target
        else:
            full_path = os.path.join(base_dir, target)

        if os.path.isfile(full_path):
            basename = os.path.basename(full_path)
            if basename not in IGNORED_FILE_PATTERNS and is_autosar_xml(full_path):
                files_found.add(os.path.abspath(full_path))
        elif os.path.isdir(full_path):
            _collect_dir_xml_files(full_path, files_found)

    return sorted(list(files_found))


def parse_schema_arg(schema_str: str) -> List[str]:
    """Parse comma-separated schema version arguments like '48,51'."""
    if not schema_str or schema_str.lower() in ('all', 'any', '*'):
        return list(SCHEMA_RELEASES.keys())

    versions = []
    for token in schema_str.split(','):
        t = token.strip()
        if not t:
            continue
        if len(t) == 2 and t.isdigit():
            t = f"000{t}"
        elif len(t) == 5 and t.isdigit():
            pass
        elif t.upper().startswith('R'):
            for k, v in SCHEMA_RELEASES.items():
                if v['release'].upper() == t.upper():
                    t = k
                    break
        if t in SCHEMA_RELEASES:
            if t not in versions:
                versions.append(t)
        else:
            allowed = list(SCHEMA_RELEASES.keys())
            print(f"Warning: Unknown schema '{token}'. Allowed: {allowed}")

    return versions if versions else list(SCHEMA_RELEASES.keys())


def main():
    """Execute main CLI schema validation entry point."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    parser = argparse.ArgumentParser(
        description="Validate AUTOSAR XML files against schemas in doc/schema."
    )
    parser.add_argument(
        'targets',
        nargs='*',
        help="Target files or directories. Default: examples/xml and template"
    )
    parser.add_argument(
        '--schema', '-s',
        default='all',
        help="Schema version(s): 48, 49, 50, 51, or comma-separated list"
    )
    parser.add_argument(
        '--schema-dir',
        default=os.path.join(repo_root, 'doc', 'schema'),
        help="Directory containing AUTOSAR XSD files (default: doc/schema)"
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help="Validate all ARXML files in both examples/ and usage_tests/"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Display detailed output for all validated files"
    )

    args = parser.parse_args()

    schema_versions = parse_schema_arg(args.schema)

    if args.all:
        target_paths = [
            os.path.join(repo_root, 'examples'),
            os.path.join(repo_root, 'usage_tests')
        ]
    elif args.targets:
        target_paths = args.targets
    else:
        target_paths = [
            os.path.join(repo_root, 'examples', 'xml'),
            os.path.join(repo_root, 'examples', 'template', 'generated')
        ]

    xml_files = find_xml_files(target_paths, repo_root)

    if not xml_files:
        if args.verbose:
            print(f"No XML files found matching target(s): {target_paths}")
        sys.exit(0)

    if args.verbose:
        print("=" * 80)
        print("AUTOSAR XML Schema Validator")
        print("=" * 80)
        sdir = os.path.relpath(args.schema_dir, repo_root)
        print(f"Schema Directory: {sdir}")
        active = [
            f"{v} ({SCHEMA_RELEASES[v]['release']})" for v in schema_versions]
        print(f"Target Schemas:   {', '.join(active)}")
        print(f"Total XML Files:  {len(xml_files)}\n")

    validator = SchemaValidator(
        args.schema_dir, requested_schemas=schema_versions)

    files_with_failures = 0
    current_dir = None

    for file_path in xml_files:
        rel_path = os.path.relpath(file_path, repo_root)
        file_dir = os.path.dirname(rel_path)

        if args.verbose and file_dir != current_dir:
            current_dir = file_dir
            print(f"\nDirectory: {current_dir}")

        results = validator.validate_file(file_path)
        failures = [r for r in results if not r['valid']]

        if failures:
            files_with_failures += 1
            for r in failures:
                print(
                    f"{rel_path}: [{r['version']} ({r['release']})] "
                    f"{r['error']}")
        elif args.verbose:
            skipped_info = ""
            skipped = [r for r in results if r.get('skipped')]
            if skipped:
                sk_vers = [r['release'] for r in skipped]
                reason = skipped[0].get('skip_reason', '')
                skipped_info = f" (skipped {', '.join(sk_vers)}: {reason})"
            print(f"  [PASS] {os.path.basename(file_path)}{skipped_info}")

    if args.verbose:
        print("\n" + "=" * 80)
        print("Validation Summary:")
        print("=" * 80)
        print(f"Files Validated:  {len(xml_files)}")
        print(f"Files Passed:     {len(xml_files) - files_with_failures}")
        print(f"Files Failed:     {files_with_failures}")

    if files_with_failures > 0:
        if args.verbose:
            print("\nRESULT: FAILED")
        sys.exit(1)
    else:
        if args.verbose:
            print("\nRESULT: ALL XML FILES PASSED SCHEMA VALIDATION")
        sys.exit(0)


if __name__ == '__main__':
    main()
