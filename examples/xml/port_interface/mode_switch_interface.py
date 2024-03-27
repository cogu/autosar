"""
ModeSwitch port interface examples
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


def create_mode_declaration_groups(workspace: autosar.xml.Workspace):
    """
    Creates mode declarations
    """
    vehicle_mode = ar_element.ModeDeclarationGroup("VehicleMode", ["OFF",
                                                                   "ACCESSORY",
                                                                   "RUNNING",
                                                                   "CRANKING"])
    workspace.add_element("ModeDeclarations", vehicle_mode)
    vehicle_mode.initial_mode_ref = vehicle_mode.find("OFF").ref()


def create_mode_switch_interface(workspace: autosar.xml.Workspace):
    """
    Creates mode switch interface
    """
    mode_declaration = workspace.get_package("ModeDeclarations").find("VehicleMode")
    portinterface = ar_element.ModeSwitchInterface("VehicleMode_I", is_service=False)
    portinterface.create_mode_group("mode", mode_declaration.ref())
    workspace.add_element("PortInterfaces", portinterface)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace into multiple XML documents
    """
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("mode_declarations.arxml", packages="/ModeDeclarations")
    workspace.create_document("mode_switch_interface.arxml", packages="/PortInterfaces")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"ModeDeclarations": "ModeDeclarations",
                                  "PortInterfaces": "PortInterfaces"})

    create_mode_declaration_groups(workspace)
    create_mode_switch_interface(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
