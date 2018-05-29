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
    basetypes=package.createSubPackage('BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')

    package.createIntegerDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint8', min=0, max=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint16', min=0, max=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint32', min=0, max=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')
    

    ws.createPackage('Constants', role='Constant')
    
    

class ARXML4ConstantTest(ARXMLTestClass):

    def test_create_array_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)        
        ws['/DataTypes'].createArrayDataType('u8Array2_T', '/DataTypes/uint8', 2)
        ws['/Constants'].createConstant('u8Array2_IV', 'u8Array2_T', [0,0])
        file_name = 'ar4_array_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

    def test_create_num_value_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package = ws['Constants']
        package.createNumericalValueConstant('U32Value_IV', 2**32-1)
        file_name = 'ar4_num_value_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

    def test_create_impl_string_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package = ws['Constants']
        package.createConstant('UserName_IV','/DataTypes/UserName_T', '')
        file_name = 'ar4_impl_string_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])


    def test_create_record_constant1(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Test_T', '/DataTypes/uint32')
        package.createArrayDataType('Array4_T', '/DataTypes/U32Test_T', 4)

        package.createRecordDataType('RecordType1_T', [('Elem1', '/DataTypes/Array4_T'), ('Elem2', '/DataTypes/U32Test_T')] )

        package = ws['Constants']
        package.createConstant('Record1_IV','/DataTypes/RecordType1_T', {'Elem1': [2**32-1,2**32-1,0,0], 'Elem2': 2**32-1})
        file_name = 'ar4_record_constant1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

    def test_create_record_constant2(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package.createRecordDataType('RecordType2_T', [('Elem1', '/DataTypes/U32Type_T'), ('Elem2', '/DataTypes/UserName_T')] )
        package = ws['Constants']
        package.createConstant('Record2_IV','/DataTypes/RecordType2_T', {'Elem1': 2**32-1, 'Elem2': 'Default'})
        file_name = 'ar4_record_constant2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

    def test_create_record_constant3(self):
        #same as test_create_record_constant2 but uses an empty string as initializer
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package.createRecordDataType('RecordType2_T', [('Elem1', '/DataTypes/U32Type_T'), ('Elem2', '/DataTypes/UserName_T')] )
        package = ws['Constants']
        package.createConstant('Record2_IV','/DataTypes/RecordType2_T', {'Elem1': 2**32-1, 'Elem2': ''})
        file_name = 'ar4_record_constant3.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])        
    
if __name__ == '__main__':
    unittest.main()