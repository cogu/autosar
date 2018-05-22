import autosar

ws = autosar.workspace(version="4.2.2")
package=ws.createPackage('DataTypes', role='DataType')
package.createSubPackage('CompuMethods', role='CompuMethod')
package.createSubPackage('DataConstrs', role='DataConstraint')
basetypes=package.createSubPackage('BaseTypes')
basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
implTypes=package.createSubPackage('ImplementationTypes')
implTypes.createIntegerDataType('uint8', min=0, max=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
implTypes.createImplementationPtrDataType('MyU8PtrType', '/DataTypes/BaseTypes/uint8')
ws.saveXML('DataTypes2.arxml', filters=['/DataTypes'])
