import autosar
import os

...

dest_dir = "."

for swc in ws.findall("/ComponentTypes/*"):
    if isinstance(swc, autosar.component.ComponentType):
        filters = ["/ComponentTypes/" + swc.name, "/ComponentTypes/{0.name}_Implementation".format(swc)]
        #Add DataTypeMappingSets if it exists
        type_mapping_ref = "/ComponentTypes/DataTypeMappingSets/{0.name}_TypeMappingSet".format(swc)
        if ws.find(type_mapping_ref) is not None:
            filters.append(type_mapping_ref)
        dest_file = os.path.join(dest_dir, "{0.name}.arxml".format(swc))
        ws.saveXML(dest_file, filters)
