import sys
sys.path.insert(0,'..')
import autosar

#### Enumeration Data Types ####
class InactiveActive_T(autosar.Template):
   valueTable=['InactiveActive_Inactive',
               'InactiveActive_Active',
               'InactiveActive_Error',
               'InactiveActive_NotAvailable']
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=cls.valueTable)

class ParkBrakeStatus_T(autosar.Template):
   valueTable=['ParkBrakeStatus_Released',
               'ParkBrakeStatus_Engaged',
               'ParkBrakeStatus_Error',
               'ParkBrakeStatus_NotAvailable']   
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=cls.valueTable)

class DirIndStat_T(autosar.Template):
   valueTable=['DirIndStat_Off',
               'DirIndStat_Inactive',
               'DirIndStat_LeftActive',
               'DirIndStat_RightActive',
               'DirIndStat_BothActive',
               'DirIndStat_Spare',
               'DirIndStat_Error',
               'DirIndStat_NotAvailable']
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=cls.valueTable)


class BatteryChargeStatus_T(autosar.Template):
   valueTable=['BatteryChargeStatus_Idle',
               'BatteryChargeStatus_Charging',
               'BatteryChargeStatus_Error',
               'BatteryChargeStatus_NotAvailable']   
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=cls.valueTable)

class VehicleSpeed_T(autosar.Template):
   minValue=0
   maxValue=65535
   offset=0
   scaling=1/64
   unit='kmph'
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:         
         package.createIntegerDataType(cls.__name__, min=cls.minValue, max=cls.maxValue, offset=cls.offset, scaling=cls.scaling, unit=cls.unit)

class EngineSpeed_T(autosar.Template):
   minValue=0
   maxValue=65535
   offset=0
   scaling=1/8
   unit='rpm'
   invalidRangeStart=None
   errorRangeStart=65024
   notAvailableRangeStart=65280
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:         
         package.createIntegerDataType(cls.__name__, min=cls.minValue, max=cls.maxValue, offset=cls.offset, scaling=cls.scaling, unit=cls.unit)

class Percent_T(autosar.Template):
   minValue=0
   maxValue=255
   offset=0
   scaling=0.4
   unit='percent'
   invalidRangeStart=251
   errorRangeStart=254
   notAvailableRangeStart=255
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:         
         package.createIntegerDataType(cls.__name__, min=cls.minValue, max=cls.maxValue, offset=cls.offset, scaling=cls.scaling, unit=cls.unit)

class Seconds_T(autosar.Template):
   minValue=0
   maxValue=255
   offset=0
   scaling=1
   unit='Seconds'
   invalidRangeStart=None
   errorRangeStart=254
   notAvailableRangeStart=255
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:         
         package.createIntegerDataType(cls.__name__, min=cls.minValue, max=cls.maxValue, offset=cls.offset, scaling=cls.scaling, unit=cls.unit)

class DistanceHiRes_T(autosar.Template):
   minValue=0
   maxValue=0xFFFFFFFF
   offset=0
   scaling=1
   unit='Meters'
   invalidRangeStart=None
   errorRangeStart=0xFE000000
   notAvailableRangeStart=0xFF000000
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:         
         package.createIntegerDataType(cls.__name__, min=cls.minValue, max=cls.maxValue, offset=cls.offset, scaling=cls.scaling, unit=cls.unit)