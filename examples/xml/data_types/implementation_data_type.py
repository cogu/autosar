"""
Implementation data type examples
"""
import os
import autosar.xml
import autosar.xml.element as ar_element


def create_array_impl_type_with_value_element():
    """
    Creates an array implementation data type with VALUE element
    """
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                                  "ImplementationDataTypes": "DataTypes/ImplementationDataTypes"})

    uint8_base_type = ar_element.SwBaseType('uint8')
    workspace.add_element("BaseTypes", uint8_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                           category="VALUE",
                                                           array_size=4,
                                                           sw_data_def_props=sw_data_def_props)
    impl_type = ar_element.ImplementationDataType('U8Array4_T',
                                                  category="ARRAY",
                                                  sub_elements=[sub_element])
    workspace.add_element("ImplementationDataTypes", impl_type)
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), 'data'))
    workspace.create_document("array_impl_type_with_value_element.arxml", packages="/DataTypes")
    workspace.write_documents()


def create_array_impl_type_with_type_ref_element():
    """
    Creates an array implementation data type with TYPE_REFERENCE element
    """
    workspace = autosar.xml.Workspace()
    workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                                  "ImplementationDataTypes": "DataTypes/ImplementationDataTypes"})
    uint8_base_type = ar_element.SwBaseType('uint8')
    workspace.add_element("BaseTypes", uint8_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    value_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                   category="VALUE",
                                                   sw_data_def_props=sw_data_def_props)
    workspace.add_element("ImplementationDataTypes", value_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=value_type.ref())
    sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                           category="TYPE_REFERENCE",
                                                           array_size=2,
                                                           sw_data_def_props=sw_data_def_props)
    array_type = ar_element.ImplementationDataType('InactiveActiveArray2_T',
                                                   category="ARRAY",
                                                   sub_elements=[sub_element])
    workspace.add_element("ImplementationDataTypes", array_type)
    workspace.set_document_root(os.path.join(os.path.dirname(__file__), 'data'))
    workspace.create_document("array_impl_type_with_type_ref_element.arxml", packages="/DataTypes")
    workspace.write_documents()


if __name__ == "__main__":
    create_array_impl_type_with_value_element()
    create_array_impl_type_with_type_ref_element()
    print("Done")
