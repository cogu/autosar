.. _component_atomic_swc:

AtomicSoftwareComponent
=======================

.. table::
   :align: left

   +--------------------+----------------------------------------------------------------------+
   | XML tag            | (abstract class)                                                     |
   +--------------------+----------------------------------------------------------------------+
   | Module             | autosar.component                                                    |
   +--------------------+----------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.component.ComponentType <ar4_component_ComponentType>` |
   +--------------------+----------------------------------------------------------------------+

Base class for all component type classes except :ref:`ar4_component_CompositionComponent`.

Attributes
-----------

..  table::
    :align: left

    +--------------------------+--------------------------------------+---------------------------+
    | Name                     | Type                                 | Description               |
    +==========================+======================================+===========================+
    | **behavior**             | autosar.behavior.SwcInternalBehavior | InternalBehavior object   |
    +--------------------------+--------------------------------------+---------------------------+
    | **implementation**       | autosar.component.SwcImplementation  | Implementation object     |
    +--------------------------+--------------------------------------+---------------------------+

Public Methods
--------------

* :ref:`find <component_atomic_swc_find>`


Method Description
--------------------

.. _component_atomic_swc_find:

find
~~~~~

..  method:: AtomicSoftwareComponent.find(ref : str)

    Similar to :ref:`ComponentType.find <ar4_component_ComponentType_find>` but also finds objects inside the behavior object.
