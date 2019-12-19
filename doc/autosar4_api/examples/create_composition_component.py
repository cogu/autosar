import autosar

ws = autosar.workspace("4.2.2")
components = ws.createPackage("ComponentTypes")
swc = components.createCompositionComponent("MyComposition")
print(swc.name)
