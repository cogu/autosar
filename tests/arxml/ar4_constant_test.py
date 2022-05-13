import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest
import warnings
warnings.simplefilter("error", DeprecationWarning)


def _create_packages(ws):

    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')
    ws.createPackage('Constants', role='Constant')

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

def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)

class ARXML4ConstantTest(ARXMLTestClass):

    def test_create_num_value_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['Constants']
        c1 = package.createNumericalValueConstant('U32Value_IV', 2**32-1)
        self.assertIsInstance(c1, autosar.constant.Constant)
        file_name = 'ar4_num_value_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_array_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createImplementationArrayDataType('u8Array2_T', '/DataTypes/uint8', 2)
        package = ws['Constants']
        c1 = package.createConstant('u8Array2_IV', 'u8Array2_T', [0,0])
        self.assertIsInstance(c1, autosar.constant.Constant)
        file_name = 'ar4_array_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_impl_string_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createImplementationArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package = ws['Constants']
        c1 = package.createConstant('UserName_IV','UserName_T', '')
        self.assertIsInstance(c1, autosar.constant.Constant)
        file_name = 'ar4_impl_string_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)


    def test_create_record_constant1(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Test_T', '/DataTypes/uint32')
        package.createImplementationArrayDataType('Array4_T', '/DataTypes/U32Test_T', 4)
        package.createImplementationRecordDataType('RecordType1_T', [('Elem1', '/DataTypes/Array4_T'), ('Elem2', '/DataTypes/U32Test_T')] )
        package = ws['Constants']
        c1 = package.createConstant('Record1_IV','/DataTypes/RecordType1_T', {'Elem1': [2**32-1,2**32-1,0,0], 'Elem2': 2**32-1})
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_record_constant1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_record_constant2(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createImplementationArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package.createImplementationRecordDataType('RecordType2_T', [('Elem1', '/DataTypes/U32Type_T'), ('Elem2', '/DataTypes/UserName_T')] )
        package = ws['Constants']
        c1 = package.createConstant('Record2_IV','/DataTypes/RecordType2_T', {'Elem1': 2**32-1, 'Elem2': 'Default'})
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_record_constant2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_record_constant3(self):
        #same as test_create_record_constant2 but uses an empty string as initializer
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createImplementationArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        package.createImplementationRecordDataType('RecordType2_T', [('Elem1', '/DataTypes/U32Type_T'), ('Elem2', '/DataTypes/UserName_T')] )
        package = ws['Constants']
        c1 = package.createConstant('Record2_IV','/DataTypes/RecordType2_T', {'Elem1': 2**32-1, 'Elem2': ''})
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_record_constant3.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_array_of_record_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createImplementationRecordDataType('ServiceResult_T', [
            ('ServiceId', '/DataTypes/uint8'),
            ('RequestResult', '/DataTypes/uint8'),
        ])
        package.createImplementationArrayDataType('ServiceResultList_T', '/DataTypes/ServiceResult_T', 2)
        package = ws['Constants']
        c1 = package.createConstant('CDiagNv_NvMServiceRequestType','/DataTypes/ServiceResultList_T',
        [
            {'ServiceId': 0, 'RequestResult': 0},
            {'ServiceId': 1, 'RequestResult': 0}
        ])
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_array_of_records.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

    def test_create_application_value1(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createUnit('rad', 'radian')
        package = ws['Constants']
        c1 = package.createApplicationValueConstant('Phys_SteeringWheelAngle_IV', autosar.constant.SwValueCont(1.745329252, '/DataTypes/Units/rad'))
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_application_value1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_application_value2(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createUnit('kg',)
        package = ws['Constants']
        c1 = package.createApplicationValueConstant('Phys_Calibration_IV',
                                                    autosar.constant.SwValueCont(63),
                                                    autosar.constant.SwAxisCont(unitRef = '/DataTypes/Units/kg'))
        self.assertIsInstance(c1, autosar.constant.Constant)

        cNaN = package.createApplicationValueConstant('Phys_Calibration_NAN_IV',
                                                    autosar.constant.SwValueCont(float('NaN')),
                                                    autosar.constant.SwAxisCont(unitRef = '/DataTypes/Units/kg'))
        self.assertIsInstance(cNaN, autosar.constant.Constant)

        cnINF = package.createApplicationValueConstant('Phys_Calibration_nINF_IV',
                                                    autosar.constant.SwValueCont(float('-INF')))
        self.assertIsInstance(cnINF, autosar.constant.Constant)

        cINF = package.createApplicationValueConstant('Phys_Calibration_INF_IV',
                                                    autosar.constant.SwValueCont(float('INF')))
        self.assertIsInstance(cINF, autosar.constant.Constant)

        cText = package.createApplicationValueConstant('Phys_Calibration_Text_IV',
                                                    autosar.constant.SwValueCont('TextValue'))
        self.assertIsInstance(cText, autosar.constant.Constant)

        file_name = 'ar4_application_value2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)
        value = c2.value
        self.assertIsInstance(value, autosar.constant.ApplicationValue)
        self.assertIsInstance(value.swAxisCont, autosar.constant.SwAxisCont)
        self.assertEqual(value.swAxisCont.unitRef, '/DataTypes/Units/kg')

        c2 = ws2.find(cNaN.ref)
        value = c2.value
        self.assertIsInstance(value.swValueCont, autosar.constant.SwValueCont)
        self.assertEqual(len(value.swValueCont.values), 1)
        self.assertEqual(str(value.swValueCont.values[0]), 'nan')

        c2 = ws2.find(cnINF.ref)
        value = c2.value
        self.assertIsInstance(value.swValueCont, autosar.constant.SwValueCont)
        self.assertEqual(len(value.swValueCont.values), 1)
        self.assertEqual(str(value.swValueCont.values[0]), '-inf')

        c2 = ws2.find(cINF.ref)
        value = c2.value
        self.assertIsInstance(value.swValueCont, autosar.constant.SwValueCont)
        self.assertEqual(len(value.swValueCont.values), 1)
        self.assertEqual(str(value.swValueCont.values[0]), 'inf')

        c2 = ws2.find(cText.ref)
        value = c2.value
        self.assertIsInstance(value.swValueCont, autosar.constant.SwValueCont)
        self.assertEqual(len(value.swValueCont.values), 1)
        self.assertEqual(value.swValueCont.values[0], 'TextValue')

if __name__ == '__main__':
    unittest.main()
