.. _ar4_behavior:

SwcInternalBehavior
===================

.. table::
   :align: left

   +--------------------+------------------------------------------------------+
   | XML tag            | <SWC-INTERNAL-BEHAVIOR>                              |
   +--------------------+------------------------------------------------------+
   | Module             | autosar.behavior                                     |
   +--------------------+------------------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------------+------------------------------------------------------+

This is the internal behavior class for AUTOSAR4 SWCs.

Attributes
----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

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

* :ref:`ar4_behavior_Behavior_createRunnable`
* :ref:`ar4_behavior_Behavior_createModeSwitchEvent`
* :ref:`ar4_behavior_Behavior_createTimerEvent`
* :ref:`ar4_behavior_Behavior_createOperationInvokedEvent`
* :ref:`ar4_behavior_Behavior_createDataReceivedEvent`
* :ref:`ar4_behavior_Behavior_createExclusiveArea`
* :ref:`ar4_behavior_Behavior_createInitEvent`
* :ref:`ar4_behavior_Behavior_createRunnable`


Method Description
------------------

.. _ar4_behavior_Behavior_createRunnable:

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

.. _ar4_behavior_Behavior_createModeSwitchEvent:

createModeSwitchEvent
~~~~~~~~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createModeSwitchEvent(runnableName, modeRef, [activationType = 'ENTRY'], [name = None])

    :param str runnableName: Name of (aldready existing) runnable to trigger when event occurs
    :param str modeRef: Mode reference
    :param str activationType: Activation type
    :param str name: Override of the shortName of this event. If left as None a (unique) default name will be generated.
    :rtype: :ref:`ar4_behavior_ModeSwitchEvent`

    Creates a new :ref:`ar4_behavior_ModeSwitchEvent` object and appends it to this object.

**activationType**

* ENTRY (Will be automatically converted to "ON-ENTRY")
* EXIT  (Will be automatically converted to "ON-EXIT")
* ON-ENTRY
* ON-EXIT

.. _ar4_behavior_Behavior_createTimerEvent:

createTimerEvent
~~~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createTimerEvent(runnableName, period, [modeDependency = None], [name = None])

    :param str runnableName: Name of (aldready existing) runnable to trigger when event occurs
    :param str period: Cycle time in milliseconds
    :param list modeDependency: Optional mode disabling settings for this event
    :param str name: Override of the shortName of this event. If left as None a (unique) default name will be generated.
    :rtype: :ref:`ar4_behavior_TimingEvent`

    Creates a new :ref:`ar4_behavior_TimingEvent` object and appends it to this object.

.. _ar4_behavior_Behavior_createOperationInvokedEvent:

createOperationInvokedEvent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createOperationInvokedEvent(runnableName, operationRef, [modeDependency = None], [name = None])

    :param str runnableName: Name of (aldready existing) runnable to trigger when event occurs
    :param str operationRef: Reference to operation
    :param list modeDependency: Optional mode disabling settings for this event
    :param str name: Override of the shortName of this event. If left as None a (unique) default name will be generated.
    :rtype: :ref:`ar4_behavior_OperationInvokedEvent`

    Creates a new :ref:`ar4_behavior_OperationInvokedEvent` object and appends it to this object.



.. _ar4_behavior_Behavior_createDataReceivedEvent:

createDataReceivedEvent
~~~~~~~~~~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createDataReceivedEvent(runnableName, dataElementRef, [modeDependency=None], [name=None] )

    :param str runnableName: Name of (aldready existing) runnable to trigger when event occurs
    :param str dataElementRef: Reference to DataElement
    :param list modeDependency: Optional mode disabling settings for this event
    :param str name: Override of the shortName of this event. If left as None a (unique) default name will be generated.
    :rtype: :ref:`ar4_behavior_DataReceivedEvent`

    Creates a new :ref:`ar4_behavior_DataReceivedEvent` object and appends it to this object.

.. _ar4_behavior_Behavior_createExclusiveArea:

createExclusiveArea
~~~~~~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createExclusiveArea(name)

    :param str name: ShortName of exclusive area
    :rtype: :ref:`ar4_behavior_ExclusiveArea`

    Creates a new :ref:`ar4_behavior_ExclusiveArea` object and appends it to this object.


createPerInstanceMemory
~~~~~~~~~~~~~~~~~~~~~~~

createSharedDataParameter
~~~~~~~~~~~~~~~~~~~~~~~~~

createNvmBlock
~~~~~~~~~~~~~~

.. _ar4_behavior_Behavior_createInitEvent:

createInitEvent
~~~~~~~~~~~~~~~

..  py:method:: SwcInternalBehavior.createInitEvent(runnableName, [modeDependency=None], [name=None] )

    :param str runnableName: Name of (aldready existing) runnable to trigger when event occurs
    :param list modeDependency: Optional mode disabling settings for this event
    :param str name: Override of the shortName of this event. If left as None a (unique) default name will be generated.
    :rtype: :ref:`ar4_behavior_InitEvent`

    Creates a new :ref:`ar4_behavior_InitEvent` and appends it to this object.

createModeSwitchAckEvent
~~~~~~~~~~~~~~~~~~~~~~~~
