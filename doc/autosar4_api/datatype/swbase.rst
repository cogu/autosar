.. _ar4_datatype_SwBaseType:

SwBaseType
==========

.. table::
   :align: left

   +--------------------+------------------------------------------------------+
   | XML tag            | <SW-BASE-TYPE>                                       |
   +--------------------+------------------------------------------------------+
   | Module             | autosar.datatype                                     |
   +--------------------+------------------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------------+------------------------------------------------------+

The SwBaseType is the lowest level of the AUTOSAR 4 type system. It defines a type in terms of bits and bytes.
All other data types eventually end up being defined by a base type.


Usage
-----

..  include:: examples/usage_sw_base_type.py
    :code: python3

Factory Methods
---------------

* :ref:`Package.createSwBaseType <ar4_package_Package_createSwBaseType>`
* :ref:`Package.createBaseType (alias) <ar4_package_Package_createSwBaseType>`


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
   :align: left

   +--------------------------+-------------------+-----------------------------------------------------+
   | Name                     | Type              | Description                                         |
   +==========================+===================+=====================================================+
   | **category**             | str               | Application data type mappings                      |
   +--------------------------+-------------------+-----------------------------------------------------+
   | **size**                 | None or int       | type size in bits                                   |
   +--------------------------+-------------------+-----------------------------------------------------+
   | **typeEncoding**         | None or str       | Optional type encoding                              |
   +--------------------------+-------------------+-----------------------------------------------------+
   | **nativeDeclaration**    | None or str       | Optional native declaration type name               |
   +--------------------------+-------------------+-----------------------------------------------------+

Attribute Defaults
------------------

   +-----------------------+------------------+
   |  Name                 |  Default Value   |
   +=======================+==================+
   | **category**          | "FIXED_LENGTH"   |
   +-----------------------+------------------+
   | **size**              |  None            |
   +-----------------------+------------------+
   | **typeEncoding**      |  None            |
   +-----------------------+------------------+
   | **nativeDeclaration** |  None            |
   +-----------------------+------------------+