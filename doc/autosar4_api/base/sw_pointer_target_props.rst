.. _ar4_base_SwPointerTargetProps:

SwPointerTargetProps
====================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <SW-POINTER-TARGET-PROPS>                                               |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.base                                                            |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     |                                                                         |
    +--------------+-------------------------------------------------------------------------+

This class is used to describe properties of pointer data objects.
The attributes describe the target category and other properties of the target/parent object.

Factory Methods
---------------

Instance(s) of this class is implictly created when creating ImplementationDataTypes of pointer category.

* :ref:`ar4_package_Package_createImplementationDataTypePtr`

Constructor
-----------

.. py:method:: base.SwPointerTargetProps([targetCategory = None], [variants = None])

:param str targetCategory: target category.
:param variants: Single instance of SwDataDefPropsConditional or list of SwDataDefPropsConditionals.
:type variants: list of :ref:`ar4_base_SwDataDefPropsConditional` or single :ref:`ar4_base_SwDataDefPropsConditional`.

Attributes
-----------

..  table::
    :align: left

    +--------------------------+---------------------------+---------------------------------------------------+
    | Name                     | Type                      | Description                                       |
    +==========================+===========================+===================================================+
    | **targetCategory**       | *str*                     | Target category                                   |
    +--------------------------+---------------------------+---------------------------------------------------+
    | **variants**             | *list*                    | List of :ref:`ar4_base_SwDataDefPropsConditional` |
    +--------------------------+---------------------------+---------------------------------------------------+

targetCategory
~~~~~~~~~~~~~~

* In case of a data pointer, it shall specify the category of the referenced data.
* In case of a function pointer, it could be used to denote the category of the referenced module entry.

Public Methods
--------------

This class does not have any additional methods.

