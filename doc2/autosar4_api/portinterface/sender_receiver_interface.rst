.. _ar4_portinterface_SenderReceiverInterface:

SenderReceiverInterface
=======================

.. table::
   :align: left

   +--------------------+-----------------------------------------------------------------------------+
   | XML tag            | <SENDER-RECEIVER-INTERFACE>                                                 |
   +--------------------+-----------------------------------------------------------------------------+
   | Module             | autosar.portinterface                                                       |
   +--------------------+-----------------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.portinterface.PortInteface <ar4_portinterface_portinterface>` |
   +--------------------+-----------------------------------------------------------------------------+

A sender receiver interface is the most common type of port interface.
It contains a set of data elements that can be used to send and receive data

Factory Methods
---------------

* :ref:`Package.createSenderReceiverInterface <ar4_package_Package_createSenderReceiverInterface>`


Attributes
----------

..  table::
    :align: left

    +--------------------------+----------------------------+-------------------------------+
    | Name                     | Type                       | Description                   |
    +==========================+============================+===============================+
    | **dataElements**         | *list(DataElement)*        | List of data elements         |
    +--------------------------+----------------------------+-------------------------------+
    | **invalidationPolicies** | *list(InvalidationPolicy)* | List of invalidation policies |
    +--------------------------+----------------------------+-------------------------------+


Public Methods
--------------

* :ref:`SenderReceiverInterface_append`


Method Description
------------------

.. _SenderReceiverInterface_append:

append
~~~~~~

..  py:method:: SenderReceiverInterface.append(elem)

    Appends a child element to this port interface.

    * If the type of elem is DataElement it will be appended to dataElements
    * If the type of elem is InvalidationPolicy it will be appended to invalidationPolicies

    :param elem: child element to be appended
    :type elem: DataElement or InvalidationPolicy

Example
^^^^^^^

.. include:: examples/creating_sender_receiver_interface.py
    :code: python3
