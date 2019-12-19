.. _ar4_component_ComponentPrototype:

ComponentPrototype
==================

.. table::
    :align: left

    +--------------+-------------------------------------------------------------------------+
    | XML tag      | <SW-COMPONENT-PROTOTYPE>                                                |
    +--------------+-------------------------------------------------------------------------+
    | Module       | autosar.submodule                                                       |
    +--------------+-------------------------------------------------------------------------+
    | Inherits     | :ref:`autosar.element.Element <ar4_element>`                            |
    +--------------+-------------------------------------------------------------------------+

Component prototypes are used as child objects to :ref:`ar4_component_CompositionComponent` objects.

Factory Methods
---------------

* :ref:`CompositionComponent.createComponentPrototype <ar4_component_CompositionComponent_createComponentPrototype>`

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element>`.

..  table::
    :align: left

    +--------------------------+---------------------------+--------------------------------------+
    | Name                     | Type                      | Description                          |
    +==========================+===========================+======================================+
    | **typeRef**              | str                       | Referenced component                 |
    +--------------------------+---------------------------+--------------------------------------+
