Modes
=====

Modes are states in state machines that are running in the vehicle. SWCs can react to modes either as events (mode switch events) or
they can choose to allow certain runnables to be active only in certain modes.

A set of states is called a mode declaration group which acts as a container of sorts for the mode (state) names.

Creating a Mode Declaration Group package
-----------------------------------------

It is recommended that you create a unique AUTOSAR package to hold your mode declaration groups. Remember to use the role "ModeDclrGroup".

.. code-block:: python

    import autosar
    
    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    
Creating Mode Declaration Groups
--------------------------------

Remember to check with your AUTOSAR vendor which mode groups you should use and what their definitions are.
Here is an example containing a made up mode declaration group called *BswM_Mode* with the following mode declarations (state names):

- POSTRUN
- RUN
- SHUTDOWN
- STARTUP (initial state)
- WAKEUP

.. code-block:: python

    import autosar

    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    package.createModeDeclarationGroup('BswM_Mode', ["POSTRUN",
                                                    "RUN",
                                                    "SHUTDOWN",
                                                    "STARTUP",
                                                    "WAKEUP"], "STARTUP")

In addition, you can also set a category and adminData for your newly created mode declaration group.
