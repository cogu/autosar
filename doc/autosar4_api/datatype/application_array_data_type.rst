.. _ar4_datatype_ApplicationArrayDataType:

ApplicationArrayDataType
========================

.. table::
    :align: left

    +--------------+--------------------------------------------------------------------------------+
    | XML tag      | <APPLICATION-ARRAY-DATA-TYPE>                                                  |
    +--------------+--------------------------------------------------------------------------------+
    | Module       | autosar.datatype                                                               |
    +--------------+--------------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.datatype.ApplicationDataType <ar4_datatype_ApplicationDataType>` |
    +--------------+--------------------------------------------------------------------------------+

Implementation of application array data type.

Usage
-----

..  include:: examples/usage_application_array_data_type.py
    :code: python3

Factory Methods
---------------

* :ref:`ar4_package_Package_createApplicationArrayDataType`

Constructor
-----------

.. py:method:: datatype.ApplicationArrayDataType(name, element, variantProps = None, category = 'ARRAY', parent=None, adminData=None)

    :param str name: ShortName.
    :param element: Array element.
    :type element: :ref:`ar4_datatype_ApplicationArrayElement`
    :param variantProps: Variant properties.
    :type arraySize: None, :ref:`ar4_base_SwDataDefPropsConditional`
    :param category: Category string.
    :type category: None, str
    :param parent: Parent package.
    :type parent: None, :ref:`ar4_package_Package`
    :param adminData: Optional AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`.

Attributes
-----------

For inherited attributes see :ref:`autosar.datatype.ApplicationDataType <ar4_datatype_ApplicationDataType>`.
