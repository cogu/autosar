import autosar

ws = autosar.workspace(version="4.2.2")
ws.loadXML('DataTypes.arxml', roles = {
    '/DataTypes': 'DataType',
    '/DataTypes/CompuMethods': 'CompuMethod',
    '/DataTypes/Units': 'Unit',
    '/DataTypes/DataConstrs': 'DataConstraint'})
print(ws.roles)