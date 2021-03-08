import autosar

ws = autosar.workspace(version="4.2.2")
package = ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")
package.createModeDeclarationGroup('VehicleMode', 
    ["OFF", "ACCESSORY", "ON", "CRANK", "RUN"], "OFF")
modeGroup = autosar.mode.ModeGroup('mode', '/ModeDclrGroups/VehicleMode')

