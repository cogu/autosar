# Template Example

Demonstrates how to apply template objects in a workspace.

## Template objects

Template objects enables developers to describe how ARXML elements should be created without specifying its final location.
Think of it like recipes for ARXML elements.
Most importantly it allows us to describe the dependencies between elements. This helps greatly when working in large scale projects with multiple developers.

To assist with their creation, a template factory (see [factory.py](demo_system/factory.py)) needs to be written. New template objects are then declared by calling on the various factory methods. For example, a relatively complex data type can now be declared using a single line of Python code (see [datatype.py](demo_system/datatype.py)).

## Namespaces

Before applying template objects we first need to declare one or more namespaces in our workspace.

A namespace is a mapping that decides in what package each new element should be placed. Data types goes into one package, port-interfaces into another and so on.

In short, namespaces handles the creation of packages while templates handles the creation of ARXML elements in those packages.

### Applying templates

Templates are applied in a workspace using the `Workspace.apply` method.
In general, applying template objects requires 4 steps.

1. Create an empty workspace.
2. In the workspace, create one or more namespaces (a default is fine).
3. Call the `Workspace.apply` method with the template object as argument.
4. Save the workspace as ARXML

During step 3, Python AUTOSAR not only creates the element itself, it automatically creates all elements
that it depends on (data types, port interfaces, modes etc.).

In the two Python scripts found in this directory you will see examples how an entire ARXML project is generated from a single line of code:

```python
workspace.apply(component.CompositionComponent)
```

This will create all ARXML elements that the compositin SWC depends on such as:

- Data types
- Port interfaces
- Constants
- Mode declarations
- inner (or child) SWCs

If you look closely in the examples you will notice that it handles the platform types differently. Normally, unused elements are skipped but
this special step forces them to be generated in the project even if they are unused/unreferenced. This is used as to not confuse the toolchain that will read the ARXML files later.

## Generation with config

The recomended way is to use a config file which are loaded into the workspace during its creation. See [config.toml](config.toml) for an example.

With a config file you can create both namespaces as well as the destination ARXML file names. This greatly helps with steps 2 and 4 above.
For a full example, see [generate_xml_using_config.py](generate_xml_using_config.py).

## Generation without config

It's possible to accomplish the same result without using a config file. It requires a bit more code setting up the workspace.
See [generate_xml_without_config.py](generate_xml_without_config.py) for a full example of that.

## Advantages and disadvantages using template objects

It's recommended to use template objects in medium to large projects that has multiple team members.

Advantages:

- Possible to track dependencies between elements.
- Prevents generating duplicate elements.
- The generated ARXML files will generate exactly what's currently in use (No unused elements).
- Easy to resolve merge conflicts when Python files are changed by different developers.

Disadantages:

- It takes a lot of time to setup. The hardest part is to to write and maintain the factory layer (see [factory.py](demo_system/factory.py)).
