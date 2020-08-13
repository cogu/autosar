import autosar

def create_platform_types(ws):
    ws.pushRoles()
    package = ws.createPackage('AUTOSAR_Platform')
    baseTypes = package.createSubPackage('BaseTypes', role = 'DataType')
    package.createSubPackage('CompuMethods', role = 'CompuMethod')
    package.createSubPackage('DataConstrs', role = 'DataConstraint')
    baseTypes.createSwBaseType('dtRef_const_VOID', 1, encoding = 'VOID', nativeDeclaration = 'void')
    baseTypes.createSwBaseType('dtRef_VOID', 1, encoding = 'VOID', nativeDeclaration = 'void')
    baseTypes.createSwBaseType('boolean', 8, encoding = 'BOOLEAN', nativeDeclaration='boolean')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    implTypes = package.createSubPackage('ImplementationDataTypes')
    implTypes.createImplementationDataType('boolean', '/AUTOSAR_Platform/BaseTypes/boolean',
        valueTable=['FALSE', 'TRUE'], typeEmitter='Platform_Type')
    implTypes.createImplementationDataTypePtr('dtRef_const_VOID',
        '/AUTOSAR_Platform/BaseTypes/dtRef_const_VOID', swImplPolicy = 'CONST')
    implTypes.createImplementationDataTypePtr('dtRef_VOID', '/AUTOSAR_Platform/BaseTypes/dtRef_VOID')
    ws.popRoles()
    ws.pushRoles()
    package = ws.createPackage('Predefined_DEV')
    package.createSubPackage('CompuMethods', role = 'CompuMethod')
    package.createSubPackage('DataConstrs', role = 'DataConstraint')
    implTypes = package.createSubPackage('ImplementationDataTypes')
    implTypes.createImplementationDataType('NvM_RequestResultType', '/AUTOSAR_Platform/BaseTypes/uint8',
        valueTable=[
                'NVM_REQ_OK',
                'NVM_REQ_NOT_OK',
                'NVM_REQ_PENDING',
                'NVM_REQ_INTEGRITY_FAILED',
                'NVM_REQ_BLOCK_SKIPPED',
                'NVM_REQ_NV_INVALIDATED'])
    ws.popRoles()

def create_port_interfaces(ws):
    package = ws.createPackage('PortInterfaces', role='PortInterface')
    portInterface=package.createClientServerInterface("NvM_RequestResultType",
        errors = autosar.ApplicationError("E_NOT_OK", 1),
        isService=True, operations = [
            "EraseBlock",
            "GetErrorStatus",
            "InvalidateNvBlock",
            "ReadBlock",
            "SetRamBlockStatus",
            "WriteBlock"])
    NvM_RequestResultType_ref = "/Predefined_DEV/ImplementationDataTypes/NvM_RequestResultType"
    boolean_ref = "/AUTOSAR_Platform/ImplementationDataTypes/boolean"
    dtRef_const_VOID_ref = "/AUTOSAR_Platform/ImplementationDataTypes/dtRef_const_VOID"
    dtRef_VOID_ref = "/AUTOSAR_Platform/ImplementationDataTypes/dtRef_VOID"
    portInterface["EraseBlock"].possibleErrors = "E_NOT_OK"
    portInterface["GetErrorStatus"].createOutArgument("ErrorStatus", NvM_RequestResultType_ref,
        "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
    portInterface["GetErrorStatus"].possibleErrors = "E_NOT_OK"
    portInterface["InvalidateNvBlock"].possibleErrors = "E_NOT_OK"
    portInterface["ReadBlock"].createInArgument("DstPtr", dtRef_VOID_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
    portInterface["ReadBlock"].possibleErrors = "E_NOT_OK"
    portInterface["SetRamBlockStatus"].createInArgument("RamBlockStatus", boolean_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
    portInterface["SetRamBlockStatus"].possibleErrors = "E_NOT_OK"
    portInterface["WriteBlock"].createInArgument("SrcPtr", dtRef_const_VOID_ref, "NOT-ACCESSIBLE", "USE-ARGUMENT-TYPE")
    portInterface["WriteBlock"].possibleErrors = "E_NOT_OK"


def create_components(ws):
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    comp1 = package.createServiceComponent('ServerComponent')
    comp1.createProvidePort('Nvm_PersonalSettings', 'NvM_RequestResultType')

    comp2 = package.createApplicationSoftwareComponent('ClientComponent')
    comp2.createRequirePort('Nvm_PersonalSettings', 'NvM_RequestResultType')

ws = autosar.workspace(version="4.2.2")
create_platform_types(ws)
create_port_interfaces(ws)
create_components(ws)
ws.saveXML('ServerComponent.arxml', filters=['/ComponentTypes/ServerComponent'])
ws.saveXML('ClientComponent.arxml', filters=['/ComponentTypes/ClientComponent'])
