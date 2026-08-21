"""Unit tests for system template elements"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestEndToEndTransformationComSpecProps(unittest.TestCase):
    """
    This primarily tests the Describable group, which is used by EndToEndTransformationComSpecProps.
    """

    def test_empty(self):
        element = ar_element.EndToEndTransformationComSpecProps()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)

    # Start Describable tests

    def test_desc_from_str(self):
        element = ar_element.EndToEndTransformationComSpecProps(desc="Description")
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <DESC>
    <L-2 L="FOR-ALL">Description</L-2>
  </DESC>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertIsInstance(elem.desc, ar_element.MultiLanguageOverviewParagraph)
        self.assertEqual(elem.desc.elements[0].parts[0], 'Description')
        self.assertEqual(elem.desc.elements[0].language, ar_enum.Language.FOR_ALL)

    def test_desc_from_tuple(self):
        desc = (ar_enum.Language.EN, "Description")
        element = ar_element.EndToEndTransformationComSpecProps(desc=desc)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <DESC>
    <L-2 L="EN">Description</L-2>
  </DESC>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertIsInstance(elem.desc, ar_element.MultiLanguageOverviewParagraph)
        self.assertEqual(elem.desc.elements[0].parts[0], 'Description')
        self.assertEqual(elem.desc.elements[0].language, ar_enum.Language.EN)

    def test_category(self):
        element = ar_element.EndToEndTransformationComSpecProps(category="MyCategory")
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <CATEGORY>MyCategory</CATEGORY>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.category, "MyCategory")

    def test_introduction(self):
        paragraph = ar_element.MultiLanguageParagraph(
            (ar_enum.Language.EN, 'Paragraph Text'))
        introduction = ar_element.DocumentationBlock(paragraph)
        element = ar_element.EndToEndTransformationComSpecProps(introduction=introduction)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <INTRODUCTION>
    <P>
      <L-1 L="EN">Paragraph Text</L-1>
    </P>
  </INTRODUCTION>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertIsInstance(elem.introduction, ar_element.DocumentationBlock)
        self.assertEqual(
            elem.introduction.elements[0].elements[0].parts[0], "Paragraph Text")

    def test_admin_data(self):
        admin_data = ar_element.AdminData(
            doc_revisions=ar_element.DocRevision(revision_label="1.0.0", issued_by="Author1", date="2024-01-01"),
            sdgs=ar_element.SpecialDataGroup("GID1", ("Inner1", "MyContent1")),
        )
        element = ar_element.EndToEndTransformationComSpecProps(admin_data=admin_data)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <ADMIN-DATA>
    <DOC-REVISIONS>
      <DOC-REVISION>
        <REVISION-LABEL>1.0.0</REVISION-LABEL>
        <ISSUED-BY>Author1</ISSUED-BY>
        <DATE>2024-01-01</DATE>
      </DOC-REVISION>
    </DOC-REVISIONS>
    <SDGS>
      <SDG GID="GID1">
        <SD GID="Inner1">MyContent1</SD>
      </SDG>
    </SDGS>
  </ADMIN-DATA>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        admin_data2 = elem.admin_data
        self.assertIsNotNone(admin_data2)
        self.assertEqual(str(admin_data2.doc_revisions[0].revision_label),
                         str(admin_data.doc_revisions[0].revision_label))
        self.assertEqual(admin_data2.doc_revisions[0].issued_by,
                         admin_data.doc_revisions[0].issued_by)
        self.assertEqual(str(admin_data2.doc_revisions[0].date),
                         str(admin_data.doc_revisions[0].date))

    # End Describable tests
    # Start EndToEndTransformationComSpecProps tests

    def test_clear_from_valid_to_invalid(self):
        element = ar_element.EndToEndTransformationComSpecProps(clear_from_valid_to_invalid=False)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <CLEAR-FROM-VALID-TO-INVALID>false</CLEAR-FROM-VALID-TO-INVALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertFalse(elem.clear_from_valid_to_invalid)

    def test_disable_disable_e2e_check(self):
        element = ar_element.EndToEndTransformationComSpecProps(disable_e2e_check=True)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <DISABLE-END-TO-END-CHECK>true</DISABLE-END-TO-END-CHECK>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertTrue(elem.disable_e2e_check)

    def test_disable_e2e_state_machine(self):
        element = ar_element.EndToEndTransformationComSpecProps(disable_e2e_state_machine=False)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <DISABLE-END-TO-END-STATE-MACHINE>false</DISABLE-END-TO-END-STATE-MACHINE>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertFalse(elem.disable_e2e_state_machine)

    def test_e2e_profile_compatibility_props_ref(self):
        ref_str = "/System/Props/E2ECompatibilityProps1"
        ref = ar_element.E2EProfileCompatibilityPropsRef(ref_str)
        element = ar_element.EndToEndTransformationComSpecProps(e2e_profile_compatibility_props_ref=ref)
        writer = autosar.xml.Writer()
        dest = "E-2-E-PROFILE-COMPATIBILITY-PROPS"
        xml = f'''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <E-2-E-PROFILE-COMPATIBILITY-PROPS-REF DEST="{dest}">{ref_str}</E-2-E-PROFILE-COMPATIBILITY-PROPS-REF>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(str(elem.e2e_profile_compatibility_props_ref), ref_str)

    def test_max_delta_counter(self):
        element = ar_element.EndToEndTransformationComSpecProps(max_delta_counter=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MAX-DELTA-COUNTER>1</MAX-DELTA-COUNTER>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.max_delta_counter, 1)

    def test_max_error_state_init(self):
        element = ar_element.EndToEndTransformationComSpecProps(max_error_state_init=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MAX-ERROR-STATE-INIT>1</MAX-ERROR-STATE-INIT>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.max_error_state_init, 1)

    def test_max_error_state_invalid(self):
        element = ar_element.EndToEndTransformationComSpecProps(max_error_state_invalid=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MAX-ERROR-STATE-INVALID>1</MAX-ERROR-STATE-INVALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.max_error_state_invalid, 1)

    def test_max_error_state_valid(self):
        element = ar_element.EndToEndTransformationComSpecProps(max_error_state_valid=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MAX-ERROR-STATE-VALID>1</MAX-ERROR-STATE-VALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.max_error_state_valid, 1)

    def test_max_no_new_or_repeated_data(self):
        element = ar_element.EndToEndTransformationComSpecProps(max_no_new_repeated_data=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MAX-NO-NEW-OR-REPEATED-DATA>1</MAX-NO-NEW-OR-REPEATED-DATA>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.max_no_new_repeated_data, 1)

    def test_min_ok_state_init(self):
        element = ar_element.EndToEndTransformationComSpecProps(min_ok_state_init=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MIN-OK-STATE-INIT>1</MIN-OK-STATE-INIT>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.min_ok_state_init, 1)

    def test_min_ok_state_invalid(self):
        element = ar_element.EndToEndTransformationComSpecProps(min_ok_state_invalid=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MIN-OK-STATE-INVALID>1</MIN-OK-STATE-INVALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.min_ok_state_invalid, 1)

    def test_min_ok_state_valid(self):
        element = ar_element.EndToEndTransformationComSpecProps(min_ok_state_valid=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <MIN-OK-STATE-VALID>1</MIN-OK-STATE-VALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.min_ok_state_valid, 1)

    def test_sync_counter_init(self):
        element = ar_element.EndToEndTransformationComSpecProps(sync_counter_init=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <SYNC-COUNTER-INIT>1</SYNC-COUNTER-INIT>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.sync_counter_init, 1)

    def test_window_size(self):
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <WINDOW-SIZE>1</WINDOW-SIZE>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)

    def test_window_size_init(self):
        element = ar_element.EndToEndTransformationComSpecProps(window_size_init=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <WINDOW-SIZE-INIT>1</WINDOW-SIZE-INIT>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.window_size_init, 1)

    def test_window_size_invalid(self):
        element = ar_element.EndToEndTransformationComSpecProps(window_size_invalid=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <WINDOW-SIZE-INVALID>1</WINDOW-SIZE-INVALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.window_size_invalid, 1)

    def test_window_size_valid(self):
        element = ar_element.EndToEndTransformationComSpecProps(window_size_valid=1)
        writer = autosar.xml.Writer()
        xml = '''<END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  <WINDOW-SIZE-VALID>1</WINDOW-SIZE-VALID>
</END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.EndToEndTransformationComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.EndToEndTransformationComSpecProps)
        self.assertEqual(elem.window_size_valid, 1)

    # End EndToEndTransformationComSpecProps tests


class TestE2EProfileCompatibilityProps(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.E2EProfileCompatibilityProps("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<E-2-E-PROFILE-COMPATIBILITY-PROPS>
  <SHORT-NAME>ShortName</SHORT-NAME>
</E-2-E-PROFILE-COMPATIBILITY-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.E2EProfileCompatibilityProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.E2EProfileCompatibilityProps)
        self.assertEqual(elem.name, "ShortName")

    def test_transit_to_invalid_extended(self):
        element = ar_element.E2EProfileCompatibilityProps("ShortName",
                                                          transit_to_invalid_extended=True)
        writer = autosar.xml.Writer()
        xml = '''<E-2-E-PROFILE-COMPATIBILITY-PROPS>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <TRANSIT-TO-INVALID-EXTENDED>true</TRANSIT-TO-INVALID-EXTENDED>
</E-2-E-PROFILE-COMPATIBILITY-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.E2EProfileCompatibilityProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.E2EProfileCompatibilityProps)
        self.assertEqual(elem.name, "ShortName")
        self.assertTrue(elem.transit_to_invalid_extended)


if __name__ == '__main__':
    unittest.main()
