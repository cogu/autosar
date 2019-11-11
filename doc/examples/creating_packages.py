import autosar
   
ws = autosar.workspace("4.2.2")
ws.createPackage('Package1')
ws.createPackage('Package2')
ws.createPackage('Package3')
ws.createPackage('Package4')
ws.saveXML('packages.arxml')