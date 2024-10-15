import autosar
import autosar.element

def create_workspace_and_datatypes():
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
    return ws

#Create SenderReceiver interface with single data element
ws = create_workspace_and_datatypes()
package = ws.find('PortInterfaces')

package.createSenderReceiverInterface('HeaterPwrStat_I', autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'HeaterPwrStat', '/DataTypes/ImplementationTypes/OffOn_T'))

#Save only the port interfaces portion to XML 
ws.saveXML('PortInterfaces.arxml', filters=['/PortInterfaces'])