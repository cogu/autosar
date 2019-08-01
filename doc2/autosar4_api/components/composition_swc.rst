.. _composition_swc:

CompositionComponent
====================

.. table::
   :align: left

   +--------------------+------------------------------------------------------------+
   | XML tag            | <COMPOSITION-SW-COMPONENT-TYPE>                            |
   +--------------------+------------------------------------------------------------+
   | Module             | autosar.component                                          |
   +--------------------+------------------------------------------------------------+
   | Inherits           | :ref:`autosar.component.ComponentType <component_type>`    |
   +--------------------+------------------------------------------------------------+

Factory Methods
---------------

* :ref:`Package.createCompositionComponent <package_createCompositionComponent>`

Attributes
----------

.. table::
   :align: left

   +--------------+-----------------------------+------------------+
   | Type         |  Name                       |  Default Value   |
   +==============+=============================+==================+
   | list         | :ref:`components`           |  \[ \]           |
   +--------------+-----------------------------+------------------+


Detailed Description
--------------------

The CompositionSoftwareComponent class is used to aggregate SWCs inside a boundary as a means of abstraction.
It also contains connectors that connect the inner SWCs together (assembly connectors) as well as
connectors that connect the inner SWCs to the composition boundary (delegation connectors).

Attribute Documentation
-----------------------

.. _components:

components
~~~~~~~~~~

List of instantiated components that are part of this composition. Use the member method createComponentPrototype to add new components.

