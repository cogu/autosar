import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    package=ws.createPackage('ApplicationTypes', role='DataType')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('Units', role='Unit')
    return ws

ws = setup()
compuMethodPackage = ws.findRolePackage('CompuMethod')
speedCompuMethod = compuMethodPackage.createCompuMethodRational('VehicleSpeed_CompuMethod', 
    scaling=1/64, offset=0, unit="Km_per_h", forceFloat=True)
dataConstraintPackage = ws.findRolePackage('DataConstraint')
speedDataConstraint = dataConstraintPackage.createInternalDataConstraint('VehicleSpeed_DataConstraint', 0, 65535)
dataTypePackage = ws.findRolePackage('DataType')
dataTypePackage.createApplicationPrimitiveDataType('VehicleSpeed_T', 
    dataConstraint = speedDataConstraint.ref,  compuMethod=speedCompuMethod.ref)
ws.saveXML('DataTypes.arxml', filters=['/ApplicationTypes'])

