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


if __name__ == '__main__':
    unittest.main()
