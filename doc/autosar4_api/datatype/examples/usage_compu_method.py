import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('Units', role='Unit')
    return ws

ws = setup()
package = ws.findRolePackage('CompuMethod')

#Rational scaling computation
package.createCompuMethodRational('VehicleSpeed_CompuMethod', scaling=1/64, offset=0, unit="Km_per_h", forceFloat=True)

#Enumeration computation
package.createCompuMethodConst('OnOff_CompuMethod',
    ['OnOff_Off', 'OnOff_On', 'OnOff_Error', 'OnOff_NotAvailable'], defaultValue='OnOff_NotAvailable')
ws.saveXML('DataTypes.arxml', filters=['/DataTypes'])
