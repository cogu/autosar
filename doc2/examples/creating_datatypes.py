import autosar

ws = autosar.workspace("4.2.2")

#Create packages and some platform types
datatypes = package=ws.createPackage('DataTypes', role='DataType')
package.createSubPackage('CompuMethods', role='CompuMethod')
package.createSubPackage('DataConstrs', role='DataConstraint')
package.createSubPackage('Units', role='Unit')
basetypes = package.createSubPackage('BaseTypes')
basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
package.createImplementationDataType('uint8',
                                     lowerLimit=0,
                                     upperLimit=255,
                                     baseTypeRef='/DataTypes/BaseTypes/uint8',
                                     typeEmitter='Platform_Type')
package.createImplementationDataType('uint16',
                                     lowerLimit=0,
                                     upperLimit=65535,
                                     baseTypeRef='/DataTypes/BaseTypes/uint16',
                                     typeEmitter='Platform_Type')


#Create our implementation data types
package.createImplementationDataTypeRef('OffOn_T',
                                        implementationTypeRef = '/DataTypes/uint8',
                                        valueTable=['OffOn_Off',
                                                    'OffOn_On',
                                                    'OffOn_Error',
                                                    'OffOn_NotAvailable'])

datatypes.createImplementationDataTypeRef('VehicleSpeed_T',
                                       implementationTypeRef = '/DataTypes/uint16',
                                       lowerLimit = 0,
                                       upperLimit = 65535,
                                       offset = 0,
                                       scaling = 1/64,
                                       unit = 'KmPerHour')

#Example of using reference strings to find our data types
dt1 = ws.find('/DataTypes/OffOn_T')
dt2 = ws.find('/DataTypes/VehicleSpeed_T')
print("dt1.name: " + dt1.name)
print("dt1.ref: " + dt1.ref)
print("dt2.name: " + dt2.name)
print("dt2.ref: " + dt2.ref)

#Export as XML
ws.saveXML('DataTypes.arxml')
