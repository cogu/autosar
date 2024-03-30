import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest
import warnings
warnings.simplefilter("error", DeprecationWarning)


class ARXML4ValueBuilderTest(ARXMLTestClass):

    def test_create_integer(self):
        ws = autosar.workspace(version="4.2.2")
        package = ws.createPackage('Constants', role='Constant')
        c1 = package.createConstant('FieldOfView_IV', None, 90, label = None)
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'integer_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'value_builder', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)
        self.assertEqual(c2.value.value, c1.value.value)

    def test_create_float(self):
        ws = autosar.workspace(version="4.2.2")
        package = ws.createPackage('Constants', role='Constant')
        c1 = package.createConstant('Radians_IV', None, 1.745329252, label = None)
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'float_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'value_builder', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)
        self.assertEqual(c2.value.value, c1.value.value)

    def test_create_text(self):
        ws = autosar.workspace(version="4.2.2")
        package = ws.createPackage('Constants', role='Constant')
        c1 = package.createConstant('Greeting_IV', None, 'Hello World', label = None)
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'text_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'value_builder', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)
        self.assertEqual(c2.value.value, c1.value.value)

    def test_create_record(self):
        ws = autosar.workspace(version="4.2.2")
        package = ws.createPackage('Constants', role='Constant')
        c1 = package.createConstant('Result_IV', None, {'Status': 0, 'ID': 22, 'Message': 'OK'})
        self.assertIsInstance(c1, autosar.constant.Constant)
        self.assertIsInstance(c1.value, autosar.constant.RecordValueAR4)

        file_name = 'record_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'value_builder', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)
        self.assertIsInstance(c2.value, autosar.constant.RecordValueAR4)

    def test_create_array(self):
        ws = autosar.workspace(version="4.2.2")
        package = ws.createPackage('Constants', role='Constant')
        c1 = package.createConstant('Array_IV', None, [1,2,3])
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'array_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'value_builder', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)

    def test_create_array_of_records(self):
        ws = autosar.workspace(version="4.2.2")
        package = ws.createPackage('Constants', role='Constant')
        c1 = package.createConstant('CDiagNv_NvMServiceRequestType', None,
            [
                {'SerciceId': 0, 'RequestResult': 0}
            ], label = None)
        self.assertIsInstance(c1, autosar.constant.Constant)

        file_name = 'array_of_records_constant.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'value_builder', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/Constants'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        c2 = ws2.find(c1.ref)
        self.assertIsInstance(c2, autosar.constant.Constant)


if __name__ == '__main__':
    unittest.main()