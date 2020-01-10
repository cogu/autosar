.. _ar4_portinterface_ModeSwitchInterface:

ModeSwitchInterface
=====================

.. table::
   :align: left

   +--------------------+-----------------------------------------------------------------------------+
   | XML tag            | <MODE-SWITCH-INTERFACE>                                                     |
   +--------------------+-----------------------------------------------------------------------------+
   | Module             | autosar.portinterface                                                       |
   +--------------------+-----------------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>` |
   +--------------------+-----------------------------------------------------------------------------+

Representa a ModeSwitch interface.

Usage
-----

.. include:: examples/usage_mode_switch_interface.py
    :code: python3

Factory Methods
---------------

* :ref:`ar4_package_Package_createModeSwitchInterface`

Attributes
----------

For inherited attributes see :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>`.

..  table::
    :align: left

    +--------------------------+----------------------------+-------------------------------+
    | Name                     | Type                       | Description                   |
    +==========================+============================+===============================+
    | **modeGroup**            | *:ref:`mode_modeGroup`*    | mode group                    |
    +--------------------------+----------------------------+-------------------------------+

Public Methods
--------------

Method Description
------------------
