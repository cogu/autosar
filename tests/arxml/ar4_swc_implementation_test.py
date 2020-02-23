import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest

def _create_packages(ws):
    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')
    package.createSubPackage('MappingSets')
    package = ws.createPackage('Constants', role='Constant')
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    package = ws.createPackage('PortInterfaces', role="PortInterface")
    package = ws.createPackage('AUTOSAR_MemMap')
    package.createSubPackage('SwAddrMethods')

def _create_base_types(ws):
    basetypes = ws.find('/DataTypes/BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    basetypes.createSwBaseType('float32', 32, encoding='IEEE754')
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

def _create_test_elements(ws):
    package = ws.find('/PortInterfaces')
    portInterface=package.createClientServerInterface('FreeRunningTimer5ms_I', ['GetTime', 'IsTimerElapsed'])
    portInterface['GetTime'].createOutArgument('value', '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("startTime", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("duration", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createOutArgument("result", '/DataTypes/boolean')
    package = ws.find('/AUTOSAR_MemMap/SwAddrMethods')
    package.createSoftwareAddressMethod("CALIB")
    package.createSoftwareAddressMethod("CODE")
    package.createSoftwareAddressMethod("CONST")

def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)
    _create_test_elements(ws)

class ARXML4ComponentTest(ARXMLTestClass):

    def test_create_swc_implementation(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('MyApplication')
        swc.createRequirePort('FreeRunningTimer', 'FreeRunningTimer5ms_I')
        swc.behavior.createRunnable('Run', portAccess=['FreeRunningTimer/GetTime', 'FreeRunningTimer/IsTimerElapsed'])
        swc.behavior.createTimerEvent('Run', 20) #execute the Run function every 20ms in all modes
        swc.implementation.codeDescriptors[0].artifactDescriptors[0].revisionLabels = ['1.0.1']
        swc.implementation.codeDescriptors[0].artifactDescriptors[0].domain = 'testDomain'
        swc.implementation.programmingLanguage = 'C'
        swc.implementation.swVersion = '1.0.0'
        swc.implementation.useCodeGenerator = 'codeGen'
        swc.implementation.vendorId = '99'

        file_name = 'ar4_swc_implementation.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_swc_implementation_memsections(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('MyApplication')
        swc.createRequirePort('FreeRunningTimer', 'FreeRunningTimer5ms_I')
        swc.behavior.createRunnable('Run', portAccess=['FreeRunningTimer/GetTime', 'FreeRunningTimer/IsTimerElapsed'])
        swc.behavior.createTimerEvent('Run', 20) #execute the Run function every 20ms in all modes
        swc.implementation.programmingLanguage = 'C'
        swc.implementation.swVersion = '1.0.0'
        swc.implementation.useCodeGenerator = 'codeGen'
        swc.implementation.vendorId = '99'

        # Create the ResourceConsumption
        swc.implementation.resourceConsumption = autosar.component.ResourceConsumption('RsrcCons_MyApplication', swc.implementation)
        swc.implementation.resourceConsumption.memorySections = []
        memorySection = autosar.component.MemorySection('CODE_INLINE', swc.implementation.resourceConsumption)
        memorySection.aligment = 'UNSPECIFIED'
        memorySection.memClassSymbol = 'memClassSymbol'
        memorySection.options = ['INLINE']
        memorySection.size = 50
        memorySection.swAddrmethodRef = '/AUTOSAR_MemMap/SwAddrMethods/CODE'
        memorySection.symbol = 'CODE_INLINE'
        swc.implementation.resourceConsumption.memorySections.append(memorySection)

        memorySection = autosar.component.MemorySection('CODE', swc.implementation.resourceConsumption)
        memorySection.aligment = 'UNSPECIFIED'
        memorySection.size = 500
        memorySection.swAddrmethodRef = '/AUTOSAR_MemMap/SwAddrMethods/CODE'
        swc.implementation.resourceConsumption.memorySections.append(memorySection)

        memorySection = autosar.component.MemorySection('CONST', swc.implementation.resourceConsumption)
        memorySection.aligment = '32'
        memorySection.swAddrmethodRef = '/AUTOSAR_MemMap/SwAddrMethods/CONST'
        swc.implementation.resourceConsumption.memorySections.append(memorySection)

        memorySection = autosar.component.MemorySection('CALIB', swc.implementation.resourceConsumption)
        memorySection.aligment = '8'
        memorySection.swAddrmethodRef = '/AUTOSAR_MemMap/SwAddrMethods/CALIB'
        swc.implementation.resourceConsumption.memorySections.append(memorySection)

        file_name = 'ar4_swc_implementation_memmap.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes', 'AUTOSAR_MemMap'])

if __name__ == '__main__':
    unittest.main()
