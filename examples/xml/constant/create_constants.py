"""
Constant examples
"""
import os
import autosar
import autosar.xml.element as ar_element


def create_numerical_constants(pkg: ar_element.Package):
    """Create some numerical constants"""
    pkg.append(ar_element.ConstantSpecification.make_constant("IntNoLabel", 1))
    pkg.append(ar_element.ConstantSpecification.make_constant("IntConstant", ("Label1", 1)))
    pkg.append(ar_element.ConstantSpecification.make_constant("FloatNoLabel", 2.5))
    pkg.append(ar_element.ConstantSpecification.make_constant("FloatConstant", ("Label2", 2.5)))


def create_text_constants(pkg: ar_element.Package):
    """Create some text-based constants"""
    pkg.append(ar_element.ConstantSpecification.make_constant("TextNoLabel", "TextValue"))
    pkg.append(ar_element.ConstantSpecification.make_constant("TextConstant", ("Label3", "TextData")))


def create_array_constants(pkg: ar_element.Package):
    """Create array constants"""
    # The 'A' below is short-hand for ARRAY, it's not part of the stored XML.
    # Instead, it's there to help Python differenitate between record and array specifications.
    # If you want to create a RECORD-VALUE-SPECIFICATION, use "R" instead or "A".
    data = ["A", 1, 2, 3, 4]
    pkg.append(ar_element.ConstantSpecification.make_constant("ArrayNoLabel", data))
    pkg.append(ar_element.ConstantSpecification.make_constant("ArrayConstant", ("Label4", data)))


def create_record_constants(pkg: ar_element.Package):
    """Create record constants"""
    data = ["R", "Value1", "Value2", 3]
    pkg.append(ar_element.ConstantSpecification.make_constant("RecordNoLabel", data))
    pkg.append(ar_element.ConstantSpecification.make_constant("RecordConstant", ("Label5", data)))


def create_record_constant_using_references(pkg: ar_element.Package):
    """
    Creates record constant using references to previously created elements
    """
    record_value = ar_element.RecordValueSpecification(fields=[
        ar_element.ConstantReference(label="First", constant_ref=ar_element.ConstantRef("/Constants/FloatConstant")),
        ar_element.ConstantReference(label="Second", constant_ref=ar_element.ConstantRef("/Constants/TextConstant"))
    ])
    pkg.append(ar_element.ConstantSpecification("RecordWithReferences", record_value))


if __name__ == "__main__":
    workspace = autosar.xml.Workspace()
    package = workspace.make_packages("/Constants")
    create_numerical_constants(package)
    create_text_constants(package)
    create_array_constants(package)
    create_record_constants(package)
    create_record_constant_using_references(package)
    document_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 'data', 'constants.arxml'))
    workspace.create_document(document_path, packages="/Constants")
    workspace.write_documents()
