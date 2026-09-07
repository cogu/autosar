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

- [ ] Preserve `import autosar.xml.element as ar_element`.
- [ ] Preserve `from autosar.xml.element import ClassName`.
- [ ] Keep `src/autosar/xml/element.py` as the public compatibility facade.
- [ ] Re-export the original class objects from `element.py`; do not
      create wrappers or duplicate class definitions.
- [ ] Preserve reader and writer `isinstance` behavior.
- [ ] Keep implementation modules importing directly from sibling modules under
      `autosar.xml.elements`, not through the public `element.py` facade.
- [ ] Define an explicit public `__all__` in `element.py` so implementation
      imports do not become accidental public API.
- [ ] Treat `autosar.xml.elements` as an internal implementation namespace; do
      not advertise direct imports from it as public API.
- [ ] Check whether the changed `Class.__module__` values affect supported
      serialization or introspection use cases.
- [ ] Continue supporting Python 3.10.

### 1. Add compatibility tests

- [ ] Test representative imports through `autosar.xml.element`.
- [ ] Test representative direct imports from `autosar.xml.element`.
- [ ] Test that facade imports and implementation-module imports refer to the
      same class objects.
- [ ] Test representative `isinstance` checks used by the reader and writer.
- [ ] Test a representative ARXML read/write round trip.
- [ ] Decide whether pickle compatibility is supported and add tests if it is.

### 2. Create the implementation package and foundational module

- [ ] Create `src/autosar/xml/elements/__init__.py`.
- [ ] Create `src/autosar/xml/elements/_base.py`.
- [ ] Keep `src/autosar/xml/element.py` in place as the public facade.
- [ ] Move the foundational value and element classes to `_base.py`:
  - `NumericalValue`
  - `PositiveIntegerValue`
  - `Referrable`
  - `MultiLanguageReferrable`
  - `Identifiable`
  - `CollectableElement`
  - `ARElement`
- [ ] Move the complete admin-data family to `_base.py` because `AdminData` is
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
- [ ] Move `make_unique_name_in_list` to `_base.py` unless a more appropriate
      shared utility module emerges.
- [ ] Add `from __future__ import annotations` to split modules.
- [ ] Use imports guarded by `TYPE_CHECKING` for annotation-only dependencies.
- [ ] Use local imports only where executable code needs a class from a module
      that would otherwise create an import cycle.
- [ ] Remove each moved definition from `element.py` and import the same class
      object from `elements._base` instead.
- [ ] Re-export the foundational API from `element.py`.
- [ ] Run the compatibility tests and the admin-data tests.

### 3. Extract low-coupling sections

Extract and validate one module at a time:

- [ ] `unit.py`
- [ ] `constraint.py`
- [ ] `computation_method.py`
- [ ] An auxiliary-object module, or place `SwAddrMethod` in the most suitable
      existing domain module.
- [ ] `service_needs.py`
- [ ] Re-export every moved public name from `element.py`.
- [ ] Run the focused tests for each extracted section before continuing.

### 4. Extract documentation and common structures

- [ ] Create `documentation.py`.
- [ ] Resolve the `_base.py`/documentation dependency deliberately:
  - `_base.py` owns `AdminData` and the foundational classes.
  - Annotation-only documentation imports use `TYPE_CHECKING`.
  - Runtime construction and `isinstance` checks use narrowly placed local
    imports where necessary.
  - `documentation.py` may import foundational classes from `_base.py`
    normally.
- [ ] Create `common.py` for generic/common structure classes.
- [ ] Re-export all moved names.
- [ ] Run documentation, admin-data, and common-structure tests.

### 5. Extract the data model group

Treat these sections as a connected group and move them in the order that
produces the fewest runtime imports:

- [ ] `data_type.py`
- [ ] `calibration_data.py`
- [ ] `constant.py`
- [ ] Resolve the runtime cycle among value specifications, value lists, and
      calibration containers with local imports where required.
- [ ] Re-export all moved names.
- [ ] Run data-type, calibration, and constant tests after each extraction.

### 6. Extract package and interface modules

- [ ] Create `package.py`.
- [ ] Resolve the `Referrable.root_collection()` dependency on
      `PackageCollection` without importing `package.py` while `_base.py` is
      loading.
- [ ] Create `mode_declaration.py`.
- [ ] Create `port_interface.py`.
- [ ] Create `system_template.py`.
- [ ] Re-export all moved names.
- [ ] Run package, mode-declaration, port-interface, and system-template tests.

### 7. Extract the software-component group

Move this tightly connected group last:

- [ ] Create `software_component.py`.
- [ ] Create `internal_behavior.py`.
- [ ] Create `service_dependency.py`.
- [ ] Place `InternalBehavior` and `SwcInternalBehavior` in
      `internal_behavior.py`, even though they currently appear after the
      service-dependency section marker.
- [ ] Resolve runtime cycles among software-component types, internal behavior,
      variable access, instance references, and service dependencies.
- [ ] Re-export all moved names.
- [ ] Run all software-component, internal-behavior, and service-dependency
      tests.

### 8. Update development tooling

- [ ] Update `dev_utils/refresh_implementation.py` to scan all Python modules in
      `src/autosar/xml/elements/` and any classes still present in
      `src/autosar/xml/element.py` during migration.
- [ ] Derive implementation categories from modules or explicit metadata rather
      than source line ranges in one file.
- [ ] Preserve the existing `.implementation_cache.json` data contract where
      practical so downstream tools remain unchanged.
- [ ] Update release-history lookup to find classes in historical
      `src/autosar/xml/element.py` revisions and current modules under
      `src/autosar/xml/elements/`.
- [ ] Update implementation-cache and wiki documentation that currently says
      only `element.py` is scanned.
- [ ] Regenerate the implementation cache and XML index and inspect the diff.

### 9. Final validation

- [ ] Run all unit tests:

  ```bash
  .venv/bin/python -m unittest discover -v tests test_*.py
  ```

- [ ] Run flake8 on source, tests, examples, and development utilities using the
      commands in `AGENTS.md`.
- [ ] Run pylint on `src`.
- [ ] Run `./validate_xml.sh`.
- [ ] Run `./validate_examples.sh`.
- [ ] Run a clean-process import smoke test for `autosar.xml.element`, reader,
      writer, workspace, document, and the internal `autosar.xml.elements`
      package.
- [ ] Confirm that no internal module imports classes through the public facade
      in a way that introduces a circular import.
- [ ] Review the final public exports against the classes and aliases exported
      by the original `element.py`.
