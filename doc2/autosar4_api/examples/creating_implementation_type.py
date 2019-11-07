import autosar

#Setup
ws = autosar.workspace(version="4.2.2")
package=ws.createPackage('DataTypes', role='DataType')
package.createSubPackage('CompuMethods', role='CompuMethod')
package.createSubPackage('DataConstrs', role='DataConstraint')

baseTypes=package.createSubPackage('BaseTypes')
baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
baseTypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')

implTypes = package.createSubPackage('ImplementationTypes')
implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
implTypes.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
implTypes.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

#Export as XML
ws.saveXML('DataTypes.arxml')
