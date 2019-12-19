.. _ar4_component_CompositionComponent:

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

For inherited attributes see :ref:`Element <ar4_element>`.

..  table::
    :align: left

    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+
    | Name                     | Type                                        | Description                                                          |
    +==========================+=============================================+======================================================================+
    | **components**           | list(:ref:`ar4_component_ComponentType`)    | List of internal components                                          |
    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+
    | **assemblyConnectors**   | list(AssemblyConnector)                     | List of connectors between internal components                       |
    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+
    | **delegationConnectors** | list(DelegationConnector)                   | List of connectors between inner components and composition boundary |
    +--------------------------+---------------------------------------------+----------------------------------------------------------------------+


Public Methods
--------------

* :ref:`ar4_component_CompositionComponent_createComponentPrototype`
* :ref:`ar4_component_CompositionComponent_createConnector`

Method Description
------------------

.. _ar4_component_CompositionComponent_createComponentPrototype:

createComponentPrototype
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: CompositionComponent.createComponentPrototype(componentRef, [name = None])

    :param str componentRef: Reference to an object derived from :ref:`ar4_component_ComponentType`
    :param str name: Optional name of the inner component. If left unset it will copy the name from the referenced component.
    :rtype: :ref:`ar4_component_ComponentPrototype`

    Creates an inner component prototype and appends it to the components list.

Example
^^^^^^^

.. include:: examples/composition_create_component_prototype.py
    :code: python


.. _ar4_component_CompositionComponent_createConnector:

createConnector
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:method:: CompositionComponent.createConnector(portRef1, portRef2)

    :param str portRef1: Reference to first port
    :param str portRef2: Reference to second port

    Creates a connector between two ports.

**Valid Port reference formats**:

+----------------------------+------------------------------------------+--------------------------------------+
| Format                     | Example                                  | Description                          |
+============================+==========================================+======================================+
| **portName**               | \\"VehicleSpeed\\"                       | Name of port on the composition      |
+----------------------------+------------------------------------------+--------------------------------------+
| **componentName/portName** | \\"Swc1/VehicleSpeed\\"                  | Name of port on an inner component   |
+----------------------------+------------------------------------------+--------------------------------------+
| **portRef**                | \\"/ComponentTypes/Swc1/VehicleSpeed\\"  | Full port reference                  |
+----------------------------+------------------------------------------+--------------------------------------+

Example
^^^^^^^

.. include:: examples/composition_create_connector.py
    :code: python


