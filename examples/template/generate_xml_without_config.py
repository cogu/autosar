"""
Generate ARXML from template classes without using config file.
Instead we programatically create namespaces and documents
"""

import os
from demo_system import platform, component
import autosar.xml.element as ar_element
import autosar.xml.workspace as ar_workspace


def create_namespaces(workspace: ar_workspace.Workspace):
    """
    Define namespaces
    """
    workspace.create_namespace("AUTOSAR_Platform", package_map={
        "BaseType": "BaseTypes",
        "ImplementationDataType": "ImplementationDataTypes",
        "CompuMethod": "CompuMethods",
        "DataConstraint": "DataConstrs"
    })

    workspace.create_namespace("Default", package_map={
        "BaseType": "/DataTypes/BaseTypes",
        "ImplementationDataType": "/DataTypes/ImplementationDataTypes",
        "CompuMethod": "/DataTypes/CompuMethods",
        "DataConstraint": "/DataTypes/DataConstrs",
        "ModeDeclaration": "/ModeDclrGroups",
        "PortInterface": "/PortInterfaces",
        "Constant": "/Constants",
        "ComponentType": "/ComponentTypes"},
        base_ref="/")


def init_behavior_settings(workspace: ar_workspace.Workspace):
    """
    Define default event name prefixess
    """
    workspace.behavior_settings.update({
        "background_event_prefix": "BT",
        "data_receive_error_event_prefix": "DRET",
        "data_receive_event_prefix": "DRT",
        "init_event_prefix": "IT",
        "operation_invoked_event_prefix": "OIT",
        "swc_mode_manager_error_event_prefix": "MMET",
        "swc_mode_switch_event_prefix": "MST",
        "timing_event_prefix": "TMT",
        "data_send_point_prefix": "SEND",
        "data_receive_point_prefix": "REC",
        "server_call_point_prefix": "SC"})


def create_documents(workspace: ar_workspace.Workspace) -> None:
    """
    Creates documents
    """
    workspace.create_document("AUTOSAR_Platform.arxml", packages="/AUTOSAR_Platform")
    workspace.create_document("DataTypes.arxml", packages="/DataTypes")
    workspace.create_document("Constants.arxml", packages="/Constants")
    workspace.create_document("PortInterfaces.arxml", packages=["/ModeDclrGroups", "/PortInterfaces"])
    workspace.create_document_mapping(package_ref="/ComponentTypes",
                                      element_types=ar_element.SwComponentType,
                                      suffix_filters=["_Implementation"])


def apply_platform_types(workspace: ar_workspace.Workspace):
    """
    Applies platform templates
    """
    workspace.apply(platform.ImplementationTypes.boolean)
    workspace.apply(platform.ImplementationTypes.uint8)
    workspace.apply(platform.ImplementationTypes.uint16)
    workspace.apply(platform.ImplementationTypes.uint32)
    workspace.apply(platform.ImplementationTypes.uint64)


def apply_component_types(workspace: ar_workspace.Workspace):
    """
    Applies component type templates
    """
    workspace.apply(component.CompositionComponent)


def main():
    """Main"""
    document_root = os.path.join(os.path.dirname(__file__), "generated")
    workspace = ar_workspace.Workspace(document_root=document_root)
    create_namespaces(workspace)
    init_behavior_settings(workspace)
    create_documents(workspace)
    apply_platform_types(workspace)
    apply_component_types(workspace)
    workspace.write_documents()
    print("Done")


if __name__ == "__main__":
    main()
