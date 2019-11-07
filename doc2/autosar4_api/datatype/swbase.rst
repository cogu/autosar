.. _ar4_datatype_SwBaseType:

SwBaseType
==========

.. table::
   :align: left

   +--------------------+----------------------------------------------+
   | XML tag            | <SW-BASE-TYPE>                               |
   +--------------------+----------------------------------------------+
   | Module             | autosar.datatype                             |
   +--------------------+----------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element>` |
   +--------------------+----------------------------------------------+

Factory Methods
---------------

* :ref:`Package.createSwBaseType <ar4_package_Package_createSwBaseType>`
* :ref:`Package.createBaseType (alias) <ar4_package_Package_createSwBaseType>`


Attributes
----------

.. table::
   :align: left

   +--------------+-----------------------+------------------+
   | Type         |  Name                 |  Default Value   |
   +==============+=======================+==================+
   | str          | **category**          |  "FIXED_LENGTH"  |
   +--------------+-----------------------+------------------+
   | int          | **size**              |      \-          |
   +--------------+-----------------------+------------------+
   | str          | **typeEncoding**      |  None            |
   +--------------+-----------------------+------------------+
   | str          | **nativeDeclaration** |  None            |
   +--------------+-----------------------+------------------+


The SwBaseType is the lowest level of the AUTOSAR 4 type system. It defines a type in terms of bits and bytes.
All other data types eventually end up being defined by a base type.
