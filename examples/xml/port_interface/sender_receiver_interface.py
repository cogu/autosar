"""
Sender-receiver port interface examples
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


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


def create_implementation_data_types(workspace: autosar.xml.Workspace):
    """
    Creates non-platform implementation data types
    """
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="AUTOSAR_Platform/BaseTypes/uint8")
    inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
    workspace.add_element("ImplementationDataTypes", inactive_active_t)


def create_sender_receiver_interface_with_one_element(workspace: autosar.xml.Workspace):
    """
    Creates interface with one element
    """
    inactive_active_t: ar_element.ImplementationDataType
    inactive_active_t = workspace.get_package("ImplementationDataTypes").find("InactiveActive_T")
    portinterface = ar_element.SenderReceiverInterface("HeadLightStatus_I")
    portinterface.create_data_element("HeadLightStatus", type_ref=inactive_active_t.ref())
    workspace.add_element("PortInterfaces", portinterface)


def create_sender_receiver_interface_with_two_elements(workspace: autosar.xml.Workspace):
    """
    Creates interface with two elements
    """
    inactive_active_t: ar_element.ImplementationDataType
    inactive_active_t = workspace.get_package("ImplementationDataTypes").find("InactiveActive_T")
    portinterface = ar_element.SenderReceiverInterface("InterfaceName")
    portinterface.create_data_element("Element1", type_ref=inactive_active_t.ref())
    portinterface.create_data_element("Element2", type_ref=inactive_active_t.ref())
    workspace.add_element("PortInterfaces", portinterface)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace into multiple XML documents
    """
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("sender_receiver_interface.arxml", packages="/PortInterfaces")
    workspace.create_document("datatypes.arxml", packages="/DataTypes")
    workspace.create_document("AUTOSAR_Platform.arxml", packages="/AUTOSAR_Platform")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"PlatformBaseTypes": "AUTOSAR_Platform/BaseTypes",
                                  "PlatformImplementationDataTypes": "AUTOSAR_Platform/ImplementationDataTypes",
                                  "ImplementationDataTypes": "DataTypes/ImplementationDataTypes",
                                  "PortInterfaces": "PortInterfaces"})
    create_platform_types(workspace)
    create_implementation_data_types(workspace)
    create_sender_receiver_interface_with_one_element(workspace)
    create_sender_receiver_interface_with_two_elements(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
