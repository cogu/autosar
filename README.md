# Python AUTOSAR v0.4

A set of Python modules for working with [AUTOSAR](https://www.autosar.org/) XML files.

The primary use case is to enable Python to generate ARXML files for further importing into other (commercial) AUTOSAR toolchains.
It has some support for parsing ARXML files.

This is the maintenance branch for v0.4. Latest release is [v0.4.2](https://github.com/cogu/autosar/releases/tag/v0.4.2).

## Documentation

[Documentation for v0.4](https://autosar.readthedocs.io/en/latest/).

## Supported AUTOSAR versions

* AUTOSAR 3.0
* AUTOSAR 4.2

Classic AUTOSAR only.

## Requirements

* Python 3.4+
* cfile v0.2.0

## Installation

```bash
pip install "autosar<0.5"
```

For now it works to install without the version part, it's there for future proofing the instruction after newer versions are released to PyPI.
