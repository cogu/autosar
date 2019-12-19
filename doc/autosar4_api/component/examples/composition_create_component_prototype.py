#Create three unique application software components and then add them to a new composition
import autosar

ws = autosar.workspace("4.2.2")
components = ws.createPackage("ComponentTypes")
app1 = components.createApplicationSoftwareComponent("Application1")
#Add ports and behavior to app1

app2 = components.createApplicationSoftwareComponent("Application2")
#Add ports and behavior to app2

app3 = components.createApplicationSoftwareComponent("Application3")
#Add ports and behavior to app3

swc = components.createCompositionComponent("MyComposition")
#Add ports to swc

#Add child components
swc.createComponentPrototype(app1.ref)
swc.createComponentPrototype(app2.ref)
swc.createComponentPrototype(app3.ref)

#Optionally call swc.autoConnect() here to create port connectors
print(ws.toXML())