.. _ar4_mode_ModeGroup:

ModeGroup
=========

.. table::
   :align: left

   +--------------+-------------------------------------------------------------------------+
   | XML tag      | <MODE_GROUP>                                                            |
   +--------------+-------------------------------------------------------------------------+
   | Module       | autosar.mode                                                            |
   +--------------+-------------------------------------------------------------------------+
   | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
   +--------------+-------------------------------------------------------------------------+

A ModeGroup is used as the internal storage container of the modeGroup attribute of the :ref:`ar4_portinterface_ModeSwitchInterface` class.

Usage
-----

..  include:: examples/usage_mode_group.py
    :code: python3

Constructor
-----------

.. py:method:: mode.ModeGroup(name, typeRef, [parent=None], [adminData=None])

    :param str name: ShortName of the object
    :param str typeRef: Full reference to a :ref:`ar4_mode_ModeDeclarationGroup` element or a shortName of a :ref:`ar4_mode_ModeDeclarationGroup` element (if package roles are used).
    :param parent: parent package (for internal use only)
    :param adminData: optional adminData


Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+-------------------------+-------------------------------------------------------------+
    | Name                     | Type                    | Description                                                 |
    +==========================+=========================+=============================================================+
    | **typeRef**              | str                     | Reference to a :ref:`ar4_mode_ModeDeclarationGroup` element |
    +--------------------------+-------------------------+-------------------------------------------------------------+
