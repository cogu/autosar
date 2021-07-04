.. _ar4_datatype_DataConstraint:

DataConstraint
==============

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <DATA-CONSTR>                                        |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
    +--------------------+------------------------------------------------------+

A DataConstraint is used to decorate other data types with one or more constraints.
Use the *dataConstraintRef* property of the :ref:`ar4_datatype_ApplicationDataType` or :ref:`ar4_datatype_ImplementationDataType` classes to access the reference string.

Usage
-----

..  include:: examples/usage_data_constraint.py
    :code: python3

Factory Methods
---------------

Implicit factory methods
~~~~~~~~~~~~~~~~~~~~~~~~

* :ref:`ar4_package_Package_createImplementationDataType`
* :ref:`ar4_package_Package_createImplementationDataTypeRef`

Explicit factory methods
~~~~~~~~~~~~~~~~~~~~~~~~

* :ref:`ar4_package_Package_createInternalDataConstraint`
* :ref:`ar4_package_Package_createPhysicalDataConstraint`


Constructor
-----------

.. py:method:: datatype.DataConstraint(name, rules, [constraintLevel = None], [parent = None], [adminData = None])

    :param str name: Short name.
    :param rules: Constraint rules
    :type rule: dict, list of dict
    :param constraintLevel: Optional constraint level.
    :type constraintLevel: None or int
    :param parent: parent package.
    :type parent: :ref:`ar4_package_Package`
    :param adminData: Optional AdminData.
    :type adminData: None, :ref:`ar4_base_AdminData`.


    The rule parameter should either be a dictionary or a list of dictionaries.
    Each dictionary in *rules* is expected to have three keys:

    * type: ('internalConstraint' or 'physicalConstraint').
    * lowerLimit: Lower limit of the constraint (int, float).
    * upperLimit: Lower limit of the constraint (int, float).
    * lowerLimitType: Type of lower limit (:literal:`'OPEN'`, :literal:`'CLOSED'`).
    * upperLimitType: Type of lower limit (:literal:`'OPEN'`, :literal:`'CLOSED'`).


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +-------------------------------+--------------------------------------------------+------------------------------------------------+
    | Name                          | Type                                             | Description                                    |
    +===============================+==================================================+================================================+
    | **level**                     | None, int                                        | <CONSTR-LEVEL>                                 |
    +-------------------------------+--------------------------------------------------+------------------------------------------------+
    | **rules**                     | list of InternalConstraint or PhysicalConstraint | <DATA-CONSTR-RULE>                             |
    +-------------------------------+--------------------------------------------------+------------------------------------------------+

Public Properties
-----------------

All properties are limited to situations where the constraint only has one internal rule. Multi-rule support will be added in a future release.

..  table::
    :align: left

    +--------------------------+---------------+-------------+
    | Name                     | Type          | Access Type |
    +==========================+===============+=============+
    | **constraintLevel**      | int           | Get         |
    +--------------------------+---------------+-------------+
    | **lowerLimit**           | int, float    | Get         |
    +--------------------------+---------------+-------------+
    | **upperLimit**           | int, float    | Get         |
    +--------------------------+---------------+-------------+
    | **lowerLimitType**       | str           | Get         |
    +--------------------------+---------------+-------------+
    | **upperLimitType**       | str           | Get         |
    +--------------------------+---------------+-------------+

Public Methods
--------------

Most methods are currently limited to situations where the constraint only has one internal rule. Multi-rule support will be added in a future release.

* :ref:`ar4_datatype_DataConstraint_checkValue`
* :ref:`ar4_datatype_DataConstraint_findByType`

Method Description
------------------

.. _ar4_datatype_DataConstraint_checkValue:

checkValue
~~~~~~~~~~~

.. py:method:: DataConstraint.checkValue(v)

    :param v: Value.
    :type v: int, float

    Checks if value *v* is inside the limits of the data constraint. If the value is outside then a DataConstraintError will be raised.

.. _ar4_datatype_DataConstraint_findByType:

findByType
~~~~~~~~~~

.. py:method:: DataConstraint.findByType(constraintType = 'internalConstraint')

    :param str constraintType: Constraint type (:literal:`'internalConstraint'`, :literal:`'physicalConstraint'`).

    Returns the first constraint rule that matches given constraint type.
