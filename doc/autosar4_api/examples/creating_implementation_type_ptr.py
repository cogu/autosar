import autosar

#Setup
ws = autosar.workspace(version="4.2.2")
package=ws.createPackage('DataTypes', role='DataType')
baseTypes=package.createSubPackage('BaseTypes')
baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
implTypes = package.createSubPackage('ImplementationTypes')




#Create implementation data type that is a pointer to uint8
implTypes.createImplementationDataTypePtr('ByteBuffer_T', baseTypeRef = '/DataTypes/BaseTypes/uint8')

#Export as XML
ws.saveXML('DataTypes.arxml')