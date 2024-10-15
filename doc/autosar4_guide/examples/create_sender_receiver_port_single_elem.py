import autosar
import autosar.element

def create_workspace_and_packages():
    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('BaseTypes')
    package.createSubPackage('ImplementationTypes')
    ws.createPackage('PortInterfaces', role='PortInterface')
    ws.createPackage('ComponentTypes', role='ComponentType')
    return ws

def create_data_types(ws):
    baseTypes = ws.find('/DataTypes/BaseTypes')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    implTypes = ws.find('/DataTypes/ImplementationTypes')
    implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255,
                            baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    implTypes.createImplementationDataTypeRef('OffOn_T',
                            implementationTypeRef = '/DataTypes/ImplementationTypes/uint8',
                            valueTable = ['OffOn_Off',
                                           'OffOn_On',
                                           'OffOn_Error',
                                           'OffOn_NotAvailable'
                                        ])

def create_port_interfaces(ws):
    package = ws.find('/PortInterfaces')
    package.createSenderReceiverInterface('HeaterPwrStat_I',
        autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'HeaterPwrStat',
                                    '/DataTypes/ImplementationTypes/OffOn_T'))

def create_components(ws):
    package = ws.find('/ComponentTypes')
    comp1 = package.createApplicationSoftwareComponent('Component1')
    comp1.createProvidePort('HeaterPwrStat', 'HeaterPwrStat_I', initValue='OffOn_NotAvailable')

    comp2 = package.createApplicationSoftwareComponent('Component2')
    comp2.createRequirePort('HeaterPwrStat', 'HeaterPwrStat_I', initValue='OffOn_NotAvailable', aliveTimeout = 30)

ws = create_workspace_and_packages()
create_data_types(ws)
create_port_interfaces(ws)
create_components(ws)
ws.saveXML('Component1.arxml', filters=['/ComponentTypes/Component1'])
ws.saveXML('Component2.arxml', filters=['/ComponentTypes/Component2'])
ws.saveXML('DataTypes.arxml', filters=['/DataTypes'])
ws.saveXML('PortInterfaces.arxml', filters = ["/PortInterfaces"])