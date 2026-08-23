"""Unit tests for service needs elements."""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element  # noqa: E402
import autosar  # noqa: E402


class TestBswMgrNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.BswMgrNeeds("BswMgrNeeds")
        writer = autosar.xml.Writer()
        xml = '''<BSW-MGR-NEEDS>
  <SHORT-NAME>BswMgrNeeds</SHORT-NAME>
</BSW-MGR-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.BswMgrNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.BswMgrNeeds)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "BswMgrNeeds")

    def test_with_admin_data(self):
        admin_data = ar_element.AdminData(
            doc_revisions=ar_element.DocRevision(revision_label="1.0.0")
        )
        element = ar_element.BswMgrNeeds("BswMgrNeeds", admin_data=admin_data)
        writer = autosar.xml.Writer()
        xml = '''<BSW-MGR-NEEDS>
  <SHORT-NAME>BswMgrNeeds</SHORT-NAME>
  <ADMIN-DATA>
    <DOC-REVISIONS>
      <DOC-REVISION>
        <REVISION-LABEL>1.0.0</REVISION-LABEL>
      </DOC-REVISION>
    </DOC-REVISIONS>
  </ADMIN-DATA>
</BSW-MGR-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.BswMgrNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.BswMgrNeeds)
        self.assertEqual(str(elem.admin_data.doc_revisions[0].revision_label), "1.0.0")

    def test_with_desc_and_category(self):
        element = ar_element.BswMgrNeeds(
            "BswMgrNeeds",
            desc="Needs for BswM",
            category="SERVICE_NEEDS"
        )
        writer = autosar.xml.Writer()
        xml = '''<BSW-MGR-NEEDS>
  <SHORT-NAME>BswMgrNeeds</SHORT-NAME>
  <DESC>
    <L-2 L="FOR-ALL">Needs for BswM</L-2>
  </DESC>
  <CATEGORY>SERVICE_NEEDS</CATEGORY>
</BSW-MGR-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.BswMgrNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.BswMgrNeeds)
        self.assertEqual(elem.desc.elements[0].parts[0], "Needs for BswM")
        self.assertEqual(elem.category, "SERVICE_NEEDS")


class TestComMgrUserNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ComMgrUserNeeds("ComMgrUserNeeds")
        writer = autosar.xml.Writer()
        xml = '''<COM-MGR-USER-NEEDS>
  <SHORT-NAME>ComMgrUserNeeds</SHORT-NAME>
</COM-MGR-USER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ComMgrUserNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ComMgrUserNeeds)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "ComMgrUserNeeds")
        self.assertIsNone(elem.max_comm_mode)

    def test_with_max_comm_mode(self):
        element = ar_element.ComMgrUserNeeds(
            "ComMgrUserNeeds",
            max_comm_mode=autosar.xml.enumeration.MaxCommMode.FULL
        )
        writer = autosar.xml.Writer()
        xml = '''<COM-MGR-USER-NEEDS>
  <SHORT-NAME>ComMgrUserNeeds</SHORT-NAME>
  <MAX-COMM-MODE>FULL</MAX-COMM-MODE>
</COM-MGR-USER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ComMgrUserNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ComMgrUserNeeds)
        self.assertEqual(elem.max_comm_mode, autosar.xml.enumeration.MaxCommMode.FULL)

    def test_with_max_comm_mode_str(self):
        element = ar_element.ComMgrUserNeeds(
            "ComMgrUserNeeds",
            max_comm_mode="SILENT"
        )
        writer = autosar.xml.Writer()
        xml = '''<COM-MGR-USER-NEEDS>
  <SHORT-NAME>ComMgrUserNeeds</SHORT-NAME>
  <MAX-COMM-MODE>SILENT</MAX-COMM-MODE>
</COM-MGR-USER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ComMgrUserNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ComMgrUserNeeds)
        self.assertEqual(elem.max_comm_mode, autosar.xml.enumeration.MaxCommMode.SILENT)

    def test_with_invalid_max_comm_mode(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.ComMgrUserNeeds(
                "ComMgrUserNeeds",
                max_comm_mode="VERBOSE"
            )

    def test_with_invalid_max_comm_mode_type(self):
        with self.assertRaises(autosar.xml.exception.AssignmentTypeError):
            ar_element.ComMgrUserNeeds(
                "ComMgrUserNeeds",
                max_comm_mode=123
            )


if __name__ == '__main__':
    unittest.main()
