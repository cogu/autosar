import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    package=ws.createPackage('ApplicationTypes', role='DataType')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    return ws

ws = setup()
package = ws.findRolePackage('DataConstraint')
package.createInternalDataConstraint('uint8_DataConstraint', 0, 255)
ws.saveXML('DataTypes.arxml', filters=['/ApplicationTypes'])