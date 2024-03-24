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


def create_abs_path(sub_directory, file_name) -> str:
    """
    Returns absolute path to a file in a sub_directory relative to this python script
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), sub_directory, file_name))


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
    workspace = ar_workspace.Workspace(document_root="generated")
    create_namespaces(workspace)
    create_documents(workspace)
    apply_platform_types(workspace)
    apply_component_types(workspace)
    workspace.write_documents()
    print("Done")


if __name__ == "__main__":
    main()
