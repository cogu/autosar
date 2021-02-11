..  _ar4_component_ComponentType:

ComponentType
=============

.. table::
   :align: left

   +--------------------+------------------------------------------------------+
   | XML tag            | (abstract class)                                     |
   +--------------------+------------------------------------------------------+
   | Module             | autosar.component                                    |
   +--------------------+------------------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------------+------------------------------------------------------+

The ComponentType class is the base class for :ref:`ar4_component_AtomicSoftwareComponent` and :ref:`ar4_component_CompositionComponent`.

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
~~~~

.. method:: ComponentType.find(ref : str)

    Find port based in info in reference string.

    :param str ref: Reference string


.. _ar4_component_ComponentType_createProvidePort:

createProvidePort
~~~~~~~~~~~~~~~~~~~~

.. method::  ComponentType.createProvidePort(name, portInterfaceRef, **kwargs)

    Creates new ProvidePort on this component.

    :param str name: ShortName for the new port
    :param str portInterfaceRef: Reference to port interface
    :param kwargs: Additional arguments depending on port interface type (see below)
    :rtype: :ref:`RequirePort <ar4_port_ProvidePort>`

.. _ar4_component_ComponentType_createRequirePort:

createRequirePort
~~~~~~~~~~~~~~~~~

.. method::  ComponentType.createRequirePort(name, portInterfaceRef, **kwargs)

    Creates new RequirePort on this component.

    :param str name: ShortName for the new port
    :param str portInterfaceRef: Reference to port interface
    :param kwargs: Additional arguments depending on port interface type (see below)
    :rtype: :ref:`RequirePort <ar4_port_RequirePort>`


Additional arguments for :ref:`SenderReceiverInterface <ar4_portinterface_SenderReceiverInterface>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. table::
   :align: left

   +------------------+---------------------+-------------------------------------------------------------------+
   | Parameter name   | Type                | Description                                                       |
   +==================+=====================+===================================================================+
   | comspec          | dict, list(dict)    | Used primarily when port interface has multiple data elements     |
   +------------------+---------------------+-------------------------------------------------------------------+
   | dataElement      | str                 | Name of the data element this ComSpec refers to.                  |
   |                  |                     |                                                                   |
   |                  |                     | For single-element port interfaces this parameter is not required |
   +------------------+---------------------+-------------------------------------------------------------------+
   | initValue        | int, float, str     | Used to set an init value literal.                                |
   |                  |                     | Mutually exclusive to initValueRef.                               |
   +------------------+---------------------+-------------------------------------------------------------------+
   | initValueRef     | str                 | Reference to existing constant specification                      |
   |                  |                     | Mutually exclusive to initValue.                                  |
   +------------------+---------------------+-------------------------------------------------------------------+
   | aliveTimeout     | int                 | Alive timeout setting (in seconds).                               |
   +------------------+---------------------+-------------------------------------------------------------------+
   | queueLength      | int                 | Length of queue (only applicable for queued port interfaces       |
   +------------------+---------------------+-------------------------------------------------------------------+

Examples — SenderReceiverInterface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Port interface with single data element
+++++++++++++++++++++++++++++++++++++++

.. include:: ../../autosar4_guide/examples/create_sender_receiver_port_single_elem.py
    :code: python3

Port interface with multiple data elements
++++++++++++++++++++++++++++++++++++++++++

.. include:: ../../autosar4_guide/examples/create_sender_receiver_port_multi_elem.py
    :code: python3


Additional arguments for :ref:`ClientServerInterface <ar4_portinterface_ClientServerInterface>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. table::
   :align: left

   +------------------+---------------------+--------------------------------------------------------------+
   | Parameter name   | Type                | Description                                                  |
   +==================+=====================+==============================================================+
   | comspec          | dict, list(dict)    | Used primarily when port interface has multiple operations   |
   +------------------+---------------------+--------------------------------------------------------------+
   | operation        | int, float, str     | Used to set an init value literal.                           |
   |                  |                     | Mutually exclusive to initValueRef.                          |
   +------------------+---------------------+--------------------------------------------------------------+
   | queueLength      | int                 | Length of queue                                              |
   +------------------+---------------------+--------------------------------------------------------------+


Examples — ClientServerInterface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: ../../autosar4_guide/examples/create_client_server_port.py
    :code: python3

Additional arguments for :ref:`ParameterInterface <ar4_portinterface_ParameterInterface>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. table::
   :align: left

   +------------------+---------------------+--------------------------------------------------------------+
   | Parameter name   | Type                | Description                                                  |
   +==================+=====================+==============================================================+
   | comspec          | dict, list(dict)    | Used primarily when port interface has multiple parameters   |
   +------------------+---------------------+--------------------------------------------------------------+
   | parameter        | str                 | Specifices which parameter this ComSpec is for.              |
   |                  |                     |                                                              |
   |                  |                     | Not required when port interface has a single parameter.     |
   +------------------+---------------------+--------------------------------------------------------------+
   | initValue        | int, float, str     | Used to set an init value literal.                           |
   +------------------+---------------------+--------------------------------------------------------------+

Additional arguments for :ref:`ModeSwitchInterface <ar4_portinterface_ModeSwitchInterface>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Provide Ports:**

.. table::
   :align: left

   +----------------------+---------------------+--------------------------------------------------------------+
   | Parameter name       | Type                | Description                                                  |
   +======================+=====================+==============================================================+
   | comspec              | dict, list(dict)    | Used primarily when port interface has multiple parameters   |
   +----------------------+---------------------+--------------------------------------------------------------+
   | modeGroup            | str                 | Specifices the mode group name                               |
   +----------------------+---------------------+--------------------------------------------------------------+
   | enhancedMode         | bool                | Enhanced mode enable/disable                                 |
   +----------------------+---------------------+--------------------------------------------------------------+
   | queueLength          | int                 | Queue length                                                 |
   +----------------------+---------------------+--------------------------------------------------------------+
   | modeSwitchAckTimeout | int                 | Acknowledgement timeout in milliseconds                      |
   +----------------------+---------------------+--------------------------------------------------------------+

**Require Ports:**

.. table::
   :align: left

   +------------------+---------------------+--------------------------------------------------------------+
   | Parameter name   | Type                | Description                                                  |
   +==================+=====================+==============================================================+
   | comspec          | dict, list(dict)    | Used primarily when port interface has multiple parameters   |
   +------------------+---------------------+--------------------------------------------------------------+
   | modeGroup        | str                 | Specifices the mode group name                               |
   +------------------+---------------------+--------------------------------------------------------------+
   | enhancedMode     | bool                | Enhanced mode enable/disable                                 |
   +------------------+---------------------+--------------------------------------------------------------+
   | supportAsync     | bool                | Asynchronous support enable/disable                          |
   +------------------+---------------------+--------------------------------------------------------------+

Additional arguments for :ref:`NvDataInterface <ar4_portinterface_NvDataInterface>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Provide Ports:**

.. table::
   :align: left

   +----------------------+---------------------+--------------------------------------------------------------+
   | Parameter name       | Type                | Description                                                  |
   +======================+=====================+==============================================================+
   | comspec              | dict, list(dict)    | Used primarily when port interface has multiple parameters   |
   +----------------------+---------------------+--------------------------------------------------------------+
   | nvData               | str                 | Specifices the name of the data element.                     |
   |                      |                     |                                                              |
   |                      |                     | Not required when port interface only has one element.       |
   +----------------------+---------------------+--------------------------------------------------------------+
   | ramBlockInitValue    | int, float, str     | Init value literal for RAM block                             |
   +----------------------+---------------------+--------------------------------------------------------------+
   | ramBlockInitValueRef | str                 | Used when you want an existing constant as init value        |
   +----------------------+---------------------+--------------------------------------------------------------+
   | romBlockInitValue    | int, float, str     | Init value literal for ROM block                             |
   +----------------------+---------------------+--------------------------------------------------------------+
   | romBlockInitValueRef | str                 | Used when you want an existing constant as init value        |
   +----------------------+---------------------+--------------------------------------------------------------+

**Require Ports:**

.. table::
   :align: left

   +------------------+---------------------+--------------------------------------------------------------+
   | Parameter name   | Type                | Description                                                  |
   +==================+=====================+==============================================================+
   | comspec          | dict, list(dict)    | Used primarily when port interface has multiple parameters   |
   +------------------+---------------------+--------------------------------------------------------------+
   | nvData           | str                 | Specifices the name of the data element.                     |
   |                  |                     |                                                              |
   |                  |                     | Not required when port interface only has one element.       |
   +------------------+---------------------+--------------------------------------------------------------+
   | InitValue        | int, float, str     | Init value literal for RAM block                             |
   +------------------+---------------------+--------------------------------------------------------------+
   | InittValueRef    | str                 | Used when you want an existing constant as init value        |
   +------------------+---------------------+--------------------------------------------------------------+
