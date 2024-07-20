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


class TestExecutableEntityActivationReason(unittest.TestCase):

    def test_read_write_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.ExecutableEntityActivationReason('MyName')
        xml = '''<EXECUTABLE-ENTITY-ACTIVATION-REASON>
  <SHORT-NAME>MyName</SHORT-NAME>
</EXECUTABLE-ENTITY-ACTIVATION-REASON>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ExecutableEntityActivationReason = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ExecutableEntityActivationReason)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.short_name, 'MyName')

    def test_read_write_bit_position(self):
        writer = autosar.xml.Writer()
        element = ar_element.ExecutableEntityActivationReason('MyName', bit_position=0)
        xml = '''<EXECUTABLE-ENTITY-ACTIVATION-REASON>
  <SHORT-NAME>MyName</SHORT-NAME>
  <BIT-POSITION>0</BIT-POSITION>
</EXECUTABLE-ENTITY-ACTIVATION-REASON>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ExecutableEntityActivationReason = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ExecutableEntityActivationReason)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.bit_position, 0)


class TestExclusiveAreaRefConditional(unittest.TestCase):

    def test_empty(self):
        element = ar_element.ExclusiveAreaRefConditional()
        writer = autosar.xml.Writer()
        xml = writer.write_str_elem(element)
        self.assertEqual(xml, '<EXCLUSIVE-AREA-REF-CONDITIONAL/>')
        reader = autosar.xml.Reader()
        elem: ar_element.ExclusiveAreaRefConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ExclusiveAreaRefConditional)

    def test_exclusive_area_ref_from_str(self):
        ref_str = "/ExclusiveAreas/AreaName"
        element = ar_element.ExclusiveAreaRefConditional(ref_str)
        writer = autosar.xml.Writer()
        xml = f'''<EXCLUSIVE-AREA-REF-CONDITIONAL>
  <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str}</EXCLUSIVE-AREA-REF>
</EXCLUSIVE-AREA-REF-CONDITIONAL>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.ExclusiveAreaRefConditional = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(elem.exclusive_area_ref), ref_str)


class TestExecutableEntity(unittest.TestCase):
    """
    ExecutableEntity is a base class. Use RunnableEntity
    for unit testing.
    """

    def test_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.RunnableEntity('MyName')
        xml = '''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.short_name, 'MyName')

    def test_activation_reasons_from_element(self):
        writer = autosar.xml.Writer()
        reason = ar_element.ExecutableEntityActivationReason("MyReason", 1, symbol="MySymbol")
        element = ar_element.RunnableEntity('MyName', activation_reasons=reason)
        xml = '''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <ACTIVATION-REASONS>
    <EXECUTABLE-ENTITY-ACTIVATION-REASON>
      <SHORT-NAME>MyReason</SHORT-NAME>
      <SYMBOL>MySymbol</SYMBOL>
      <BIT-POSITION>1</BIT-POSITION>
    </EXECUTABLE-ENTITY-ACTIVATION-REASON>
  </ACTIVATION-REASONS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.activation_reasons), 1)
        activation_reason = elem.activation_reasons[0]
        self.assertIsInstance(activation_reason, ar_element.ExecutableEntityActivationReason)
        self.assertEqual(activation_reason.name, 'MyReason')

    def test_activation_reasons_from_list(self):
        writer = autosar.xml.Writer()
        reasons = [ar_element.ExecutableEntityActivationReason("MyReason1", 0, symbol="MySymbol1"),
                   ar_element.ExecutableEntityActivationReason("MyReason2", 1, symbol="MySymbol2")]
        element = ar_element.RunnableEntity('MyName', activation_reasons=reasons)
        xml = '''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <ACTIVATION-REASONS>
    <EXECUTABLE-ENTITY-ACTIVATION-REASON>
      <SHORT-NAME>MyReason1</SHORT-NAME>
      <SYMBOL>MySymbol1</SYMBOL>
      <BIT-POSITION>0</BIT-POSITION>
    </EXECUTABLE-ENTITY-ACTIVATION-REASON>
    <EXECUTABLE-ENTITY-ACTIVATION-REASON>
      <SHORT-NAME>MyReason2</SHORT-NAME>
      <SYMBOL>MySymbol2</SYMBOL>
      <BIT-POSITION>1</BIT-POSITION>
    </EXECUTABLE-ENTITY-ACTIVATION-REASON>
  </ACTIVATION-REASONS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.activation_reasons), 2)
        activation_reason = elem.activation_reasons[0]
        self.assertIsInstance(activation_reason, ar_element.ExecutableEntityActivationReason)
        self.assertEqual(activation_reason.name, 'MyReason1')
        activation_reason = elem.activation_reasons[1]
        self.assertIsInstance(activation_reason, ar_element.ExecutableEntityActivationReason)
        self.assertEqual(activation_reason.name, 'MyReason2')

    def test_can_enters_from_element(self):
        """
        CAN-ENTERS is used for XML schema version >= 50
        """
        ref_str = "/MyPackage/MySwc/MyExclusiveArea"
        writer = autosar.xml.Writer()
        exclusive_area_cond = ar_element.ExclusiveAreaRefConditional(ref_str)
        element = ar_element.RunnableEntity('MyName', can_enter_leave=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <CAN-ENTERS>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
  </CAN-ENTERS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.can_enter_leave), 1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.can_enter_leave[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str)

    def test_can_enters_from_list(self):
        ref_str1 = "/MyPackage/MySwc/MyExclusiveArea1"
        ref_str2 = "/MyPackage/MySwc/MyExclusiveArea2"
        writer = autosar.xml.Writer()
        exclusive_area_cond = [ar_element.ExclusiveAreaRefConditional(ref_str1),
                               ar_element.ExclusiveAreaRefConditional(ref_str2)]
        element = ar_element.RunnableEntity('MyName', can_enter_leave=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <CAN-ENTERS>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str1}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str2}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
  </CAN-ENTERS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.can_enter_leave), 2)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.can_enter_leave[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.can_enter_leave[1]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str2)

    def test_can_enter_exclusive_area_from_element(self):
        """
        CAN-ENTER-EXCLUSIVE-AREA-REFS is used for XML schema version < 50
        """
        ref_str = "/MyPackage/MySwc/MyExclusiveArea"
        writer = autosar.xml.Writer(schema_version=49)
        exclusive_area_cond = ar_element.ExclusiveAreaRefConditional(ref_str)
        element = ar_element.RunnableEntity('MyName', can_enter_leave=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <CAN-ENTER-EXCLUSIVE-AREA-REFS>
    <CAN-ENTER-EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str}</CAN-ENTER-EXCLUSIVE-AREA-REF>
  </CAN-ENTER-EXCLUSIVE-AREA-REFS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader(schema_version=49)
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.can_enter_leave), 1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.can_enter_leave[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str)

    def test_can_enter_exclusive_area_from_list(self):
        ref_str1 = "/MyPackage/MySwc/MyExclusiveArea1"
        ref_str2 = "/MyPackage/MySwc/MyExclusiveArea2"
        writer = autosar.xml.Writer(schema_version=49)
        exclusive_area_cond = [ar_element.ExclusiveAreaRefConditional(ref_str1),
                               ar_element.ExclusiveAreaRefConditional(ref_str2)]
        element = ar_element.RunnableEntity('MyName', can_enter_leave=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <CAN-ENTER-EXCLUSIVE-AREA-REFS>
    <CAN-ENTER-EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str1}</CAN-ENTER-EXCLUSIVE-AREA-REF>
    <CAN-ENTER-EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str2}</CAN-ENTER-EXCLUSIVE-AREA-REF>
  </CAN-ENTER-EXCLUSIVE-AREA-REFS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader(schema_version=49)
        # During XML reading, elements of type ExclusiveAreaRef are automatically wrapped
        # inside the newer ExclusiveAreaRefConditional element
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.can_enter_leave), 2)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.can_enter_leave[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.can_enter_leave[1]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str2)

    def test_can_enter_create_directly_from_reference_string(self):
        ref_str = "/MyPackage/MySwc/MyExclusiveArea"
        writer = autosar.xml.Writer()
        exclusive_area_cond = ar_element.ExclusiveAreaRefConditional(ref_str)
        element = ar_element.RunnableEntity('MyName', can_enter_leave=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <CAN-ENTERS>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
  </CAN-ENTERS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)

    def test_can_enter_create_from_list_of_reference_strings(self):
        ref_str1 = "/MyPackage/MySwc/MyExclusiveArea1"
        ref_str2 = "/MyPackage/MySwc/MyExclusiveArea2"
        writer = autosar.xml.Writer()
        element = ar_element.RunnableEntity('MyName', can_enter_leave=[ref_str1, ref_str2])
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <CAN-ENTERS>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str1}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str2}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
  </CAN-ENTERS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)

    def test_exclusive_area_nesting_order_refs_from_element(self):
        ref_str = "/MyPackage/MySwc/MyExclusiveAreaNestingOrder"
        writer = autosar.xml.Writer()
        exclusive_area_nesting_order = ar_element.ExclusiveAreaNestingOrderRef(ref_str)
        element = ar_element.RunnableEntity('MyName', exclusive_area_nesting_order=exclusive_area_nesting_order)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <EXCLUSIVE-AREA-NESTING-ORDER-REFS>
    <EXCLUSIVE-AREA-NESTING-ORDER-REF DEST="EXCLUSIVE-AREA-NESTING-ORDER">{ref_str}</EXCLUSIVE-AREA-NESTING-ORDER-REF>
  </EXCLUSIVE-AREA-NESTING-ORDER-REFS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.exclusive_area_nesting_order), 1)
        nesting_order: ar_element.ExclusiveAreaNestingOrderRef = elem.exclusive_area_nesting_order[0]
        self.assertIsInstance(nesting_order, ar_element.ExclusiveAreaNestingOrderRef)
        self.assertEqual(str(nesting_order), ref_str)

    def test_exclusive_area_nesting_order_refs_from_list(self):
        ref_str1 = "/MyPackage/MySwc/MyExclusiveAreaNestingOrder1"
        ref_str2 = "/MyPackage/MySwc/MyExclusiveAreaNestingOrder1"
        writer = autosar.xml.Writer()
        exclusive_area_nesting_order = [ar_element.ExclusiveAreaNestingOrderRef(ref_str1),
                                        ar_element.ExclusiveAreaNestingOrderRef(ref_str1)]
        element = ar_element.RunnableEntity('MyName', exclusive_area_nesting_order=exclusive_area_nesting_order)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <EXCLUSIVE-AREA-NESTING-ORDER-REFS>
    <EXCLUSIVE-AREA-NESTING-ORDER-REF DEST="EXCLUSIVE-AREA-NESTING-ORDER">{ref_str1}</EXCLUSIVE-AREA-NESTING-ORDER-REF>
    <EXCLUSIVE-AREA-NESTING-ORDER-REF DEST="EXCLUSIVE-AREA-NESTING-ORDER">{ref_str2}</EXCLUSIVE-AREA-NESTING-ORDER-REF>
  </EXCLUSIVE-AREA-NESTING-ORDER-REFS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.exclusive_area_nesting_order), 2)
        nesting_order: ar_element.ExclusiveAreaNestingOrderRef = elem.exclusive_area_nesting_order[0]
        self.assertIsInstance(nesting_order, ar_element.ExclusiveAreaNestingOrderRef)
        self.assertEqual(str(nesting_order), ref_str1)
        nesting_order = elem.exclusive_area_nesting_order[1]
        self.assertIsInstance(nesting_order, ar_element.ExclusiveAreaNestingOrderRef)
        self.assertEqual(str(nesting_order), ref_str2)

    def test_minimum_start_interval_100ms(self):
        writer = autosar.xml.Writer()
        element = ar_element.RunnableEntity('MyName', minimum_start_interval=0.1)
        xml = '''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <MINIMUM-START-INTERVAL>0.1</MINIMUM-START-INTERVAL>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertAlmostEqual(elem.minimum_start_interval, 0.1)

    def test_minimum_start_interval_2s(self):
        writer = autosar.xml.Writer()
        element = ar_element.RunnableEntity('MyName', minimum_start_interval=2)
        xml = '''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <MINIMUM-START-INTERVAL>2</MINIMUM-START-INTERVAL>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(elem.minimum_start_interval, 2)

    def test_reentrancy_level(self):
        writer = autosar.xml.Writer()
        element = ar_element.RunnableEntity('MyName',
                                            reentrancy_level=ar_enum.ReentrancyLevel.SINGLE_CORE_REENTRANT)
        xml = '''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <REENTRANCY-LEVEL>SINGLE-CORE-REENTRANT</REENTRANCY-LEVEL>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(elem.reentrancy_level, ar_enum.ReentrancyLevel.SINGLE_CORE_REENTRANT)

    def test_runs_insides_from_element(self):
        """
        RUNS-INSIDES is used for XML schema version >= 50
        """
        ref_str = "/MyPackage/MySwc/MyExclusiveArea"
        writer = autosar.xml.Writer()
        exclusive_area_cond = ar_element.ExclusiveAreaRefConditional(ref_str)
        element = ar_element.RunnableEntity('MyName', runs_insides=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <RUNS-INSIDES>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
  </RUNS-INSIDES>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.runs_insides), 1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.runs_insides[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str)

    def test_runs_insides_from_list(self):
        ref_str1 = "/MyPackage/MySwc/MyExclusiveArea1"
        ref_str2 = "/MyPackage/MySwc/MyExclusiveArea2"
        writer = autosar.xml.Writer()
        exclusive_area_cond = [ar_element.ExclusiveAreaRefConditional(ref_str1),
                               ar_element.ExclusiveAreaRefConditional(ref_str2)]
        element = ar_element.RunnableEntity('MyName', runs_insides=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <RUNS-INSIDES>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str1}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
    <EXCLUSIVE-AREA-REF-CONDITIONAL>
      <EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str2}</EXCLUSIVE-AREA-REF>
    </EXCLUSIVE-AREA-REF-CONDITIONAL>
  </RUNS-INSIDES>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.runs_insides), 2)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.runs_insides[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.runs_insides[1]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str2)

    def test_runs_inside_exclusive_area_from_element(self):
        """
        RUNS-INSIDE-EXCLUSIVE-AREA-REFS is used for XML schema version < 50
        """
        ref_str = "/MyPackage/MySwc/MyExclusiveArea"
        writer = autosar.xml.Writer(schema_version=49)
        exclusive_area_cond = ar_element.ExclusiveAreaRefConditional(ref_str)
        element = ar_element.RunnableEntity('MyName', runs_insides=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <RUNS-INSIDE-EXCLUSIVE-AREA-REFS>
    <RUNS-INSIDE-EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str}</RUNS-INSIDE-EXCLUSIVE-AREA-REF>
  </RUNS-INSIDE-EXCLUSIVE-AREA-REFS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader(schema_version=49)
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.runs_insides), 1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.runs_insides[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str)

    def test_run_insides_exclusive_area_from_list(self):
        ref_str1 = "/MyPackage/MySwc/MyExclusiveArea1"
        ref_str2 = "/MyPackage/MySwc/MyExclusiveArea2"
        writer = autosar.xml.Writer(schema_version=49)
        exclusive_area_cond = [ar_element.ExclusiveAreaRefConditional(ref_str1),
                               ar_element.ExclusiveAreaRefConditional(ref_str2)]
        element = ar_element.RunnableEntity('MyName', runs_insides=exclusive_area_cond)
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <RUNS-INSIDE-EXCLUSIVE-AREA-REFS>
    <RUNS-INSIDE-EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str1}</RUNS-INSIDE-EXCLUSIVE-AREA-REF>
    <RUNS-INSIDE-EXCLUSIVE-AREA-REF DEST="EXCLUSIVE-AREA">{ref_str2}</RUNS-INSIDE-EXCLUSIVE-AREA-REF>
  </RUNS-INSIDE-EXCLUSIVE-AREA-REFS>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader(schema_version=49)
        # During XML reading, elements of type ExclusiveAreaRef are automatically wrapped
        # inside the newer ExclusiveAreaRefConditional element
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        self.assertEqual(len(elem.runs_insides), 2)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.runs_insides[0]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str1)
        conditional: ar_element.ExclusiveAreaRefConditional = elem.runs_insides[1]
        self.assertIsInstance(conditional, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(conditional.exclusive_area_ref), ref_str2)

    def test_sw_addr_method_from_element(self):
        ref_str = '/SwAddrMethods/DEFAULT'
        writer = autosar.xml.Writer()
        element = ar_element.RunnableEntity('MyName',
                                            sw_addr_method=ar_element.SwAddrMethodRef(ref_str))
        xml = f'''<RUNNABLE-ENTITY>
  <SHORT-NAME>MyName</SHORT-NAME>
  <SW-ADDR-METHOD-REF DEST="SW-ADDR-METHOD">{ref_str}</SW-ADDR-METHOD-REF>
</RUNNABLE-ENTITY>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RunnableEntity = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RunnableEntity)
        ref = elem.sw_addr_method
        self.assertEqual(ref.value, '/SwAddrMethods/DEFAULT')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD)

    def test_create_sw_addr_method_from_string(self):
        ref_str = '/SwAddrMethods/DEFAULT'
        element = ar_element.RunnableEntity('MyName', sw_addr_method=ref_str)
        ref = element.sw_addr_method
        self.assertEqual(ref.value, '/SwAddrMethods/DEFAULT')
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD)


class TestInitEvent(unittest.TestCase):
    """
    Tests elements from RTEEvent base class.
    InitEvent doesn't have any additional elements except those inherited
    from RTEEvent.
    """

    def test_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.InitEvent('MyName')
        xml = '''<INIT-EVENT>
  <SHORT-NAME>MyName</SHORT-NAME>
</INIT-EVENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.InitEvent = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InitEvent)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.short_name, 'MyName')

    def test_disabled_modes_from_element(self):
        context_port_ref_str = "/ComponentTypes/MyComponent/BswM_Mode"
        context_mode_decl_group_ref_str = "/PortInterfaces/BswM_ModeSwitchInterface/BswM_Mode"
        target_mode_decl_ref_str = "/ModeDclrGroups/BswM_Mode/POSTRUN"
        context_port = ar_element.PortPrototypeRef(context_port_ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
        context_mode_decl_group = ar_element.ModeDeclarationGroupPrototypeRef(context_mode_decl_group_ref_str)
        target_mode_decl = ar_element.ModeDeclarationRef(target_mode_decl_ref_str)
        disabled_mode = ar_element.RModeInAtomicSwcInstanceRef(
            context_port_ref=context_port,
            context_mode_declaration_group_prototype_ref=context_mode_decl_group,
            target_mode_declaration_ref=target_mode_decl)
        element = ar_element.InitEvent('MyName',
                                       disabled_modes=disabled_mode)
        writer = autosar.xml.Writer()
        xml = f'''<INIT-EVENT>
  <SHORT-NAME>MyName</SHORT-NAME>
  <DISABLED-MODE-IREFS>
    <DISABLED-MODE-IREF>
      <CONTEXT-PORT-REF DEST="R-PORT-PROTOTYPE">{context_port_ref_str}</CONTEXT-PORT-REF>
      <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">\
{context_mode_decl_group_ref_str}</CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF>
      <TARGET-MODE-DECLARATION-REF DEST="MODE-DECLARATION">{target_mode_decl_ref_str}</TARGET-MODE-DECLARATION-REF>
    </DISABLED-MODE-IREF>
  </DISABLED-MODE-IREFS>
</INIT-EVENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.InitEvent = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InitEvent)
        self.assertEqual(len(elem.disabled_modes), 1)
        child = elem.disabled_modes[0]
        self.assertIsInstance(child, ar_element.RModeInAtomicSwcInstanceRef)
        self.assertEqual(str(child.target_mode_declaration_ref), target_mode_decl_ref_str)

    def test_disabled_modes_from_list(self):
        context_port_ref_str = "/ComponentTypes/MyComponent/BswM_Mode"
        context_mode_decl_group_ref_str = "/PortInterfaces/BswM_ModeSwitchInterface/BswM_Mode"
        target_mode_decl_refs = ["/ModeDclrGroups/BswM_Mode/POSTRUN",
                                 "/ModeDclrGroups/BswM_Mode/STARTUP",
                                 "/ModeDclrGroups/BswM_Mode/SHUTDOWN",
                                 ]
        disabled_modes = []
        for target_mode_decl_ref in target_mode_decl_refs:
            context_port = ar_element.PortPrototypeRef(context_port_ref_str,
                                                       ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)
            context_mode_decl_group = ar_element.ModeDeclarationGroupPrototypeRef(context_mode_decl_group_ref_str)
            target_mode_decl = ar_element.ModeDeclarationRef(target_mode_decl_ref)
            disabled_modes.append(ar_element.RModeInAtomicSwcInstanceRef(
                context_port_ref=context_port,
                context_mode_declaration_group_prototype_ref=context_mode_decl_group,
                target_mode_declaration_ref=target_mode_decl))
        element = ar_element.InitEvent('MyName',
                                       disabled_modes=disabled_modes)
        writer = autosar.xml.Writer()
        xml = f'''<INIT-EVENT>
  <SHORT-NAME>MyName</SHORT-NAME>
  <DISABLED-MODE-IREFS>
    <DISABLED-MODE-IREF>
      <CONTEXT-PORT-REF DEST="R-PORT-PROTOTYPE">{context_port_ref_str}</CONTEXT-PORT-REF>
      <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">\
{context_mode_decl_group_ref_str}</CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF>
      <TARGET-MODE-DECLARATION-REF DEST="MODE-DECLARATION">{target_mode_decl_refs[0]}</TARGET-MODE-DECLARATION-REF>
    </DISABLED-MODE-IREF>
    <DISABLED-MODE-IREF>
      <CONTEXT-PORT-REF DEST="R-PORT-PROTOTYPE">{context_port_ref_str}</CONTEXT-PORT-REF>
      <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">\
{context_mode_decl_group_ref_str}</CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF>
      <TARGET-MODE-DECLARATION-REF DEST="MODE-DECLARATION">{target_mode_decl_refs[1]}</TARGET-MODE-DECLARATION-REF>
    </DISABLED-MODE-IREF>
    <DISABLED-MODE-IREF>
      <CONTEXT-PORT-REF DEST="R-PORT-PROTOTYPE">{context_port_ref_str}</CONTEXT-PORT-REF>
      <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF DEST="MODE-DECLARATION-GROUP-PROTOTYPE">\
{context_mode_decl_group_ref_str}</CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF>
      <TARGET-MODE-DECLARATION-REF DEST="MODE-DECLARATION">{target_mode_decl_refs[2]}</TARGET-MODE-DECLARATION-REF>
    </DISABLED-MODE-IREF>
  </DISABLED-MODE-IREFS>
</INIT-EVENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.InitEvent = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InitEvent)
        self.assertEqual(len(elem.disabled_modes), 3)
        child = elem.disabled_modes[0]
        self.assertIsInstance(child, ar_element.RModeInAtomicSwcInstanceRef)
        self.assertEqual(str(child.target_mode_declaration_ref), target_mode_decl_refs[0])
        child = elem.disabled_modes[1]
        self.assertIsInstance(child, ar_element.RModeInAtomicSwcInstanceRef)
        self.assertEqual(str(child.target_mode_declaration_ref), target_mode_decl_refs[1])
        child = elem.disabled_modes[2]
        self.assertIsInstance(child, ar_element.RModeInAtomicSwcInstanceRef)
        self.assertEqual(str(child.target_mode_declaration_ref), target_mode_decl_refs[2])

    def test_start_on_event(self):
        ref_str = '/ComponentTypes/MyComponent/MyComponent_InternalBehavior/MyComponent_Init'
        element = ar_element.InitEvent('MyName',
                                       start_on_event=ar_element.RunnableEntityRef(ref_str))
        writer = autosar.xml.Writer()
        xml = f'''<INIT-EVENT>
  <SHORT-NAME>MyName</SHORT-NAME>
  <START-ON-EVENT-REF DEST="RUNNABLE-ENTITY">{ref_str}</START-ON-EVENT-REF>
</INIT-EVENT>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.InitEvent = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.InitEvent)
        self.assertEqual(str(elem.start_on_event), ref_str)


class TestSwcInternalBehavior(unittest.TestCase):
    """
    Most elements are not implemented yet
    """

    def test_name_only(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwcInternalBehavior('MyName')
        xml = '''<SWC-INTERNAL-BEHAVIOR>
  <SHORT-NAME>MyName</SHORT-NAME>
</SWC-INTERNAL-BEHAVIOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcInternalBehavior = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcInternalBehavior)
        self.assertEqual(elem.name, 'MyName')
        self.assertEqual(elem.short_name, 'MyName')

    # Base class elements
    # IMPLEMENT LATER: CONSTANT-MEMORYS
    # IMPLEMENT LATER: CONSTANT-VALUE-MAPPING-REFS
    # IMPLEMENT LATER: DATA-TYPE-MAPPING-REFS
    # IMPLEMENT LATER: EXCLUSIVE-AREAS
    # IMPLEMENT LATER: EXCLUSIVE-AREA-NESTING-ORDERS
    # IMPLEMENT LATER: STATIC-MEMORYS
    # Class elements
    # IMPLEMENT LATER: AR-TYPED-PER-INSTANCE-MEMORYS
    # IMPLEMENT LATER: EVENTS
    # IMPLEMENT LATER: EXCLUSIVE-AREA-POLICYS
    # IMPLEMENT LATER: EXPLICIT-INTER-RUNNABLE-VARIABLES
    # IMPLEMENT LATER: HANDLE-TERMINATION-AND-RESTART
    # IMPLEMENT LATER: IMPLICIT-INTER-RUNNABLE-VARIABLES
    # IMPLEMENT LATER: INCLUDED-DATA-TYPE-SETS
    # IMPLEMENT LATER: INCLUDED-MODE-DECLARATION-GROUP-SETS
    # IMPLEMENT LATER: INSTANTIATION-DATA-DEF-PROPSS
    # IMPLEMENT LATER: PER-INSTANCE-MEMORYS
    # IMPLEMENT LATER: PER-INSTANCE-PARAMETERS
    # IMPLEMENT LATER: PORT-API-OPTIONS

    # RUNNABLES

    def test_runnables_from_element(self):
        writer = autosar.xml.Writer()
        element = ar_element.SwcInternalBehavior('MyName', runnables=ar_element.RunnableEntity("MyRunnable"))
        xml = '''<SWC-INTERNAL-BEHAVIOR>
  <SHORT-NAME>MyName</SHORT-NAME>
  <RUNNABLES>
    <RUNNABLE-ENTITY>
      <SHORT-NAME>MyRunnable</SHORT-NAME>
    </RUNNABLE-ENTITY>
  </RUNNABLES>
</SWC-INTERNAL-BEHAVIOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcInternalBehavior = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcInternalBehavior)
        self.assertEqual(len(elem.runnables), 1)
        runnable = elem.runnables[0]
        self.assertIsInstance(runnable, ar_element.RunnableEntity)

    def test_runnables_from_list(self):
        writer = autosar.xml.Writer()
        runnable1 = ar_element.RunnableEntity("MyRunnable1")
        runnable2 = ar_element.RunnableEntity("MyRunnable2")
        runnable3 = ar_element.RunnableEntity("MyRunnable3")
        element = ar_element.SwcInternalBehavior('MyName', runnables=[runnable1,
                                                                      runnable2,
                                                                      runnable3])
        xml = '''<SWC-INTERNAL-BEHAVIOR>
  <SHORT-NAME>MyName</SHORT-NAME>
  <RUNNABLES>
    <RUNNABLE-ENTITY>
      <SHORT-NAME>MyRunnable1</SHORT-NAME>
    </RUNNABLE-ENTITY>
    <RUNNABLE-ENTITY>
      <SHORT-NAME>MyRunnable2</SHORT-NAME>
    </RUNNABLE-ENTITY>
    <RUNNABLE-ENTITY>
      <SHORT-NAME>MyRunnable3</SHORT-NAME>
    </RUNNABLE-ENTITY>
  </RUNNABLES>
</SWC-INTERNAL-BEHAVIOR>'''
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcInternalBehavior = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcInternalBehavior)
        self.assertEqual(len(elem.runnables), 3)
        runnable = elem.runnables[0]
        self.assertIsInstance(runnable, ar_element.RunnableEntity)
        self.assertEqual(runnable.name, "MyRunnable1")
        runnable = elem.runnables[1]
        self.assertIsInstance(runnable, ar_element.RunnableEntity)
        self.assertEqual(runnable.name, "MyRunnable2")
        runnable = elem.runnables[2]
        self.assertIsInstance(runnable, ar_element.RunnableEntity)
        self.assertEqual(runnable.name, "MyRunnable3")

    # IMPLEMENT LATER: SERVICE-DEPENDENCYS"
    # IMPLEMENT LATER: SHARED-PARAMETERS
    # IMPLEMENT LATER: SUPPORTS-MULTIPLE-INSTANTIATION
    # NOT SUPPORTED: VARIATION-POINT-PROXYS
    # NOT SUPPORTED:  VARIATION-POINT


if __name__ == '__main__':
    unittest.main()
