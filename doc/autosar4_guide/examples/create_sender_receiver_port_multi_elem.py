import autosar
import autosar.element

def create_workspace_and_packages():
    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')    
    package.createSubPackage('ImplementationTypes')
    ws.createPackage('PortInterfaces', role='PortInterface')
    ws.createPackage('ComponentTypes', role='ComponentType')
    return ws

def create_data_types(ws):
    baseTypes = ws.find('/DataTypes/BaseTypes')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    implTypes = ws.find('/DataTypes/ImplementationTypes')
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

def create_port_interfaces(ws):
    package = ws.find('/PortInterfaces')
    package.createSenderReceiverInterface('BatteryStat_I',
        [
            autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'ChargeLevel', '/DataTypes/ImplementationTypes/PercentLevel_T'),
            autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'VoltageLevel', '/DataTypes/ImplementationTypes/VoltageLevel_T')
        ])

def create_components(ws):
    package = ws.find('/ComponentTypes')
    comp1 = package.createApplicationSoftwareComponent('Component1')
    comp1.createProvidePort('BatteryStat', 'BatteryStat_I', comspec = 
        [
            {'dataElement': 'ChargeLevel', 'initValue': 255},
            {'dataElement': 'VoltageLevel', 'initValue': 65535}
        ])

    
    comp2 = package.createApplicationSoftwareComponent('Component2')
    comp2.createRequirePort('BatteryStat', 'BatteryStat_I', comspec = 
        [
            {'dataElement': 'ChargeLevel', 'initValue': 255, 'aliveTimeout': 30},
            {'dataElement': 'VoltageLevel', 'initValue': 65535, 'aliveTimeout': 30}
        ])

ws = create_workspace_and_packages()
create_data_types(ws)
create_port_interfaces(ws)
create_components(ws)
ws.saveXML('Component1.arxml', filters=['/ComponentTypes/Component1'])
ws.saveXML('Component2.arxml', filters=['/ComponentTypes/Component2'])
ws.saveXML('DataTypes.arxml', filters=['/DataTypes'])
ws.saveXML('PortInterfaces.arxml', filters = ["/PortInterfaces"])