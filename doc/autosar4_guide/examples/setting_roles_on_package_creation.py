import autosar

ws = autosar.workspace(version="4.2.2")
package=ws.createPackage('DataTypes', role='DataType')
package.createSubPackage('CompuMethods', role='CompuMethod')
package.createSubPackage('Units', role='Unit')
package.createSubPackage('DataConstrs', role='DataConstraint')
baseTypes=package.createSubPackage('BaseTypes')
baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
implTypes = package.createSubPackage('ImplementationTypes')
implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
implTypes.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
ws.saveXML('DataTypes.arxml')
