import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    dataTypePackage=ws.createPackage('ApplicationTypes', role='DataType')
    dataConstraintPackage = dataTypePackage.createSubPackage('DataConstrs', role='DataConstraint')
    compuMethodPackage = dataTypePackage.createSubPackage('CompuMethods', role='CompuMethod')
    dataTypePackage.createSubPackage('Units', role='Unit')
    compuMethod = compuMethodPackage.createCompuMethodRational('SensorReading_CompuMethod',
        scaling=1, offset=0, unit="Counts")
    dataConstraint = dataConstraintPackage.createInternalDataConstraint('SensorReading_DataConstraint', 0, 255)
    dataTypePackage.createApplicationPrimitiveDataType('SensorReading_T',
        dataConstraint = dataConstraint.ref,  compuMethod=compuMethod.ref)
    return ws

ws = setup()
package = ws.findRolePackage('DataType')
Record_T = package.createApplicationRecordDataType('Record_T')
SensorReading_T = ws.find('SensorReading_T', role='DataType')
Record_T.createElement('SensorReading', SensorReading_T.ref)
ws.saveXML('DataTypes.arxml', filters=['/ApplicationTypes'])
