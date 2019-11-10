.. _ar4_behavior_Runnable:

RunnableEntity
==============

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <RUNNABLE-ENTITY>                                                       |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.behavior                                                        |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element>`                            |
    +--------------+-------------------------------------------------------------------------+
   
AUTOSAR Runnable

Factory Methods
---------------

* :ref:`ar4_behavior_Behavior_createRunnable`

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element>`.

..  table::
    :align: left

    +---------------------------+---------------------------------+---------------------------------------+
    | Name                      | Type                            | Description                           |
    +==========================+==================================+=======================================+
    | **symbol**                | *str*                           | Target language symbol name           |
    +---------------------------+---------------------------------+---------------------------------------+
    | **dataReceivePoints**     | *list(DataReceivePoint)*        | Used for port access                  |
    +---------------------------+---------------------------------+---------------------------------------+
    | **dataSendPoints**        | *list(DataSendPoint)*           | Used for port access                  |
    +---------------------------+---------------------------------+---------------------------------------+
    | **serverCallPoints**      | *list(SyncServerCallPoint)*     | Used for port access                  |
    +---------------------------+---------------------------------+---------------------------------------+
    | **exclusiveAreaRefs**     | *list(str)*                     | Used for exclusive area access        |
    +---------------------------+---------------------------------+---------------------------------------+
    | **modeAccessPoints**      | *list(ModeAccessPoint)*         | Used for port access                  |
    +---------------------------+---------------------------------+---------------------------------------+
    | **modeSwitchPoints**      | *list(ModeSwitchPoint)*         | Used for mode-switch event triggering |
    +---------------------------+---------------------------------+---------------------------------------+
    | **parameterAccessPoints** | *list(ParameterAccessPoint)*    | Used for parameter access             |
    +---------------------------+---------------------------------+---------------------------------------+
    

Public Methods
--------------

Method Description
------------------

