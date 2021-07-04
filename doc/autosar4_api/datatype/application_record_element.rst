.. _ar4_datatype_ApplicationRecordElement:

ApplicationRecordElement
========================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <APPLICATION-RECORD-ELEMENT>                                            |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.datatype                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
    +--------------+-------------------------------------------------------------------------+

ApplicationRecordElement describes one record element. To be used when creating :ref:`ar4_datatype_ApplicationRecordDataType`.

Usage
-----

..  include:: examples/usage_application_record_element.py
    :code: python3

Constructor
-----------

.. py:method:: datatype.ApplicationRecordElement(name, typeRef, [category = None], [parent=None], [adminData=None] )

    :param str name: Element name.
    :param str typeRef: Type reference.
    :param category: Category.
    :type category: None, str
    :param parent: Parent datatype.
    :type parent: None, :ref:`ar4_datatype_ApplicationRecordDataType`
    :param adminData: Optional AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`.

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+---------------------------+--------------------------------------+
    | Name                     | Type                      | Tag                                  |
    +==========================+===========================+======================================+
    | **typeRef**              | *str*                     | <TYPE-TREF>                          |
    +--------------------------+---------------------------+--------------------------------------+
