import sys
sys.path.insert(0,'../..')
sys.path.append('..')
import autosar
import PortInterfaces
import Signals

class FuelLevelMonitor(autosar.Template):
   @classmethod
   def apply(cls, ws):
      componentName = cls.__name__
      package = ws.getComponentTypePackage()
      if package.find(componentName) is None:
         swc = package.createApplicationSoftwareComponent(componentName)
         cls.addPorts(swc)
         cls.addBehavior(swc)
   
   @classmethod
   def addPorts(cls, swc):
      componentName = cls.__name__
      swc.apply(Signals.FuelLevelPercent.Receive)
      swc.apply(Signals.LowFuelLevelWarning.Send)
   
   @classmethod
   def addBehavior(cls, swc):
      componentName = cls.__name__
      swc.behavior.createRunnable(componentName+'_Init', portAccess=[x.name for x in swc.providePorts])
      swc.behavior.createRunnable(componentName+'_Exit', portAccess=[x.name for x in swc.providePorts])
      swc.behavior.createRunnable(componentName+'_Run', portAccess=[x.name for x in swc.requirePorts+swc.providePorts])
      swc.behavior.createTimerEvent(componentName+'_Run', 20)

if __name__ == '__main__':
   ws = autosar.workspace()
   ws.apply(FuelLevelMonitor)
   ws.saveXML('FuelLevelMonitor.arxml')
