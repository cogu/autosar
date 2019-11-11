.. _ar4_port_ProvidePort:

ProvidePort
===========

.. table::
   :align: left

   +--------------------+------------------------------------------+
   | XML tag            | <P-PORT-PROTOTYPE>                       |
   +--------------------+------------------------------------------+
   | Module             | autosar.port                             |
   +--------------------+------------------------------------------+
   | Inherits           | :ref:`autosar.port.Port <ar4_port_Port>` |
   +--------------------+------------------------------------------+

Factory Methods
---------------

* :ref:`ComponentType.createProvidePort <ar4_component_ComponentType_createProvidePort>`

Public Methods
--------------

* :ref:`copy <ar4_port_ProvidePort_copy>`
* :ref:`mirror <ar4_port_ProvidePort_mirror>`



Method Description
------------------

.. _ar4_port_ProvidePort_copy:

copy
~~~~

..  py:method:: ProvidePort.copy()

Returns a new port that is a copy of itself.

.. _ar4_port_ProvidePort_mirror:

mirror
~~~~~~

..  py:method:: ProvidePort.mirror()

Returns a :ref:`ar4_port_RequirePort` object based on attributes in this port.
