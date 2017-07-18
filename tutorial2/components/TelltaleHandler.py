import sys
sys.path.insert(0,'../..')
sys.path.append('..')
import autosar
import PortInterfaces
import Signals

class TelltaleHandler(autosar.Template):
   @classmethod
   def apply(cls, ws):
      package = ws.getComponentTypePackage()
      if package.find(cls.__name__) is None:
         swc = package.createApplicationSoftwareComponent(cls.__name__)
         swc.apply(Signals.ParkBrakeStatus.Receive)
         swc.apply(Signals.DirIndStat.Receive)


if __name__ == '__main__':
   ws = autosar.workspace()
   ws.apply(TelltaleHandler)
   #ws.packages = sorted(ws.packages, key=lambda x:x.name.lower())
   ws.saveXML('TellTaleHandler.arxml')
   
         
