.. _ar4_datatype_Unit:

Unit
====

.. table::
    :align: left

    +--------------------+------------------------------------------------------+
    | XML tag            | <UNIT>                                               |
    +--------------------+------------------------------------------------------+
    | Module             | autosar.datatype                                     |
    +--------------------+------------------------------------------------------+
    | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
    +--------------------+------------------------------------------------------+

Units are used to name physical units.

Usage
-----

..  include:: examples/usage_unit.py
    :code: python3

Factory Methods
---------------

* :ref:`Package.createUnit <ar4_package_Package_createUnit>`

Units can also be created automatically while creating application or implementation data types. 
For this mechanism to work you must first set the *Unit* :ref:`package rols <ar4_Roles>`.

Constructor
-----------

.. py:method:: datatype.Unit(name, displayName, [factor = None], [offset = None], [parent = None])

    :param str name: Short name.
    :param bool displayName: Display name.
    :param factor: Scaling factor.
    :type factor: None, int, float
    :param offset: Scaling offset.
    :type offset: None, int, float
    :param parent: Parent package.
    :type parent: :ref:`ar4_package_Package`


Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

.. table::
    :align: left

    +-------------------------+--------------------+-------------------------------------------------+
    | Name                    | Type               | Description                                     |
    +=========================+====================+=================================================+
    | **displayName**         | str                | <DISPLAY-NAME> (Could be the same as shortName) |
    +-------------------------+--------------------+-------------------------------------------------+
    | **factor**              | None, int or float | <FACTOR-SI-TO-UNIT>                             |
    +-------------------------+--------------------+-------------------------------------------------+
    | **offset**              | None, int or float | <OFFSET-SI-TO-UNIT>                             |
    +-------------------------+--------------------+-------------------------------------------------+
