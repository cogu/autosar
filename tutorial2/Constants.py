import sys
sys.path.insert(0,'..')
import autosar
import DataTypes

#### Helpers ####
def createConstantTemplateFromEnumerationType(name, dataTypeTemplate):
   @classmethod
   def apply(cls, ws):
      package = ws.getConstantPackage()
      if package.find(cls.__name__) is None:
         ws.apply(cls.dataTypeTemplate)
         package.createConstant(cls.__name__, cls.dataTypeTemplate.__name__, len(cls.dataTypeTemplate.valueTable)-1)
   return type(name, (autosar.Template,), dict(dataTypeTemplate=dataTypeTemplate, apply=apply))

def createConstantTemplateFromPhysicalType(name, dataTypeTemplate):
   @classmethod
   def apply(cls, ws):
      package = ws.getConstantPackage()
      if package.find(cls.__name__) is None:
         ws.apply(cls.dataTypeTemplate)
         package.createConstant(cls.__name__, cls.dataTypeTemplate.__name__, cls.dataTypeTemplate.maxValue)
   return type(name, (autosar.Template,), dict(dataTypeTemplate=dataTypeTemplate, apply=apply))

#### Enumeration Constants ####
C_ParkBrakeStatus_IV = createConstantTemplateFromEnumerationType('C_ParkBrakeStatus_IV', DataTypes.ParkBrakeStatus_T)
C_DirIndStat_IV = createConstantTemplateFromEnumerationType('C_DirIndStat_IV', DataTypes.DirIndStat_T)
C_BatteryChargeStatus_IV = createConstantTemplateFromEnumerationType('C_BatteryChargeStatus_IV', DataTypes.BatteryChargeStatus_T)
C_LowFuelLevelWarning_IV = createConstantTemplateFromEnumerationType('C_LowFuelLevelWarning_IV', DataTypes.InactiveActive_T)

#### Physical Constants ####
C_VehicleSpeed_IV = createConstantTemplateFromPhysicalType('C_VehicleSpeed_IV', DataTypes.VehicleSpeed_T)
C_EngineSpeed_IV = createConstantTemplateFromPhysicalType('C_EngineSpeed_IV', DataTypes.EngineSpeed_T)
C_FuelLevelPercent_IV = createConstantTemplateFromPhysicalType('C_FuelLevelPercent_IV', DataTypes.Percent_T)
C_TripDistA_IV = createConstantTemplateFromPhysicalType('C_TripDistA_IV', DataTypes.DistanceHiRes_T)
C_TripDistB_IV = createConstantTemplateFromPhysicalType('C_TripDistB_IV', DataTypes.DistanceHiRes_T)
C_TripDistTotal_IV = createConstantTemplateFromPhysicalType('C_TripDistTotal_IV', DataTypes.DistanceHiRes_T)
C_RtcSeconds_IV = createConstantTemplateFromPhysicalType('C_RtcSeconds_IV', DataTypes.Seconds_T)
C_RtcMinutes_IV = createConstantTemplateFromPhysicalType('C_RtcMinutes_IV', DataTypes.Minutes_T)
C_RtcHours_IV = createConstantTemplateFromPhysicalType('C_RtcHours_IV', DataTypes.Hours_T)