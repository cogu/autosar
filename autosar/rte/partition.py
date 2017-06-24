import autosar.component
import autosar.rte.base
import cfile as C
from collections import namedtuple


Queue = namedtuple('Queue', "name typename length")

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
   def __init__(self, shortname, func):
      super().__init__(shortname, func)

class CalPrmPortFunction(PortFunction):
   """port function for Rte_Call actions"""
   def __init__(self, shortname, func):
      super().__init__(shortname, func)

class RteDataElement:
   """
   defines an RTE data element
   """
   def __init__(self, name, dataType, initValue = None):
      self.name = name
      self.dataType = dataType      
      if (initValue is not None) and (isinstance(initValue, autosar.constant.Constant)):
         self.initValue = initValue.value
      else:
         self.initValue = initValue

   
   
class ComponentAPI:
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
                     'modeswitch': [],
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
   """
   Container clas for AUTOSAR SWC
   """
   def __init__(self, swc):
      self.swc = swc
      self.componentAPI = ComponentAPI()
      self.read = {}
      self.write = {}
      self.rteRunnables = {}
      self.rteEvents = {}
      self.autosarRunnables = []
      self.serverCallPoints = set()                
      self.parameters = set()
      self.dataElements = set()

class Runnable:
   """RTE Runnable"""
   def __init__(self, name, symbol, prototype = None):
      self.name = name
      self.symbol = symbol
      self.events = []
      if prototype is None:
         self.prototype = C.function(self.symbol, 'void')
      else:
         self.prototype = prototype
      

class TimerEvent:
   """Runnable triggered by timer"""
   def __init__(self, name, triggerOnEvent):
      self.name = name
      self.triggerOnEvent = triggerOnEvent
      

class OperationInvokeEvent:
   """Runnable triggered by server invocation"""
   def __init__(self, name, symbol, port, operation):
      self.name = name
      #self.symbol = symbol
      self.port = port
      self.operation = operation
      #self.prototype = self._createPrototype()
   
   def createPrototype(self):
      ws = self.operation.rootWS()
      assert(ws is not None)
      returnType = 'void'
      if len(self.operation.errorRefs)>0:
         returnType = 'Std_ReturnType'
      func = C.function(self.symbol, returnType)
      for argument in self.operation.arguments:
         dataType = ws.find(argument.typeRef)
         if dataType is None:
            raise ValueError('invalid type reference: '+argument.typeRef)
         isPointer = False
         if isinstance(dataType, autosar.datatype.RecordDataType) or isinstance(dataType, autosar.datatype.ArrayDataType) or isinstance(dataType, autosar.datatype.ArrayDataType):
            isPointer = True
         if (isPointer == False) and (argument.direction == 'OUT') or (argument.direction == 'INOUT'):
            isPointer = True
         func.add_arg(C.variable(argument.name, dataType.name, pointer=isPointer))
      return func

class ModeSwitchEvent:
   """
   Runnable triggered by mode switch event
   """
   def __init__(self, name, symbol, eventName):
      self.name = name
      #self.symbol = symbol         


class Partition:
   
   def __init__(self, mode='full', prefix='Rte'):
      self.mode = mode #can be single or full
      self.prefix=prefix
      self.components = []
      self.componentAPI = ComponentAPI() #merged API for all components
      self.dataElements = {}
      self.types = autosar.rte.RteTypeManager()
      self.isFinalized = False
      self.comLayerPrefix = None
   
   def addComponent(self, swc, runnables = None, name=None):
      """
      adds software component to partition.
      Optional parameters:
      name: Can be used to override name of swc. Default is to use name from swc.
      """
      swc_name = name if name is not None else swc.name
      if isinstance(swc, autosar.component.AtomicSoftwareComponent):
         ws = swc.rootWS()         
         assert(ws is not None)
         component = Component(swc)
         self.components.append(component)         
         if swc.behavior is not None:
            for runnable in swc.behavior.runnables:               
               if runnables is None or runnable.name in runnables:   
                  component.autosarRunnables.append(runnable)
            #events
            for event in swc.behavior.events:
               if isinstance(event, autosar.behavior.TimingEvent):
                  runnable = ws.find(event.startOnEventRef)
                  if runnable is None:
                     raise ValueError('invalid reference: '+event.startOnEventRef)
                  if runnables is None or runnable.name in runnables:
                     if runnable.name not in component.rteRunnables:
                        component.rteRunnables[runnable.name] = TimerRunnable(runnable.name, runnable.symbol, event.period, runnable.invokeConcurrently)                         
               elif isinstance(event, autosar.behavior.OperationInvokedEvent):
                  runnable = ws.find(event.startOnEventRef)
                  if runnable is None:
                     raise ValueError('invalid reference: '+event.startOnEventRef)
                  if runnables is None or runnable.name in runnables:
                     if runnable.name not in component.rteRunnables: 
                        iref = event.operationInstanceRef
                        port = ws.find(iref.portRef)
                        operation = ws.find(iref.operationRef)
                        if operation is None:
                           raise ValueError('invalid reference: '+iref.operationRef)   
                        rte_runnable = OperationInvokeRunnable(runnable.name, runnable.symbol, port, operation)
                        component.rteRunnables[runnable.name] = rte_runnable
                        for argument in operation.arguments:
                           dataType = ws.find(argument.typeRef)
                        if dataType is None:
                           raise ValueError('invalid type reference: '+argument.typeRef)
                        self.types.processType(ws, dataType)
               elif isinstance(event, autosar.behavior.ModeSwitchEvent):
                  runnable = ws.find(event.startOnEventRef)
                  if runnable is None:
                     raise ValueError('invalid reference: '+event.startOnEventRef)
                  if runnables is None or runnable.name in runnables:
                     #print("runnable=%s"%runnable.name)
                     modeDeclaration = ws.find(event.modeInstRef.modeDeclarationRef)
                     mode = modeDeclaration.parent
                     activationType = 'OnEntry' if (event.activationType == 'ON-ENTRY' or event.activationType == 'ENTRY')  else 'OnExit'
                     eventName = "%s_%s_%s"%(activationType, mode.name, modeDeclaration.name)
                     #rte_runnable = ModeSwitchRunnable(runnable.name, runnable.symbol, eventName)
                     component.rteRunnables[runnable.name] = rte_runnable
               else:
                  raise NotImplementedError(type(event))
                     
                  
            #RTE send and call
            for runnable in component.autosarRunnables:
               for dataPoint in runnable.dataReceivePoints+runnable.dataSendPoints:
                  key=(swc.behavior.componentRef, dataPoint.portRef, dataPoint.dataElemRef)
                  component.dataElements.add(key)
               for callPoint in runnable.serverCallPoints:
                  for elem in callPoint.operationInstanceRefs:
                     key=(swc.behavior.componentRef, elem.portRef, elem.operationRef)
                     component.serverCallPoints.add(key)
            
            #parameter ports
            for port in swc.requirePorts:               
               portInterface = ws.find(port.portInterfaceRef)
               if portInterface is not None:
                  if isinstance(portInterface, autosar.portinterface.ParameterInterface):                     
                     for dataElement in portInterface.dataElements:                        
                        key = (swc.ref, port.ref, dataElement.ref)
                        component.parameters.add(key)
            
            
   def _type2arg(self,typeObj,pointer=False):
      if ( isinstance(typeObj,autosar.datatype.IntegerDataType) or isinstance(typeObj,autosar.datatype.BooleanDataType) ):
         return C.variable('data',typeObj.name,pointer=pointer)
      else:
         pointer=True
         return C.variable('data',typeObj.name,pointer=pointer)
   
   def _createDataElement(self, port, dataElement, dataType, initValue = None):
      """
      creates new DataElement object
      """
      name = port.name
      
      if name not in self.dataElements:         
         element = RteDataElement(name, dataType, initValue)
         self.dataElements[name] = element
      # if isinstance(dataType, autosar.datatype.BooleanDataType):
      #    self.vars[name]=autosar.rte.BooleanVariable(name, dataType.name)
      # elif isinstance(dataType, autosar.datatype.IntegerDataType):         
      #    if initValue is not None:
      #       assert(isinstance(initValue, autosar.constant.IntegerValue))
      #       initData=str(initValue.value)
      #    retval = autosar.rte.IntegerVariable(name, dataType.name, initValue=initData)
      # elif isinstance(dataType, autosar.datatype.RecordDataType):
      #    retval = autosar.rte.RecordVariable(name, dataType.name)
      # elif isinstance(dataType, autosar.datatype.StringDataType):
      #    retval = autosar.rte.ArrayVariable(name, dataType.name)         
      # else:
      #    raise NotImplementedError(type(dataType))
      # self.vars[name]= retval
      # return retval
      return self.dataElements[name]

   def finalize(self):
      if self.isFinalized==False:
         for component in self.components:
            self._resolveCallPoints(component)
            self._resolveDataElements(component)
            self._resolveParameters(component)
            component.componentAPI.finalize()
            self.componentAPI.update(component.componentAPI)
      self.componentAPI.finalize()
      self.isFinalized=True
    
   def _resolveCallPoints(self, component):
      ws = component.swc.rootWS()
      assert(ws is not None)
      for elem in component.serverCallPoints:         
         (componentRef,portRef,operationRef)=elem
         swc=ws.find(componentRef)
         port=ws.find(portRef)
         operation = ws.find(operationRef)         
         if operation is None:
            raise ValueError('invalid reference: '+operationRef)
         portInterface = ws.find(port.portInterfaceRef)
         if portInterface is None:
            raise ValueError('invalid reference: '+port.portInterfaceRef)
         serverRunnable = self._findServerRunnable(portInterface, operation)
         if serverRunnable is not None:
            shortname='_'.join(['%s_Call'%self.prefix, port.name, operation.name])
            component.componentAPI.call[shortname]=CallPortFunction(shortname, serverRunnable.prototype)

   def _findServerRunnable(self, portInterface, operation):
      """
      Searches the RTE partition for a invocation runnable that implements the given operation
      
      Returns:
      Runnable object on success, None on failure.
      """
      for component in self.components:
         swc = component.swc
         ws = swc.rootWS()
         assert (ws is not None)
         for runnable in [x for x in component.rteRunnables.values() if isinstance(x, OperationInvokeRunnable)]:
            serverPortInterface = ws.find(runnable.port.portInterfaceRef)
            assert(serverPortInterface is not None)
            if (serverPortInterface.ref == portInterface.ref) and (runnable.operation.name == operation.name):
               return runnable            
      return None
   
   def _resolveDataElements(self, component):
      ws = component.swc.rootWS()
      assert(ws is not None)
      for elem in component.dataElements:
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
         rte_data_element = None
         if len(port.comspec)>0 and (port.comspec[0].initValueRef is not None):                  
            initValue = ws.find(port.comspec[0].initValueRef)                    
         rte_data_element = self._createDataElement(port, dataElement, typeObj, initValue)
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
         if shortname in component.componentAPI.__dict__[ftype.lower()]:
            raise ValueError('error: %s already defined'%shortname)
         
         rte_port_func = None
         if ftype == 'Read':
            rte_port_func = ReadPortFunction(shortname, func, rte_data_element)
         elif ftype == 'Write':
            rte_port_func = WritePortFunction(shortname, func, rte_data_element)
         elif ftype == 'Send':
            rte_port_func = SendPortFunction(shortname, func, rte_data_element)
         elif ftype == 'Receive':
            rte_port_func = ReceivePortFunction(shortname, func, rte_data_element)
         else:
            raise NotImplementedError(ftype)
         component.componentAPI.__dict__[ftype.lower()][shortname] = rte_port_func

   def _resolveParameters(self, component):
      ws = component.swc.rootWS()
      assert(ws is not None)
      for elem in component.parameters:
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
         ftype='Calprm'
         if self.mode == 'single':
            fname='%s_%s_%s_%s_%s'%(self.prefix, ftype, swc_name, port.name, dataElement.name)
         elif self.mode == 'full':
            fname='%s_%s_%s_%s'%(self.prefix, ftype, port.name, dataElement.name)
         else:
            raise ValueError('invalid mode value. Valid modes are "full" and "single"')
         shortname='Rte_%s_%s_%s'%(ftype, port.name, dataElement.name)               
         func=C.function(fname, typeObj.name)               
         if shortname in component.componentAPI.__dict__[ftype.lower()]:
            raise ValueError('error: %s already defined'%shortname)
         component.componentAPI.__dict__[ftype.lower()][shortname] = CalPrmPortFunction(shortname, func)
      
