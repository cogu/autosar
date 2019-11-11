import autosar

#Create some packages and data types
ws = autosar.workspace('4.2.2')
datatypes = ws.createPackage('DataTypes', role='DataType')
basetypes = datatypes.createSubPackage('BaseTypes')
u8Type = basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
u16Type = basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
u32Type = basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
ws.saveXML('basetypes.arxml')

#Print reference and name for the created objects
print('u8Type.name: ' + u8Type.name)
print('u8Type.ref: ' + u8Type.ref)
print('u16Type.name: ' + u16Type.name)
print('u16Type.ref: ' + u16Type.ref)
print('u32Type.name: ' + u32Type.name)
print('u32Type.ref: ' + u32Type.ref)
