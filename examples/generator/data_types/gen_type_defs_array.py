"""
Example generation of RTE type header - Array type
Requires cfile v0.3.2
"""
import autosar
import autosar.xml.element as ar_element
from autosar.model import ImplementationModel
import autosar.generator

EXPECTED_HEADER = """#ifndef RTE_TYPE_H_
#define RTE_TYPE_H_

#ifdef __cplusplus
extern "C"
{
#endif

/***********************************
*             INCLUDES             *
************************************/
#include "Rte.h"

/***********************************
*     CONSTANTS AND DATA TYPES     *
************************************/

typedef uint8 InactiveActive_T;
typedef InactiveActive_T InactiveActiveArray_T[3];

#ifdef __cplusplus
}
#endif // __cplusplus
#endif // RTE_TYPE_H_
"""


def main():
    """
    Create workspace and generate type header
    """
    workspace = autosar.xml.Workspace()
    packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                        workspace.make_packages("DataTypes/BaseTypes",
                                                "DataTypes/ImplementationDataTypes")))

    uint8_base_type = ar_element.SwBaseType("uint8")
    packages["BaseTypes"].append(uint8_base_type)
    package = workspace.find("DataTypes/ImplementationDataTypes")
    workspace.append(package)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    value_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                   category="VALUE",
                                                   sw_data_def_props=sw_data_def_props)
    packages["ImplementationDataTypes"].append(value_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=value_type.ref())
    sub_element = ar_element.ImplementationDataTypeElement("Element",
                                                           category="TYPE_REFERENCE",
                                                           array_size=3,
                                                           sw_data_def_props=sw_data_def_props)
    array_type = ar_element.ImplementationDataType("InactiveActiveArray_T",
                                                   category="ARRAY",
                                                   sub_elements=[sub_element])
    packages["ImplementationDataTypes"].append(array_type)
    implementation = ImplementationModel(workspace)
    implementation.create_from_element(array_type)
    type_generator = autosar.generator.TypeGenerator(implementation)
    header_str = type_generator.write_type_header_str()
    assert header_str == EXPECTED_HEADER, f"Generated header mismatch:\n{header_str}"


if __name__ == "__main__":
    main()
