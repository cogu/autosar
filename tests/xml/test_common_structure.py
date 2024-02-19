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


if __name__ == '__main__':
    unittest.main()
