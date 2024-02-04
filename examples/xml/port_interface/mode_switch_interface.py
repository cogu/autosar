"""
Sender-receiver port interface examples
"""
import os
import autosar
import autosar.xml.element as ar_element


def create_mode_declaration_groups(packages: dict[str, ar_element.Package]):
    """
    Creates mode declarations
    """
    vehicle_mode = ar_element.ModeDeclarationGroup("VehicleMode", ["OFF",
                                                                   "ACCESSORY",
                                                                   "RUNNING",
                                                                   "CRANKING"])
    packages["ModeDeclarations"].append(vehicle_mode)
    vehicle_mode.initial_mode_ref = vehicle_mode.find("OFF").ref()


def create_mode_switch_interface(packages: dict[str, ar_element.Package]):
    """
    Creates mode switch interface
    """
    mode_declaration = packages["ModeDeclarations"].find("VehicleMode")
    portinterface = ar_element.ModeSwitchInterface("VehicleMode_I", is_service=False)
    portinterface.create_mode_group("mode", mode_declaration.ref())
    packages["PortInterfaces"].append(portinterface)


def save_xml_files(workspace: autosar.xml.Workspace):
    """
    Saves workspace as XML documents
    """
    interface_document_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                           'data',
                                                           'mode_switch_interface.arxml'))
    mode_declaration_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                         'data',
                                                         'mode_declarations.arxml'))
    workspace.create_document(interface_document_path, packages="/PortInterfaces")
    workspace.create_document(mode_declaration_path, packages="/ModeDeclarations")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["ModeDeclarations", "PortInterfaces"],
                    workspace.make_packages("ModeDeclarations", "PortInterfaces")))
    create_mode_declaration_groups(packages)
    create_mode_switch_interface(packages)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
