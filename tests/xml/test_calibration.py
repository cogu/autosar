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
        self.assertEqual(child.values, [1, 2, "Value"])

    def test_read_write_vtf(self):
        element = ar_element.SwValues(values=[
            ar_element.NumericalOrText(vf=10),
            ar_element.NumericalOrText(vt="TextVal"),
            ar_element.NumericalOrText(vf=ar_element.NumericalValue("0x20")),
        ])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VTF>
    <VF>10</VF>
  </VTF>
  <VTF>
    <VT>TextVal</VT>
  </VTF>
  <VTF>
    <VF>0x20</VF>
  </VTF>
</SW-VALUES-PHYS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        self.assertEqual(len(elem.values), 3)

        self.assertIsInstance(elem.values[0], ar_element.NumericalOrText)
        self.assertEqual(elem.values[0].vf, 10)
        self.assertIsNone(elem.values[0].vt)

        self.assertIsInstance(elem.values[1], ar_element.NumericalOrText)
        self.assertIsNone(elem.values[1].vf)
        self.assertEqual(elem.values[1].vt, "TextVal")

        self.assertIsInstance(elem.values[2], ar_element.NumericalOrText)
        self.assertIsInstance(elem.values[2].vf, ar_element.NumericalValue)
        self.assertEqual(elem.values[2].vf.value, 32)
        self.assertEqual(elem.values[2].vf.value_format, ar_enum.ValueFormat.HEXADECIMAL)

    def test_read_write_value_group_with_vtf(self):
        vg = ar_element.ValueGroup(values=[ar_element.NumericalOrText(vf=20)])
        element = ar_element.SwValues(values=[vg])
        writer = autosar.xml.Writer()
        xml = '''<SW-VALUES-PHYS>
  <VG>
    <VTF>
      <VF>20</VF>
    </VTF>
  </VG>
</SW-VALUES-PHYS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        child: ar_element.ValueGroup = elem.values[0]
        self.assertIsInstance(child, ar_element.ValueGroup)
        self.assertIsInstance(child.values[0], ar_element.NumericalOrText)
        self.assertEqual(child.values[0].vf, 20)

    def test_init_single_vtf(self):
        vtf = ar_element.NumericalOrText(vf=5)
        element = ar_element.SwValues(values=vtf)
        self.assertEqual(len(element.values), 1)
        self.assertIsInstance(element.values[0], ar_element.NumericalOrText)
        self.assertEqual(element.values[0].vf, 5)

    def test_read_vf(self):
        xml = '''<SW-VALUES-PHYS>
  <VF>10</VF>
  <VF>3.14</VF>
  <VF>0x10</VF>
</SW-VALUES-PHYS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.SwValues = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwValues)
        self.assertEqual(len(elem.values), 3)
        self.assertEqual(elem.values[0], 10)
        self.assertAlmostEqual(elem.values[1], 3.14)
        self.assertIsInstance(elem.values[2], ar_element.NumericalValue)
        self.assertEqual(elem.values[2].value, 16)
        self.assertEqual(elem.values[2].value_format, ar_enum.ValueFormat.HEXADECIMAL)


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
  <CATEGORY>STD_AXIS</CATEGORY>
</SW-AXIS-CONT>'''

        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwAxisCont)
        self.assertEqual(elem.category, ar_enum.CalibrationAxisCategory.STD_AXIS)

        # Verify backward compatibility with legacy hyphenated enum values
        legacy_xml = '''<SW-AXIS-CONT>
  <CATEGORY>STD-AXIS</CATEGORY>
</SW-AXIS-CONT>'''
        elem_legacy: ar_element.SwAxisCont = reader.read_str_elem(legacy_xml)
        self.assertEqual(elem_legacy.category, ar_enum.CalibrationAxisCategory.STD_AXIS)

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


class TestRuleBasedAxisCont(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.RuleBasedAxisCont()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<RULE-BASED-AXIS-CONT/>')
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedAxisCont)

    def test_read_write_category(self):
        element = ar_element.RuleBasedAxisCont(category=ar_enum.CalibrationAxisCategory.STD_AXIS)
        writer = autosar.xml.Writer()
        xml = '''<RULE-BASED-AXIS-CONT>
  <CATEGORY>STD_AXIS</CATEGORY>
</RULE-BASED-AXIS-CONT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedAxisCont)
        self.assertEqual(elem.category, ar_enum.CalibrationAxisCategory.STD_AXIS)

    def test_read_write_full(self):
        rbv = ar_element.RuleBasedValueSpecification(
            rule="RAMP",
            arguments=ar_element.RuleArguments([0, 10]),
            max_size_to_fill=11
        )
        element = ar_element.RuleBasedAxisCont(
            category=ar_enum.CalibrationAxisCategory.STD_AXIS,
            unit_ref=ar_element.UnitRef("/Units/Kph"),
            sw_axis_index=1,
            sw_array_size=ar_element.ValueList([11]),
            rule_based_values=rbv
        )
        writer = autosar.xml.Writer()
        xml = '''<RULE-BASED-AXIS-CONT>
  <CATEGORY>STD_AXIS</CATEGORY>
  <UNIT-REF DEST="UNIT">/Units/Kph</UNIT-REF>
  <SW-ARRAYSIZE>
    <V>11</V>
  </SW-ARRAYSIZE>
  <SW-AXIS-INDEX>1</SW-AXIS-INDEX>
  <RULE-BASED-VALUES>
    <RULE>RAMP</RULE>
    <ARGUMENTSS>
      <RULE-ARGUMENTS>
        <V>0</V>
        <V>10</V>
      </RULE-ARGUMENTS>
    </ARGUMENTSS>
    <MAX-SIZE-TO-FILL>11</MAX-SIZE-TO-FILL>
  </RULE-BASED-VALUES>
</RULE-BASED-AXIS-CONT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedAxisCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedAxisCont)
        self.assertEqual(elem.category, ar_enum.CalibrationAxisCategory.STD_AXIS)
        self.assertEqual(str(elem.unit_ref), "/Units/Kph")
        self.assertEqual(elem.sw_axis_index, 1)
        self.assertEqual(elem.sw_array_size.values, [11])
        self.assertIsNotNone(elem.rule_based_values)
        self.assertEqual(elem.rule_based_values.rule, "RAMP")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            ar_element.RuleBasedAxisCont(unit_ref="not_a_unit_ref")
        with self.assertRaises(TypeError):
            ar_element.RuleBasedAxisCont(sw_axis_index=[1])
        with self.assertRaises(TypeError):
            ar_element.RuleBasedAxisCont(rule_based_values=object())


class TestRuleBasedValueCont(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.RuleBasedValueCont()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<RULE-BASED-VALUE-CONT/>')
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedValueCont)

    def test_read_write_full(self):
        rbv = ar_element.RuleBasedValueSpecification(
            rule="FILL",
            arguments=ar_element.RuleArguments(0),
            max_size_to_fill=100
        )
        element = ar_element.RuleBasedValueCont(
            unit_ref=ar_element.UnitRef("/Units/Nm"),
            sw_array_size=ar_element.ValueList([10, 10]),
            rule_based_values=rbv
        )
        writer = autosar.xml.Writer()
        xml = '''<RULE-BASED-VALUE-CONT>
  <UNIT-REF DEST="UNIT">/Units/Nm</UNIT-REF>
  <SW-ARRAYSIZE>
    <V>10</V>
    <V>10</V>
  </SW-ARRAYSIZE>
  <RULE-BASED-VALUES>
    <RULE>FILL</RULE>
    <ARGUMENTSS>
      <RULE-ARGUMENTS>
        <V>0</V>
      </RULE-ARGUMENTS>
    </ARGUMENTSS>
    <MAX-SIZE-TO-FILL>100</MAX-SIZE-TO-FILL>
  </RULE-BASED-VALUES>
</RULE-BASED-VALUE-CONT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedValueCont = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedValueCont)
        self.assertEqual(str(elem.unit_ref), "/Units/Nm")
        self.assertEqual(elem.sw_array_size.values, [10, 10])
        self.assertIsNotNone(elem.rule_based_values)
        self.assertEqual(elem.rule_based_values.rule, "FILL")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            ar_element.RuleBasedValueCont(unit_ref="not_a_unit_ref")
        with self.assertRaises(TypeError):
            ar_element.RuleBasedValueCont(rule_based_values=object())


if __name__ == '__main__':
    unittest.main()
