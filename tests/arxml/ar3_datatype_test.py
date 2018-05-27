import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
import unittest
import time
import shutil

_output_dir = 'derived'

def _create_packages(ws):

    package=ws.createPackage('DataType', role='DataType')
    package.createSubPackage('CompuMethod', role='CompuMethod')    
    package.createSubPackage('Units', role='Unit')

def _create_base_types(ws):
    package = ws.find('/DataType')
    package.createIntegerDataType('UInt8', min=0, max=255)
    package.createIntegerDataType('UInt16', min=0, max=65535)
    package.createIntegerDataType('UInt32', min=0, max=4294967295)
  

class TestDataTypeARXML3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        output_dir_full = os.path.join(os.path.dirname(__file__), _output_dir)
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        output_dir_full = os.path.join(os.path.dirname(__file__), _output_dir)
        os.rmdir(output_dir_full)

    def save_and_check(self, ws, expected_file, generated_file, filters, force_copy=False):
        expected_path = os.path.join(os.path.dirname(__file__), expected_file)
        generated_path = os.path.join(os.path.dirname(__file__), generated_file)
        ws.saveXML(generated_path, filters=filters)
        if force_copy:
            shutil.copyfile(generated_path, expected_path)
        with open (generated_path, "r") as fp:
            expected_text=fp.read()
        with open (generated_path, "r") as fp:
            generated_text=fp.read()
        self.assertEqual(expected_text, generated_text)
        os.remove(generated_path)

    def test_create_integer_types(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        package = ws.find('/DataType')
        package.createIntegerDataType('UInt8', min=0, max=255)
        package.createIntegerDataType('UInt16', min=0, max=65535)
        package.createIntegerDataType('UInt32', min=0, max=4294967295)
        file_name = 'ar3_integer_types.arxml'
        generated_file = os.path.join(_output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'])
   
    def test_create_record_type_simple(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws.find('/DataType')
        
        package.createRecordDataType('MyRecord_T',
                             elements = [
                                ('UserId1', 'UInt16'),
                                ('UserId2', 'UInt16'),
                                ('UserId3', 'UInt16')
                                ])
        file_name = 'ar3_record_type_simple.arxml'
        generated_file = os.path.join(_output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'])

    def test_create_record_type_array(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws.find('/DataType')        
        record_type = package.createRecordDataType('MyRecord_T',
                             elements = [
                                ('Setting1', 'UInt8'),
                                ('Setting2', 'UInt16'),
                                ('Setting3', 'UInt32')
                                ])
        package.createArrayDataType('MyArray_T', record_type.ref, 8)
        file_name = 'ar3_record_type_array.arxml'
        generated_file = os.path.join(_output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'], True)





if __name__ == '__main__':
    unittest.main()