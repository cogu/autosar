![Python package](https://github.com/cogu/autosar/actions/workflows/python-package.yml/badge.svg)

# Python AUTOSAR v0.5

A set of Python modules for working with [AUTOSAR](https://www.autosar.org/) XML files.

The primary use case is to enable Python to generate ARXML files for import in other (commercial) AUTOSAR toolchains.
It also has some support for parsing AUTOSAR XML files.

**Important notes:**

1. Python AUTOSAR v0.5+ uses a new API and is incompatible with earlier versions.
2. For Python AUTOSAR v0.4, see the [v0.4 maintenance branch](https://github.com/cogu/autosar/tree/maintenance/0.4).
3. At this point most elements are supported except for SwcInternalBehavior. Due to its massive size, that element won't have proper support until v0.5.5.

## Major design changes

AUTOSAR v0.5 has been rewritten and modernized.

**Key features:**

* New class hierachy
  * Follows the structure of the AUTOSAR XML schema where possible.
* Snake-case naming of variables and methods (Follow PEP8 standard).
* Modern type hinting (this unfortunately requires Python 3.10 or later).
* Python Enum classes for enumeration types.
* Improved XML reading and writing using lxml.
* Linting support
  * Source code is checked with both Pylint and flake8.
* New unit test suite
  * More comprehensive unit tests for every element.
  * Much faster to run as it uses the new XML reader and writer.

## Supported AUTOSAR versions

The implementation tries to follow release R22-11. However, the generated ARXML validates against all versions listed below.
When saving, use the `schema_version` parameter to select desired version (integer with value 48-51).

* 48 (R19-11, Classic AUTOSAR 4.5)
* 49 (R20-11, Classic AUTOSAR 4.6)
* 50 (R21-11, Classic AUTOSAR 4.7)
* 51 (R22-11, Classic AUTOSAR 4.8)

Only Clasic AUTOSAR will be supported.

## Supported XML elements

For currently supported XML elements, see the [CHANGELOG](CHANGELOG.md) file.

## Usage

```python
import autosar.xml
import autosar.xml.element as ar_element


workspace = autosar.xml.Workspace()
workspace.create_package_map({"ApplicationDataTypes": "DataTypes/ApplicationDataTypes",
                              "DataConstrs": "DataTypes/DataConstrs"})
data_constraint = ar_element.DataConstraint.make_internal("uint8_ADT_DataConstr", 0, 255)
workspace.add_element("DataConstrs", data_constraint)
sw_data_def_props = ar_element.SwDataDefPropsConditional(data_constraint_ref=data_constraint.ref())
data_type = ar_element.ApplicationPrimitiveDataType("uint8_ADT",
                                                    category="VALUE",
                                                    sw_data_def_props=sw_data_def_props)
workspace.add_element("ApplicationDataTypes", data_type)
workspace.create_document("datatypes.arxml", packages="/DataTypes")
workspace.write_documents()
```

## Requirements

* Python 3.10+
* lxml
* tomli (Python 3.10 only, tomli is built-in for Python 3.11)
* [cfile](https://github.com/cogu/cfile) v0.4.0+

## Installation

Manual install required as this version is not available on PyPI (until v0.6).

### Preparation

Download a compressed source package from GitHub or clone this repo to a local directory.

### Installation steps for virtual environment

Start bash (Linux) or Powershell (Windows).

#### Create virtual environment

```bash
python -m venv .venv
```

#### Activate virtual environment

On Windows run:

```bash
.\.venv\Scripts\activate
```

On Linux run:

```bash
source .venv/bin/activate
```

#### Upgrade toolchain

Once virtual environment is active run:

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
```

#### Installing the Python module

Your current directory must be either where you unzipped the source package
or your where you cloned the git repo (See preparation step above).

For standard install, run:

```bash
pip install  .
```

For editable install, run:

```bash
pip install --editable .
```

### XML Workspace API

The `autosar.xml.Workspace` class offers two slightly different APIs for creating packages and elements. The main difference between them is the usage of namespaces.

#### Simple API methods

For small projects, use the simple API.

Methods in the simple API:

* Workspace.create_package_map
* Workspace.add_element
* Workspace.find_element
* Workspace.get_package

For for more information, see the [Simple API - User Guide](doc/markdown/simple_api_user_guide.md) that demonstrates the use of this API.

#### Advanced API - Requires namespaces

The advanced API is recomended for larger projects. It requires you to write custom template classes in addition to creating namespaces.

Methods in the advanced API:

* Workspace.create_namespace
* Workspace.get_package_ref_by_role
* Workspace.apply
* Workspace.load_config

It can be quite powerful when used the right way but requires some setting up.

There's no user guide yet. See the files under [examples/template](examples/template/) for reference.

#### Common methods

A number of methods are common for both APIs. For the advanced API you can skip most of them and instead use config files (.toml) to let the
`Workspace` class handle both package and document creation automatically.

Common methods:

* Workspace.set_document_root
* Workspace.create_document
* Workspace.create_document_mapping
* Workspace.write_documents

### Creating XML elements

The module `autosar.xml.element` contains all supported elements that you can add to a package. Most often you simply call the constructor for an object you want to create and then add it to a package.

Some elements are quite complicated to create manually. Instead of using the constructor method, some classes offers one or several convenience-methods with names
beginning with either `make_` or `create_`. Exploring these methods is highly recomended.

List of convenience-methods:

* `MultiLanguageOverviewParagraph.make`
* `Computation.make_value_table`
* `Computation.make_rational`
* `DataConstraint.make_physical`
* `DataConstraint.make_internal`
* `ValueSpecification.make_value_with_check`
* `ValueSpecification.make_value`
* `ConstantSpecification.make_constant`
* `ModeDeclarationGroup.create_mode_declaration`
* `SenderReceiverInterface.create_data_element`
* `SenderReceiverInterface.create_invalidation_policy`
* `NvDataInterface.create_data_element`
* `ParameterInterface.create_parameter`
* `ClientServerOperation.create_argument`
* `ClientServerOperation.create_in_argument`
* `ClientServerOperation.create_inout_argument`
* `ClientServerOperation.create_out_argument`
* `ClientServerOperation.create_possible_error_ref`
* `ClientServerInterface.create_operation`
* `ClientServerInterface.create_possible_error`
* `ModeSwitchInterface.create_mode_group`
* `ProvidePortComSpec.make_from_port_interface`
* `ProvidePortComSpec.make_non_queued_sender_com_spec`
* `ProvidePortComSpec.make_from_port_interface`
* `RequirePortComSpec.make_non_queued_receiver_com_spec`
* `SwComponentType.create_provide_port`
* `SwComponentType.create_require_port`
* `SwComponentType.create_pr_port`
* `CompositionSwComponentType.create_component_prototype`
* `CompositionSwComponentType.create_connector`

## Python Module Hierachy

### autosar.xml

Packages for handling AUTOSAR XML (ARXML).

### autosar.model

Implementation model, an intermediate model between XML and RTE generation.

### autosar.generator

RTE generators. Right now it only has a generator for the RTE type header.
This part is in early stages of development and is probably not very useful.

## Development Roadmap

Below is a rough roadmap of planned releases.

**v0.5.0:** Data types

**v0.5.1:** Value specifications and constants

**v0.5.2:** Port interfaces

**v0.5.3:** Components and ports

**v0.5.4:** SwcInternalBehavior - basics

* Runnables
* Events

**v0.5.5** SwcInternalBehavior - ports

* Port-access
* Port-API options

**v0.5.6** Fixes and refactoring

* Fix some early design mistakes
* Harmonize some member names to better match "qualified name" from XSD (BREAKING CHANGE)
  * For the most part this means that several class members will have its "_ref" suffix stripped from its name.
* Attempt to break apart large Python files into smaller ones.

**v0.5.7** Add some missing elements and functions that wasn't prioritized before.

**v0.6.0:** Stable version, publish to PyPI.

**v0.7.0:** RTE-generator and system description

* Contract-phase RTE generator
* System description support

**v0.8.0:** Stable version, publish to PyPI.

**v0.9.0:** Documentation

* Update documentation project on readthedocs site.

**v1.0.0:** Stable version, publish to PyPI.
