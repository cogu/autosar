.. _ar4_behavior_TimingEvent:

TimingEvent
===========

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <TIMING-EVENT>                                                          |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.behavior                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.behavior.Event <ar4_behavior_Event>`                      |
    +--------------+-------------------------------------------------------------------------+

Factory Methods
---------------

* :ref:`SwcInternalBehavior.createTimerEvent <ar4_behavior_Behavior_createTimerEvent>`

Attributes
-----------

For inherited attributes see :ref:`ar4_behavior_Event`.

..  table::
    :align: left

    +--------------------------+---------------------------+----------------------------------------+
    | Name                     | Type                      | Description                            |
    +==========================+===========================+========================================+
    | **period**               | *int*                     | Cycle period in milliseconds           |
    +--------------------------+---------------------------+----------------------------------------+
    
