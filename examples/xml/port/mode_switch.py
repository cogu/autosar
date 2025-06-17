"""
Demonstrates port access for mode-switch ports
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
                                  "ComponentTypes": "ComponentTypes",
                                  "ModeDeclarations": "ModeDeclarations"})


def init_behavior_settings(workspace: ar_workspace.Workspace):
    """
    Define default event name prefixess
    """
    workspace.behavior_settings.update({
        "mode_access_point_prefix": "ACCESS",
        "mode_switch_point_prefix": "SWITCH"})


def create_mode_declaration_groups(workspace: autosar.xml.Workspace):
    """
    Creates mode declarations
    """
    vehicle_mode = ar_element.ModeDeclarationGroup("VehicleMode", ["OFF",
                                                                   "PARKING",
                                                                   "ACCESSORY",
                                                                   "CRANKING",
                                                                   "RUNNING"])
    workspace.add_element("ModeDeclarations", vehicle_mode)
    vehicle_mode.initial_mode_ref = vehicle_mode.find("OFF").ref()
    ecum_mode = ar_element.ModeDeclarationGroup("EcuM_Mode", ["STARTUP",
                                                              "RUN",
                                                              "POST_RUN",
                                                              "SLEEP",
                                                              "WAKE_SLEEP",
                                                              "SHUTDOWN"])
    workspace.add_element("ModeDeclarations", ecum_mode)
    vehicle_mode.initial_mode_ref = ecum_mode.find("STARTUP").ref()


def create_mode_switch_interface(workspace: autosar.xml.Workspace):
    """
    Creates mode switch interface
    """
    # VehicleMode
    mode_declaration = workspace.get_package("ModeDeclarations").find("VehicleMode")
    portinterface = ar_element.ModeSwitchInterface("VehicleMode_I", is_service=False)
    portinterface.create_mode_group("mode", mode_declaration.ref())
    workspace.add_element("PortInterfaces", portinterface)
    # EcuM_Mode
    mode_declaration = workspace.get_package("ModeDeclarations").find("EcuM_Mode")
    portinterface = ar_element.ModeSwitchInterface("EcuM_CurrentMode", is_service=True)
    portinterface.create_mode_group("currentMode", mode_declaration.ref())
    workspace.add_element("PortInterfaces", portinterface)


def create_application_component(workspace: autosar.xml.Workspace):
    """
    Creates application SWC with two sender ports
    """
    ecu_mode_interface = workspace.find_element("PortInterfaces", "EcuM_CurrentMode")
    vehicle_mode_interface = workspace.find_element("PortInterfaces", "VehicleMode_I")
    swc = ar_element.ApplicationSoftwareComponentType("ModeSwitchComponent")
    workspace.add_element("ComponentTypes", swc)

    # Create ports
    swc.create_r_port("EcuM_CurrentMode", ecu_mode_interface, com_spec={"enhanced_mode_api": False,
                                                                        "supports_async": False})
    swc.create_p_port("VehicleMode", vehicle_mode_interface, com_spec={"enhanced_mode_api": False,
                                                                       "mode_switched_ack": 1.0})

    # Create internal behavior
    behavior = swc.create_internal_behavior()

    # Create SWC Implementation object
    impl = ar_element.SwcImplementation(swc.name + "_Implementation", behavior_ref=swc.internal_behavior.ref())
    workspace.add_element("ComponentTypes", impl)

    # Create Runnables
    init_runnable_name = swc.name + '_Init'
    periodic_runnable_name = swc.name + '_Run'
    behavior.create_runnable(init_runnable_name,)
    runnable = behavior.create_runnable(periodic_runnable_name)

    # Create Port access
    # Default access type for mode-switch port is "ACCESS".
    # If you explicitly write the "ACCESS" prefix, an <IDENT> tag containing a generated <SHORT-NAME> will also
    # be created.
    # If you give no prefix (default), an anomymous mode access point will be created.
    # For P-PORTS you can use the "SWITCH" prefix which will create a mode-switch-point with a generated name.
    runnable.create_port_access(["EcuM_CurrentMode",
                                 "SWITCH: VehicleMode"])


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
    create_mode_declaration_groups(workspace)
    create_mode_switch_interface(workspace)
    create_application_component(workspace)
    save_xml_files(workspace)


if __name__ == "__main__":
    main()
