# Development Utilities (`dev_utils`)

This directory contains developer tooling and utility scripts for developing, exploring AUTOSAR XML schemas, validating XML, and maintaining documentation in the `autosar` codebase.

---

## Tool Overview

| Script | Purpose | Wrapper Script |
|---|---|---|
| [`explore_subelement.py`](explore_subelement.py) | Schema inspection, child element analysis, and dependency tree explorer. | — |
| [`refresh_implementation.py`](refresh_implementation.py) | AST scanner that indexes implemented classes and enums into `.implementation_cache.json`. | — |
| [`validate_xml.py`](validate_xml.py) | Multi-schema XSD validator (`00048`–`00051`) using `lxml` and `doc/schema/`. | `validate_xml.cmd`, `validate_xml.sh` |
| [`build_docs.py`](build_docs.py) | Jinja2 documentation generator that embeds tested code and captured output. | `build_docs.cmd`, `build_docs.sh` |

---

## 1. Schema Explorer: `explore_subelement.py`

Inspects AUTOSAR XSD schemas ([`doc/schema/AUTOSAR_00051.xsd`](../doc/schema/AUTOSAR_00051.xsd)) to analyze element structures, wrapper hierarchies, cardinality, and implementation wiring status.

### Usage
```bash
# Explore child elements and inherited groups of a complexType or group
python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR

# Drill down into a specific child path or wrapper
python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR/RUNNABLES

# Generate a recursive dependency tree with bottom-up implementation leaf order
python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR/AR-TYPED-PER-INSTANCE-MEMORYS

# Limit search depth
python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR/RUNNABLES -d 1

# Include variant handling / blueprint elements (omitted by default)
python dev_utils/explore_subelement.py SWC-INTERNAL-BEHAVIOR --include-ignored

# Include deprecated (removed/obsolete) elements (omitted by default)
python dev_utils/explore_subelement.py APPLICATION-ENDPOINT --include-deprecated
```

### Deprecation & Status Handling (`atp.Status`)
- **`removed` / `obsolete`**: Filtered out and marked `[REMOVED]` / `[OBSOLETE]` (or `[NOT SUPPORTED: Removed/Obsolete]`) to prevent implementing obsolete elements.
- **`draft` / `candidate`**: Tagged clearly as `[DRAFT]` / `[CANDIDATE]` across child listings, dependency trees, bottom-up order, and implementation summaries.


---

## 2. Implementation Cache Builder: `refresh_implementation.py`

Uses Python's AST parser to scan [`src/autosar/xml/element.py`](../src/autosar/xml/element.py) and [`src/autosar/xml/enumeration.py`](../src/autosar/xml/enumeration.py), extracting docstring mappings (`Complex type AR:...`, `group AR:...`, `Tag Variants:...`) and constructor parameter wiring.

Saves cache to `dev_utils/.implementation_cache.json` (gitignored).

### Usage
```bash
python dev_utils/refresh_implementation.py
```

---

## 3. XML Schema Validator: `validate_xml.py`

Validates generated `*.arxml` files across all target schemas in [`doc/schema/`](../doc/schema) (`00048` / R19-11 through `00051` / R22-11) using Python's `lxml` bindings.

- **Silent on success** (exit code `0`).
- **Detailed errors on failure** (exit code `1`, compiler-style `file:line:col` error format).
- **Directory Exception Rules** (e.g. automatically skips `00048`/`00049` for `examples/xml/component` where `<CAN-ENTERS>` requires `00050`+).

### Usage
```bash
# Validate default directories (examples/xml and examples/template/generated) silently
validate_xml.cmd               # Windows
./validate_xml.sh              # Linux

# Verbose output with full summary
validate_xml.cmd -v

# Validate all ARXML files in repo (examples/ and usage_tests/)
validate_xml.cmd --all -v

# Target specific schema versions
python dev_utils/validate_xml.py examples/xml/port -s 48,51
```

---

## 4. Documentation Generator: `build_docs.py`

Renders Jinja2 documentation templates from [`doc/templates/`](../doc/templates) into [`doc/markdown/`](../doc/markdown).

### Template Helpers
- `{{ include_code("usage_tests/basic_use/1_packages.py") }}`: Embeds source code inside a markdown code block.
- `{{ run_code("usage_tests/basic_use/1_packages.py") }}`: Executes the script and embeds real `stdout` into a text block, ensuring documentation output never goes stale.
- `{{ file_content("path/to/file") }}`: Returns raw file content.

### Usage
```bash
# Render all documentation templates
build_docs.cmd                 # Windows
./build_docs.sh                # Linux

# Check if markdown documentation is up-to-date (exits with code 1 if diff exists)
python dev_utils/build_docs.py --check
```
