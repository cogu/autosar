import autosar

def create_packages(ws):

    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('BaseTypes')
    ws.createPackage('PortInterfaces', role="PortInterface")

def create_data_types(ws):
    basetypes = ws.find('/DataTypes/BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

def setup_ws():
    ws = autosar.workspace(version='4.2.2')
    create_packages(ws)
    create_data_types(ws)
    return ws

ws = setup_ws()
package = ws.find('/PortInterfaces')

#Creates new port interface with two operations
portInterface=package.createClientServerInterface('FreeRunningTimer_I', ['GetTime', 'IsTimerElapsed'])

#Individually create arguments for each operation using the returned object
portInterface['GetTime'].createOutArgument('value', '/DataTypes/uint32')
portInterface["IsTimerElapsed"].createInArgument("startTime", '/DataTypes/uint32')
portInterface["IsTimerElapsed"].createInArgument("duration", '/DataTypes/uint32')
portInterface["IsTimerElapsed"].createOutArgument("result", '/DataTypes/boolean')

#Save ARXML ...
ws.saveXML('PortInterfaces.arxml', filters=['/PortInterfaces'])
#... or generate DaVinci project
autosar.util.createDcf(ws).save('davinci', 'Example', force=True)
