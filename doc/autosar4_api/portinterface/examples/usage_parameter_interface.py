import autosar

def create_workspace_and_datatypes():
    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('DataTypes')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    baseTypes = package.createSubPackage('BaseTypes')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    implTypes = package.createSubPackage('ImplementationTypes', role="DataType")
    implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255,
                                                    baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    ws.createPackage('PortInterfaces', role='PortInterface')
    return ws

ws = create_workspace_and_datatypes()
package = ws.findRolePackage('PortInterface')
package.createParameterInterface('ButtonDebounceTime_I', autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Parameter, 'v', "uint8"))
ws.saveXML("ParameterInterface.arxml")
