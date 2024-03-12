"""
Composition component example
"""
import os
import autosar
import autosar.xml.element as ar_element


def create_platform_types(workspace: autosar.xml.Workspace):
    """
    Creates necessary platform types
    """
    boolean_base_type = ar_element.SwBaseType('boolean', size=8, encoding="BOOLEAN")
    workspace.add_element("PlatformBaseTypes", boolean_base_type)
    uint8_base_type = ar_element.SwBaseType('uint8', size=8)
    workspace.add_element("PlatformBaseTypes", uint8_base_type)
    uint16_base_type = ar_element.SwBaseType('uint16', size=16)
    workspace.add_element("PlatformBaseTypes", uint16_base_type)
    uint32_base_type = ar_element.SwBaseType('uint32', size=32)
    workspace.add_element("PlatformBaseTypes", uint32_base_type)
    boolean_data_constr = ar_element.DataConstraint.make_internal("boolean_DataConstr", 0, 1)
    workspace.add_element("PlatformDataConstraints", boolean_data_constr)
    computation = ar_element.Computation.make_value_table(["FALSE", "TRUE"])
    boolean_compu_method = ar_element.CompuMethod(name="boolean_CompuMethod",
                                                  category="TEXTTABLE",
                                                  int_to_phys=computation)
    workspace.add_element("PlatformCompuMethods", boolean_compu_method)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref(),
                                                             data_constraint_ref=boolean_data_constr.ref(),
                                                             compu_method_ref=boolean_compu_method.ref())
    boolean_impl_type = ar_element.ImplementationDataType("boolean",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", boolean_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", uint8_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint16_base_type.ref())
    uint16_impl_type = ar_element.ImplementationDataType("uint16",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", uint16_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint32_base_type.ref())
    uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", uint32_impl_type)


def create_sender_receiver_port_interfaces(workspace: autosar.xml.Workspace):
    """
    Creates necessary sender-receiver port interfaces
    """
    uint16_impl_t = workspace.find_element("PlatformImplementationDataTypes", "uint16")
    port_interface = ar_element.SenderReceiverInterface("VehicleSpeed_I")
    port_interface.create_data_element("VehicleSpeed", type_ref=uint16_impl_t.ref())
    workspace.add_element("PortInterfaces", port_interface)
    port_interface = ar_element.SenderReceiverInterface("EngineSpeed_I")
    port_interface.create_data_element("EngineSpeed", type_ref=uint16_impl_t.ref())
    workspace.add_element("PortInterfaces", port_interface)


def create_constants(workspace: autosar.xml.Workspace):
    """
    Creates init values in Constants package
    """
    constant = ar_element.ConstantSpecification.make_constant("VehicleSpeed_IV", 65535)
    workspace.add_element("Constants", constant)
    constant = ar_element.ConstantSpecification.make_constant("EngineSpeed_IV", 65535)
    workspace.add_element("Constants", constant)


def create_client_server_interfaces(workspace: autosar.xml.Workspace):
    """
    Creates client-server interface with one operation
    """
    uint32_impl_type = workspace.find_element("PlatformImplementationDataTypes", "uint32")
    boolean_impl_type = workspace.find_element("PlatformImplementationDataTypes", "boolean")
    port_interface = ar_element.ClientServerInterface("FreeRunningTimer_I")
    operation = port_interface.create_operation("GetTime")
    operation.create_out_argument("value", type_ref=uint32_impl_type.ref())
    operation = port_interface.create_operation("IsTimerElapsed")
    operation.create_in_argument("startTime", type_ref=uint32_impl_type.ref())
    operation.create_in_argument("duration", type_ref=uint32_impl_type.ref())
    operation.create_out_argument("result", type_ref=boolean_impl_type.ref())
    workspace.add_element("PortInterfaces", port_interface)


def create_receiver_component(workspace: autosar.xml.Workspace):
    """
    Creates application SWC with two receiver ports and one client port
    """
    timer_interface = workspace.find_element("PortInterfaces", "FreeRunningTimer_I")
    vehicle_speed_interface = workspace.find_element("PortInterfaces", "VehicleSpeed_I")
    vehicle_speed_init = workspace.find_element("Constants", "VehicleSpeed_IV")
    engine_speed_interface = workspace.find_element("PortInterfaces", "EngineSpeed_I")
    engine_speed_init = workspace.find_element("Constants", "EngineSpeed_IV")
    swc = ar_element.ApplicationSoftwareComponentType("ReceiverComponent")
    swc.create_require_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
                                                                               "alive_timeout": 0,
                                                                               "enable_update": False,
                                                                               "uses_end_to_end_protection": False,
                                                                               "handle_never_received": False
                                                                               })
    swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "alive_timeout": 0,
                                                                             "enable_update": False,
                                                                             "uses_end_to_end_protection": False,
                                                                             "handle_never_received": False
                                                                             })
    swc.create_require_port("FreeRunningTimer", timer_interface, com_spec={"GetTime": {}, "IsTimerElapsed": {}})
    workspace.add_element("ComponentTypes", swc)


def create_server_component(workspace: autosar.xml.Workspace):
    """
    Creates application SWC with one server port
    """
    timer_interface = workspace.find_element("PortInterfaces", "FreeRunningTimer_I")
    swc = ar_element.ApplicationSoftwareComponentType("TimerComponent")
    swc.create_provide_port("FreeRunningTimer", timer_interface, com_spec={"GetTime": {"queue_length": 1},
                                                                           "IsTimerElapsed": {"queue_length": 1}
                                                                           })
    workspace.add_element("ComponentTypes", swc)


def create_composition_component(workspace: autosar.xml.Workspace):
    """
    Creates composition component
    """
    vehicle_speed_interface = workspace.find_element("PortInterfaces", "VehicleSpeed_I")
    vehicle_speed_init = workspace.find_element("Constants", "VehicleSpeed_IV")
    engine_speed_interface = workspace.find_element("PortInterfaces", "EngineSpeed_I")
    engine_speed_init = workspace.find_element("Constants", "EngineSpeed_IV")
    swc = ar_element.CompositionSwComponentType("CompositionComponent")
    swc.create_require_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
                                                                               "uses_end_to_end_protection": False})
    swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "uses_end_to_end_protection": False})

    swc.create_component_prototype(workspace.find_element("ComponentTypes", "ReceiverComponent"))
    swc.create_component_prototype(workspace.find_element("ComponentTypes", "TimerComponent"))
    # Element must be added to workspace before connectors can be created
    workspace.add_element("ComponentTypes", swc)
    swc.create_connector("TimerComponent/FreeRunningTimer", "ReceiverComponent/FreeRunningTimer", workspace)
    swc.create_connector("VehicleSpeed", "ReceiverComponent/VehicleSpeed", workspace)
    swc.create_connector("EngineSpeed", "ReceiverComponent/EngineSpeed", workspace)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace as XML documents
    """
    interface_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'portinterfaces.arxml'))
    platform_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'platform.arxml'))
    component_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'composition.arxml'))
    constant_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'constants.arxml'))
    workspace.create_document(interface_document_path, packages="/PortInterfaces")
    workspace.create_document(constant_document_path, packages="/Constants")
    workspace.create_document(platform_document_path, packages="/AUTOSAR_Platform")
    workspace.create_document(component_document_path, packages="/ComponentTypes")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    workspace.init_package_map({"PlatformBaseTypes": "AUTOSAR_Platform/BaseTypes",
                                "PlatformImplementationDataTypes": "AUTOSAR_Platform/ImplementationDataTypes",
                                "PlatformDataConstraints": "AUTOSAR_Platform/DataConstraints",
                                "PlatformCompuMethods": "AUTOSAR_Platform/CompuMethods",
                                "Constants": "Constants",
                                "PortInterfaces": "PortInterfaces",
                                "ComponentTypes": "ComponentTypes"})
    create_platform_types(workspace)
    create_sender_receiver_port_interfaces(workspace)
    create_client_server_interfaces(workspace)
    create_constants(workspace)
    create_receiver_component(workspace)
    create_server_component(workspace)
    create_composition_component(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
