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


class TestDiagnosticCommunicationManagerNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticCommunicationManagerNeeds("DiagnosticCommunicationManagerNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS>
  <SHORT-NAME>DiagnosticCommunicationManagerNeeds</SHORT-NAME>
</DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticCommunicationManagerNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticCommunicationManagerNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "DiagnosticCommunicationManagerNeeds")
        self.assertEqual(elem.audience, [])
        self.assertIsNone(elem.diag_requirement)
        self.assertIsNone(elem.security_access_level)
        self.assertIsNone(elem.service_request_callback_type)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticCommunicationManagerNeeds(
            "DiagnosticCommunicationManagerNeeds",
            audience=[autosar.xml.enumeration.DiagnosticAudience.DEVELOPMENT,
                      autosar.xml.enumeration.DiagnosticAudience.MANUFACTURING],
            diag_requirement="REQ-1234",
            security_access_level=1,
            service_request_callback_type=(
                autosar.xml.enumeration.DiagnosticServiceRequestCallbackType.REQUEST_CALLBACK_TYPE_MANUFACTURER
            )
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS>
  <SHORT-NAME>DiagnosticCommunicationManagerNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>DEVELOPMENT</AUDIENCE>
    <AUDIENCE>MANUFACTURING</AUDIENCE>
  </AUDIENCES>
  <DIAG-REQUIREMENT>REQ-1234</DIAG-REQUIREMENT>
  <SECURITY-ACCESS-LEVEL>1</SECURITY-ACCESS-LEVEL>
  <SERVICE-REQUEST-CALLBACK-TYPE>REQUEST-CALLBACK-TYPE-MANUFACTURER</SERVICE-REQUEST-CALLBACK-TYPE>
</DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticCommunicationManagerNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticCommunicationManagerNeeds)
        self.assertEqual(elem.audience, [
            autosar.xml.enumeration.DiagnosticAudience.DEVELOPMENT,
            autosar.xml.enumeration.DiagnosticAudience.MANUFACTURING
        ])
        self.assertEqual(elem.diag_requirement, "REQ-1234")
        self.assertEqual(elem.security_access_level, 1)
        self.assertEqual(
            elem.service_request_callback_type,
            autosar.xml.enumeration.DiagnosticServiceRequestCallbackType.REQUEST_CALLBACK_TYPE_MANUFACTURER
        )

    def test_with_string_enums(self):
        element = ar_element.DiagnosticCommunicationManagerNeeds(
            "DiagnosticCommunicationManagerNeeds",
            audience="AFTERMARKET",
            service_request_callback_type="REQUEST-CALLBACK-TYPE-SUPPLIER"
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS>
  <SHORT-NAME>DiagnosticCommunicationManagerNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>AFTERMARKET</AUDIENCE>
  </AUDIENCES>
  <SERVICE-REQUEST-CALLBACK-TYPE>REQUEST-CALLBACK-TYPE-SUPPLIER</SERVICE-REQUEST-CALLBACK-TYPE>
</DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticCommunicationManagerNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticCommunicationManagerNeeds)
        self.assertEqual(elem.audience, [autosar.xml.enumeration.DiagnosticAudience.AFTERMARKET])
        self.assertEqual(
            elem.service_request_callback_type,
            autosar.xml.enumeration.DiagnosticServiceRequestCallbackType.REQUEST_CALLBACK_TYPE_SUPPLIER
        )

    def test_invalid_audience(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticCommunicationManagerNeeds(
                "DiagnosticCommunicationManagerNeeds",
                audience="INVALID_AUDIENCE"
            )

    def test_invalid_service_request_callback_type(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticCommunicationManagerNeeds(
                "DiagnosticCommunicationManagerNeeds",
                service_request_callback_type="INVALID_TYPE"
            )


class TestDiagnosticComponentNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticComponentNeeds("DiagnosticComponentNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-COMPONENT-NEEDS>
  <SHORT-NAME>DiagnosticComponentNeeds</SHORT-NAME>
</DIAGNOSTIC-COMPONENT-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticComponentNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticComponentNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "DiagnosticComponentNeeds")

    def test_with_fields(self):
        element = ar_element.DiagnosticComponentNeeds(
            "DiagnosticComponentNeeds",
            audience=autosar.xml.enumeration.DiagnosticAudience.DEVELOPMENT,
            diag_requirement="REQ-COMP-01",
            security_access_level=2
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-COMPONENT-NEEDS>
  <SHORT-NAME>DiagnosticComponentNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>DEVELOPMENT</AUDIENCE>
  </AUDIENCES>
  <DIAG-REQUIREMENT>REQ-COMP-01</DIAG-REQUIREMENT>
  <SECURITY-ACCESS-LEVEL>2</SECURITY-ACCESS-LEVEL>
</DIAGNOSTIC-COMPONENT-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticComponentNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticComponentNeeds)
        self.assertEqual(elem.audience, [autosar.xml.enumeration.DiagnosticAudience.DEVELOPMENT])
        self.assertEqual(elem.diag_requirement, "REQ-COMP-01")
        self.assertEqual(elem.security_access_level, 2)


class TestDiagnosticControlNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticControlNeeds("DiagnosticControlNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-CONTROL-NEEDS>
  <SHORT-NAME>DiagnosticControlNeeds</SHORT-NAME>
</DIAGNOSTIC-CONTROL-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticControlNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticControlNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "DiagnosticControlNeeds")

    def test_with_fields(self):
        element = ar_element.DiagnosticControlNeeds(
            "DiagnosticControlNeeds",
            audience=[autosar.xml.enumeration.DiagnosticAudience.AFTERMARKET,
                      autosar.xml.enumeration.DiagnosticAudience.SUPPLIER],
            diag_requirement="REQ-CTRL-02",
            security_access_level=3
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-CONTROL-NEEDS>
  <SHORT-NAME>DiagnosticControlNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>AFTERMARKET</AUDIENCE>
    <AUDIENCE>SUPPLIER</AUDIENCE>
  </AUDIENCES>
  <DIAG-REQUIREMENT>REQ-CTRL-02</DIAG-REQUIREMENT>
  <SECURITY-ACCESS-LEVEL>3</SECURITY-ACCESS-LEVEL>
</DIAGNOSTIC-CONTROL-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticControlNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticControlNeeds)
        self.assertEqual(elem.audience, [
            autosar.xml.enumeration.DiagnosticAudience.AFTERMARKET,
            autosar.xml.enumeration.DiagnosticAudience.SUPPLIER
        ])
        self.assertEqual(elem.diag_requirement, "REQ-CTRL-02")
        self.assertEqual(elem.security_access_level, 3)


class TestDiagnosticEnableConditionNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticEnableConditionNeeds("DiagnosticEnableConditionNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-ENABLE-CONDITION-NEEDS>
  <SHORT-NAME>DiagnosticEnableConditionNeeds</SHORT-NAME>
</DIAGNOSTIC-ENABLE-CONDITION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEnableConditionNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEnableConditionNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "DiagnosticEnableConditionNeeds")
        self.assertIsNone(elem.initial_status)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticEnableConditionNeeds(
            "DiagnosticEnableConditionNeeds",
            audience=autosar.xml.enumeration.DiagnosticAudience.MANUFACTURING,
            diag_requirement="REQ-ENABLE-01",
            security_access_level=1,
            initial_status=autosar.xml.enumeration.EventAcceptanceStatus.EVENT_ACCEPTANCE_ENABLED
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-ENABLE-CONDITION-NEEDS>
  <SHORT-NAME>DiagnosticEnableConditionNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>MANUFACTURING</AUDIENCE>
  </AUDIENCES>
  <DIAG-REQUIREMENT>REQ-ENABLE-01</DIAG-REQUIREMENT>
  <SECURITY-ACCESS-LEVEL>1</SECURITY-ACCESS-LEVEL>
  <INITIAL-STATUS>EVENT-ACCEPTANCE-ENABLED</INITIAL-STATUS>
</DIAGNOSTIC-ENABLE-CONDITION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEnableConditionNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEnableConditionNeeds)
        self.assertEqual(elem.audience, [autosar.xml.enumeration.DiagnosticAudience.MANUFACTURING])
        self.assertEqual(elem.diag_requirement, "REQ-ENABLE-01")
        self.assertEqual(elem.security_access_level, 1)
        self.assertEqual(
            elem.initial_status,
            autosar.xml.enumeration.EventAcceptanceStatus.EVENT_ACCEPTANCE_ENABLED
        )

    def test_with_string_enums(self):
        element = ar_element.DiagnosticEnableConditionNeeds(
            "DiagnosticEnableConditionNeeds",
            initial_status="EVENT-ACCEPTANCE-DISABLED"
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-ENABLE-CONDITION-NEEDS>
  <SHORT-NAME>DiagnosticEnableConditionNeeds</SHORT-NAME>
  <INITIAL-STATUS>EVENT-ACCEPTANCE-DISABLED</INITIAL-STATUS>
</DIAGNOSTIC-ENABLE-CONDITION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEnableConditionNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEnableConditionNeeds)
        self.assertEqual(
            elem.initial_status,
            autosar.xml.enumeration.EventAcceptanceStatus.EVENT_ACCEPTANCE_DISABLED
        )

    def test_invalid_initial_status(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticEnableConditionNeeds(
                "DiagnosticEnableConditionNeeds",
                initial_status="INVALID_STATUS"
            )


class TestDiagnosticEventInfoNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticEventInfoNeeds("DiagnosticEventInfoNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-EVENT-INFO-NEEDS>
  <SHORT-NAME>DiagnosticEventInfoNeeds</SHORT-NAME>
</DIAGNOSTIC-EVENT-INFO-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEventInfoNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEventInfoNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticEventInfoNeeds")
        self.assertIsNone(elem.obd_dtc_number)
        self.assertIsNone(elem.uds_dtc_number)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticEventInfoNeeds(
            "DiagnosticEventInfoNeeds",
            audience=autosar.xml.enumeration.DiagnosticAudience.DEVELOPMENT,
            diag_requirement="REQ-EV-01",
            security_access_level=1,
            obd_dtc_number=1234,
            uds_dtc_number=5678
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-EVENT-INFO-NEEDS>
  <SHORT-NAME>DiagnosticEventInfoNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>DEVELOPMENT</AUDIENCE>
  </AUDIENCES>
  <DIAG-REQUIREMENT>REQ-EV-01</DIAG-REQUIREMENT>
  <SECURITY-ACCESS-LEVEL>1</SECURITY-ACCESS-LEVEL>
  <OBD-DTC-NUMBER>1234</OBD-DTC-NUMBER>
  <UDS-DTC-NUMBER>5678</UDS-DTC-NUMBER>
</DIAGNOSTIC-EVENT-INFO-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEventInfoNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEventInfoNeeds)
        self.assertEqual(elem.obd_dtc_number, 1234)
        self.assertEqual(elem.uds_dtc_number, 5678)


class TestDiagnosticEventManagerNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticEventManagerNeeds("DiagnosticEventManagerNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-EVENT-MANAGER-NEEDS>
  <SHORT-NAME>DiagnosticEventManagerNeeds</SHORT-NAME>
</DIAGNOSTIC-EVENT-MANAGER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEventManagerNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEventManagerNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticEventManagerNeeds")

    def test_with_fields(self):
        element = ar_element.DiagnosticEventManagerNeeds(
            "DiagnosticEventManagerNeeds",
            audience=autosar.xml.enumeration.DiagnosticAudience.SUPPLIER,
            diag_requirement="REQ-EVM-01",
            security_access_level=2
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-EVENT-MANAGER-NEEDS>
  <SHORT-NAME>DiagnosticEventManagerNeeds</SHORT-NAME>
  <AUDIENCES>
    <AUDIENCE>SUPPLIER</AUDIENCE>
  </AUDIENCES>
  <DIAG-REQUIREMENT>REQ-EVM-01</DIAG-REQUIREMENT>
  <SECURITY-ACCESS-LEVEL>2</SECURITY-ACCESS-LEVEL>
</DIAGNOSTIC-EVENT-MANAGER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticEventManagerNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticEventManagerNeeds)
        self.assertEqual(elem.audience, [autosar.xml.enumeration.DiagnosticAudience.SUPPLIER])
        self.assertEqual(elem.diag_requirement, "REQ-EVM-01")
        self.assertEqual(elem.security_access_level, 2)


class TestDiagnosticIoControlNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticIoControlNeeds("DiagnosticIoControlNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-IO-CONTROL-NEEDS>
  <SHORT-NAME>DiagnosticIoControlNeeds</SHORT-NAME>
</DIAGNOSTIC-IO-CONTROL-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticIoControlNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticIoControlNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticIoControlNeeds")
        self.assertIsNone(elem.current_value_ref)
        self.assertIsNone(elem.freeze_current_state_supported)
        self.assertIsNone(elem.reset_to_default_supported)
        self.assertIsNone(elem.short_term_adjustment_supported)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticIoControlNeeds(
            "DiagnosticIoControlNeeds",
            current_value_ref="/PortInterfaces/DiagnosticValueNeeds1",
            freeze_current_state_supported=True,
            reset_to_default_supported=False,
            short_term_adjustment_supported=True
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-IO-CONTROL-NEEDS>
  <SHORT-NAME>DiagnosticIoControlNeeds</SHORT-NAME>
  <CURRENT-VALUE-REF DEST="DIAGNOSTIC-VALUE-NEEDS">/PortInterfaces/DiagnosticValueNeeds1</CURRENT-VALUE-REF>
  <FREEZE-CURRENT-STATE-SUPPORTED>true</FREEZE-CURRENT-STATE-SUPPORTED>
  <RESET-TO-DEFAULT-SUPPORTED>false</RESET-TO-DEFAULT-SUPPORTED>
  <SHORT-TERM-ADJUSTMENT-SUPPORTED>true</SHORT-TERM-ADJUSTMENT-SUPPORTED>
</DIAGNOSTIC-IO-CONTROL-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticIoControlNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticIoControlNeeds)
        self.assertIsInstance(elem.current_value_ref, ar_element.DiagnosticValueNeedsRef)
        self.assertEqual(elem.current_value_ref.value, "/PortInterfaces/DiagnosticValueNeeds1")
        self.assertTrue(elem.freeze_current_state_supported)
        self.assertFalse(elem.reset_to_default_supported)
        self.assertTrue(elem.short_term_adjustment_supported)


class TestDiagnosticOperationCycleNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticOperationCycleNeeds("DiagnosticOperationCycleNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-OPERATION-CYCLE-NEEDS>
  <SHORT-NAME>DiagnosticOperationCycleNeeds</SHORT-NAME>
</DIAGNOSTIC-OPERATION-CYCLE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticOperationCycleNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticOperationCycleNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticOperationCycleNeeds")
        self.assertIsNone(elem.operation_cycle)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticOperationCycleNeeds(
            "DiagnosticOperationCycleNeeds",
            operation_cycle=autosar.xml.enumeration.OperationCycleType.IGNITION
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-OPERATION-CYCLE-NEEDS>
  <SHORT-NAME>DiagnosticOperationCycleNeeds</SHORT-NAME>
  <OPERATION-CYCLE>IGNITION</OPERATION-CYCLE>
</DIAGNOSTIC-OPERATION-CYCLE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticOperationCycleNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticOperationCycleNeeds)
        self.assertEqual(
            elem.operation_cycle,
            autosar.xml.enumeration.OperationCycleType.IGNITION
        )

    def test_with_string_enums(self):
        element = ar_element.DiagnosticOperationCycleNeeds(
            "DiagnosticOperationCycleNeeds",
            operation_cycle="WARMUP"
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-OPERATION-CYCLE-NEEDS>
  <SHORT-NAME>DiagnosticOperationCycleNeeds</SHORT-NAME>
  <OPERATION-CYCLE>WARMUP</OPERATION-CYCLE>
</DIAGNOSTIC-OPERATION-CYCLE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticOperationCycleNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticOperationCycleNeeds)
        self.assertEqual(
            elem.operation_cycle,
            autosar.xml.enumeration.OperationCycleType.WARMUP
        )

    def test_invalid_operation_cycle(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticOperationCycleNeeds(
                "DiagnosticOperationCycleNeeds",
                operation_cycle="INVALID_CYCLE"
            )


class TestDiagnosticRequestFileTransferNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticRequestFileTransferNeeds("DiagnosticRequestFileTransferNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS>
  <SHORT-NAME>DiagnosticRequestFileTransferNeeds</SHORT-NAME>
</DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticRequestFileTransferNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticRequestFileTransferNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticRequestFileTransferNeeds")


class TestDiagnosticRoutineNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticRoutineNeeds("DiagnosticRoutineNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-ROUTINE-NEEDS>
  <SHORT-NAME>DiagnosticRoutineNeeds</SHORT-NAME>
</DIAGNOSTIC-ROUTINE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticRoutineNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticRoutineNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticRoutineNeeds")
        self.assertIsNone(elem.diag_routine_type)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticRoutineNeeds(
            "DiagnosticRoutineNeeds",
            diag_routine_type=autosar.xml.enumeration.DiagnosticRoutineType.ASYNCHRONOUS
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-ROUTINE-NEEDS>
  <SHORT-NAME>DiagnosticRoutineNeeds</SHORT-NAME>
  <DIAG-ROUTINE-TYPE>ASYNCHRONOUS</DIAG-ROUTINE-TYPE>
</DIAGNOSTIC-ROUTINE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticRoutineNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticRoutineNeeds)
        self.assertEqual(
            elem.diag_routine_type,
            autosar.xml.enumeration.DiagnosticRoutineType.ASYNCHRONOUS
        )

    def test_with_string_enums(self):
        element = ar_element.DiagnosticRoutineNeeds(
            "DiagnosticRoutineNeeds",
            diag_routine_type="SYNCHRONOUS"
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-ROUTINE-NEEDS>
  <SHORT-NAME>DiagnosticRoutineNeeds</SHORT-NAME>
  <DIAG-ROUTINE-TYPE>SYNCHRONOUS</DIAG-ROUTINE-TYPE>
</DIAGNOSTIC-ROUTINE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticRoutineNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticRoutineNeeds)
        self.assertEqual(
            elem.diag_routine_type,
            autosar.xml.enumeration.DiagnosticRoutineType.SYNCHRONOUS
        )

    def test_invalid_diag_routine_type(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticRoutineNeeds(
                "DiagnosticRoutineNeeds",
                diag_routine_type="INVALID_TYPE"
            )


class TestDiagnosticStorageConditionNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticStorageConditionNeeds("DiagnosticStorageConditionNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-STORAGE-CONDITION-NEEDS>
  <SHORT-NAME>DiagnosticStorageConditionNeeds</SHORT-NAME>
</DIAGNOSTIC-STORAGE-CONDITION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticStorageConditionNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticStorageConditionNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticStorageConditionNeeds")
        self.assertIsNone(elem.initial_status)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticStorageConditionNeeds(
            "DiagnosticStorageConditionNeeds",
            initial_status=autosar.xml.enumeration.StorageConditionStatus.EVENT_STORAGE_ENABLED
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-STORAGE-CONDITION-NEEDS>
  <SHORT-NAME>DiagnosticStorageConditionNeeds</SHORT-NAME>
  <INITIAL-STATUS>EVENT-STORAGE-ENABLED</INITIAL-STATUS>
</DIAGNOSTIC-STORAGE-CONDITION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticStorageConditionNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticStorageConditionNeeds)
        self.assertEqual(
            elem.initial_status,
            autosar.xml.enumeration.StorageConditionStatus.EVENT_STORAGE_ENABLED
        )

    def test_with_string_enums(self):
        element = ar_element.DiagnosticStorageConditionNeeds(
            "DiagnosticStorageConditionNeeds",
            initial_status="EVENT-STORAGE-DISABLED"
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-STORAGE-CONDITION-NEEDS>
  <SHORT-NAME>DiagnosticStorageConditionNeeds</SHORT-NAME>
  <INITIAL-STATUS>EVENT-STORAGE-DISABLED</INITIAL-STATUS>
</DIAGNOSTIC-STORAGE-CONDITION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticStorageConditionNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticStorageConditionNeeds)
        self.assertEqual(
            elem.initial_status,
            autosar.xml.enumeration.StorageConditionStatus.EVENT_STORAGE_DISABLED
        )

    def test_invalid_initial_status(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticStorageConditionNeeds(
                "DiagnosticStorageConditionNeeds",
                initial_status="INVALID_STATUS"
            )


class TestDiagnosticUploadDownloadNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticUploadDownloadNeeds("DiagnosticUploadDownloadNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS>
  <SHORT-NAME>DiagnosticUploadDownloadNeeds</SHORT-NAME>
</DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticUploadDownloadNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticUploadDownloadNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticUploadDownloadNeeds")


class TestDiagnosticValueNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticValueNeeds("DiagnosticValueNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-VALUE-NEEDS>
  <SHORT-NAME>DiagnosticValueNeeds</SHORT-NAME>
</DIAGNOSTIC-VALUE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticValueNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticValueNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticValueNeeds")
        self.assertIsNone(elem.data_length)
        self.assertIsNone(elem.diagnostic_value_access)
        self.assertIsNone(elem.fixed_length)
        self.assertIsNone(elem.processing_style)

    def test_with_all_fields(self):
        element = ar_element.DiagnosticValueNeeds(
            "DiagnosticValueNeeds",
            data_length=4,
            diagnostic_value_access=autosar.xml.enumeration.DiagnosticValueAccess.READ_WRITE,
            fixed_length=True,
            processing_style=autosar.xml.enumeration.DiagnosticProcessingStyle.PROCESSING_STYLE_SYNCHRONOUS
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-VALUE-NEEDS>
  <SHORT-NAME>DiagnosticValueNeeds</SHORT-NAME>
  <DATA-LENGTH>4</DATA-LENGTH>
  <DIAGNOSTIC-VALUE-ACCESS>READ-WRITE</DIAGNOSTIC-VALUE-ACCESS>
  <FIXED-LENGTH>true</FIXED-LENGTH>
  <PROCESSING-STYLE>PROCESSING-STYLE-SYNCHRONOUS</PROCESSING-STYLE>
</DIAGNOSTIC-VALUE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticValueNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticValueNeeds)
        self.assertEqual(elem.data_length, 4)
        self.assertEqual(
            elem.diagnostic_value_access,
            autosar.xml.enumeration.DiagnosticValueAccess.READ_WRITE
        )
        self.assertTrue(elem.fixed_length)
        self.assertEqual(
            elem.processing_style,
            autosar.xml.enumeration.DiagnosticProcessingStyle.PROCESSING_STYLE_SYNCHRONOUS
        )

    def test_with_string_enums(self):
        element = ar_element.DiagnosticValueNeeds(
            "DiagnosticValueNeeds",
            diagnostic_value_access="READ-ONLY",
            processing_style="PROCESSING-STYLE-ASYNCHRONOUS"
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTIC-VALUE-NEEDS>
  <SHORT-NAME>DiagnosticValueNeeds</SHORT-NAME>
  <DIAGNOSTIC-VALUE-ACCESS>READ-ONLY</DIAGNOSTIC-VALUE-ACCESS>
  <PROCESSING-STYLE>PROCESSING-STYLE-ASYNCHRONOUS</PROCESSING-STYLE>
</DIAGNOSTIC-VALUE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticValueNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticValueNeeds)
        self.assertEqual(
            elem.diagnostic_value_access,
            autosar.xml.enumeration.DiagnosticValueAccess.READ_ONLY
        )
        self.assertEqual(
            elem.processing_style,
            autosar.xml.enumeration.DiagnosticProcessingStyle.PROCESSING_STYLE_ASYNCHRONOUS
        )

    def test_invalid_enums(self):
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticValueNeeds(
                "DiagnosticValueNeeds",
                diagnostic_value_access="INVALID_ACCESS"
            )
        with self.assertRaises(autosar.xml.exception.ConversionError):
            ar_element.DiagnosticValueNeeds(
                "DiagnosticValueNeeds",
                processing_style="INVALID_STYLE"
            )


class TestDiagnosticsCommunicationSecurityNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagnosticsCommunicationSecurityNeeds("DiagnosticsCommunicationSecurityNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS>
  <SHORT-NAME>DiagnosticsCommunicationSecurityNeeds</SHORT-NAME>
</DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagnosticsCommunicationSecurityNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagnosticsCommunicationSecurityNeeds)
        self.assertIsInstance(elem, ar_element.DiagnosticCapabilityElement)
        self.assertEqual(elem.name, "DiagnosticsCommunicationSecurityNeeds")


class TestDiagEventDebounceCounterBased(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagEventDebounceCounterBased("DiagEventDebounceCounterBased")
        writer = autosar.xml.Writer()
        xml = '''<DIAG-EVENT-DEBOUNCE-COUNTER-BASED>
  <SHORT-NAME>DiagEventDebounceCounterBased</SHORT-NAME>
</DIAG-EVENT-DEBOUNCE-COUNTER-BASED>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagEventDebounceCounterBased = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceCounterBased)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceAlgorithm)
        self.assertEqual(elem.name, "DiagEventDebounceCounterBased")
        self.assertIsNone(elem.counter_based_fdc_threshold_storage_value)
        self.assertIsNone(elem.counter_decrement_step_size)
        self.assertIsNone(elem.counter_failed_threshold)
        self.assertIsNone(elem.counter_increment_step_size)
        self.assertIsNone(elem.counter_jump_down)
        self.assertIsNone(elem.counter_jump_down_value)
        self.assertIsNone(elem.counter_jump_up)
        self.assertIsNone(elem.counter_jump_up_value)
        self.assertIsNone(elem.counter_passed_threshold)

    def test_with_all_fields(self):
        element = ar_element.DiagEventDebounceCounterBased(
            "DiagEventDebounceCounterBased",
            counter_based_fdc_threshold_storage_value=10,
            counter_decrement_step_size=1,
            counter_failed_threshold=20,
            counter_increment_step_size=2,
            counter_jump_down=True,
            counter_jump_down_value=5,
            counter_jump_up=False,
            counter_jump_up_value=15,
            counter_passed_threshold=-20
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAG-EVENT-DEBOUNCE-COUNTER-BASED>
  <SHORT-NAME>DiagEventDebounceCounterBased</SHORT-NAME>
  <COUNTER-BASED-FDC-THRESHOLD-STORAGE-VALUE>10</COUNTER-BASED-FDC-THRESHOLD-STORAGE-VALUE>
  <COUNTER-DECREMENT-STEP-SIZE>1</COUNTER-DECREMENT-STEP-SIZE>
  <COUNTER-FAILED-THRESHOLD>20</COUNTER-FAILED-THRESHOLD>
  <COUNTER-INCREMENT-STEP-SIZE>2</COUNTER-INCREMENT-STEP-SIZE>
  <COUNTER-JUMP-DOWN>true</COUNTER-JUMP-DOWN>
  <COUNTER-JUMP-DOWN-VALUE>5</COUNTER-JUMP-DOWN-VALUE>
  <COUNTER-JUMP-UP>false</COUNTER-JUMP-UP>
  <COUNTER-JUMP-UP-VALUE>15</COUNTER-JUMP-UP-VALUE>
  <COUNTER-PASSED-THRESHOLD>-20</COUNTER-PASSED-THRESHOLD>
</DIAG-EVENT-DEBOUNCE-COUNTER-BASED>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagEventDebounceCounterBased = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceCounterBased)
        self.assertEqual(elem.counter_based_fdc_threshold_storage_value, 10)
        self.assertEqual(elem.counter_decrement_step_size, 1)
        self.assertEqual(elem.counter_failed_threshold, 20)
        self.assertEqual(elem.counter_increment_step_size, 2)
        self.assertTrue(elem.counter_jump_down)
        self.assertEqual(elem.counter_jump_down_value, 5)
        self.assertFalse(elem.counter_jump_up)
        self.assertEqual(elem.counter_jump_up_value, 15)
        self.assertEqual(elem.counter_passed_threshold, -20)


class TestDiagEventDebounceMonitorInternal(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagEventDebounceMonitorInternal("DiagEventDebounceMonitorInternal")
        writer = autosar.xml.Writer()
        xml = '''<DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL>
  <SHORT-NAME>DiagEventDebounceMonitorInternal</SHORT-NAME>
</DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagEventDebounceMonitorInternal = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceMonitorInternal)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceAlgorithm)
        self.assertEqual(elem.name, "DiagEventDebounceMonitorInternal")


class TestDiagEventDebounceTimeBased(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DiagEventDebounceTimeBased("DiagEventDebounceTimeBased")
        writer = autosar.xml.Writer()
        xml = '''<DIAG-EVENT-DEBOUNCE-TIME-BASED>
  <SHORT-NAME>DiagEventDebounceTimeBased</SHORT-NAME>
</DIAG-EVENT-DEBOUNCE-TIME-BASED>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagEventDebounceTimeBased = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceTimeBased)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceAlgorithm)
        self.assertEqual(elem.name, "DiagEventDebounceTimeBased")
        self.assertIsNone(elem.time_based_fdc_threshold_storage_value)
        self.assertIsNone(elem.time_failed_threshold)
        self.assertIsNone(elem.time_passed_threshold)

    def test_with_all_fields(self):
        element = ar_element.DiagEventDebounceTimeBased(
            "DiagEventDebounceTimeBased",
            time_based_fdc_threshold_storage_value=0.5,
            time_failed_threshold=1.2,
            time_passed_threshold=0.8
        )
        writer = autosar.xml.Writer()
        xml = '''<DIAG-EVENT-DEBOUNCE-TIME-BASED>
  <SHORT-NAME>DiagEventDebounceTimeBased</SHORT-NAME>
  <TIME-BASED-FDC-THRESHOLD-STORAGE-VALUE>0.5</TIME-BASED-FDC-THRESHOLD-STORAGE-VALUE>
  <TIME-FAILED-THRESHOLD>1.2</TIME-FAILED-THRESHOLD>
  <TIME-PASSED-THRESHOLD>0.8</TIME-PASSED-THRESHOLD>
</DIAG-EVENT-DEBOUNCE-TIME-BASED>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DiagEventDebounceTimeBased = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DiagEventDebounceTimeBased)
        self.assertEqual(elem.time_based_fdc_threshold_storage_value, 0.5)
        self.assertEqual(elem.time_failed_threshold, 1.2)
        self.assertEqual(elem.time_passed_threshold, 0.8)


class TestDltUserNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DltUserNeeds("DltUserNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DLT-USER-NEEDS>
  <SHORT-NAME>DltUserNeeds</SHORT-NAME>
</DLT-USER-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DltUserNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DltUserNeeds)
        self.assertIsInstance(elem, ar_element.ServiceNeeds)
        self.assertEqual(elem.name, "DltUserNeeds")


class TestDoIpActivationLineNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DoIpActivationLineNeeds("DoIpActivationLineNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-ACTIVATION-LINE-NEEDS>
  <SHORT-NAME>DoIpActivationLineNeeds</SHORT-NAME>
</DO-IP-ACTIVATION-LINE-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpActivationLineNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpActivationLineNeeds)
        self.assertIsInstance(elem, ar_element.DoIpServiceNeeds)
        self.assertEqual(elem.name, "DoIpActivationLineNeeds")


class TestDoIpGidNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DoIpGidNeeds("DoIpGidNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-GID-NEEDS>
  <SHORT-NAME>DoIpGidNeeds</SHORT-NAME>
</DO-IP-GID-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpGidNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpGidNeeds)
        self.assertIsInstance(elem, ar_element.DoIpServiceNeeds)
        self.assertEqual(elem.name, "DoIpGidNeeds")


class TestDoIpGidSynchronizationNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DoIpGidSynchronizationNeeds("DoIpGidSynchronizationNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-GID-SYNCHRONIZATION-NEEDS>
  <SHORT-NAME>DoIpGidSynchronizationNeeds</SHORT-NAME>
</DO-IP-GID-SYNCHRONIZATION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpGidSynchronizationNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpGidSynchronizationNeeds)
        self.assertIsInstance(elem, ar_element.DoIpServiceNeeds)
        self.assertEqual(elem.name, "DoIpGidSynchronizationNeeds")


class TestDoIpPowerModeStatusNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DoIpPowerModeStatusNeeds("DoIpPowerModeStatusNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-POWER-MODE-STATUS-NEEDS>
  <SHORT-NAME>DoIpPowerModeStatusNeeds</SHORT-NAME>
</DO-IP-POWER-MODE-STATUS-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpPowerModeStatusNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpPowerModeStatusNeeds)
        self.assertIsInstance(elem, ar_element.DoIpServiceNeeds)
        self.assertEqual(elem.name, "DoIpPowerModeStatusNeeds")


class TestDoIpRoutingActivationAuthenticationNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DoIpRoutingActivationAuthenticationNeeds("DoIpRoutingActivationAuthenticationNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS>
  <SHORT-NAME>DoIpRoutingActivationAuthenticationNeeds</SHORT-NAME>
</DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpRoutingActivationAuthenticationNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpRoutingActivationAuthenticationNeeds)
        self.assertIsInstance(elem, ar_element.DoIpServiceNeeds)
        self.assertEqual(elem.name, "DoIpRoutingActivationAuthenticationNeeds")
        self.assertIsNone(elem.data_length_request)
        self.assertIsNone(elem.data_length_response)
        self.assertIsNone(elem.routing_activation_type)

    def test_with_all_fields(self):
        element = ar_element.DoIpRoutingActivationAuthenticationNeeds(
            "DoIpRoutingActivationAuthenticationNeeds",
            data_length_request=16,
            data_length_response=32,
            routing_activation_type="RA_0xE1"
        )
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS>
  <SHORT-NAME>DoIpRoutingActivationAuthenticationNeeds</SHORT-NAME>
  <DATA-LENGTH-REQUEST>16</DATA-LENGTH-REQUEST>
  <DATA-LENGTH-RESPONSE>32</DATA-LENGTH-RESPONSE>
  <ROUTING-ACTIVATION-TYPE>RA_0xE1</ROUTING-ACTIVATION-TYPE>
</DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpRoutingActivationAuthenticationNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpRoutingActivationAuthenticationNeeds)
        self.assertEqual(elem.data_length_request, 16)
        self.assertEqual(elem.data_length_response, 32)
        self.assertEqual(elem.routing_activation_type, "RA_0xE1")


class TestDoIpRoutingActivationConfirmationNeeds(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DoIpRoutingActivationConfirmationNeeds("DoIpRoutingActivationConfirmationNeeds")
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS>
  <SHORT-NAME>DoIpRoutingActivationConfirmationNeeds</SHORT-NAME>
</DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpRoutingActivationConfirmationNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpRoutingActivationConfirmationNeeds)
        self.assertIsInstance(elem, ar_element.DoIpServiceNeeds)
        self.assertEqual(elem.name, "DoIpRoutingActivationConfirmationNeeds")
        self.assertIsNone(elem.data_length_request)
        self.assertIsNone(elem.data_length_response)
        self.assertIsNone(elem.routing_activation_type)

    def test_with_all_fields(self):
        element = ar_element.DoIpRoutingActivationConfirmationNeeds(
            "DoIpRoutingActivationConfirmationNeeds",
            data_length_request=8,
            data_length_response=16,
            routing_activation_type="0x01"
        )
        writer = autosar.xml.Writer()
        xml = '''<DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS>
  <SHORT-NAME>DoIpRoutingActivationConfirmationNeeds</SHORT-NAME>
  <DATA-LENGTH-REQUEST>8</DATA-LENGTH-REQUEST>
  <DATA-LENGTH-RESPONSE>16</DATA-LENGTH-RESPONSE>
  <ROUTING-ACTIVATION-TYPE>0x01</ROUTING-ACTIVATION-TYPE>
</DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DoIpRoutingActivationConfirmationNeeds = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DoIpRoutingActivationConfirmationNeeds)
        self.assertEqual(elem.data_length_request, 8)
        self.assertEqual(elem.data_length_response, 16)
        self.assertEqual(elem.routing_activation_type, "0x01")


if __name__ == '__main__':
    unittest.main()
