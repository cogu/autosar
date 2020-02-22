.. _ar4_package_Package:

Package
=======

.. table::
   :align: left

   +--------------------+-------------------------------------------+
   | XML tag            | <AR-PACKAGE>                              |
   +--------------------+-------------------------------------------+
   | Module             | autosar.package                           |
   +--------------------+-------------------------------------------+
   | Inherits           |                                           |
   +--------------------+-------------------------------------------+

An AUTOSAR package is a container for elements.
Elements are almost everything else that are not packages.
In addition to elements each package can also contain zero or more sub-packages.

Usage
-----

.. code-block:: python

   import autosar

   ws = autosar.workspace("4.2.2")
   package = ws.createPackage('ComponentTypes', role = 'ComponentType')

Attributes
----------

..  table::
    :align: left

    +-----------------+--------------------+-----------------------------+
    | Name            | Type               | Description                 |
    +=================+====================+=============================+
    | **name**        | str                | Name of the package         |
    +-----------------+--------------------+-----------------------------+
    | **elements**    | list[Elements]     | List of elements            |
    +-----------------+--------------------+-----------------------------+
    | **subPackages** | list[Package]      | List of sub-packages        |
    +-----------------+--------------------+-----------------------------+
    | **role**        | str                | Package role                |
    +-----------------+--------------------+-----------------------------+

.. _ar4_package_Package_roles:

Package Roles
-------------

..  table::
    :align: left

    +------------------+--------------------------------------------+
    | *Constant*       | Main container for Constants               |
    +------------------+--------------------------------------------+
    | *ComponentType*  | Main container for Components              |
    +------------------+--------------------------------------------+
    | *CompuMethod*    | Main container for Computational Methods   |
    +------------------+--------------------------------------------+
    | *DataConstraint* | Main container for Data Constraints        |
    +------------------+--------------------------------------------+
    | *DataType*       | Main container for Data Types              |
    +------------------+--------------------------------------------+
    | *ModeDclrGroup*  | Main container for Mode Declaration Groups |
    +------------------+--------------------------------------------+
    | *PortInterface*  | Main container for Port Interfaces         |
    +------------------+--------------------------------------------+
    | *Unit*           | Main container for Units                   |
    +------------------+--------------------------------------------+


Public Methods
--------------

**ComponentType**

* :ref:`ar4_package_Package_createApplicationSoftwareComponent`
* :ref:`ar4_package_Package_createComplexDeviceDriverComponent`
* :ref:`ar4_package_Package_createCompositionComponent`
* :ref:`ar4_package_Package_createNvBlockComponent`
* :ref:`ar4_package_Package_createServiceComponent`

**CompuMethod**

* :ref:`ar4_package_Package_createCompuMethodConst`
* :ref:`ar4_package_Package_createCompuMethodLinear`
* :ref:`ar4_package_Package_createCompuMethodRational`
* :ref:`ar4_package_Package_createCompuMethodRationalPhys`

**Constant**

* :ref:`ar4_package_Package_createApplicationValueConstant`
* :ref:`ar4_package_Package_createConstant`
* :ref:`ar4_package_Package_createNumericalValueConstant`

**DataConstraint**

* :ref:`ar4_package_Package_createInternalDataConstraint`
* :ref:`ar4_package_Package_createPhysicalDataConstraint`

**DataType**

* :ref:`ar4_package_Package_createApplicationArrayDataType`
* :ref:`ar4_package_Package_createApplicationPrimitiveDataType`
* :ref:`ar4_package_Package_createApplicationRecordDataType`
* :ref:`ar4_package_Package_createBaseType`
* :ref:`ar4_package_Package_createImplementationArrayDataType`
* :ref:`ar4_package_Package_createImplementationDataType`
* :ref:`ar4_package_Package_createImplementationDataTypeRef`
* :ref:`ar4_package_Package_createImplementationDataTypePtr`
* :ref:`ar4_package_Package_createImplementationRecordDataType`
* :ref:`ar4_package_Package_createSwBaseType`

**Mode**

* :ref:`ar4_package_Package_createModeDeclarationGroup`

**PortInterface**

* :ref:`ar4_package_Package_createClientServerInterface`
* :ref:`ar4_package_Package_createModeSwitchInterface`
* :ref:`ar4_package_Package_createNvDataInterface`
* :ref:`ar4_package_Package_createParameterInterface`
* :ref:`ar4_package_Package_createSenderReceiverInterface`

**SubPackage**

* :ref:`ar4_package_Package_createSubPackage`

**SoftwareAddressMethod**

* :ref:`ar4_package_Package_createSoftwareAddressMethod`

**Unit**

* :ref:`ar4_package_Package_createUnit`

Method Description
------------------

.. _ar4_package_Package_createApplicationSoftwareComponent:

createApplicationSoftwareComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createApplicationSoftwareComponent(swcName, [behaviorName = None], [implementationName = None], [multipleInstance = False])

    Creates a new :ref:`ar4_component_ApplicationSoftwareComponent` and adds it to the package.

    :param str swcName: ShortName of the component type
    :param str behaviorName: ShortName of the associated Behavior object. If not set an automatic name is selected.
    :param str implementationName: ShortName of the associated Implementation object. If not set an automatic name is selected.
    :param bool multipleInstance: Set to True if this component prototype needs to support multiple instances
    :param bool autoCreatePortAPIOptions: Set to True to automatically create port API options.
    :rtype: :ref:`ar4_component_ApplicationSoftwareComponent`

Example
^^^^^^^

.. include:: examples/create_application_component.py
    :code: python

.. _ar4_package_Package_createComplexDeviceDriverComponent:

createComplexDeviceDriverComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createComplexDeviceDriverComponent(swcName, [behaviorName = None], [implementationName = None], [multipleInstance = False])

    Creates a new :ref:`ar4_component_ComplexDeviceDriverComponent` and adds it to the package.

    :param str swcName: ShortName of the component type
    :param str behaviorName: ShortName of the associated Behavior object. If not set an automatic name is selected.
    :param str implementationName: ShortName of the associated Implementation object. If not set an automatic name is selected.
    :param bool multipleInstance: Set to True if this component prototype needs to support multiple instances
    :param bool autoCreatePortAPIOptions: Set to True to automatically create port API options.
    :rtype: :ref:`ar4_component_ComplexDeviceDriverComponent`

.. _ar4_package_Package_createCompositionComponent:

createCompositionComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createCompositionComponent(componentName, [adminData = None])

    Creates a new :ref:`ar4_component_CompositionComponent` and adds it to the package.

    :param str componentName: ShortName of the component type
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_component_CompositionComponent`

Example
^^^^^^^

.. include:: examples/create_composition_component.py
    :code: python

.. _ar4_package_Package_createNvBlockComponent:

createNvBlockComponent
~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createNvBlockComponent(swcName, [behaviorName = None], [implementationName = None], [multipleInstance = False])

    Creates a new NvBlockComponent and adds it to the package.

    :param str swcName: ShortName of the component type
    :param str behaviorName: ShortName of the associated Behavior object. If not set an automatic name is selected.
    :param str implementationName: ShortName of the associated Implementation object. If not set an automatic name is selected.
    :param bool multipleInstance: Set to True if this component prototype needs to support multiple instances
    :param bool autoCreatePortAPIOptions: Set to True to automatically create port API options.
    :rtype: NvBlockComponent

.. _ar4_package_Package_createServiceComponent:

createServiceComponent
~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createServiceComponent(swcName, [behaviorName = None], [implementationName = None], [multipleInstance = False])

    Creates a new :ref:`ar4_component_ServiceComponent` and adds it to the package.

    :param str swcName: ShortName of the component type.
    :param str behaviorName: ShortName of the associated Behavior object. If not set an automatic name is selected.
    :param str implementationName: ShortName of the associated Implementation object. If not set an automatic name is selected.
    :param bool multipleInstance: Set to True if this component prototype needs to support multiple instances.
    :param bool autoCreatePortAPIOptions: Set to True to automatically create port API options.
    :rtype: :ref:`ar4_component_ServiceComponent`

Example
^^^^^^^

.. include:: examples/create_service_component.py
    :code: python

.. _ar4_package_Package_createCompuMethodConst:

createCompuMethodConst
~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createCompuMethodConst(name, valueTable, [unit = None], [defaultValue = None], [category = 'TEXTTABLE'], [adminData = None])

    Creates a new CompuMethod based on a value-table (better known as enumeration) and adds it to the package.

    :param str name: shortName of the new CompuMethod.
    :param list valueTable: List of strings containing enumeration values. See below for more advanced options.
    :param str unit: Optional unit name (requires :ref:`package role <ar4_package_Package_roles>` 'Unit' to be setup).
    :param str defaultValue: Optional default value.
    :param str category: Category string used for the new CompuMethod.
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: CompuMethod


.. _ar4_package_Package_createCompuMethodLinear:

createCompuMethodLinear
~~~~~~~~~~~~~~~~~~~~~~~

Alias for :ref:`ar4_package_Package_createCompuMethodRational`.

.. _ar4_package_Package_createCompuMethodRational:

createCompuMethodRational
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createCompuMethodRational(name, offset, scaling, [lowerLimit = None], [upperLimit = None], [lowerLimitType = 'CLOSED'], [upperLimitType = 'CLOSED'], [unit = None], [defaultValue = None], [label = 'SCALING'], [forceFloat = False], [useIntToPhys=True], [usePhysToInt = False], [category = 'LINEAR'], [adminData = None])

    Creates a new CompuMethod containing a CompuScaleElement (offset+scaling) and adds it to the package.

    :param str name: ShortName of the new CompuMethod.
    :param offset: Offset.
    :type offset: int,float
    :param scaling: Scaling factor.
    :type scaling: int, float, rational number
    :param int lowerLimit: Lower limit of the CompuScaleElement.
    :param int upperLimit: Upper limit of the CompuScaleElement.
    :param str lowerLimitType: Interval type of lowerLimit ("OPEN" or "CLOSED"). Only applies when lowerLimit is not None.
    :param str upperLimitType: Interval type of upperLimit ("OPEN" or "CLOSED"). Only applies when upperLimit is not None.
    :param str unit: Optional unit name (requires :ref:`package role <ar4_package_Package_roles>` 'Unit' to be setup).
    :param defaultValue: Optional default value.
    :type defaultValue: None, int, float, str
    :param str label: Label of the CompuScaleElement
    :param bool forceFloat: When False it sets the scaling numerator/denominator to closest possible rational number. When True it forces numerator to float and sets denominator to 1.
    :param bool useIntToPhys: When True, creates an internal to physical Computation. Cannot be True when usePhysToInt is also True.
    :param bool usePhysToInt: When True, creates a physical to internal Computation. Cannot be True when useIntToPhys is also True.
    :param str category: Category string used for the new CompuMethod.
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: CompuMethod

    This method by default creates an internal to physical computation, use the method :ref:`ar4_package_Package_createCompuMethodRationalPhys` to create a physical to internal computation.
    Some AUTOSAR toolchains does not work when numerator and denominator is a rational number. Use the option forceFloat to force the scaling factor to be stored as a floating point number.


.. _ar4_package_Package_createCompuMethodRationalPhys:

createCompuMethodRationalPhys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convenience method that calls :ref:`ar4_package_Package_createCompuMethodRational` but creates physical to internal computation instead.

.. _ar4_package_Package_createApplicationValueConstant:

createApplicationValueConstant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createApplicationValueConstant(name, [swValueCont = None], [swAxisCont = None], [valueCategory = None], [valueLabel = None])

    Creates an application value constant and adds it to the package.

    :param str name: ShortName of the new constant
    :param SwValueCont swValueCont: Value container
    :param SwValueCont swAxisCont: Axis container
    :param str valueCategory: Optional category for (inner) value
    :param str valueLabel: Optional label for (inner) value
    :rtype: :ref:`ar4_constant_Constant`

.. _ar4_package_Package_createConstant:

createConstant
~~~~~~~~~~~~~~

.. py:method:: Package.createConstant(name, typeRef, initValue, adminData=None)

    Creates a new constant (based on a type reference) and adds it to the package.

    :param str name: ShortName of the new constant
    :param str typeRef: Reference to (existing) data type
    :param initValue: Init value (type depends on typeRef)
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_constant_Constant`


.. _ar4_package_Package_createNumericalValueConstant:

createNumericalValueConstant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createNumericalValueConstant(name, value)

    Creates a new constant (based on a numerical value) and adds it to the package.

    :param str name: ShortName of the new constant
    :param value: Value
    :type value: int, float
    :rtype: :ref:`ar4_constant_Constant`


.. _ar4_package_Package_createInternalDataConstraint:

createInternalDataConstraint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createInternalDataConstraint(name, lowerLimit, upperLimit, lowerLimitType="CLOSED", upperLimitType="CLOSED", adminData = None)

    Creates a new internal data constraint and adds it the package.

    :param str name: ShortName of the new DataConstraint.
    :param lowerLimit: Lower limit.
    :type lowerLimit: int, float.
    :param upperLimit: Upper limit.
    :type upperLimit: int, float.
    :param str lowerLimitType: Interval type of lowerLimit ("OPEN"/"CLOSED").
    :param str upperLimitType: Interval type of upperLimit ("OPEN"/"CLOSED").
    :rtype: DataConstraint


.. _ar4_package_Package_createPhysicalDataConstraint:

createPhysicalDataConstraint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createPhysicalDataConstraint(name, lowerLimit, upperLimit, lowerLimitType="CLOSED", upperLimitType="CLOSED", adminData = None)

    Creates a new physical data constraint and adds it the package.

    :param str name: ShortName of the new DataConstraint.
    :param lowerLimit: Lower limit.
    :type lowerLimit: int, float.
    :param upperLimit: Upper limit.
    :type upperLimit: int, float.
    :param str lowerLimitType: Interval type of lowerLimit ("OPEN"/"CLOSED").
    :param str upperLimitType: Interval type of upperLimit ("OPEN"/"CLOSED").
    :rtype: DataConstraint



.. _ar4_package_Package_createApplicationArrayDataType:

createApplicationArrayDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.ApplicationArrayDataType(name, element, [swCalibrationAccess = None], [category = None], [adminData = None])

    Creates a new ApplicationArrayDataType and appends it to the package.

    :param str name: ShortName of the new datatype
    :param ApplicationArrayElement element: An ApplicationArrayElement object
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str category: Optional category string
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: ApplicationArrayDataType




.. _ar4_package_Package_createApplicationPrimitiveDataType:

createApplicationPrimitiveDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createApplicationPrimitiveDataType(name, [dataConstraint = ""], [compuMethod = None], [unit = None], [swCalibrationAccess = None], [category = None], [adminData = None])

    Creates a new ApplicationPrimitiveDataType and appends it to this package.

    :param str name: ShortName of the new datatype
    :param str dataConstraint: Optional name or reference to a DataConstraint object. Empty string means that an automatic data constraint will be created. Set to None to disable.
    :param str compuMethod: Optional name or reference to a CompuMethod object
    :param str unit: Optional name or reference to a Unit object
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str category: Optional category string
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: ApplicationPrimitiveDataType



.. _ar4_package_Package_createApplicationRecordDataType:

createApplicationRecordDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createApplicationRecordDataType(name, elements, [swCalibrationAccess = ""], [category = "STRUCTURE"], [adminData=None])

    Creates a new ApplicationRecordDataType and appends it to the package.

    :param str name: ShortName of the new datatype
    :param str elements: List containing tuples. First tuple element is the record name (string), second tuple element is a type reference (string).
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str category: Category string
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: ApplicationRecordDataType

.. _ar4_package_Package_createBaseType:

createBaseType
~~~~~~~~~~~~~~

Alias for :ref:`ar4_package_Package_createSwBaseType`.


.. _ar4_package_Package_createImplementationArrayDataType:

createImplementationArrayDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createImplementationArrayDataType(name, implementationTypeRef, arraySize, [elementName = None], [swCalibrationAccess = ''], [typeEmitter = None], [category = 'ARRAY'], [targetCategory = 'TYPE_REFERENCE'], [adminData = None])

    Creates an implementation array data type and adds it to the package.

    :param str name: ShortName of the new data type
    :param str implementationTypeRef: Reference to (existing) :ref:`ar4_datatype_ImplementationDataType`
    :param int arraySize: Number of elements in array
    :param str elementName: Optional (inner) element name.
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str typeEmitter: Optional type emitter
    :param str category: Category for the (outer) array data type
    :param str targetCategory: Category for the (inner) array element
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_datatype_ImplementationDataType`


.. _ar4_package_Package_createImplementationDataType:

createImplementationDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createImplementationDataType(name, baseTypeRef, [lowerLimit = None], [upperLimit = None], [valueTable = None], [bitmask = None], [offset = None], [scaling = None], [unit = None], [forceFloat = False], [dataConstraint = ''], [swCalibrationAccess = ''], [typeEmitter = None], [lowerLimitType = None], [upperLimitType = None], [category='VALUE'], [adminData = None])

    Creates a new implementation data type that is tied directly to a base type.

    :param str name: ShortName of the datatype
    :param str baseTypeRef: Reference to existing :ref:`base type <ar4_datatype_SwBaseType>`
    :param int lowerLimit: Optional lower limit.
    :param int upperLimit: Optional upper limit.
    :param valueTable: Optional valueTable. See :ref:`ar4_package_Package_valueTable` for details.
    :param bitmask: Optional bitmask. See :ref:`ar4_package_Package_bitmask` for details.
    :param int offset: Optional offset (for CompuMethod). When this is used, scaling also has to be set.
    :param scaling: Optional scaling factor (for CompuMethod).
    :type scaling: int or float
    :param str unit: Optional unit.
    :param bool forceFloat: When False it sets the scaling numerator/denominator to closest possible rational number. When True it forces numerator to float type and sets denominator to 1.
    :param str dataConstraint: Optional name or reference to existing DataConstraint element. Value None prevents dataConstraint from being created while empty-string automatically attempts to create a DataConstraint element.
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str typeEmitter: Optional type emitter string.
    :param str lowerLimitType: Selects lowerLimitType ("OPEN" or "CLOSED") if lowerLimit is used. Value None defaults to "CLOSED".
    :param str upperLimitType: Selects upperLimitType ("OPEN" or "CLOSED") if upperLimit is used. Value None defaults to "CLOSED".
    :param str category: Category string.
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_datatype_ImplementationDataType`

Example
^^^^^^^

.. include:: examples/creating_implementation_type.py
    :code: python


.. _ar4_package_Package_createImplementationDataTypeRef:

createImplementationDataTypeRef
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createImplementationDataTypeRef(name, implementationTypeRef, [lowerLimit = None], [upperLimit = None], [valueTable = None], [bitmask = None], [offset = None], [scaling = None], [unit = None], [forceFloat = False], [dataConstraint = ''], [swCalibrationAccess = ''], [typeEmitter = None], [lowerLimitType = None], [upperLimitType = None], [category = 'TYPE_REFERENCE'], [adminData = None])

    Creates a new implementation data type that is a reference to another implementation type.
    This is similar in concept to a typedef in the C programming language

    :param str name: ShortName of the datatype
    :param str implementationTypeRef: Reference to existing :ref:`ar4_datatype_ImplementationDataType`
    :param int lowerLimit: Optional lower limit.
    :param int upperLimit: Optional upper limit.
    :param valueTable: Optional valueTable. See :ref:`ar4_package_Package_valueTable` for details.
    :param bitmask: Optional bitmask. See :ref:`ar4_package_Package_bitmask` for details.
    :param int offset: Optional offset (for CompuMethod). When this is used, scaling also has to be set.
    :param scaling: Optional scaling factor (for CompuMethod).
    :type scaling: int or float
    :param str unit: Optional unit.
    :param bool forceFloat: When False it sets the scaling numerator/denominator to closest possible rational number. When True it forces numerator to float type and sets denominator to 1.
    :param str dataConstraint: Optional name or reference to existing DataConstraint element. Value None prevents dataConstraint from being created while empty-string automatically attempts to create a DataConstraint element.
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str typeEmitter: Optional type emitter string.
    :param str lowerLimitType: Selects lowerLimitType ("OPEN" or "CLOSED") if lowerLimit is used. Value None defaults to "CLOSED".
    :param str upperLimitType: Selects upperLimitType ("OPEN" or "CLOSED") if upperLimit is used. Value None defaults to "CLOSED".
    :param str category: Category string.
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_datatype_ImplementationDataType`


Example
^^^^^^^

.. include:: examples/creating_implementation_type_ref.py
    :code: python


.. _ar4_package_Package_createImplementationDataTypePtr:

createImplementationDataTypePtr
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createImplementationDataTypePtr(name, baseTypeRef, [swImplPolicy=None], [category='DATA_REFERENCE', [targetCategory=VALUE], [adminData=None])

   Creates a new implementation data type that is a pointer to a base data type.
   This is similar to a pointer type definition in C.

   :param str name: ShortName of the datatype.
   :param str baseTypeRef: Reference to (existing) base type object.
   :param str swImplPolicy: Optional swImplPolicy.
   :param str category: Optional category string (for the datatype)
   :param str targetCategory: Optional category string for the inner target property.
   :param adminData: Optional :ref:`ar4_base_AdminData`
   :rtype: :ref:`ar4_datatype_ImplementationDataType`

Example
^^^^^^^

.. include:: examples/creating_implementation_type_ptr.py
    :code: python


.. _ar4_package_Package_createImplementationRecordDataType:

createImplementationRecordDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createImplementationRecordDataType(name, elements, [swCalibrationAccess = ''], [category = 'STRUCTURE'], [adminData = None])

    Creates an implementation record data type and adds it to the package.

    :param str name: ShortName of the new data type
    :param str elements: List containing tuples. First tuple element is the record name (string), second tuple element is a type reference (string).
    :param str swCalibrationAccess: Optional :ref:`calibration access <ar4_package_Package_swCalibrationAccess>`
    :param str category: Category for the (outer) array data type
    :param str targetCategory: Category for the (inner) array element
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_datatype_ImplementationDataType`


.. _ar4_package_Package_createSwBaseType:

createSwBaseType
~~~~~~~~~~~~~~~~~

..  py:method:: Package.createSwBaseType(name , [size=None], [encoding=None], [nativeDeclaration=None], [category='FIXED_LENGTH'], [adminData=None])

    Creates a new SwBaseType and adds it to the package.

    :param str name: ShortName of the new datatype
    :param int size: Size of type in bits
    :param str encoding: Encoding string
    :param str nativeDeclaration: Used to map this base type to one of the native types known to the RTE
    :param str category: Category string
    :param adminData: Optional :ref:`ar4_base_AdminData`

Example
^^^^^^^

.. include:: examples/creating_platform_basetypes.py
    :code: python3

.. _ar4_package_Package_createModeDeclarationGroup:

createModeDeclarationGroup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createModeDeclarationGroup(name, [modeDeclarations=None], [initialMode=None], [category=None], [adminData=None])

    Creates a new :ref:`mode_modeDeclarationGroup` and adds it to the package.

    :param str name: ShortName of the object
    :param modeDeclarations: List of mode declaration names
    :type modeDeclarations: list(str)
    :param str initialMode: Initial mode value (must be one of strings from modeDeclarations list)
    :param str category: Optional category
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`mode_modeDeclarationGroup`

.. _ar4_package_Package_createClientServerInterface:

createClientServerInterface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  method:: Package.createClientServerInterface(name, operations, [errors=None], [isService=False], [serviceKind = None], [adminData=None])

    Creates a new :ref:`ar4_portinterface_clientServerInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param operations: List of names to be created as of :ref:`ar4_portinterface_Operation`
    :type operations: list(str)
    :param errors: Possible errors that can be returned. Errors must be assigned here first, before you can use them in individual operations.
    :type errors: ApplicationError or list(ApplicationError)
    :param bool isService: Set this to True for service interfaces
    :param str serviceKind: Optional serviceKind string
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_portinterface_clientServerInterface`

Example
^^^^^^^

.. include:: examples/creating_client_server_interface.py
    :code: python


.. _ar4_package_Package_createModeSwitchInterface:

createModeSwitchInterface
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createModeSwitchInterface(name, [modeGroup = None], [isService=False], [adminData=None])

    Creates a new :ref:`ar4_portinterface_ModeSwitchInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param modeGroup: mode group object
    :type modeGroup: :ref:`mode_modeGroup`
    :param bool isService: Set this to True for service interfaces
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_portinterface_ModeSwitchInterface`

.. _ar4_package_Package_createNvDataInterface:

createNvDataInterface
~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createNvDataInterface(name, [nvDatas=None], [isService=False], [serviceKind = None], [adminData=None])

    Creates a new NvDataInterface and adds it to the package.

    :param str name: ShortName of the port interface
    :param nvDatas: data element(s)
    :type nvDatas: :ref:`ar4_element_DataElement` or list(:ref:`ar4_element_DataElement`)
    :param bool isService: Set this to True for service interfaces
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: NvDataInterface

.. _ar4_package_Package_createParameterInterface:

createParameterInterface
~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createParameterInterface(name, parameters=None, isService=False, adminData=None)

    Creates a new :ref:`ar4_portinterface_ParameterInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param parameters: Parameter or parameters
    :type parameters: :ref:`ar4_element_ParameterDataPrototype` or list(:ref:`ar4_element_ParameterDataPrototype`)
    :param bool isService: Enables the isService attribute
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_portinterface_ParameterInterface`

.. _ar4_package_Package_createSenderReceiverInterface:

createSenderReceiverInterface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createSenderReceiverInterface(name, [dataElements=None], [isService=False], [serviceKind = None], [adminData=None])

    Creates a new :ref:`ar4_portinterface_SenderReceiverInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param dataElements: Data element(s) in this port interface
    :type dataElements: list(DataElement) or DataElement
    :param bool isService: Sets the isService attribute
    :param str serviceKind: Optional serviceKind string
    :param adminData: Optional :ref:`ar4_base_AdminData`
    :rtype: :ref:`ar4_portinterface_SenderReceiverInterface`

Examples
^^^^^^^^

**Port interface with single data element**

.. include:: portinterface/examples/usage_sender_receiver_interface.py
    :code: python3

.. _ar4_package_Package_createSubPackage:

createSubPackage
~~~~~~~~~~~~~~~~~

.. py:method:: Package.createPackage(name, [role=None])

    Creates a new package and appends it to this package as a sub-package.

    :param str name: ShortName of the new package
    :param str role: Optional :ref:`package role <ar4_package_Package_roles>`
    :rtype: :ref:`ar4_package_Package`



Example
^^^^^^^

.. include:: examples/create_sub_packages.py
    :code: python

.. _ar4_package_Package_createSoftwareAddressMethod:

createSoftwareAddressMethod
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createSoftwareAddressMethod(name)

    Creates a new SoftwareAddressMethod and adds it to the package.

    :param str name: ShortName of the address method
    :rtype: SoftwareAddressMethod

.. _ar4_package_Package_createUnit:

createUnit
~~~~~~~~~~

.. py:method:: Package.createUnit(self, shortName, [displayName = None], [offset = None], [scaling = None])

    Creates a new Unit and adds it to the package.

    :param str name: ShortName of the new unit.
    :param str displayName: Optional Display name (Will default to shortName if not set)
    :param offset: Optional offset
    :type offset: None, int, float
    :param factor: Optional scaling factor
    :type factor: None, int, float
    :rtype: Unit

Parameter Details
-----------------

.. _ar4_package_Package_swCalibrationAccess:

swCalibrationAccess
~~~~~~~~~~~~~~~~~~~

+-----------------------+------------------------------------------------------------------------------------------------+
| Value                 | Description                                                                                    |
+=======================+================================================================================================+
| None                  | No calibration access set                                                                      |
+-----------------------+------------------------------------------------------------------------------------------------+
| \\"\\" (Empty string) | Create default calibration access value                                                        |
|                       | as set by Workspace.profile.swCalibrationAccessDefault                                         |
+-----------------------+------------------------------------------------------------------------------------------------+
| \\"NOT-ACCESSIBLE\\"  | The element will not be accessible by external tools                                           |
+-----------------------+------------------------------------------------------------------------------------------------+
| \\"READ-ONLY\\"       | Read only access                                                                               |
+-----------------------+------------------------------------------------------------------------------------------------+
| \\"READ-WRITE\\"      | Read-write access                                                                              |
+-----------------------+------------------------------------------------------------------------------------------------+

.. _ar4_package_Package_valueTable:

valueTable
~~~~~~~~~~

The valueTable parameter accepts three different formats:

1. List of strings
2. List of 2-tuples
3. List of 3-tuples

List of strings
^^^^^^^^^^^^^^^

List of text values. LowerLimit starts at 0 and is automatically incremented by 1 for each element in the list.
The UpperLimit follows LowerLimit for each element.

List of 2-tuples
^^^^^^^^^^^^^^^^

The first element of the tuple is used as both lowerLimit and upperLimit (int). The second element is the text value (str).

List of 3-tuples
^^^^^^^^^^^^^^^^

The first element of the tuple is lowerLimit (int). The Second element is the upperLimit (int). The third element is the text value (str).

.. _ar4_package_Package_bitmask:

bitmask
~~~~~~~

The bitmask parameter is a list of 2-tuples. The first element of the tuple is the bitmask (int). The second elementof is the symbol (str).
