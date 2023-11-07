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


class TestSwAxisCont(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.SwAxisCont()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<SW-AXIS-CONT/>')
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)

    def test_read_write_category(self):
        element = ar_element.SwAxisCont(category=ar_enum.CalibrationAxisCategory.STD_AXIS)
        writer = autosar.xml.Writer()
        xml = '''<SW-AXIS-CONT>
  <CATEGORY>STD-AXIS</CATEGORY>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(elem.category, ar_enum.CalibrationAxisCategory.STD_AXIS)

    def test_read_write_unit_ref(self):
        element = ar_element.SwAxisCont(unit_ref=ar_element.UnitRef("/Units/MyUnit"))
        writer = autosar.xml.Writer()
        xml = '''<SW-AXIS-CONT>
  <UNIT-REF DEST="UNIT">/Units/MyUnit</UNIT-REF>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(str(elem.unit_ref), "/Units/MyUnit")

    def test_read_write_unit_display_name(self):
        unit_display_name = ar_element.SingleLanguageUnitNames("Km/h")
        element = ar_element.SwAxisCont(unit_display_name=unit_display_name)
        writer = autosar.xml.Writer()
        xml = '''<SW-AXIS-CONT>
  <UNIT-DISPLAY-NAME>Km/h</UNIT-DISPLAY-NAME>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(str(elem.unit_display_name), "Km/h")

    def test_read_write_sw_axis_index(self):
        element = ar_element.SwAxisCont(sw_axis_index=1)
        writer = autosar.xml.Writer()
        xml = '''<SW-AXIS-CONT>
  <SW-AXIS-INDEX>1</SW-AXIS-INDEX>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(elem.sw_axis_index, 1)

    def test_read_write_sw_array_size(self):
        element = ar_element.SwAxisCont(sw_array_size=ar_element.ValueList([1, 2]))
        writer = autosar.xml.Writer()
        xml = '''<SW-AXIS-CONT>
  <SW-ARRAYSIZE>
    <V>1</V>
    <V>2</V>
  </SW-ARRAYSIZE>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(elem.sw_array_size.values, [1, 2])

    def test_read_write_sw_values_phys(self):
        element = ar_element.SwAxisCont(sw_values_phys=ar_element.SwValues(1))
        writer = autosar.xml.Writer()
        xml = '''<SW-AXIS-CONT>
  <SW-VALUES-PHYS>
    <V>1</V>
  </SW-VALUES-PHYS>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(elem.sw_values_phys.values, [1])


class TestSwValueCont(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.SwValueCont()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<SW-VALUE-CONT/>')
        reader = autosar.xml.Reader()
        elem: ar_element.SwValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValueCont)

    def test_read_write_unit_ref(self):
        element = ar_element.SwValueCont(unit_ref=ar_element.UnitRef("/Units/MyUnit"))
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUE-CONT>
  <UNIT-REF DEST="UNIT">/Units/MyUnit</UNIT-REF>
</SW-VALUE-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValueCont)
        self.assertEqual(str(elem.unit_ref), "/Units/MyUnit")

    def test_read_write_unit_display_name(self):
        unit_display_name = ar_element.SingleLanguageUnitNames("Km/h")
        element = ar_element.SwValueCont(unit_display_name=unit_display_name)
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUE-CONT>
  <UNIT-DISPLAY-NAME>Km/h</UNIT-DISPLAY-NAME>
</SW-VALUE-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValueCont)
        self.assertEqual(str(elem.unit_display_name), "Km/h")

    def test_read_write_sw_array_size(self):
        element = ar_element.SwValueCont(sw_array_size=ar_element.ValueList([1, 2]))
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUE-CONT>
  <SW-ARRAYSIZE>
    <V>1</V>
    <V>2</V>
  </SW-ARRAYSIZE>
</SW-VALUE-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValueCont)
        self.assertEqual(elem.sw_array_size.values, [1, 2])

    def test_read_write_sw_values_phys(self):
        element = ar_element.SwValueCont(sw_values_phys=ar_element.SwValues(1))
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUE-CONT>
  <SW-VALUES-PHYS>
    <V>1</V>
  </SW-VALUES-PHYS>
</SW-VALUE-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValueCont)
        self.assertEqual(elem.sw_values_phys.values, [1])


if __name__ == '__main__':
    unittest.main()
