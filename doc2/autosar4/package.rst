Package (AR4)
=============

The AUTOSAR Package class.

**Usage:**

.. code-block:: python

   import autosar

   ws=autosar.workspace()
   package = ws.createPackage('ComponentType')

   print(ws.toXML())

.. _Package:

.. py:class:: Package(name : str)

   constructor.
   Also see :ref:`workspace-createPackage`.

   An AUTOSAR package is a container for elements. Elements can be basically anything that are not packages.


Attributes
----------

.. py:attribute:: Package.name

   The name of the package

.. py:attribute:: Package.elements

   List of elements in the package. Elements can be basically anything (except for packages and workspaces).

Data Types
----------

In AUTOSAR4 you can create different variants of implementation data types.

Type References
~~~~~~~~~~~~~~~

.. py:method:: Package.createImplementationDataTypeRef(name : str, implementationTypeRef : str, adminData = None)

   Creates a new implementation data type that is a reference to another implementation type (similar to a typedef in C).

Arguments:
^^^^^^^^^^
    * name: The name of the new data type
    * implementationTypeRef: Reference (string) to existing implementation type. If you have the implementation type as an object, use the .ref attribute to get it as string.
    * adminData (optional): optional AdminData object

Example:
^^^^^^^

.. include:: examples/createImplementationDataTypeRef.py
    :code: python

Implementation Pointer Data Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createImplementationDataTypePtr(name : str, implementationTypeRef : str, swImplPolicy = None, adminData = None)

   Creates a new implementation data type that is a pointer to a base type (Similar to a pointer type definition in C).

Arguments:
^^^^^^^^^^
    * name: The name of the new data type
    * baseTypeRef: Reference (string) to existing base type. If you have the base type as an object, use the .ref attribute to get it as string.
    * swImplPolicy (optional): Set this to 'CONST' in order to create a const pointer data type
    * adminData (optional): optional AdminData object

Example:
^^^^^^^

.. include:: examples/createImplementationDataTypePtr.py
    :code: python
