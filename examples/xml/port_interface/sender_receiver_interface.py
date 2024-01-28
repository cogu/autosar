"""
Sender-receiver port interface examples
"""
import os
import autosar
import autosar.xml.element as ar_element


def create_interface_with_one_element():
    """
    Creates an array implementation data type with VALUE element
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["BaseTypes", "ImplementationDataTypes", "PortInterfaces"],
                    workspace.make_packages("DataTypes/BaseTypes",
                                            "DataTypes/ImplementationDataTypes",
                                            "PortInterfaces")))
    uint8_base_type = ar_element.SwBaseType('uint8', size=8)
    packages["BaseTypes"].append(uint8_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
    packages["ImplementationDataTypes"].append(inactive_active_t)
    portinterface = ar_element.SenderReceiverInterface.make_simple("HeadLightStatus_I",
                                                                   "HeadLightStatus",
                                                                   type_ref=inactive_active_t.ref())
    packages["PortInterfaces"].append(portinterface)
    document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'sender_receiver_interface.arxml'))
    workspace.create_document(document_path, packages="/PortInterfaces")
    workspace.write_documents()


if __name__ == "__main__":
    create_interface_with_one_element()
