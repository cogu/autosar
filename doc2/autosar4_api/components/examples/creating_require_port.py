import autosar

def main():    
    #init
    ws = init_workspace()
    #Create SWC
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    swc = package.createApplicationSoftwareComponent('MySWC')
    #Create new RequirePort in the swc
    port = swc.createRequirePort('HeaterStat', 'HeaterStat_I', initValue = 'OffOn_NotAvailable', aliveTimeout = 30)    
    #save SWC to XML
    ws.saveXML('MySWC.arxml', filters=['/ComponentTypes/MySWC'])


def init_workspace():
    ws = autosar.workspace(version="4.2.2")
    package = ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    baseTypes = package.createSubPackage('BaseTypes')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')    
    implTypes = package.createSubPackage('ImplementationTypes')
    implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255,
                                                        baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    implTypes.createImplementationDataTypeRef('OffOn_T', implementationTypeRef = '/DataTypes/ImplementationTypes/uint8',
                                          valueTable = ['OffOn_Off',
                                                        'OffOn_On',
                                                        'OffOn_Error',
                                                        'OffOn_NotAvailable'
                                                        ])
    package = ws.createPackage('PortInterfaces', role='PortInterface')
    package.createSenderReceiverInterface('HeaterStat_I', autosar.element.DataElement('HeaterStat', '/DataTypes/ImplementationTypes/OffOn_T'))
    return ws

if __name__ == '__main__':
    main()
