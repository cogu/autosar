import autosar.datatype
from collections import namedtuple

PortInstance = namedtuple('PortRef', 'component port')
PortConnector = namedtuple('PortConnector', 'provide require')

class RteTypeManager:
   
   def __init__(self):
      self.typeMap = {}
   
   def processType(self, ws, dataType):
      if dataType.ref not in self.typeMap:         
         if isinstance(dataType, autosar.datatype.RecordDataType):
            for elem in dataType.elements:
               childType = ws.find(elem.typeRef, role='DataType')
               if childType is None:
                  raise ValueError('invalid reference: ' + elem.typeRef)
               self.processType(ws, childType)
            self.typeMap[dataType.ref]=dataType
         elif isinstance(dataType, autosar.datatype.ArrayDataType):
               childType = ws.find(dataType.typeRef, role='DataType')
               if childType is None:
                  raise ValueError('invalid reference: ' + elem.typeRef)
               self.processType(ws, childType)
               self.typeMap[dataType.ref]=dataType
         else:
            self.typeMap[dataType.ref]=dataType
   
   def getTypes(self):
      basicTypes=set()
      complexTypes=set()
      modeTypes=set()
      
      for dataType in self.typeMap.values():
         if isinstance(dataType, autosar.datatype.RecordDataType) or isinstance(dataType, autosar.datatype.ArrayDataType):
            complexTypes.add(dataType.ref)
         elif isinstance(dataType, autosar.portinterface.ModeDeclarationGroup):
            modeTypes.add(dataType.ref)
         else:
            basicTypes.add(dataType.ref)
      return list(basicTypes),list(complexTypes),list(modeTypes)


class PortFunction:
   """base class for port functions"""
   def __init__(self, shortname, func):
      self.shortname = shortname
      self.func = func

class ReadPortFunction(PortFunction):
   """port function for Rte_Read actions"""
   def __init__(self, shortname, func, data_element):
      super().__init__(shortname, func)
      self.data_element = data_element

class WritePortFunction(PortFunction):
   """port function for Rte_Write actions"""
   def __init__(self, shortname, func, data_element):
      super().__init__(shortname, func)
      self.data_element = data_element

class SendPortFunction(PortFunction):
   """port function for Rte_Read actions"""
   def __init__(self, shortname, func, data_element):
      super().__init__(shortname, func)
      self.data_element = data_element

class ReceivePortFunction(PortFunction):
   """port function for Rte_Write actions"""
   def __init__(self, shortname, func, data_element):
      super().__init__(shortname, func)
      self.data_element = data_element

class CallPortFunction(PortFunction):
   """port function for Rte_Call actions"""
   def __init__(self, shortname, func, operation):
      super().__init__(shortname, func)
      self.operation = operation

class CalPrmPortFunction(PortFunction):
   """port function for Rte_Call actions"""
   def __init__(self, shortname, func):
      super().__init__(shortname, func)

class DataElement:
   """
   RTE wrapper around an autosar.portinterface.DataElement
   """
   def __init__(self, name, parent, dataType, initValue = None, isQueued=False, queueLength=None):
      self.symbol = None
      self.name = name
      self.dataType = dataType
      assert(parent is not None)
      self.parent = parent
      self.isQueued = isQueued
      self.queueLength = queueLength
      self.com_access = {'Send': None, 'Receive': None}
      if initValue is not None:
         self.initValue = initValue
      else:
         self.initValue = None

class Operation:
   """
   RTE wrapper around an autosar.portinterface.Operation
   """
   def __init__(self, name, parent, arguments, ar_operation):
      self.name = name
      self.parent=parent
      self.arguments = arguments
      self.ar_operation = ar_operation
