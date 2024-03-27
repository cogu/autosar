# Simple API - User Guide

This is a short user guide how to create packages and elements using the simple API.

## Simple API

The simple API doesn't use namespaces as seen in the advanced API. Instead it relies on
a key-value (dictionary) data-structure to create and reference packages.

Here's a list of methods offered by the API:

* Workspace.create_package_map
* Workspace.add_element
* Workspace.find_element
* Workspace.get_package

## Workspace

Create a new workspace object.

```python
import autosar.xml

workspace = autosar.xml.Workspace()
```

## Creating packages

Use the `Workspace.create_package_map` to create packages.
The input argument is a dictionary where each value is a package reference string (of arbitrary depth)
and the key is a string of your choice which allows you to simply access the package later.

Use the `Workspace.get_package` method for accessing the package object by using the same key as
was used during the call to `Workspace.create_package_map`.

```python
import autosar.xml

workspace = autosar.xml.Workspace()
workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                            "ImplementationDataTypes": "DataTypes/ImplementationDataTypes"})
print(workspace.get_package("BaseTypes").name)
print(workspace.get_package("ImplementationDataTypes").name)
```

Output

```text
BaseTypes
ImplementationDataTypes
```

## Creating data types

Let's start by creating a `SwBaseType` followed by an `ImplementationDataType` referencing the previously created base type.

References are custom objects returned by the `ref`-method provided by all classes derived from `ARElement`.
All newly created elements must be added to a package before references can be created. Otherwise the `ref`-method will return `None`.

To quickly add an element to a package you created by calling the `Workspace.create_package_map` method,
use the `Workspace.add_element`-method.

In the example below we also save the `DataTypes`-package and all its sub-packages into a document titled `data/datatypes.arxml`.
Before you try the code, make sure you've created the directory `data` in same place as your Python-script.

```python
import os
import autosar.xml
import autosar.xml.element as ar_element

# Create workspace and packages
workspace = autosar.xml.Workspace()
workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                              "ImplementationDataTypes": "DataTypes/ImplementationDataTypes"})

# Create uint8 base type
uint8_base_type = ar_element.SwBaseType("uint8", size=8)
workspace.add_element("BaseTypes", uint8_base_type)

# Create implementation data type referencing the uint8 base type
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
workspace.add_element("ImplementationDataTypes", inactive_active_t)

# Save DataType package and all its sub-packages into data/datatypes.arxml
workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
workspace.create_document("datatypes.arxml", "/DataTypes")
workspace.write_documents()
```

## Creating ImplementationDataType with Compumethod

Let's add a `TEXTTABLE` `CompuMethod` to our `InactiveActive_T` implementation data type.
Here we take advantage of the `Computation.make_value_table` convenience-method to let Python fill
in the right properties of the object.

```python
import os
import autosar.xml
import autosar.xml.element as ar_element

workspace = autosar.xml.Workspace()
workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                              "ImplementationDataTypes": "DataTypes/ImplementationDataTypes",
                              "CompuMethods": "DataTypes/CompuMethods"})
# Create SwBaseType
uint8_base_type = ar_element.SwBaseType("uint8")
workspace.add_element("BaseTypes", uint8_base_type)

# Create CompuMethod
computation = ar_element.Computation.make_value_table(["Inactive",
                                                       "Active",
                                                       "Error",
                                                       "NotAvailable"])
compu_method = ar_element.CompuMethod(name='InactiveActive_T',
                                      int_to_phys=computation,
                                      category="TEXTTABLE")
workspace.add_element("CompuMethods", compu_method)

# Create ImplementantationDataType, referencing the SwBaseType and CompuMethod
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref(),
                                                         compu_method_ref=compu_method.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
workspace.add_element("ImplementationDataTypes", inactive_active_t)

# Save DataType package and all its sub-packages into data/datatypes.arxml
workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
workspace.create_document("datatypes.arxml", packages="/DataTypes")
workspace.write_documents()
```

### Reading XML files

Use the Reader class to read ARXML from files or strings. The read-methods produce `Document` objects.

```python
import os
from autosar.xml import Reader

# Read document from file "data/datatypes.arxml"
base_path = os.path.join(os.path.dirname(__file__), "data")
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
