.. _ar4_portinterface_portinterface:

PortInterface
=============

.. table::
   :align: left

   +--------------------+----------------------------------------------+
   | XML tag            | (Abstract class)                             |
   +--------------------+----------------------------------------------+
   | Module             | autosar.portinterface                        |
   +--------------------+----------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <ar4_element>` |
   +--------------------+----------------------------------------------+

Base class for AUTOSAR port interfaces.

**Derived Classes**:

* :ref:`ar4_portinterface_SenderReceiverInterface`
* :ref:`ar4_portinterface_ClientServerInterface`
* :ref:`ar4_portinterface_ModeSwitchInterface`


Attributes
----------

..  table::
    :align: left

    +--------------------------+--------------------------+-------------------------------+
    | Name                     | Type                     | Description                   |
    +==========================+==========================+===============================+
    | **isService**            | Boolean                  | Is this a service interface?  |
    +--------------------------+--------------------------+-------------------------------+
    | **serviceKind**          | str                      | Optional service kind string  |
    +--------------------------+--------------------------+-------------------------------+
