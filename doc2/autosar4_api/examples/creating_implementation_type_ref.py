import autosar

#Setup
ws = autosar.workspace(version="4.2.2")
package=ws.createPackage('DataTypes', role='DataType')
package.createSubPackage('CompuMethods', role='CompuMethod')
package.createSubPackage('DataConstrs', role='DataConstraint')
baseTypes=package.createSubPackage('BaseTypes')
baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
implTypes = package.createSubPackage('ImplementationTypes')
implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
implTypes.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')




#Create implementation data type with offset and scaling
implTypes.createImplementationDataTypeRef('VehicleSpeed_T',
                                            implementationTypeRef = '/DataTypes/ImplementationTypes/uint16',
                                            lowerLimit = 0,
                                            upperLimit = 65535,
                                            offset = 0,
                                            scaling = 1/64,
                                            forceFloat = True)

#Create implementation data type with enumeration table (also known as value table)
implTypes.createImplementationDataTypeRef('OffOn_T', implementationTypeRef = '/DataTypes/ImplementationTypes/uint8',
                                          valueTable = ['OffOn_Off',
                                                        'OffOn_On',
                                                        'OffOn_Error',
                                                        'OffOn_NotAvailable'
                                                        ])

#Export as XML
ws.saveXML('DataTypes.arxml')