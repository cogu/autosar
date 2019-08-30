import autosar

def init_ws():
    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    baseTypes = package.createSubPackage('BaseTypes')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    implTypes = package.createSubPackage('ImplementationTypes')
    implTypes.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535,
                                                        baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')    
    implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255,
                                                        baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    implTypes.createImplementationDataTypeRef('PercentLevel_T', lowerLimit=0, upperLimit = 255,
                                              implementationTypeRef = '/DataTypes/ImplementationTypes/uint8',
                                              offset=0, scaling=0.4, unit='Percent', forceFloat=True)
    implTypes.createImplementationDataTypeRef('VoltageLevel_T', lowerLimit=0, upperLimit = 65535,
                                              implementationTypeRef = '/DataTypes/ImplementationTypes/uint16',
                                              offset=0, scaling=1/64, unit='Volt', forceFloat=True)
    package = ws.createPackage('PortInterfaces', role='PortInterface')
    package.createSenderReceiverInterface('BatteryStat_I',
                                        [
                                            autosar.element.DataElement('ChargeLevel', '/DataTypes/ImplementationTypes/PercentLevel_T'),
                                            autosar.element.DataElement('VoltageLevel', '/DataTypes/ImplementationTypes/VoltageLevel_T')
                                        ])
    return ws


ws = init_ws()    
#Create SWC
package = ws.createPackage('ComponentTypes', role='ComponentType')
swc = package.createApplicationSoftwareComponent('SWC2')
#Create new RequirePort with multiple comspecs
swc.createRequirePort('BatteryStat', 'BatteryStat_I', comspec = [
    {'dataElement': 'ChargeLevel', 'initValue': 255, 'aliveTimeout': 30},
    {'dataElement': 'VoltageLevel', 'initValue': 65535, 'aliveTimeout': 30}
])    
#save SWC to XML
ws.saveXML('{}.arxml'.format(swc.name), filters=['/ComponentTypes/{}'.format(swc.name)])