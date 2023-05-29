[![Python package](https://github.com/cogu/autosar/actions/workflows/python-package.yml/badge.svg?branch=research%2F0.5)](https://github.com/cogu/autosar/actions/workflows/python-package.yml)

# Python AUTOSAR

A set of Python modules for working with [AUTOSAR](https://www.autosar.org/) XML files.

The primary use case is to enable Python to generate ARXML files for further importing into other (commercial AUTOSAR) toolchains.
It also has some support for parsing ARXML files.

## Version 0.4

Stable version. Latest release is [v0.4.1](https://github.com/cogu/autosar/releases/tag/v0.4.1).

[Documentation for v0.4](https://autosar.readthedocs.io/en/latest/).

### Supported AUTOSAR versions (v0.4)

* AUTOSAR 3.0
* AUTOSAR 4.2

Classic AUTOSAR only.

### Requirements (v0.4)

* Python 3.4+
* cfile

### Installation (v0.4)

```bash
pip install "autosar<0.5"
```

For now it works to install without the version part, it's there for future proofing the instruction
after newer versions are released to PyPI.

## Version 0.5

Development and research version. Not yet released.

Documentation for v0.5 will be maintained in the [project Wiki](https://github.com/cogu/autosar/wiki).

### Supported AUTOSAR versions (v0.5)

* R21-11 (Schema version 50).

Classic AUTOSAR only.

### Requirements (v0.5)

* Python 3.10+
* lxml

### Installation (v0.5)

Manual install required as this version is not available on PyPI.

1. Make sure you have the latest version of `pip` and `setuptools` installed.
2. Download source or clone git repo.
3. Install locally using one of the below methods.

#### Preparation

Run in either venv or local.

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
```

#### Standard install

```bash
pip install  .
```

#### Editable install (Development mode)

```bash
python -m venv .venv
# Activate your venv environment
pip install --editable .
pip install flake8
```