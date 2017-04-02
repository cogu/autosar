import autosar.component
import autosar.rte.base
import cfile as C
from collections import namedtuple

class Variable:
   def __init__(self, name, typename, isQueued=False, queueLen=None):
      self.name = name
      self.typename = typename
      self.hasRead = False
      self.hasWrite = False
      self.isQueued = isQueued
      self.queueLen  = queueLen

class IntegerVariable(Variable):
   def __init__(self, name, typename, isQueued=False, queueLen=None, initValue=0):
      super().__init__(name, typename, isQueued, queueLen)
   

FunctionPrototype = namedtuple('FunctionPrototype', "shortname func")
Queue = namedtuple('Queue', "name typename length")

class Partition:
   
   def __init__(self):
      self.components = []
      self.prototypes = {
         'read': [],
         'write': [],
         'send': [],
         'receive': [],
         'mode': [],
         'call': [],
         'calprm': []
      }
      self.vars = {}
   
   def addComponent(self, swc, runnables = None, name=None):
      """
      adds software component to partition.
      Optional parameters:
      name: Can be used to override name of swc. Default is to use name from swc.
      """
      swc_name = name if name is not None else swc.name
      if isinstance(swc, autosar.component.ApplicationSoftwareComponent):
         ws = swc.rootWS()
         assert(ws is not None)
         runnableList = []
         if swc.behavior is not None:
            for runnable in swc.behavior.runnables:               
               if runnables is None or runnable.name in runnables:
                  runnableList.append(runnable)            
            dataElements=set()
            operations=set()
            for runnable in runnableList:               
               for dataPoint in runnable.dataReceivePoints+runnable.dataSendPoints:
                  key=(swc.behavior.componentRef, dataPoint.portRef, dataPoint.dataElemRef)
                  dataElements.add(key)
               for callPoint in runnable.serverCallPoints:
                  for elem in callPoint.operationInstanceRefs:
                     key=(swc.behavior.componentRef, elem.portRef, elem.operationRef)
                     operations.add(key)
            for elem in dataElements:
               (componentRef,portRef,dataElemRef)=elem
               swc=ws.find(componentRef)
               port=ws.find(portRef)
               dataElement = ws.find(dataElemRef)
               if dataElement is None:
                  raise ValueError(dataElemRef)
               typeObj=ws.find(dataElement.typeRef)
               if typeObj is None:
                  raise ValueError('invalid reference: %s'%dataElement.typeRef)
               pointer=False           
               ftype=None
               if dataElement.name not in self.vars:
                  self._createVar(port, dataElement, typeObj)
               if isinstance(port,autosar.component.RequirePort):
                  if dataElement.isQueued:
                     ftype='receive'                  
                  else:
                     ftype='read'                  
                  pointer=True
               else:
                  if dataElement.isQueued:
                     ftype='send'                  
                  else:
                     ftype='write'                  
               assert(ftype is not None)
               fname='Rte_%s_%s_%s_%s'%(ftype, swc_name, port.name, dataElement.name)
               shortname='Rte_%s_%s_%s'%(ftype, port.name, dataElement.name)
               typeArg=self._type2arg(typeObj,pointer)
               func=C.function(fname, 'Std_ReturnType')
               func.add_arg(typeArg)
               self.prototypes[ftype].append(FunctionPrototype(shortname,func))
               
   
            for elem in operations:
               (componentRef,portRef,operationRef)=elem
               swc=ws.find(componentRef)
               port=ws.find(portRef)
               operation = ws.find(operationRef)
               if operation is None:
                  raise ValueError('invalid reference: '+operationRef)
               args=[]
               for argument in operation.arguments:
                  dataType = ws.find(argument.typeRef)
                  pointer = None
                  if isinstance(dataType, autosar.datatype.RecordDataType) or isinstance(dataType, autosar.datatype.ArrayDataType):
                     pointer=True
                  else:
                     pointer=False
                  if argument.direction == 'INOUT' or argument.direction=='OUT':
                     pointer=True               
                  args.append(C.variable(argument.name, dataType.name, pointer=pointer))
               fname='_'.join(['Rte_Call', swc_name, port.name, operation.name])
               shortname='_'.join(['Rte_Call', port.name, operation.name])            
               func=C.function(fname, 'Std_ReturnType', args=args)            
               self.prototypes['call'].append(FunctionPrototype(shortname,func))
         
               
   def _type2arg(self,typeObj,pointer=False):
      if ( isinstance(typeObj,autosar.datatype.IntegerDataType) or isinstance(typeObj,autosar.datatype.BooleanDataType) ):
         return C.variable('data',typeObj.name,pointer=pointer)
      else:
         pointer=True
         return C.variable('data',typeObj.name,pointer=pointer)
   
   def _createVar(self, port, dataElement, dataType):
      """
      creates new Variable or Queue object in self.vars map
      """
      if isinstance(dataType, autosar.datatype.IntegerDataType):
         pass
      elif isinstance(dataType, autosar.datatype.RecordDataType):
         pass
      elif isinstance(dataType, autosar.datatype.StringDataType):
         pass
      else:
         raise NotImplementedError(type(dataType))
