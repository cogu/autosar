import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    package=ws.createPackage('ApplicationTypes', role='DataType')
    package.createSubPackage('Units', role='Unit')
    return ws

ws = setup()
package = ws.findRolePackage('Unit')
package.createUnit('Percent', '%')
ws.saveXML('DataTypes.arxml', filters=['/ApplicationTypes'])