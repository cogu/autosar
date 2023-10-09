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
    package = workspace.make_packages("DataTypes/BaseTypes")
    base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
    package.append(base_type)
    package = workspace.make_packages("DataTypes/ImplementationDataTypes")
    workspace.append(package)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
    impl_type = ar_element.ImplementationDataType("MyUInt8",
                                                  category="VALUE",
                                                  sw_data_def_props=sw_data_def_props)
    package.append(impl_type)
    implementation = ImplementationModel(workspace)
    implementation.create_from_element(impl_type)
    type_generator = autosar.generator.TypeGenerator(implementation)
    print(type_generator.write_type_header_str())


if __name__ == "__main__":
    main()
