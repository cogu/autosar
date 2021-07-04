.. _ar4_base_SwDataDefPropsConditional:

SwDataDefPropsConditional
=========================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <SW-DATA-DEF-PROPS-CONDITIONAL>                                         |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.base                                                            |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     |                                                                         |
    +--------------+-------------------------------------------------------------------------+

This class is a collection of properties used by various data objects.

Note that not all of the attributes are useful all of the time. The special value *None* is used when an attribute is not active.

Factory Methods
---------------

Instances of SwDataDefPropsConditional are automatically being constructed when you are creating 
:ref:`Application <ar4_datatype_ApplicationDataType>` or :ref:`Implementation <ar4_datatype_ImplementationDataType>` data types 
using the :ref:`Package API <ar4_package_Package>`.

* :ref:`ar4_package_Package_createApplicationPrimitiveDataType`
* :ref:`ar4_package_Package_createApplicationArrayDataType`
* :ref:`ar4_package_Package_createApplicationRecordDataType`
* :ref:`ar4_package_Package_createImplementationArrayDataType`
* :ref:`ar4_package_Package_createImplementationDataType`
* :ref:`ar4_package_Package_createImplementationDataTypeRef`
* :ref:`ar4_package_Package_createImplementationDataTypePtr`
* :ref:`ar4_package_Package_createImplementationRecordDataType`

Constructor
-----------

.. py:method:: base.DataConstraint([baseTypeRef = None], [implementationTypeRef = None], [swAddressMethodRef = None], [swCalibrationAccess = None], [swImplPolicy = None], [swPointerTargetProps = None], [compuMethodRef = None], [dataConstraintRef = None], [unitRef = None], [parent = None])

    :param str baseTypeRef: Reference to :ref:`ar4_datatype_SwBaseType`.
    :param str implementationTypeRef: Reference to :ref:`ar4_datatype_ImplementationDataType`.
    :param str swAddressMethodRef: Reference to :ref:`ar4_element_SoftwareAddressMethod`.
    :param str swCalibrationAccess: :ref:`Software calibration access <ar4_base_SwDataDefPropsConditional_swCalibrationAccess>`.
    :param str swImplPolicy: :ref:`Software implementation policy <ar4_base_SwDataDefPropsConditional_swImplPolicy>`.
    :param swPointerTargetProps: Optional instance of SwPointerTargetProps
    :type swPointerTargetProps: :ref:`ar4_base_SwPointerTargetProps`.
    :param str compuMethodRef: Reference to :ref:`ar4_datatype_CompuMethod`.
    :param str dataConstraintRef: Reference to :ref:`ar4_datatype_DataConstraint`.
    :param str unitRef: Reference to :ref:`ar4_datatype_Unit`.
    :param parent: Parent package.
    :type parent: :ref:`ar4_package_Package`.

.. _ar4_base_SwDataDefPropsConditional_swCalibrationAccess:

swCalibrationAccess
~~~~~~~~~~~~~~~~~~~

+------------------------------+------------------------------------------------------------------------------------------------+
| Value                        | Description                                                                                    |
+==============================+================================================================================================+
| :literal:`None`              | No calibration access set                                                                      |
+------------------------------+------------------------------------------------------------------------------------------------+
| :literal:`""` (Empty string) | Create default calibration access value                                                        |
|                              | as set by Workspace.profile.swCalibrationAccessDefault                                         |
+------------------------------+------------------------------------------------------------------------------------------------+
| :literal:`"NOT-ACCESSIBLE"`  | The element will not be accessible by external tools                                           |
+------------------------------+------------------------------------------------------------------------------------------------+
| :literal:`"READ-ONLY"`       | Read only access                                                                               |
+------------------------------+------------------------------------------------------------------------------------------------+
| :literal:`"READ-WRITE"`      | Read-write access                                                                              |
+------------------------------+------------------------------------------------------------------------------------------------+

.. _ar4_base_SwDataDefPropsConditional_swImplPolicy:

swImplPolicy
~~~~~~~~~~~~

+--------------------------------+-----------------------------------------------------------------------------------------+
| Value                          | Description                                                                             |
+================================+=========================================================================================+
| :literal:`None`                | No policy set                                                                           |
+--------------------------------+-----------------------------------------------------------------------------------------+
| :literal:`"CONST"`             | Prevent implementation to modify the memory. Uses the "const" modifier in C.            |
+--------------------------------+-----------------------------------------------------------------------------------------+
| :literal:`"FIXED"`             | Data element is fixed and might be implemented as in place data such as a #define.      |
+--------------------------------+-----------------------------------------------------------------------------------------+
| :literal:`"MEASUREMENT-POINT"` | Data element is created for measurement purposes only.                                  |
+--------------------------------+-----------------------------------------------------------------------------------------+
| :literal:`"QUEUED"`            | Data element is queued and has event semantics. Data is processed in FIFO order.        |
+--------------------------------+-----------------------------------------------------------------------------------------+
| :literal:`"STANDARD"`          | Data element is non-queued and uses the "last is best" semantics                        |
+--------------------------------+-----------------------------------------------------------------------------------------+


Attributes
-----------


..  table::
    :align: left

    +---------------------------+---------------------------------------------+-----------------------------------+
    | Name                      | Type                                        | Description                       |
    +===========================+=============================================+===================================+
    | **baseTypeRef**           | None or str                                 |  <BASE-TYPE-REF>                  |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **compuMethodRef**        | None or str                                 |  <COMPU-METHOD-REF>               |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **dataConstraintRef**     | None or str                                 |  <DATA-CONSTR-REF>                |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **implementationTypeRef** | None or str                                 |  <IMPLEMENTATION-DATA-TYPE-REF>   |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **parent**                | None or :ref:`ar4_package_Package`          |  Parent package                   |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **swAddressMethodRef**    | None or str                                 |  <SW-ADDR-METHOD-REF>             |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **swCalibrationAccess**   | None or str                                 |  <SW-CALIBRATION-ACCESS>          |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **swImplPolicy**          | None or str                                 |  <SW-IMPL-POLICY>                 |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **swPointerTargetProps**  | None or :ref:`ar4_base_SwPointerTargetProps`|  <SW-POINTER-TARGET-PROPS>        |
    +---------------------------+---------------------------------------------+-----------------------------------+
    | **unitRef**               | None or str                                 |  <UNIT-REF>                       |
    +---------------------------+---------------------------------------------+-----------------------------------+


Public Properties
-----------------

..  table::
    :align: left

    +--------------------------+---------------+-------------+
    | Name                     | Type          | Access Type |
    +==========================+===============+=============+
    | **swImplPolicy**         | str           | Get, Set    |
    +--------------------------+---------------+-------------+

swImplPolicy
~~~~~~~~~~~~

Get or set current :ref:`software implementation policy <ar4_base_SwDataDefPropsConditional_swImplPolicy>`.


Public Methods
--------------

* :ref:`ar4_base_SwDataDefPropsConditional_hasAnyProp`

Method Description
------------------

.. _ar4_base_SwDataDefPropsConditional_hasAnyProp:

hasAnyProp    
~~~~~~~~~~

.. py:method:: SwDataDefPropsConditional.hasAnyProp()

    :rtype bool: :ref:`ar4_package_Package`.
    
    Returns True if any internal attribute is not None, else False
    The check excludes the parent attribute.