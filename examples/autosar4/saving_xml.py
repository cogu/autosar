import autosar
    
ws = autosar.workspace(version='4.2.2')
        
ws.createPackage('DataTypes', role='DataType')
ws.createPackage('Constants', role="Constant")
ws.createPackage('PortInterfaces', role="PortInterface")
ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
ws.createPackage('ComponentTypes', role='ComponentType')
  
#save the file as XML
ws.saveXML('Workspace.arxml')

    
ws = autosar.workspace(version='4.2.2')
        
ws.createPackage('DataTypes', role='DataType')
ws.createPackage('Constants', role="Constant")
ws.createPackage('PortInterfaces', role="PortInterface")
ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
ws.createPackage('ComponentTypes', role='ComponentType')

#save workspace packages into XML files
ws.saveXML('DataTypes.arxml', filters=['/DataTypes'])
ws.saveXML('Constants.arxml', filters=['/Constants'])
ws.saveXML('PortInterfaces.arxml', filters=['/PortInterfaces', '/ModeDclrGroups'])
ws.saveXML('ComponentTypes.arxml', filters=['/ComponentTypes']) 