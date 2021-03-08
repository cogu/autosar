.. _ar4_datatype_ModeRequestTypeMap:

ModeRequestTypeMap
==================

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <MODE-REQUEST-TYPE-MAP>                              |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
    +--------------------+------------------------------------------------------+

Mapping from ModeGroupDeclaration to ImplementationDataType.

   
Factory Methods
---------------

* :ref:`DataTypeMappingSet.createModeRequestMapping <ar4_datatype_DataTypeMappingSet_createModeRequestMapping>`


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +-------------------------------+-------------------+---------------------------------------------------------+
    | Name                          | Type              | Description                                             |
    +===============================+===================+=========================================================+
    | **modeDeclarationGroupRef**   | str               | Reference to :ref:`ar4_mode_ModeDeclarationGroup`       |
    +-------------------------------+-------------------+---------------------------------------------------------+
    | **implementationDataTypeRef** | str               | Reference to :ref:`ar4_datatype_ImplementationDataType` |
    +-------------------------------+-------------------+---------------------------------------------------------+
