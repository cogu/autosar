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

Constructor
-----------

.. py:method:: datatype.ModeRequestTypeMap(modeDeclarationGroupRef, implementationDataTypeRef)

    :param str modeDeclarationGroupRef: Reference to :ref:`ar4_mode_ModeDeclarationGroup`.
    :param str implementationDataTypeRef: Reference to :ref:`ar4_datatype_ImplementationDataType`.


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +-------------------------------+-------------------+---------------------------------------------------------+
    | Name                          | Type              | Description                                             |
    +===============================+===================+=========================================================+
    | **modeDeclarationGroupRef**   | str               | <MODE-GROUP-REF>                                        |
    +-------------------------------+-------------------+---------------------------------------------------------+
    | **implementationDataTypeRef** | str               | <IMPLEMENTATION-DATA-TYPE-REF>                          |
    +-------------------------------+-------------------+---------------------------------------------------------+

Public Methods
--------------

This class does not have any additional methods.