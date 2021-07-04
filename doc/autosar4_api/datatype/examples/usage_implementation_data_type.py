import autosar

def setup():
    ws = autosar.workspace(version="4.2.2")
    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    baseTypes=package.createSubPackage('BaseTypes')
    baseTypes.createSwBaseType('dtRef_const_VOID', encoding = 'VOID', nativeDeclaration = 'void')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    package.createSubPackage('ImplementationTypes')
    return ws

ws = setup()
implTypes = ws.find('/DataTypes/ImplementationTypes')

#Basic Implementation Type
uint8_BaseRef = '/DataTypes/BaseTypes/uint8'
uint8_Impl = implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, 
    baseTypeRef = uint8_BaseRef, typeEmitter='Platform_Type')
#Type Reference
implTypes.createImplementationDataTypeRef('OffOn_T', implementationTypeRef = uint8_Impl.ref, 
    valueTable = ['OffOn_Off', 'OffOn_On', 'OffOn_Error', 'OffOn_NotAvailable'])

#Pointer Type
dtRef_const_VOID_BaseRef = '/DataTypes/BaseTypes/dtRef_const_VOID'
implTypes.createImplementationDataTypePtr('dtRef_const_VOID', dtRef_const_VOID_BaseRef, swImplPolicy = 'CONST')

ws.saveXML('DataTypes.arxml')