import autosar.component
import autosar.rte.base
import cfile as C
from collections import namedtuple


FunctionPrototype = namedtuple('FunctionPrototype', "shortname func")
Queue = namedtuple('Queue', "name typename length")

class Prototypes:
   def __init__(self):
      self.read = {}
      self.write = {}
      self.send = {}
      self.receive = {}
      self.mode = {}
      self.call = {}
      self.calprm = {}
      
      self.final = {
                     'read': [],
                     'write': [],
                     'receive': [],
                     'send': [],
                     'mode': [],
                     'call': [],
                     'calprm': [],
                   }

   def finalize(self):      
      if len(self.read)>0:
         self.final['read']=[self.read[k] for k in sorted(self.read.keys())]
      if len(self.write)>0:
         self.final['write']=[self.write[k] for k in sorted(self.write.keys())]
      if len(self.receive)>0:
         self.final['receive']=[self.receive[k] for k in sorted(self.receive.keys())]
      if len(self.mode)>0:
         self.final['receive']=[self.mode[k] for k in sorted(self.mode.keys())]
      if len(self.call)>0:
         self.final['call']=[self.call[k] for k in sorted(self.call.keys())]
      if len(self.calprm)>0:
         self.final['calprm']=[self.calprm[k] for k in sorted(self.calprm.keys())]      
   
   def get_all(self):
      return self.final['read']+self.final['write']+self.final['receive']+self.final['send']+self.final['mode']+self.final['call']+self.final['calprm']
   
   def update(self, other):
      self.read.update(other.read)
      self.write.update(other.write)
      self.send.update(other.send)
      self.receive.update(other.receive)
      self.mode.update(other.mode)
      self.call.update(other.call)
      self.calprm.update(other.calprm)

class Component:
   def __init__(self, swc):
      self.swc = swc
      self.prototypes = Prototypes()


class Partition:
   
   def __init__(self, mode='full', prefix='Rte'):
      self.mode = mode #can be single or full
      self.prefix=prefix
      self.components = []
      self.prototypes = Prototypes()
      self.vars = {}
      self.types = autosar.rte.RteTypeManager()
      self.isFinalized=False
   
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
         component = Component(swc)
         self.components.append(component)
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
               self.types.processType(ws, typeObj)
               pointer=False           
               ftype=None
               if dataElement.name not in self.vars:                  
                  if port.comspec[0].initValueRef is not None:                     
                     initValue = ws.find(port.comspec[0].initValueRef)                     
                  self._createVar(port, dataElement, typeObj, initValue)                  
               if isinstance(port,autosar.component.RequirePort):
                  if dataElement.isQueued:
                     ftype='Receive'
                  else:
                     ftype='Read'                  
                  pointer=True
               else:
                  if dataElement.isQueued:
                     ftype='Send'                  
                  else:
                     ftype='Write'                  
               assert(ftype is not None)
               if self.mode == 'single':
                  fname='%s_%s_%s_%s_%s'%(self.prefix, ftype, swc_name, port.name, dataElement.name)
               elif self.mode == 'full':
                  fname='%s_%s_%s_%s'%(self.prefix, ftype, port.name, dataElement.name)
               else:
                  raise ValueError('invalid mode value. Valid modes are "full" and "single"')
               shortname='Rte_%s_%s_%s'%(ftype, port.name, dataElement.name)
               typeArg=self._type2arg(typeObj,pointer)
               func=C.function(fname, 'Std_ReturnType')
               func.add_arg(typeArg)
               if shortname in component.prototypes.__dict__[ftype.lower()]:
                  raise ValueError('error: %s already defined'%shortname)
               component.prototypes.__dict__[ftype.lower()][shortname] = FunctionPrototype(shortname,func)
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
               fname='_'.join(['%s_Call'%self.prefix, swc_name, port.name, operation.name])
               shortname='_'.join(['%s_Call'%self.prefix, port.name, operation.name])            
               func=C.function(fname, 'Std_ReturnType', args=args)            
               component.prototypes.call[shortname]=FunctionPrototype(shortname,func)         
               
   def _type2arg(self,typeObj,pointer=False):
      if ( isinstance(typeObj,autosar.datatype.IntegerDataType) or isinstance(typeObj,autosar.datatype.BooleanDataType) ):
         return C.variable('data',typeObj.name,pointer=pointer)
      else:
         pointer=True
         return C.variable('data',typeObj.name,pointer=pointer)
   
   def _createVar(self, port, dataElement, dataType, initValue):
      """
      creates new Variable or Queue object in self.vars map
      """
      name = port.name
      assert(name not in self.vars)
      
      if isinstance(dataType, autosar.datatype.IntegerDataType):         
         if initValue is not None:
            assert(isinstance(initValue.value, autosar.constant.IntegerValue))
         initData=str(initValue.value.value)
         self.vars[name]=autosar.rte.IntegerVariable(name, dataType.name, initValue=initData)
      elif isinstance(dataType, autosar.datatype.RecordDataType):
         self.vars[name]=autosar.rte.RecordVariable(name, dataType.name)         
      elif isinstance(dataType, autosar.datatype.StringDataType):
         self.vars[name]=autosar.rte.ArrayVariable(name, dataType.name)
      else:
         raise NotImplementedError(type(dataType))

   def finalize(self):
      if self.isFinalized==False:
         for component in self.components:
            component.prototypes.finalize()
            self.prototypes.update(component.prototypes)
      self.prototypes.finalize()
      self.isFinalized=True
      