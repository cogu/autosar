import autosar

ws = autosar.workspace()

ws.loadXML('../datatypes/DataTypes.arxml', roles={'/DataType': 'DataType'})
ws.loadXML('PortInterfaces.arxml')

for portinterface in ws['PortInterface'].elements:
   print("%s: %s"%(portinterface.name, type(portinterface)))
   for dataElement in portinterface.dataElements:
      dataType = ws.find(dataElement.typeRef)
      print("   %s: %s"%(dataElement.name, type(dataType)))