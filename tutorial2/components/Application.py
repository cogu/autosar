import sys
sys.path.insert(0,'../..')
sys.path.append('..')
import autosar
import Signals
import time
from TelltaleHandler import TelltaleHandler
from GaugeHandler import GaugeHandler

class Application(autosar.Template):
   @classmethod
   def apply(cls, ws):
      if ws.find(cls.__name__) is None:
         package = ws.getComponentTypePackage()
         swc = package.createCompositionComponent(cls.__name__)
         cls._addTelltaleHandler(ws, swc)
         cls._addGaugeHandler(ws, swc)
   
   @classmethod
   def _addTelltaleHandler(cls, ws, swc):
      ws.apply(TelltaleHandler)
      swc.apply(Signals.ParkBrakeStatus.Receive)
      swc.apply(Signals.DirIndStat.Receive)
      swc.createComponentRef('TelltaleHandler')
      swc.createConnector('ParkBrakeStatus', 'TelltaleHandler/ParkBrakeStatus')
      swc.createConnector('DirIndStat', 'TelltaleHandler/DirIndStat')

   @classmethod
   def _addGaugeHandler(cls, ws, swc):
      ws.apply(GaugeHandler)
      swc.apply(Signals.VehicleSpeed.Receive)      
      swc.createComponentRef('GaugeHandler')
      swc.createConnector('VehicleSpeed', 'GaugeHandler/VehicleSpeed')

if __name__ == '__main__':   
   ws = autosar.workspace()
   ws.apply(Application)
   swc = ws.find('Application', role='ComponentType')
   messages = swc.verify()
   #print(swc)   
   # ignoreList = []
   # ignoreList.append(ws.find('TelltaleHandler', role='ComponentType'))
   # ignoreList.append(ws.find('GaugeHandler', role='ComponentType'))
   # ws.saveXML('Application.arxml', packages=['ComponentType'], ignore=[swc.ref for swc in ignoreList])
