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
    package.createSubPackage('ImplementationTypes')
    ws.createPackage('Constants', role='Constant')

def _create_base_types(ws):
    baseTypes = ws.find('/DataTypes/BaseTypes')
    booleanBase = baseTypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    uint8Base = baseTypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    uint16Base = baseTypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    uint32Base = baseTypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    baseTypes.createSwBaseType('float32', 32, encoding='IEEE754')
    implTypes = ws.find('DataTypes/ImplementationTypes')
    implTypes.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef=booleanBase.ref, typeEmitter='Platform_Type')
    implTypes.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef=uint8Base.ref, typeEmitter='Platform_Type')
    implTypes.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef=uint16Base.ref, typeEmitter='Platform_Type')
    implTypes.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef=uint32Base.ref, typeEmitter='Platform_Type')

def _create_enum_types(ws):
    baseTypes = ws.find('/DataTypes/BaseTypes')
    implTypes = ws.find('/DataTypes/ImplementationTypes')
    uint8Impl = implTypes.find("uint8")
    uint8Base = baseTypes.find("uint8")
    implTypes.createImplementationDataTypeRef('OffOn_T', implementationTypeRef = uint8Impl.ref, valueTable = ['OffOn_Off',
                                                                                                              'OffOn_On',
                                                                                                              'OffOn_Error',
                                                                                                              'OffOn_NotAvailable'])
    implTypes.createImplementationDataType('SparseInactiveActive_T', baseTypeRef=uint8Base.ref, valueTable=[(0, 'SparseInactiveActive_InActive'),
                                                                                                            (1, 'SparseInactiveActive_Active'),
                                                                                                            (3, 'SparseInactiveActive_NotAvailable')])

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
        implTypes = ws['DataTypes/ImplementationTypes']
        uint8Impl = implTypes.find("uint8")
        arrayType=implTypes.createImplementationArrayDataType('u8Array2_T', uint8Impl.ref, 2)
        package = ws['Constants']
        c1 = package.createConstant('u8Array2_IV', arrayType.ref, [0,0])
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
        implTypes = ws['DataTypes/ImplementationTypes']
        uint8Impl = implTypes.find("uint8")
        arrayType=implTypes.createImplementationArrayDataType('UserName_T', uint8Impl.ref, 32)
        package = ws['Constants']
        c1 = package.createConstant('UserName_IV', arrayType.ref, '')
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
        implTypes = ws['DataTypes/ImplementationTypes']
        uint32Impl = implTypes.find("uint32")
        refType = implTypes.createImplementationDataTypeRef('U32Test_T', uint32Impl.ref)
        arrayType = implTypes.createImplementationArrayDataType('Array4_T', refType.ref, 4)
        recordType = implTypes.createImplementationRecordDataType('RecordType1_T', [('Elem1', arrayType.ref), ('Elem2', refType.ref)] )
        package = ws['Constants']
        c1 = package.createConstant('Record1_IV', recordType.ref, {'Elem1': [2**32-1,2**32-1,0,0], 'Elem2': 2**32-1})
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
        implTypes = ws['DataTypes/ImplementationTypes']
        uint8Impl = implTypes.find("uint8")
        uint32Impl = implTypes.find("uint32")
        refType = implTypes.createImplementationDataTypeRef('U32Type_T', uint32Impl.ref)
        arrayType = implTypes.createImplementationArrayDataType('UserName_T', uint8Impl.ref, 32)
        recordType = implTypes.createImplementationRecordDataType('RecordType2_T', [('Elem1', refType.ref), ('Elem2', arrayType.ref)] )
        package = ws['Constants']
        c1 = package.createConstant('Record2_IV', recordType.ref, {'Elem1': 2**32-1, 'Elem2': 'Default'})
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
        implTypes = ws['DataTypes/ImplementationTypes']
        uint8Impl = implTypes.find("uint8")
        uint32Impl = implTypes.find("uint32")
        refType = implTypes.createImplementationDataTypeRef('U32Type_T', uint32Impl.ref)
        arrayType = implTypes.createImplementationArrayDataType('UserName_T', uint8Impl.ref, 32)
        recordType = implTypes.createImplementationRecordDataType('RecordType2_T', [('Elem1', refType.ref), ('Elem2', arrayType.ref)] )
        package = ws['Constants']
        c1 = package.createConstant('Record2_IV', recordType.ref, {'Elem1': 2**32-1, 'Elem2': ''})
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_record_constant3.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_record_constant4(self):
        """
        Tests record constants containing enum values
        """
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        _create_enum_types(ws)
        implTypes = ws['DataTypes/ImplementationTypes']
        OffOn_T = implTypes.find("OffOn_T")
        SparseInactiveActive_T = implTypes.find("SparseInactiveActive_T")
        RecordType_T = implTypes.createImplementationRecordDataType('RecordType_T', [('Elem1', OffOn_T.ref), ('Elem2', SparseInactiveActive_T.ref)] )
        package = ws['Constants']
        c1 = package.createConstant('Record_IV', RecordType_T.ref, {'Elem1': 0, 'Elem2': 3})
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_record_constant4.arxml'
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
        implTypes = ws['DataTypes/ImplementationTypes']
        uint8Impl = implTypes.find("uint8")
        recordType = implTypes.createImplementationRecordDataType('ServiceResult_T', [
            ('ServiceId', uint8Impl.ref),
            ('RequestResult', uint8Impl.ref),
        ])
        arrayType = implTypes.createImplementationArrayDataType('ServiceResultList_T', recordType.ref, 2)
        package = ws['Constants']
        c1 = package.createConstant('CDiagNv_NvMServiceRequestType', arrayType.ref,
        [
            {'ServiceId': 0, 'RequestResult': 0},
            {'ServiceId': 1, 'RequestResult': 0}
        ])
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_array_of_records.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

    def test_create_record_in_record_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        implTypes = ws['DataTypes/ImplementationTypes']
        booleanImpl = implTypes.find("boolean")
        uint32Impl = implTypes.find("uint32")
        Active_T = implTypes.createImplementationDataTypeRef('Active_T', booleanImpl.ref)
        AlarmTime_T = implTypes.createImplementationDataTypeRef('AlarmTime_T', uint32Impl.ref)
        AlarmId_T = implTypes.createImplementationDataTypeRef('AlarmId_T', uint32Impl.ref)
        RecordType1_T = implTypes.createImplementationRecordDataType('RecordType1_T', [('AlarmEnabled', Active_T.ref),
                                                                                       ('AlarmTime', AlarmTime_T.ref)])
        RecordType2_T = implTypes.createImplementationRecordDataType('RecordType2_T', [('AlarmId', AlarmId_T.ref),
                                                                                       ('AlarmProps', RecordType1_T.ref)])
        package = ws['Constants']
        c1 = package.createConstant('RecordInRecord_IV', RecordType2_T.ref, {'AlarmId': 1,
                                                                             'AlarmProps': {"AlarmEnabled": True, "AlarmTime": 10000}})
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_record_in_record_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join('expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_array_in_array_constant(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        implTypes = ws['DataTypes/ImplementationTypes']
        uint8Impl = implTypes.find("uint8")
        Number_T = implTypes.createImplementationDataTypeRef('Number_T', uint8Impl.ref)
        ArrayType1_T = implTypes.createImplementationArrayDataType('ArrayType1_T', Number_T.ref, 4)
        ArrayType2_T = implTypes.createImplementationArrayDataType('ArrayType2_T', ArrayType1_T.ref, 2)
        package = ws['Constants']
        c1 = package.createConstant('ArrayInArray_IV', ArrayType2_T.ref, [[1, 2, 3, 4], [5, 6, 7, 8]])
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_array_of_array_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join('expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

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

    def test_create_application_value3(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws['DataTypes']
        package.createUnit('deg', 'degree')
        package = ws['Constants']
        c1 = package.createApplicationValueConstant(
            'Phys_SteeringWheelAngle_IV',
            autosar.constant.SwValueCont(
                [32.05, 120.11, -36.345, 22.0, 58.0], '/DataTypes/Units/deg'))
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'ar4_application_value3.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'constant', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

        explicit_array_size_file_path = os.path.join( 'expected_gen', 'constant', 'ar4_application_value4.arxml')
        ws3 = autosar.workspace(ws.version_str)
        ws3.loadXML(os.path.join(os.path.dirname(__file__), explicit_array_size_file_path))
        c3 = ws3.find(c1.ref)
        self.assertIsInstance(c3, autosar.constant.Constant)



if __name__ == '__main__':
    unittest.main()
