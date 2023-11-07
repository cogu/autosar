"""Unit tests for constants and value specifications."""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
#import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestTextValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.TextValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<TEXT-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.TextValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TextValueSpecification)

    def test_read_write_label(self):
        element = ar_element.TextValueSpecification(label="MyLabel")
        writer = autosar.xml.Writer()
        xml = '''<TEXT-VALUE-SPECIFICATION>
  <SHORT-LABEL>MyLabel</SHORT-LABEL>
</TEXT-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.TextValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TextValueSpecification)
        self.assertEqual(elem.label, "MyLabel")

    def test_read_write_value(self):
        element = ar_element.TextValueSpecification(value="MyValue")
        writer = autosar.xml.Writer()
        xml = '''<TEXT-VALUE-SPECIFICATION>
  <VALUE>MyValue</VALUE>
</TEXT-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.TextValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TextValueSpecification)
        self.assertEqual(elem.value, "MyValue")


class TestNumericalValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.NumericalValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NUMERICAL-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalValueSpecification)

    def test_read_write_int_value(self):
        element = ar_element.NumericalValueSpecification(value=4)
        writer = autosar.xml.Writer()
        xml = '''<NUMERICAL-VALUE-SPECIFICATION>
  <VALUE>4</VALUE>
</NUMERICAL-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.value, 4)

    def test_read_write_float_value(self):
        element = ar_element.NumericalValueSpecification(value=4 / 10)
        writer = autosar.xml.Writer()
        xml = '''<NUMERICAL-VALUE-SPECIFICATION>
  <VALUE>0.4</VALUE>
</NUMERICAL-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalValueSpecification)
        self.assertAlmostEqual(elem.value, 0.4)


class TestNotAvailableValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.NotAvailableValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NOT-AVAILABLE-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NotAvailableValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NotAvailableValueSpecification)

    def test_read_write_default_pattern(self):
        element = ar_element.NotAvailableValueSpecification(default_pattern=255)
        writer = autosar.xml.Writer()
        xml = '''<NOT-AVAILABLE-VALUE-SPECIFICATION>
  <DEFAULT-PATTERN>255</DEFAULT-PATTERN>
</NOT-AVAILABLE-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NotAvailableValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NotAvailableValueSpecification)
        self.assertEqual(elem.default_pattern, 255)


class TestArrayValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.ArrayValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<ARRAY-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ArrayValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArrayValueSpecification)

    def test_read_write_label(self):
        element = ar_element.ArrayValueSpecification(label="MyLabel")
        writer = autosar.xml.Writer()
        xml = '''<ARRAY-VALUE-SPECIFICATION>
  <SHORT-LABEL>MyLabel</SHORT-LABEL>
</ARRAY-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArrayValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArrayValueSpecification)
        self.assertEqual(elem.label, "MyLabel")

    def test_read_write_numerical_elements(self):
        element = ar_element.ArrayValueSpecification()
        element.append(ar_element.NumericalValueSpecification(value=1))
        element.append(ar_element.NumericalValueSpecification(value=2))
        element.append(ar_element.NumericalValueSpecification(value=3))
        writer = autosar.xml.Writer()
        xml = '''<ARRAY-VALUE-SPECIFICATION>
  <ELEMENTS>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>1</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>2</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>3</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </ELEMENTS>
</ARRAY-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArrayValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArrayValueSpecification)
        self.assertEqual(len(elem.elements), 3)
        child_elem = elem.elements[0]
        self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
        self.assertEqual(child_elem.value, 1)
        child_elem = elem.elements[1]
        self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
        self.assertEqual(child_elem.value, 2)
        child_elem = elem.elements[2]
        self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
        self.assertEqual(child_elem.value, 3)

    def test_read_write_text_elements(self):
        element = ar_element.ArrayValueSpecification()
        element.append(ar_element.TextValueSpecification(value="First"))
        element.append(ar_element.TextValueSpecification(value="Second"))
        writer = autosar.xml.Writer()
        xml = '''<ARRAY-VALUE-SPECIFICATION>
  <ELEMENTS>
    <TEXT-VALUE-SPECIFICATION>
      <VALUE>First</VALUE>
    </TEXT-VALUE-SPECIFICATION>
    <TEXT-VALUE-SPECIFICATION>
      <VALUE>Second</VALUE>
    </TEXT-VALUE-SPECIFICATION>
  </ELEMENTS>
</ARRAY-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArrayValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArrayValueSpecification)
        self.assertEqual(len(elem.elements), 2)
        child_elem = elem.elements[0]
        self.assertIsInstance(child_elem, ar_element.TextValueSpecification)
        self.assertEqual(child_elem.value, "First")
        child_elem = elem.elements[1]
        self.assertIsInstance(child_elem, ar_element.TextValueSpecification)
        self.assertEqual(child_elem.value, "Second")


class TestRecordValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.RecordValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<RECORD-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.RecordValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RecordValueSpecification)

    def test_read_write_numerical_elements(self):
        element = ar_element.RecordValueSpecification()
        element.append(ar_element.NumericalValueSpecification(label="First", value=1))
        element.append(ar_element.NumericalValueSpecification(label="Second", value=2))
        element.append(ar_element.NumericalValueSpecification(label="Third", value=3))
        writer = autosar.xml.Writer()
        xml = '''<RECORD-VALUE-SPECIFICATION>
  <FIELDS>
    <NUMERICAL-VALUE-SPECIFICATION>
      <SHORT-LABEL>First</SHORT-LABEL>
      <VALUE>1</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
    <NUMERICAL-VALUE-SPECIFICATION>
      <SHORT-LABEL>Second</SHORT-LABEL>
      <VALUE>2</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
    <NUMERICAL-VALUE-SPECIFICATION>
      <SHORT-LABEL>Third</SHORT-LABEL>
      <VALUE>3</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </FIELDS>
</RECORD-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RecordValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RecordValueSpecification)
        self.assertEqual(len(elem.fields), 3)
        child_elem = elem.fields[0]
        self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
        self.assertEqual(child_elem.label, "First")
        self.assertEqual(child_elem.value, 1)
        child_elem = elem.fields[1]
        self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
        self.assertEqual(child_elem.label, "Second")
        self.assertEqual(child_elem.value, 2)
        child_elem = elem.fields[2]
        self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
        self.assertEqual(child_elem.label, "Third")
        self.assertEqual(child_elem.value, 3)


class TestValueBuilder(unittest.TestCase):

    def test_make_numerical_from_int(self):
        element: ar_element.NumericalValueSpecification = ar_element.ValueSpecification.make_value(10)
        self.assertIsInstance(element, ar_element.NumericalValueSpecification)
        self.assertIsNone(element.label)
        self.assertEqual(element.value, 10)

        element: ar_element.NumericalValueSpecification = ar_element.ValueSpecification.make_value(("MyLabel", 20))
        self.assertIsInstance(element, ar_element.NumericalValueSpecification)
        self.assertEqual(element.label, "MyLabel")
        self.assertEqual(element.value, 20)

    def test_make_text_str(self):
        element: ar_element.TextValueSpecification = ar_element.ValueSpecification.make_value("Value")
        self.assertIsInstance(element, ar_element.TextValueSpecification)
        self.assertIsNone(element.label)
        self.assertEqual(element.value, "Value")

    def test_make_not_available_from_none(self):
        element: ar_element.NotAvailableValueSpecification = ar_element.ValueSpecification.make_value(None)
        self.assertIsInstance(element, ar_element.NotAvailableValueSpecification)
        self.assertIsNone(element.label)

        element: ar_element.NotAvailableValueSpecification
        element = ar_element.ValueSpecification.make_value(("MyLabel", None, 255))
        self.assertIsInstance(element, ar_element.NotAvailableValueSpecification)
        self.assertEqual(element.label, "MyLabel")
        self.assertEqual(element.default_pattern, 255)

    def test_make_array_from_list(self):
        element: ar_element.ArrayValueSpecification
        element = ar_element.ValueSpecification.make_value(["ARRAY", 1, 2, 3])
        self.assertIsInstance(element, ar_element.ArrayValueSpecification)
        self.assertEqual(len(element.elements), 3)
        for i, child_elem in enumerate(element.elements, 1):
            self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
            self.assertEqual(child_elem.value, i)

    def test_make_multi_level_array(self):
        element: ar_element.ArrayValueSpecification
        element = ar_element.ValueSpecification.make_value(["ARRAY",
                                                            ["ARRAY", 1, 2, 3],
                                                            ["ARRAY", 4, 5, 6],
                                                            ["ARRAY", 7, 8, 9]
                                                            ])
        self.assertIsInstance(element, ar_element.ArrayValueSpecification)
        self.assertEqual(len(element.elements), 3)
        child_elem: ar_element.ArrayValueSpecification = element.elements[0]
        self.assertIsInstance(child_elem, ar_element.ArrayValueSpecification)
        self.assertEqual(len(child_elem.elements), 3)
        for i, grand_child in enumerate(child_elem.elements, 1):
            self.assertIsInstance(grand_child, ar_element.NumericalValueSpecification)
            self.assertEqual(grand_child.value, i)
        child_elem = element.elements[1]
        self.assertIsInstance(child_elem, ar_element.ArrayValueSpecification)
        self.assertEqual(len(child_elem.elements), 3)
        for i, grand_child in enumerate(child_elem.elements, 4):
            self.assertIsInstance(grand_child, ar_element.NumericalValueSpecification)
            self.assertEqual(grand_child.value, i)
        child_elem = element.elements[2]
        self.assertIsInstance(child_elem, ar_element.ArrayValueSpecification)
        self.assertEqual(len(child_elem.elements), 3)
        for i, grand_child in enumerate(child_elem.elements, 7):
            self.assertIsInstance(grand_child, ar_element.NumericalValueSpecification)
            self.assertEqual(grand_child.value, i)

    def test_make_record_from_list(self):
        element: ar_element.RecordValueSpecification
        element = ar_element.ValueSpecification.make_value(["RECORD", 1, 2, 3])
        self.assertIsInstance(element, ar_element.RecordValueSpecification)
        self.assertEqual(len(element.fields), 3)
        for i, child_elem in enumerate(element.fields, 1):
            self.assertIsInstance(child_elem, ar_element.NumericalValueSpecification)
            self.assertEqual(child_elem.value, i)

    def test_make_array_of_records_with_labels(self):
        element: ar_element.ArrayValueSpecification
        element = ar_element.ValueSpecification.make_value(["ARRAY",
                                                            ["RECORD",
                                                             ("First", 1),
                                                             ("Second", 2),
                                                             ("Third", 3),
                                                             ],
                                                            ["RECORD",
                                                             ("First", 4),
                                                             ("Second", 5),
                                                             ("Third", 6),
                                                             ],
                                                            ["RECORD",
                                                             ("First", 7),
                                                             ("Second", 8),
                                                             ("Third", 9),
                                                             ],
                                                            ])
        self.assertIsInstance(element, ar_element.ArrayValueSpecification)
        self.assertEqual(len(element.elements), 3)
        child_elem: ar_element.RecordValueSpecification
        labels = ["First", "Second", "Third"]
        for i, child_elem in enumerate(element.elements, 0):
            self.assertIsInstance(child_elem, ar_element.RecordValueSpecification)
            self.assertEqual(len(child_elem.fields), 3)
            grand_child: ar_element.NumericalValueSpecification
            for j, grand_child in enumerate(child_elem.fields):
                self.assertEqual(grand_child.label, labels[j])
                self.assertEqual(grand_child.value, i * 3 + j + 1)


class TestApplicationValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.ApplicationValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<APPLICATION-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationValueSpecification)

    def test_read_write_category(self):
        element = ar_element.ApplicationValueSpecification(category="MyCategory")
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-VALUE-SPECIFICATION>
  <CATEGORY>MyCategory</CATEGORY>
</APPLICATION-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationValueSpecification)
        self.assertEqual(elem.category, "MyCategory")

    def test_read_write_sw_axis_cont_single(self):
        sw_axis_cont = ar_element.SwAxisCont(unit_ref=ar_element.UnitRef("/Units/MyUnit"))
        element = ar_element.ApplicationValueSpecification(sw_axis_conts=sw_axis_cont)
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-VALUE-SPECIFICATION>
  <SW-AXIS-CONTS>
    <SW-AXIS-CONT>
      <UNIT-REF DEST="UNIT">/Units/MyUnit</UNIT-REF>
    </SW-AXIS-CONT>
  </SW-AXIS-CONTS>
</APPLICATION-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationValueSpecification)
        self.assertEqual(str(elem.sw_axis_conts[0].unit_ref), "/Units/MyUnit")

    def test_read_write_sw_axis_cont_multi(self):
        sw_axis_cont1 = ar_element.SwAxisCont(unit_ref=ar_element.UnitRef("/Units/MyUnit1"))
        sw_axis_cont2 = ar_element.SwAxisCont(unit_ref=ar_element.UnitRef("/Units/MyUnit2"))
        element = ar_element.ApplicationValueSpecification(sw_axis_conts=[sw_axis_cont1, sw_axis_cont2])
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-VALUE-SPECIFICATION>
  <SW-AXIS-CONTS>
    <SW-AXIS-CONT>
      <UNIT-REF DEST="UNIT">/Units/MyUnit1</UNIT-REF>
    </SW-AXIS-CONT>
    <SW-AXIS-CONT>
      <UNIT-REF DEST="UNIT">/Units/MyUnit2</UNIT-REF>
    </SW-AXIS-CONT>
  </SW-AXIS-CONTS>
</APPLICATION-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationValueSpecification)
        self.assertEqual(str(elem.sw_axis_conts[0].unit_ref), "/Units/MyUnit1")
        self.assertEqual(str(elem.sw_axis_conts[1].unit_ref), "/Units/MyUnit2")

    def test_read_write_sw_value_cont(self):
        sw_value_cont = ar_element.SwValueCont(sw_values_phys=ar_element.SwValues([1, 2, 3, 4]))
        element = ar_element.ApplicationValueSpecification(sw_value_cont=sw_value_cont)
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-VALUE-SPECIFICATION>
  <SW-VALUE-CONT>
    <SW-VALUES-PHYS>
      <V>1</V>
      <V>2</V>
      <V>3</V>
      <V>4</V>
    </SW-VALUES-PHYS>
  </SW-VALUE-CONT>
</APPLICATION-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationValueSpecification)
        self.assertEqual(elem.sw_value_cont.sw_values_phys.values, [1, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()
