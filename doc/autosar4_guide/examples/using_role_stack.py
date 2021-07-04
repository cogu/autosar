import autosar

def create_platform_types(ws):
    ws.pushRoles()
    package = ws.createPackage('AUTOSAR_Platform')
    baseTypes = package.createSubPackage('BaseTypes')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    implTypes = package.createSubPackage('ImplementationDataTypes', role='DataType')
    implTypes.createImplementationDataType('uint8', '/AUTOSAR_Platform/BaseTypes/uint8', lowerLimit=0, upperLimit=255, typeEmitter='Platform_Type')
    ws.popRoles()

def create_component_data_types(ws):
    ws.pushRoles()
    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    implTypes = package.createSubPackage('ImplementationDataTypes')
    implTypes.createImplementationDataTypeRef('OffOn_T',
        implementationTypeRef = '/AUTOSAR_Platform/ImplementationDataTypes/uint8',
        valueTable = ['OffOn_Off',
                      'OffOn_On',
                      'OffOn_Error',
                      'OffOn_NotAvailable'])
    ws.popRoles()

def main():
    ws = autosar.workspace(version="4.2.2")
    create_platform_types(ws)
    create_component_data_types(ws)
    ws.saveXML('AUTOSAR_Platform.arxml', filters=['/AUTOSAR_Platform'])
    ws.saveXML('DataTypes.arxml', filters=['/DataTypes'])

if __name__ == '__main__':
    main()