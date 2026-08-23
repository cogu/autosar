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


class TestCryptoKeyManagementNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.CryptoKeyManagementNeeds("CryptoKeyManagementNeeds")
        writer = autosar.xml.Writer()
        xml = '''<CRYPTO-KEY-MANAGEMENT-NEEDS>
  <SHORT-NAME>CryptoKeyManagementNeeds</SHORT-NAME>
</CRYPTO-KEY-MANAGEMENT-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CryptoKeyManagementNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CryptoKeyManagementNeeds)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "CryptoKeyManagementNeeds")


class TestCryptoServiceJobNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.CryptoServiceJobNeeds("CryptoServiceJobNeeds")
        writer = autosar.xml.Writer()
        xml = '''<CRYPTO-SERVICE-JOB-NEEDS>
  <SHORT-NAME>CryptoServiceJobNeeds</SHORT-NAME>
</CRYPTO-SERVICE-JOB-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CryptoServiceJobNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CryptoServiceJobNeeds)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "CryptoServiceJobNeeds")


class TestCryptoServiceNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.CryptoServiceNeeds("CryptoServiceNeeds")
        writer = autosar.xml.Writer()
        xml = '''<CRYPTO-SERVICE-NEEDS>
  <SHORT-NAME>CryptoServiceNeeds</SHORT-NAME>
</CRYPTO-SERVICE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CryptoServiceNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CryptoServiceNeeds)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "CryptoServiceNeeds")
        self.assertIsNone(elem.algorithm_family)
        self.assertIsNone(elem.algorithm_mode)
        self.assertIsNone(elem.crypto_key_description)
        self.assertIsNone(elem.maximum_key_length)

    def test_with_all_fields(self):
        element = ar_element.CryptoServiceNeeds(
            "CryptoServiceNeeds",
            algorithm_family="AES",
            algorithm_mode="CBC",
            crypto_key_description="Key for AES-128",
            maximum_key_length=128
        )
        writer = autosar.xml.Writer()
        xml = '''<CRYPTO-SERVICE-NEEDS>
  <SHORT-NAME>CryptoServiceNeeds</SHORT-NAME>
  <ALGORITHM-FAMILY>AES</ALGORITHM-FAMILY>
  <ALGORITHM-MODE>CBC</ALGORITHM-MODE>
  <CRYPTO-KEY-DESCRIPTION>Key for AES-128</CRYPTO-KEY-DESCRIPTION>
  <MAXIMUM-KEY-LENGTH>128</MAXIMUM-KEY-LENGTH>
</CRYPTO-SERVICE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CryptoServiceNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CryptoServiceNeeds)
        self.assertEqual(elem.algorithm_family, "AES")
        self.assertEqual(elem.algorithm_mode, "CBC")
        self.assertEqual(elem.crypto_key_description, "Key for AES-128")
        self.assertEqual(elem.maximum_key_length, 128)

    def test_invalid_positive_int(self):
        with self.assertRaises(ValueError):
            ar_element.CryptoServiceNeeds(
                "CryptoServiceNeeds",
                maximum_key_length=-1
            )


if __name__ == '__main__':
    unittest.main()
