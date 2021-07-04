.. _ar4_datatype_ApplicationPrimitiveDataType:

ApplicationPrimitiveDataType
============================

.. table::
    :align: left

    +--------------+--------------------------------------------------------------------------------+
    | XML tag      | <APPLICATION-PRIMITIVE-DATA-TYPE>                                              |
    +--------------+--------------------------------------------------------------------------------+
    | Module       | autosar.datatype                                                               |
    +--------------+--------------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.datatype.ApplicationDataType <ar4_datatype_ApplicationDataType>` |
    +--------------+--------------------------------------------------------------------------------+

Primitive application data type.

Usage
-----

..  include:: examples/usage_application_primitive_data_type.py
    :code: python3

Factory Methods
---------------

* :ref:`ar4_package_Package_createApplicationPrimitiveDataType`

Constructor
-----------

.. py:method:: datatype.ApplicationPrimitiveDataType(name, [variantProps = None], [category = None], [parent = None], [adminData = None])

    :param str name: Short name.
    :param variantProps: variant properties.
    :type variantProps: None, :ref:`ar4_base_SwDataDefPropsConditional`, list
    :param category: Category string.
    :type category: None, str
    :param parent: Parent package.
    :type parent: None, :ref:`ar4_package_Package`
    :param adminData: Admin data.
    :type adminData: None, :ref:`ar4_base_AdminData`

Attributes
-----------

For inherited attributes see :ref:`autosar.datatype.ApplicationDataType <ar4_datatype_ApplicationDataType>`.