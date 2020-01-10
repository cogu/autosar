.. _ar4_element_DataElement:

DataElement
===========

.. table::
   :align: left

   +--------------+------------------------------------------------------+
   | XML tag      | <DATA-ELEMENT>                                       |
   +--------------+------------------------------------------------------+
   | Module       | autosar.element                                      |
   +--------------+------------------------------------------------------+
   | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------+------------------------------------------------------+

DataElements are commonly used in :ref:`ar4_portinterface_SenderReceiverInterface` but they sometimes are used for other purposes.

Constructor
-----------

..  py:method:: DataElement(name, typeRef, [isQueued = False], [swAddressMethodRef = None], [swCalibrationAccess = None], [swImplPolicy = None], [category = None], [parent = None], [adminData = None])

    :param str name: Short-name identifer
    :param str typeRef: Type reference
    :param bool isQueued: Queued property
    :param str swAddressMethodRef: Reference to SoftwareAddressMethod
    :param str swCalibrationAccess: Calibration access setting
    :param str swImplPolicy: Implementation policy
    :param str category: Category string
    :param parent: Only used internally (leave as None)
    :param adminData: Optional AdminData object

**swCalibrationAccess**

TBD

**swImplPolicy**

* CONST
* FIXED
* MEASUREMENT-POINT
* QUEUED
* STANDARD

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+-------------------+-----------------------------------------------------+
    | Name                     | Type              | Description                                         |
    +==========================+===================+=====================================================+
    | **dataConstraintRef**    | *None* or *str*   | Reference to DataConstraint                         |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **isQueued**             | *bool*            | Queued property                                     |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **swAddressMethodRef**   | *None* or *str*   | Reference to SoftwareAddressMethod                  |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **swCalibrationAccess**  | *None* or *str*   | Calibration access setting                          |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **typeRef**              | *str*             | Data type reference                                 |
    +--------------------------+-------------------+-----------------------------------------------------+

.. note::

    It might be better idea to change DataElement to have a single instance of autosar.base.SwDataDefPropsConditional.
    This will remove some duplicated attributes found in this class.


Properties
----------

..  table::
    :align: left

    +--------------------------+-------------------+-----------------------------------------------------+
    | Name                     | Type              | Description                                         |
    +==========================+===================+=====================================================+
    | **swImplPolicy**         | *None* or *str*   | Software Implementation Policy                      |
    +--------------------------+-------------------+-----------------------------------------------------+

Public Methods
--------------

* :ref:`ar4_element_DataElement_setProps`

Method Description
------------------

.. _ar4_element_DataElement_setProps:

setProps
~~~~~~~~

.. py:method:: DataElement.setProps(props)

    :param props: Properties object
    :type props: autosar.base.SwDataDefPropsConditional

    Updates the following attributes/properties from the given props object

    * dataConstraintRef
    * swAddressMethodRef
    * swCalibrationAccess
    * swImplPolicy
