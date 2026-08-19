import os
import autosar.xml
import autosar.xml.element as ar_element

workspace = autosar.xml.Workspace()
workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                              "ImplementationDataTypes": "DataTypes/ImplementationDataTypes",
                              "CompuMethods": "DataTypes/CompuMethods"})
# Create SwBaseType
uint8_base_type = ar_element.SwBaseType("uint8")
workspace.add_element("BaseTypes", uint8_base_type)

# Create CompuMethod
computation = ar_element.Computation.make_value_table(["Inactive",
                                                       "Active",
                                                       "Error",
                                                       "NotAvailable"])
compu_method = ar_element.CompuMethod(name='InactiveActive_T',
                                      int_to_phys=computation,
                                      category="TEXTTABLE")
workspace.add_element("CompuMethods", compu_method)

# Create ImplementantationDataType, referencing the SwBaseType and CompuMethod
sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref(),
                                                         compu_method_ref=compu_method.ref())
inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
workspace.add_element("ImplementationDataTypes", inactive_active_t)

# Save DataType package and all its sub-packages into data/datatypes.arxml
workspace.set_document_root(os.path.abspath(os.path.join(os.path.dirname(__file__), "data")))
workspace.create_document("datatypes.arxml", packages="/DataTypes")
workspace.write_documents()
