import autosar

ws = autosar.workspace("4.2.2")
platform = ws.createPackage('AUTOSAR_Platform')
basetypes = platform.createSubPackage('BaseTypes')
basetypes.createSwBaseType('boolean', 1, encoding = 'BOOLEAN', nativeDeclaration='boolean')
basetypes.createSwBaseType('float32', 32, encoding = 'IEEE754', nativeDeclaration = 'float32')
basetypes.createSwBaseType('float64', 64, encoding = 'IEEE754', nativeDeclaration = 'float64')
basetypes.createSwBaseType('sint8', 8, nativeDeclaration='sint8')
basetypes.createSwBaseType('sint16', 16, nativeDeclaration='uint16')
basetypes.createSwBaseType('sint32', 32, nativeDeclaration='sint32')
basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')

ws.saveXML('PlatformTypes_AR4.arxml')