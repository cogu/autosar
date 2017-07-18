import sys
sys.path.insert(0,'..')
import autosar

class InactiveActive_T(autosar.Template):
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=['InactiveActive_Inactive',
                                                                 'InactiveActive_Active',
                                                                 'InactiveActive_Error',
                                                                 'InactiveActive_NotAvailable'])

class ParkBrakeStatus_T(autosar.Template):
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=['ParkBrakeStatus_Released',
                                                                 'ParkBrakeStatus_Engaged',
                                                                 'ParkBrakeStatus_Error',
                                                                 'ParkBrakeStatus_NotAvailable'])

class DirIndStat_T(autosar.Template):
   @classmethod
   def apply(cls, ws):
      package = ws.getDataTypePackage()
      if package.find(cls.__name__) is None:
         package.createIntegerDataType(cls.__name__, valueTable=['DirIndStat_Off',
                                                                 'DirIndStat_Inactive',
                                                                 'DirIndStat_LeftActive',
                                                                 'DirIndStat_RightActive',
                                                                 'DirIndStat_BothActive',
                                                                 'DirIndStat_Spare',
                                                                 'DirIndStat_Error',
                                                                 'DirIndStat_NotAvailable'])
