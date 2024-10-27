"""
Composition component example
"""
import os
import autosar
import autosar.xml.element as ar_element
import autosar.xml.workspace as ar_workspace


def create_package_map(workspace: ar_workspace.Workspace):
    """
    Creates package map in workspace
    """
    workspace.create_package_map({"PlatformBaseTypes": "AUTOSAR_Platform/BaseTypes",
                                  "PlatformImplementationDataTypes": "AUTOSAR_Platform/ImplementationDataTypes",
                                  "PlatformDataConstraints": "AUTOSAR_Platform/DataConstraints",
                                  "PlatformCompuMethods": "AUTOSAR_Platform/CompuMethods",
                                  "Constants": "Constants",
                                  "PortInterfaces": "PortInterfaces",
                                  "ComponentTypes": "ComponentTypes"})


def create_behavior_settings(workspace: ar_workspace.Workspace):
    """
    Define default event name prefixess
    """
    workspace.behavior_settings.update({
        "background_event_prefix": "BT_",
        "data_receive_error_event_prefix": "DRET_",
        "data_receive_event_prefix": "DRT_",
        "init_event_prefix": "IT_",
        "operation_invoked_event_prefix": "OIT_",
        "swc_mode_manager_error_event_prefix": "MMET_",
        "swc_mode_switch_event_prefix": "MST_",
        "timing_event_prefix": "TMT_"})


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
    constant = ar_element.ConstantSpecification.make_constant("EngineSpeed_IV", 65535)
    workspace.add_element("Constants", constant)
    constant = ar_element.ConstantSpecification.make_constant("VehicleSpeed_IV", 65535)
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
    engine_speed_interface = workspace.find_element("PortInterfaces", "EngineSpeed_I")
    engine_speed_init = workspace.find_element("Constants", "EngineSpeed_IV")
    vehicle_speed_interface = workspace.find_element("PortInterfaces", "VehicleSpeed_I")
    vehicle_speed_init = workspace.find_element("Constants", "VehicleSpeed_IV")
    swc = ar_element.ApplicationSoftwareComponentType("ReceiverComponent")
    workspace.add_element("ComponentTypes", swc)
    swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "alive_timeout": 0,
                                                                             "enable_update": False,
                                                                             "uses_end_to_end_protection": False,
                                                                             "handle_never_received": False
                                                                             })
    swc.create_require_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
                                                                               "alive_timeout": 0,
                                                                               "enable_update": False,
                                                                               "uses_end_to_end_protection": False,
                                                                               "handle_never_received": False
                                                                               })
    swc.create_require_port("FreeRunningTimer", timer_interface, com_spec={"GetTime": {}, "IsTimerElapsed": {}})

    init_runnable_name = swc.name + '_Init'
    periodic_runnable_name = swc.name + '_Run'
    behavior = swc.create_internal_behavior()
    behavior.create_runnable(init_runnable_name)
    behavior.create_runnable(periodic_runnable_name)
    behavior.create_init_event(init_runnable_name)
    behavior.create_timing_event(periodic_runnable_name, 0.1)
    impl = ar_element.SwcImplementation("ReceiverComponent_Implementation", behavior_ref=behavior.ref())
    workspace.add_element("ComponentTypes", impl)


def create_server_component(workspace: autosar.xml.Workspace):
    """
    Creates application SWC with one server port
    """
    timer_interface = workspace.find_element("PortInterfaces", "FreeRunningTimer_I")
    swc = ar_element.ApplicationSoftwareComponentType("TimerComponent")
    workspace.add_element("ComponentTypes", swc)
    swc.create_provide_port("FreeRunningTimer", timer_interface, com_spec={"GetTime": {"queue_length": 1},
                                                                           "IsTimerElapsed": {"queue_length": 1}
                                                                           })
    init_runnable_name = swc.name + '_Init'
    get_time_runnable_name = "TimerComponent_FreeRunningTimer_GetTime"
    is_timer_elapsed_runnable_name = "TimerComponent_FreeRunningTimer_IsTimerElapsed"
    behavior = swc.create_internal_behavior()
    behavior.create_runnable(init_runnable_name)
    behavior.create_runnable(get_time_runnable_name)
    behavior.create_runnable(is_timer_elapsed_runnable_name)
    behavior.create_init_event(init_runnable_name)
    behavior.create_operation_invoked_event(get_time_runnable_name, "FreeRunningTimer/GetTime")
    behavior.create_operation_invoked_event(is_timer_elapsed_runnable_name, "FreeRunningTimer/IsTimerElapsed")
    impl = ar_element.SwcImplementation("TimerComponent_Implementation", behavior_ref=behavior.ref())
    workspace.add_element("ComponentTypes", impl)


def create_composition_component(workspace: autosar.xml.Workspace):
    """
    Creates composition component
    """
    engine_speed_interface = workspace.find_element("PortInterfaces", "EngineSpeed_I")
    engine_speed_init = workspace.find_element("Constants", "EngineSpeed_IV")
    vehicle_speed_interface = workspace.find_element("PortInterfaces", "VehicleSpeed_I")
    vehicle_speed_init = workspace.find_element("Constants", "VehicleSpeed_IV")
    swc = ar_element.CompositionSwComponentType("CompositionComponent")
    swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "uses_end_to_end_protection": False})
    swc.create_require_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
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
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("portinterfaces.arxml", packages="/PortInterfaces")
    workspace.create_document("constants.arxml", packages="/Constants")
    workspace.create_document("platform.arxml", packages="/AUTOSAR_Platform")
    workspace.create_document_mapping(package_ref="/ComponentTypes",
                                      element_types=ar_element.SwComponentType,
                                      suffix_filters=["_Implementation"])
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    create_package_map(workspace)
    create_behavior_settings(workspace)
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
