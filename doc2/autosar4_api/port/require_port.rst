.. _ar4_port_RequirePort:

RequirePort
===========

.. table::
   :align: left

   +--------------------+------------------------------------------+
   | XML tag            | <R-PORT-PROTOTYPE>                       |
   +--------------------+------------------------------------------+
   | Module             | autosar.port                             |
   +--------------------+------------------------------------------+
   | Inherits           | :ref:`autosar.port.Port <ar4_port_Port>` |
   +--------------------+------------------------------------------+

Factory Methods
---------------

* :ref:`ComponentType.createRequirePort <ar4_component_ComponentType_createRequirePort>`

Public Methods
--------------

* :ref:`copy <ar4_port_RequirePort_copy>`
* :ref:`mirror <ar4_port_RequirePort_mirror>`


Method Description
------------------

.. _ar4_port_RequirePort_copy:

copy
~~~~

..  py:method:: RequirePort.copy()

Returns a new port that is a copy of itself.

.. _ar4_port_RequirePort_mirror:

mirror
~~~~~~

..  py:method:: RequirePort.mirror()

Returns a :ref:`ar4_port_ProvidePort` object based on attributes in this port.
