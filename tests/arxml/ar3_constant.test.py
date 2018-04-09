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

    package.createIntegerDataType('UInt8', min=0, max=255)
    package.createIntegerDataType('UInt16', min=0, max=65535)
    package.createIntegerDataType('UInt32', min=0, max=4294967295)
    package.createArrayDataType('u8Array2_T', '/DataTypes/UInt8', 2)

    package = ws.createPackage('Constants', role='Constant')
    package.createConstant('u8Array2_IV', 'u8Array2_T', [0,0])

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
        os.rmdir(_output_dir)

    def test_create_application_software_component(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        package = ws.find('/ComponentTypes')
        file_name = 'ar3_array_constant.arxml'
        generated_file = os.path.join(_output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        ws.saveXML(generated_file, filters=['/Constants'])
        with open (generated_file, "r") as fp:
            generated_text=fp.read()
        with open (expected_file, "r") as fp:
            expected_text=fp.read()
        self.assertEqual(generated_text, expected_text)
        os.remove(generated_file)



if __name__ == '__main__':
    unittest.main()