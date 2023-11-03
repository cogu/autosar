"""Unit tests for calibration data"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402

class TestSwValues(unittest.TestCase): # noqa D101

    def test_read_write_empty(self):
        element = ar_element.SwValues()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<SW-VALUES-PHYS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)

    def test_read_write_text(self):
        element = ar_element.SwValues(values=["Value1", "Value2"])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VT>Value1</VT>
  <VT>Value2</VT>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        self.assertEqual(elem.values, ["Value1", "Value2"])

    def test_read_write_int(self):
        element = ar_element.SwValues(values=[1, 2, 3])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <V>1</V>
  <V>2</V>
  <V>3</V>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        self.assertEqual(elem.values, [1, 2, 3])

    def test_read_write_float(self):
        element = ar_element.SwValues(values=[1.5, 2.4])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <V>1.5</V>
  <V>2.4</V>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        self.assertAlmostEqual(elem.values[0], 1.5)
        self.assertAlmostEqual(elem.values[1], 2.4)

    def test_read_write_binary_literal(self):
        element = ar_element.SwValues(values=[
            ar_element.NumericalValue("0b1111011"),
            ar_element.NumericalValue("0b1100"),
        ])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <V>0b1111011</V>
  <V>0b1100</V>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        value: ar_element.NumericalValue = elem.values[0]
        self.assertEqual(value.value_format, ar_enum.ValueFormat.BINARY)
        self.assertEqual(value.value, 123)
        value: ar_element.NumericalValue = elem.values[1]
        self.assertAlmostEqual(value.value_format, ar_enum.ValueFormat.BINARY)
        self.assertEqual(value.value, 12)

    def test_read_write_empty_value_group(self):
        element = ar_element.SwValues(values=[ar_element.ValueGroup()])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VG/>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        child = elem.values[0]
        self.assertIsInstance(child, ar_element.ValueGroup)

    def test_read_write_value_group_label_only(self):
        vg = ar_element.ValueGroup(label=(ar_enum.Language.FOR_ALL, "MyLabel"))
        element = ar_element.SwValues(values=[vg])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VG>
    <LABEL>
      <L-4 L="FOR-ALL">MyLabel</L-4>
    </LABEL>
  </VG>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        child: ar_element.ValueGroup = elem.values[0]
        self.assertIsInstance(child, ar_element.ValueGroup)
        self.assertEqual(child.label.elements[0].parts[0], 'MyLabel')
        self.assertEqual(child.label.elements[0].language, ar_enum.Language.FOR_ALL)

    def test_read_write_value_group_no_label(self):
        vg = ar_element.ValueGroup(values=[1, 2, "Value"])
        element = ar_element.SwValues(values=[vg])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VG>
    <V>1</V>
    <V>2</V>
    <VT>Value</VT>
  </VG>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        child: ar_element.ValueGroup = elem.values[0]
        self.assertIsInstance(child, ar_element.ValueGroup)
        self.assertEqual(child.values, [1, 2, "Value"])

    def test_read_write_value_group_with_label(self):
        vg = ar_element.ValueGroup(label=(ar_enum.Language.FOR_ALL, "MyLabel"), values=[1, 2, "Value"])
        element = ar_element.SwValues(values=[vg])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VG>
    <LABEL>
      <L-4 L="FOR-ALL">MyLabel</L-4>
    </LABEL>
    <V>1</V>
    <V>2</V>
    <VT>Value</VT>
  </VG>
</SW-VALUES-PHYS>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        child: ar_element.ValueGroup = elem.values[0]
        self.assertIsInstance(child, ar_element.ValueGroup)
        self.assertEqual(child.values, [1, 2, "Value"])


if __name__ == '__main__':
    unittest.main()
