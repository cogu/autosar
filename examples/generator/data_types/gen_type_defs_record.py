"""
Example generation of RTE type header - Record type
Requires cfile v0.3.1
"""
import autosar
import autosar.xml.element as ar_element
from autosar.model import ImplementationModel
import autosar.generator


def main():
    """
    Create workspace and print type header to stdout
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                        workspace.make_packages("DataTypes/BaseTypes",
                                                "DataTypes/ImplementationDataTypes")))
    uint8_base_type = ar_element.SwBaseType("uint8")
    packages["BaseTypes"].append(uint8_base_type)
    uint32_base_type = ar_element.SwBaseType("uint32")
    packages["BaseTypes"].append(uint32_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props,
                                                         type_emitter="Platform_Types")
    packages["ImplementationDataTypes"].append(uint32_impl_type)
    inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
    packages["ImplementationDataTypes"].append(inactive_active_t)

    record_members = []
    sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=inactive_active_t.ref())
    record_members.append(ar_element.ImplementationDataTypeElement("First",
                                                                   category="TYPE_REFERENCE",
                                                                   sw_data_def_props=sw_data_def_props))
    sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint32_impl_type.ref())
    record_members.append(ar_element.ImplementationDataTypeElement("Second",
                                                                   category="TYPE_REFERENCE",
                                                                   sw_data_def_props=sw_data_def_props))
    record_type = ar_element.ImplementationDataType("MyRecord_T",
                                                    category="STRUCTURE",
                                                    sub_elements=record_members)
    packages["ImplementationDataTypes"].append(record_type)

    implementation = ImplementationModel(workspace)
    implementation.create_from_element(record_type)
    type_generator = autosar.generator.TypeGenerator(implementation)
    print(type_generator.write_type_header_str())


if __name__ == "__main__":
    main()
