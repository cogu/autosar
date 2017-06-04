import autosar

ws=autosar.workspace()

dataTypes=ws.createPackage('DataType')
dataTypes.createSubPackage('DataTypeSemantics', role='CompuMethod')
dataTypes.createSubPackage('DataTypeUnits', role='Unit')

dataTypes.createIntegerDataType('EngineSpeed_T', min=0, max=65535, offset=0, scaling=1/8, unit='rpm')
dataTypes.createIntegerDataType('VehicleSpeed_T', min=0, max=65535, offset=0, scaling=1/64,unit='kph')
dataTypes.createIntegerDataType('Percent_T', min=0, max=255, offset=0, scaling=0.4, unit='Percent')
dataTypes.createIntegerDataType('CoolantTemp_T', min=0, max=255, offset=-40, scaling=0.5, unit='DegreeC')
dataTypes.createIntegerDataType('InactiveActive_T', valueTable=[
     'InactiveActive_Inactive',       #0
     'InactiveActive_Active',         #1
     'InactiveActive_Error',          #2
     'InactiveActive_NotAvailable'])  #3
dataTypes.createIntegerDataType('OnOff_T', valueTable=[
    "OnOff_Off",                      #0
    "OnOff_On",                       #1
    "OnOff_Error",                    #2
    "OnOff_NotAvailable"])            #3

ws.saveXML('DataTypes.arxml')
print("Done")