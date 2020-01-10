SWC Behavior
============

The behavior object is a container for runnables, events and other objects. All SWCs has its own behavior object, except for compositions.

In AUTOSAR4, the behavior object is an instance of the SwcInternalBehavior class and it is created automatically when you create SWCs using these helper methods:

- Package.createApplicationSoftwareComponent
- Package.createServiceComponent
- Package.createComplexDeviceDriverComponent

Runnables
---------

Runnables are execution points. They are implemented as C functions and are triggered by events.

Examples:

.. code-block:: python

    ws = autosar.workspace(version="4.2.2")
    #... Datatypes, port interfaces and constants are loaded or created here

    package = ws.createPackage('ComponentTypes', role='ComponentType')
    swc = package.createApplicationSoftwareComponent('MyApplication')
    swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
    swc.createRequirePort('EngineSpeed', 'EngineSpeed_I', initValueRef = 'EngineSpeed_IV')

    swc.behavior.createRunnable('runnableName', portAccess=['VehicleSpeed', 'EngineSpeed'])


Port Access
^^^^^^^^^^^

Port access is a list of intent. This is where you list which SWC data elements (sender-receiver interface) or
operations (client-server interface) that you intend to call from this runnable.
It is important that you correctly fill in the port access list since it is used by the RTE generator.

In those cases where your port only as a single data element it is enough to just give the name of the port (as a string).
If you want to declare a specific data-element or operation use a front-slash as a seprator

Examples:

.. code-block:: python

    ws = autosar.workspace(version="4.2.2")
    #... Datatypes, port interfaces and constants are loaded or created here

    package = ws.createPackage('ComponentTypes', role='ComponentType')
    swc = package.createApplicationSoftwareComponent('MyApplication')
    swc.createRequirePort('FreeRunningTimer', 'FreeRunningTimer_I') #port interface has operations GetTime and IsTimerElapsed
    swc.behavior.createRunnable('runnableName',
                                portAccess=['FreeRunningTimer/GetTime', 'FreeRunningTimer/IsTimerElapsed'])

Timer Events
------------



Mode Switch Events
------------------

Data Events
-----------



