.. _ar4_mode_ModeDeclarationGroup:

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

A collection of :ref:`Mode Declarations <ar4_mode_ModeDeclaration>`.

Usage
-----

..  include:: examples/usage_mode_declaration_group.py
    :code: python3

Factory Methods
---------------

* :ref:`Package.createModeDeclarationGroup <ar4_package_Package_createModeDeclarationGroup>`

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+---------------------------------------+-------------------------------+
    | Name                     | Type                                  | Description                   |
    +==========================+=======================================+===============================+
    | **modeDeclarations**     | list(:ref:`ar4_mode_ModeDeclaration`) | List of mode declarations     |
    +--------------------------+---------------------------------------+-------------------------------+
    | **initialModeRef**       | str                                   | Initial mode value            |
    +--------------------------+---------------------------------------+-------------------------------+
