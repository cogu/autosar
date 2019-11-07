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

An AUTOSAR package is a container for elements. Elements can be basically anything that are not packages.

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

**Sub-package**
* :ref:`ar4_package_Package_createSubPackage`

**DataType**

* :ref:`ar4_package_Package_createSwBaseType`
* :ref:`ar4_package_Package_createImplementationDataType`
* :ref:`ar4_package_Package_createImplementationDataTypeRef`
* :ref:`ar4_package_Package_createImplementationDataTypePtr`

**PortInterface**

* :ref:`ar4_package_Package_createSenderReceiverInterface`
* :ref:`ar4_package_Package_createClientServerInterface`
* :ref:`ar4_package_Package_createModeSwitchInterface`


**ComponentType**

* :ref:`ar4_package_Package_createApplicationSoftwareComponent`

**Mode**

* :ref:`ar4_package_Package_createModeDeclarationGroup`

Method Description
------------------

.. _ar4_package_Package_createSubPackage:

createSubPackage
~~~~~~~~~~~~~~~~~

.. py:method:: Package.createPackage(name, [role=None])

    :param str name: ShortName of the new package
    :param str role: Optional :ref:`package role <ar4_package_Package_roles>`
    :rtype: :ref:`ar4_package_Package`

    Creates a new package and appends it to this package as a sub-package.

Example
^^^^^^^

.. code-block:: python

    import autosar

    ws = autosar.workspace("4.2.2")
    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')


.. _ar4_package_Package_createSwBaseType:

createSwBaseType
~~~~~~~~~~~~~~~~~

..  py:method:: Package.createSwBaseType(name , [size=None], [encoding=None], [nativeDeclaration=None], [adminData=None])

    Creates a new SwBaseType object add appends it to this package.

    :param int size: Size of type in bits
    :param str encoding: Encoding string
    :param str nativeDeclaration: Used to map this base type to one of the native types known to the RTE
    :param adminData: Optional AdminData

Example
^^^^^^^

.. include:: examples/creating_platform_basetypes.py
    :code: python3

.. _ar4_package_Package_createImplementationDataType:

createImplementationDataType
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createImplementationDataType(name, baseTypeRef, [lowerLimit = None], [upperLimit = None], [valueTable = None], [bitmask = None], [offset = None], [scaling = None], [unit = None], [forceFloat = False], [dataConstraint = ''], [swCalibrationAccess = ''], [typeEmitter = None], [lowerLimitType = None], [upperLimitType = None], [category='VALUE'], [adminData = None])

    :param str name: ShortName of the datatype
    :param str baseTypeRef: Reference to existing :ref:`base type <ar4_datatype_SwBaseType>`
    :rtype: :ref:`ar4_datatype_ImplementationDataType`

    Creates a new implementation data type that is tied directly to a base type.

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
    :param str implementationTypeRef: Reference to existing implementation type
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

   :param str name: ShortName of the datatype
   :param str baseTypeRef: Reference to (existing) base type object
   :rtype: :ref:`ar4_datatype_ImplementationDataType`

Example
^^^^^^^

.. include:: examples/creating_implementation_type_ptr.py
    :code: python

.. _ar4_package_Package_createSenderReceiverInterface:

createSenderReceiverInterface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  method:: Package.createSenderReceiverInterface(name, [dataElements=None], [isService=False], [serviceKind = None], [adminData=None])

    Creates a new SenderReceiver port interface and adds it to the package.

    :param str name: ShortName of the port interface
    :param dataElements: Data element(s) in this port interface
    :type dataElements: list(DataElement) or DataElement
    :param bool isService: Sets the isService attribute
    :param str serviceKind: Optional serviceKind string
    :param adminData: Optional adminData
    :rtype: :ref:`ar4_portinterface_SenderReceiverInterface`

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
    :param adminData: Optional adminData
    :rtype: :ref:`ar4_portinterface_clientServerInterface`

.. _ar4_package_Package_createModeSwitchInterface:

createModeSwitchInterface
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createModeSwitchInterface(name, [modeGroup = None], [isService=False], [adminData=None])

    Creates a new :ref:`ar4_portinterface_ModeSwitchInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param modeGroup: mode group object
    :type modeGroup: :ref:`mode_modeGroup`
    :param bool isService: Set this to True for service interfaces
    :param adminData: Optional adminData
    :rtype: :ref:`ar4_portinterface_ModeSwitchInterface`

.. _ar4_package_Package_createApplicationSoftwareComponent:

createApplicationSoftwareComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createApplicationSoftwareComponent(swcName, [behaviorName = None], [implementationName = None], [multipleInstance = False])

    Creates a new :ref:`component_applicationSoftwareComponent` and adds it to the package.

    :param str swcName: ShortName of the component type
    :param str behaviorName: ShortName of the associated Behavior object. If not set an automatic name is selected.
    :param str implementationName: ShortName of the associated Implementation object. If not set an automatic name is selected.
    :rtype: :ref:`component_applicationSoftwareComponent`

.. _ar4_package_Package_createCompositionComponent:

createCompositionComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createCompositionComponent(componentName, [adminData = None])

    Creates a new :ref:`component_compositionComponent` and adds it to the package.

    :param str componentName: ShortName of the component type
    :param adminData: Optional adminData
    :rtype: :ref:`component_compositionComponent`

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
    :param adminData: Optional adminData
    :rtype: :ref:`mode_modeDeclarationGroup`
