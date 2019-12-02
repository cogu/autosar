.. _ar4_portinterface_ClientServerInterface:

ClientServerInterface
=====================

.. table::
   :align: left

   +--------------------+-----------------------------------------------------------------------------+
   | XML tag            | <CLIENT-SERVER-INTERFACE>                                                   |
   +--------------------+-----------------------------------------------------------------------------+
   | Module             | autosar.portinterface                                                       |
   +--------------------+-----------------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>` |
   +--------------------+-----------------------------------------------------------------------------+

Client Server interfaces contains a set of callable operations.
Operations are called by one or more client SWCs and are (usually) served by a single server SWC.

Usage
-----

.. include:: examples/usage_client_server_interface.py
    :code: python3

Factory Methods
---------------

* :ref:`Package.createClientServerInterface <ar4_package_Package_createClientServerInterface>`


Attributes
----------

For inherited attributes see :ref:`autosar.portinterface.PortInteface <ar4_portinterface_Portinterface>`.

..  table::
    :align: left

    +--------------------------+--------------------------+-----------------------------------------+
    | Name                     | Type                     | Description                             |
    +==========================+==========================+=========================================+
    | **operations**           | *list(Operation)*        | Operations in this interface            |
    +--------------------------+--------------------------+-----------------------------------------+
    | **applicationErrors**    | *list(ApplicationError)* | Application errors in this interface    |
    +--------------------------+--------------------------+-----------------------------------------+


Public Methods
--------------

* :ref:`ar4_portinterface_ClientServerInterface_append`


Method Description
------------------

.. _ar4_portinterface_ClientServerInterface_append:

append
~~~~~~

..  py:method:: ClientServerInterface.append(elem)

    Adds element to the self.operations or self.applicationErrors lists depending on type.

    :param elem: Element
    :type elem: :ref:`ar4_portinterface_Operation` or ApplicationError
