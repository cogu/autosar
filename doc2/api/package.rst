:noindex:

To be reworked
===============

The AUTOSAR Package class.

**Usage:**

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()
   package = ws.createPackage('ComponentType')
   
   print(ws.toXML())
   
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

Recommended packages in a workspace
-----------------------------------
   
   +--------------------+-------------------+------------------------+
   | Package Name       | Package Role Name | Package Contents       |
   +====================+===================+========================+
   | DataType           | DataType          | * DataType Elements    |
   |                    |                   | * CompuMethod Elements |
   |                    |                   | * Unit Elements        |
   +--------------------+-------------------+------------------------+      

Data Types
----------

Integer data types
~~~~~~~~~~~~~~~~~~   

.. py:method:: Package.createIntegerDataType(name :str, min=None, max=None, valueTable=None, offset=None, scaling=None, unit=None)
      
   Creates an instance of IntegerDataType and appends it to the *Package.elements* list.
   
   For enumeration type integers:
     
     use min (int), max (int), and possibly ValueTable (see example below).
     
   For physical unit data types:
   
      use offset (float), scaling (float) and unit (str).

Example: Create new enumeration data type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   
   import autosar

   ws = autosar.workspace()
   package=ws.createPackage("DataType", role="DataType")
   package.createSubPackage('DataTypeSemantics', role='CompuMethod')
   package.createSubPackage('DataTypeUnits', role='Unit')
   
   package.createIntegerDataType('InactiveActive_T',valueTable=[
         'InactiveActive_Inactive',
         'InactiveActive_Active',
         'InactiveActive_Error',
         'InactiveActive_NotAvailable'])
   
   ws.saveXML('DataTypes.arxml', packages=['DataType'])

Example: Create new physical unit data type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   
   ws = autosar.workspace()
   package=ws.createPackage("DataType", role="DataType")
   package.createSubPackage('DataTypeSemantics', role='CompuMethod')
   package.createSubPackage('DataTypeUnits', role='Unit')
   
   BatteryCurrent_T = package.createIntegerDataType('BatteryCurrent_T', min=0, max=65535, offset=-1600, scaling=0.05, unit="Ampere")
   BatteryCurrent_T.desc = "65024-65279 Error; 65280 - 65535 Not Available"
   
   ws.saveXML('DataTypes.arxml', packages=['DataType'])

Software Components (SWCs)
--------------------------

.. py:method:: Package.createApplicationSoftwareComponent(swcName : str, behaviorName=None, implementationName=None, multipleInstance=False)

   Creates an instance of ApplicationSoftwareComponent and appends it to the list of package elements.
   
   swcName: The name of the software component.
   
   optional arguments:
   
   * *behaviorName*: can be used to override the default name of the behavior instance that will be created with this object.
   * *implementationName*: can be used to override the default name of the implementation instance that will be created with this object.
   * *multipleInstance*: set to True in case this software component will need to support multiple instances.
      

.. _createModeDeclarationGroup:

Mode Declaration Groups
-----------------------

.. py:method:: Package.createModeDeclarationGroup(self, name, modeDeclarations, initialMode, category=None, adminData=None):

   Creates a new mode declaration group and appends it to the list of package elements
   
   *Arguments*
   
   * **name**: Name of the new group (string)
   * **modeDeclarations**: A list of mode names (list of strings)
   * **initialMode**: Selects which element from previous list shall be the initial mode (string)
   
   *Optional Arguments*
   
   * **category** (AUTOSAR4): Sets the category property (string). Example: category="ALPHABETIC_ORDER"
   * **adminData**: Sets additional adminData for the newly created object. Example: adminData={"SDG_GID": "edve:BSWM", "SD": "EcuM"}
