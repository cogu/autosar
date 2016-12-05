Package
*******

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
      
Attributes
----------
      
.. py:attribute:: Package.name
   
   The name of the package

.. py:attribute:: Package.elements
   
   List of elements in the package. Elements can be basically anything (except for packages and workspaces).
   
   Currently implemented element types:

Convenience Methods
-------------------

The Package class has many convencienc methods for creating various elements, they are documented in the following sections.
   
DataTypes 
---------
   
.. py:method:: Package.createIntegerDataType(name :str,min=None,max=None,valueTable=None,offset=None, scaling=None, unit=None)
      
   Creates an instance of IntegerDataType and appends it to the list of package elements.
   
   For enumeration type integers:
     
     use min (int), max (int), and possibly ValueTable (described later)     
     
   For integer that has physical representation:
   
      use offset (int), scaling (int) and unit (str).

ApplicationSoftwareComponent
----------------------------

.. py:method:: Package.createApplicationSoftwareComponent(swcName : str,behaviorName=None,implementationName=None,multipleInstance=False)

   Creates an instance of ApplicationSoftwareComponent and appends it to the list of package elements.
   
   swcName: The name of the software component.
   
   optional arguments:
   
   * *behaviorName*: can be used to override the default name of the behavior instance that will be created with this object.
   * *implementationName*: can be used to override the default name of the implementation instance that will be created with this object.
   * *multipleInstance*: set to True in case this software component will need to support multiple instances.
      

