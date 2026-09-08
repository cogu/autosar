# v0.5.8 TODO

## Split the implementation behind `autosar.xml.element`

Refactor `src/autosar/xml/element.py` into smaller modules without changing the
public API or the runtime identity of its classes.

Keep `autosar.xml.element` as the stable public facade and place extracted
implementations in the internal `autosar.xml.elements` package:

```text
src/autosar/xml/
      element.py
      elements/
            __init__.py
            _base.py
            documentation.py
            common.py
            computation_method.py
            constraint.py
            unit.py
            data_type.py
            calibration_data.py
            constant.py
            package.py
            mode_declaration.py
            port_interface.py
            system_template.py
            software_component.py
            service_needs.py
            internal_behavior.py
            service_dependency.py
```

The exact module grouping may be adjusted when an extraction reveals a clearer
dependency boundary. The existing section markers are a starting point, not a
requirement that every section becomes exactly one module. During migration,
`element.py` may contain the classes not yet extracted alongside imports that
re-export classes already moved to `elements/`.

### Compatibility requirements

- [x] Preserve `import autosar.xml.element as ar_element`.
- [x] Preserve `from autosar.xml.element import ClassName`.
- [x] Keep `src/autosar/xml/element.py` as the public compatibility facade.
- [x] Re-export the original class objects from `element.py`; do not
      create wrappers or duplicate class definitions.
- [x] Preserve reader and writer `isinstance` behavior.
- [x] Keep implementation modules importing directly from sibling modules under
      `autosar.xml.elements`, not through the public `element.py` facade.
- [x] Define an explicit public `__all__` in `element.py` so implementation
      imports do not become accidental public API.
- [x] Treat `autosar.xml.elements` as an internal implementation namespace; do
      not advertise direct imports from it as public API.
- [x] Check whether the changed `Class.__module__` values affect supported
      serialization or introspection use cases.
- [x] Continue supporting Python 3.10.

### 1. Add compatibility tests

- [x] Test representative imports through `autosar.xml.element`.
- [x] Test representative direct imports from `autosar.xml.element`.
- [x] Test that facade imports and implementation-module imports refer to the
      same class objects.
- [x] Test representative `isinstance` checks used by the reader and writer.
- [x] Test a representative ARXML read/write round trip.
- [x] Decide whether pickle compatibility is supported and add tests if it is.

### 2. Create the implementation package and foundational module

- [x] Create `src/autosar/xml/elements/__init__.py`.
- [x] Create `src/autosar/xml/elements/_base.py`.
- [x] Keep `src/autosar/xml/element.py` in place as the public facade.
- [x] Move the foundational value and element classes to `_base.py`:
  - `NumericalValue`
  - `PositiveIntegerValue`
  - `Referrable`
  - `MultiLanguageReferrable`
  - `Identifiable`
  - `CollectableElement`
  - `ARElement`
- [x] Move the complete admin-data family to `_base.py` because `AdminData` is
      part of the ubiquitous `Identifiable` substrate:
  - `SpecialDataElement`
  - `SpecialDataValue`
  - `SpecialDataGroupContent`
  - `SpecialDataGroup`
  - `Modification`
  - `ModificationsArgumentType`
  - `DocRevision`
  - `UsedLanguageArgtype`
  - `AdminData`
- [x] Move `make_unique_name_in_list` to `_base.py` unless a more appropriate
      shared utility module emerges.
- [x] Add `from __future__ import annotations` to split modules.
- [x] Use imports guarded by `TYPE_CHECKING` for annotation-only dependencies.
- [x] Use local imports only where executable code needs a class from a module
      that would otherwise create an import cycle.
- [x] Remove each moved definition from `element.py` and import the same class
      object from `elements._base` instead.
- [x] Re-export the foundational API from `element.py`.
- [x] Run the compatibility tests and the admin-data tests.

### 3. Extract low-coupling sections

Extract and validate one module at a time:

- [x] `unit.py`
- [x] `constraint.py`
- [x] `computation_method.py`
- [x] An auxiliary-object module, or place `SwAddrMethod` in the most suitable
      existing domain module.
- [x] `service_needs.py`
- [x] Re-export every moved public name from `element.py`.
- [x] Run the focused tests for each extracted section before continuing.

### 4. Extract documentation and common structures

- [x] Create `documentation.py`.
- [x] Resolve the `_base.py`/documentation dependency deliberately:
  - `_base.py` owns `AdminData` and the foundational classes.
  - Annotation-only documentation imports use `TYPE_CHECKING`.
  - Runtime construction and `isinstance` checks use narrowly placed local
    imports where necessary.
  - `documentation.py` may import foundational classes from `_base.py`
    normally.
- [x] Create `common.py` for generic/common structure classes.
- [x] Re-export all moved names.
- [x] Run documentation, admin-data, and common-structure tests.

### 5. Extract the data model group

Treat these sections as a connected group and move them in the order that
produces the fewest runtime imports:

- [x] `data_type.py`
- [x] `calibration_data.py`
- [x] `constant.py`
- [x] Resolve the runtime cycle among value specifications, value lists, and
      calibration containers with local imports where required.
- [x] Re-export all moved names.
- [x] Run data-type, calibration, and constant tests after each extraction.

### 6. Extract package and interface modules

- [x] Create `package.py`.
- [x] Resolve the `Referrable.root_collection()` dependency on
      `PackageCollection` without importing `package.py` while `_base.py` is
      loading.
- [x] Create `mode_declaration.py`.
- [x] Create `port_interface.py`.
- [x] Create `system_template.py`.
- [x] Re-export all moved names.
- [x] Run package, mode-declaration, port-interface, and system-template tests.

### 7. Extract the software-component group

Move this tightly connected group last:

- [x] Create `software_component.py`.
- [x] Create `internal_behavior.py`.
- [x] Create `service_dependency.py`.
- [x] Place `InternalBehavior` and `SwcInternalBehavior` in
      `internal_behavior.py`, even though they currently appear after the
      service-dependency section marker.
- [x] Resolve runtime cycles among software-component types, internal behavior,
      variable access, instance references, and service dependencies.
- [x] Re-export all moved names.
- [x] Run all software-component, internal-behavior, and service-dependency
      tests.

### 8. Update development tooling

- [x] Update `dev_utils/refresh_implementation.py` to scan all Python modules in
      `src/autosar/xml/elements/` and any classes still present in
      `src/autosar/xml/element.py` during migration.
- [x] Derive implementation categories from modules or explicit metadata rather
      than source line ranges in one file.
- [x] Preserve the existing `.implementation_cache.json` data contract where
      practical so downstream tools remain unchanged.
- [x] Update release-history lookup to find classes in historical
      `src/autosar/xml/element.py` revisions and current modules under
      `src/autosar/xml/elements/`.
- [x] Update implementation-cache and wiki documentation that currently says
      only `element.py` is scanned.
- [x] Regenerate the implementation cache and XML index and inspect the diff.

### 9. Final validation

- [x] Run all unit tests:

  ```bash
  .venv/bin/python -m unittest discover -v tests test_*.py
  ```

- [x] Run flake8 on source, tests, examples, and development utilities using the
      commands in `AGENTS.md`.
- [x] Run pylint on `src`.
- [x] Run `./validate_xml.sh`.
- [x] Run `./validate_examples.sh`.
- [x] Run a clean-process import smoke test for `autosar.xml.element`, reader,
      writer, workspace, document, and the internal `autosar.xml.elements`
      package.
- [x] Confirm that no internal module imports classes through the public facade
      in a way that introduces a circular import.
- [x] Review the final public exports against the classes and aliases exported
      by the original `element.py`.
