.. _mode_modeGroup:

ModeGroup
=========

.. table::
   :align: left

   +--------------+-------------------------------------------------------------------------+
   | XML tag      | <MODE_GROUP>                                                            |
   +--------------+-------------------------------------------------------------------------+
   | Module       | autosar.submodule                                                       |
   +--------------+-------------------------------------------------------------------------+
   | Inherits     | :ref:`autosar.element.Element <ar4_element>`                            |
   +--------------+-------------------------------------------------------------------------+

A ModeGroup is used as the internal storage container of the modeGroup attribute of the :ref:`ar4_portinterface_ModeSwitchInterface` class.

Usage
-----

.. code-block:: python

    import autosar

    modeGroup = autosar.mode.ModeGroup('mode', '/ModeDeclrs/VehicleMode')

Constructor
-----------

.. py:method:: mode.ModeGroup(name, typeRef, [parent=None], [adminData=None])

    :param str name: ShortName of the object
    :param str typeRef: Full reference to a :ref:`mode_modeDeclarationGroup` element or a shortName of a :ref:`mode_modeDeclarationGroup` element (if package roles are used).
    :param parent: parent package (for internal use only)
    :param adminData: optional adminData


Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element>`.

..  table::
    :align: left

    +--------------------------+-------------------------+---------------------------------------------------------+
    | Name                     | Type                    | Description                                             |
    +==========================+=========================+=========================================================+
    | **typeRef**              | str                     | Reference to a :ref:`mode_modeDeclarationGroup` element |
    +--------------------------+-------------------------+---------------------------------------------------------+
