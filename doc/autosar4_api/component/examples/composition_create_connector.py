import autosar

def init_workspace():
    ws = autosar.workspace("4.2.2")
    datatypes = ws.createPackage('DataTypes')
    datatypes.createSubPackage('BaseTypes')
    datatypes.createSubPackage('ImplementationTypes', role='DataType')
    datatypes.createSubPackage('CompuMethods', role='CompuMethod')
    datatypes.createSubPackage('DataConstrs', role='DataConstraint')
    datatypes.createSubPackage('Units', role='Unit')
    ws.createPackage("Constants", role = "Constant")
    ws.createPackage("PortInterfaces", role="PortInterface")
    ws.createPackage("ComponentTypes")
    return ws


def create_data_types(ws):
    basetypes = ws.find('DataTypes/BaseTypes')
    uint8_base = basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    uint16_base = basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    implTypes = ws.find('DataTypes/ImplementationTypes')
    uint8_impl = implTypes.createImplementationDataType('uint8', uint8_base.ref, 0, 255, typeEmitter='Platform_Type')
    uint16_impl = implTypes.createImplementationDataType('uint16', uint16_base.ref, 0, 65535, typeEmitter='Platform_Type')
    implTypes.createImplementationDataTypeRef('Inactive_Active_T',
                                                uint8_impl.ref,
                                                valueTable = [
                                                    'Inactive_Active_Inactive',
                                                    'Inactive_Active_Active',
                                                    'Inactive_Active_Error',
                                                    'Inactive_Active_NotAvailable',
                                                ])
    implTypes.createImplementationDataTypeRef('VehicleSpeed_T',
                                                uint16_impl.ref,
                                                offset = 0,
                                                scaling = 1/256,
                                                unit="KmPerHour",
                                                forceFloat=True)
    implTypes.createImplementationDataTypeRef('EngineSpeed_T',
                                                uint16_impl.ref,
                                                offset = 0,
                                                scaling = 1/8,
                                                unit="RotationPerMinute",
                                                forceFloat=True)


def create_port_interfaces(ws):
    portInterfaces = ws.find('/PortInterfaces')
    portInterfaces.createSenderReceiverInterface('VehicleOverSpeed_I',
                                                    autosar.element.DataElement('VehicleOverSpeed', 'Inactive_Active_T'))
    portInterfaces.createSenderReceiverInterface('EngineOverSpeed_I',
                                                    autosar.element.DataElement('EngineOverSpeed', 'Inactive_Active_T'))
    portInterfaces.createSenderReceiverInterface('VehicleSpeed_I',
                                                    autosar.element.DataElement('VehicleSpeed', 'VehicleSpeed_T'))
    portInterfaces.createSenderReceiverInterface('EngineSpeed_I',
                                                    autosar.element.DataElement('EngineSpeed', 'EngineSpeed_T'))


def create_constants(ws):
    constants = ws['Constants']
    constants.createConstant('VehicleOverSpeed_IV', 'Inactive_Active_T', 3)
    constants.createConstant('EngineOverSpeed_IV', 'Inactive_Active_T', 3)
    constants.createConstant('VehicleSpeed_IV', 'VehicleSpeed_T', 65535)
    constants.createConstant('EngineSpeed_IV', 'EngineSpeed_T', 65535)

def create_components(ws):
    components = ws['ComponentTypes']
    app1 = components.createApplicationSoftwareComponent("Application1")
    app1.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
    app1.createRequirePort('EngineSpeed', 'EngineSpeed_I', initValueRef = 'EngineSpeed_IV')
    app1.createProvidePort('VehicleOverSpeed', 'VehicleOverSpeed_I', initValueRef = 'VehicleOverSpeed_IV')
    app1.createProvidePort('EngineOverSpeed', 'EngineOverSpeed_I', initValueRef = 'EngineOverSpeed_IV')

    app2 = components.createApplicationSoftwareComponent("Application2")
    app2.createRequirePort('VehicleOverSpeed', 'VehicleOverSpeed_I', initValueRef = 'VehicleOverSpeed_IV')
    app2.createRequirePort('EngineOverSpeed', 'EngineOverSpeed_I', initValueRef = 'EngineOverSpeed_IV')


    swc = components.createCompositionComponent("MyComposition")
    swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
    swc.createRequirePort('EngineSpeed', 'EngineSpeed_I', initValueRef = 'EngineSpeed_IV')

    #Add child components
    swc.createComponentPrototype(app1.ref)
    swc.createComponentPrototype(app2.ref)

    #Create connectors
    swc.createConnector('VehicleSpeed', 'Application1/VehicleSpeed')
    swc.createConnector('EngineSpeed', 'Application1/EngineSpeed')

if __name__ == "__main__":
    ws = init_workspace()
    create_data_types(ws)
    create_port_interfaces(ws)
    create_constants(ws)
    create_components(ws)
    ws.saveXML("DataTypes.arxml", filters=["/DataTypes"])
    ws.saveXML("Constants.arxml", filters=["/Constants"])
    ws.saveXML("PortInterfaces.arxml", filters=["/PortInterfaces"])
    ws.saveXML("ComponentTypes.arxml", filters=["/ComponentTypes"])