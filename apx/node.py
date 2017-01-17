import autosar
import apx
from copy import deepcopy
if __name__ == '__main__':
   import base as apx

class Node:
   def __init__(self,name):
      self.name=name
      self.dataTypes = []
      self.requirePorts=[]
      self.providePorts=[]
      self.dataTypeMap = {}      
   
   def _updateDataType(self, ws, port):
      portInterface = ws.find(port.portInterfaceRef)
      if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
         if len(portInterface.dataElements)==1:         
            dataType = ws.find(portInterface.dataElements[0].typeRef)
            assert(dataType is not None)
            if dataType.name not in self.dataTypeMap:
               item = apx.DataType(ws,dataType)
               item.id=len(self.dataTypes)
               self.dataTypeMap[dataType.name]=item
               self.dataTypes.append(item)
               return item
            else:
               return self.dataTypeMap[dataType.name]
         elif len(portInterface.dataElements)>1:
            raise NotImplementedError('SenderReceiverInterface with more than 1 element not supported')

   
   def import_swc(self, ws, swc):
      assert(isinstance(swc, autosar.component.AtomicSoftwareComponent))
      for port in swc.providePorts:
         dataType=self._updateDataType(ws, port)
         self.providePorts.append(apx.ProvidePort(port.name, dataType.id, ws, port))
      for port in swc.requirePorts:
         dataType=self._updateDataType(ws, port)
         self.requirePorts.append(apx.RequirePort(port.name, dataType.id, ws, port))

   def write(self, fp):
      """
      writes node as text in fp
      """
      print('N"%s"'%self.name, file=fp)
      for dataType in self.dataTypes:
         print(str(dataType), file=fp)
      for port in self.providePorts:
         print(str(port), file=fp)
      for port in self.requirePorts:
         print(str(port), file=fp)
   
   def lines(self):
      """
      returns context as list of strings (one line at a time)
      """
      lines = ['N"%s"'%self.name]      
      for dataType in self.dataTypes:
         lines.append(str(dataType))
      for port in self.providePorts:
         lines.append(str(port))
      for port in self.requirePorts:
         lines.append(str(port))
      return lines
   
   def mirror(self, name):
      """
      clones the node in a version where all provide and require ports are reversed
      """
      mirror = Node(name)
      mirror.dataTypes = deepcopy(self.dataTypes)
      mirror.requirePorts = [port.mirror() for port in self.providePorts]
      mirror.providePorts = [port.mirror() for port in self.requirePorts]
      for dataType in mirror.dataTypes:
         mirror.dataTypeMap[dataType.name]=dataType
      return mirror
      
   
