.. _ar4_datatype_ImplementationDataType:

ImplementationDataType
======================

.. table::
   :align: left

   +--------------------+------------------------------------------------------+
   | XML tag            | <IMPLEMENTATION-DATA-TYPE>                           |
   +--------------------+------------------------------------------------------+
   | Module             | autosar.datatype                                     |
   +--------------------+------------------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------------+------------------------------------------------------+

Implementation Data Types is a very generic container and can define almost any data type.

Usage
-----

..  include:: examples/usage_implementation_data_type.py
    :code: python3


Factory Methods
---------------

Basic Implementation Types
~~~~~~~~~~~~~~~~~~~~~~~~~~

In its simplest form, an implementation data type is just a reference to a :ref:`ar4_datatype_SwBaseType` with optional data constraint and compuMethod.
Use the :ref:`Package.createImplementationDataType <ar4_package_Package_createImplementationDataType>` method to create basic implementation types.

Type References
~~~~~~~~~~~~~~~

You can also create an implementation data type that references another implementation data type. This is known as *typedef* in the C programming language.
Use the :ref:`Package.createImplementationDataTypeRef <ar4_package_Package_createImplementationDataTypeRef>` method to create type references.

Pointer Types
~~~~~~~~~~~~~

You can create data types that are pointers to base types. A future release should be able to support pointers to other implementation types.
Use the :ref:`Package.createImplementationDataTypePtr <ar4_package_Package_createImplementationDataTypePtr>` method to create pointer types.

Array Types
~~~~~~~~~~~

You can create implementation data types that are arrays of other implementation data types.
Use the :ref:`ar4_package_Package_createImplementationArrayDataType` to create array data types.

Record Types
~~~~~~~~~~~~

You can create implementation data types that are records of other implementation data types.
Use the :ref:`ar4_package_Package_createImplementationRecordDataType` to create record data types.

Note: Record types are sometimes called structs or structure types.

Constructor
-----------

.. py:method:: datatype.ImplementationDataType(name, [variantProps = None], [dynamicArraySizeProfile = None], [typeEmitter = None], [category='VALUE'], [parent = None], [adminData = None])

   :param str name: Short name.
   :param variantProps: variant properties.
   :type variantProps: None, :ref:`ar4_base_SwDataDefPropsConditional`, list
   :param dynamicArraySizeProfile: Dynamic array size profile.
   :type dynamicArraySizeProfile: None, str
   :param typeEmitter: Type emitter
   :type typeEmitter: None, str
   :param category: Category string.
   :type category: None, str
   :param parent: Parent package.
   :type parent: None, :ref:`ar4_package_Package`
   :param adminData: Admin data.
   :type adminData: None, :ref:`ar4_base_AdminData`

Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +-----------------------------+-----------------------------------------------------------+------------------------------+
    | Name                        | Type                                                      | Description                  |
    +=============================+===========================================================+==============================+
    | **dynamicArraySizeProfile** | None, str                                                 | <DYNAMIC-ARRAY-SIZE-PROFILE> |
    +-----------------------------+-----------------------------------------------------------+------------------------------+
    | **subElements**             | list of :ref:`ar4_datatype_ImplementationDataTypeElement` | <SUB-ELEMENTS>               |
    +-----------------------------+-----------------------------------------------------------+------------------------------+
    | **symbolProps**             | None, :ref:`ar4_base_SymbolProps`                         | <SYMBOL-PROPS>               |
    +-----------------------------+-----------------------------------------------------------+------------------------------+
    | **typeEmitter**             | None, str                                                 | <TYPE-EMITTER>               |
    +-----------------------------+-----------------------------------------------------------+------------------------------+
    | **variantProps**            | list of :ref:`ar4_base_SwDataDefPropsConditional`         | <SW-DATA-DEF-PROPS>          |
    +-----------------------------+-----------------------------------------------------------+------------------------------+

Properties
----------

..  table::
    :align: left

    +----------------------------+--------------+-------------+--------------------------------------------------------------------------+
    | Name                       | Type         | Access Type | Description                                                              |
    +============================+==============+=============+==========================================================================+
    | **arraySize**              | int          | Get         | Returns the array size of first *subElements* element                    |
    +----------------------------+--------------+-------------+--------------------------------------------------------------------------+
    | **baseTypeRef**            | str          | Get         | Returns the base type reference of first *subElements* element           |
    +----------------------------+--------------+-------------+--------------------------------------------------------------------------+
    | **compuMethodRef**         | str          | Get         | Returns the CompuMethod reference of first *subElements* element         |
    +----------------------------+--------------+-------------+--------------------------------------------------------------------------+
    | **dataConstraintRef**      | str          | Get         | Returns the data constraint reference of first *subElements* element     |
    +----------------------------+--------------+-------------+--------------------------------------------------------------------------+
    | **implementationTypeRef**  | str          | Get         | Returns the implementation type reference of first *subElements* element |
    +----------------------------+--------------+-------------+--------------------------------------------------------------------------+



Public Methods
--------------

* :ref:`ar4_datatype_ImplementationDataType_setSymbolProps`

Method Description
------------------

.. _ar4_datatype_ImplementationDataType_setSymbolProps:

setSymbolProps
~~~~~~~~~~~~~~

.. py:method:: ImplementationDataType.setSymbolProps([name = None], [symbol = None])

   :param name: Short name.
   :type name: None, str
   :param symbol: Symbol name.
   :type symbol: None, str

   Assigns the symbolProps attribute by creating a new instance of :ref:`ar4_base_SymbolProps`.
