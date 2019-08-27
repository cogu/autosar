.. _portinterface_ClientServerInterface:

ClientServerInterface
=====================

.. table::
   :align: left

   +--------------------+-------------------------------------------------------------------------+
   | XML tag            | <CLIENT-SERVER-INTERFACE>                                               |
   +--------------------+-------------------------------------------------------------------------+
   | Module             | autosar.portinterface                                                   |
   +--------------------+-------------------------------------------------------------------------+
   | Inherits           | :ref:`autosar.portinterface.PortInteface <portinterface_portinterface>` |
   +--------------------+-------------------------------------------------------------------------+

Client Server interfaces contains a set of callable operations.
Operations are called by one or more client SWCs and are (usually) served by a single server SWC.

Usage
-----

.. code-block:: python

   import autosar
   
   ... #Create packages and port interfaces
   
    NvM_RequestResultType_ref = "/Predefined_DEV/ImplementationDataTypes/NvM_RequestResultType"
    boolean_ref = "/AUTOSAR_Platform/ImplementationDataTypes/boolean"
    dtRef_const_VOID_ref = "/AUTOSAR_Platform/ImplementationDataTypes/dtRef_const_VOID"
    dtRef_VOID_ref = "/AUTOSAR_Platform/ImplementationDataTypes/dtRef_VOID"

    package = ws.find('/PortInterfaces')
    portInterface=package.createClientServerInterface("NvM_RequestResultType", operations = [
        "EraseBlock",
        "GetErrorStatus",
        "InvalidateNvBlock",
        "ReadBlock",
        "SetRamBlockStatus",
        "WriteBlock"],
        errors = autosar.ApplicationError("E_NOT_OK", 1), isService=True)
        
        portInterface["EraseBlock"].possibleErrors = "E_NOT_OK"
        portInterface["GetErrorStatus"].createOutArgument("ErrorStatus", NvM_RequestResultType_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
        portInterface["GetErrorStatus"].possibleErrors = "E_NOT_OK"
        portInterface["InvalidateNvBlock"].possibleErrors = "E_NOT_OK"
        portInterface["ReadBlock"].createInArgument("DstPtr", dtRef_VOID_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
        portInterface["ReadBlock"].possibleErrors = "E_NOT_OK"
        portInterface["SetRamBlockStatus"].createInArgument("RamBlockStatus", boolean_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
        portInterface["SetRamBlockStatus"].possibleErrors = "E_NOT_OK"
        portInterface["WriteBlock"].createInArgument("SrcPtr", dtRef_const_VOID_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
        portInterface["WriteBlock"].possibleErrors = "E_NOT_OK"

Factory Methods
---------------

* :ref:`Package.createClientServerInterface <package_createClientServerInterface>`


Attributes
----------

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

* :ref:`ClientServerInterface_append`


Method Description
------------------

.. _ClientServerInterface_append:

append
~~~~~~

..  py:method:: ClientServerInterface.append(elem)

    Adds element to the self.operations or self.applicationErrors lists depending on type.
    
    :param elem: Element
    :type elem: :ref:`portinterface_Operation` or ApplicationError





