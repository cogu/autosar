"""
Demonstrates how to create ARXML constants
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


def create_numerical_constants(workspace: autosar.xml.Workspace):
    """Create numerical constants"""
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("IntNoLabel", 1))
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("IntConstant",
                                                                                      ("Label1", 1)))
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("FloatNoLabel", 2.5))
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("FloatConstant",
                                                                                      ("Label2", 2.5)))


def create_text_constants(workspace: autosar.xml.Workspace):
    """Create text-based constants"""
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("TextNoLabel", "TextValue"))
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("TextConstant",
                                                                                      ("Label3", "TextData")))


def create_array_constants(workspace: autosar.xml.Workspace):
    """Create array constants"""
    # The 'A' below is short-hand for ARRAY, it's not part of the stored XML.
    # Instead, it's there to help Python differenitate between record and array specifications.
    data = ["A", 1, 2, 3, 4]
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("ArrayNoLabel", data))
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("ArrayConstant",
                                                                                      ("Label4", data)))


def create_record_constants(workspace: autosar.xml.Workspace):
    """Create record constants"""
    # If you want to create a RECORD-VALUE-SPECIFICATION, use "R" instead or "A".
    data = ["R", "Value1", "Value2", 3]
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("RecordNoLabel", data))
    workspace.add_element("Constants", ar_element.ConstantSpecification.make_constant("RecordConstant",
                                                                                      ("Label5", data)))


def create_record_constant_using_references(workspace: autosar.xml.Workspace):
    """
    Creates record constant using references to previously created elements
    """
    record_value = ar_element.RecordValueSpecification(fields=[
        ar_element.ConstantReference(label="First", constant_ref=ar_element.ConstantRef("/Constants/FloatConstant")),
        ar_element.ConstantReference(label="Second", constant_ref=ar_element.ConstantRef("/Constants/TextConstant"))
    ])
    workspace.add_element("Constants", ar_element.ConstantSpecification("RecordWithReferences", record_value))


def main():
    """Main function"""
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"Constants": "/Constants"})
    create_numerical_constants(workspace)
    create_text_constants(workspace)
    create_array_constants(workspace)
    create_record_constants(workspace)
    create_record_constant_using_references(workspace)
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("constants.arxml", packages="/Constants")
    workspace.write_documents()


if __name__ == "__main__":
    main()
