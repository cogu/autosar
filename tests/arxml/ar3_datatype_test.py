import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest

def _create_packages(ws):

    package=ws.createPackage('DataType', role='DataType')
    package.createSubPackage('CompuMethod', role='CompuMethod')
    package.createSubPackage('Units', role='Unit')

def _create_base_types(ws):
    package = ws.find('/DataType')
    package.createIntegerDataType('UInt8', min=0, max=255)
    package.createIntegerDataType('UInt16', min=0, max=65535)
    package.createIntegerDataType('UInt32', min=0, max=4294967295)

class ARXML3DataTypeTest(ARXMLTestClass):

    def test_create_integer_types(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        package = ws.find('/DataType')
        dt11 = package.createIntegerDataType('UInt8', min=0, max=255)
        dt12 = package.createIntegerDataType('UInt16', min=0, max=65535)
        dt13 = package.createIntegerDataType('UInt32', min=0, max=4294967295)
        file_name = 'ar3_integer_types.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt21 = ws2.find('/DataType/UInt8')
        dt22 = ws2.find('/DataType/UInt8')
        dt23 = ws2.find('/DataType/UInt32')
        self.assertIsInstance(dt21, autosar.datatype.IntegerDataType)
        self.assertIsInstance(dt22, autosar.datatype.IntegerDataType)
        self.assertIsInstance(dt23, autosar.datatype.IntegerDataType)



    def test_create_enumeration_types(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        package = ws.find('/DataType')
        dt1 = package.createIntegerDataType('InactiveActive_T', valueTable=[
            'InactiveActive_Inactive',
            'InactiveActive_Active',
            'InactiveActive_Error',
            'InactiveActive_NotAvailable'])
        self.assertEqual(dt1.minVal, 0)
        self.assertEqual(dt1.maxVal, 3)

        file_name = 'ar3_enumeration_types.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find('/DataType/InactiveActive_T')
        self.assertIsInstance(dt2, autosar.datatype.IntegerDataType)
        self.assertEqual(dt2.minVal, dt1.minVal)
        self.assertEqual(dt2.maxVal, dt1.maxVal)


    def test_create_record_type_simple(self):
        ws = autosar.workspace(version="3.0.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws.find('/DataType')

        dt1 = package.createRecordDataType('MyRecord_T',
                             elements = [
                                ('UserId1', 'UInt16'),
                                ('UserId2', 'UInt16'),
                                ('UserId3', 'UInt16')
                                ])
        self.assertEqual(len(dt1.elements), 3)
        file_name = 'ar3_record_type_simple.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find('/DataType/MyRecord_T')
        self.assertEqual(len(dt2.elements), len(dt1.elements))


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
        dt1 = package.createArrayDataType('MyArray_T', record_type.ref, 8)
        self.assertIsInstance(dt1, autosar.datatype.ArrayDataType)
        self.assertEqual(dt1.length, 8)
        file_name = 'ar3_record_type_array.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataType'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find('/DataType/MyArray_T')
        self.assertIsInstance(dt2, autosar.datatype.ArrayDataType)
        self.assertEqual(dt2.length, 8)

if __name__ == '__main__':
    unittest.main()