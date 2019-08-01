SwBaseType
==========

.. table::
   :align: left

   +--------------------+------------------------------------+
   | XML tag            | <SW-BASE-TYPE>                     |
   +--------------------+------------------------------------+
   | Module             | autosar.datatype                   |
   +--------------------+------------------------------------+
   | Inherits           | autosar.element.Element            |
   +--------------------+------------------------------------+

Factory Methods
---------------

* :ref:`Package.createSwBaseType <package_createSwBaseType>`
* :ref:`Package.createBaseType (alias) <package_createSwBaseType>`


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
