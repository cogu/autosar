![Python package](https://github.com/cogu/autosar/actions/workflows/python-package.yml/badge.svg)

# Python AUTOSAR v0.5

A set of Python modules for working with [AUTOSAR](https://www.autosar.org/) XML files.

The primary use case is to enable Python to generate ARXML files for import in other (commercial) AUTOSAR toolchains.
It also has some support for parsing AUTOSAR XML files.

**Important notes:**

1. Python AUTOSAR v0.5+ uses a new API and is incompatible with earlier versions.
2. For Python AUTOSAR v0.4, see the [v0.4 maintenance branch](https://github.com/cogu/autosar/tree/maintenance/0.4).
3. Currently, only the categories mentioned below are supported. If you want a full API, wait for v0.6.0:
    * Data Types
    * Constants

## Major design changes

AUTOSAR v0.5 has been rewritten and modernized.

**Key features:**

* New class hierachy
  * Follows the structure of the AUTOSAR XML schema where possible.
* Snake-case naming of variables and methods (Follow PEP8 standard).
* Modern type hinting (this unfortunately requires Python 3.10 or later).
* Python Enum classes for enumeration types.
* Improved XML reading and writing with lxml.
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

## Requirements

* Python 3.10+
* lxml
* [cfile](https://github.com/cogu/cfile) v0.3.2+

## Installation

Manual install required as this version is not available on PyPI (until v0.6).

1. Make sure you have the latest version of `pip` and `setuptools` installed.
2. Download source or clone this repo.
3. Download source or clone the cfile repo (instruction below).
4. Install locally using one of the below methods.

### Preparation

Run in either venv or local.

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
git clone https://github.com/cogu/cfile.git cfile_0.3
cd cfile_0.3
git checkout v0.3.2
cd ..
python -m pip install cfile_0.3
```

You can delete the directory `cfile_0.3` after preparation step.

### Standard install

```bash
pip install  .
```

### Editable install (Development mode)

```bash
python -m venv .venv
# Activate your venv environment
pip install --editable .
pip install flake8
```

## Usage

Below is a short introduction. A more comprehensive documentation for v0.5 will be written later.

### Workspace

Create a new workspace object.

```python
import autosar.xml

workspace = autosar.xml.Workspace()
```

### Creating packages

Packages are created using the `make_packages` method. It can recursively create packages as if they are directories.

If you give it a single argument it will return the package created. If you give it multiple arguments it will return a list of packages created.

```python
import autosar.xml

workspace = autosar.xml.Workspace()
packages = workspace.make_packages("DataTypes/BaseTypes",
                                   "DataTypes/ImplementationDataTypes")
print(packages[0].name)
print(packages[1].name)
```

Output

```text
BaseTypes
ImplementationDataTypes
```

Using the builtin `zip`-method you can easily convert the returned list to a dictionary.

```python
import autosar.xml

workspace = autosar.xml.Workspace()
packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                    workspace.make_packages("DataTypes/BaseTypes",
                                            "DataTypes/ImplementationDataTypes")))
print(packages["BaseTypes"].name)
print(packages["ImplementationDataTypes"].name)
```

Output

```text
BaseTypes
ImplementationDataTypes
```

### Saving XML documents

Use the Writer class to save XML documents.

```python
import os
from autosar.xml import Document, Writer
import autosar.xml.element as ar_element

# Create new document object with an empty package
document = Document()
package = ar_element.Package("MyPackage")
document.append(package)
# Create a new file "document.arxml" in directory "data"
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
writer = Writer()
writer.write_file(document, os.path.join(base_path, "document.arxml"))
```

If you want to avoid creating the Document object(s) manually, the Workspace class offers several convenience methods related to saving XML.

```python
import os
from autosar.xml import Workspace

workspace = Workspace()
# Create three packages in workspace
workspace.make_packages("DataTypes", "PortInterfaces", "ComponentTypes")
# Save each package to a separate file inside the "data" directory
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
workspace.create_document(os.path.join(base_path, "datatypes.arxml"),
                          packages="/DataTypes")
workspace.create_document(os.path.join(base_path, "port_interfaces.arxml"),
                          packages="/PortInterfaces")
workspace.create_document(os.path.join(base_path, "component_types.arxml"),
                          packages="/ComponentTypes")
workspace.write_documents()
```

### Creating elements

The module `autosar.xml.element` contains all supported elements that you can add to a package. Just call the constructor for an object you want to create and then append it to a package.

Some classes, such as `Computation` has static helper methods starting with `make_`. They act like factory-methods for commonly used creation-patterns and returns a constructed object.

Here's an example where we create both a base type and a simple implementation data type. Newly created elements must be added to a package before they can be referenced by other elements.

```python
import autosar.xml
import autosar.xml.element as ar_element

workspace = autosar.xml.Workspace()
packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                    workspace.make_packages("DataTypes/BaseTypes",
                                            "DataTypes/ImplementationDataTypes")))

#Create new base type
uint8_base_type = ar_element.SwBaseType("uint8")
# Taking a reference before the element is added to a package returns None
print(uint8_base_type.ref())
# Add base type to package
packages["BaseTypes"].append(uint8_base_type)
# Taking a reference after the element is added to package returns a SwBaseTypeRef object
print(uint8_base_type.ref()) # SwBaseTypeRef has built-in string conversion

# Create new implementation data type
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
# Add implementation data type to package
packages["ImplementationDataTypes"].append(inactive_active_t)
# Find newly added element by its reference
element = workspace.find("/DataTypes/ImplementationDataTypes/InactiveActive_T")
print(f"{element.name}: {str(type(element))}")
```

Output

```text
None
/DataTypes/BaseTypes/uint8
InactiveActive_T: <class 'autosar.xml.element.ImplementationDataType'>
```

Here's a more fleshed out example, tt adds a `TEXTTABLE` CompuMethod and saves everything to an ARXML file. It also demonstrates how you control the XML schema version
when saving the file.

```python
import os
import autosar.xml
import autosar.xml.element as ar_element

workspace = autosar.xml.Workspace()
packages = dict(zip(["BaseTypes", "ImplementationDataTypes", "CompuMethods"],
                    workspace.make_packages("DataTypes/BaseTypes",
                                            "DataTypes/ImplementationDataTypes",
                                            "DataTypes/CompuMethods")))
uint8_base_type = ar_element.SwBaseType("uint8")
packages["BaseTypes"].append(uint8_base_type)

# Create CompuMethod
computation = ar_element.Computation.make_value_table(["Inactive",
                                                       "Active",
                                                       "Error",
                                                       "NotAvailable"])
compu_method = ar_element.CompuMethod(name='InactiveActive_T',
                                      int_to_phys=computation,
                                      category="TEXTTABLE")
#Add new CompuMethod to CompuMethods package
packages["CompuMethods"].append(compu_method)
# Create ImplementantationDataType, referencing the CompuMethod from different package
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref(),
                                                         compu_method_ref=compu_method.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
packages["ImplementationDataTypes"].append(inactive_active_t)
# Save DataType package and all its sub-packages into data/datatypes.arxml
# Before saving documents, set schema-version to 48 (R19-11) (Default is 51 or R22-11)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
workspace.create_document(os.path.join(base_path, "datatypes.arxml"), packages="/DataTypes")
workspace.write_documents(scehema_version=48)
```

### Reading XML files

Use the Reader class to read ARXML from files or strings. The read-methods produce `Document` objects.

```python
import os
from autosar.xml import Reader

# Read document from file "data/datatypes.arxml"
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
file_path = os.path.join(base_path, "datatypes.arxml")
reader = Reader()
document = reader.read_file(file_path)
# Find element by reference and then print name and type
data_type = document.find("/DataTypes/ImplementationDataTypes/InactiveActive_T")
print(f"{data_type.name}: {str(type(data_type))}")
```

Output

```text
InactiveActive_T: <class 'autosar.xml.element.ImplementationDataType'>
```

### RTE generator

RTE generation is in prototype stage and can't do very much at this point.
Here's a simple example how to generate the `Rte_Type.h` header file containing a single type definition.

It uses the latest version of [cfile](https://github.com/cogu/cfile) which has been completely rewritten to better handle complex code generation scenarios.

```python
import os
import autosar.xml
import autosar.xml.element as ar_element
from autosar.generator import TypeGenerator
from autosar.model import ImplementationModel

workspace = autosar.xml.Workspace()
packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                    workspace.make_packages("DataTypes/BaseTypes",
                                            "DataTypes/ImplementationDataTypes")))
uint8_base_type = ar_element.SwBaseType("uint8")
packages["BaseTypes"].append(uint8_base_type)
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
packages["ImplementationDataTypes"].append(inactive_active_t)
# Create ImplementationModel from XML workspace
implementation = ImplementationModel(workspace)
# Create data-type instance inside ImplementationModel
implementation.create_from_element(inactive_active_t)
# Generate RTE Types header in "data" folder
type_generator = TypeGenerator(implementation)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
type_generator.write_type_header(base_path)
```

Content of Rte_Type.h

```c
#ifndef RTE_TYPE_H_
#define RTE_TYPE_H_

#ifndef __cplusplus
extern "C"
{
#endif

/***********************************
*             INCLUDES             *
************************************/
#include "Rte.h"

/***********************************
*     CONSTANTS AND DATA TYPES     *
************************************/

typedef uint8 InactiveActive_T;

#ifndef __cplusplus
}
#endif // __cplusplus
#endif // RTE_TYPE_H_
```

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

**v0.5.4:** Component (internal) behavior

(There will probably be some intermediate versions here since behavior is a huge area.)

**v0.5.?:** System description

**v0.6.0:** First stable release. Publish to PyPI.
