import sys
sys.path.insert(0,'..')
import autosar
import DataTypes

def _createSenderReceiverInterface(ws, name, dataTypeTemplate):
   package = ws.getPortInterfacePackage()
   if package.find(name) is None:
      ws.apply(dataTypeTemplate)
      package.createSenderReceiverInterface(name, autosar.DataElement(name, dataTypeTemplate.__name__))
      
class ParkBrakeStatus_I(autosar.Template):
   @classmethod
   def apply(cls, ws):      
      _createSenderReceiverInterface(ws, cls.__name__, DataTypes.ParkBrakeStatus_T)

class DirIndStat_I(autosar.Template):
   @classmethod
   def apply(cls, ws):      
      _createSenderReceiverInterface(ws, cls.__name__, DataTypes.DirIndStat_T)
