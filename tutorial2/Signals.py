import sys
sys.path.insert(0,'..')
import autosar
import PortInterfaces
import Constants
from SignalsHelper import createSenderReceiverPortTemplate

ParkBrakeStatus = createSenderReceiverPortTemplate('ParkBrakeStatus', PortInterfaces.ParkBrakeStatus_I, Constants.C_ParkBrakeStatus_IV, aliveTimeout=30)
DirIndStat = createSenderReceiverPortTemplate('DirIndStat', PortInterfaces.DirIndStat_I, Constants.C_DirIndStat_IV, aliveTimeout=30)
BatteryChargeStatus = createSenderReceiverPortTemplate('BatteryChargeStatus', PortInterfaces.BatteryChargeStatus_I, Constants.C_BatteryChargeStatus_IV, aliveTimeout=30)
VehicleSpeed = createSenderReceiverPortTemplate('VehicleSpeed', PortInterfaces.VehicleSpeed_I, Constants.C_VehicleSpeed_IV, aliveTimeout=30)
EngineSpeed = createSenderReceiverPortTemplate('EngineSpeed', PortInterfaces.EngineSpeed_I, Constants.C_EngineSpeed_IV, aliveTimeout=30)
FuelLevelPercent = createSenderReceiverPortTemplate('FuelLevelPercent', PortInterfaces.FuelLevelPercent_I, Constants.C_FuelLevelPercent_IV, aliveTimeout=30)
LowFuelLevelWarning = createSenderReceiverPortTemplate('LowFuelLevelWarning', PortInterfaces.LowFuelLevelWarning_I, Constants.C_LowFuelLevelWarning_IV)

