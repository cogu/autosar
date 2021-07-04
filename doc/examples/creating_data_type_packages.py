import autosar

ws = autosar.workspace(version="4.2.2")
package=ws.createPackage('DataTypes')
baseTypes = package.createSubPackage('BaseTypes')
BaseTypeUint8 = baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
implTypes = package.createSubPackage('ImplementationTypes', role='DataType')
implTypes.createSubPackage('CompuMethods', role='CompuMethod')
implTypes.createSubPackage('DataConstrs', role='DataConstraint')
implTypes.createImplementationDataType('uint8', BaseTypeUint8.ref, 0, 255)
ws.saveXML('DataTypes.arxml')