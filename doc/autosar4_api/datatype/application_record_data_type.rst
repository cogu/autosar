.. _ar4_datatype_ApplicationRecordDataType:

ApplicationRecordDataType
=========================

.. table::
    :align: left

    +--------------+--------------------------------------------------------------------------------+
    | XML tag      | <APPLICATION-RECORD-DATA-TYPE>                                                 |
    +--------------+--------------------------------------------------------------------------------+
    | Module       | autosar.datatype                                                               |
    +--------------+--------------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.datatype.ApplicationDataType <ar4_datatype_ApplicationDataType>` |
    +--------------+--------------------------------------------------------------------------------+

Implementation of application record data type.

Usage
-----

..  include:: examples/usage_application_record_data_type.py
    :code: python3

Factory Methods
---------------

* :ref:`ar4_package_Package_createApplicationRecordDataType`
    
Constructor
-----------

.. py:method:: datatype.ApplicationRecordDataType(name, [elements = None], [variantProps = None], [category = None], [parent = None], [adminData = None])

    :param str name: ShortName.
    :param elements: List of record elements.
    :type elements: None, list of :ref:`ar4_datatype_ApplicationRecordElement`
    :param variantProps: Additional type properties.
    :type variantProps: None, :ref:`ar4_base_SwDataDefPropsConditional`
    :param category: Category string.
    :type category: None, str
    :param parent: Parent package.
    :type parent: None, :ref:`ar4_package_Package`
    :param adminData: AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`

Attributes
-----------

For inherited attributes see :ref:`autosar.datatype.ApplicationDataType <ar4_datatype_ApplicationDataType>`.

..  table::
    :align: left

    +--------------------------+---------------------------+--------------------------------------+
    | Name                     | Type                      | Tag                                  |
    +==========================+===========================+======================================+
    | **elements**             | *list*                     | <ELEMENTS>                          |
    +--------------------------+---------------------------+--------------------------------------+

Public Methods
--------------

* :ref:`ar4_datatype_ApplicationRecordDataType_append`
* :ref:`ar4_datatype_ApplicationRecordDataType_createElement`

Method Description
------------------

.. _ar4_datatype_ApplicationRecordDataType_append:

append
~~~~~~

.. py:method:: ApplicationRecordDataType.append(element)

    Appends element to elements list.

    :param element: element.
    :type element: :ref:`ar4_datatype_ApplicationRecordElement`

.. _ar4_datatype_ApplicationRecordDataType_createElement:

createElement
~~~~~~~~~~~~~

.. py:method:: ApplicationRecordDataType.createElement(name, typeRef, [category = 'VALUE'], [adminData = None])

    Creates a new instance of :ref:`ar4_datatype_ApplicationRecordElement` and appends it to internal elements list.

    :param str name: Element name.
    :param str typeRef: Type reference.
    :param category: Category string.
    :type category: None, str
    :param adminData: Optional AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`.
