.. _ar4_behavior_ModeSwitchEvent:

ModeSwitchEvent
===============

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <SWC-MODE-SWITCH-EVENT>                                                 |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.behavior                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.behavior.Event <ar4_behavior_Event>`                      |
    +--------------+-------------------------------------------------------------------------+

Factory Methods
---------------

* :ref:`SwcInternalBehavior.createModeSwitchEvent <ar4_behavior_Behavior_createModeSwitchEvent>`

Attributes
-----------

For inherited attributes see :ref:`ar4_behavior_Event`.

..  table::
    :align: left

    +--------------------------+---------------------------+--------------------------------------+
    | Name                     | Type                      | Description                          |
    +==========================+===========================+======================================+
    | **modeInstRef**          | *str*                     | Reference to mode                    |
    +--------------------------+---------------------------+--------------------------------------+
    | **activationType**       | *str*                     | Activation type                      |
    +--------------------------+---------------------------+--------------------------------------+
    
**activationType**

* ON-ENTRY
* ON-EXIT
    

