.. _ar4_datatype_DataTypeMap:

DataTypeMap
===========

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <DATA-TYPE-MAP>                                      |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
    +--------------------+------------------------------------------------------+

Mapping from ApplicationDataType to ImplementationDataType.

   
Factory Methods
---------------

* :ref:`DataTypeMappingSet.createDataTypeMapping <ar4_datatype_DataTypeMappingSet_createDataTypeMapping>`


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +-------------------------------+-------------------+---------------------------------------------------------+
    | Name                          | Type              | Description                                             |
    +===============================+===================+=========================================================+
    | **applicationDataTypeRef**    | str               | Reference to :ref:`ar4_datatype_ApplicationDataType`    |
    +-------------------------------+-------------------+---------------------------------------------------------+
    | **implementationDataTypeRef** | str               | Reference to :ref:`ar4_datatype_ImplementationDataType` |
    +-------------------------------+-------------------+---------------------------------------------------------+
