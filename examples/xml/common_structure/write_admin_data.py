"""
Read admin data from xml
"""
import os
import autosar
import autosar.xml.element as ar_element


def create_component(workspace: autosar.xml.Workspace) -> None:
    """
    Creates an SWC with simple admin data
    """
    workspace.update_package_map({"ComponentTypes": "ComponentTypes"})
    sdg = ar_element.SpecialDataGroup("Master", "true")
    swc = ar_element.ApplicationSoftwareComponentType("SWC", admin_data=sdg)
    workspace.add_element("ComponentTypes", swc)


def save_xml_file(workspace: autosar.xml.Workspace) -> None:
    """
    Saves workspace as XML documents
    """
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("swc_with_admin_data.arxml", packages="/ComponentTypes")
    workspace.write_documents()


def main():
    """
    Main
    """
    workspace = autosar.xml.Workspace()
    create_component(workspace)
    save_xml_file(workspace)


if __name__ == "__main__":
    main()
