.. _ar4_Roles:

Package Roles
=============

Package roles are used as a hint to Python, telling it what AUTOSAR package contains what kind of element.
Using this mechanism allows the AUTOSAR Python package to implictly find or create elements and place them into the right package.
AUTOSAR package roles are not stored anywhere in the XML. You have to explicitly set them programmatically while either creating or loading AUTOSAR packages.

Role Types
----------

.. table::
   :align: left

   +-------------------+---------------------------+
   | Package Role Name |  Element Types            |
   +===================+===========================+
   | DataType          | Data Types                |
   +-------------------+---------------------------+
   | Constant          | Constants                 |
   +-------------------+---------------------------+
   | ComponentType     | Components (prototypes)   |
   +-------------------+---------------------------+
   | ModeDclrGroup     | Mode Declaration Groups   |
   +-------------------+---------------------------+
   | CompuMethod       | Computational Methods     |
   +-------------------+---------------------------+
   | DataConstraint    | Data Constraints          |
   +-------------------+---------------------------+

Examples
--------

Example 1 - Setting roles on package creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates how to assign a role when the package is created.
By assigning both *CompuMethod* and *DataConstraint* allows the :ref:`ar4_package_Package_createImplementationDataType` method to 
implictly create associated :ref:`ar4_datatype_CompuMethod` and :ref:`ar4_datatype_DataConstraint` objects.

.. include:: examples/setting_roles_on_package_creation.py
    :code: python3



Example 2 - Setting roles while loading ARXML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example uses the saved XML from previous example and reassigns the roles while the XML is loading.

.. include:: examples/setting_roles_on_load_xml.py
    :code: python3


Example 3 - Pushing and popping roles on the roles stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working in large scale scale projects it can sometimes be beneficial to temporarily overrride the currently selected roles while inside a Python function.
For this purpose you can use the :ref:`ar4_workspace_Workspace_pushRoles` and :ref:`ar4_workspace_Workspace_popRoles` methods from the :ref:`ar4_workspace` class.

The next example has two functions:

* create_platform_types
* create_component_data_types
  
By calling *pushRoles* in the beginning and *popRoles* at the end of each function we prevent roles to still remain active after each function call.
In this example, we use this mechanism to allow *AUTOSAR_Platform* and *DataTypes* to have independent CompuMethod and DataConstraint sub-packages while we are
creating :ref:`ImplementationDataTypes <ar4_datatype_ImplementationDataType>`.

.. include:: examples/using_role_stack.py
    :code: python3

