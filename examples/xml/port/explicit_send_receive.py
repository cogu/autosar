"""
Demonstrates explicit port access on s/r ports
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
        "data_send_point_prefix": "SEND",
        "data_receive_point_prefix": "REC"})


def create_platform_types(workspace: autosar.xml.Workspace):
    """
    Creates necessary platform types
    """
    uint8_base_type = ar_element.SwBaseType('uint8', size=8)
    workspace.add_element("PlatformBaseTypes", uint8_base_type)
    uint16_base_type = ar_element.SwBaseType('uint16', size=16)
    workspace.add_element("PlatformBaseTypes", uint16_base_type)
    uint32_base_type = ar_element.SwBaseType('uint32', size=32)
    workspace.add_element("PlatformBaseTypes", uint32_base_type)
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
    uint8_impl_t = workspace.find_element("PlatformImplementationDataTypes", "uint8")
    port_interface1 = ar_element.SenderReceiverInterface("SingleElement_I")
    port_interface1.create_data_element("Value", type_ref=uint8_impl_t.ref())
    workspace.add_element("PortInterfaces", port_interface1)
    uint16_impl_t = workspace.find_element("PlatformImplementationDataTypes", "uint16")
    port_interface2 = ar_element.SenderReceiverInterface("MultiElement_I")
    port_interface2.create_data_element("Value1", type_ref=uint16_impl_t.ref())
    port_interface2.create_data_element("Value2", type_ref=uint8_impl_t.ref())
    workspace.add_element("PortInterfaces", port_interface2)


def create_application_component(workspace: autosar.xml.Workspace):
    """
    Creates application SWC with two sender ports
    """
    single_element_interface = workspace.find_element("PortInterfaces", "SingleElement_I")
    multi_element_interface = workspace.find_element("PortInterfaces", "MultiElement_I")
    swc = ar_element.ApplicationSoftwareComponentType("ExplicitSendReceiveComponent")
    workspace.add_element("ComponentTypes", swc)

    # Create ports
    swc.create_r_port("MyReceivePort", multi_element_interface, com_spec=[("Value1", {"init_value": 65535}),
                                                                          ("Value2", {"init_value": 255})])
    swc.create_p_port("MySendPort", single_element_interface, com_spec={"init_value": 65535})

    # Create internal behavior
    behavior = swc.create_internal_behavior()

    # Create SWC Implementation object
    impl = ar_element.SwcImplementation(swc.name + "_Implementation", behavior_ref=swc.internal_behavior.ref())
    workspace.add_element("ComponentTypes", impl)

    # Create Runnables
    init_runnable_name = swc.name + '_Init'
    periodic_runnable_name = swc.name + '_Run'
    behavior.create_runnable(init_runnable_name,
                             can_be_invoked_concurrently=False,
                             minimum_start_interval=0)
    runnable = behavior.create_runnable(periodic_runnable_name,
                                        can_be_invoked_concurrently=False,
                                        minimum_start_interval=0)

    # Create Port access
    # For Ports with sender-receiver interface you use the "Port/DataElement" pattern.
    # A special case is when the port-interface only has a single elemeent. Then it's enough to just give the port name.
    #
    # Explicit receive on R-PORTS allows you to choose between "ARGUMENT" and "VALUE" using a port access prefix.
    # ARGUMENT (or ARG) will return the port value in an argument and also give you the receive result (OK/NOK etc.)
    # VALUE (or VAL) will return the port value directly from the function call but you will be unable to get the
    # result.
    # For R-PORTS, ARGUMENT is the default so you don't need to explicitly write it
    # For P-PORTS the only explicit option is SEND. This is the default so you don't need to explicitly write it.
    # In this example we do it anyway for completeness.
    # Before calling create_port_access, don't forget to set the name prefixes. See init_behavior_settings above.
    runnable.create_port_access(["VALUE: MyReceivePort/Value1",
                                 "ARGUMENT: MyReceivePort/Value2",
                                 "SEND: MySendPort"])


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves only the appliction component xml
    """
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document_mapping(package_ref="/ComponentTypes",
                                      element_types=ar_element.SwComponentType,
                                      suffix_filters=["_Implementation"])
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    init_behavior_settings(workspace)
    create_package_map(workspace)
    create_platform_types(workspace)
    create_sender_receiver_port_interfaces(workspace)
    create_application_component(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
