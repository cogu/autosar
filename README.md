# autosar

Redesign of the AUTOSAR Python package.

## DISCLAIMER

THIS IS FOR RESEARCH-PURPOSES ONLY.

## Requirements

* Python 3.10+
* lxml

## Abstract

Investigate how the AUTOSAR XML schema can be realized as Python classes.

* How would such a software design look like?
* Is it useful?

## Project Scope

### New class hierarchy

* Follow XML schema as much as possible.
* Evaluate variadic arguments in class constructors.
  * Is it user-friendly enough or too hard to use?
  * How to document?
* Which factory methods are needed to create elements programmatically?

### Modern coding style

* Snake-case naming on variable and method names.
* Modern type-hinting, this forces Python 3.10+.
* Python Enum classes for enumeration types seen in XML schema.

### New approach to reading and writing XML

* Simplify reuse by following the new class hierachy (polymorphism).
* Evaulate lxml module, can it be used to improve error handling?

### Unit testing

* Evaluate reading and writing ARXML only for the element under test instead of entire ARXML files.

## Project Limitations

* Support AUTOSAR classic platform only.
* Support only newer AUTOSAR schema versions, starting with R21-11.
* Don't support blueprints or variant handling of any kind.

## Supported Elements

Supported elements will be listed here. If an element is not mentioned below it's not yet supported.

### Packageable Elements

No packageable elements are supported.

### Other Elements

No other elements are supported.
