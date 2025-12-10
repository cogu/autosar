"""Unit tests for common structure elements"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestDataFilter(unittest.TestCase):

    def test_empty(self):
        element = ar_element.DataFilter()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, "DATA-FILTER")
        self.assertEqual(xml, '<DATA-FILTER/>')
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)

    def test_data_filter_type(self):
        element = ar_element.DataFilter(ar_enum.DataFilterType.ONE_EVERY_N)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <DATA-FILTER-TYPE>ONE-EVERY-N</DATA-FILTER-TYPE>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.data_filter_type, ar_enum.DataFilterType.ONE_EVERY_N)

    def test_mask(self):
        element = ar_element.DataFilter(mask=0xFF00)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <MASK>65280</MASK>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.mask, 0xFF00)

    def test_max(self):
        element = ar_element.DataFilter(max_val=100)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <MAX>100</MAX>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.max_val, 100)

    def test_min(self):
        element = ar_element.DataFilter(min_val=0)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <MIN>0</MIN>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.min_val, 0)

    def test_offset(self):
        element = ar_element.DataFilter(offset=1)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <OFFSET>1</OFFSET>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.offset, 1)

    def test_period(self):
        element = ar_element.DataFilter(period=10)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <PERIOD>10</PERIOD>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.period, 10)

    def test_x(self):
        element = ar_element.DataFilter(x=2)
        writer = autosar.xml.Writer()
        xml = '''<DATA-FILTER>
  <X>2</X>
</DATA-FILTER>'''
        self.assertEqual(writer.write_str_elem(element, "DATA-FILTER"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DataFilter = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataFilter)
        self.assertEqual(elem.x, 2)


class TestAutosarEngineeringObject(unittest.TestCase):
    """
    Also tests parent class EngineeringObject
    """

    def test_empty(self):
        element = ar_element.AutosarEngineeringObject()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, "AUTOSAR-ENGINEERING-OBJECT")
        self.assertEqual(xml, '<AUTOSAR-ENGINEERING-OBJECT/>')
        reader = autosar.xml.Reader()
        elem: ar_element.AutosarEngineeringObject = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AutosarEngineeringObject)

    def test_data_filter_type(self):
        element = ar_element.AutosarEngineeringObject(label="MyLabel")
        writer = autosar.xml.Writer()
        xml = '''<AUTOSAR-ENGINEERING-OBJECT>
  <SHORT-LABEL>MyLabel</SHORT-LABEL>
</AUTOSAR-ENGINEERING-OBJECT>'''
        self.assertEqual(writer.write_str_elem(element, "AUTOSAR-ENGINEERING-OBJECT"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AutosarEngineeringObject = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AutosarEngineeringObject)
        self.assertEqual(elem.label, "MyLabel")


class TestCode(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.Code("Default")
        writer = autosar.xml.Writer()
        xml = '''<CODE>
  <SHORT-NAME>Default</SHORT-NAME>
</CODE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Code = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Code)
        self.assertEqual(elem.name, "Default")

    def test_artifact_descriptor(self):
        descriptor = ar_element.AutosarEngineeringObject(label="Default", category="SWSRC")
        element = ar_element.Code("Default", artifact_descriptors=descriptor)
        writer = autosar.xml.Writer()
        xml = '''<CODE>
  <SHORT-NAME>Default</SHORT-NAME>
  <ARTIFACT-DESCRIPTORS>
    <AUTOSAR-ENGINEERING-OBJECT>
      <SHORT-LABEL>Default</SHORT-LABEL>
      <CATEGORY>SWSRC</CATEGORY>
    </AUTOSAR-ENGINEERING-OBJECT>
  </ARTIFACT-DESCRIPTORS>
</CODE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.Code = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Code)
        self.assertEqual(len(elem.artifact_descriptors), 1)
        artifact_descriptor = elem.artifact_descriptors[0]
        self.assertEqual(artifact_descriptor.label, "Default")
        self.assertEqual(artifact_descriptor.category, "SWSRC")


if __name__ == '__main__':
    unittest.main()
