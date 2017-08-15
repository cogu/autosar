import sys
sys.path.insert(0,'..')
import autosar
import DataTypes

#### Helpers ####
def createSenderReceiverInterfaceTemplate(name, dataTypeTemplate):
   @classmethod
   def apply(cls, ws):
      package = ws.getPortInterfacePackage()
      if package.find(name) is None:
         ws.apply(cls.dataTypeTemplate)
         package.createSenderReceiverInterface(name, autosar.DataElement(name, cls.dataTypeTemplate.__name__))
   return type(name, (autosar.Template,), dict(dataTypeTemplate=dataTypeTemplate, apply=apply))

#### Sender Receiver Port Interfaces ####
ParkBrakeStatus_I = createSenderReceiverInterfaceTemplate('ParkBrakeStatus_I', DataTypes.ParkBrakeStatus_T)
DirIndStat_I = createSenderReceiverInterfaceTemplate('DirIndStat_I', DataTypes.DirIndStat_T)
BatteryChargeStatus_I = createSenderReceiverInterfaceTemplate('BatteryChargeStatus_I', DataTypes.BatteryChargeStatus_T)
VehicleSpeed_I = createSenderReceiverInterfaceTemplate('VehicleSpeed_I', DataTypes.VehicleSpeed_T)
EngineSpeed_I = createSenderReceiverInterfaceTemplate('EngineSpeed_I', DataTypes.EngineSpeed_T)
FuelLevelPercent_I = createSenderReceiverInterfaceTemplate('FuelLevelPercent_I', DataTypes.Percent_T)
TripDist_I = createSenderReceiverInterfaceTemplate('TripDist_I', DataTypes.DistanceHiRes_T)
LowFuelLevelWarning_I = createSenderReceiverInterfaceTemplate('LowFuelLevelWarning_I', DataTypes.InactiveActive_T)
RtcSeconds_I = createSenderReceiverInterfaceTemplate('RtcSeconds_I', DataTypes.Seconds_T)
RtcMinutes_I = createSenderReceiverInterfaceTemplate('RtcMinutes_I', DataTypes.Minutes_T)
RtcHours_I = createSenderReceiverInterfaceTemplate('RtcHours_I', DataTypes.Hours_T)

class SimpleNvm_I(autosar.Template):
   @classmethod
   def apply(cls, ws):
      package = ws.getPortInterfacePackage()
      if package.find(cls.__name__) is None:
         operationsList = ['SetRamBlockStatus']
         portInterface=package.createClientServerInterface(cls.__name__,
                                                           operationsList,
                                                           autosar.ApplicationError("E_NOT_OK", 1),
                                                           isService=True)
         portInterface["SetRamBlockStatus"].possibleErrors = "E_NOT_OK"
         portInterface['SetRamBlockStatus'].createInArgument("RamBlockStatus", "Boolean")