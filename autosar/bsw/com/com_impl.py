import autosar.base

class Signal:
   def __init__(self, name, dataType):
      self.name = name
      self.dataType = dataType

class Config:
   def __init__(self, prefix = 'Com'):
      self.prefix = prefix
      self.receive={}
      self.send={}
   
   def addReceiveInterface(self, signalName, typeName):
      """
      adds a new <prefix>_Receive_<signalName>(<typeName>)
      """
      assert(signalName is not None)
      assert(typeName is not None)
      self.receive[signalName]=Signal(signalName, typeName)
   
   def addSendInterface(self, signalName, typeName):
      """
      adds a new <prefix>_Send_<signalName>(<typeName>)
      """
      assert(signalName is not None)
      assert(typeName is not None)
      self.send[signalName]=Signal(signalName, typeName)
      
   