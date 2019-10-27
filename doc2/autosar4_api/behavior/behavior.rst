.. _ar4_behavior:

SwcInternalBehavior
===================

.. table::
   :align: left
   
   +--------------------+-------------------------------------------+
   | XML tag            | <SWC-INTERNAL-BEHAVIOR>                   |
   +--------------------+-------------------------------------------+
   | Module             | autosar.behavior                          |
   +--------------------+-------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <element>`  |
   +--------------------+-------------------------------------------+
   
This is the internal behavior class for AUTOSAR4 SWCs.

Attributes
----------

..  table::
    :align: left

    +--------------------------+---------------------------+--------------------------------------+
    | Name                     | Type                      | Description                          |
    +==========================+===========================+======================================+
    | **componentRef**         | str                       | Reference to SWC prototype           |
    +--------------------------+---------------------------+--------------------------------------+
    | **events**               | *list(Event)*             | Events                               |
    +--------------------------+---------------------------+--------------------------------------+
    | **exclusiveAreas**       | *list(ExclsiveArea)*      | Exclusive areas                      |
    +--------------------------+---------------------------+--------------------------------------+
    | **multipleInstance**     | bool                      | Enables/disabled Multiple instances  |
    +--------------------------+---------------------------+--------------------------------------+
    | **perInstanceMemories**  | *list(PerInstanceMemory)* | PerInstanceMemory objects            |
    +--------------------------+---------------------------+--------------------------------------+
    | **portAPIOptions**       | *list(PortAPIOption)*     | Port API options                     |
    +--------------------------+---------------------------+--------------------------------------+
    | **runnables**            | *list(Runnable)*          | Runnables                            |
    +--------------------------+---------------------------+--------------------------------------+
    
    
    
    
    
    


Public Methods
--------------

* :ref:`ar4_behavior_createRunnable`


Method Description
------------------

.. _ar4_behavior_createRunnable:

createRunnable
~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createRunnable(name, [portAccess=None], [symbol=None], [concurrent=False], [exclusiveAreas=None], [adminData=None])

    :param str name: ShortName of the runnable
    :param portAccess: Select which ports this runnable will access
    :type portAccess: list(str)
    :param str symbol: Used to override the generated C symbol (default is to use the name)
    :param bool concurrent: Selects if this runnable can run concurrently
    :param exclusiveAreas: Select which exclusive areas this runnable will use
    :type exclusiveAreas: list(str)
    :param adminData: Optional AdminData
