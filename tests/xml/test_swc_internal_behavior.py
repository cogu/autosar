"""Unit tests for internal behavior elements"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar.xml.element as ar_element # noqa E402
import autosar # noqa E402


class TestArVariableInImplementationDataInstanceRef(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.xml_tag = "AUTOSAR-VARIABLE-IN-IMPL-DATATYPE"

    def test_empty(self):
        element = ar_element.ArVariableInImplementationDataInstanceRef()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, self.xml_tag)
        self.assertEqual(xml, '<AUTOSAR-VARIABLE-IN-IMPL-DATATYPE/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ArVariableInImplementationDataInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArVariableInImplementationDataInstanceRef)

    def test_port_prototype_ref(self):
        ref_str = "/Components/SwcName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str,
                                               ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        element = ar_element.ArVariableInImplementationDataInstanceRef(port_prototype_ref=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>
  <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">{ref_str}</PORT-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArVariableInImplementationDataInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArVariableInImplementationDataInstanceRef)
        self.assertEqual(str(elem.port_prototype_ref), ref_str)

    def test_root_variable_data_prototype_ref(self):
        ref_str = "/Components/SwcName/VariableName"
        variable_ref = ar_element.VariableDataPrototypeRef(ref_str)
        element = ar_element.ArVariableInImplementationDataInstanceRef(root_variable_data_prototype_ref=variable_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>
  <ROOT-VARIABLE-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">{ref_str}</ROOT-VARIABLE-DATA-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArVariableInImplementationDataInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArVariableInImplementationDataInstanceRef)
        self.assertEqual(str(elem.root_variable_data_prototype_ref), ref_str)

    def test_context_data_prototype_refs_single(self):
        ref_str = "/DataTypes/RecordTypeName/ElementName"
        dest = ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE_ELEMENT
        element_ref = ar_element.AbstractImplementationDataTypeElementRef(ref_str, dest)
        element = ar_element.ArVariableInImplementationDataInstanceRef(context_data_prototype_refs=element_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>
  <CONTEXT-DATA-PROTOTYPE-REFS>
    <CONTEXT-DATA-PROTOTYPE-REF DEST="IMPLEMENTATION-DATA-TYPE-ELEMENT">{ref_str}</CONTEXT-DATA-PROTOTYPE-REF>
  </CONTEXT-DATA-PROTOTYPE-REFS>
</AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArVariableInImplementationDataInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArVariableInImplementationDataInstanceRef)
        self.assertEqual(len(elem.context_data_prototype_refs), 1)
        self.assertCountEqual(str(elem.context_data_prototype_refs[0]), ref_str)

    def test_target_data_prototype_ref(self):
        ref_str = "/DataTypes/RecordTypeName/ElementName"
        dest = ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE_ELEMENT
        element_ref = ar_element.AbstractImplementationDataTypeElementRef(ref_str, dest)
        element = ar_element.ArVariableInImplementationDataInstanceRef(target_data_prototype_ref=element_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>
  <TARGET-DATA-PROTOTYPE-REF DEST="IMPLEMENTATION-DATA-TYPE-ELEMENT">{ref_str}</TARGET-DATA-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ArVariableInImplementationDataInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ArVariableInImplementationDataInstanceRef)
        self.assertEqual(str(elem.target_data_prototype_ref), ref_str)


class TestVariableInAtomicSWCTypeInstanceRef(unittest.TestCase):

    def test_empty(self):
        element = ar_element.VariableInAtomicSWCTypeInstanceRef()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<AUTOSAR-VARIABLE-IREF/>')
        reader = autosar.xml.Reader()
        elem: ar_element.VariableInAtomicSWCTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableInAtomicSWCTypeInstanceRef)

    def test_port_prototype_ref(self):
        ref_str = "/Components/SwcName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str,
                                               ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        element = ar_element.VariableInAtomicSWCTypeInstanceRef(port_prototype_ref=port_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IREF>
  <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">{ref_str}</PORT-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IREF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableInAtomicSWCTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableInAtomicSWCTypeInstanceRef)
        self.assertEqual(str(elem.port_prototype_ref), ref_str)

    def test_root_variable_data_prototype_ref(self):
        ref_str = "/Components/SwcName/VariableName"
        variable_ref = ar_element.VariableDataPrototypeRef(ref_str)
        element = ar_element.VariableInAtomicSWCTypeInstanceRef(root_variable_data_prototype_ref=variable_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IREF>
  <ROOT-VARIABLE-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">{ref_str}</ROOT-VARIABLE-DATA-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IREF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableInAtomicSWCTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableInAtomicSWCTypeInstanceRef)
        self.assertEqual(str(elem.root_variable_data_prototype_ref), ref_str)

    def test_context_data_prototype_refs_single(self):
        ref_str = "/DataTypes/RecordTypeName/ElementName"
        dest = ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT
        element_ref = ar_element.ApplicationCompositeElementDataPrototypeRef(ref_str, dest)
        element = ar_element.VariableInAtomicSWCTypeInstanceRef(context_data_prototype_refs=element_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IREF>
  <CONTEXT-DATA-PROTOTYPE-REF DEST="APPLICATION-RECORD-ELEMENT">{ref_str}</CONTEXT-DATA-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IREF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableInAtomicSWCTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableInAtomicSWCTypeInstanceRef)
        self.assertEqual(len(elem.context_data_prototype_refs), 1)
        self.assertCountEqual(str(elem.context_data_prototype_refs[0]), ref_str)

    def test_target_data_prototype_ref(self):
        ref_str = "/DataTypes/RecordTypeName/ElementName"
        dest = ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT
        element_ref = ar_element.DataPrototypeRef(ref_str, dest)
        element = ar_element.VariableInAtomicSWCTypeInstanceRef(target_data_prototype_ref=element_ref)
        writer = autosar.xml.Writer()
        xml = f'''<AUTOSAR-VARIABLE-IREF>
  <TARGET-DATA-PROTOTYPE-REF DEST="APPLICATION-RECORD-ELEMENT">{ref_str}</TARGET-DATA-PROTOTYPE-REF>
</AUTOSAR-VARIABLE-IREF>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.VariableInAtomicSWCTypeInstanceRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.VariableInAtomicSWCTypeInstanceRef)
        self.assertEqual(str(elem.target_data_prototype_ref), ref_str)


class TestAutosarVariableRef(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.xml_tag = "ACCESSED-VARIABLE"

    def test_empty(self):
        element = ar_element.AutosarVariableRef()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element, self.xml_tag)
        self.assertEqual(xml, '<ACCESSED-VARIABLE/>')
        reader = autosar.xml.Reader()
        elem: ar_element.AutosarVariableRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AutosarVariableRef)

    def test_ar_variable_in_impl_datatype(self):
        ref_str = "/Components/SwcName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str,
                                               ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        variable_dataprototype = ar_element.ArVariableInImplementationDataInstanceRef(port_prototype_ref=port_ref)
        element = ar_element.AutosarVariableRef(ar_variable_in_impl_datatype=variable_dataprototype)
        writer = autosar.xml.Writer()
        xml = f'''<ACCESSED-VARIABLE>
  <AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>
    <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">{ref_str}</PORT-PROTOTYPE-REF>
  </AUTOSAR-VARIABLE-IN-IMPL-DATATYPE>
</ACCESSED-VARIABLE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AutosarVariableRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AutosarVariableRef)
        self.assertIsInstance(elem.ar_variable_in_impl_datatype, ar_element.ArVariableInImplementationDataInstanceRef)

    def test_ar_variable_iref(self):
        ref_str = "/Components/SwcName/PortName"
        port_ref = ar_element.PortPrototypeRef(ref_str,
                                               ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        variable_iref = ar_element.VariableInAtomicSWCTypeInstanceRef(port_prototype_ref=port_ref)
        element = ar_element.AutosarVariableRef(ar_variable_iref=variable_iref)
        writer = autosar.xml.Writer()
        xml = f'''<ACCESSED-VARIABLE>
  <AUTOSAR-VARIABLE-IREF>
    <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">{ref_str}</PORT-PROTOTYPE-REF>
  </AUTOSAR-VARIABLE-IREF>
</ACCESSED-VARIABLE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AutosarVariableRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AutosarVariableRef)
        self.assertIsInstance(elem.ar_variable_iref, ar_element.VariableInAtomicSWCTypeInstanceRef)

    def test_local_variable_ref(self):
        ref_str = "/Components/SwcName/VariableName"
        variable_ref = ar_element.VariableDataPrototypeRef(ref_str)
        element = ar_element.AutosarVariableRef(local_variable_ref=variable_ref)
        writer = autosar.xml.Writer()
        xml = f'''<ACCESSED-VARIABLE>
  <LOCAL-VARIABLE-REF DEST="VARIABLE-DATA-PROTOTYPE">{ref_str}</LOCAL-VARIABLE-REF>
</ACCESSED-VARIABLE>'''
        self.assertEqual(writer.write_str_elem(element, self.xml_tag), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.AutosarVariableRef = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.AutosarVariableRef)
        self.assertIsInstance(elem.local_variable_ref, ar_element.VariableDataPrototypeRef)


if __name__ == '__main__':
    unittest.main()
