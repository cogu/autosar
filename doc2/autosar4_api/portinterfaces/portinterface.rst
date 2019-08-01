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

* :ref:`portinterface_SenderReceiverInterface`


Attributes
----------

..  table::
    :align: left

    +--------------------------+--------------------------+-------------------------------+
    | Name                     | Type                     | Description                   |
    +==========================+==========================+===============================+        
    | **dataElements**         | list[DataElement]        | List of data elements         |
    +--------------------------+--------------------------+-------------------------------+
    | **isService**            | Boolean                  | Is this a service interface?  |
    +--------------------------+--------------------------+-------------------------------+
    | **serviceKind**          | str                      | Optional service kind string  |
    +--------------------------+--------------------------+-------------------------------+
