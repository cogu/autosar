"""
Sender-receiver port interface examples
"""
import os
import autosar
import autosar.xml.element as ar_element


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


def create_implementation_data_types(packages: dict[str, ar_element.Package]):
    """
    Creates non-platform implementation data types
    """
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="AUTOSAR_Platform/BaseTypes/uint8")
    inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
    packages["ImplementationDataTypes"].append(inactive_active_t)


def create_sender_receiver_interface_with_one_element(packages: dict[str, ar_element.Package]):
    """
    Creates interface with one element
    """
    inactive_active_t = packages["ImplementationDataTypes"].find("InactiveActive_T")
    portinterface = ar_element.SenderReceiverInterface("HeadLightStatus_I")
    portinterface.create_data_element("HeadLightStatus", type_ref=inactive_active_t.ref())
    packages["PortInterfaces"].append(portinterface)


def create_sender_receiver_interface_with_two_elements(packages: dict[str, ar_element.Package]):
    """
    Creates interface with two elements
    """
    inactive_active_t = packages["ImplementationDataTypes"].find("InactiveActive_T")
    portinterface = ar_element.SenderReceiverInterface("InterfaceName")
    portinterface.create_data_element("Element1", type_ref=inactive_active_t.ref())
    portinterface.create_data_element("Element2", type_ref=inactive_active_t.ref())
    packages["PortInterfaces"].append(portinterface)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace as XML documents
    """
    interface_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'sender_receiver_interface.arxml'))
    datatype_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'datatypes.arxml'))
    platform_document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'platform.arxml'))
    workspace.create_document(interface_document_path, packages="/PortInterfaces")
    workspace.create_document(datatype_document_path, packages="/DataTypes")
    workspace.create_document(platform_document_path, packages="/AUTOSAR_Platform")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["PlatformBaseTypes",
                         "PlatformImplementationDataTypes",
                         "ImplementationDataTypes",
                         "PortInterfaces"],
                    workspace.make_packages("AUTOSAR_Platform/BaseTypes",
                                            "AUTOSAR_Platform/ImplementationDataTypes",
                                            "DataTypes/ImplementationDataTypes",
                                            "PortInterfaces")))
    create_platform_types(packages)
    create_implementation_data_types(packages)
    create_sender_receiver_interface_with_one_element(packages)
    create_sender_receiver_interface_with_two_elements(packages)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
