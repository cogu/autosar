.. _ar3_package:

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
   
   ws = autosar.workspace("3.0.2")
   package = ws.createPackage('DataTypes', role = 'DataType')
   
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
    | *Constant*       | Main container for Constants               |
    +------------------+--------------------------------------------+
    | *ComponentType*  | Main container for Components              |
    +------------------+--------------------------------------------+
    | *CompuMethod*    | Main Container for Computational Methods   |
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

**Data Types**:

* :ref:`ar3_package_createIntegerDataType`
* :ref:`ar3_package_createArrayDataType`
* :ref:`ar3_package_createRecordDataType`

        

Method Description
------------------

.. _ar3_package_createIntegerDataType:

createIntegerDataType
~~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createIntegerDataType(name, [min=None], [max=None], [valueTable=None], [offset=None], [scaling=None], [unit=None], [adminData=None])

    Creates a new IntegerDataType object add appends it to this package.
    
    :param str name: (short)Name of new datatype
    :param int min: Lower limit
    :param str max: Upper limit
    :param list valueTable: Value table
    :param offset: Scaling offset
    :type offset: int or float
    :param scaling: Scaling factor
    :type scaling: int or float
    :param str unit: Unit name
    :param adminData: Optional AdminData


.. _ar3_package_createArrayDataType:

createArrayDataType
~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createArrayDataType(name, typeRef, arraySize, [elementName=None], [adminData=None])

    Creates a new array data type and appends it to current package
   
    :param str name: (short)Name of new datatype
    :param str typeRef: Reference to data type (used as the type for array element)
    :param int arraySize: Number of elements in the array
    :param adminData: Optional AdminData

.. _ar3_package_createRecordDataType:

createRecordDataType
~~~~~~~~~~~~~~~~~~~~

..  py:method:: Package.createRecordDataType(name, elements, [adminData=None])

    Creates a new array data type and appends it to current package
   
    :param str name: (short)Name of new datatype
    :param list elements: Elements in the record
    :param adminData: Optional AdminData

