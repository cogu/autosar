import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest


_output_dir = 'derived'

def _create_packages(ws):

    package=ws.createPackage('DataType', role='DataType')
    package.createSubPackage('CompuMethod', role='CompuMethod')    
    package.createSubPackage('Units', role='Unit')
    ws.createPackage('Constant', role='Constant')
    _create_base_types(ws)

def _create_base_types(ws):
    package = ws.find('/DataType')
    package.createIntegerDataType('UInt8', min=0, max=255)
    package.createIntegerDataType('UInt16', min=0, max=65535)
    package.createIntegerDataType('UInt32', min=0, max=4294967295)
  

class ARXML3ConstantTest(ARXMLTestClass):

    def test_create_integer_constant(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        package = ws.find('/DataType')
        package.createIntegerDataType('Warning3Bit_T', min=0, max=7)
        package = ws.find('/Constant')
        package.createConstant('WarningSignal_IV', 'Warning3Bit_T', 7)
        
        file_name = 'ar3_integer_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constant'])

    def test_create_array_record_constant(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        package = ws.find('/DataType')        
        record_type = package.createRecordDataType('MyRecord_T',
                                                    elements = [
                                                    ('Setting1', 'UInt8'),
                                                    ('Setting2', 'UInt16'),
                                                    ('Setting3', 'UInt32')
                                                    ])
        package.createArrayDataType('MyRecordArray_T', record_type.ref, 3)
        
        package = ws.find('/Constant')
        package.createConstant('MyConstant', 'MyRecordArray_T', [
                                                                    {'Setting1': 255, 'Setting2': 65535, 'Setting3': 2**32-1},
                                                                    {'Setting1': 0, 'Setting2': 0, 'Setting3': 0},
                                                                    {'Setting1': 255, 'Setting2': 65535, 'Setting3': 2**32-1}
                                                                ])
        
        file_name = 'ar3_array_record_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constant'], True)
   
if __name__ == '__main__':
    unittest.main()