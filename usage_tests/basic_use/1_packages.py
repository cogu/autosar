import autosar.xml

workspace = autosar.xml.Workspace()
workspace.create_package_map({"BaseTypes": "DataTypes/BaseTypes",
                              "ImplementationDataTypes": "DataTypes/ImplementationDataTypes"})
print(workspace.get_package("BaseTypes").name)
print(workspace.get_package("ImplementationDataTypes").name)
