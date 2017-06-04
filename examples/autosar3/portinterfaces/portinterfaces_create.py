import sys
import autosar

ws = autosar.workspace()
ws.loadXML('../datatypes/DataTypes.arxml', roles={'/DataType': 'DataType'})

package=ws.createPackage('PortInterface', role='PortInterface')

package.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed','EngineSpeed_T'))
package.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed','VehicleSpeed_T'))
package.createSenderReceiverInterface('FuelLevel_I', autosar.DataElement('FuelLevel','Percent_T'))
package.createSenderReceiverInterface('CoolantTemp_I', autosar.DataElement('CoolantTemp','CoolantTemp_T'))
package.createSenderReceiverInterface('InactiveActive_I', autosar.DataElement('InactiveActive','InactiveActive_T'))
package.createSenderReceiverInterface('OnOff_I', autosar.DataElement('OnOff','OnOff_T'))

ws.saveXML('PortInterfaces.arxml', packages=['PortInterface'])