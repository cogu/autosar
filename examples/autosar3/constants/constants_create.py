import autosar

ws = autosar.workspace()
ws.loadXML('../datatypes/DataTypes.arxml', roles={'/DataType': 'DataType'})

package = ws.createPackage('Constant')

package.createConstant('EngineSpeed_IV', 'EngineSpeed_T', 0)
package.createConstant('VehicleSpeed_IV', 'VehicleSpeed_T', 0)
package.createConstant('FuelLevel_IV', 'Percent_T', 0)
package.createConstant('CoolantTemp_IV', 'CoolantTemp_T', 0)
package.createConstant('ParkBrakeState_IV', 'InactiveActive_T', 3) #3=NotAvailable
package.createConstant('MainBeamState_IV', 'OnOff_T', 3) #3=NotAvailable

ws.saveXML('Constants.arxml', packages=['Constant'])
print("Done")