"""
Application data type examples
"""
import os
import autosar
import autosar.xml.element as ar_element


def create_primitive_application_data_type():
    """
    Creates a primitive application data type
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["ApplicationDataTypes", "DataConstrs"],
                        workspace.make_packages("DataTypes/ApplicationDataTypes", "DataTypes/DataConstrs")))
    data_constraint = ar_element.DataConstraint.make_internal("uint8_ADT_DataConstr", 0, 255)
    packages["DataConstrs"].append(data_constraint)
    print(str(data_constraint.ref()))
    sw_data_def_props = ar_element.SwDataDefPropsConditional(data_constraint_ref=data_constraint.ref())
    data_type = ar_element.ApplicationPrimitiveDataType("uint8_ADT",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props)
    packages["ApplicationDataTypes"].append(data_type)
    print(str(data_type.ref()))
    document_path = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'data', 'application_primitive_datatype.arxml'))
    workspace.create_document(document_path, packages="/DataTypes")
    workspace.write_documents()


if __name__ == "__main__":
    create_primitive_application_data_type()
