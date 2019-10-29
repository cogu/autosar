.. _package:

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

Package Roles
-------------

..  table::
    :align: left

    +------------------+--------------------------------------------+
    | *Constant*       |  Main container for Constants              |
    +------------------+--------------------------------------------+
    | *ComponentType*  | Main container for Components              |
    +------------------+--------------------------------------------+
    | *CompuMethod*    | Main Container for Computational Methods   |
    +------------------+--------------------------------------------+
    | *DataConstraint* | Main container for Data Constraints        |
    +------------------+--------------------------------------------+
    | *DataType*       | Main container for Data Types              |
    +------------------+--------------------------------------------+
    | *ModeDclrGroup*  | Main Container for Mode Declaration Groups |
    +------------------+--------------------------------------------+
    | *PortInterface*  | Main Container for Port Interfaces         |
    +------------------+--------------------------------------------+
    | *Unit*           | Main Container for Units                   |
    +------------------+--------------------------------------------+


Public Methods
--------------

**DataType**

* :ref:`package_createSwBaseType`
* :ref:`package_createImplementationDataTypeRef`
* :ref:`package_createImplementationDataTypePtr`

**PortInterface**

* :ref:`package_createSenderReceiverInterface`
* :ref:`package_createClientServerInterface`
* :ref:`package_createModeSwitchInterface`


**ComponentType**

* :ref:`package_createApplicationSoftwareComponent`

**Mode**

* :ref:`package_createModeDeclarationGroup`

Method Description
------------------

.. _package_createSwBaseType:

createSwBaseType
~~~~~~~~~~~~~~~~~

..  py:method:: Package.createSwBaseType(name , [size=None], [encoding=None], [nativeDeclaration=None], [adminData=None])

    Creates a new SwBaseType object add appends it to this package.

    :param int size: Size of type in bits
    :param str encoding: Encoding string
    :param str nativeDeclaration: Used to map this base type to one of the native types known to the RTE
    :param adminData: Optional AdminData

Example - Platform Types
^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: examples/creating_platform_basetypes.py
    :code: python3

.. _package_createImplementationDataTypeRef:

createImplementationDataTypeRef
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createImplementationDataTypeRef(name, implementationTypeRef, [lowerLimit = None], [upperLimit = None], [valueTable = None], [bitmask = None], [offset = None], [scaling = None], [unit = None], [forceFloat = False], [dataConstraint = ''], [swCalibrationAccess = ''], [typeEmitter = None], [lowerLimitType = None], [upperLimitType = None], [category = 'TYPE_REFERENCE'], [adminData = None])

    Creates a new implementation data type that is a reference to another implementation type.
    This is similar in concept to a typedef in the C programming language

    :param str name: ShortName of the datatype
    :param str implementationTypeRef: Reference to existing implementation type
    :param adminData: Optional AdminData


Example
^^^^^^^

.. include:: examples/creating_implementation_type_ref.py
    :code: python


.. _package_createImplementationDataTypePtr:

createImplementationDataTypePtr
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createImplementationDataTypePtr(name, baseTypeRef, [swImplPolicy=None], [category='DATA_REFERENCE', [targetCategory=VALUE], [adminData=None])

   Creates a new implementation data type that is a pointer to a base data type.
   This is similar to a pointer type definition in C.

   :param str name: ShortName of the datatype
   :param str baseTypeRef: Reference to (existing) base type object
   :param str swImplPolicy: Set this to 'CONST' in order to create a const pointer data type
   :param adminData: Option AdminData

Example
^^^^^^^

.. include:: examples/creating_implementation_type_ptr.py
    :code: python


.. _package_createSenderReceiverInterface:

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
    :rtype: :ref:`portinterface_SenderReceiverInterface`

.. _package_createClientServerInterface:

createClientServerInterface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  method:: Package.createClientServerInterface(name, operations, [errors=None], [isService=False], [serviceKind = None], [adminData=None])

    Creates a new :ref:`portinterface_clientServerInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param operations: List of names to be created as of :ref:`portinterface_Operation`
    :type operations: list(str)
    :param errors: Possible errors that can be returned. Errors must be assigned here first, before you can use them in individual operations.
    :type errors: ApplicationError or list(ApplicationError)
    :param bool isService: Set this to True for service interfaces
    :param str serviceKind: Optional serviceKind string
    :param adminData: Optional adminData
    :rtype: :ref:`portinterface_clientServerInterface`

.. _package_createModeSwitchInterface:

createModeSwitchInterface
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createModeSwitchInterface(name, [modeGroup = None], [isService=False], [adminData=None])

    Creates a new :ref:`portinterface_ModeSwitchInterface` and adds it to the package.

    :param str name: ShortName of the port interface
    :param modeGroup: mode group object
    :type modeGroup: :ref:`mode_modeGroup`
    :param bool isService: Set this to True for service interfaces
    :param adminData: Optional adminData
    :rtype: :ref:`portinterface_ModeSwitchInterface`


.. _package_createApplicationSoftwareComponent:

createApplicationSoftwareComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createApplicationSoftwareComponent(swcName, [behaviorName = None], [implementationName = None], [multipleInstance = False])

    Creates a new :ref:`component_applicationSoftwareComponent` and adds it to the package.

    :param str swcName: ShortName of the component type
    :param str behaviorName: ShortName of the associated Behavior object. If not set an automatic name is selected.
    :param str implementationName: ShortName of the associated Implementation object. If not set an automatic name is selected.
    :rtype: :ref:`component_applicationSoftwareComponent`

.. _package_createCompositionComponent:

createCompositionComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: Package.createCompositionComponent(componentName, [adminData = None])

    Creates a new :ref:`component_compositionComponent` and adds it to the package.

    :param str componentName: ShortName of the component type
    :param adminData: Optional adminData
    :rtype: :ref:`component_compositionComponent`

.. _package_createModeDeclarationGroup:

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

