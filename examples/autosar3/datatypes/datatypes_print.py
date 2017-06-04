import autosar

ws = autosar.workspace()
ws.loadXML('DataTypes.arxml')

for elem in ws['DataType'].elements:
   print("%s: %s"%(elem.name,type(elem)))