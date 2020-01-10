.. _ar4_element_ParameterDataPrototype:

ParameterDataPrototype
======================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <PARAMETER-DATA-PROTOTYPE>                                              |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.element                                                         |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
    +--------------+-------------------------------------------------------------------------+

Represents a parameter data protoype.

.. note::

    This class replaces autosar.portinterface.Parameter as well as autosar.behavior.ParameterDataPrototype


Usage
-----

.. code-block:: python

    ws = autosar.workspace(version="4.2.2")
    ws.createPackage('Contraints', role='DataConstraint')
    basetypes = ws.createPackage('BaseTypes')
    uint8_base = basetypes.createBaseType('uint8', 8, None)
    package = ws.createPackage('DataTypes')
    int8_type = package.createImplementationDataType('uint8', uint8_base.ref, 0, 255)
    package = ws.createPackage('PortInterfaces')
    parameter = autosar.element.ParameterDataPrototype('v', uint8_type.ref)

Factory Methods
---------------

* autosar.ParameterDataPrototype

Constructor
-----------

..  py:method:: ParameterDataPrototype(name, typeRef, [swAddressMethodRef = None], [swCalibrationAccess = None], [initValue = None], [parent=None], [adminData=None])

    :param str name: ShortName identifer
    :param str typeRef: Type reference
    :param str swAddressMethodRef: Reference to SoftwareAddressMethod
    :param str swCalibrationAccess: Calibration access setting
    :param str initValue: Optional init value (TBD)
    :param parent: Internal use only (leave as None)
    :param adminData: Optional AdminData object

**swCalibrationAccess**

* None: No calibration access set
* \\"\\" (Empty string): Create default calibration access value as set by Workspace.profile.swCalibrationAccessDefault
* \\"NOT-ACCESSIBLE\\": The element will not be accessible by external tools
* \\"READ-ONLY\\": Read only access
* \\"READ-WRITE\\": Read-write access

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+----------------------------------------------+--------------------------------------+
    | Name                     | Type                                         | Description                          |
    +==========================+==============================================+======================================+
    | **typeRef**              | *str*                                        | Reference to datatype                |
    +--------------------------+----------------------------------------------+--------------------------------------+
    | **swAddressMethodRef**   | *None or str*                                | Reference to SoftwareAddressMethod   |
    +--------------------------+----------------------------------------------+--------------------------------------+
    | **swCalibrationAccess**  | *None or str*                                | Software calibration access          |
    +--------------------------+----------------------------------------------+--------------------------------------+
    | **initValue**            | *Object derived from autosar.value.ValueAR4* | Software calibration access          |
    +--------------------------+----------------------------------------------+--------------------------------------+

