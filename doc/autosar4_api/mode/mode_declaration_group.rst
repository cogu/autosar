.. _mode_modeDeclarationGroup:

ModeDeclarationGroup
====================

.. table::
   :align: left

   +--------------+-------------------------------------------------------------------------+
   | XML tag      | <MODE-DECLARATION-GROUP>                                                |
   +--------------+-------------------------------------------------------------------------+
   | Module       | autosar.mode                                                            |
   +--------------+-------------------------------------------------------------------------+
   | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>`                    |
   +--------------+-------------------------------------------------------------------------+

A collection of :ref:`Mode Declarations <mode_declaration>`.

Usage
-----

.. code-block:: python

    import autosar

    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
    package.createModeDeclarationGroup('BswM_Mode', ["POSTRUN",
                                                    "RUN",
                                                    "SHUTDOWN",
                                                    "STARTUP",
                                                    "WAKEUP"], "STARTUP")

Factory Methods
---------------

* :ref:`Package.createModeDeclarationGroup <ar4_package_Package_createModeDeclarationGroup>`

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+-------------------------------+-------------------------------+
    | Name                     | Type                          | Description                   |
    +==========================+===============================+===============================+
    | **modeDeclarations**     | list(:ref:`mode_declaration`) | List of mode declarations     |
    +--------------------------+-------------------------------+-------------------------------+
    | **initialModeRef**       | str                           | Initial mode value            |
    +--------------------------+-------------------------------+-------------------------------+
