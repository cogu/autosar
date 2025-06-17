"""
Application component example
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


def init_behavior_settings(workspace: ar_workspace.Workspace):
    """
    Define default event name prefixess
    """
    workspace.behavior_settings.update({
        "background_event_prefix": "BT",
        "data_receive_error_event_prefix": "DRET",
        "data_receive_event_prefix": "DRT",
        "init_event_prefix": "IT",
        "operation_invoked_event_prefix": "OIT",
        "swc_mode_manager_error_event_prefix": "MMET",
        "swc_mode_switch_event_prefix": "MST",
        "timing_event_prefix": "TMT",
        "data_send_point_prefix": "SEND",
        "data_receive_point_prefix": "REC"})


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
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=boolean_base_type.ref(),
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
    port_interface = ar_element.SenderReceiverInterface("EngineSpeed_I")
    port_interface.create_data_element("EngineSpeed", type_ref=uint16_impl_t.ref())
    workspace.add_element("PortInterfaces", port_interface)
    port_interface = ar_element.SenderReceiverInterface("VehicleSpeed_I")
    port_interface.create_data_element("VehicleSpeed", type_ref=uint16_impl_t.ref())
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


def create_application_component(workspace: autosar.xml.Workspace):
    """
    Creates application SWC with two sender ports
    """
    engine_speed_interface = workspace.find_element("PortInterfaces", "EngineSpeed_I")
    engine_speed_init = workspace.find_element("Constants", "EngineSpeed_IV")
    vehicle_speed_interface = workspace.find_element("PortInterfaces", "VehicleSpeed_I")
    vehicle_speed_init = workspace.find_element("Constants", "VehicleSpeed_IV")
    swc = ar_element.ApplicationSoftwareComponentType("SenderComponent")
    workspace.add_element("ComponentTypes", swc)

    # Create ports
    swc.create_provide_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "uses_end_to_end_protection": False})
    swc.create_provide_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
                                                                               "uses_end_to_end_protection": False})
    # Create internal behavior
    behavior = swc.create_internal_behavior()

    # Create Exclusive areas
    behavior.create_exclusive_area("ExampleExclusiveArea")

    # Create Runnables
    init_runnable_name = swc.name + '_Init'
    periodic_runnable_name = swc.name + '_Run'
    behavior.create_runnable(init_runnable_name,
                             can_be_invoked_concurrently=False, minimum_start_interval=0)
    runnable = behavior.create_runnable(periodic_runnable_name,
                                        can_be_invoked_concurrently=False,
                                        minimum_start_interval=0,
                                        can_enter_leave="ExampleExclusiveArea")
    runnable.create_port_access(["EngineSpeed", "VehicleSpeed"])
    # Create events
    behavior.create_init_event(init_runnable_name)
    behavior.create_timing_event(periodic_runnable_name, period=0.1)

    # Adding port API options
    behavior.create_port_api_options("*", enable_take_address=False, indirect_api=False)
    behavior.port_api_options["VehicleSpeed"].enable_take_address = True

    # Create SWC Implementation object
    impl = ar_element.SwcImplementation("SenderComponent_Implementation", behavior_ref=swc.internal_behavior.ref())
    workspace.add_element("ComponentTypes", impl)


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
    init_behavior_settings(workspace)
    create_platform_types(workspace)
    create_sender_receiver_port_interfaces(workspace)
    create_client_server_interfaces(workspace)
    create_constants(workspace)
    create_application_component(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
