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

   Package constructor.
      
Attributes
----------

.. py:attribute:: Package.name

   The name of the package

.. py:attribute:: Package.elements

   List of elements in the package. Elements can be basically anything (except for packages and workspaces).

AUTOSAR 4 Package API
---------------------

Data Types
~~~~~~~~~~

 * :ref:`createImplementationDataType <datatype-createImplementationDataType>`