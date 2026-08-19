import os
import autosar.xml
import autosar.xml.element as ar_element

workspace = autosar.xml.Workspace()

workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                              "ImplementationDataTypes": "DataTypes/ImplementationDataTypes"})

# Create uint8 base type
uint8_base_type = ar_element.SwBaseType("uint8", size=8)
workspace.add_element("BaseTypes", uint8_base_type)

# Create implementation data referencing the uint8 base type
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
workspace.add_element("ImplementationDataTypes", inactive_active_t)

# Save DataType package and all its sub-packages into data/datatypes.arxml
workspace.set_document_root(os.path.abspath(os.path.join(os.path.dirname(__file__), "data")))
workspace.create_document("datatypes.arxml", "/DataTypes")
workspace.write_documents()
