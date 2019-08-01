ImplementationDataType
======================

.. table::
   :align: left

   +--------------------+-------------------------------------------+
   | XML tag            | <IMPLEMENTATION-DATA-TYPE>                |
   +--------------------+-------------------------------------------+
   | Module             | autosar.datatype                          |
   +--------------------+-------------------------------------------+
   | Inherits           | autosar.element.Element                   |
   +--------------------+-------------------------------------------+
   
Implementation Data Types is a very generic container and can define almost any data type.
For ease of use this Python module offers several different factory methods to create the most
commonly used data types.

Factory Methods
---------------

* :ref:`Package.createImplementationDataTypeRef <package_createImplementationDataTypeRef>`
* :ref:`Package.createImplementationDataTypePtr <package_createImplementationDataTypePtr>`


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






