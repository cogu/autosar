dev_mode = True
if dev_mode:
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import autosar

def create_autosar_platform(ws):
    package = ws.createPackage('AUTOSAR_Platform')
    baseTypes = package.createSubPackage('BaseTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    implTypes = package.createSubPackage('ImplementationDataTypes')
    baseTypes.createSwBaseType('dtRef_const_VOID', 1, encoding = 'VOID', nativeDeclaration = 'void')
    baseTypes.createSwBaseType('dtRef_VOID', 1, encoding = 'VOID', nativeDeclaration = 'void')
    baseTypes.createSwBaseType('boolean', 8, encoding = 'BOOLEAN', nativeDeclaration='boolean')
    baseTypes.createSwBaseType('float32', 32, encoding = 'IEEE754', nativeDeclaration = 'float32')
    baseTypes.createSwBaseType('float64', 64, encoding = 'IEEE754', nativeDeclaration = 'float64')
    baseTypes.createSwBaseType('sint8', 8, encoding = '2C', nativeDeclaration='sint8')
    baseTypes.createSwBaseType('sint16', 16, encoding = '2C', nativeDeclaration='uint16')
    baseTypes.createSwBaseType('sint32', 32, encoding = '2C', nativeDeclaration='sint32')
    baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    baseTypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    ws.setRole(implTypes.ref, 'DataType')
    implTypes.createImplementationDataTypePtr('dtRef_const_VOID', '/AUTOSAR_Platform/BaseTypes/dtRef_const_VOID', swImplPolicy = 'CONST')
    implTypes.createImplementationDataTypePtr('dtRef_VOID', '/AUTOSAR_Platform/BaseTypes/dtRef_VOID')
    implTypes.createImplementationDataType('boolean', '/AUTOSAR_Platform/BaseTypes/boolean', valueTable=['FALSE', 'TRUE'], typeEmitter='Platform_Type')
    implTypes.createImplementationDataType('uint8', '/AUTOSAR_Platform/BaseTypes/uint8', lowerLimit=0, upperLimit=255, typeEmitter='Platform_Type')
    implTypes.createImplementationDataType('uint16', '/AUTOSAR_Platform/BaseTypes/uint16', lowerLimit=0, upperLimit=65535, typeEmitter='Platform_Type')
    implTypes.createImplementationDataType('uint32', '/AUTOSAR_Platform/BaseTypes/uint32', lowerLimit=0, upperLimit=4294967295, typeEmitter='Platform_Type')

if __name__ == '__main__':
    ws = autosar.workspace("4.2.2")
    create_autosar_platform(ws)
    autosar.util.createDcf(ws).save(dest_dir = 'autosar4', dcf_name = 'PlatformExample', file_map = {'AUTOSAR_Platform': {'root': 'DATATYPE', 'filters': ['/AUTOSAR_Platform']}})
    print("Done")
