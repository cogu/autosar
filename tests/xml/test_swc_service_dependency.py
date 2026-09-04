"""Unit tests for SWC service dependency elements."""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element  # noqa: E402
import autosar.xml.enumeration as ar_enum  # noqa: E402
import autosar  # noqa: E402


class TestPortGroupRef(unittest.TestCase):

    def test_default_dest(self):
        ref = ar_element.PortGroupRef("/PortGroups/PortGroup1")
        self.assertEqual(ref.value, "/PortGroups/PortGroup1")
        self.assertEqual(ref.dest, ar_enum.IdentifiableSubTypes.PORT_GROUP)

    def test_accepted_sub_types(self):
        self.assertEqual(
            ar_element.PortGroupRef.accepted_sub_types(),
            {ar_enum.IdentifiableSubTypes.PORT_GROUP}
        )


class TestSymbolicNameProps(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.SymbolicNameProps("MySymbolicProps")
        writer = autosar.xml.Writer()
        xml = """<SYMBOLIC-NAME-PROPS>
  <SHORT-NAME>MySymbolicProps</SHORT-NAME>
</SYMBOLIC-NAME-PROPS>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SymbolicNameProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SymbolicNameProps)
        self.assertEqual(elem.name, "MySymbolicProps")
        self.assertIsNone(elem.symbol)

    def test_with_symbol(self):
        element = ar_element.SymbolicNameProps("MySymbolicProps", symbol="SYM_PORT_1")
        writer = autosar.xml.Writer()
        xml = """<SYMBOLIC-NAME-PROPS>
  <SHORT-NAME>MySymbolicProps</SHORT-NAME>
  <SYMBOL>SYM_PORT_1</SYMBOL>
</SYMBOLIC-NAME-PROPS>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SymbolicNameProps = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SymbolicNameProps)
        self.assertEqual(elem.name, "MySymbolicProps")
        self.assertEqual(elem.symbol, "SYM_PORT_1")


class TestRoleBasedDataAssignment(unittest.TestCase):

    def test_role_only(self):
        element = ar_element.RoleBasedDataAssignment(role="DataRole1")
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-DATA-ASSIGNMENT>
  <ROLE>DataRole1</ROLE>
</ROLE-BASED-DATA-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedDataAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedDataAssignment)
        self.assertEqual(elem.role, "DataRole1")
        self.assertIsNone(elem.used_data_element)
        self.assertIsNone(elem.used_parameter_element)
        self.assertIsNone(elem.used_pim_ref)

    def test_with_used_pim_ref(self):
        element = ar_element.RoleBasedDataAssignment(
            role="PimRole",
            used_pim_ref=ar_element.PerInstanceMemoryRef("/Components/MySwc/InternalBehavior/Pim1")
        )
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-DATA-ASSIGNMENT>
  <ROLE>PimRole</ROLE>
  <USED-PIM-REF DEST="PER-INSTANCE-MEMORY">/Components/MySwc/InternalBehavior/Pim1</USED-PIM-REF>
</ROLE-BASED-DATA-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedDataAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedDataAssignment)
        self.assertEqual(elem.role, "PimRole")
        self.assertIsInstance(elem.used_pim_ref, ar_element.PerInstanceMemoryRef)
        self.assertEqual(elem.used_pim_ref.value, "/Components/MySwc/InternalBehavior/Pim1")
        self.assertEqual(elem.used_pim_ref.dest, ar_enum.IdentifiableSubTypes.PER_INSTANCE_MEMORY)

    def test_with_used_data_element(self):
        var_iref = ar_element.VariableInAtomicSWCTypeInstanceRef(
            port_prototype_ref=ar_element.PortPrototypeRef(
                "/Components/MySwc/Port1",
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE
            ),
            target_data_prototype_ref=ar_element.DataPrototypeRef(
                "/Interfaces/MyIf/Element1",
                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE
            )
        )
        used_data = ar_element.AutosarVariableRef(ar_variable_iref=var_iref)
        element = ar_element.RoleBasedDataAssignment(
            role="DataRole",
            used_data_element=used_data
        )
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-DATA-ASSIGNMENT>
  <ROLE>DataRole</ROLE>
  <USED-DATA-ELEMENT>
    <AUTOSAR-VARIABLE-IREF>
      <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">/Components/MySwc/Port1</PORT-PROTOTYPE-REF>
      <TARGET-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">/Interfaces/MyIf/Element1</TARGET-DATA-PROTOTYPE-REF>
    </AUTOSAR-VARIABLE-IREF>
  </USED-DATA-ELEMENT>
</ROLE-BASED-DATA-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedDataAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedDataAssignment)
        self.assertEqual(elem.role, "DataRole")
        self.assertIsInstance(elem.used_data_element, ar_element.AutosarVariableRef)
        self.assertEqual(elem.used_data_element.ar_variable_iref.port_prototype_ref.value, "/Components/MySwc/Port1")

    def test_with_used_parameter_element(self):
        param_iref = ar_element.ParameterInAtomicSwcTypeInstanceRef(
            port_prototype=ar_element.PortPrototypeRef(
                "/Components/MySwc/Port1",
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE
            ),
            target_data_prototype=ar_element.DataPrototypeRef(
                "/Interfaces/ParamIf/Param1",
                ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE
            )
        )
        used_param = ar_element.AutosarParameterRef(autosar_parameter=param_iref)
        element = ar_element.RoleBasedDataAssignment(
            role="ParamRole",
            used_parameter_element=used_param
        )
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-DATA-ASSIGNMENT>
  <ROLE>ParamRole</ROLE>
  <USED-PARAMETER-ELEMENT>
    <AUTOSAR-PARAMETER-IREF>
      <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">/Components/MySwc/Port1</PORT-PROTOTYPE-REF>
      <TARGET-DATA-PROTOTYPE-REF DEST="PARAMETER-DATA-PROTOTYPE">/Interfaces/ParamIf/Param1</TARGET-DATA-PROTOTYPE-REF>
    </AUTOSAR-PARAMETER-IREF>
  </USED-PARAMETER-ELEMENT>
</ROLE-BASED-DATA-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedDataAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedDataAssignment)
        self.assertEqual(elem.role, "ParamRole")
        self.assertIsInstance(elem.used_parameter_element, ar_element.AutosarParameterRef)
        self.assertEqual(elem.used_parameter_element.autosar_parameter.port_prototype.value, "/Components/MySwc/Port1")


class TestRoleBasedDataTypeAssignment(unittest.TestCase):

    def test_role_only(self):
        element = ar_element.RoleBasedDataTypeAssignment(role="TypeRole1")
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-DATA-TYPE-ASSIGNMENT>
  <ROLE>TypeRole1</ROLE>
</ROLE-BASED-DATA-TYPE-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedDataTypeAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedDataTypeAssignment)
        self.assertEqual(elem.role, "TypeRole1")
        self.assertIsNone(elem.used_implementation_data_type_ref)

    def test_with_used_implementation_data_type_ref(self):
        element = ar_element.RoleBasedDataTypeAssignment(
            role="TypeRole2",
            used_implementation_data_type_ref=ar_element.ImplementationDataTypeRef("/DataTypes/u8")
        )
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-DATA-TYPE-ASSIGNMENT>
  <ROLE>TypeRole2</ROLE>
  <USED-IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/DataTypes/u8</USED-IMPLEMENTATION-DATA-TYPE-REF>
</ROLE-BASED-DATA-TYPE-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedDataTypeAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedDataTypeAssignment)
        self.assertEqual(elem.role, "TypeRole2")
        self.assertIsInstance(elem.used_implementation_data_type_ref, ar_element.ImplementationDataTypeRef)
        self.assertEqual(elem.used_implementation_data_type_ref.value, "/DataTypes/u8")


class TestRoleBasedPortAssignment(unittest.TestCase):

    def test_role_only(self):
        element = ar_element.RoleBasedPortAssignment(role="PortRole1")
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-PORT-ASSIGNMENT>
  <ROLE>PortRole1</ROLE>
</ROLE-BASED-PORT-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedPortAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedPortAssignment)
        self.assertEqual(elem.role, "PortRole1")
        self.assertIsNone(elem.port_prototype_ref)

    def test_with_port_prototype_ref(self):
        element = ar_element.RoleBasedPortAssignment(
            port_prototype_ref=ar_element.PortPrototypeRef(
                "/Components/MySwc/Port1",
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE
            ),
            role="PortRole2"
        )
        writer = autosar.xml.Writer()
        xml = """<ROLE-BASED-PORT-ASSIGNMENT>
  <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">/Components/MySwc/Port1</PORT-PROTOTYPE-REF>
  <ROLE>PortRole2</ROLE>
</ROLE-BASED-PORT-ASSIGNMENT>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.RoleBasedPortAssignment = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.RoleBasedPortAssignment)
        self.assertEqual(elem.role, "PortRole2")
        self.assertIsInstance(elem.port_prototype_ref, ar_element.PortPrototypeRef)
        self.assertEqual(elem.port_prototype_ref.value, "/Components/MySwc/Port1")


class TestSwcServiceDependency(unittest.TestCase):

    def test_name_only(self):
        element = ar_element.SwcServiceDependency("MyServiceDep")
        writer = autosar.xml.Writer()
        xml = """<SWC-SERVICE-DEPENDENCY>
  <SHORT-NAME>MyServiceDep</SHORT-NAME>
</SWC-SERVICE-DEPENDENCY>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcServiceDependency = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcServiceDependency)
        self.assertIsInstance(elem, ar_element.ServiceDependency)
        self.assertEqual(elem.name, "MyServiceDep")

    def test_full_service_dependency(self):
        data_type_assign = ar_element.RoleBasedDataTypeAssignment(
            role="NvDataType",
            used_implementation_data_type_ref="/T/a"
        )
        data_assign = ar_element.RoleBasedDataAssignment(
            role="PimData",
            used_pim_ref="/Components/MySwc/IB/Pim1"
        )
        port_assign = ar_element.RoleBasedPortAssignment(
            port_prototype_ref=ar_element.PortPrototypeRef(
                "/Components/MySwc/NvMNotifyPort",
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE
            ),
            role="JobFinishedNotification"
        )
        symbolic_props = ar_element.SymbolicNameProps("SymProps", symbol="NVM_BLOCK_1")
        service_needs = ar_element.NvBlockNeeds(
            "NvNeeds1",
            n_data_sets=1,
            ram_block_status_control=ar_enum.RamBlockStatusControl.API
        )

        element = ar_element.SwcServiceDependency(
            "MyNvBlockDep",
            assigned_data_types=data_type_assign,
            diagnostic_relevance=ar_enum.ServiceDiagnosticRelevance.IS_RELEVANT,
            symbolic_name_props=symbolic_props,
            assigned_datas=data_assign,
            assigned_ports=port_assign,
            represented_port_group_ref="/PortGroups/MyPortGroup",
            service_needs=service_needs
        )

        writer = autosar.xml.Writer()
        xml = """<SWC-SERVICE-DEPENDENCY>
  <SHORT-NAME>MyNvBlockDep</SHORT-NAME>
  <ASSIGNED-DATA-TYPES>
    <ROLE-BASED-DATA-TYPE-ASSIGNMENT>
      <ROLE>NvDataType</ROLE>
      <USED-IMPLEMENTATION-DATA-TYPE-REF DEST="IMPLEMENTATION-DATA-TYPE">/T/a</USED-IMPLEMENTATION-DATA-TYPE-REF>
    </ROLE-BASED-DATA-TYPE-ASSIGNMENT>
  </ASSIGNED-DATA-TYPES>
  <DIAGNOSTIC-RELEVANCE>IS-RELEVANT</DIAGNOSTIC-RELEVANCE>
  <SYMBOLIC-NAME-PROPS>
    <SHORT-NAME>SymProps</SHORT-NAME>
    <SYMBOL>NVM_BLOCK_1</SYMBOL>
  </SYMBOLIC-NAME-PROPS>
  <ASSIGNED-DATAS>
    <ROLE-BASED-DATA-ASSIGNMENT>
      <ROLE>PimData</ROLE>
      <USED-PIM-REF DEST="PER-INSTANCE-MEMORY">/Components/MySwc/IB/Pim1</USED-PIM-REF>
    </ROLE-BASED-DATA-ASSIGNMENT>
  </ASSIGNED-DATAS>
  <ASSIGNED-PORTS>
    <ROLE-BASED-PORT-ASSIGNMENT>
      <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">/Components/MySwc/NvMNotifyPort</PORT-PROTOTYPE-REF>
      <ROLE>JobFinishedNotification</ROLE>
    </ROLE-BASED-PORT-ASSIGNMENT>
  </ASSIGNED-PORTS>
  <REPRESENTED-PORT-GROUP-REF DEST="PORT-GROUP">/PortGroups/MyPortGroup</REPRESENTED-PORT-GROUP-REF>
  <SERVICE-NEEDS>
    <NV-BLOCK-NEEDS>
      <SHORT-NAME>NvNeeds1</SHORT-NAME>
      <N-DATA-SETS>1</N-DATA-SETS>
      <RAM-BLOCK-STATUS-CONTROL>API</RAM-BLOCK-STATUS-CONTROL>
    </NV-BLOCK-NEEDS>
  </SERVICE-NEEDS>
</SWC-SERVICE-DEPENDENCY>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcServiceDependency = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcServiceDependency)
        self.assertEqual(elem.name, "MyNvBlockDep")
        self.assertEqual(len(elem.assigned_data_types), 1)
        self.assertEqual(elem.assigned_data_types[0].role, "NvDataType")
        self.assertEqual(elem.diagnostic_relevance, ar_enum.ServiceDiagnosticRelevance.IS_RELEVANT)
        self.assertIsInstance(elem.symbolic_name_props, ar_element.SymbolicNameProps)
        self.assertEqual(elem.symbolic_name_props.symbol, "NVM_BLOCK_1")
        self.assertEqual(len(elem.assigned_datas), 1)
        self.assertEqual(elem.assigned_datas[0].role, "PimData")
        self.assertEqual(len(elem.assigned_ports), 1)
        self.assertEqual(elem.assigned_ports[0].role, "JobFinishedNotification")
        self.assertIsInstance(elem.represented_port_group_ref, ar_element.PortGroupRef)
        self.assertEqual(elem.represented_port_group_ref.value, "/PortGroups/MyPortGroup")
        self.assertIsInstance(elem.service_needs, ar_element.NvBlockNeeds)
        self.assertEqual(elem.service_needs.name, "NvNeeds1")
        self.assertEqual(elem.service_needs.n_data_sets, 1)
        self.assertEqual(elem.service_needs.ram_block_status_control, ar_enum.RamBlockStatusControl.API)

    def test_diagnostic_event_needs_service_dependency(self):
        diag_needs = ar_element.DiagnosticEventNeeds("DTC_Needs_1")
        element = ar_element.SwcServiceDependency("DiagServiceDep", service_needs=diag_needs)
        writer = autosar.xml.Writer()
        xml = """<SWC-SERVICE-DEPENDENCY>
  <SHORT-NAME>DiagServiceDep</SHORT-NAME>
  <SERVICE-NEEDS>
    <DIAGNOSTIC-EVENT-NEEDS>
      <SHORT-NAME>DTC_Needs_1</SHORT-NAME>
    </DIAGNOSTIC-EVENT-NEEDS>
  </SERVICE-NEEDS>
</SWC-SERVICE-DEPENDENCY>"""
        self.assertEqual(writer.write_str_elem(element), xml)
        reader = autosar.xml.Reader()
        elem: ar_element.SwcServiceDependency = reader.read_str_elem(xml)
        self.assertIsInstance(elem, ar_element.SwcServiceDependency)
        self.assertIsInstance(elem.service_needs, ar_element.DiagnosticEventNeeds)
        self.assertEqual(elem.service_needs.name, "DTC_Needs_1")


class TestSwcInternalBehaviorServiceDependency(unittest.TestCase):

    def test_service_dependency_in_behavior(self):
        behavior = ar_element.SwcInternalBehavior("MyBehavior")
        dep = behavior.create_service_dependency(
            "NvM_Block1",
            service_needs=ar_element.NvBlockNeeds("Block1_Needs")
        )
        self.assertIsInstance(dep, ar_element.SwcServiceDependency)
        self.assertEqual(dep.parent, behavior)
        self.assertEqual(len(behavior.service_dependency), 1)

        writer = autosar.xml.Writer()
        xml = """<SWC-INTERNAL-BEHAVIOR>
  <SHORT-NAME>MyBehavior</SHORT-NAME>
  <SERVICE-DEPENDENCYS>
    <SWC-SERVICE-DEPENDENCY>
      <SHORT-NAME>NvM_Block1</SHORT-NAME>
      <SERVICE-NEEDS>
        <NV-BLOCK-NEEDS>
          <SHORT-NAME>Block1_Needs</SHORT-NAME>
        </NV-BLOCK-NEEDS>
      </SERVICE-NEEDS>
    </SWC-SERVICE-DEPENDENCY>
  </SERVICE-DEPENDENCYS>
</SWC-INTERNAL-BEHAVIOR>"""
        self.assertEqual(writer.write_str_elem(behavior), xml)
        reader = autosar.xml.Reader()
        read_behavior: ar_element.SwcInternalBehavior = reader.read_str_elem(xml)
        self.assertIsInstance(read_behavior, ar_element.SwcInternalBehavior)
        self.assertEqual(len(read_behavior.service_dependency), 1)
        self.assertEqual(read_behavior.service_dependency[0].name, "NvM_Block1")
        self.assertIsInstance(read_behavior.service_dependency[0].service_needs, ar_element.NvBlockNeeds)
        self.assertEqual(read_behavior.service_dependency[0].service_needs.name, "Block1_Needs")

    def test_service_dependency_init_list(self):
        dep1 = ar_element.SwcServiceDependency("Dep1")
        dep2 = ar_element.SwcServiceDependency("Dep2")
        behavior = ar_element.SwcInternalBehavior("MyBehavior", service_dependency=[dep1, dep2])
        self.assertEqual(len(behavior.service_dependency), 2)
        self.assertEqual(behavior.service_dependency[0].name, "Dep1")
        self.assertEqual(behavior.service_dependency[1].name, "Dep2")


if __name__ == '__main__':
    unittest.main()
