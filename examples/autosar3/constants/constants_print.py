import autosar

ws = autosar.workspace()
ws.loadXML('Constants.arxml')

for elem in ws['Constant'].elements:
   print("%s: %s"%(elem.name,type(elem)))