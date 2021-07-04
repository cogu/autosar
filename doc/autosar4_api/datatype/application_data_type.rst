.. _ar4_datatype_ApplicationDataType:

ApplicationDataType
===================

.. table::
   :align: left

   +--------------------+------------------------------------------------------+
   | XML tag            |  -                                                   |
   +--------------------+------------------------------------------------------+
   | Module             | autosar.datatype                                     |
   +--------------------+------------------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------------+------------------------------------------------------+

Base class for AUTOSAR application data types. Types that derive from this class are:

* :ref:`ar4_datatype_ApplicationPrimitiveDataType`
* :ref:`ar4_datatype_ApplicationArrayDataType`
* :ref:`ar4_datatype_ApplicationRecordDataType`

Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +-----------------------------+---------------------------------------------------+-----------------------+
    | Name                        | Type                | Description                                         |
    +=============================+===================================================+=======================+
    | **variantProps**            | list of :ref:`ar4_base_SwDataDefPropsConditional` | List of properties    |
    +-----------------------------+---------------------------------------------------+-----------------------+

Properties
----------

..  table::
    :align: left

    +--------------------------+---------------------------+-------------+
    | Name                     | Type                      | Access Type |
    +==========================+===========================+=============+
    | **compuMethodRef**       | *str*                     | Get         |
    +--------------------------+---------------------------+-------------+
    | **dataConstraintRef**    | *str*                     | Get         |
    +--------------------------+---------------------------+-------------+
    | **unitRef**              | *str*                     | Get         |
    +--------------------------+---------------------------+-------------+

compuMethodRef
~~~~~~~~~~~~~~

Returns the :ref:`ar4_datatype_CompuMethod` reference from the first item of the variantProps list. 
Raises Runtime error if variantProps list is empty.

dataConstraintRef
~~~~~~~~~~~~~~~~~

Returns the :ref:`ar4_datatype_DataConstraint` reference from the first item of the variantProps list.
Raises Runtime error if variantProps list is empty.


unitRef
~~~~~~~

Returns the :ref:`ar4_datatype_Unit` reference from the first item of the variantProps list.
Raises Runtime error if variantProps list is empty.

