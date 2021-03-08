.. _ar4_datatype_DataTypeMappingSet:

DataTypeMappingSet
==================

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <DATA-TYPE-MAPPING-SET>                              |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
    +--------------------+------------------------------------------------------+

This class contains type mappings between ApplicationDataTypes and ImplementationDataTypes.
In addition, it can contain type mappings between ModeDeclarationGroups and ImplementationDataTypes.

Factory Methods
---------------

* :ref:`Package.createDataTypeMappingSet <ar4_package_Package_createDataTypeMappingSet>`


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +--------------------------+-------------------+-----------------------------------------------------+
    | Name                     | Type              | Description                                         |
    +==========================+===================+=====================================================+
    | **applicationTypeMap**   | dict              | Application data type mappings                      |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **modeRequestMap**       | dict              | Mode request mappings                               |
    +--------------------------+-------------------+-----------------------------------------------------+

The ARXML definition uses lists containing mappings while Python uses dictionaries.
For the **applicationTypeMap** dictionary, each key is a reference to an application data type and each value
is a reference to an implementation data type.
Likewise for the *modeRequestMap* dictionary, each key is a reference to a mode declaration group and each value
is a reference to an implementation data type.

Public Methods
--------------

* :ref:`ar4_datatype_DataTypeMappingSet_createDataTypeMapping`
* :ref:`ar4_datatype_DataTypeMappingSet_createModeRequestMapping`
* :ref:`ar4_datatype_DataTypeMappingSet_add`
* :ref:`ar4_datatype_DataTypeMappingSet_getDataTypeMapping`
* :ref:`ar4_datatype_DataTypeMappingSet_getModeRequestMapping`
* :ref:`ar4_datatype_DataTypeMappingSet_findMappedDataTypeRef`
* :ref:`ar4_datatype_DataTypeMappingSet_findMappedModeRequestRef`
* :ref:`ar4_datatype_DataTypeMappingSet_findMappedDataType`
* :ref:`ar4_datatype_DataTypeMappingSet_findMappedModeRequest`

Method Description
--------------------

.. _ar4_datatype_DataTypeMappingSet_createDataTypeMapping:

createDataTypeMapping
~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.createDataTypeMapping(applicationDataTypeRef : str, implementationDataTypeRef : str)

    Creates a new type mapping between an application type (reference) and implementation data type (reference).
    The created mapping is added to the internal applicationTypeMap dictionary.

    :param str applicationDataTypeRef: Reference to an ApplicationDataType
    :param str implementationDataTypeRef: Reference to an :ref:`ar4_datatype_ImplementationDataType`

.. _ar4_datatype_DataTypeMappingSet_createModeRequestMapping:

createModeRequestMapping
~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.createModeRequestMapping(modeDeclarationGroupRef : str, implementationDataTypeRef : str)

    Creates a new type mapping between a mode declaration group (reference) and implementation data type (reference).
    The created mapping is added to the internal modeRequestMap dictionary.

    :param str modeDeclarationGroupRef: Reference to a :ref:`ar4_mode_ModeDeclarationGroup`
    :param str implementationDataTypeRef: Reference to an :ref:`ar4_datatype_ImplementationDataType`

.. _ar4_datatype_DataTypeMappingSet_add:

add
~~~

.. method:: DataTypeMappingSet.add(item)

    Adds a user-created mapping to this mapping set.
    If the item is of type :ref:`ar4_datatype_DataTypeMap` it gets inserted into to the applicationTypeMap dictionary.
    Likewise, if the item is of type :ref:`ar4_datatype_ModeRequestTypeMap` it gets inserted into to the modeRequestMap dictionary.

    :param item: Reference to an ApplicationDataType
    :type item: :ref:`ar4_datatype_DataTypeMap` or :ref:`ar4_datatype_ModeRequestTypeMap`

.. _ar4_datatype_DataTypeMappingSet_getDataTypeMapping:

getDataTypeMapping
~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.getDataTypeMapping(applicationDataTypeRef : str)

    Returns the mapping object that is currently associated with the given application data type reference.
    If the reference string is not found in the internal applicationTypeMap dictionary, None is returned.

    :param str applicationDataTypeRef: Reference to an :ref:`ar4_datatype_ApplicationDataType`
    :rtype: :ref:`ar4_datatype_DataTypeMappingSet` or None

.. _ar4_datatype_DataTypeMappingSet_getModeRequestMapping:

getModeRequestMapping
~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.getModeRequestMapping(modeDeclarationGroupRef : str)

    Returns the mapping object that is currently associated with the given mode declaration group reference.
    If the reference string is not found in the internal modeRequestMap dictionary, None is returned.

    :param str modeDeclarationGroupRef: Reference to a
    :rtype: :ref:`ar4_mode_ModeDeclarationGroup` or None

.. _ar4_datatype_DataTypeMappingSet_findMappedDataTypeRef:

findMappedDataTypeRef
~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.findMappedDataTypeRef(applicationDataTypeRef : str)

    Same as :ref:`ar4_datatype_DataTypeMappingSet_getDataTypeMapping` but instead returns the reference to the mapped implementation data type.
    Returns None in case the application data type reference is not part of the internal applicationTypeMap dictionary.

    :param str applicationDataTypeRef: Reference to an :ref:`ar4_datatype_ApplicationDataType`
    :rtype: str

.. _ar4_datatype_DataTypeMappingSet_findMappedModeRequestRef:

findMappedModeRequestRef
~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.findMappedModeRequestRef(modeDeclarationGroupRef : str)

   Same as :ref:`ar4_datatype_DataTypeMappingSet_getModeRequestMapping` but instead returns the reference to the mapped implementation data type.
   Returns None in case the mode declaration group reference is not part of the internal modeRequestMap dictionary.

    :param str applicationDataTypeRef: :ref:`ar4_mode_ModeDeclarationGroup`
    :rtype: str

.. _ar4_datatype_DataTypeMappingSet_findMappedDataType:

findMappedDataType
~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.findMappedDataType(applicationDataTypeRef : str)

   Same as :ref:`ar4_datatype_DataTypeMappingSet_findMappedDataTypeRef` but instead returns the
   referenced to :ref:`ar4_datatype_ImplementationDataType` object.

    :param str applicationDataTypeRef: Reference to a :ref:`ar4_datatype_ApplicationDataType`
    :rtype: :ref:`ar4_datatype_ImplementationDataType`

.. _ar4_datatype_DataTypeMappingSet_findMappedModeRequest:

findMappedModeRequest
~~~~~~~~~~~~~~~~~~~~~

.. method:: DataTypeMappingSet.findMappedModeRequest(modeDeclarationGroupRef : str)

   Same as :ref:`ar4_datatype_DataTypeMappingSet_findMappedModeRequestRef` but instead returns the
   referenced to :ref:`ar4_datatype_ImplementationDataType` object.

   :param str modeDeclarationGroupRef: Reference to a :ref:`ar4_mode_ModeDeclarationGroup`
   :rtype: :ref:`ar4_datatype_ImplementationDataType`