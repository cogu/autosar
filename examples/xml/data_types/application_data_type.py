"""
Application data type examples
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


def create_primitive_application_data_type():
    """
    Creates a primitive application data type
    """
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"ApplicationDataTypes": "DataTypes/ApplicationDataTypes",
                                  "DataConstrs": "DataTypes/DataConstrs"})
    data_constraint = ar_element.DataConstraint.make_internal("uint8_ADT_DataConstr", 0, 255)
    workspace.add_element("DataConstrs", data_constraint)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(data_constraint_ref=data_constraint.ref())
    data_type = ar_element.ApplicationPrimitiveDataType("uint8_ADT",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props)
    workspace.add_element("ApplicationDataTypes", data_type)
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), "data"))
    workspace.create_document("application_primitive_datatype.arxml", packages="/DataTypes")
    workspace.write_documents()


if __name__ == "__main__":
    create_primitive_application_data_type()
    print("Done")
