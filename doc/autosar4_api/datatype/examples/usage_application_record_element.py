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
SensorReading_T = ws.find('SensorReading_T', role='DataType')
element = autosar.datatype.ApplicationRecordElement('SensorReading', SensorReading_T.ref)