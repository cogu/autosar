.. _component_compositionComponent:

CompositionComponent
====================

.. table::
   :align: left

   +--------------------+----------------------------------------------------------------------+
   | XML tag            | <COMPOSITION-SW-COMPONENT-TYPE>                                      |
   +--------------------+----------------------------------------------------------------------+
   | Module             | autosar.component                                                    |
   +--------------------+----------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.component.ComponentType <ar4_component_ComponentType>` |
   +--------------------+----------------------------------------------------------------------+

The CompositionComponent class is used to instantiate inner components inside a new component boundary as a means of abstraction.

Factory Methods
---------------

* :ref:`Package.createCompositionComponent <ar4_package_Package_createCompositionComponent>`

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element>`.

..  table::
    :align: left

    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+
    | Name                     | Type                                        | Description                                                          |
    +==========================+=============================================+======================================================================+
    | **components**           | *list(:ref:`ar4_component_ComponentType`)*  | List of internal components                                          |
    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+
    | **assemblyConnectors**   | *list(AssemblyConnector)*                   | List of connectors between internal components                       |
    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+
    | **delegationConnectors** | *list(DelegationConnector)*                 | List of connectors between inner components and composition boundary |
    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+


Public Methods
--------------

* :ref:`ar4_component_CompositionComponent_createComponentPrototype`

Method Description
------------------

.. _ar4_component_CompositionComponent_createComponentPrototype:

createComponentPrototype
~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: CompositionComponent.createComponentPrototype(componentRef)

    :param str componentRef: Reference to an object derived from ref:`ar4_component_ComponentType`
    :rtype ComponentPrototype:

    Creates an inner component prototype and appends it to the components list.




