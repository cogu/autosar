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
    
Method Description
------------------

.. _package_createSwBaseType:

createSwBaseType
~~~~~~~~~~~~~~~~~

..  py:method:: Package.createSwBaseType(name , size, [encoding=None], [nativeDeclaration=None], [adminData=None])

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

..  py:method:: Package.createImplementationDataTypeRef(self, name, implementationTypeRef, [lowerLimit = None], [upperLimit = None], [valueTable = None], [bitmask = None], [offset = None], [scaling = None], [unit = None], [forceFloat = False], [dataConstraint = ''], [swCalibrationAccess = ''], [typeEmitter = None], [lowerLimitType = None], [upperLimitType = None], [category = 'TYPE_REFERENCE'], [adminData = None])

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

.. py:method:: Package.createImplementationDataTypePtr(self, name, baseTypeRef, [swImplPolicy=None], [category='DATA_REFERENCE', [targetCategory=VALUE], [adminData=None])

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

.. _package_createCompositionComponent:

createCompositionComponent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD
