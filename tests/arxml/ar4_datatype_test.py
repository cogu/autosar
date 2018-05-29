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

def _create_base_types(ws):
    package = ws.find('/DataTypes')
    basetypes=package.createSubPackage('BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')

    package.createIntegerDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint8', min=0, max=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint16', min=0, max=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createIntegerDataType('uint32', min=0, max=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

class ARXML4DataTypeTest(ARXMLTestClass):

    def test_create_array_datatype(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws['DataTypes']
        package.createArrayDataType('u8Array2_T', '/DataTypes/uint8', 2)
        file_name = 'ar4_array_datatype.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, filters=['/DataTypes'])

    def test_create_implementation_ref_type(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        file_name = 'ar4_implementation_type_ref.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])



    def test_create_impl_string_type(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        file_name = 'ar4_impl_string_type.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

    def test_create_record_type1(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createRecordDataType('RecordType1_T', [('Elem1', '/DataTypes/uint8'), ('Elem2', '/DataTypes/U32Type_T')] )
        file_name = 'ar4_record_type1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

    def test_create_record_type2(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package.createRecordDataType('RecordType2_T', [('Elem1', '/DataTypes/U32Type_T'), ('Elem2', '/DataTypes/UserName_T')] )
        file_name = 'ar4_record_type2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

    def test_create_ref_type_with_valueTable(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createImplementationDataTypeRef('OffOn_T', '/DataTypes/uint8', valueTable=['OffOn_Off', 'OffOn_On', 'OffOn_Error', 'OffOn_NotAvailable'])
        file_name = 'ar4_ref_type_vt.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

    def test_create_ref_type_with_bitmask(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('DataTypeWithBitMask_T', '/DataTypes/uint8', bitmask=[
            'MASK1',
            'MASK2',
            'MASK4',
            'MASK8',
            'MASK16',
            'MASK32',
            'MASK64',
            'MASK128',
            ])
        file_name = 'ar4_ref_type_bitmask.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
    
    def test_create_data_constraint_with_custom_name(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws['DataTypes']
                
        package.createImplementationDataTypeRef('OffOn_T', '/DataTypes/uint8', valueTable=['OffOn_Off', 'OffOn_On', 'OffOn_Error', 'OffOn_NotAvailable'], dataConstraint=None)
        file_name = 'ar4_disable_auto_data_constraint.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

    def test_disable_auto_constraint(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)
        
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32RefCustom_T', '/DataTypes/uint32', minVal=0, maxVal=100000, dataConstraint='CustomConstraintName')
        file_name = 'ar4_custom_data_constraint_ref.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
    
if __name__ == '__main__':
    unittest.main()