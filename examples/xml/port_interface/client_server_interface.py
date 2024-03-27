"""
Sender-receiver port interface examples
"""
import os
import autosar.xml
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum


def create_platform_types(workspace: autosar.xml.Workspace):
    """
    Creates necessary platform types
    """
    uint8_base_type = ar_element.SwBaseType('uint8', size=8)
    workspace.add_element("PlatformBaseTypes", uint8_base_type)
    uint32_base_type = ar_element.SwBaseType('uint32', size=32)
    workspace.add_element("PlatformBaseTypes", uint32_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", uint8_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint32_base_type.ref())
    uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    workspace.add_element("PlatformImplementationDataTypes", uint32_impl_type)


def create_port_interfaces(workspace: autosar.xml.Workspace):
    """
    Creates client-server interface with one operation
    """
    uint32_impl_type = workspace.get_package("PlatformImplementationDataTypes").find("uint32")
    portinterface = ar_element.ClientServerInterface("FreeRunningTimer_I", is_service=True)
    operation = portinterface.create_operation("GetTimeStamp")
    operation.create_out_argument("value",
                                  ar_enum.ServerArgImplPolicy.USE_ARGUMENT_TYPE,
                                  type_ref=uint32_impl_type.ref())
    workspace.add_element("PortInterfaces", portinterface)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace into multiple XML documents
    """
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("client_server_interface.arxml", packages="/PortInterfaces")
    workspace.create_document("AUTOSAR_Platform.arxml", packages="/AUTOSAR_Platform")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"PlatformBaseTypes": "AUTOSAR_Platform/BaseTypes",
                                  "PlatformImplementationDataTypes": "AUTOSAR_Platform/ImplementationDataTypes",
                                  "PortInterfaces": "PortInterfaces"})

    create_platform_types(workspace)
    create_port_interfaces(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
