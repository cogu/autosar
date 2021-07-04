import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    #Application Types
    dataTypePackage=ws.createPackage('ApplicationTypes', role='DataType')
    dataConstraintPackage = dataTypePackage.createSubPackage('DataConstrs', role='DataConstraint')
    compuMethodPackage = dataTypePackage.createSubPackage('CompuMethods', role='CompuMethod')
    onOffDataConstraint = dataConstraintPackage.createInternalDataConstraint('OnOff_DataConstraint', 0, 3)
    onOffCompuMethod = compuMethodPackage.createCompuMethodConst('OnOff_CompuMethod',
        ['OnOff_Off', 'OnOff_On', 'OnOff_Error', 'OnOff_NotAvailable'],
        defaultValue='OnOff_NotAvailable')
    dataTypePackage.createApplicationPrimitiveDataType('OnOff_T',
    dataConstraint = onOffDataConstraint.ref,  compuMethod=onOffCompuMethod.ref)
    #Base Types
    baseTypes=ws.createPackage('BaseTypes')
    baseTypeUint8 = baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    #Implementation Types
    dataTypePackage = ws.createPackage('ImplementationTypes', role = 'DataType')
    dataTypePackage.createSubPackage('DataConstrs', role='DataConstraint')
    dataTypePackage.createSubPackage('CompuMethods', role='CompuMethod')
    dataTypePackage.createImplementationDataType('OnOff_T', baseTypeUint8.ref,
        valueTable = ['OnOff_Off', 'OnOff_On', 'OnOff_Error', 'OnOff_NotAvailable'])
    return ws

ws = setup()
package = ws.createPackage('DataTypeMappingSets')
mappingSet = package.createDataTypeMappingSet('MappingSet')
appType = ws.find('/ApplicationTypes/OnOff_T')
implType = ws.find('/ImplementationTypes/OnOff_T')
mappingSet.createDataTypeMapping(appType.ref, implType.ref)
ws.saveXML('DataTypes.arxml')