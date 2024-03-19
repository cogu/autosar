"""
Generate ARXML from template classes using local config file.
"""

import os
from demo_system import platform, component
import autosar.xml.workspace as ar_workspace


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
    workspace.apply(component.ReceiverComponent_Implementation)


def main():
    """Main"""
    config_file_path = os.path.join(os.path.dirname(__file__), "config.toml")
    document_root = os.path.join(os.path.dirname(__file__), "generated")
    workspace = ar_workspace.Workspace(config_file_path, document_root=document_root)
    apply_platform_types(workspace)
    apply_component_types(workspace)
    workspace.write_documents()
    print("Done")


if __name__ == "__main__":
    main()
