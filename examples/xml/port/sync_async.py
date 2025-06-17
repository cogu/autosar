"""
Demonstrates synchronous/asynchronous port access on c/s ports
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
    workspace.behavior_settings.update({"server_call_point_prefix": "SC"})


def create_platform_types(workspace: autosar.xml.Workspace):
    """
    Creates necessary platform types
    """
    boolean_base_type = ar_element.SwBaseType('boolean', size=8, encoding="BOOLEAN")
    workspace.add_element("PlatformBaseTypes", boolean_base_type)
    # boolean
    boolean_data_constr = ar_element.DataConstraint.make_internal("boolean_DataConstr", 0, 1)
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
    # uint32
    uint32_base_type = ar_element.SwBaseType('uint32', size=32)
    workspace.add_element("PlatformBaseTypes", uint32_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint32_base_type.ref())
    uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", uint32_impl_type)


def create_client_server_interfaces(workspace: autosar.xml.Workspace):
    """
    Creates client-server interface with one operation
    """
    boolean_impl_type = workspace.find_element("PlatformImplementationDataTypes", "boolean")
    uint32_impl_type = workspace.find_element("PlatformImplementationDataTypes", "uint32")
    port_interface = ar_element.ClientServerInterface("Timer_I")
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
    timer_interface = workspace.find_element("PortInterfaces", "Timer_I")
    swc = ar_element.ApplicationSoftwareComponentType("SyncAsyncCallerComponent")
    workspace.add_element("ComponentTypes", swc)

    # Create ports
    swc.create_r_port("Timer", timer_interface)

    # Create internal behavior
    behavior = swc.create_internal_behavior()

    # Create SWC Implementation
    impl = ar_element.SwcImplementation(swc.name + "_Implementation", behavior_ref=swc.internal_behavior.ref())
    workspace.add_element("ComponentTypes", impl)

    # Create Runnables
    init_runnable_name = swc.name + '_Init'
    periodic_runnable_name = swc.name + '_Run'
    behavior.create_runnable(init_runnable_name)
    runnable = behavior.create_runnable(periodic_runnable_name)

    # Create port access
    # For client-server interfaces on R-PORTS you declare port access using the "port/operation" pattern
    # By default, all port accesses are synchronous but you can give it the "ASYNC" prefix to make it
    # asynchronous.
    # Before calling create_port_access, don't forget to set the name prefixes. See init_behavior_settings above.
    runnable.create_port_access(["ASYNC: Timer/GetTime",
                                 "SYNC: Timer/IsTimerElapsed"])


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
    create_client_server_interfaces(workspace)
    create_application_component(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
