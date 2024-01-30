"""Unit tests for port interface"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestInvalidationPolicy(unittest.TestCase):

    def test_empty(self):
        element = ar_element.InvalidationPolicy()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<INVALIDATION-POLICY/>')
        reader = autosar.xml.Reader()
        elem: ar_element.InvalidationPolicy = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InvalidationPolicy)

    def test_data_element_ref(self):
        element = ar_element.InvalidationPolicy(data_element_ref="/PortInterfaces/InterfaceName/ElementName")
        writer = autosar.xml.Writer()
        xml = '''<INVALIDATION-POLICY>
  <DATA-ELEMENT-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/InterfaceName/ElementName</DATA-ELEMENT-REF>
</INVALIDATION-POLICY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.InvalidationPolicy = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InvalidationPolicy)
        self.assertEqual(str(elem.data_element_ref), "/PortInterfaces/InterfaceName/ElementName")

    def test_handle_invalid(self):
        element = ar_element.InvalidationPolicy(handle_invalid=ar_enum.HandleInvalid.EXTERNAL_REPLACEMENT)
        writer = autosar.xml.Writer()
        xml = '''<INVALIDATION-POLICY>
  <HANDLE-INVALID>EXTERNAL-REPLACEMENT</HANDLE-INVALID>
</INVALIDATION-POLICY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.InvalidationPolicy = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InvalidationPolicy)
        self.assertEqual(elem.handle_invalid, ar_enum.HandleInvalid.EXTERNAL_REPLACEMENT)


class TestSenderReceiverInterface(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.SenderReceiverInterface("InterfaceName")
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")

    def test_create_interface_with_one_element_using_constructor(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("InterfaceName",
                                                     ar_element.VariableDataPrototype("Element1",
                                                                                      type_ref=ref_to_uint8_type))

        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 1)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Element1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")

    def test_create_interface_with_two_elements_using_constructor(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        ref_to_uint16_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint16",
                                                           ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("InterfaceName", [
            ar_element.VariableDataPrototype("Element1", type_ref=ref_to_uint8_type),
            ar_element.VariableDataPrototype("Element2", type_ref=ref_to_uint16_type)
        ])
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 2)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Element1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")
        data_element = elem.data_elements[1]
        self.assertEqual(data_element.name, "Element2")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint16")

    def test_create_interface_with_one_element_using_make_method(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("InterfaceName")
        element.make_data_element("Element1", type_ref=ref_to_uint8_type)
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 1)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Element1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")

    def test_create_interface_with_two_elements_using_make_method(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        ref_to_uint16_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint16",
                                                           ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("InterfaceName")
        element.make_data_element("Element1", type_ref=ref_to_uint8_type)
        element.make_data_element("Element2", type_ref=ref_to_uint16_type)
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 2)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Element1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")
        data_element = elem.data_elements[1]
        self.assertEqual(data_element.name, "Element2")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint16")

    def test_make_element_with_invalidation_policy(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("InterfaceName")
        element.make_data_element("Element1", type_ref=ref_to_uint8_type)
        element.make_invalidation_policy("/PortInterfaces/InterfaceName/Element1",
                                         handle_invalid=ar_enum.HandleInvalid.REPLACE)
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
  <INVALIDATION-POLICYS>
    <INVALIDATION-POLICY>
      <DATA-ELEMENT-REF DEST="VARIABLE-DATA-PROTOTYPE">/PortInterfaces/InterfaceName/Element1</DATA-ELEMENT-REF>
      <HANDLE-INVALID>REPLACE</HANDLE-INVALID>
    </INVALIDATION-POLICY>
  </INVALIDATION-POLICYS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 1)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Element1")
        self.assertEqual(len(elem.invalidation_policies), 1)
        invalidataion_policy = elem.invalidation_policies[0]
        self.assertEqual(str(invalidataion_policy.data_element_ref), "/PortInterfaces/InterfaceName/Element1")
        self.assertEqual(invalidataion_policy.handle_invalid, ar_enum.HandleInvalid.REPLACE)

    def test_make_element_with_numerical_init_value(self):
        ref_to_impl_type = ar_element.AutosarDataTypeRef("DataTypes/OnOff_T",
                                                         ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("InterfaceName")
        element.make_data_element("Element1",
                                  init_value=ar_element.ValueSpecification.make_value(3),
                                  type_ref=ref_to_impl_type)
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">DataTypes/OnOff_T</TYPE-TREF>
      <INIT-VALUE>
        <NUMERICAL-VALUE-SPECIFICATION>
          <VALUE>3</VALUE>
        </NUMERICAL-VALUE-SPECIFICATION>
      </INIT-VALUE>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 1)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Element1")
        self.assertEqual(str(data_element.type_ref), "DataTypes/OnOff_T")
        init_value: ar_element.NumericalValueSpecification = data_element.init_value
        self.assertIsInstance(init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(init_value.value, 3)

    def test_create_service_interface_with_one_element_using_constructor(self):
        ref_to_impl_type = ar_element.AutosarDataTypeRef("DataTypes/OnOff_T",
                                                         ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("ServiceInterface",
                                                     ar_element.VariableDataPrototype("Element1",
                                                                                      type_ref=ref_to_impl_type),
                                                     is_service=True)
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>ServiceInterface</SHORT-NAME>
  <IS-SERVICE>true</IS-SERVICE>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">DataTypes/OnOff_T</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "ServiceInterface")
        self.assertTrue(elem.is_service)

    def test_create_service_interface_with_one_element_using_make_method(self):
        ref_to_impl_type = ar_element.AutosarDataTypeRef("DataTypes/OnOff_T",
                                                         ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.SenderReceiverInterface("ServiceInterface", is_service=True)
        element.make_data_element("Element1", type_ref=ref_to_impl_type)
        writer = autosar.xml.Writer()
        xml = '''<SENDER-RECEIVER-INTERFACE>
  <SHORT-NAME>ServiceInterface</SHORT-NAME>
  <IS-SERVICE>true</IS-SERVICE>
  <DATA-ELEMENTS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Element1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">DataTypes/OnOff_T</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </DATA-ELEMENTS>
</SENDER-RECEIVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SenderReceiverInterface)
        self.assertEqual(elem.name, "ServiceInterface")
        self.assertTrue(elem.is_service)


class TestNvDataInterface(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.NvDataInterface("InterfaceName")
        writer = autosar.xml.Writer()
        xml = '''<NV-DATA-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
</NV-DATA-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvDataInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvDataInterface)
        self.assertEqual(elem.name, "InterfaceName")

    def test_create_interface_with_one_element_using_constructor(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.NvDataInterface("InterfaceName",
                                             ar_element.VariableDataPrototype("Data1", type_ref=ref_to_uint8_type))
        writer = autosar.xml.Writer()
        xml = '''<NV-DATA-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <NV-DATAS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Data1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </NV-DATAS>
</NV-DATA-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvDataInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvDataInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 1)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Data1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")

    def test_create_interface_with_two_elements_using_constructor(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        ref_to_uint16_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint16",
                                                           ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.NvDataInterface("InterfaceName",
                                             [ar_element.VariableDataPrototype("Data1", type_ref=ref_to_uint8_type),
                                              ar_element.VariableDataPrototype("Data2", type_ref=ref_to_uint16_type)
                                              ])
        writer = autosar.xml.Writer()
        xml = '''<NV-DATA-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <NV-DATAS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Data1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Data2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </NV-DATAS>
</NV-DATA-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvDataInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvDataInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 2)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Data1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")
        data_element = elem.data_elements[1]
        self.assertEqual(data_element.name, "Data2")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint16")

    def test_create_interface_with_one_element_using_make_method(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.NvDataInterface("InterfaceName")
        element.make_data_element("Data1", type_ref=ref_to_uint8_type)
        writer = autosar.xml.Writer()
        xml = '''<NV-DATA-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <NV-DATAS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Data1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </NV-DATAS>
</NV-DATA-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvDataInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvDataInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 1)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Data1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")

    def test_create_interface_with_two_elements_using_make_method(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        ref_to_uint16_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint16",
                                                           ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.NvDataInterface("InterfaceName")
        element.make_data_element("Data1", type_ref=ref_to_uint8_type)
        element.make_data_element("Data2", type_ref=ref_to_uint16_type)

        writer = autosar.xml.Writer()
        xml = '''<NV-DATA-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <NV-DATAS>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Data1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
    <VARIABLE-DATA-PROTOTYPE>
      <SHORT-NAME>Data2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>
    </VARIABLE-DATA-PROTOTYPE>
  </NV-DATAS>
</NV-DATA-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.NvDataInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.NvDataInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.data_elements), 2)
        data_element = elem.data_elements[0]
        self.assertEqual(data_element.name, "Data1")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")
        data_element = elem.data_elements[1]
        self.assertEqual(data_element.name, "Data2")
        self.assertEqual(str(data_element.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint16")


class TestParameterInterface(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ParameterInterface("InterfaceName")
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
</PARAMETER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterInterface)
        self.assertEqual(elem.name, "InterfaceName")

    def test_create_interface_with_one_parameter_using_constructor(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.ParameterInterface("InterfaceName",
                                                ar_element.ParameterDataPrototype("Param1", type_ref=ref_to_uint8_type))
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <PARAMETERS>
    <PARAMETER-DATA-PROTOTYPE>
      <SHORT-NAME>Param1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </PARAMETER-DATA-PROTOTYPE>
  </PARAMETERS>
</PARAMETER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SenderReceiverInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.parameters), 1)
        parameter = elem.parameters[0]
        self.assertEqual(parameter.name, "Param1")
        self.assertEqual(str(parameter.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")

    def test_create_interface_with_two_parameters_using_constructor(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        ref_to_uint16_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint16",
                                                           ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.ParameterInterface("InterfaceName", [
            ar_element.ParameterDataPrototype("Param1", type_ref=ref_to_uint8_type),
            ar_element.ParameterDataPrototype("Param2", type_ref=ref_to_uint16_type)
        ])
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <PARAMETERS>
    <PARAMETER-DATA-PROTOTYPE>
      <SHORT-NAME>Param1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </PARAMETER-DATA-PROTOTYPE>
    <PARAMETER-DATA-PROTOTYPE>
      <SHORT-NAME>Param2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>
    </PARAMETER-DATA-PROTOTYPE>
  </PARAMETERS>
</PARAMETER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.parameters), 2)
        parameter = elem.parameters[0]
        self.assertEqual(parameter.name, "Param1")
        self.assertEqual(str(parameter.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")
        parameter = elem.parameters[1]
        self.assertEqual(parameter.name, "Param2")
        self.assertEqual(str(parameter.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint16")

    def test_create_interface_with_one_parameter_using_make_method(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.ParameterInterface("InterfaceName")
        element.make_parameter("Param1", type_ref=ref_to_uint8_type)
        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <PARAMETERS>
    <PARAMETER-DATA-PROTOTYPE>
      <SHORT-NAME>Param1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </PARAMETER-DATA-PROTOTYPE>
  </PARAMETERS>
</PARAMETER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.parameters), 1)
        parameter = elem.parameters[0]
        self.assertEqual(parameter.name, "Param1")
        self.assertEqual(str(parameter.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")

    def test_create_interface_with_two_parameters_using_make_method(self):
        ref_to_uint8_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint8",
                                                          ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        ref_to_uint16_type = ar_element.AutosarDataTypeRef("AUTOSAR_Platform/ImplementationDataTypes/uint16",
                                                           ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
        element = ar_element.ParameterInterface("InterfaceName")
        element.make_parameter("Param1", type_ref=ref_to_uint8_type)
        element.make_parameter("Param2", type_ref=ref_to_uint16_type)

        writer = autosar.xml.Writer()
        xml = '''<PARAMETER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <PARAMETERS>
    <PARAMETER-DATA-PROTOTYPE>
      <SHORT-NAME>Param1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint8</TYPE-TREF>
    </PARAMETER-DATA-PROTOTYPE>
    <PARAMETER-DATA-PROTOTYPE>
      <SHORT-NAME>Param2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>
    </PARAMETER-DATA-PROTOTYPE>
  </PARAMETERS>
</PARAMETER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ParameterInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ParameterInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.parameters), 2)
        parameter = elem.parameters[0]
        self.assertEqual(parameter.name, "Param1")
        self.assertEqual(str(parameter.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint8")
        parameter = elem.parameters[1]
        self.assertEqual(parameter.name, "Param2")
        self.assertEqual(str(parameter.type_ref), "AUTOSAR_Platform/ImplementationDataTypes/uint16")


if __name__ == '__main__':
    unittest.main()
