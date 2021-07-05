import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    dataTypePackage=ws.createPackage('ApplicationTypes', role='DataType')
    dataConstraintPackage = dataTypePackage.createSubPackage('DataConstrs', role='DataConstraint')
    compuMethodPackage = dataTypePackage.createSubPackage('CompuMethods', role='CompuMethod')
    dataTypePackage.createSubPackage('Units', role='Unit')
    compuMethod = compuMethodPackage.createCompuMethodRational('Percent_CompuMethod',
        scaling=4/10, offset=0, unit="Percent", forceFloat=True)
    dataConstraint = dataConstraintPackage.createInternalDataConstraint(
        'Percent_DataConstraint', 0, 250)
    dataTypePackage.createApplicationPrimitiveDataType('PercentSetting_T',
        dataConstraint = dataConstraint.ref,  compuMethod=compuMethod.ref)
    return ws

ws = setup()
package = ws.findRolePackage('DataType')
PercentSetting_T = ws.find('PercentSetting_T', role='DataType')
package.createApplicationArrayDataType('SettingsArray_T',
    autosar.datatype.ApplicationArrayElement(typeRef = PercentSetting_T.ref, arraySize=5))
ws.saveXML('DataTypes.arxml')