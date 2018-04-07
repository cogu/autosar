import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
import unittest
import time
import shutil

_output_dir = 'derived'

def _create_packages(ws):

    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    basetypes=package.createSubPackage('BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')

    package.createIntegerDataType('uint8', min=0, max=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint16', min=0, max=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint32', min=0, max=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

    package = ws.createPackage('PortInterfaces', role="PortInterface")
    package.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed', 'uint16'))
    package.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed', 'uint16'))

    package = ws.createPackage('Constants', role='Constant')
    package.createConstant('VehicleSpeed_IV', 'uint16', 65535)
    package.createConstant('EngineSpeed_IV', 'uint16', 65535)

    package = ws.createPackage('ComponentTypes', role='ComponentType')

class TestBehaviorARXML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        output_dir_full = os.path.join(os.path.dirname(__file__), _output_dir)
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(_output_dir)

    def test_create_application_software_component(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/ComponentTypes')
        swc = package.createApplicationSoftwareComponent('MyApplication')
        swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        generated_file = os.path.join(_output_dir, 'ar4_application_swc.arxml')
        expected_file = os.path.join( 'expected_gen', 'component', 'ar4_application_swc.arxml')
        ws.saveXML(generated_file, filters=['/ComponentTypes'])
        with open (generated_file, "r") as fp:
            generated_text=fp.read()
        with open (expected_file, "r") as fp:
            expected_text=fp.read()
        self.assertEqual(generated_text, expected_text)

    # def test_create_service_software_component(self):
    #     ws = autosar.workspace(version="4.2.2")
    #     _create_packages(ws)
    #     package = ws.find('/ComponentTypes')
    #     swc = package.createServiceComponent('MyService')
    #     swc.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
    #     generated_file = os.path.join(_output_dir, 'ar4_service_swc.arxml')
    #     expected_file = os.path.join( 'expected_gen', 'component', 'ar4_service_swc.arxml')
    #     ws.saveXML(generated_file, filters=['/ComponentTypes'])
    #     with open (generated_file, "r") as fp:
    #         generated_text=fp.read()
    #     with open (expected_file, "r") as fp:
    #         expected_text=fp.read()
    #     self.assertEqual(generated_text, expected_text)


if __name__ == '__main__':
    unittest.main()

