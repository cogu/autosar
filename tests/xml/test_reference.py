"""Unit tests for programmatically building components and save them as XML"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element # noqa E402
import autosar.xml.enumeration as ar_enum  # noqa E402
import autosar # noqa E402


class TestPortReferences(unittest.TestCase):

    def test_abstract_require_port_prototype_ref(self):

        rport_ref = ar_element.PortPrototypeRef("/ComponentTypes/MyApplicationComponent/RequirePort1",
                                                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        pport_ref = ar_element.PortPrototypeRef("/ComponentTypes/MyApplicationComponent/ProvidePort1",
                                                ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        ar_element.AbstractRequiredPortPrototypeRef(rport_ref.value, rport_ref.dest)
        with self.assertRaises(ValueError):
            ar_element.AbstractRequiredPortPrototypeRef(pport_ref.value, pport_ref.dest)


class TestPortInterfaceRef(unittest.TestCase):
    def test_client_server_interface(self):
        reference = "/PortInterfaces/PortInterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(reference,
                                                         ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE)
        element = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>PortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="CLIENT-SERVER-INTERFACE">{reference}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), reference)
        self.assertEqual(elem.port_interface_ref.dest,
                         ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE)

    def test_mode_switch_interface(self):
        reference = "/PortInterfaces/PortInterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(reference,
                                                         ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE)
        element = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>PortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="MODE-SWITCH-INTERFACE">{reference}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), reference)
        self.assertEqual(elem.port_interface_ref.dest,
                         ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE)

    def test_nv_data_interface(self):
        reference = "/PortInterfaces/PortInterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(reference,
                                                         ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE)
        element = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>PortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="NV-DATA-INTERFACE">{reference}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), reference)
        self.assertEqual(elem.port_interface_ref.dest,
                         ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE)

    def test_parameter_interface(self):
        reference = "/PortInterfaces/PortInterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(reference,
                                                         ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE)
        element = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>PortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="PARAMETER-INTERFACE">{reference}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), reference)
        self.assertEqual(elem.port_interface_ref.dest, ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE)

    def test_sender_receiver_interface(self):
        reference = "/PortInterfaces/PortInterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(reference,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        element = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>PortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{reference}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), reference)
        self.assertEqual(elem.port_interface_ref.dest,
                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)

    def test_trigger_interface(self):
        reference = "/PortInterfaces/PortInterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(reference, ar_enum.IdentifiableSubTypes.TRIGGER_INTERFACE)
        element = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>PortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="TRIGGER-INTERFACE">{reference}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), reference)
        self.assertEqual(elem.port_interface_ref.dest, ar_enum.IdentifiableSubTypes.TRIGGER_INTERFACE)


class TestDataPrototypeRef(unittest.TestCase):

    def test_requires_dest(self):
        with self.assertRaises(ValueError):
            ar_element.DataPrototypeRef("/Component/MyPrototype")

    def test_valid_dest(self):
        ref = ar_element.DataPrototypeRef("/Component/MyPrototype",
                                          ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
        self.assertEqual(str(ref), "/Component/MyPrototype")
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)


if __name__ == '__main__':
    unittest.main()
