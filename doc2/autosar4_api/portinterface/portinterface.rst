.. _portinterface_portinterface:

PortInterface
=============

.. table::
   :align: left

   +--------------------+-------------------------------------------+
   | XML tag            | (Abstract class)                          |
   +--------------------+-------------------------------------------+
   | Module             | autosar.portinterface                     |
   +--------------------+-------------------------------------------+
   | Inherits           | :ref:`autosar.element.Element <element>`  |
   +--------------------+-------------------------------------------+

Base class for AUTOSAR port interfaces.

**Derived Classes**:

* :ref:`portinterface_SenderReceiverInterface`
* :ref:`portinterface_ClientServerInterface`


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
