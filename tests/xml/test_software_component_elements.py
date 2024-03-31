"""Unit tests for reading/writing software component elements"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestTestModeSwitchedAckRequest(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ModeSwitchedAckRequest()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<MODE-SWITCHED-ACK/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchedAckRequest = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchedAckRequest)

    def test_timeout_from_int(self):
        element = ar_element.ModeSwitchedAckRequest(timeout=0)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCHED-ACK>
  <TIMEOUT>0</TIMEOUT>
</MODE-SWITCHED-ACK>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchedAckRequest = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchedAckRequest)
        self.assertEqual(elem.timeout, 0)

    def test_timeout_from_float(self):
        element = ar_element.ModeSwitchedAckRequest(timeout=1.62)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCHED-ACK>
  <TIMEOUT>1.62</TIMEOUT>
</MODE-SWITCHED-ACK>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchedAckRequest = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchedAckRequest)
        self.assertAlmostEqual(elem.timeout, 1.62)


class TestModeSwitchSenderComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ModeSwitchSenderComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<MODE-SWITCH-SENDER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchSenderComSpec)

    def test_enhanced_mode_api(self):
        element = ar_element.ModeSwitchSenderComSpec(enhanced_mode_api=True)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-SENDER-COM-SPEC>
  <ENHANCED-MODE-API>true</ENHANCED-MODE-API>
</MODE-SWITCH-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchSenderComSpec)
        self.assertTrue(elem.enhanced_mode_api)

    def test_mode_group_ref_from_str(self):
        element = ar_element.ModeSwitchSenderComSpec(mode_group_ref="/PortInterfaces/InterfaceName/ModeName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-SENDER-COM-SPEC>
  <MODE-GROUP-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">/PortInterfaces/InterfaceName/ModeName</MODE-GROUP-REF>
</MODE-SWITCH-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchSenderComSpec)
        self.assertIsInstance(elem.mode_group_ref, ar_element.ModeDeclarationGroupPrototypeRef)
        self.assertEqual(str(elem.mode_group_ref), "/PortInterfaces/InterfaceName/ModeName")

    def test_mode_group_ref_from_object(self):
        mode_group_ref = ar_element.ModeDeclarationGroupPrototypeRef("/PortInterfaces/InterfaceName/ModeName")
        element = ar_element.ModeSwitchSenderComSpec(mode_group_ref=mode_group_ref)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-SENDER-COM-SPEC>
  <MODE-GROUP-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">/PortInterfaces/InterfaceName/ModeName</MODE-GROUP-REF>
</MODE-SWITCH-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchSenderComSpec)
        self.assertIsInstance(elem.mode_group_ref, ar_element.ModeDeclarationGroupPrototypeRef)
        self.assertEqual(str(elem.mode_group_ref), "/PortInterfaces/InterfaceName/ModeName")

    def test_mode_switched_ack(self):
        element = ar_element.ModeSwitchSenderComSpec(mode_switched_ack=0.01)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-SENDER-COM-SPEC>
  <MODE-SWITCHED-ACK>
    <TIMEOUT>0.01</TIMEOUT>
  </MODE-SWITCHED-ACK>
</MODE-SWITCH-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchSenderComSpec)
        self.assertIsInstance(elem.mode_switched_ack, ar_element.ModeSwitchedAckRequest)
        self.assertAlmostEqual(elem.mode_switched_ack.timeout, 0.01)

    def test_queue_length(self):
        element = ar_element.ModeSwitchSenderComSpec(queue_length=1)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-SENDER-COM-SPEC>
  <QUEUE-LENGTH>1</QUEUE-LENGTH>
</MODE-SWITCH-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchSenderComSpec)
        self.assertEqual(elem.queue_length, 1)


class TestTransmissionComSpecProps(unittest.TestCase):

    def test_empty(self):
        element = ar_element.TransmissionComSpecProps()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<TRANSMISSION-PROPS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.TransmissionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TransmissionComSpecProps)

    def test_data_update_period(self):
        element = ar_element.TransmissionComSpecProps(data_update_period=0.02)
        writer = autosar.xml.Writer()
        xml = '''<TRANSMISSION-PROPS>
  <DATA-UPDATE-PERIOD>0.02</DATA-UPDATE-PERIOD>
</TRANSMISSION-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.TransmissionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TransmissionComSpecProps)
        self.assertAlmostEqual(elem.data_update_period, 0.02)

    def test_minimum_send_interval(self):
        element = ar_element.TransmissionComSpecProps(minimum_send_interval=0.1)
        writer = autosar.xml.Writer()
        xml = '''<TRANSMISSION-PROPS>
  <MINIMUM-SEND-INTERVAL>0.1</MINIMUM-SEND-INTERVAL>
</TRANSMISSION-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.TransmissionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TransmissionComSpecProps)
        self.assertAlmostEqual(elem.minimum_send_interval, 0.1)

    def test_transmission_mode(self):
        element = ar_element.TransmissionComSpecProps(transmission_mode=ar_enum.TransmissionMode.CYCLIC_AND_ON_CHANGE)
        writer = autosar.xml.Writer()
        xml = '''<TRANSMISSION-PROPS>
  <TRANSMISSION-MODE>CYCLIC-AND-ON-CHANGE</TRANSMISSION-MODE>
</TRANSMISSION-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.TransmissionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.TransmissionComSpecProps)
        self.assertEqual(elem.transmission_mode, ar_enum.TransmissionMode.CYCLIC_AND_ON_CHANGE)


class TestQueuedSenderComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.QueuedSenderComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<QUEUED-SENDER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)

    def test_data_element_ref(self):
        data_element_ref = ar_element.AutosarDataPrototypeRef("/PortInterfaces/InterfaceName/ElementName",
                                                              ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
        element = ar_element.QueuedSenderComSpec(data_element_ref=data_element_ref)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-SENDER-COM-SPEC>
  <DATA-ELEMENT-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/InterfaceName/ElementName</DATA-ELEMENT-REF>
</QUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)
        self.assertIsInstance(elem.data_element_ref, ar_element.AutosarDataPrototypeRef)
        self.assertEqual(str(elem.data_element_ref), "/PortInterfaces/InterfaceName/ElementName")
        self.assertEqual(elem.data_element_ref.dest, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)

    def test_handle_out_range(self):
        element = ar_element.QueuedSenderComSpec(handle_out_of_range=ar_enum.HandleOutOfRange.SATURATE)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-SENDER-COM-SPEC>
  <HANDLE-OUT-OF-RANGE>SATURATE</HANDLE-OUT-OF-RANGE>
</QUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)
        self.assertAlmostEqual(elem.handle_out_of_range, ar_enum.HandleOutOfRange.SATURATE)

    def test_network_representation(self):
        impl_type_ref = ar_element.ImplementationDataTypeRef("/DataTypes/TypeName")
        network_props = ar_element.SwDataDefProps(
            ar_element.SwDataDefPropsConditional(impl_data_type_ref=impl_type_ref))
        element = ar_element.QueuedSenderComSpec(network_representation=network_props)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-SENDER-COM-SPEC>
  <NETWORK-REPRESENTATION>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/TypeName</IMPLEMENTATION-DATA-TYPE-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </NETWORK-REPRESENTATION>
</QUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)
        self.assertEqual(str(elem.network_representation[0].impl_data_type_ref),
                         "/DataTypes/TypeName")

    def test_transmission_acknowledge(self):
        tranmsission_ack = ar_element.TransmissionAcknowledgementRequest(5)
        element = ar_element.QueuedSenderComSpec(transmission_acknowledge=tranmsission_ack)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-SENDER-COM-SPEC>
  <TRANSMISSION-ACKNOWLEDGE>
    <TIMEOUT>5</TIMEOUT>
  </TRANSMISSION-ACKNOWLEDGE>
</QUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)
        self.assertEqual(elem.transmission_acknowledge.timeout, 5)

    def test_tranmsission_props(self):
        tranmsission_props = ar_element.TransmissionComSpecProps(data_update_period=0.1,
                                                                 transmission_mode=ar_enum.TransmissionMode.CYCLIC)
        element = ar_element.QueuedSenderComSpec(tranmsission_props=tranmsission_props)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-SENDER-COM-SPEC>
  <TRANSMISSION-PROPS>
    <DATA-UPDATE-PERIOD>0.1</DATA-UPDATE-PERIOD>
    <TRANSMISSION-MODE>CYCLIC</TRANSMISSION-MODE>
  </TRANSMISSION-PROPS>
</QUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)
        self.assertAlmostEqual(elem.tranmsission_props.data_update_period, 0.1)
        self.assertEqual(elem.tranmsission_props.transmission_mode, ar_enum.TransmissionMode.CYCLIC)

    def test_uses_end_to_end_protection(self):
        element = ar_element.QueuedSenderComSpec(uses_end_to_end_protection=False)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-SENDER-COM-SPEC>
  <USES-END-TO-END-PROTECTION>false</USES-END-TO-END-PROTECTION>
</QUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedSenderComSpec)
        self.assertFalse(elem.uses_end_to_end_protection)


class TestNonqueuedSenderComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.NonqueuedSenderComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NONQUEUED-SENDER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedSenderComSpec)

    def test_data_filter(self):
        data_filter = ar_element.DataFilter(min_val=0, max_val=10)
        element = ar_element.NonqueuedSenderComSpec(data_filter=data_filter)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-SENDER-COM-SPEC>
  <DATA-FILTER>
    <MAX>10</MAX>
    <MIN>0</MIN>
  </DATA-FILTER>
</NONQUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedSenderComSpec)
        self.assertIsInstance(elem.data_filter, ar_element.DataFilter)
        self.assertEqual(elem.data_filter.min_val, 0)
        self.assertEqual(elem.data_filter.max_val, 10)

    def test_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=10)
        element = ar_element.NonqueuedSenderComSpec(init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-SENDER-COM-SPEC>
  <INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>10</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </INIT-VALUE>
</NONQUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedSenderComSpec)
        self.assertIsInstance(elem.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.init_value.value, 10)

    def test_normal_use_case(self):
        data_element_ref = ar_element.VariableDataPrototypeRef("/PortInterfaces/InterfaceName/ElementName")
        init_value_ref = ar_element.ConstantReference("/Constants/ConstantName")
        element = ar_element.NonqueuedSenderComSpec(data_element_ref=data_element_ref,
                                                    init_value=init_value_ref,
                                                    uses_end_to_end_protection=False)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-SENDER-COM-SPEC>
  <DATA-ELEMENT-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/InterfaceName/ElementName</DATA-ELEMENT-REF>
  <USES-END-TO-END-PROTECTION>false</USES-END-TO-END-PROTECTION>
  <INIT-VALUE>
    <CONSTANT-REFERENCE>
      <CONSTANT-REF DEST="CONSTANT-SPECIFICATION">/Constants/ConstantName</CONSTANT-REF>
    </CONSTANT-REFERENCE>
  </INIT-VALUE>
</NONQUEUED-SENDER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedSenderComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedSenderComSpec)
        self.assertEqual(str(elem.data_element_ref), "/PortInterfaces/InterfaceName/ElementName")
        self.assertEqual(str(elem.init_value.constant_ref), "/Constants/ConstantName")
        self.assertFalse(elem.uses_end_to_end_protection)


class TestNvProvideComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.NvProvideComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NV-PROVIDE-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NvProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvProvideComSpec)

    def test_variable_ref_from_object(self):
        variable_ref = ar_element.VariableDataPrototypeRef("/PortInterfaces/NvDataInterface/Data")
        element = ar_element.NvProvideComSpec(variable_ref=variable_ref)
        writer = autosar.xml.Writer()
        xml = '''<NV-PROVIDE-COM-SPEC>
  <VARIABLE-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/NvDataInterface/Data</VARIABLE-REF>
</NV-PROVIDE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvProvideComSpec)
        self.assertEqual(str(elem.variable_ref), "/PortInterfaces/NvDataInterface/Data")

    def test_ram_block_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=255)
        element = ar_element.NvProvideComSpec(ram_block_init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<NV-PROVIDE-COM-SPEC>
  <RAM-BLOCK-INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>255</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </RAM-BLOCK-INIT-VALUE>
</NV-PROVIDE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvProvideComSpec)
        self.assertIsInstance(elem.ram_block_init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.ram_block_init_value.value, 255)

    def test_rom_block_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=255)
        element = ar_element.NvProvideComSpec(rom_block_init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<NV-PROVIDE-COM-SPEC>
  <ROM-BLOCK-INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>255</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </ROM-BLOCK-INIT-VALUE>
</NV-PROVIDE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvProvideComSpec)
        self.assertIsInstance(elem.rom_block_init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.rom_block_init_value.value, 255)


class TestParameterProvideComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ParameterProvideComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<PARAMETER-PROVIDE-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterProvideComSpec)

    def test_variable_ref_from_object(self):
        parameter_ref = ar_element.ParameterDataPrototypeRef("/PortInterfaces/ParameterInterface/Value")
        element = ar_element.ParameterProvideComSpec(parameter_ref=parameter_ref)
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-PROVIDE-COM-SPEC>
  <PARAMETER-REF DEST="PARAMETER-DATA-PROTOTYPE">/PortInterfaces/ParameterInterface/Value</PARAMETER-REF>
</PARAMETER-PROVIDE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterProvideComSpec)
        self.assertEqual(str(elem.parameter_ref), "/PortInterfaces/ParameterInterface/Value")

    def test_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=0)
        element = ar_element.ParameterProvideComSpec(init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-PROVIDE-COM-SPEC>
  <INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>0</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </INIT-VALUE>
</PARAMETER-PROVIDE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterProvideComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterProvideComSpec)
        self.assertIsInstance(elem.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.init_value.value, 0)


class TestServerComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ServerComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<SERVER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ServerComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ServerComSpec)

    def test_operation_ref_from_object(self):
        ref_str = "/PortInterfaces/ClientServerInterface1/Operation1"
        operation_ref = ar_element.ClientServerOperationRef(ref_str)
        element = ar_element.ServerComSpec(operation_ref=operation_ref)
        writer = autosar.xml.Writer()
        xml = f'''<SERVER-COM-SPEC>
  <OPERATION-REF DEST="CLIENT-SERVER-OPERATION">{ref_str}</OPERATION-REF>
</SERVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ServerComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ServerComSpec)
        self.assertEqual(str(elem.operation_ref), ref_str)

    def test_operation_ref_from_str(self):
        ref_str = "/PortInterfaces/ClientServerInterface1/Operation1"
        element = ar_element.ServerComSpec(operation_ref=ref_str)
        writer = autosar.xml.Writer()
        xml = f'''<SERVER-COM-SPEC>
  <OPERATION-REF DEST="CLIENT-SERVER-OPERATION">{ref_str}</OPERATION-REF>
</SERVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ServerComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ServerComSpec)
        self.assertEqual(str(elem.operation_ref), ref_str)

    def test_queue_length(self):
        element = ar_element.ServerComSpec(queue_length=1)
        writer = autosar.xml.Writer()
        xml = '''<SERVER-COM-SPEC>
  <QUEUE-LENGTH>1</QUEUE-LENGTH>
</SERVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ServerComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ServerComSpec)
        self.assertEqual(elem.queue_length, 1)

    def test_transformation_com_spec_props_single(self):
        com_spec_props = ar_element.EndToEndTransformationComSpecProps(disable_e2e_check=True)
        element = ar_element.ServerComSpec(transformation_com_spec_props=com_spec_props)
        writer = autosar.xml.Writer()
        xml = '''<SERVER-COM-SPEC>
  <TRANSFORMATION-COM-SPEC-PROPSS>
    <END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
      <DISABLE-END-TO-END-CHECK>true</DISABLE-END-TO-END-CHECK>
    </END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  </TRANSFORMATION-COM-SPEC-PROPSS>
</SERVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ServerComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ServerComSpec)
        self.assertEqual(len(elem.transformation_com_spec_props), 1)
        props = elem.transformation_com_spec_props[0]
        self.assertTrue(props.disable_e2e_check)


class TestReceptionComSpecProps(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ReceptionComSpecProps()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<RECEPTION-PROPS/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ReceptionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ReceptionComSpecProps)

    def test_data_update_period(self):
        element = ar_element.ReceptionComSpecProps(data_update_period=0.1)
        writer = autosar.xml.Writer()
        xml = '''<RECEPTION-PROPS>
  <DATA-UPDATE-PERIOD>0.1</DATA-UPDATE-PERIOD>
</RECEPTION-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ReceptionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ReceptionComSpecProps)
        self.assertAlmostEqual(elem.data_update_period, 0.1)

    def test_timeout(self):
        element = ar_element.ReceptionComSpecProps(timeout=1)
        writer = autosar.xml.Writer()
        xml = '''<RECEPTION-PROPS>
  <TIMEOUT>1</TIMEOUT>
</RECEPTION-PROPS>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ReceptionComSpecProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ReceptionComSpecProps)
        self.assertAlmostEqual(elem.timeout, 1)


class TestVariableAccess(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.VariableAccess("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<VARIABLE-ACCESS>
  <SHORT-NAME>ShortName</SHORT-NAME>
</VARIABLE-ACCESS>'''
        self.assertEqual(writer.write_str_elem(element, "VARIABLE-ACCESS"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableAccess = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableAccess)
        self.assertEqual(elem.name, "ShortName")

    def test_accessed_variable(self):
        ref_str = "/Components/SwcName/VariableName"
        variable_ref = ar_element.VariableDataPrototypeRef(ref_str)
        accessed_var = ar_element.AutosarVariableRef(local_variable_ref=variable_ref)
        element = ar_element.VariableAccess("ShortName",
                                            accessed_variable=accessed_var)
        writer = autosar.xml.Writer()
        xml = f'''<VARIABLE-ACCESS>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <ACCESSED-VARIABLE>
    <LOCAL-VARIABLE-REF DEST="VARIABLE-DATA-PROTOTYPE">{ref_str}</LOCAL-VARIABLE-REF>
  </ACCESSED-VARIABLE>
</VARIABLE-ACCESS>'''
        self.assertEqual(writer.write_str_elem(element, "VARIABLE-ACCESS"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableAccess = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableAccess)
        self.assertIsInstance(elem.accessed_variable, ar_element.AutosarVariableRef)

    def test_scope(self):
        element = ar_element.VariableAccess("ShortName",
                                            scope=ar_enum.VariableAccessScope.INTER_PARTITION_INTRA_ECU)
        writer = autosar.xml.Writer()
        xml = '''<VARIABLE-ACCESS>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <SCOPE>INTER-PARTITION-INTRA-ECU</SCOPE>
</VARIABLE-ACCESS>'''
        self.assertEqual(writer.write_str_elem(element, "VARIABLE-ACCESS"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableAccess = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableAccess)
        self.assertEqual(elem.scope, ar_enum.VariableAccessScope.INTER_PARTITION_INTRA_ECU)


class TestQueuedReceiverComSpec(unittest.TestCase):
    """
    This also tests elements in class ReceiverComSpec
    """

    def test_empty(self):
        element = ar_element.QueuedReceiverComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<QUEUED-RECEIVER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)

    def test_data_element_ref(self):
        data_element_ref = ar_element.AutosarDataPrototypeRef("/PortInterfaces/InterfaceName/ElementName",
                                                              ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
        element = ar_element.QueuedReceiverComSpec(data_element_ref=data_element_ref)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <DATA-ELEMENT-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/InterfaceName/ElementName</DATA-ELEMENT-REF>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertIsInstance(elem.data_element_ref, ar_element.AutosarDataPrototypeRef)
        self.assertEqual(str(elem.data_element_ref), "/PortInterfaces/InterfaceName/ElementName")
        self.assertEqual(elem.data_element_ref.dest, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)

    def test_handle_out_of_range(self):
        element = ar_element.QueuedReceiverComSpec(handle_out_of_range=ar_enum.HandleOutOfRange.SATURATE)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <HANDLE-OUT-OF-RANGE>SATURATE</HANDLE-OUT-OF-RANGE>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(elem.handle_out_of_range, ar_enum.HandleOutOfRange.SATURATE)

    def test_handle_out_of_range_status(self):
        element = ar_element.QueuedReceiverComSpec(handle_out_of_range_status=ar_enum.HandleOutOfRangeStatus.SILENT)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <HANDLE-OUT-OF-RANGE-STATUS>SILENT</HANDLE-OUT-OF-RANGE-STATUS>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(elem.handle_out_of_range_status, ar_enum.HandleOutOfRangeStatus.SILENT)

    def test_max_delta_counter_init(self):
        element = ar_element.QueuedReceiverComSpec(max_delta_counter_init=10)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <MAX-DELTA-COUNTER-INIT>10</MAX-DELTA-COUNTER-INIT>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(elem.max_delta_counter_init, 10)

    def test_max_no_new_repeated_data(self):
        element = ar_element.QueuedReceiverComSpec(max_no_new_repeated_data=20)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <MAX-NO-NEW-OR-REPEATED-DATA>20</MAX-NO-NEW-OR-REPEATED-DATA>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(elem.max_no_new_repeated_data, 20)

    def test_network_representation(self):
        impl_type_ref = ar_element.ImplementationDataTypeRef("/DataTypes/TypeName")
        network_props = ar_element.SwDataDefProps(
            ar_element.SwDataDefPropsConditional(impl_data_type_ref=impl_type_ref))
        element = ar_element.QueuedReceiverComSpec(network_representation=network_props)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <NETWORK-REPRESENTATION>
    <SW-DATA-DEF-PROPS-VARIANTS>
      <SW-DATA-DEF-PROPS-CONDITIONAL>
        <IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/TypeName</IMPLEMENTATION-DATA-TYPE-REF>
      </SW-DATA-DEF-PROPS-CONDITIONAL>
    </SW-DATA-DEF-PROPS-VARIANTS>
  </NETWORK-REPRESENTATION>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(str(elem.network_representation[0].impl_data_type_ref), "/DataTypes/TypeName")

    def test_reception_props(self):
        props = ar_element.ReceptionComSpecProps(data_update_period=0.1, timeout=0.8)
        element = ar_element.QueuedReceiverComSpec(reception_props=props)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <RECEPTION-PROPS>
    <DATA-UPDATE-PERIOD>0.1</DATA-UPDATE-PERIOD>
    <TIMEOUT>0.8</TIMEOUT>
  </RECEPTION-PROPS>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertAlmostEqual(elem.reception_props.data_update_period, 0.1)
        self.assertAlmostEqual(elem.reception_props.timeout, 0.8)

    def test_replace_with(self):
        access = ar_element.VariableAccess("ShortName",
                                           scope=ar_enum.VariableAccessScope.INTER_PARTITION_INTRA_ECU)
        element = ar_element.QueuedReceiverComSpec(replace_with=access)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <REPLACE-WITH>
    <SHORT-NAME>ShortName</SHORT-NAME>
    <SCOPE>INTER-PARTITION-INTRA-ECU</SCOPE>
  </REPLACE-WITH>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertIsInstance(elem.replace_with, ar_element.VariableAccess)

    def test_sync_counter_init(self):
        element = ar_element.QueuedReceiverComSpec(sync_counter_init=10)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <SYNC-COUNTER-INIT>10</SYNC-COUNTER-INIT>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(elem.sync_counter_init, 10)

    def test_transformation_com_spec_props_single(self):
        com_spec_props = ar_element.EndToEndTransformationComSpecProps(disable_e2e_check=True)
        element = ar_element.QueuedReceiverComSpec(transformation_com_spec_props=com_spec_props)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <TRANSFORMATION-COM-SPEC-PROPSS>
    <END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
      <DISABLE-END-TO-END-CHECK>true</DISABLE-END-TO-END-CHECK>
    </END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  </TRANSFORMATION-COM-SPEC-PROPSS>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(len(elem.transformation_com_spec_props), 1)
        props = elem.transformation_com_spec_props[0]
        self.assertTrue(props.disable_e2e_check)

    def test_uses_end_to_end_protection(self):
        element = ar_element.QueuedReceiverComSpec(uses_end_to_end_protection=False)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <USES-END-TO-END-PROTECTION>false</USES-END-TO-END-PROTECTION>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertFalse(elem.uses_end_to_end_protection)

    def test_queue_length(self):
        element = ar_element.QueuedReceiverComSpec(queue_length=1)
        writer = autosar.xml.Writer()
        xml = '''<QUEUED-RECEIVER-COM-SPEC>
  <QUEUE-LENGTH>1</QUEUE-LENGTH>
</QUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.QueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.QueuedReceiverComSpec)
        self.assertEqual(elem.queue_length, 1)


class TestNonqueuedReceiverComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.NonqueuedReceiverComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NONQUEUED-RECEIVER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)

    def test_alive_timeout(self):
        element = ar_element.NonqueuedReceiverComSpec(alive_timeout=2)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <ALIVE-TIMEOUT>2</ALIVE-TIMEOUT>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)

    def test_enable_update(self):
        element = ar_element.NonqueuedReceiverComSpec(enable_update=True)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <ENABLE-UPDATE>true</ENABLE-UPDATE>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertTrue(elem.enable_update)

    def test_data_filter(self):
        data_filter = ar_element.DataFilter(min_val=0, max_val=10)
        element = ar_element.NonqueuedReceiverComSpec(data_filter=data_filter)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <FILTER>
    <MAX>10</MAX>
    <MIN>0</MIN>
  </FILTER>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertIsInstance(elem.data_filter, ar_element.DataFilter)
        self.assertEqual(elem.data_filter.min_val, 0)
        self.assertEqual(elem.data_filter.max_val, 10)

    def test_handle_data_status(self):
        element = ar_element.NonqueuedReceiverComSpec(handle_data_status=True)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <HANDLE-DATA-STATUS>true</HANDLE-DATA-STATUS>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertTrue(elem.handle_data_status)

    def test_handle_never_received(self):
        element = ar_element.NonqueuedReceiverComSpec(handle_never_received=True)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <HANDLE-NEVER-RECEIVED>true</HANDLE-NEVER-RECEIVED>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertTrue(elem.handle_never_received)

    def test_handle_timeout_type(self):
        timeout_handling = ar_enum.HandleTimeout.REPLACE_BY_TIMEOUT_SUBSTITUTION_VALUE
        element = ar_element.NonqueuedReceiverComSpec(handle_timeout_type=timeout_handling)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <HANDLE-TIMEOUT-TYPE>REPLACE-BY-TIMEOUT-SUBSTITUTION-VALUE</HANDLE-TIMEOUT-TYPE>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertEqual(elem.handle_timeout_type, timeout_handling)

    def test_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=0)
        element = ar_element.NonqueuedReceiverComSpec(init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>0</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </INIT-VALUE>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertIsInstance(elem.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.init_value.value, 0)

    def test_timeout_substitution_value(self):
        timeout_substitution_value = ar_element.NumericalValueSpecification(value=3)
        element = ar_element.NonqueuedReceiverComSpec(timeout_substitution_value=timeout_substitution_value)
        writer = autosar.xml.Writer()
        xml = '''<NONQUEUED-RECEIVER-COM-SPEC>
  <TIMEOUT-SUBSTITUTION-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>3</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </TIMEOUT-SUBSTITUTION-VALUE>
</NONQUEUED-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NonqueuedReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NonqueuedReceiverComSpec)
        self.assertIsInstance(elem.timeout_substitution_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.timeout_substitution_value.value, 3)


class TestNvRequireComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.NvRequireComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<NV-REQUIRE-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.NvRequireComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvRequireComSpec)

    def test_variable_ref_from_object(self):
        variable_ref = ar_element.VariableDataPrototypeRef("/PortInterfaces/NvDataInterface/Data")
        element = ar_element.NvRequireComSpec(variable_ref=variable_ref)
        writer = autosar.xml.Writer()
        xml = '''<NV-REQUIRE-COM-SPEC>
  <VARIABLE-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/NvDataInterface/Data</VARIABLE-REF>
</NV-REQUIRE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvRequireComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvRequireComSpec)
        self.assertEqual(str(elem.variable_ref), "/PortInterfaces/NvDataInterface/Data")

    def test_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=255)
        element = ar_element.NvRequireComSpec(init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<NV-REQUIRE-COM-SPEC>
  <INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>255</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </INIT-VALUE>
</NV-REQUIRE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvRequireComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvRequireComSpec)
        self.assertIsInstance(elem.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.init_value.value, 255)


class TestParameterRequireComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ParameterRequireComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<PARAMETER-REQUIRE-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterRequireComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterRequireComSpec)

    def test_variable_ref_from_object(self):
        parameter_ref = ar_element.ParameterDataPrototypeRef("/PortInterfaces/ParameterInterface/Value")
        element = ar_element.ParameterRequireComSpec(parameter_ref=parameter_ref)
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-REQUIRE-COM-SPEC>
  <PARAMETER-REF DEST="PARAMETER-DATA-PROTOTYPE">/PortInterfaces/ParameterInterface/Value</PARAMETER-REF>
</PARAMETER-REQUIRE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterRequireComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterRequireComSpec)
        self.assertEqual(str(elem.parameter_ref), "/PortInterfaces/ParameterInterface/Value")

    def test_init_value(self):
        init_value = ar_element.NumericalValueSpecification(value=7)
        element = ar_element.ParameterRequireComSpec(init_value=init_value)
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-REQUIRE-COM-SPEC>
  <INIT-VALUE>
    <NUMERICAL-VALUE-SPECIFICATION>
      <VALUE>7</VALUE>
    </NUMERICAL-VALUE-SPECIFICATION>
  </INIT-VALUE>
</PARAMETER-REQUIRE-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterRequireComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterRequireComSpec)
        self.assertIsInstance(elem.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(elem.init_value.value, 7)


class TestModeSwitchReceiverComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ModeSwitchReceiverComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<MODE-SWITCH-RECEIVER-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchReceiverComSpec)

    def test_enhanced_mode_api(self):
        element = ar_element.ModeSwitchReceiverComSpec(enhanced_mode_api=True)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-RECEIVER-COM-SPEC>
  <ENHANCED-MODE-API>true</ENHANCED-MODE-API>
</MODE-SWITCH-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchReceiverComSpec)
        self.assertTrue(elem.enhanced_mode_api)

    def test_mode_group_ref_from_str(self):
        element = ar_element.ModeSwitchReceiverComSpec(mode_group_ref="/PortInterfaces/InterfaceName/ModeName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-RECEIVER-COM-SPEC>
  <MODE-GROUP-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">/PortInterfaces/InterfaceName/ModeName</MODE-GROUP-REF>
</MODE-SWITCH-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchReceiverComSpec)
        self.assertIsInstance(elem.mode_group_ref, ar_element.ModeDeclarationGroupPrototypeRef)
        self.assertEqual(str(elem.mode_group_ref), "/PortInterfaces/InterfaceName/ModeName")

    def test_mode_group_ref_from_object(self):
        mode_group_ref = ar_element.ModeDeclarationGroupPrototypeRef("/PortInterfaces/InterfaceName/ModeName")
        element = ar_element.ModeSwitchReceiverComSpec(mode_group_ref=mode_group_ref)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-RECEIVER-COM-SPEC>
  <MODE-GROUP-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">/PortInterfaces/InterfaceName/ModeName</MODE-GROUP-REF>
</MODE-SWITCH-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchReceiverComSpec)
        self.assertIsInstance(elem.mode_group_ref, ar_element.ModeDeclarationGroupPrototypeRef)
        self.assertEqual(str(elem.mode_group_ref), "/PortInterfaces/InterfaceName/ModeName")

    def test_supports_async(self):
        element = ar_element.ModeSwitchReceiverComSpec(supports_async=True)
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-RECEIVER-COM-SPEC>
  <SUPPORTS-ASYNCHRONOUS-MODE-SWITCH>true</SUPPORTS-ASYNCHRONOUS-MODE-SWITCH>
</MODE-SWITCH-RECEIVER-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchReceiverComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchReceiverComSpec)
        self.assertTrue(elem.supports_async)


class TestClientComSpec(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ClientComSpec()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<CLIENT-COM-SPEC/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ClientComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientComSpec)

    def test_operation_ref_from_object(self):
        ref_str = "/PortInterfaces/ClientServerInterface1/Operation1"
        operation_ref = ar_element.ClientServerOperationRef(ref_str)
        element = ar_element.ClientComSpec(operation_ref=operation_ref)
        writer = autosar.xml.Writer()
        xml = f'''<CLIENT-COM-SPEC>
  <OPERATION-REF DEST="CLIENT-SERVER-OPERATION">{ref_str}</OPERATION-REF>
</CLIENT-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientComSpec)
        self.assertEqual(str(elem.operation_ref), ref_str)

    def test_operation_ref_from_str(self):
        ref_str = "/PortInterfaces/ClientServerInterface1/Operation1"
        element = ar_element.ClientComSpec(operation_ref=ref_str)
        writer = autosar.xml.Writer()
        xml = f'''<CLIENT-COM-SPEC>
  <OPERATION-REF DEST="CLIENT-SERVER-OPERATION">{ref_str}</OPERATION-REF>
</CLIENT-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientComSpec)
        self.assertEqual(str(elem.operation_ref), ref_str)

    def test_e2e_call_respone_timeout(self):
        element = ar_element.ClientComSpec(e2e_call_respone_timeout=1)
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-COM-SPEC>
  <END-TO-END-CALL-RESPONSE-TIMEOUT>1</END-TO-END-CALL-RESPONSE-TIMEOUT>
</CLIENT-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientComSpec)
        self.assertEqual(elem.e2e_call_respone_timeout, 1)

    def test_transformation_com_spec_props_single(self):
        com_spec_props = ar_element.EndToEndTransformationComSpecProps(disable_e2e_check=True)
        element = ar_element.ClientComSpec(transformation_com_spec_props=com_spec_props)
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-COM-SPEC>
  <TRANSFORMATION-COM-SPEC-PROPSS>
    <END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
      <DISABLE-END-TO-END-CHECK>true</DISABLE-END-TO-END-CHECK>
    </END-TO-END-TRANSFORMATION-COM-SPEC-PROPS>
  </TRANSFORMATION-COM-SPEC-PROPSS>
</CLIENT-COM-SPEC>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientComSpec = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientComSpec)
        self.assertEqual(len(elem.transformation_com_spec_props), 1)
        props = elem.transformation_com_spec_props[0]
        self.assertTrue(props.disable_e2e_check)


class TestProvidePortPrototype(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ProvidePortPrototype("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<P-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(elem.name, "ShortName")

    def test_com_spec(self):
        com_spec = ar_element.NonqueuedSenderComSpec(init_value=ar_element.ValueSpecification.make_value(7))
        element = ar_element.ProvidePortPrototype("ShortName", com_spec=com_spec)
        writer = autosar.xml.Writer()
        xml = '''<P-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PROVIDED-COM-SPECS>
    <NONQUEUED-SENDER-COM-SPEC>
      <INIT-VALUE>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>7</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
      </INIT-VALUE>
    </NONQUEUED-SENDER-COM-SPEC>
  </PROVIDED-COM-SPECS>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertIsInstance(elem.com_spec[0], ar_element.NonqueuedSenderComSpec)
        self.assertEqual(elem.com_spec[0].init_value.value, 7)

    def test_port_interface_ref(self):
        ref_str = "/PortInterfaces/InterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(ref_str,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        element = ar_element.ProvidePortPrototype("ShortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<P-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PROVIDED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{ref_str}</PROVIDED-INTERFACE-TREF>
</P-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ProvidePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ProvidePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), ref_str)


class TestRequirePortPrototype(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.RequirePortPrototype("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<R-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
</R-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RequirePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RequirePortPrototype)
        self.assertEqual(elem.name, "ShortName")

    def test_com_spec(self):
        com_spec = ar_element.NonqueuedReceiverComSpec(init_value=ar_element.ValueSpecification.make_value(3))
        element = ar_element.RequirePortPrototype("ShortName", com_spec=com_spec)
        writer = autosar.xml.Writer()
        xml = '''<R-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <REQUIRED-COM-SPECS>
    <NONQUEUED-RECEIVER-COM-SPEC>
      <INIT-VALUE>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>3</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
      </INIT-VALUE>
    </NONQUEUED-RECEIVER-COM-SPEC>
  </REQUIRED-COM-SPECS>
</R-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RequirePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RequirePortPrototype)
        self.assertIsInstance(elem.com_spec[0], ar_element.NonqueuedReceiverComSpec)
        self.assertEqual(elem.com_spec[0].init_value.value, 3)

    def test_port_interface_ref(self):
        ref_str = "/PortInterfaces/InterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(ref_str,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        element = ar_element.RequirePortPrototype("ShortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<R-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{ref_str}</REQUIRED-INTERFACE-TREF>
</R-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RequirePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RequirePortPrototype)
        self.assertEqual(str(elem.port_interface_ref), ref_str)

    def test_allow_unconnected(self):
        element = ar_element.RequirePortPrototype("ShortName", allow_unconnected=True)
        writer = autosar.xml.Writer()
        xml = '''<R-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <MAY-BE-UNCONNECTED>true</MAY-BE-UNCONNECTED>
</R-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RequirePortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RequirePortPrototype)
        self.assertTrue(elem.allow_unconnected)


class TestPRPortPrototype(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.PRPortPrototype("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<PR-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
</PR-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PRPortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PRPortPrototype)
        self.assertEqual(elem.name, "ShortName")

    def test_com_spec(self):
        provided_com_spec = ar_element.NonqueuedSenderComSpec(init_value=ar_element.ValueSpecification.make_value(3))
        required_com_spec = ar_element.NonqueuedReceiverComSpec(init_value=ar_element.ValueSpecification.make_value(3))
        element = ar_element.PRPortPrototype("ShortName",
                                             provided_com_spec=provided_com_spec,
                                             required_com_spec=required_com_spec)
        writer = autosar.xml.Writer()
        xml = '''<PR-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PROVIDED-COM-SPECS>
    <NONQUEUED-SENDER-COM-SPEC>
      <INIT-VALUE>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>3</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
      </INIT-VALUE>
    </NONQUEUED-SENDER-COM-SPEC>
  </PROVIDED-COM-SPECS>
  <REQUIRED-COM-SPECS>
    <NONQUEUED-RECEIVER-COM-SPEC>
      <INIT-VALUE>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>3</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
      </INIT-VALUE>
    </NONQUEUED-RECEIVER-COM-SPEC>
  </REQUIRED-COM-SPECS>
</PR-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PRPortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PRPortPrototype)
        self.assertIsInstance(elem.provided_com_spec[0], ar_element.NonqueuedSenderComSpec)
        self.assertEqual(elem.provided_com_spec[0].init_value.value, 3)
        self.assertIsInstance(elem.required_com_spec[0], ar_element.NonqueuedReceiverComSpec)
        self.assertEqual(elem.required_com_spec[0].init_value.value, 3)

    def test_port_interface_ref(self):
        ref_str = "/PortInterfaces/InterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(ref_str,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        element = ar_element.PRPortPrototype("ShortName", port_interface_ref=port_interface_ref)
        writer = autosar.xml.Writer()
        xml = f'''<PR-PORT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PROVIDED-REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{ref_str}</PROVIDED-REQUIRED-INTERFACE-TREF>
</PR-PORT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PRPortPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PRPortPrototype)
        self.assertEqual(str(elem.port_interface_ref), ref_str)


class TestApplicationSoftwareComponentType(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ApplicationSoftwareComponentType("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
</APPLICATION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationSoftwareComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationSoftwareComponentType)
        self.assertEqual(elem.name, "ShortName")

    def test_internal_behavior(self):
        internal_behavior = ar_element.SwcInternalBehavior("BehaviorName")
        element = ar_element.ApplicationSoftwareComponentType("ShortName",
                                                              internal_behavior=internal_behavior)
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <INTERNAL-BEHAVIORS>
    <SWC-INTERNAL-BEHAVIOR>
      <SHORT-NAME>BehaviorName</SHORT-NAME>
    </SWC-INTERNAL-BEHAVIOR>
  </INTERNAL-BEHAVIORS>
</APPLICATION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationSoftwareComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationSoftwareComponentType)
        self.assertIsInstance(elem.internal_behavior, ar_element.SwcInternalBehavior)
        self.assertEqual(elem.internal_behavior.name, "BehaviorName")

    def test_symbol_props(self):
        symbol_props = ar_element.SymbolProps("PropsName", "Symbol")
        element = ar_element.ApplicationSoftwareComponentType("ShortName",
                                                              symbol_props=symbol_props)
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <SYMBOL-PROPS>
    <SHORT-NAME>PropsName</SHORT-NAME>
    <SYMBOL>Symbol</SYMBOL>
  </SYMBOL-PROPS>
</APPLICATION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationSoftwareComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationSoftwareComponentType)
        self.assertIsInstance(elem.symbol_props, ar_element.SymbolProps)
        self.assertEqual(elem.symbol_props.symbol, "Symbol")

    def test_single_require_port(self):
        ref_str = "/PortInterfaces/InterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(ref_str,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port = ar_element.RequirePortPrototype("PortName", port_interface_ref=port_interface_ref)
        element = ar_element.ApplicationSoftwareComponentType("ShortName",
                                                              ports=port)
        writer = autosar.xml.Writer()
        xml = f'''<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PORTS>
    <R-PORT-PROTOTYPE>
      <SHORT-NAME>PortName</SHORT-NAME>
      <REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{ref_str}</REQUIRED-INTERFACE-TREF>
    </R-PORT-PROTOTYPE>
  </PORTS>
</APPLICATION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationSoftwareComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationSoftwareComponentType)
        self.assertIsInstance(elem.ports[0], ar_element.RequirePortPrototype)
        self.assertEqual(elem.ports[0].name, "PortName")
        self.assertEqual(str(elem.ports[0].port_interface_ref), ref_str)

    def test_single_provide_port(self):
        ref_str = "/PortInterfaces/InterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(ref_str,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port = ar_element.ProvidePortPrototype("PortName", port_interface_ref=port_interface_ref)
        element = ar_element.ApplicationSoftwareComponentType("ShortName",
                                                              ports=port)
        writer = autosar.xml.Writer()
        xml = f'''<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PORTS>
    <P-PORT-PROTOTYPE>
      <SHORT-NAME>PortName</SHORT-NAME>
      <PROVIDED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{ref_str}</PROVIDED-INTERFACE-TREF>
    </P-PORT-PROTOTYPE>
  </PORTS>
</APPLICATION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationSoftwareComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationSoftwareComponentType)
        self.assertIsInstance(elem.ports[0], ar_element.ProvidePortPrototype)
        self.assertEqual(elem.ports[0].name, "PortName")
        self.assertEqual(str(elem.ports[0].port_interface_ref), ref_str)

    def test_single_pr_port(self):
        ref_str = "/PortInterfaces/InterfaceName"
        port_interface_ref = ar_element.PortInterfaceRef(ref_str,
                                                         ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port = ar_element.PRPortPrototype("PortName", port_interface_ref=port_interface_ref)
        element = ar_element.ApplicationSoftwareComponentType("ShortName",
                                                              ports=port)
        writer = autosar.xml.Writer()
        xml = f'''<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PORTS>
    <PR-PORT-PROTOTYPE>
      <SHORT-NAME>PortName</SHORT-NAME>
      <PROVIDED-REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">{ref_str}</PROVIDED-REQUIRED-INTERFACE-TREF>
    </PR-PORT-PROTOTYPE>
  </PORTS>
</APPLICATION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationSoftwareComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationSoftwareComponentType)
        self.assertIsInstance(elem.ports[0], ar_element.PRPortPrototype)
        self.assertEqual(elem.ports[0].name, "PortName")
        self.assertEqual(str(elem.ports[0].port_interface_ref), ref_str)

    def test_provide_port_iterator(self):
        ref_str1 = "/PortInterfaces/InterfaceName1"
        ref_str2 = "/PortInterfaces/InterfaceName2"
        ref_str3 = "/PortInterfaces/InterfaceName3"
        port_interface_ref1 = ar_element.PortInterfaceRef(ref_str1,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port_interface_ref2 = ar_element.PortInterfaceRef(ref_str2,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port_interface_ref3 = ar_element.PortInterfaceRef(ref_str3,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port1 = ar_element.RequirePortPrototype("RequirePort", port_interface_ref=port_interface_ref1)
        port2 = ar_element.ProvidePortPrototype("ProvidePort", port_interface_ref=port_interface_ref2)
        port3 = ar_element.PRPortPrototype("PRPort", port_interface_ref=port_interface_ref3)
        element = ar_element.ApplicationSoftwareComponentType("ShortName", ports=[port1, port2, port3])
        ports = list(element.provide_ports)
        self.assertEqual(len(ports), 1)
        port = ports[0]
        self.assertIsInstance(port, ar_element.ProvidePortPrototype)
        self.assertEqual(port.name, "ProvidePort")

    def test_require_port_iterator(self):
        ref_str1 = "/PortInterfaces/InterfaceName1"
        ref_str2 = "/PortInterfaces/InterfaceName2"
        ref_str3 = "/PortInterfaces/InterfaceName3"
        port_interface_ref1 = ar_element.PortInterfaceRef(ref_str1,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port_interface_ref2 = ar_element.PortInterfaceRef(ref_str2,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port_interface_ref3 = ar_element.PortInterfaceRef(ref_str3,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port1 = ar_element.RequirePortPrototype("RequirePort", port_interface_ref=port_interface_ref1)
        port2 = ar_element.ProvidePortPrototype("ProvidePort", port_interface_ref=port_interface_ref2)
        port3 = ar_element.PRPortPrototype("PRPort", port_interface_ref=port_interface_ref3)
        element = ar_element.ApplicationSoftwareComponentType("ShortName", ports=[port1, port2, port3])
        ports = list(element.require_ports)
        self.assertEqual(len(ports), 1)
        port = ports[0]
        self.assertIsInstance(port, ar_element.RequirePortPrototype)
        self.assertEqual(port.name, "RequirePort")

    def test_pr_port_iterator(self):
        ref_str1 = "/PortInterfaces/InterfaceName1"
        ref_str2 = "/PortInterfaces/InterfaceName2"
        ref_str3 = "/PortInterfaces/InterfaceName3"
        port_interface_ref1 = ar_element.PortInterfaceRef(ref_str1,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port_interface_ref2 = ar_element.PortInterfaceRef(ref_str2,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port_interface_ref3 = ar_element.PortInterfaceRef(ref_str3,
                                                          ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)
        port1 = ar_element.RequirePortPrototype("RequirePort", port_interface_ref=port_interface_ref1)
        port2 = ar_element.ProvidePortPrototype("ProvidePort", port_interface_ref=port_interface_ref2)
        port3 = ar_element.PRPortPrototype("PRPort", port_interface_ref=port_interface_ref3)
        element = ar_element.ApplicationSoftwareComponentType("ShortName", ports=[port1, port2, port3])
        ports = list(element.pr_ports)
        self.assertEqual(len(ports), 1)
        port = ports[0]
        self.assertIsInstance(port, ar_element.PRPortPrototype)
        self.assertEqual(port.name, "PRPort")


class TestSwComponentPrototype(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.SwComponentPrototype("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<SW-COMPONENT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
</SW-COMPONENT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwComponentPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwComponentPrototype)
        self.assertEqual(elem.name, "ShortName")

    def test_type_ref(self):
        ref_str = "/ComponentTypes/ApplicationComponent"
        type_ref = ar_element.SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE)
        element = ar_element.SwComponentPrototype("ShortName", type_ref=type_ref)
        writer = autosar.xml.Writer()
        xml = f'''<SW-COMPONENT-PROTOTYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <TYPE-TREF DEST="APPLICATION-SW-COMPONENT-TYPE">{ref_str}</TYPE-TREF>
</SW-COMPONENT-PROTOTYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwComponentPrototype = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwComponentPrototype)
        self.assertEqual(str(elem.type_ref), ref_str)
        self.assertEqual(elem.type_ref.dest, ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE)


class TestPortInCompositionTypeInstanceRef(unittest.TestCase):

    def test_empty_provider(self):
        element = ar_element.PortInCompositionTypeInstanceRef()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, "PROVIDER-IREF")
        self.assertEqual(xml, '<PROVIDER-IREF/>')
        reader = autosar.xml.Reader()
        elem: ar_element.PortInCompositionTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PortInCompositionTypeInstanceRef)

    def test_empty_requester(self):
        element = ar_element.PortInCompositionTypeInstanceRef()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, "REQUESTER-IREF")
        self.assertEqual(xml, '<REQUESTER-IREF/>')
        reader = autosar.xml.Reader()
        elem: ar_element.PortInCompositionTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PortInCompositionTypeInstanceRef)

    def test_component_ref(self):
        ref_str = "ComponentTypes/Composition/ComponentName"
        component_ref = ar_element.SwComponentPrototypeRef(ref_str)
        element = ar_element.PortInCompositionTypeInstanceRef(component_ref=component_ref)
        writer = autosar.xml.Writer()
        xml = f'''<PROVIDER-IREF>
  <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{ref_str}</CONTEXT-COMPONENT-REF>
</PROVIDER-IREF>'''
        self.assertEqual(writer.write_str_elem(element, "PROVIDER-IREF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PortInCompositionTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem.component_ref, ar_element.SwComponentPrototypeRef)
        self.assertEqual(str(elem.component_ref), ref_str)

    def test_provider_port_ref(self):
        ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        element = ar_element.PortInCompositionTypeInstanceRef(port_ref=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<PROVIDER-IREF>
  <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">{ref_str}</TARGET-P-PORT-REF>
</PROVIDER-IREF>'''
        self.assertEqual(writer.write_str_elem(element, "PROVIDER-IREF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PortInCompositionTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem.port_ref, ar_element.PortPrototypeRef)
        self.assertEqual(str(elem.port_ref), ref_str)
        self.assertEqual(elem.port_ref.dest, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)

    def test_requester_port_ref(self):
        ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        element = ar_element.PortInCompositionTypeInstanceRef(port_ref=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<REQUESTER-IREF>
  <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">{ref_str}</TARGET-R-PORT-REF>
</REQUESTER-IREF>'''
        self.assertEqual(writer.write_str_elem(element, "REQUESTER-IREF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PortInCompositionTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem.port_ref, ar_element.PortPrototypeRef)
        self.assertEqual(str(elem.port_ref), ref_str)
        self.assertEqual(elem.port_ref.dest, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)

    def test_requester_pr_port_ref(self):
        ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE)
        element = ar_element.PortInCompositionTypeInstanceRef(port_ref=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<REQUESTER-IREF>
  <TARGET-R-PORT-REF DEST="PR-PORT-PROTOTYPE">{ref_str}</TARGET-R-PORT-REF>
</REQUESTER-IREF>'''
        self.assertEqual(writer.write_str_elem(element, "REQUESTER-IREF"), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PortInCompositionTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem.port_ref, ar_element.PortPrototypeRef)
        self.assertEqual(str(elem.port_ref), ref_str)
        self.assertEqual(elem.port_ref.dest, ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE)


class TestAssemblySwConnector(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.AssemblySwConnector("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<ASSEMBLY-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
</ASSEMBLY-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AssemblySwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AssemblySwConnector)
        self.assertEqual(elem.name, "ShortName")

    def test_provide_port(self):
        component_ref_str = "ComponentTypes/Composition/ComponentName"
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        component_ref = ar_element.SwComponentPrototypeRef(component_ref_str)
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        port_instance = ar_element.PortInCompositionTypeInstanceRef(component_ref=component_ref,
                                                                    port_ref=port_ref)
        element = ar_element.AssemblySwConnector("ShortName", provide_port=port_instance)
        writer = autosar.xml.Writer()
        xml = f'''<ASSEMBLY-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PROVIDER-IREF>
    <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component_ref_str}</CONTEXT-COMPONENT-REF>
    <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">{port_ref_str}</TARGET-P-PORT-REF>
  </PROVIDER-IREF>
</ASSEMBLY-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AssemblySwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AssemblySwConnector)
        self.assertIsInstance(elem.provide_port, ar_element.PortInCompositionTypeInstanceRef)

    def test_require_port(self):
        component_ref_str = "ComponentTypes/Composition/ComponentName"
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        component_ref = ar_element.SwComponentPrototypeRef(component_ref_str)
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        port_instance = ar_element.PortInCompositionTypeInstanceRef(component_ref=component_ref,
                                                                    port_ref=port_ref)
        element = ar_element.AssemblySwConnector("ShortName", require_port=port_instance)
        writer = autosar.xml.Writer()
        xml = f'''<ASSEMBLY-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <REQUESTER-IREF>
    <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component_ref_str}</CONTEXT-COMPONENT-REF>
    <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">{port_ref_str}</TARGET-R-PORT-REF>
  </REQUESTER-IREF>
</ASSEMBLY-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AssemblySwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AssemblySwConnector)
        self.assertIsInstance(elem.require_port, ar_element.PortInCompositionTypeInstanceRef)


class TestDelegationSwConnector(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.DelegationSwConnector("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
</DELEGATION-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DelegationSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DelegationSwConnector)
        self.assertEqual(elem.name, "ShortName")

    def test_inner_port_with_provide_port(self):
        component_ref_str = "ComponentTypes/Composition/ComponentName"
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        component_ref = ar_element.SwComponentPrototypeRef(component_ref_str)
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        port_instance = ar_element.PortInCompositionTypeInstanceRef(component_ref=component_ref,
                                                                    port_ref=port_ref)
        element = ar_element.DelegationSwConnector("ShortName", inner_port=port_instance)
        writer = autosar.xml.Writer()
        xml = f'''<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <INNER-PORT-IREF>
    <P-PORT-IN-COMPOSITION-INSTANCE-REF>
      <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component_ref_str}</CONTEXT-COMPONENT-REF>
      <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">{port_ref_str}</TARGET-P-PORT-REF>
    </P-PORT-IN-COMPOSITION-INSTANCE-REF>
  </INNER-PORT-IREF>
</DELEGATION-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DelegationSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DelegationSwConnector)
        self.assertIsInstance(elem.inner_port, ar_element.PortInCompositionTypeInstanceRef)
        self.assertEqual(str(elem.inner_port.port_ref), port_ref_str)

    def test_inner_port_with_require_port(self):
        component_ref_str = "ComponentTypes/Composition/ComponentName"
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        component_ref = ar_element.SwComponentPrototypeRef(component_ref_str)
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        port_instance = ar_element.PortInCompositionTypeInstanceRef(component_ref=component_ref,
                                                                    port_ref=port_ref)
        element = ar_element.DelegationSwConnector("ShortName", inner_port=port_instance)
        writer = autosar.xml.Writer()
        xml = f'''<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <INNER-PORT-IREF>
    <R-PORT-IN-COMPOSITION-INSTANCE-REF>
      <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component_ref_str}</CONTEXT-COMPONENT-REF>
      <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">{port_ref_str}</TARGET-R-PORT-REF>
    </R-PORT-IN-COMPOSITION-INSTANCE-REF>
  </INNER-PORT-IREF>
</DELEGATION-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DelegationSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DelegationSwConnector)
        self.assertIsInstance(elem.inner_port, ar_element.PortInCompositionTypeInstanceRef)
        self.assertEqual(str(elem.inner_port.port_ref), port_ref_str)

    def test_outer_port_with_provide_port(self):
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        element = ar_element.DelegationSwConnector("ShortName", outer_port=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <OUTER-PORT-REF DEST="P-PORT-PROTOTYPE">{port_ref_str}</OUTER-PORT-REF>
</DELEGATION-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DelegationSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DelegationSwConnector)
        self.assertIsInstance(elem.outer_port, ar_element.PortPrototypeRef)
        self.assertEqual(str(elem.outer_port), port_ref_str)

    def test_outer_port_with_require_port(self):
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        element = ar_element.DelegationSwConnector("ShortName", outer_port=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <OUTER-PORT-REF DEST="R-PORT-PROTOTYPE">{port_ref_str}</OUTER-PORT-REF>
</DELEGATION-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.DelegationSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.DelegationSwConnector)
        self.assertIsInstance(elem.outer_port, ar_element.PortPrototypeRef)
        self.assertEqual(str(elem.outer_port), port_ref_str)


class TestPassThroughSwConnector(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.PassThroughSwConnector("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<PASS-THROUGH-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
</PASS-THROUGH-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PassThroughSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PassThroughSwConnector)
        self.assertEqual(elem.name, "ShortName")

    def test_provide_port(self):
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        element = ar_element.PassThroughSwConnector("ShortName", provide_port=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<PASS-THROUGH-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <PROVIDED-OUTER-PORT-REF DEST="P-PORT-PROTOTYPE">{port_ref_str}</PROVIDED-OUTER-PORT-REF>
</PASS-THROUGH-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PassThroughSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PassThroughSwConnector)
        self.assertIsInstance(elem.provide_port, ar_element.PortPrototypeRef)
        self.assertEqual(elem.provide_port.dest, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)

    def test_require_port(self):
        port_ref_str = "ComponentTypes/ComponentName/PortName"
        port_ref = ar_element.PortPrototypeRef(port_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        element = ar_element.PassThroughSwConnector("ShortName", require_port=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<PASS-THROUGH-SW-CONNECTOR>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <REQUIRED-OUTER-PORT-REF DEST="R-PORT-PROTOTYPE">{port_ref_str}</REQUIRED-OUTER-PORT-REF>
</PASS-THROUGH-SW-CONNECTOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.PassThroughSwConnector = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.PassThroughSwConnector)
        self.assertIsInstance(elem.require_port, ar_element.PortPrototypeRef)
        self.assertEqual(elem.require_port.dest, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)


class TestCompositionSwComponentType(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.CompositionSwComponentType("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<COMPOSITION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
</COMPOSITION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositionSwComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositionSwComponentType)
        self.assertEqual(elem.name, "ShortName")

    def test_component_single(self):
        component = ar_element.SwComponentPrototype("ComponentName")
        element = ar_element.CompositionSwComponentType("ShortName", components=component)
        writer = autosar.xml.Writer()
        xml = '''<COMPOSITION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <COMPONENTS>
    <SW-COMPONENT-PROTOTYPE>
      <SHORT-NAME>ComponentName</SHORT-NAME>
    </SW-COMPONENT-PROTOTYPE>
  </COMPONENTS>
</COMPOSITION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositionSwComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositionSwComponentType)
        self.assertEqual(len(elem.components), 1)
        self.assertEqual(elem.components[0].name, "ComponentName")

    def test_assembly_connector(self):
        component1_ref_str = "ComponentTypes/ShortName/Component1"
        component2_ref_str = "ComponentTypes/ShortName/Component2"
        port1_ref_str = "ComponentTypes/Component1/PortName"
        port2_ref_str = "ComponentTypes/Component2/PortName"
        component1_ref = ar_element.SwComponentPrototypeRef(component1_ref_str)
        component2_ref = ar_element.SwComponentPrototypeRef(component2_ref_str)
        port1_ref = ar_element.PortPrototypeRef(port1_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        port2_ref = ar_element.PortPrototypeRef(port2_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        port_instance1 = ar_element.PortInCompositionTypeInstanceRef(component_ref=component1_ref,
                                                                     port_ref=port1_ref)
        port_instance2 = ar_element.PortInCompositionTypeInstanceRef(component_ref=component2_ref,
                                                                     port_ref=port2_ref)
        connector = ar_element.AssemblySwConnector("ConnectorName",
                                                   provide_port=port_instance1,
                                                   require_port=port_instance2)
        element = ar_element.CompositionSwComponentType("ShortName", connectors=connector)
        writer = autosar.xml.Writer()
        xml = f'''<COMPOSITION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <CONNECTORS>
    <ASSEMBLY-SW-CONNECTOR>
      <SHORT-NAME>ConnectorName</SHORT-NAME>
      <PROVIDER-IREF>
        <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component1_ref_str}</CONTEXT-COMPONENT-REF>
        <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">{port1_ref_str}</TARGET-P-PORT-REF>
      </PROVIDER-IREF>
      <REQUESTER-IREF>
        <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component2_ref_str}</CONTEXT-COMPONENT-REF>
        <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">{port2_ref_str}</TARGET-R-PORT-REF>
      </REQUESTER-IREF>
    </ASSEMBLY-SW-CONNECTOR>
  </CONNECTORS>
</COMPOSITION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositionSwComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositionSwComponentType)
        self.assertEqual(len(elem.connectors), 1)
        self.assertIsInstance(elem.connectors[0], ar_element.AssemblySwConnector)

    def test_delegation_connector(self):
        component1_ref_str = "ComponentTypes/ShortName/Component1"
        port1_ref_str = "ComponentTypes/Component1/PortName"
        port2_ref_str = "ComponentTypes/ShortName/PortName"
        component1_ref = ar_element.SwComponentPrototypeRef(component1_ref_str)
        port1_ref = ar_element.PortPrototypeRef(port1_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        port2_ref = ar_element.PortPrototypeRef(port2_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        port_instance1 = ar_element.PortInCompositionTypeInstanceRef(component_ref=component1_ref,
                                                                     port_ref=port1_ref)
        connector = ar_element.DelegationSwConnector("ConnectorName",
                                                     inner_port=port_instance1,
                                                     outer_port=port2_ref)
        element = ar_element.CompositionSwComponentType("ShortName", connectors=connector)
        writer = autosar.xml.Writer()
        xml = f'''<COMPOSITION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <CONNECTORS>
    <DELEGATION-SW-CONNECTOR>
      <SHORT-NAME>ConnectorName</SHORT-NAME>
      <INNER-PORT-IREF>
        <P-PORT-IN-COMPOSITION-INSTANCE-REF>
          <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">{component1_ref_str}</CONTEXT-COMPONENT-REF>
          <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">{port1_ref_str}</TARGET-P-PORT-REF>
        </P-PORT-IN-COMPOSITION-INSTANCE-REF>
      </INNER-PORT-IREF>
      <OUTER-PORT-REF DEST="R-PORT-PROTOTYPE">{port2_ref_str}</OUTER-PORT-REF>
    </DELEGATION-SW-CONNECTOR>
  </CONNECTORS>
</COMPOSITION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositionSwComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositionSwComponentType)
        self.assertEqual(len(elem.connectors), 1)
        connector = elem.connectors[0]
        self.assertIsInstance(elem.connectors[0], ar_element.DelegationSwConnector)

    def test_pass_through_connector(self):
        port1_ref_str = "ComponentTypes/Component1/PortName"
        port2_ref_str = "ComponentTypes/ShortName/PortName"
        port1_ref = ar_element.PortPrototypeRef(port1_ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)
        port2_ref = ar_element.PortPrototypeRef(port2_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        connector = ar_element.PassThroughSwConnector("ConnectorName",
                                                      provide_port=port1_ref,
                                                      require_port=port2_ref)
        element = ar_element.CompositionSwComponentType("ShortName", connectors=connector)
        writer = autosar.xml.Writer()
        xml = f'''<COMPOSITION-SW-COMPONENT-TYPE>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <CONNECTORS>
    <PASS-THROUGH-SW-CONNECTOR>
      <SHORT-NAME>ConnectorName</SHORT-NAME>
      <PROVIDED-OUTER-PORT-REF DEST="P-PORT-PROTOTYPE">{port1_ref_str}</PROVIDED-OUTER-PORT-REF>
      <REQUIRED-OUTER-PORT-REF DEST="R-PORT-PROTOTYPE">{port2_ref_str}</REQUIRED-OUTER-PORT-REF>
    </PASS-THROUGH-SW-CONNECTOR>
  </CONNECTORS>
</COMPOSITION-SW-COMPONENT-TYPE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.CompositionSwComponentType = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.CompositionSwComponentType)
        self.assertEqual(len(elem.connectors), 1)
        connector = elem.connectors[0]
        self.assertIsInstance(elem.connectors[0], ar_element.PassThroughSwConnector)


class TestSwcImplementation(unittest.TestCase):
    """
    Also tests group AR:IMPLEMENTATION
    """

    def test_name_only(self):
        element = ar_element.SwcImplementation("ShortName")
        writer = autosar.xml.Writer()
        xml = '''<SWC-IMPLEMENTATION>
  <SHORT-NAME>ShortName</SHORT-NAME>
</SWC-IMPLEMENTATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcImplementation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcImplementation)
        self.assertEqual(elem.name, "ShortName")

    def test_code_descriptor(self):
        descriptor = ar_element.AutosarEngineeringObject(label="Default", category="SWSRC")
        code = ar_element.Code("Default", artifact_descriptors=descriptor)
        element = ar_element.SwcImplementation("ShortName", code_descriptors=code)
        writer = autosar.xml.Writer()
        xml = '''<SWC-IMPLEMENTATION>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <CODE-DESCRIPTORS>
    <CODE>
      <SHORT-NAME>Default</SHORT-NAME>
      <ARTIFACT-DESCRIPTORS>
        <AUTOSAR-ENGINEERING-OBJECT>
          <SHORT-LABEL>Default</SHORT-LABEL>
          <CATEGORY>SWSRC</CATEGORY>
        </AUTOSAR-ENGINEERING-OBJECT>
      </ARTIFACT-DESCRIPTORS>
    </CODE>
  </CODE-DESCRIPTORS>
</SWC-IMPLEMENTATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcImplementation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcImplementation)
        self.assertEqual(len(elem.code_descriptors), 1)
        code_descriptor = elem.code_descriptors[0]
        self.assertEqual(len(code_descriptor.artifact_descriptors), 1)
        artifact_descriptor = code_descriptor.artifact_descriptors[0]
        self.assertEqual(artifact_descriptor.label, "Default")
        self.assertEqual(artifact_descriptor.category, "SWSRC")

    def test_behavior_ref(self):
        ref_str = "/ComponentTypes/Component/Behavior"
        element = ar_element.SwcImplementation("ShortName", behavior_ref=ref_str)
        writer = autosar.xml.Writer()
        xml = f'''<SWC-IMPLEMENTATION>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <BEHAVIOR-REF DEST="SWC-INTERNAL-BEHAVIOR">{ref_str}</BEHAVIOR-REF>
</SWC-IMPLEMENTATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcImplementation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcImplementation)
        self.assertEqual(str(elem.behavior_ref), ref_str)

    def test_required_rte_vendor(self):
        vendor_name = "VendorName"
        element = ar_element.SwcImplementation("ShortName", required_rte_vendor=vendor_name)
        writer = autosar.xml.Writer()
        xml = f'''<SWC-IMPLEMENTATION>
  <SHORT-NAME>ShortName</SHORT-NAME>
  <REQUIRED-RTE-VENDOR>{vendor_name}</REQUIRED-RTE-VENDOR>
</SWC-IMPLEMENTATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcImplementation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcImplementation)
        self.assertEqual(str(elem.required_rte_vendor), vendor_name)


if __name__ == '__main__':
    unittest.main()
