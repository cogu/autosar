"""
Sender-receiver port interface examples
"""
import os
import autosar
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum


def create_platform_types(packages: dict[str, ar_element.Package]):
    """
    Creates necessary platform types
    """
    uint8_base_type = ar_element.SwBaseType('uint8', size=8)
    packages["PlatformBaseTypes"].append(uint8_base_type)
    uint32_base_type = ar_element.SwBaseType('uint32', size=32)
    packages["PlatformBaseTypes"].append(uint32_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props)
    packages["PlatformImplementationDataTypes"].append(uint8_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint32_base_type.ref())
    uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    packages["PlatformImplementationDataTypes"].append(uint32_impl_type)


def create_port_interfaces(packages: dict[str, ar_element.Package]):
    """
    Creates client-server interface with one operation
    """
    uint32_impl_type = packages["PlatformImplementationDataTypes"].find("uint32")
    interface = ar_element.ClientServerInterface("FreeRunningTimer_I", is_service=True)
    operation = interface.create_operation("GetTimeStamp")
    operation.create_out_argument("value",
                                  ar_enum.ServerArgImplPolicy.USE_ARGUMENT_TYPE,
                                  type_ref=uint32_impl_type.ref())
    packages["PortInterfaces"].append(interface)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace as XML documents
    """
    interface_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'client_server_interface.arxml'))
    platform_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'platform.arxml'))
    workspace.create_document(interface_document_path, packages="/PortInterfaces")
    workspace.create_document(platform_document_path, packages="/AUTOSAR_Platform")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["PlatformBaseTypes",
                         "PlatformImplementationDataTypes",
                         "PortInterfaces"],
                    workspace.make_packages("AUTOSAR_Platform/BaseTypes",
                                            "AUTOSAR_Platform/ImplementationDataTypes",
                                            "PortInterfaces")))
    create_platform_types(packages)
    create_port_interfaces(packages)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
