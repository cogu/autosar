.. _ar4_datatype_ImplementationDataType:

ImplementationDataType
======================

.. table::
   :align: left

   +--------------------+----------------------------------------------+
   | XML tag            | <IMPLEMENTATION-DATA-TYPE>                   |
   +--------------------+----------------------------------------------+
   | Module             | autosar.datatype                             |
   +--------------------+----------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element>` |
   +--------------------+----------------------------------------------+

Implementation Data Types is a very generic container and can define almost any data type.
For ease of use this Python module offers several different factory methods to create the most
commonly used data types.

Factory Methods
---------------

* :ref:`Package.createImplementationDataType <ar4_package_Package_createImplementationDataType>`
* :ref:`Package.createImplementationDataTypeRef <ar4_package_Package_createImplementationDataTypeRef>`
* :ref:`Package.createImplementationDataTypePtr <ar4_package_Package_createImplementationDataTypePtr>`

Attributes
----------

..  table::
    :align: left

    +-----------------------------+---------------------+-----------------------------+
    | Name                        | Type                | Description                 |
    +=============================+=====================+=============================+
    | **dynamicArraySizeProfile** | None or str         |                             |
    +-----------------------------+---------------------+-----------------------------+
    | **subElements**             | list                |                             |
    +-----------------------------+---------------------+-----------------------------+
    | **symbolProps**             | None or SymbolProps |                             |
    +-----------------------------+---------------------+-----------------------------+
    | **typeEmitter**             | None or str         |                             |
    +-----------------------------+---------------------+-----------------------------+
    | **variantProps**            | list                |                             |
    +-----------------------------+---------------------+-----------------------------+

Properties
----------

.. table::
   :align: left

   +--------------------+-------------------------------------------+
   | int                | **arraySize**                             |
   +--------------------+-------------------------------------------+
   | str                | **implementationTypeRef**                 |
   +--------------------+-------------------------------------------+
   | str                | **implementationTypeRef**                 |
   +--------------------+-------------------------------------------+
   | str                | **baseTypeRef**                           |
   +--------------------+-------------------------------------------+
   | str                | **dataConstraintRef**                     |
   +--------------------+-------------------------------------------+
   | str                | **compuMethodRef**                        |
   +--------------------+-------------------------------------------+
   | str                | **compuMethodRef**                        |
   +--------------------+-------------------------------------------+

Public Methods
--------------

.. table::
   :align: left

   +--------------------+-------------------------------------------+
   | void               | **setSymbolProps**                        |
   +--------------------+-------------------------------------------+
