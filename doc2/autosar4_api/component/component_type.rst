..  _ar4_component_ComponentType:

ComponentType
=============

.. table::
   :align: left

   +--------------------+------------------------------------+
   | XML tag            | (abstract class)                   |
   +--------------------+------------------------------------+
   | Module             | autosar.component                  |
   +--------------------+------------------------------------+
   | Inherits           | autosar.element.Element            |
   +--------------------+------------------------------------+

The ComponentType class is the base class for :ref:`component_atomic_swc` and :ref:`component_compositionComponent`.

Attributes
----------

..  table::
    :align: left

    +------------------------+---------------------------------------------+---------------------------------+
    | Name                   | Type                                        | Description                     |
    +========================+=============================================+=================================+
    | **providePorts**       | *list(:ref:`ar4_port_ProvidePort`)*         | Provide ports in this component |
    +------------------------+---------------------------------------------+---------------------------------+
    | **requirePorts**       | *list(:ref:`ar4_port_RequirePort`)*         | Require ports in this componen  |
    +------------------------+---------------------------------------------+---------------------------------+

Public Methods
--------------

* :ref:`ar4_component_ComponentType_find`
* :ref:`ar4_component_ComponentType_createProvidePort`
* :ref:`ar4_component_ComponentType_createRequirePort`


Method Description
--------------------

.. _ar4_component_ComponentType_find:

find
~~~~~~~

.. method:: ComponentType.find(ref : str)

    Find port based in info in reference string.

    :param str ref: Reference string


.. _ar4_component_ComponentType_createProvidePort:

createProvidePort
~~~~~~~~~~~~~~~~~~~~

.. method::  ComponentType.createProvidePort(name, portInterfaceRef, [elemName=None], [initValueRef=None], [canInvalidate=False])

    Creates new ProvidePort on this component.

    :param str name: ShortName for the new port
    :param str portInterfaceRef: Reference to port interface
    :param str elemName: ShortName of inner dataElement (default uses same name as the port)
    :param str initValueRef: Reference to init value (constant object)
    :param bool canInvalidate: sets the canInvalidate attribute on the port
    :rtype: :ref:`ProvidePort <ar4_port_ProvidePort>`

.. _ar4_component_ComponentType_createRequirePort:

createRequirePort
~~~~~~~~~~~~~~~~~

.. method::  ComponentType.createRequirePort(name, portInterfaceRef, \*\*kwargs)

    Creates new RequirePort on this component.

    :param str name: ShortName for the new port
    :param str portInterfaceRef: Reference to port interface
    :param kwargs: Additional arguments (see below)
    :rtype: :ref:`RequirePort <ar4_port_RequirePort>`

Creating ports from SenderReceiverInterface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Optional kwarg parameters in createRequirePort method**

.. table::
   :align: left

   +------------------+---------------------+--------------------------------------------------------------+
   | Parameter name   | Type                | Description                                                  |
   +==================+=====================+==============================================================+
   | comspec          | list                | Use to take direct control of comspec creation               |
   +------------------+---------------------+--------------------------------------------------------------+
   | initValue        | int, float, str     | Used to set an init value literal.                           |
   |                  |                     | Mutually exclusive to initValueRef.                          |
   +------------------+---------------------+--------------------------------------------------------------+
   | initValueRef     | str                 | Reference to existing constant specification                 |
   |                  |                     | Mutually exclusive to initValue.                             |
   +------------------+---------------------+--------------------------------------------------------------+
   | aliveTimeout     | int                 | Alive timeout setting (in seconds).                          |
   +------------------+---------------------+--------------------------------------------------------------+
   | queueLength      | int                 | Length of queue (only applicable for queued port interfaces  |
   +------------------+---------------------+--------------------------------------------------------------+


Examples
++++++++

**Create port from SenderReceiver PortInterface containing a single data element**

.. include:: examples/creating_require_port.py
    :code: python3

**Create port from SenderReceiver PortInterface containing multiple data elements**

.. include:: examples/creating_multi_elem_require_port.py
    :code: python3
