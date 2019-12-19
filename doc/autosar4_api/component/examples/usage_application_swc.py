import autosar

def init_ws():
    ws = autosar.workspace(version="4.2.2")
    #Create Packages
    datatypes = ws.createPackage('DataTypes', role='DataType')
    datatypes.createSubPackage('CompuMethods', role='CompuMethod')
    datatypes.createSubPackage('DataConstrs', role='DataConstraint')    
    basetypes = datatypes.createSubPackage('BaseTypes')
    portinterfaces = ws.createPackage('PortInterfaces', role="PortInterface")
    components = ws.createPackage('ComponentTypes', role='ComponentType')
    constants = ws.createPackage('Constants', role='Constant')
    #Create DataTypes    
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    datatypes.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    #Create Constants
    constants.createConstant('VehicleSpeed_IV', 'uint16', 65535)
    constants.createConstant('EngineSpeed_IV', 'uint16', 65535)
    #Create PortInterfaces
    portinterfaces.createSenderReceiverInterface('VehicleSpeed_I', autosar.element.DataElement('VehicleSpeed', 'uint16'))
    portinterfaces.createSenderReceiverInterface('EngineSpeed_I', autosar.element.DataElement('EngineSpeed', 'uint16'))
    return ws


ws = init_ws()
components = ws.find('/ComponentTypes')
swc = components.createApplicationSoftwareComponent('SWC1')
swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV', aliveTimeout=30)
swc.createRequirePort('EngineSpeed', 'EngineSpeed_I', initValueRef = 'EngineSpeed_IV', aliveTimeout=30)

#save SWC1 into separate ARXML file
ws.saveXML('{}.arxml'.format(swc.name), filters=['/ComponentTypes/{}'.format(swc.name)])