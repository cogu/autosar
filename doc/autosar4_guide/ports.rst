Ports
=====

A SoftwareComponent encapsulates a set of related functions and/or data. The component commmunicates with the outside world exclusively using *ports*.
The ports are a part of the component and represents its interface. In AUTOSAR, this is called the :ref:`Port Interface <ar4_portinterface_Portinterface>`

In general, there are two types of ports:

- Require Port (R-Port)
- Provide Port (P-Port)

For the most part the they are the same, the main difference is the **direction** of the port.

.. image:: /_static/autosar_component.png

Port Interfaces
---------------

Ports are created from *port interfaces*. They come in different types.

- SenderReceiverPortInterface
- ClientServerPortInterface
- ParameterPortInterface
- ModeSwitchPortInterface
- NvDataPortInterface

SenderReceiverPortInterface
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SenderReceiverPortInterface is the traditional interface used for sending and receiving automotive *signals*.
It integrates well with automotive buses such as CAN and LIN (which are primarily signal-based buses).

The RTE function prefixes are:

- Rte_Write (P-Port, Non-Queued)
- Rte_Read  (R-Port, Non-Queued)
- Rte_Send  (P-Port, Queued)
- Rte_Receive (R-Port, Queued)

ClientServerPortInterface
~~~~~~~~~~~~~~~~~~~~~~~~~

ClientServer ports are used by SoftwareComponents when requesting services located in BSW (usually through service-mapping) or in another SoftwareComponent.
The function call can be configured to be either synchronous or asynchronous through configuration.

The RTE function prefixes are:

- Rte_Call (R-Port)

For server ports (or P-Ports), the user can select any function name as long as it it's known by the RTE during generation (we will cover this later).

ParameterPortInterface
~~~~~~~~~~~~~~~~~~~~~~

Parameter ports are used for parameter data, sometimes known as calibration data. They are usually read-only data values which
controls the behavior of SoftwareComponents.

The RTE function prefixes are:

- Rte_Prm (R-Port)

ModeSwitchPortInterface
~~~~~~~~~~~~~~~~~~~~~~~

Mode ports are used to react to mode changes in the ECU.

The RTE function prefixes are:

- Rte_Mode (R-Port)
- Rte_Switch (P-Port)

NvDataPortInterface
~~~~~~~~~~~~~~~~~~~

The non-volatile data port interface is used exclusively by the NvBlock SoftwareComponent.

ComSpec
-------

The Communication Specification (ComSpec) is used to describe specific communication needs of a port.
This can include information such as init-values or queue-length.

For more details about which ComSpecs are supported from Python see the :ref:`ComponentType API <ar4_component_ComponentType>`.

Port Creation Examples
----------------------

Example 1: SenderReceiver ports with single data element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create components with a single port which contains one data element.
Here you can give the ComSpec arguments directly to the port creation function call.
Use keyword **initValueRef** instead of **initValue** if you intend to
use constants as port initialier.

.. include:: examples/create_sender_receiver_port_single_elem.py
    :code: python3

Example 2: SenderReceiver ports with multiple data elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create components with a single port which contains two data elements.
Here you have to explicitly give a **comspec** argument containing a list of dictionaries.

.. include:: examples/create_sender_receiver_port_multi_elem.py
    :code: python3


Example 3: ClientServer port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an NVM-related client-server interface and use it as both client
and server ports.

.. include:: examples/create_client_server_port.py
    :code: python3
