"""
Generate ARXML from template classes without using config file.
Instead we programatically create namespaces and documents
"""

import os
from demo_system import platform, datatype, portinterface
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
        "PortInterface": "/PortInterfaces"},
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
    sub_directory = "generated"
    platform_document_path = create_abs_path(sub_directory, "AUTOSAR_Platform.arxml")
    datatype_document_path = create_abs_path(sub_directory, "DataTypes.arxml")
    portinterface_document_path = create_abs_path(sub_directory, "PortInterfaces.arxml")
    workspace.create_document(platform_document_path, packages="/AUTOSAR_Platform")
    workspace.create_document(datatype_document_path, packages="/DataTypes")
    workspace.create_document(portinterface_document_path, packages=["/ModeDclrGroups", "/PortInterfaces"])


def apply_platform_types(workspace: ar_workspace.Workspace):
    """
    Applies platform templates
    """
    workspace.apply(platform.ImplementationTypes.boolean)
    workspace.apply(platform.ImplementationTypes.uint8)
    workspace.apply(platform.ImplementationTypes.uint16)
    workspace.apply(platform.ImplementationTypes.uint32)
    workspace.apply(platform.ImplementationTypes.uint64)


def apply_data_types(workspace: ar_workspace.Workspace):
    """
    Applies data type templates
    """
    workspace.apply(datatype.InactiveActive_T)


def apply_portinterfaces(workspace: ar_workspace.Workspace):
    """
    Applies mode templates
    """
    workspace.apply(portinterface.EcuM_CurrentMode)
    workspace.apply(portinterface.NvMService_I)


def main():
    """Main"""
    workspace = ar_workspace.Workspace()
    create_namespaces(workspace)
    apply_platform_types(workspace)
    apply_data_types(workspace)
    apply_portinterfaces(workspace)
    create_documents(workspace)
    workspace.write_documents()
    print("Done")


if __name__ == "__main__":
    main()
