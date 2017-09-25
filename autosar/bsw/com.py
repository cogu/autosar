import autosar.base
import autosar.component
import autosar.portinterface

# class Signal:
#    def __init__(self, name, port, dataElement, dataType):
#       self.name = name
#       self.port = port
#       self.dataElement = dataElement
#       self.dataType = dataType
#       self.initValue = None
#       for comspec in port.comspec:
#          if isinstance(comspec, autosar.component.DataElementComSpec) and (comspec.name == dataElement.name) and (comspec.initValueRef is not None):
#             ws = port.rootWS()
#             if ws is not None:
#                self.initValue = ws.find(comspec.initValueRef)
#                if self.initValue is None:
#                   raise InvalidInitValueRef(comspec.initValueRef)

class UpperLayerAPI:
   
   def __init__(self):
      self.receive = []
      self.send = []
      self.map = {}

class ReceiveFunction:   
   def __init__(self, proto, port, data_element):      
      self.proto = proto
      self.port = port
      self.data_element = data_element
      self.body = None

class SendFunction:   
   def __init__(self, proto, port, data_element):      
      self.proto = proto
      self.port = port
      self.data_element = data_element
      self.body = None


class ComComponent(autosar.component.AtomicSoftwareComponent):
   """
   A simplified configuration of a Com component
   """
   def __init__(self, ws, name = 'Com'):
      super().__init__(name,None)
      self.ws = ws      
      self.isFinalized = False
      self.upperLayerAPI = UpperLayerAPI()
   
   def rootWS(self):
      return self.ws
   
   def ref(self):
      return '/EcuC/%s'%self.name
   
   def addReceiveInterface(self, proto, port, data_element):
      if proto.name not in self.upperLayerAPI.map:
         func = ReceiveFunction(proto, port, data_element)
         self.upperLayerAPI.map[proto.name]=func
         self.upperLayerAPI.receive.append(func)
   
   def addSendInterface(self, proto, port, data_element):
      if proto.name not in self.upperLayerAPI.map:
         func = SendFunction(proto, port, data_element)
         self.upperLayerAPI.map[proto.name]=func
         self.upperLayerAPI.send.append(func)
