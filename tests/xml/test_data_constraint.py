"""Unit tests for dataconstraint elements."""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402

class TestScaleConstraint(unittest.TestCase): # noqa D101

    def test_write_read_empty(self): # noqa D102
        element = ar_element.ScaleConstraint()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<SCALE-CONSTR/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ScaleConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ScaleConstraint)

    def test_write_read_label(self): # noqa D102
        element = ar_element.ScaleConstraint(label="MyLabel")
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<SCALE-CONSTR>
  <SHORT-LABEL>MyLabel</SHORT-LABEL>
</SCALE-CONSTR>''')
        reader = autosar.xml.Reader()
        elem: ar_element.ScaleConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ScaleConstraint)
        self.assertEqual(elem.label, "MyLabel")

    def test_write_read_desc(self): # noqa D102
        description = ar_element.MultiLanguageOverviewParagraph((ar_enum.Language.FOR_ALL, 'Description'))
        element = ar_element.ScaleConstraint(desc=description)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<SCALE-CONSTR>
  <DESC>
    <L-2 L="FOR-ALL">Description</L-2>
  </DESC>
</SCALE-CONSTR>''')
        reader = autosar.xml.Reader()
        elem: ar_element.ScaleConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ScaleConstraint)
        desc = elem.desc
        self.assertEqual(desc.elements[0].language, ar_enum.Language.FOR_ALL)
        self.assertEqual(desc.elements[0].parts[0], "Description")

    def test_write_read_limit_with_default_interval_type(self): # noqa D102
        element = ar_element.ScaleConstraint(lower_limit=0, upper_limit=255)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<SCALE-CONSTR>
  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">255</UPPER-LIMIT>
</SCALE-CONSTR>''')
        reader = autosar.xml.Reader()
        elem: ar_element.ScaleConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ScaleConstraint)
        self.assertEqual(elem.lower_limit, 0)
        self.assertEqual(elem.upper_limit, 255)
        self.assertEqual(elem.lower_limit_type, ar_enum.IntervalType.CLOSED)
        self.assertEqual(elem.upper_limit_type, ar_enum.IntervalType.CLOSED)

class TestInternalConstraint(unittest.TestCase): # noqa D101

    def test_write_read_empty(self): # noqa D102
        element = ar_element.InternalConstraint()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<INTERNAL-CONSTRS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.InternalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InternalConstraint)

    def test_write_read_limits(self): # noqa D102
        element = ar_element.InternalConstraint(lower_limit=0, upper_limit=7)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<INTERNAL-CONSTRS>
  <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
  <UPPER-LIMIT INTERVAL-TYPE="CLOSED">7</UPPER-LIMIT>
</INTERNAL-CONSTRS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.InternalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InternalConstraint)
        self.assertEqual(elem.lower_limit, 0)
        self.assertEqual(elem.upper_limit, 7)
        self.assertEqual(elem.lower_limit_type, ar_enum.IntervalType.CLOSED)
        self.assertEqual(elem.upper_limit_type, ar_enum.IntervalType.CLOSED)

    def test_write_read_scale_constrs(self): # noqa D102
        scale_constrs = []
        scale_constrs.append(ar_element.ScaleConstraint(lower_limit=0, upper_limit=99))
        scale_constrs.append(ar_element.ScaleConstraint(lower_limit=0, upper_limit=199))
        element = ar_element.InternalConstraint(scale_constr=scale_constrs)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<INTERNAL-CONSTRS>
  <SCALE-CONSTRS>
    <SCALE-CONSTR>
      <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
      <UPPER-LIMIT INTERVAL-TYPE="CLOSED">99</UPPER-LIMIT>
    </SCALE-CONSTR>
    <SCALE-CONSTR>
      <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
      <UPPER-LIMIT INTERVAL-TYPE="CLOSED">199</UPPER-LIMIT>
    </SCALE-CONSTR>
  </SCALE-CONSTRS>
</INTERNAL-CONSTRS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.InternalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InternalConstraint)
        constrs = elem.scale_constrs
        self.assertEqual(constrs[0].lower_limit, 0)
        self.assertEqual(constrs[0].upper_limit, 99)
        self.assertEqual(constrs[1].lower_limit, 0)
        self.assertEqual(constrs[1].upper_limit, 199)

    def test_write_read_max_gradient(self): # noqa D102
        element = ar_element.InternalConstraint(max_gradient=1.2)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<INTERNAL-CONSTRS>
  <MAX-GRADIENT>1.2</MAX-GRADIENT>
</INTERNAL-CONSTRS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.InternalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InternalConstraint)
        self.assertEqual(elem.max_gradient, 1.2)

    def test_write_read_max_diff(self): # noqa D102
        element = ar_element.InternalConstraint(max_diff=14)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<INTERNAL-CONSTRS>
  <MAX-DIFF>14</MAX-DIFF>
</INTERNAL-CONSTRS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.InternalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InternalConstraint)
        self.assertEqual(elem.max_diff, 14)

    def test_write_monotonoy(self): # noqa D102
        element = ar_element.InternalConstraint(monotony=ar_enum.Monotony.STRICTLY_DECREASING)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<INTERNAL-CONSTRS>
  <MONOTONY>STRICTLY-DECREASING</MONOTONY>
</INTERNAL-CONSTRS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.InternalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InternalConstraint)
        self.assertEqual(elem.monotony, ar_enum.Monotony.STRICTLY_DECREASING)

class TestPhysicalConstraint(unittest.TestCase): # noqa D101

    def test_write_read_empty(self): # noqa D102
        element = ar_element.PhysicalConstraint()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<PHYS-CONSTRS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.PhysicalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PhysicalConstraint)

    # PhysicalConstraint shares implementantion with InternalConstraint
    # and there's no need to test all common elements again.
    # We just test the unique parts of PhysicalConstraint

    def test_write_read_unit_ref(self): # noqa D102
        element = ar_element.PhysicalConstraint(unit_ref=ar_element.UnitRef("/Units/KmPerHour"))
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<PHYS-CONSTRS>
  <UNIT-REF DEST="UNIT">/Units/KmPerHour</UNIT-REF>
</PHYS-CONSTRS>''')
        reader = autosar.xml.Reader()
        elem: ar_element.PhysicalConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PhysicalConstraint)
        self.assertEqual(str(elem.unit_ref), "/Units/KmPerHour")

class TestDataConstraintRule(unittest.TestCase): # noqa D101

    def test_write_read_empty(self): # noqa D102
        element = ar_element.DataConstraintRule()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<DATA-CONSTR-RULE/>')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraintRule = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraintRule)

    def test_write_read_constr_level(self): # noqa D102
        element = ar_element.DataConstraintRule(level=-1)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<DATA-CONSTR-RULE>
  <CONSTR-LEVEL>-1</CONSTR-LEVEL>
</DATA-CONSTR-RULE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraintRule = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraintRule)

    def test_write_read_physical_constraing(self): # noqa D102
        constr = ar_element.PhysicalConstraint(lower_limit=0, upper_limit=15)
        element = ar_element.DataConstraintRule(physical=constr)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<DATA-CONSTR-RULE>
  <PHYS-CONSTRS>
    <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
    <UPPER-LIMIT INTERVAL-TYPE="CLOSED">15</UPPER-LIMIT>
  </PHYS-CONSTRS>
</DATA-CONSTR-RULE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraintRule = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraintRule)

    def test_write_read_internal_constraint(self): # noqa D102
        constr = ar_element.InternalConstraint(lower_limit=0, upper_limit=15)
        element = ar_element.DataConstraintRule(internal=constr)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<DATA-CONSTR-RULE>
  <INTERNAL-CONSTRS>
    <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
    <UPPER-LIMIT INTERVAL-TYPE="CLOSED">15</UPPER-LIMIT>
  </INTERNAL-CONSTRS>
</DATA-CONSTR-RULE>''')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraintRule = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraintRule)

class TestDataConstraint(unittest.TestCase): # noqa D101

    def test_write_read_name_only(self): # noqa D102
        element = ar_element.DataConstraint("Test_Constr")
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<DATA-CONSTR>
  <SHORT-NAME>Test_Constr</SHORT-NAME>
</DATA-CONSTR>''')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraint)
        self.assertEqual(elem.name, "Test_Constr")

    def test_write_read_physical(self): # noqa D102
        element = ar_element.DataConstraint.make_physical("Test_Constr", 0, 1)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<DATA-CONSTR>
  <SHORT-NAME>Test_Constr</SHORT-NAME>
  <DATA-CONSTR-RULES>
    <DATA-CONSTR-RULE>
      <PHYS-CONSTRS>
        <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
        <UPPER-LIMIT INTERVAL-TYPE="CLOSED">1</UPPER-LIMIT>
      </PHYS-CONSTRS>
    </DATA-CONSTR-RULE>
  </DATA-CONSTR-RULES>
</DATA-CONSTR>''')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraint)
        self.assertEqual(elem.name, "Test_Constr")
        rule: ar_element.DataConstraintRule = elem.rules[0]
        self.assertEqual(rule.physical.lower_limit, 0)
        self.assertEqual(rule.physical.upper_limit, 1)

    def test_write_read_internal(self): # noqa D102
        element = ar_element.DataConstraint.make_internal("Test_Constr", 0, 10)
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '''<DATA-CONSTR>
  <SHORT-NAME>Test_Constr</SHORT-NAME>
  <DATA-CONSTR-RULES>
    <DATA-CONSTR-RULE>
      <INTERNAL-CONSTRS>
        <LOWER-LIMIT INTERVAL-TYPE="CLOSED">0</LOWER-LIMIT>
        <UPPER-LIMIT INTERVAL-TYPE="CLOSED">10</UPPER-LIMIT>
      </INTERNAL-CONSTRS>
    </DATA-CONSTR-RULE>
  </DATA-CONSTR-RULES>
</DATA-CONSTR>''')
        reader = autosar.xml.Reader()
        elem: ar_element.DataConstraint = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DataConstraint)
        self.assertEqual(elem.name, "Test_Constr")
        rule: ar_element.DataConstraintRule = elem.rules[0]
        self.assertEqual(rule.internal.lower_limit, 0)
        self.assertEqual(rule.internal.upper_limit, 10)


if __name__ == '__main__':
    unittest.main()
