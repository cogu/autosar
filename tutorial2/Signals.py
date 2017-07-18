import sys
sys.path.insert(0,'..')
import autosar
import PortInterfaces
import types
from collections import namedtuple

def _createProvidePort(swc, name, portInterfaceTemplate, initValueTemplate=None):
   ws = swc.rootWS()
   ws.apply(portInterfaceTemplate)
   if initValueTemplate is not None:
      ws.apply(initValueTemplate)
      swc.createProvidePort(name, portInterfaceTemplate.__name__, initValue=initValueTemplate.__name__)
   else:
      swc.createProvidePort(name, portInterfaceTemplate.__name__)

def _createRequirePort(swc, name, portInterfaceTemplate, initValueTemplate=None):
   ws = swc.rootWS()
   ws.apply(portInterfaceTemplate)
   if initValueTemplate is not None:
      ws.apply(initValueTemplate)
      swc.createRequirePort(name, portInterfaceTemplate.__name__, initValue=initValueTemplate.__name__)
   else:
      swc.createRequirePort(name, portInterfaceTemplate.__name__)
   

def createSenderReceiverPortTemplate(name, portInterfaceTemplate):
   class SenderReceiverPortTemplate:
      class Provide(autosar.Template):
         @classmethod
         def apply(cls, swc):
            _createProvidePort(swc, name, portInterfaceTemplate)
            
      class Require(autosar.Template):
         @classmethod
         def apply(cls, swc):
            _createRequirePort(swc, name, portInterfaceTemplate)
      
      class Send(autosar.Template):
         @classmethod
         def apply(cls, swc):
            _createProvidePort(swc, name, portInterfaceTemplate)
         
      class Receive(autosar.Template):
         @classmethod
         def apply(cls, swc):
            _createRequirePort(swc, name, portInterfaceTemplate)
   return SenderReceiverPortTemplate

ParkBrakeStatus = createSenderReceiverPortTemplate('ParkBrakeStatus', PortInterfaces.ParkBrakeStatus_I)
DirIndStat = createSenderReceiverPortTemplate('DirIndStat', PortInterfaces.DirIndStat_I)
