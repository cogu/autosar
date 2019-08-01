..  _component_type:

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
   
The ComponentType class is the base class for :ref:`atomic_swc` and :ref:`composition_swc`.

Attributes
----------
    
.. attribute:: ComponentType.providePorts
        
        List of provide ports in this component. Default is an empty list.
        
.. attribute:: ComponentType.requirePorts
        
        List of provide ports in this component. Default is an empty list.

Public Methods
--------------

* :ref:`find <component_type_find>`
* :ref:`createProvidePort <component_type_createProvidePort>`
* :ref:`createRequirePort <component_type_createRequirePort>`


Method Description
--------------------

.. _component_type_find:

find
~~~~~~~

.. method:: ComponentType.find(ref : str)

    Find port based in info in reference string.
    
    :param str ref: Reference string


.. _component_type_createProvidePort:

createProvidePort
~~~~~~~~~~~~~~~~~~~~

.. method::  ComponentType.createProvidePort(name, portInterfaceRef, [elemName=None], [initValueRef=None], [canInvalidate=False])

    Creates new ProvidePort on this component.

    :param str name: ShortName for the new port
    :param str portInterfaceRef: Reference to port interface
    :param str elemName: ShortName of inner dataElement (default uses same name as the port)
    :param str initValueRef: Reference to init value (constant object)
    :param bool canInvalidate: sets the canInvalidate attribute on the port    
    :rtype: :ref:`ProvidePort <port_ProvidePort>`
    
.. _component_type_createRequirePort:

createRequirePort
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. method::  ComponentType.createRequirePort(name, portInterfaceRef, \*\*kwargs)
   
    Creates new RequirePort on this component.

    :param str name: ShortName for the new port
    :param str portInterfaceRef: Reference to port interface
    :param kwargs: Additional arguments (see below)
    :rtype: :ref:`RequirePort <port_RequirePort>`

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




