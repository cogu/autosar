.. _ar4_datatype_CompuMethod:

CompuMethod
===========

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <COMPU-METHOD>                                       |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
    +--------------------+------------------------------------------------------+

A CompuMethod or *computation method* is used to decorate other data types with additional information.
The *compuMethodRef* attribute of the :ref:`ar4_datatype_ApplicationDataType` or :ref:`ar4_datatype_ImplementationDataType` is used to
associate a data type with a certain CompuMethod.

Primary uses for CompuMethods are:

* Scaling (rational/linear)
* ValueTables/Enumerations
* Bit masks

Usage
-----

..  include:: examples/usage_compu_method.py
    :code: python3

Factory Methods
---------------

CompuMethods can be implictly created while creating :ref:`ar4_datatype_ApplicationDataType` or :ref:`ar4_datatype_ImplementationDataType` but
they can also be explicitly created using the package API:

* :ref:`Package.createCompuMethodConst <ar4_package_Package_createCompuMethodConst>`
* :ref:`Package.createCompuMethodRational <ar4_package_Package_createCompuMethodRational>`
* :ref:`Package.createCompuMethodRationalPhys <ar4_package_Package_createCompuMethodRationalPhys>`

To allow Python to implictly create CompuMethods while creating data types you must first assign the *compuMethod* and the *unit* roles on packages 
or sub-packages in your workspace. For more information about package roles, see :ref:`ar4_Roles`.

Constructor
-----------

.. py:method:: datatype.CompuMethod(name, useIntToPhys, usePhysToInt, [unitRef = None], [category = None], [parent = None], [adminData = None])

    :param str name: Short name.
    :param bool useIntToPhys: Uses internal to physical computation (False, True).
    :param bool usePhysToInt: Uses physical to internal computation (False, True).
    :param unitRef: Optional reference to :ref:`ar4_datatype_Unit`.
    :type unitRef: None, str
    :param category: Category string.
    :type categry: None, str
    :param parent: parent package.
    :type parent: None, :ref:`ar4_package_Package`
    :param adminData: Optional AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`.


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +-------------------------------+-----------------------------------------+------------------------------------------------+
    | Name                          | Type                                    | Tag                                            |
    +===============================+=========================================+================================================+
    | **unitRef**                   | None or str                             | <UNIT-REF>                                     |
    +-------------------------------+-----------------------------------------+------------------------------------------------+
    | **intToPhys**                 | None or :ref:`ar4_datatype_Computation` | <COMPU-INTERNAL-TO-PHYS>                       |
    +-------------------------------+-----------------------------------------+------------------------------------------------+
    | **physToInt**                 | None or :ref:`ar4_datatype_Computation` | <COMPU-PHYS-TO-INTERNAL>                       |
    +-------------------------------+-----------------------------------------+------------------------------------------------+
