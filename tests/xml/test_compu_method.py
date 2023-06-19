"""Unit tests for computation elements."""

# noqa D101
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402

class TestCompuRational(unittest.TestCase): # noqa D101

    def test_write_read_int_numerator(self):  # noqa D102
        element = ar_element.CompuRational((0, 1))
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-RATIONAL-COEFFS>
  <COMPU-NUMERATOR>
    <V>0</V>
    <V>1</V>
  </COMPU-NUMERATOR>
</COMPU-RATIONAL-COEFFS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuRational = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuRational)
        self.assertEqual(elem.numerator, (0, 1))

    def test_write_read_int_tuple_numerator(self): # noqa D102
        element = ar_element.CompuRational((-1, 2))
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-RATIONAL-COEFFS>
  <COMPU-NUMERATOR>
    <V>-1</V>
    <V>2</V>
  </COMPU-NUMERATOR>
</COMPU-RATIONAL-COEFFS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuRational = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuRational)
        self.assertEqual(elem.numerator, (-1, 2))

    def test_write_read_float_numerator(self): # noqa D102
        element = ar_element.CompuRational((0, float(1 / 64)))
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-RATIONAL-COEFFS>
  <COMPU-NUMERATOR>
    <V>0</V>
    <V>0.015625</V>
  </COMPU-NUMERATOR>
</COMPU-RATIONAL-COEFFS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuRational = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuRational)
        self.assertEqual(elem.numerator, (0, 0.015625))

    def test_write_read_float_tuple_numerator(self): # noqa D102
        element = ar_element.CompuRational((-140.0, 0.5))
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-RATIONAL-COEFFS>
  <COMPU-NUMERATOR>
    <V>-140</V>
    <V>0.5</V>
  </COMPU-NUMERATOR>
</COMPU-RATIONAL-COEFFS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuRational = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuRational)
        self.assertEqual(elem.numerator, (-140, 0.5))


class TestCompuScale(unittest.TestCase): # noqa D101

    def test_write_read_label(self): # noqa D102
        element = ar_element.CompuScale(label="label")
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <SHORT-LABEL>label</SHORT-LABEL>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.label, "label")

    def test_write_read_symbol(self): # noqa D102
        element = ar_element.CompuScale(symbol="symbol")
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <SYMBOL>symbol</SYMBOL>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.symbol, "symbol")

    def test_write_read_desc(self): # noqa D102
        desc = ar_element.MultiLanguageOverviewParagraph((ar_enum.Language.FOR_ALL, 'Description'))
        element = ar_element.CompuScale(desc=desc)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <DESC>
    <L-2 L="FOR-ALL">Description</L-2>
  </DESC>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        desc = elem.desc
        self.assertEqual(desc.elements[0].language, ar_enum.Language.FOR_ALL)
        self.assertEqual(desc.elements[0].parts[0], "Description")

    def test_write_read_mask(self): # noqa D102
        element = ar_element.CompuScale(mask=255)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <MASK>255</MASK>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.mask, 255)

    def test_write_read_limit_with_default_interval_type(self): # noqa D102
        element = ar_element.CompuScale(lower_limit=1, upper_limit=2)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">1</LOWER-LIMIT>
  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">2</UPPER-LIMIT>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.lower_limit, 1)
        self.assertEqual(elem.upper_limit, 2)
        self.assertEqual(elem.lower_limit_type, ar_enum.IntervalType.CLOSED)
        self.assertEqual(elem.upper_limit_type, ar_enum.IntervalType.CLOSED)

    def test_read_limits_missing_interval_type(self): # noqa D102
        xml = '''<COMPU-SCALE>
  <LOWER-LIMIT>1</LOWER-LIMIT>
  <UPPER-LIMIT>2</UPPER-LIMIT>
</COMPU-SCALE>'''
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.lower_limit, 1)
        self.assertEqual(elem.upper_limit, 2)
        self.assertEqual(elem.lower_limit_type, ar_enum.IntervalType.CLOSED)
        self.assertEqual(elem.upper_limit_type, ar_enum.IntervalType.CLOSED)

    def test_write_read_limit_with_open_interval_type(self): # noqa D102
        element = ar_element.CompuScale(lower_limit=float("-Inf"),
                                        upper_limit=float("Inf"),
                                        lower_limit_type=ar_enum.IntervalType.OPEN,
                                        upper_limit_type=ar_enum.IntervalType.OPEN,)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <LOWER-LIMIT INTERVAL-TYPE="OPEN">-INF</LOWER-LIMIT>
  <UPPER-LIMIT INTERVAL-TYPE="OPEN">INF</UPPER-LIMIT>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.lower_limit, float("-Inf"))
        self.assertEqual(elem.upper_limit, float("Inf"))
        self.assertEqual(elem.lower_limit_type, ar_enum.IntervalType.OPEN)
        self.assertEqual(elem.upper_limit_type, ar_enum.IntervalType.OPEN)

    def test_write_read_inverse_value(self): # noqa D102
        element = ar_element.CompuScale(inverse_value=-1)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-SCALE>
  <COMPU-INVERSE-VALUE>
    <V>-1</V>
  </COMPU-INVERSE-VALUE>
</COMPU-SCALE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuScale = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuScale)
        self.assertEqual(elem.inverse_value.value, -1)


class TestComputation(unittest.TestCase): # noqa D101

    def test_make_simple_value_table(self): # noqa D102
        element = ar_element.Computation.make_value_table(["FALSE", "TRUE"], auto_label=False)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, 'COMPU-INTERNAL-TO-PHYS')
        self.assertEqual(xml, '''<COMPU-INTERNAL-TO-PHYS>
  <COMPU-SCALES>
    <COMPU-SCALE>
      <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
      <UPPER-LIMIT INTERVAL-TYPE="CLOSED">0</UPPER-LIMIT>
      <COMPU-CONST>
        <VT>FALSE</VT>
      </COMPU-CONST>
    </COMPU-SCALE>
    <COMPU-SCALE>
      <LOWER-LIMIT INTERVAL-TYPE="CLOSED">1</LOWER-LIMIT>
      <UPPER-LIMIT INTERVAL-TYPE="CLOSED">1</UPPER-LIMIT>
      <COMPU-CONST>
        <VT>TRUE</VT>
      </COMPU-CONST>
    </COMPU-SCALE>
  </COMPU-SCALES>
</COMPU-INTERNAL-TO-PHYS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.Computation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Computation)
        self.assertEqual(elem.compu_scales[0].content.value, "FALSE")
        self.assertEqual(elem.compu_scales[1].content.value, "TRUE")

    def test_make_int_to_phys_rational(self): # noqa D102
        element = ar_element.Computation.make_rational(scaling_factor=1 / 64,
                                                       offset=0,
                                                       lower_limit=0,
                                                       upper_limit=65535,
                                                       default_value=65535)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, 'COMPU-INTERNAL-TO-PHYS')
        self.assertEqual(xml, '''<COMPU-INTERNAL-TO-PHYS>
  <COMPU-SCALES>
    <COMPU-SCALE>
      <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
      <UPPER-LIMIT INTERVAL-TYPE="CLOSED">65535</UPPER-LIMIT>
      <COMPU-RATIONAL-COEFFS>
        <COMPU-NUMERATOR>
          <V>0</V>
          <V>0.015625</V>
        </COMPU-NUMERATOR>
        <COMPU-DENOMINATOR>
          <V>1</V>
        </COMPU-DENOMINATOR>
      </COMPU-RATIONAL-COEFFS>
    </COMPU-SCALE>
  </COMPU-SCALES>
  <COMPU-DEFAULT-VALUE>
    <V>65535</V>
  </COMPU-DEFAULT-VALUE>
</COMPU-INTERNAL-TO-PHYS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.Computation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.Computation)
        self.assertEqual(elem.compu_scales[0].content.numerator, (0, 0.015625))
        self.assertEqual(elem.compu_scales[0].content.denominator, (1,))
        self.assertEqual(elem.default_value.value, 65535)


class TestCompuMethod(unittest.TestCase): # noqa D101

    def test_write_read_compumethod_boolean(self): # noqa D102
        computation = ar_element.Computation.make_value_table(["FALSE", "TRUE"], default_value="FALSE")
        element = ar_element.CompuMethod("boolean",
                                         int_to_phys=computation,
                                         category="TEXTTABLE")
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<COMPU-METHOD>
  <SHORT-NAME>boolean</SHORT-NAME>
  <CATEGORY>TEXTTABLE</CATEGORY>
  <COMPU-INTERNAL-TO-PHYS>
    <COMPU-SCALES>
      <COMPU-SCALE>
        <SHORT-LABEL>FALSE</SHORT-LABEL>
        <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
        <UPPER-LIMIT INTERVAL-TYPE="CLOSED">0</UPPER-LIMIT>
        <COMPU-CONST>
          <VT>FALSE</VT>
        </COMPU-CONST>
      </COMPU-SCALE>
      <COMPU-SCALE>
        <SHORT-LABEL>TRUE</SHORT-LABEL>
        <LOWER-LIMIT INTERVAL-TYPE="CLOSED">1</LOWER-LIMIT>
        <UPPER-LIMIT INTERVAL-TYPE="CLOSED">1</UPPER-LIMIT>
        <COMPU-CONST>
          <VT>TRUE</VT>
        </COMPU-CONST>
      </COMPU-SCALE>
    </COMPU-SCALES>
    <COMPU-DEFAULT-VALUE>
      <VT>FALSE</VT>
    </COMPU-DEFAULT-VALUE>
  </COMPU-INTERNAL-TO-PHYS>
</COMPU-METHOD>''')
        reader = autosar.xml.Reader()
        elem: ar_element.CompuMethod = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompuMethod)
        self.assertEqual(elem.int_to_phys.compu_scales[0].content.value, "FALSE")
        self.assertEqual(elem.int_to_phys.compu_scales[1].content.value, "TRUE")
        self.assertEqual(elem.int_to_phys.default_value.value, "FALSE")


if __name__ == '__main__':
    unittest.main()
