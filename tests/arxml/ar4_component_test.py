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
    package = ws.createPackage('Constants', role='Constant')
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    package = ws.createPackage('PortInterfaces', role="PortInterface")


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
    package = ws.find('/Constants')
    package.createConstant('VehicleSpeed_IV', 'uint16', 65535)
    package.createConstant('EngineSpeed_IV', 'uint16', 65535)
    package = ws.find('/PortInterfaces')
    package.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed', 'uint16'))
    package.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed', 'uint16'))
    portInterface=package.createClientServerInterface('FreeRunningTimer5ms_I', ['GetTime', 'IsTimerElapsed'])
    portInterface['GetTime'].createOutArgument('value', '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("startTime", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("duration", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createOutArgument("result", '/DataTypes/boolean')




def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)
    _create_test_elements(ws)

class ARXML4ComponentTest(ARXMLTestClass):

    def test_create_application_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('MyApplication')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        swc.createRequirePort('FreeRunningTimer', 'FreeRunningTimer5ms_I')
        swc.behavior.createRunnable('Run', portAccess=['VehicleSpeed', 'FreeRunningTimer/GetTime', 'FreeRunningTimer/IsTimerElapsed'])
        swc.behavior.createTimerEvent('Run', 20) #execute the Run function every 20ms in all modes
        file_name = 'ar4_application_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_service_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createServiceComponent('MyService')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        file_name = 'ar4_service_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

    def test_create_cdd_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createComplexDeviceDriverComponent('MyService')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        file_name = 'ar4_cdd_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
    
    def test_create_composition_component(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createCompositionComponent('MyComposition')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        file_name = 'ar4_composition_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'component', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        

        
        

if __name__ == '__main__':
    unittest.main()
