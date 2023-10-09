"""
Example generation of RTE type header
Requires cfile v0.3.0 (unreleased)
"""
import autosar
import autosar.xml.element as ar_element
from autosar.model import ImplementationModel
import autosar.generator


def main():
    """
    Prints header to stdout
    """
    workspace = autosar.xml.Workspace()
    packages = workspace.make_packages("DataTypes/BaseTypes",
                                       "DataTypes/ImplementationDataTypes")
    uint8_base_type = ar_element.SwBaseType('uint8')
    packages[0].append(uint8_base_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props, type_emitter="Platform")
    packages[1].append(uint8_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint8_impl_type.ref())
    inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                          category="TYPE_REFERENCE",
                                                          sw_data_def_props=sw_data_def_props)
    packages[1].append(inactive_active_t)

    implementation = ImplementationModel(workspace)
    implementation.create_from_element(inactive_active_t)
    type_generator = autosar.generator.TypeGenerator(implementation)
    print(type_generator.write_type_header_str())


if __name__ == "__main__":
    main()
