"""Unit tests for port interface"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402

IMPLEMENTATION_DATA_TYPE = ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE


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


class TestApplicationError(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ApplicationError("ErrorName")
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-ERROR>
  <SHORT-NAME>ErrorName</SHORT-NAME>
</APPLICATION-ERROR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationError = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationError)
        self.assertEqual(elem.name, "ErrorName")

    def test_error_code(self):
        element = ar_element.ApplicationError("ErrorName", error_code=10)
        writer = autosar.xml.Writer()
        xml = '''<APPLICATION-ERROR>
  <SHORT-NAME>ErrorName</SHORT-NAME>
  <ERROR-CODE>10</ERROR-CODE>
</APPLICATION-ERROR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ApplicationError = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ApplicationError)
        self.assertEqual(elem.name, "ErrorName")
        self.assertEqual(elem.error_code, 10)


class TestClientServerOperation(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ClientServerOperation("OperationName")
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertEqual(elem.name, "OperationName")

    def test_one_argument(self):
        element = ar_element.ClientServerOperation("OperationName")
        element.make_in_argument("Arg1",
                                 type_ref=ar_element.AutosarDataTypeRef("/DataTypes/uint8", IMPLEMENTATION_DATA_TYPE))
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
  <ARGUMENTS>
    <ARGUMENT-DATA-PROTOTYPE>
      <SHORT-NAME>Arg1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint8</TYPE-TREF>
      <DIRECTION>IN</DIRECTION>
    </ARGUMENT-DATA-PROTOTYPE>
  </ARGUMENTS>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertEqual(elem.name, "OperationName")
        self.assertEqual(len(elem.arguments), 1)
        argument: ar_element.ArgumentDataPrototype = elem.arguments[0]
        self.assertIsInstance(argument, ar_element.ArgumentDataPrototype)
        self.assertEqual(argument.name, "Arg1")
        self.assertEqual(str(argument.type_ref), "/DataTypes/uint8")
        self.assertEqual(argument.direction, ar_enum.ArgumentDirection.IN)

    def test_two_arguments(self):
        element = ar_element.ClientServerOperation("OperationName")
        element.make_in_argument("Arg1",
                                 type_ref=ar_element.AutosarDataTypeRef("/DataTypes/uint8", IMPLEMENTATION_DATA_TYPE))
        element.make_out_argument("Arg2",
                                  type_ref=ar_element.AutosarDataTypeRef("/DataTypes/bool", IMPLEMENTATION_DATA_TYPE))
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
  <ARGUMENTS>
    <ARGUMENT-DATA-PROTOTYPE>
      <SHORT-NAME>Arg1</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint8</TYPE-TREF>
      <DIRECTION>IN</DIRECTION>
    </ARGUMENT-DATA-PROTOTYPE>
    <ARGUMENT-DATA-PROTOTYPE>
      <SHORT-NAME>Arg2</SHORT-NAME>
      <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/bool</TYPE-TREF>
      <DIRECTION>OUT</DIRECTION>
    </ARGUMENT-DATA-PROTOTYPE>
  </ARGUMENTS>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertEqual(len(elem.arguments), 2)
        argument: ar_element.ArgumentDataPrototype = elem.arguments[0]
        self.assertIsInstance(argument, ar_element.ArgumentDataPrototype)
        self.assertEqual(argument.name, "Arg1")
        self.assertEqual(str(argument.type_ref), "/DataTypes/uint8")
        self.assertEqual(argument.direction, ar_enum.ArgumentDirection.IN)
        argument: ar_element.ArgumentDataPrototype = elem.arguments[1]
        self.assertIsInstance(argument, ar_element.ArgumentDataPrototype)
        self.assertEqual(argument.name, "Arg2")
        self.assertEqual(str(argument.type_ref), "/DataTypes/bool")
        self.assertEqual(argument.direction, ar_enum.ArgumentDirection.OUT)

    def test_diag_arg_integrity(self):
        element = ar_element.ClientServerOperation("OperationName",
                                                   diag_arg_integrity=False)
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
  <DIAG-ARG-INTEGRITY>false</DIAG-ARG-INTEGRITY>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertFalse(elem.diag_arg_integrity)

    def test_fire_and_forget(self):
        element = ar_element.ClientServerOperation("OperationName",
                                                   fire_and_forget=True)
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
  <FIRE-AND-FORGET>true</FIRE-AND-FORGET>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertTrue(elem.fire_and_forget)

    def test_single_possible_error(self):
        element = ar_element.ClientServerOperation("OperationName")
        element.make_possible_error_ref("/PortInterfaces/OperationName/ErrorName1")
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
  <POSSIBLE-ERROR-REFS>
    <POSSIBLE-ERROR-REF DEST="APPLICATION-ERROR">/PortInterfaces/OperationName/ErrorName1</POSSIBLE-ERROR-REF>
  </POSSIBLE-ERROR-REFS>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertEqual(elem.name, "OperationName")
        self.assertEqual(len(elem.possible_error_refs), 1)
        possible_error_ref: ar_element.ApplicationErrorRef = elem.possible_error_refs[0]
        self.assertIsInstance(possible_error_ref, ar_element.ApplicationErrorRef)
        self.assertEqual(str(possible_error_ref), "/PortInterfaces/OperationName/ErrorName1")

    def test_dual_possible_errors(self):
        element = ar_element.ClientServerOperation("OperationName")
        element.make_possible_error_ref("/PortInterfaces/OperationName/ErrorName1")
        element.make_possible_error_ref("/PortInterfaces/OperationName/ErrorName2")
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-OPERATION>
  <SHORT-NAME>OperationName</SHORT-NAME>
  <POSSIBLE-ERROR-REFS>
    <POSSIBLE-ERROR-REF DEST="APPLICATION-ERROR">/PortInterfaces/OperationName/ErrorName1</POSSIBLE-ERROR-REF>
    <POSSIBLE-ERROR-REF DEST="APPLICATION-ERROR">/PortInterfaces/OperationName/ErrorName2</POSSIBLE-ERROR-REF>
  </POSSIBLE-ERROR-REFS>
</CLIENT-SERVER-OPERATION>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerOperation = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerOperation)
        self.assertEqual(elem.name, "OperationName")
        self.assertEqual(len(elem.possible_error_refs), 2)
        possible_error_ref: ar_element.ApplicationErrorRef = elem.possible_error_refs[0]
        self.assertIsInstance(possible_error_ref, ar_element.ApplicationErrorRef)
        self.assertEqual(str(possible_error_ref), "/PortInterfaces/OperationName/ErrorName1")
        possible_error_ref: ar_element.ApplicationErrorRef = elem.possible_error_refs[1]
        self.assertIsInstance(possible_error_ref, ar_element.ApplicationErrorRef)
        self.assertEqual(str(possible_error_ref), "/PortInterfaces/OperationName/ErrorName2")


class TestClientServerInterface(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ClientServerInterface("InterfaceName")
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
</CLIENT-SERVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerInterface)
        self.assertEqual(elem.name, "InterfaceName")

    def test_operation(self):
        element = ar_element.ClientServerInterface("InterfaceName")
        operation = element.make_operation("Operation1")
        operation.make_in_argument("Arg1",
                                   type_ref=ar_element.AutosarDataTypeRef("/DataTypes/uint8", IMPLEMENTATION_DATA_TYPE))
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <OPERATIONS>
    <CLIENT-SERVER-OPERATION>
      <SHORT-NAME>Operation1</SHORT-NAME>
      <ARGUMENTS>
        <ARGUMENT-DATA-PROTOTYPE>
          <SHORT-NAME>Arg1</SHORT-NAME>
          <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint8</TYPE-TREF>
          <DIRECTION>IN</DIRECTION>
        </ARGUMENT-DATA-PROTOTYPE>
      </ARGUMENTS>
    </CLIENT-SERVER-OPERATION>
  </OPERATIONS>
</CLIENT-SERVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.operations), 1)
        operation = elem.operations[0]
        self.assertIsInstance(operation, ar_element.ClientServerOperation)
        self.assertEqual(operation.name, "Operation1")

    def test_operation_with_possible_error(self):
        element = ar_element.ClientServerInterface("InterfaceName")
        element.make_possible_error("E_NOT_OK")
        operation = element.make_operation("Operation1")
        operation.make_in_argument("Arg1",
                                   type_ref=ar_element.AutosarDataTypeRef("/DataTypes/uint8", IMPLEMENTATION_DATA_TYPE))
        operation.make_possible_error_ref("/Portinterfaces/InterfaceName/E_NOT_OK")
        writer = autosar.xml.Writer()
        xml = '''<CLIENT-SERVER-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <OPERATIONS>
    <CLIENT-SERVER-OPERATION>
      <SHORT-NAME>Operation1</SHORT-NAME>
      <ARGUMENTS>
        <ARGUMENT-DATA-PROTOTYPE>
          <SHORT-NAME>Arg1</SHORT-NAME>
          <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/uint8</TYPE-TREF>
          <DIRECTION>IN</DIRECTION>
        </ARGUMENT-DATA-PROTOTYPE>
      </ARGUMENTS>
      <POSSIBLE-ERROR-REFS>
        <POSSIBLE-ERROR-REF DEST="APPLICATION-ERROR">/Portinterfaces/InterfaceName/E_NOT_OK</POSSIBLE-ERROR-REF>
      </POSSIBLE-ERROR-REFS>
    </CLIENT-SERVER-OPERATION>
  </OPERATIONS>
  <POSSIBLE-ERRORS>
    <APPLICATION-ERROR>
      <SHORT-NAME>E_NOT_OK</SHORT-NAME>
    </APPLICATION-ERROR>
  </POSSIBLE-ERRORS>
</CLIENT-SERVER-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ClientServerInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ClientServerInterface)
        self.assertEqual(elem.name, "InterfaceName")
        self.assertEqual(len(elem.operations), 1)
        operation = elem.operations[0]
        self.assertIsInstance(operation, ar_element.ClientServerOperation)
        self.assertEqual(len(operation.possible_error_refs), 1)
        possible_error_ref = operation.possible_error_refs[0]
        self.assertEqual(str(possible_error_ref), "/Portinterfaces/InterfaceName/E_NOT_OK")
        self.assertEqual(len(elem.possible_errors), 1)
        possible_errors = elem.possible_errors[0]
        self.assertEqual(possible_errors.name, "E_NOT_OK")


class TestModeSwitchInterface(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.ModeSwitchInterface("InterfaceName")
        writer = autosar.xml.Writer()
        xml = '''<MODE-SWITCH-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
</MODE-SWITCH-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchInterface)
        self.assertEqual(elem.name, "InterfaceName")

    def test_mode_group_in_constructor(self):
        mode_declaration_ref = "ModeDeclarations/ModeGroupName/Mode1"
        mode_group = ar_element.ModeDeclarationGroupPrototype("mode", type_ref=mode_declaration_ref)
        element = ar_element.ModeSwitchInterface("InterfaceName", mode_group=mode_group)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-SWITCH-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <MODE-GROUP>
    <SHORT-NAME>mode</SHORT-NAME>
    <TYPE-TREF DEST="MODE-DECLARATION-GROUP">{mode_declaration_ref}</TYPE-TREF>
  </MODE-GROUP>
</MODE-SWITCH-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchInterface)
        self.assertIsInstance(elem.mode_group, ar_element.ModeDeclarationGroupPrototype)
        self.assertEqual(elem.mode_group.name, "mode")
        self.assertEqual(str(elem.mode_group.type_ref), mode_declaration_ref)

    def test_mode_group_from_create_method(self):
        mode_declaration_ref = "ModeDeclarations/ModeGroupName/Mode1"
        element = ar_element.ModeSwitchInterface("InterfaceName")
        element.create_mode_group("mode", type_ref=mode_declaration_ref)
        writer = autosar.xml.Writer()
        xml = f'''<MODE-SWITCH-INTERFACE>
  <SHORT-NAME>InterfaceName</SHORT-NAME>
  <MODE-GROUP>
    <SHORT-NAME>mode</SHORT-NAME>
    <TYPE-TREF DEST="MODE-DECLARATION-GROUP">{mode_declaration_ref}</TYPE-TREF>
  </MODE-GROUP>
</MODE-SWITCH-INTERFACE>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ModeSwitchInterface = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ModeSwitchInterface)
        self.assertIsInstance(elem.mode_group, ar_element.ModeDeclarationGroupPrototype)
        self.assertEqual(elem.mode_group.name, "mode")
        self.assertEqual(str(elem.mode_group.type_ref), mode_declaration_ref)


if __name__ == '__main__':
    unittest.main()
