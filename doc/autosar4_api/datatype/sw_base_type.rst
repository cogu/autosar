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
* :ref:`Package.createBaseType (alias) <ar4_package_Package_createBaseType>`

Constructor
-----------

.. py:method:: datatype.SwBaseType(name, [size = None], [typeEncoding = None], [nativeDeclaration = None], [category = 'FIXED_LENGTH'], [parent = None], [adminData = None])

   :param str name: Short name.
   :param size: Type size in bits.
   :type size: None, int
   :param typeEncoding: Type encoding (e.g. "2C" for Two's-complement encoding).
   :type typeEncoding: None, str
   :param nativeDeclaration: Native declaration (name of type in C programming language).
   :param category: Category string.
   :type category: None, str
   :param parent: parent package.
   :type parent: :ref:`ar4_package_Package`
   :param adminData: Optional AdminData.
   :type adminData: None, :ref:`ar4_base_AdminData`.


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
   :align: left

   +--------------------------+-------------------+------------------------------------------------+
   | Name                     | Type              | Description                                    |
   +==========================+===================+================================================+      
   | **nativeDeclaration**    | None, str         | <NATIVE-DECLARATION>                           |
   +--------------------------+-------------------+------------------------------------------------+
   | **size**                 | None, int         | <BASE-TYPE-SIZE>                               |
   +--------------------------+-------------------+------------------------------------------------+
   | **typeEncoding**         | None, str         | <BASE-TYPE-ENCODING>                           |
   +--------------------------+-------------------+------------------------------------------------+
