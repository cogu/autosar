"""Unit tests for constants and value specifications."""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element # noqa E402
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.exception as ar_exception # noqa E402
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


class TestConstantSpecification(unittest.TestCase):

    def test_read_write_name_only(self):
        element = ar_element.ConstantSpecification("MyName")
        writer = autosar.xml.Writer()
        xml = '''<CONSTANT-SPECIFICATION>
  <SHORT-NAME>MyName</SHORT-NAME>
</CONSTANT-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantSpecification)
        self.assertEqual(elem.name, "MyName")

    def test_read_write_value_spec_from_object(self):
        value = ar_element.NumericalValueSpecification(label="MyLabel", value=2.5)
        element = ar_element.ConstantSpecification("MyName", value=value)
        writer = autosar.xml.Writer()
        xml = '''<CONSTANT-SPECIFICATION>
  <SHORT-NAME>MyName</SHORT-NAME>
  <VALUE-SPEC>
    <NUMERICAL-VALUE-SPECIFICATION>
      <SHORT-LABEL>MyLabel</SHORT-LABEL>
      <VALUE>2.5</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </VALUE-SPEC>
</CONSTANT-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantSpecification)
        self.assertEqual(elem.name, "MyName")
        self.assertEqual(elem.value.label, "MyLabel")
        self.assertEqual(elem.value.value, 2.5)

    def test_read_write_value_spec_made_from_value_builder(self):
        element = ar_element.ConstantSpecification.make_constant("MyName",
                                                                 ("MyLabel", 2.5))
        writer = autosar.xml.Writer()
        xml = '''<CONSTANT-SPECIFICATION>
  <SHORT-NAME>MyName</SHORT-NAME>
  <VALUE-SPEC>
    <NUMERICAL-VALUE-SPECIFICATION>
      <SHORT-LABEL>MyLabel</SHORT-LABEL>
      <VALUE>2.5</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </VALUE-SPEC>
</CONSTANT-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantSpecification)
        self.assertEqual(elem.name, "MyName")
        self.assertEqual(elem.value.label, "MyLabel")
        self.assertEqual(elem.value.value, 2.5)


class TestConstantReference(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.ConstantReference()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<CONSTANT-REFERENCE/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantReference = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantReference)

    def test_read_write_constant_ref_from_object(self):
        element = ar_element.ConstantReference(constant_ref=ar_element.ConstantRef("/Constants/MyConstant"))
        writer = autosar.xml.Writer()
        xml = '''<CONSTANT-REFERENCE>
  <CONSTANT-REF DEST="CONSTANT-SPECIFICATION">/Constants/MyConstant</CONSTANT-REF>
</CONSTANT-REFERENCE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantReference = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantReference)
        self.assertEqual(str(elem.constant_ref), "/Constants/MyConstant")

    def test_read_write_constant_ref_from_str(self):
        element = ar_element.ConstantReference(constant_ref="/Constants/MyConstant")
        writer = autosar.xml.Writer()
        xml = '''<CONSTANT-REFERENCE>
  <CONSTANT-REF DEST="CONSTANT-SPECIFICATION">/Constants/MyConstant</CONSTANT-REF>
</CONSTANT-REFERENCE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantReference = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantReference)
        self.assertEqual(str(elem.constant_ref), "/Constants/MyConstant")

    def test_read_write_label(self):
        element = ar_element.ConstantReference(label="MyLabel")
        writer = autosar.xml.Writer()
        xml = '''<CONSTANT-REFERENCE>
  <SHORT-LABEL>MyLabel</SHORT-LABEL>
</CONSTANT-REFERENCE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ConstantReference = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ConstantReference)
        self.assertEqual(elem.label, "MyLabel")


class TestReferenceValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.ReferenceValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<REFERENCE-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ReferenceValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ReferenceValueSpecification)
        self.assertIsNone(elem.reference_value)

    def test_read_write_reference_value_from_object(self):
        ref = ar_element.DataPrototypeRef("/Component/MyPrototype",
                                          ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
        element = ar_element.ReferenceValueSpecification(reference_value=ref)
        writer = autosar.xml.Writer()
        xml = '''<REFERENCE-VALUE-SPECIFICATION>
  <REFERENCE-VALUE-REF DEST="VARIABLE-DATA-PROTOTYPE">/Component/MyPrototype</REFERENCE-VALUE-REF>
</REFERENCE-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ReferenceValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ReferenceValueSpecification)
        self.assertIsInstance(elem.reference_value, ar_element.DataPrototypeRef)
        self.assertEqual(str(elem.reference_value), "/Component/MyPrototype")
        self.assertEqual(elem.reference_value.dest, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)

    def test_read_write_label(self):
        ref = ar_element.DataPrototypeRef("/Component/MyPrototype",
                                          ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
        element = ar_element.ReferenceValueSpecification(label="MyLabel",
                                                         reference_value=ref)
        writer = autosar.xml.Writer()
        xml = '''<REFERENCE-VALUE-SPECIFICATION>
  <SHORT-LABEL>MyLabel</SHORT-LABEL>
  <REFERENCE-VALUE-REF DEST="VARIABLE-DATA-PROTOTYPE">/Component/MyPrototype</REFERENCE-VALUE-REF>
</REFERENCE-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ReferenceValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ReferenceValueSpecification)
        self.assertEqual(elem.label, "MyLabel")
        self.assertEqual(str(elem.reference_value), "/Component/MyPrototype")
        self.assertEqual(elem.reference_value.dest, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)

    def test_make_value_with_check(self):
        ref = ar_element.DataPrototypeRef("/Component/MyPrototype",
                                          ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
        val = ar_element.ValueSpecification.make_value_with_check(ref)
        self.assertIsInstance(val, ar_element.ReferenceValueSpecification)
        self.assertEqual(str(val.reference_value), "/Component/MyPrototype")
        self.assertEqual(val.reference_value.dest, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)

    def test_invalid_reference_value_type(self):
        with self.assertRaises(TypeError):
            ar_element.ReferenceValueSpecification(reference_value=123)
        with self.assertRaises(TypeError):
            ar_element.ReferenceValueSpecification(reference_value="/Component/MyPrototype")


class TestNumericalOrText(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.NumericalOrText()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<VTF/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalOrText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalOrText)
        self.assertIsNone(elem.vf)
        self.assertIsNone(elem.vt)

    def test_read_write_vf_int(self):
        element = ar_element.NumericalOrText(vf=10)
        writer = autosar.xml.Writer()
        xml = '''<VTF>
  <VF>10</VF>
</VTF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalOrText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalOrText)
        self.assertEqual(elem.vf, 10)
        self.assertIsNone(elem.vt)

    def test_read_write_vf_float(self):
        element = ar_element.NumericalOrText(vf=3.14)
        writer = autosar.xml.Writer()
        xml = '''<VTF>
  <VF>3.14</VF>
</VTF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalOrText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalOrText)
        self.assertEqual(elem.vf, 3.14)
        self.assertIsNone(elem.vt)

    def test_read_write_vf_hex(self):
        element = ar_element.NumericalOrText(vf=ar_element.NumericalValue("0x10"))
        writer = autosar.xml.Writer()
        xml = '''<VTF>
  <VF>0x10</VF>
</VTF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalOrText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalOrText)
        self.assertIsInstance(elem.vf, ar_element.NumericalValue)
        self.assertEqual(elem.vf.value, 16)
        self.assertEqual(elem.vf.value_format, ar_enum.ValueFormat.HEXADECIMAL)

    def test_read_write_vt(self):
        element = ar_element.NumericalOrText(vt="Hello")
        writer = autosar.xml.Writer()
        xml = '''<VTF>
  <VT>Hello</VT>
</VTF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalOrText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalOrText)
        self.assertIsNone(elem.vf)
        self.assertEqual(elem.vt, "Hello")

    def test_read_write_both(self):
        element = ar_element.NumericalOrText(vf=1, vt="One")
        writer = autosar.xml.Writer()
        xml = '''<VTF>
  <VF>1</VF>
  <VT>One</VT>
</VTF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalOrText = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalOrText)
        self.assertEqual(elem.vf, 1)
        self.assertEqual(elem.vt, "One")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            ar_element.NumericalOrText(vf="not_a_number")
        with self.assertRaises(TypeError):
            ar_element.NumericalOrText(vt=123)


class TestRuleArguments(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.RuleArguments()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<RULE-ARGUMENTS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(len(elem.values), 0)

    def test_read_write_single_int(self):
        element = ar_element.RuleArguments(10)
        writer = autosar.xml.Writer()
        xml = '''<RULE-ARGUMENTS>
  <V>10</V>
</RULE-ARGUMENTS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(elem.values, [10])

    def test_read_write_single_float(self):
        element = ar_element.RuleArguments(2.5)
        writer = autosar.xml.Writer()
        xml = '''<RULE-ARGUMENTS>
  <V>2.5</V>
</RULE-ARGUMENTS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(elem.values, [2.5])

    def test_read_write_single_text(self):
        element = ar_element.RuleArguments("TextValue")
        writer = autosar.xml.Writer()
        xml = '''<RULE-ARGUMENTS>
  <VT>TextValue</VT>
</RULE-ARGUMENTS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(elem.values, ["TextValue"])

    def test_read_write_numerical_or_text(self):
        element = ar_element.RuleArguments(ar_element.NumericalOrText(vf=5, vt="Five"))
        writer = autosar.xml.Writer()
        xml = '''<RULE-ARGUMENTS>
  <VTF>
    <VF>5</VF>
    <VT>Five</VT>
  </VTF>
</RULE-ARGUMENTS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(len(elem.values), 1)
        self.assertIsInstance(elem.values[0], ar_element.NumericalOrText)
        self.assertEqual(elem.values[0].vf, 5)
        self.assertEqual(elem.values[0].vt, "Five")

    def test_read_write_mixed_list(self):
        element = ar_element.RuleArguments([10, "Hello", 2.5, ar_element.NumericalOrText(vf=1)])
        writer = autosar.xml.Writer()
        xml = '''<RULE-ARGUMENTS>
  <V>10</V>
  <VT>Hello</VT>
  <V>2.5</V>
  <VTF>
    <VF>1</VF>
  </VTF>
</RULE-ARGUMENTS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(len(elem.values), 4)
        self.assertEqual(elem.values[0], 10)
        self.assertEqual(elem.values[1], "Hello")
        self.assertEqual(elem.values[2], 2.5)
        self.assertIsInstance(elem.values[3], ar_element.NumericalOrText)
        self.assertEqual(elem.values[3].vf, 1)

    def test_read_vf_element(self):
        xml = '''<RULE-ARGUMENTS>
  <VF>42</VF>
</RULE-ARGUMENTS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.RuleArguments = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleArguments)
        self.assertEqual(elem.values, [42])

    def test_append_and_type_errors(self):
        elem = ar_element.RuleArguments()
        elem.append(100)
        elem.append("str")
        self.assertEqual(elem.values, [100, "str"])
        with self.assertRaises(TypeError):
            ar_element.RuleArguments(values=object())
        with self.assertRaises(TypeError):
            elem.append(object())


class TestRuleBasedValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.RuleBasedValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<RULE-BASED-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedValueSpecification)
        self.assertIsNone(elem.rule)
        self.assertEqual(len(elem.arguments), 0)
        self.assertIsNone(elem.max_size_to_fill)

    def test_read_write_rule_only(self):
        element = ar_element.RuleBasedValueSpecification(rule="FILL")
        writer = autosar.xml.Writer()
        xml = '''<RULE-BASED-VALUE-SPECIFICATION>
  <RULE>FILL</RULE>
</RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedValueSpecification)
        self.assertEqual(elem.rule, "FILL")
        self.assertEqual(len(elem.arguments), 0)
        self.assertIsNone(elem.max_size_to_fill)

    def test_read_write_full(self):
        args = ar_element.RuleArguments([0])
        element = ar_element.RuleBasedValueSpecification(
            rule="FILL",
            arguments=args,
            max_size_to_fill=100
        )
        writer = autosar.xml.Writer()
        xml = '''<RULE-BASED-VALUE-SPECIFICATION>
  <RULE>FILL</RULE>
  <ARGUMENTSS>
    <RULE-ARGUMENTS>
      <V>0</V>
    </RULE-ARGUMENTS>
  </ARGUMENTSS>
  <MAX-SIZE-TO-FILL>100</MAX-SIZE-TO-FILL>
</RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedValueSpecification)
        self.assertEqual(elem.rule, "FILL")
        self.assertEqual(len(elem.arguments), 1)
        self.assertEqual(elem.arguments[0].values, [0])
        self.assertEqual(elem.max_size_to_fill, 100)

    def test_read_rule_based_values_tag(self):
        xml = '''<RULE-BASED-VALUES>
  <RULE>RAMP</RULE>
  <ARGUMENTSS>
    <RULE-ARGUMENTS>
      <V>0</V>
      <V>1</V>
    </RULE-ARGUMENTS>
  </ARGUMENTSS>
  <MAX-SIZE-TO-FILL>50</MAX-SIZE-TO-FILL>
</RULE-BASED-VALUES>'''
        reader = autosar.xml.Reader()
        elem: ar_element.RuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RuleBasedValueSpecification)
        self.assertEqual(elem.rule, "RAMP")
        self.assertEqual(len(elem.arguments), 1)
        self.assertEqual(elem.arguments[0].values, [0, 1])
        self.assertEqual(elem.max_size_to_fill, 50)

    def test_append_and_type_errors(self):
        elem = ar_element.RuleBasedValueSpecification()
        args = ar_element.RuleArguments([10])
        elem.append(args)
        self.assertEqual(len(elem.arguments), 1)
        with self.assertRaises(TypeError):
            ar_element.RuleBasedValueSpecification(rule=123)
        with self.assertRaises(TypeError):
            ar_element.RuleBasedValueSpecification(arguments=object())
        with self.assertRaises(TypeError):
            ar_element.RuleBasedValueSpecification(max_size_to_fill="not_int")
        with self.assertRaises(TypeError):
            elem.append(object())


class TestNumericalRuleBasedValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.NumericalRuleBasedValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NUMERICAL-RULE-BASED-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalRuleBasedValueSpecification)
        self.assertIsNone(elem.label)
        self.assertIsNone(elem.rule_based_values)

    def test_read_write_with_label(self):
        element = ar_element.NumericalRuleBasedValueSpecification(label="MyRuleValue")
        writer = autosar.xml.Writer()
        xml = '''<NUMERICAL-RULE-BASED-VALUE-SPECIFICATION>
  <SHORT-LABEL>MyRuleValue</SHORT-LABEL>
</NUMERICAL-RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalRuleBasedValueSpecification)
        self.assertEqual(elem.label, "MyRuleValue")
        self.assertIsNone(elem.rule_based_values)

    def test_read_write_full_fill_until_end(self):
        rbv = ar_element.RuleBasedValueSpecification(
            rule="FILL_UNTIL_END",
            arguments=ar_element.RuleArguments([10, 20, 0]),
            max_size_to_fill=100
        )
        element = ar_element.NumericalRuleBasedValueSpecification(
            label="FilledArray",
            rule_based_values=rbv
        )
        writer = autosar.xml.Writer()
        xml = '''<NUMERICAL-RULE-BASED-VALUE-SPECIFICATION>
  <SHORT-LABEL>FilledArray</SHORT-LABEL>
  <RULE-BASED-VALUES>
    <RULE>FILL_UNTIL_END</RULE>
    <ARGUMENTSS>
      <RULE-ARGUMENTS>
        <V>10</V>
        <V>20</V>
        <V>0</V>
      </RULE-ARGUMENTS>
    </ARGUMENTSS>
    <MAX-SIZE-TO-FILL>100</MAX-SIZE-TO-FILL>
  </RULE-BASED-VALUES>
</NUMERICAL-RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NumericalRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NumericalRuleBasedValueSpecification)
        self.assertEqual(elem.label, "FilledArray")
        self.assertIsNotNone(elem.rule_based_values)
        self.assertEqual(elem.rule_based_values.rule, "FILL_UNTIL_END")
        self.assertEqual(elem.rule_based_values.max_size_to_fill, 100)
        self.assertEqual(len(elem.rule_based_values.arguments), 1)
        self.assertEqual(elem.rule_based_values.arguments[0].values, [10, 20, 0])

    def test_make_value_with_check(self):
        rbv = ar_element.RuleBasedValueSpecification(
            rule="FILL",
            arguments=ar_element.RuleArguments(0)
        )
        val = ar_element.ValueSpecification.make_value_with_check(rbv)
        self.assertIsInstance(val, ar_element.NumericalRuleBasedValueSpecification)
        self.assertIs(val.rule_based_values, rbv)

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            ar_element.NumericalRuleBasedValueSpecification(rule_based_values=object())


class TestApplicationRuleBasedValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.ApplicationRuleBasedValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<APPLICATION-RULE-BASED-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRuleBasedValueSpecification)
        self.assertIsNone(elem.label)
        self.assertIsNone(elem.category)
        self.assertEqual(len(elem.sw_axis_conts), 0)
        self.assertIsNone(elem.sw_value_cont)

    def test_read_write_full(self):
        axis = ar_element.RuleBasedAxisCont(
            category=ar_enum.CalibrationAxisCategory.STD_AXIS,
            sw_axis_index=1,
            rule_based_values=ar_element.RuleBasedValueSpecification(
                rule="RAMP",
                arguments=ar_element.RuleArguments([0, 5]),
                max_size_to_fill=5
            )
        )
        val_cont = ar_element.RuleBasedValueCont(
            sw_array_size=ar_element.ValueList([5]),
            rule_based_values=ar_element.RuleBasedValueSpecification(
                rule="FILL",
                arguments=ar_element.RuleArguments(0),
                max_size_to_fill=5
            )
        )
        element = ar_element.ApplicationRuleBasedValueSpecification(
            label="CurveValue",
            category="CURVE",
            sw_axis_conts=axis,
            sw_value_cont=val_cont
        )
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-RULE-BASED-VALUE-SPECIFICATION>
  <SHORT-LABEL>CurveValue</SHORT-LABEL>
  <CATEGORY>CURVE</CATEGORY>
  <SW-AXIS-CONTS>
    <RULE-BASED-AXIS-CONT>
      <CATEGORY>STD_AXIS</CATEGORY>
      <SW-AXIS-INDEX>1</SW-AXIS-INDEX>
      <RULE-BASED-VALUES>
        <RULE>RAMP</RULE>
        <ARGUMENTSS>
          <RULE-ARGUMENTS>
            <V>0</V>
            <V>5</V>
          </RULE-ARGUMENTS>
        </ARGUMENTSS>
        <MAX-SIZE-TO-FILL>5</MAX-SIZE-TO-FILL>
      </RULE-BASED-VALUES>
    </RULE-BASED-AXIS-CONT>
  </SW-AXIS-CONTS>
  <SW-VALUE-CONT>
    <SW-ARRAYSIZE>
      <V>5</V>
    </SW-ARRAYSIZE>
    <RULE-BASED-VALUES>
      <RULE>FILL</RULE>
      <ARGUMENTSS>
        <RULE-ARGUMENTS>
          <V>0</V>
        </RULE-ARGUMENTS>
      </ARGUMENTSS>
      <MAX-SIZE-TO-FILL>5</MAX-SIZE-TO-FILL>
    </RULE-BASED-VALUES>
  </SW-VALUE-CONT>
</APPLICATION-RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationRuleBasedValueSpecification)
        self.assertEqual(elem.label, "CurveValue")
        self.assertEqual(elem.category, "CURVE")
        self.assertEqual(len(elem.sw_axis_conts), 1)
        self.assertEqual(elem.sw_axis_conts[0].category, ar_enum.CalibrationAxisCategory.STD_AXIS)
        self.assertIsNotNone(elem.sw_value_cont)
        self.assertEqual(elem.sw_value_cont.rule_based_values.rule, "FILL")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            ar_element.ApplicationRuleBasedValueSpecification(category=123)
        with self.assertRaises(TypeError):
            ar_element.ApplicationRuleBasedValueSpecification(sw_axis_conts=object())
        with self.assertRaises(TypeError):
            ar_element.ApplicationRuleBasedValueSpecification(sw_value_cont=object())


class TestCompositeRuleBasedValueSpecification(unittest.TestCase):

    def test_read_write_empty(self):
        element = ar_element.CompositeRuleBasedValueSpecification()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<COMPOSITE-RULE-BASED-VALUE-SPECIFICATION/>')
        reader = autosar.xml.Reader()
        elem: ar_element.CompositeRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositeRuleBasedValueSpecification)
        self.assertIsNone(elem.label)
        self.assertIsNone(elem.rule)
        self.assertEqual(len(elem.arguments), 0)
        self.assertEqual(len(elem.compound_primitive_arguments), 0)
        self.assertIsNone(elem.max_size_to_fill)

    def test_read_write_arguments(self):
        rec1 = ar_element.RecordValueSpecification(fields=[
            ar_element.NumericalValueSpecification(value=1),
            ar_element.TextValueSpecification(value="A")
        ])
        rec2 = ar_element.RecordValueSpecification(fields=[
            ar_element.NumericalValueSpecification(value=0),
            ar_element.TextValueSpecification(value="Default")
        ])
        element = ar_element.CompositeRuleBasedValueSpecification(
            label="CompositeRuleArray",
            rule="FILL_UNTIL_END",
            arguments=[rec1, rec2],
            max_size_to_fill=20
        )
        writer = autosar.xml.Writer()
        xml = '''<COMPOSITE-RULE-BASED-VALUE-SPECIFICATION>
  <SHORT-LABEL>CompositeRuleArray</SHORT-LABEL>
  <RULE>FILL_UNTIL_END</RULE>
  <ARGUMENTS>
    <RECORD-VALUE-SPECIFICATION>
      <FIELDS>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>1</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
        <TEXT-VALUE-SPECIFICATION>
          <VALUE>A</VALUE>
        </TEXT-VALUE-SPECIFICATION>
      </FIELDS>
    </RECORD-VALUE-SPECIFICATION>
    <RECORD-VALUE-SPECIFICATION>
      <FIELDS>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>0</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
        <TEXT-VALUE-SPECIFICATION>
          <VALUE>Default</VALUE>
        </TEXT-VALUE-SPECIFICATION>
      </FIELDS>
    </RECORD-VALUE-SPECIFICATION>
  </ARGUMENTS>
  <MAX-SIZE-TO-FILL>20</MAX-SIZE-TO-FILL>
</COMPOSITE-RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositeRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositeRuleBasedValueSpecification)
        self.assertEqual(elem.label, "CompositeRuleArray")
        self.assertEqual(elem.rule, "FILL_UNTIL_END")
        self.assertEqual(len(elem.arguments), 2)
        self.assertEqual(elem.max_size_to_fill, 20)

    def test_read_write_compound_primitive_arguments(self):
        app_val = ar_element.ApplicationValueSpecification(category="VALUE")
        element = ar_element.CompositeRuleBasedValueSpecification(
            rule="REPEAT",
            compound_primitive_arguments=[app_val],
            max_size_to_fill=10
        )
        writer = autosar.xml.Writer()
        xml = '''<COMPOSITE-RULE-BASED-VALUE-SPECIFICATION>
  <RULE>REPEAT</RULE>
  <COMPOUND-PRIMITIVE-ARGUMENTS>
    <APPLICATION-VALUE-SPECIFICATION>
      <CATEGORY>VALUE</CATEGORY>
    </APPLICATION-VALUE-SPECIFICATION>
  </COMPOUND-PRIMITIVE-ARGUMENTS>
  <MAX-SIZE-TO-FILL>10</MAX-SIZE-TO-FILL>
</COMPOSITE-RULE-BASED-VALUE-SPECIFICATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositeRuleBasedValueSpecification = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositeRuleBasedValueSpecification)
        self.assertEqual(len(elem.compound_primitive_arguments), 1)
        self.assertEqual(elem.compound_primitive_arguments[0].category, "VALUE")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            ar_element.CompositeRuleBasedValueSpecification(rule=123)
        with self.assertRaises(TypeError):
            ar_element.CompositeRuleBasedValueSpecification(arguments=object())
        with self.assertRaises(TypeError):
            ar_element.CompositeRuleBasedValueSpecification(compound_primitive_arguments=object())
        with self.assertRaises(TypeError):
            ar_element.CompositeRuleBasedValueSpecification(max_size_to_fill="invalid")

    def test_read_invalid_max_size_to_fill(self):
        xml = '''<COMPOSITE-RULE-BASED-VALUE-SPECIFICATION>
  <RULE>FILL</RULE>
  <MAX-SIZE-TO-FILL>-5</MAX-SIZE-TO-FILL>
</COMPOSITE-RULE-BASED-VALUE-SPECIFICATION>'''
        reader = autosar.xml.Reader()
        with self.assertRaises(ar_exception.ParseError):
            reader.read_str_elem(xml)


if __name__ == '__main__':
    unittest.main()
