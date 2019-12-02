import autosar

ws = autosar.workspace("4.2.2")
package = ws.createPackage('PortInterfaces', role = "PortInterface")

portInterface=package.createClientServerInterface("Example_I",
    operations = ["Invalidate"],
    errors = autosar.ApplicationError("E_NOT_OK", 1),
    isService=True)

portInterface["Invalidate"].possibleErrors = "E_NOT_OK"

ws.saveXML('PortInterfaces.arxml', filters=['/PortInterfaces'])
