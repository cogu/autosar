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
