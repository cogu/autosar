import autosar

ws = autosar.workspace()
package=ws.createPackage("DataType", role="DataType")
package.createSubPackage('DataTypeSemantics', role='CompuMethod')
package.createSubPackage('DataTypeUnits', role='Unit')
package.createIntegerDataType('InactiveActive_T',valueTable=[
        'InactiveActive_Inactive',
        'InactiveActive_Active',
        'InactiveActive_Error',
        'InactiveActive_NotAvailable'])

ws.saveXML('DataTypes.arxml', packages=['DataType'])

ws2 = autosar.workspace()
ws2.loadXML('DataTypes.arxml')
print(ws2['DataType/InactiveActive_T'].name)