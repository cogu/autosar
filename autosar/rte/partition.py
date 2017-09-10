import autosar.base
import autosar.component
import autosar.rte.base
import cfile as C
from autosar.rte.base import PortConnector, PortInstance


#Queue = namedtuple('Queue', "name typename length")



def _type2arg(typeObj,pointer=False):
   if ( isinstance(typeObj,autosar.datatype.IntegerDataType) or isinstance(typeObj,autosar.datatype.BooleanDataType) ):
      return C.variable('data',typeObj.name,pointer=pointer)
   else:
      pointer=True
      return C.variable('data',typeObj.name,pointer=pointer)


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
   def __init__(self, shortname, func, port, portInterface, operation):
      super().__init__(shortname, func)
      self.port = port
      self.portInterface = portInterface
      self.operation = operation

class CalPrmPortFunction(PortFunction):
   """port function for Rte_Call actions"""
   def __init__(self, shortname, func):
      super().__init__(shortname, func)

class DataElement:
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

class TimerEvent:
   """Runnable triggered by timer"""
   def __init__(self, name, rte_runnable):
      self.name = name
      self.rte_runnable = rte_runnable


class OperationInvokeEvent:
   """triggered by server invocation"""
   def __init__(self, name, rte_runnable ):
      self.name = name
      self.rte_runnable = rte_runnable


   def createPrototype(self):
      ws = self.operation.rootWS()

      return func

class ModeSwitchEvent:
   """
   Runnable triggered by mode switch event
   """
   def __init__(self, ws, ar_event, rte_runnable):
      modeDeclaration = ws.find(ar_event.modeInstRef.modeDeclarationRef)
      if modeDeclaration is None:
         raise ValueError("Error: invalid reference: %s"+ar_event.modeInstRef.modeDeclarationRef)
      mode = modeDeclaration.parent
      self.activationType = 'OnEntry' if (ar_event.activationType == 'ON-ENTRY' or ar_event.activationType == 'ENTRY')  else 'OnExit'
      self.name = "%s_%s_%s"%(self.activationType, mode.name, modeDeclaration.name)
      self.mode=mode.name
      self.modeDeclaration=modeDeclaration.name
      self.rte_runnable = rte_runnable

class ComponentAPI:
   """
   defines the API both for clients (components) and server (RTE)
   """
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

   def get_data_element_functions(self):
      return list(self.read.values())+list(self.write.values())+list(self.send.values())+list(self.receive.values())

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
   def __init__(self, swc, rte_prefix='Rte'):
      self.swc = swc
      self.clientAPI = ComponentAPI() #function calls towards the RTE (stuff that the RTE must provide)
      self.read = {}
      self.write = {}
      self.rte_runnables = {}
      self.rte_events = []
      #self.server_runnables = {}
      self.parameters = set()
      self.data_elements = {}
      self.rte_prefix = rte_prefix

   def finalize(self):
      self.clientAPI.finalize()
      self._create_data_elements()

   def get_runnable(self, name):
      return self.rte_runnables[name]

   def create_server_call_point(self, ws, port, operation):
      shortname='_'.join([self.rte_prefix,'Call', port.name, operation.name])
      func = C.function(shortname, 'Std_ReturnType')
      portInterface = ws.find(port.portInterfaceRef)
      if portInterface is None:
         raise ValueError("Error: invalid port interface reference: "+port.portInterfaceRef)
      for argument in operation.arguments:
         dataType = ws.find(argument.typeRef)
         if dataType is None:
            raise ValueError('Error: Invalid type reference: '+argument.typeRef)
         isPointer = False
         if dataType.isComplexType or (argument.direction == 'OUT') or (argument.direction == 'INOUT'):
            isPointer = True
         func.add_arg(C.variable(argument.name, dataType.name, pointer=isPointer))

         rte_port_func = CallPortFunction(shortname, func, port, portInterface, operation)
         self.clientAPI.call[shortname] = rte_port_func

   def create_data_receive_point(self, ws, port, data_element, data_type):
      if data_element.isQueued:
         call_type='Receive'
      else:
         call_type='Read'
      pointer=True
      fname='%s_%s_%s_%s_%s'%(self.rte_prefix, call_type, self.swc.name, port.name, data_element.name)
      shortname='%s_%s_%s_%s'%(self.rte_prefix, call_type, port.name, data_element.name)
      type_arg=_type2arg(data_type,pointer)
      func=C.function(fname, 'Std_ReturnType')
      func.add_arg(type_arg)
      if shortname not in self.clientAPI.__dict__[call_type.lower()]:
         rte_port_func = None
         rte_data_element = None
         if len(port.comspec)>0 and (port.comspec[0].initValueRef is not None):
            initValue = ws.find(port.comspec[0].initValueRef)
         rte_data_element = DataElement(port.name, data_type, initValue)
         if call_type == 'Read':
            rte_port_func = ReadPortFunction(shortname, func, rte_data_element)
         else:
            rte_port_func = ReceivePortFunction(shortname, func, rte_data_element)
         self.clientAPI.__dict__[call_type.lower()][shortname] = rte_port_func

   def create_data_send_point(self, ws, port, data_element, data_type):
      if data_element.isQueued:
         call_type='Send'
      else:
         call_type='Write'
      pointer=True if data_type.isComplexType else False
      fname='%s_%s_%s_%s_%s'%(self.rte_prefix, call_type, self.swc.name, port.name, data_element.name)
      shortname='%s_%s_%s_%s'%(self.rte_prefix, call_type, port.name, data_element.name)
      type_arg=_type2arg(data_type,pointer)
      func=C.function(fname, 'Std_ReturnType')
      func.add_arg(type_arg)
      if shortname not in self.clientAPI.__dict__[call_type.lower()]:
         rte_port_func = None
         rte_data_element = None
         if len(port.comspec)>0 and (port.comspec[0].initValueRef is not None):
            initValue = ws.find(port.comspec[0].initValueRef)
         rte_data_element = DataElement(port.name, data_type, initValue)
         if call_type == 'Send':
            rte_port_func = SendPortFunction(shortname, func, rte_data_element)
         else:
            rte_port_func = WritePortFunction(shortname, func, rte_data_element)
         self.clientAPI.__dict__[call_type.lower()][shortname] = rte_port_func
   def _create_data_elements(self):

      for port_function in self.clientAPI.get_data_element_functions():
         data_element = port_function.data_element
         if data_element.name not in self.data_elements:
            self.data_elements[data_element.name] = {'element': port_function.data_element, 'send': [], 'receive':[]}
         if isinstance(port_function, (ReadPortFunction, ReceivePortFunction)):
            self.data_elements[data_element.name]['receive'].append(port_function)
         elif isinstance(port_function, (WritePortFunction, ReceivePortFunction)):
            self.data_elements[data_element.name]['send'].append(port_function)

   def create_parameter(self, ws, port, data_element, data_type):
      shortname='_'.join([self.rte_prefix,'Calprm', port.name, data_element.name])
      prototype=C.function(shortname, data_type.name)
      self.clientAPI.calprm[shortname] = CalPrmPortFunction(shortname, prototype)

   def create_server_runnable(self, ws, port, operation, rte_runnable):
      port_interface = ws.find(port.portInterfaceRef)
      if port_interface is None:
         raise ValueError('Error: Invalid reference: %port.portInterfaceRef')
      self.rte_runnables[rte_runnable.name] = rte_runnable
      assert(rte_runnable.isServerRunnable)

   def add_event(self, rte_event):
      self.rte_events.append(rte_event)

class Runnable:
   """RTE Runnable"""
   def __init__(self, name, symbol, prototype = None):
      self.name = name
      self.symbol = symbol
      self.isServerRunnable=False
      self.serverPortInterface = None
      self.serverOperation = None
      self.events=[] #rte events
      if prototype is None:
         self.prototype = C.function(self.symbol, 'void')
      else:
         self.prototype = prototype
   @classmethod
   def OperationInvokedRunnable(cls, name, symbol, ws, port, operation):
      assert(ws is not None)
      returnType = 'void'
      if len(operation.errorRefs)>0:
         returnType = 'Std_ReturnType'
      prototype = C.function(symbol, returnType)
      for argument in operation.arguments:
         dataType = ws.find(argument.typeRef)
         if dataType is None:
            raise ValueError('invalid type reference: '+argument.typeRef)
         isPointer = False
         if isinstance(dataType, autosar.datatype.RecordDataType) or isinstance(dataType, autosar.datatype.ArrayDataType) or isinstance(dataType, autosar.datatype.ArrayDataType):
            isPointer = True
         if (isPointer == False) and (argument.direction == 'OUT') or (argument.direction == 'INOUT'):
            isPointer = True
         prototype.add_arg(C.variable(argument.name, dataType.name, pointer=isPointer))
      self = cls(name, symbol, prototype)
      self.isServerRunnable=True
      self.serverPortInterface = ws.find(port.portInterfaceRef)
      self.serverOperation = operation
      return self

class Partition:

   def __init__(self, mode='full', prefix='Rte'):
      self.mode = mode #can be single or full
      self.prefix=prefix
      self.components = [] #clients (components)
      self.serverAPI = ComponentAPI() #functions that the RTE must support towards its clients
      self.data_elements = {}
      self.types = autosar.rte.RteTypeManager() #centralized type manager
      self.isFinalized = False
      self.comLayerPrefix = None
      self.ws = None
      self.assemblyConnectors=[]
      self.assemblyConnectorMap={}

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
         if self.ws is None:
            self.ws = ws
         else:
            if self.ws is not ws:
               raise ValueError('Cannot add components from different workspaces!')
         component = Component(swc)
         self.components.append(component)
         if swc.behavior is not None:
            self._process_server_runnables(component, ws, swc, runnables)
            self._process_runnables(component, ws, swc, runnables)
            self._process_events(component, ws, swc, runnables)
         self._process_parameter_ports(component, ws, swc)


   def finalize(self):
      if not self.isFinalized:
         for component in self.components:
            component.finalize()
            self._resolveCallPoints(component)
            self._resolveDataElements(component)
            self._resolveParameters(component)
            self.serverAPI.update(component.clientAPI)
      self.serverAPI.finalize()
      self.isFinalized=True

   def createConnector(self, portRef1, portRef2):
      """
      creates a connector between an inner and outer port or between two inner ports
      portRef1 and portRef2 can be of either formats:
      'componentName/portName', 'portName' or 'componentRef/portName'
      """      
      assert (self.ws is not None)
      port1, component1 = self._analyzePortRef(portRef1)
      port2, component2 = self._analyzePortRef(portRef2)

      if isinstance(component1, autosar.component.ComponentType) and isinstance(component2, autosar.component.ComponentType):
         #create an assembly port between the two ports
         providePort=None
         requirePort=None
         if isinstance(port1, autosar.component.RequirePort) and isinstance(port2, autosar.component.ProvidePort):
            requesterComponent, providerComponent = component1, component2
            requirePort, providePort = port1, port2
         elif isinstance(port2, autosar.component.RequirePort) and isinstance(port1, autosar.component.ProvidePort):
            requesterComponent, providerComponent = component2, component1
            requirePort, providePort = port2, port1
         elif isinstance(port2, autosar.component.RequirePort) and isinstance(port1, autosar.component.RequirePort):
            raise ValueError('cannot create assembly connector between two require ports')
         else:
            raise ValueError('cannot create assembly connector between two provide ports')
            return self._createConnectorInternal(PortInstance(providerComponent,providePort), PortInstance(requesterComponent,requirePort))
      else:
         raise ValueError('invalid connector arguments ("%s", "%s")'%(portRef1, portRef2))

   
   def autoConnect(self):
      """
      Attemts to create compatible connectors between components
      """
      requirePortInstances = [] #list of rte.PortInstance
      providePortInstances = [] #list of rte.PortInstance
      for rteComponent in self.components:
         swc = rteComponent.swc
         for port in swc.requirePorts:
            requirePortInstances.append(PortInstance(swc, port))
         for port in swc.providePorts:
            providePortInstances.append(PortInstance(swc, port))
      
      for requirePortInstance in requirePortInstances:
         providePortInstance = self._findCompatibleProvidePort(requirePortInstance, providePortInstances)
            
   def _findCompatibleProvidePort(self, requirePortInstance, providePortInstances):
      requirePortInterface = self.ws.find(requirePortInstance.port.portInterfaceRef)
      if requirePortInterface is None: raise ValueError("Invalid port interface ref: %s"%requirePortInstance.port.portInterfaceRef)
      for providePortInstance in providePortInstances:
         providePortInterface = self.ws.find(providePortInstance.port.portInterfaceRef)
         if providePortInterface is None: raise ValueError("Invalid port interface ref: %s"%providePortInstance.port.portInterfaceRef)
         if requirePortInterface==providePortInterface:
            self._createConnectorInternal(providePortInstance, requirePortInstance)            
         
   def _createConnectorInternal(self, providePortInstance, requirePortInstance):
      connectorName='_'.join([providePortInstance.component.name, providePortInstance.port.name, requirePortInstance.component.name, requirePortInstance.port.name])
      if connectorName in self.assemblyConnectorMap:
         raise ValueError('connector "%s" already exists'%connectorName)
      connector = PortConnector(providePortInstance, requirePortInstance)
      self.assemblyConnectors.append(connector)
      self.assemblyConnectorMap[connectorName]=connector
      return connector
   
   def _process_parameter_ports(self, component, ws, swc):
      for port in swc.requirePorts:
         portInterface = ws.find(port.portInterfaceRef)
         if portInterface is not None:
            if isinstance(portInterface, autosar.portinterface.ParameterInterface):
               for data_element in portInterface.dataElements:
                  data_type = ws.find(data_element.typeRef)
                  if data_type is None:
                     raise ValueError("Error: Invalid type reference: "+ data_element.typeRef)
                  self.types.processType(ws, data_type)
                  component.create_parameter(ws, port, data_element, data_type)

   def _process_server_runnables(self, component, ws, swc, runnables=None):
      for event in swc.behavior.events:
         if isinstance(event, autosar.behavior.OperationInvokedEvent):
            runnable = ws.find(event.startOnEventRef)
            if runnable is None:
               raise ValueError('invalid reference: '+event.startOnEventRef)
            if runnables is None or runnable.name in runnables:
               if runnable.name not in component.rte_runnables:
                  iref = event.operationInstanceRef
                  port = ws.find(iref.portRef)
                  operation = ws.find(iref.operationRef)
                  if operation is None:
                     raise ValueError('invalid reference: '+iref.operationRef)
                  rte_runnable = Runnable.OperationInvokedRunnable(runnable.name, runnable.symbol, ws, port, operation)
                  component.create_server_runnable(ws, port, operation, rte_runnable)
                  for argument in operation.arguments:
                     dataType = ws.find(argument.typeRef)
                     if dataType is None:
                        raise ValueError('invalid type reference: '+argument.typeRef)
                     self.types.processType(ws, dataType)
               else:
                  rte_runnable=component.rte_runnables[runnable.name]
               rte_event = OperationInvokeEvent(event.name, rte_runnable)
               rte_runnable.events.append(rte_event)

   def _process_runnables(self, component, ws, swc, runnables=None):
      for autosar_runnable in swc.behavior.runnables:
         for dataPoint in autosar_runnable.dataReceivePoints+autosar_runnable.dataSendPoints:
            port=ws.find(dataPoint.portRef)
            if port is None:
               raise ValueError('Error: Invalid port reference: '+dataPoint.dataPoint.portRef)
            data_element = ws.find(dataPoint.dataElemRef)
            if data_element is None:
               raise ValueError('Error: Invalid data element reference: '+dataPoint.dataElemRef)
            data_type=ws.find(data_element.typeRef)
            if data_type is None:
               raise ValueError('Error: Invalid data type reference: %s'%data_element.typeRef)
            self.types.processType(ws, data_type)
            if isinstance(dataPoint, autosar.behavior.DataReceivePoint):
               component.create_data_receive_point(ws, port, data_element, data_type)
            elif isinstance(dataPoint, autosar.behavior.DataSendPoint):
               component.create_data_send_point(ws, port, data_element, data_type)
            else:
               raise ValueError('unknown type: '+str(type(dataPoint)))
         for callPoint in autosar_runnable.serverCallPoints:
            for instanceRef in callPoint.operationInstanceRefs:
               port = ws.find(instanceRef.portRef)
               if port is None:
                  raise ValueError('Error: Invalid port reference: '+instanceRef.portRef)
               operation = ws.find(instanceRef.operationRef)
               if port is None:
                  raise ValueError('Error: Invalid operation reference: '+instanceRef.operationRef)
               component.create_server_call_point(ws, port, operation)
         if autosar_runnable.symbol not in component.rte_runnables:
            prototype = C.function(autosar_runnable.symbol, 'void')
            component.rte_runnables[autosar_runnable.name] = Runnable(autosar_runnable.name, autosar_runnable.symbol, prototype)

   def _process_events(self, component, ws, swc, runnables=None):
      for event in swc.behavior.events:
         ar_runnable = ws.find(event.startOnEventRef)
         rte_runnable = component.get_runnable(ar_runnable.name)
         if isinstance(event, autosar.behavior.TimingEvent):
            rte_event = TimerEvent(event.name, rte_runnable)
            component.add_event(rte_event)
         elif isinstance(event, autosar.behavior.ModeSwitchEvent):
            if ar_runnable is None:
               raise ValueError('invalid reference: '+event.startOnEventRef)
            if runnables is None or ar_runnable.name in runnables:
               rte_event = ModeSwitchEvent(ws, event, rte_runnable)
               rte_runnable.events.append(rte_event)
               component.add_event(rte_event)
         elif isinstance(event, autosar.behavior.OperationInvokedEvent):
            pass #already processed
         else:
            raise NotImplementedError(type(event))

   def _analyzePortRef(self, portRef):
      parts=autosar.base.splitRef(portRef)
      if len(parts)>1:
         if len(parts)==2:
            #assume format 'componentName/portName' with ComponentType role set
            port=None
            for rteComponent in self.components:
               if rteComponent.swc.name == parts[0]:
                  port = rteComponent.swc.find(parts[1])
                  if port is None:
                     raise ValueError('component %s does not have port with name %s'%(rteComponent.swc.name,parts[1]))
                  component=rteComponent.swc
                  break
         else:
            #assume portRef1 is a full reference
            port = self.ws.find(portRef)
            component=port.parent
      else:
         raise ValueError('Invalid port reference: %s'%portRef)
      if port is None or not isinstance(port, autosar.component.Port):
         raise ValueError('invalid port name: '+parts[-1])
      return port,component

   def _resolveCallPoints(self, component):
      if len(component.clientAPI.call):
         for key in component.clientAPI.call:
            port_func = component.clientAPI.call[key]
            rte_runnable = self._findServerRunnable(component, port_func)
            if rte_runnable is None:
               #raise RuntimeError('Error: no RTE runnable found for %s in component %s'%(port_func.shortname, component.swc.name))
               port_func.func = self._createDefaultFunction(component, port_func.port, port_func.operation)
            else:
               port_func.func = rte_runnable.prototype


   def _findServerRunnable(self, component, port_func):
      for component2 in self.components:
         if component2 is component:
            next
         for rte_runnable in component2.rte_runnables.values():
            if rte_runnable.isServerRunnable:
               if (rte_runnable.serverPortInterface is port_func.portInterface) and (rte_runnable.serverOperation is port_func.operation):
                   return rte_runnable
      return None

   def _resolveDataElements(self, component):
      ws = component.swc.rootWS()
      assert(ws is not None)
      for data_element_name in component.data_elements.keys():
         function_map = component.data_elements[data_element_name]
         if data_element_name not in self.data_elements:
            data_element = None
            if len(component.data_elements[data_element_name]['send'])>0:
               data_element = component.data_elements[data_element_name]['send'][0].data_element
            elif len(component.data_elements[data_element_name]['receive'])>0:
               data_element = component.data_elements[data_element_name]['receive'][0].data_element
            if data_element is not None:
               self.data_elements[data_element_name] = {'element': data_element, 'send': [], 'receive': []}
            else:
               ValueError('failed to create data_element')

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
         if shortname in component.clientAPI.__dict__[ftype.lower()]:
            raise ValueError('error: %s already defined'%shortname)
         component.clientAPI.__dict__[ftype.lower()][shortname] = CalPrmPortFunction(shortname, func)

   def _createDefaultFunction(self, component, port, operation):
      ws = component.swc.rootWS()
      assert(ws is not None)
      func_name='_'.join([self.prefix,'Call', component.swc.name, port.name, operation.name])
      func = C.function(func_name, 'Std_ReturnType')
      portInterface = ws.find(port.portInterfaceRef)
      if portInterface is None:
         raise ValueError("Error: invalid port interface reference: "+port.portInterfaceRef)
      for argument in operation.arguments:
         dataType = ws.find(argument.typeRef)
         if dataType is None:
            raise ValueError('Error: Invalid type reference: '+argument.typeRef)
         self.types.processType(ws, dataType)
         isPointer = False
         if dataType.isComplexType or (argument.direction == 'OUT') or (argument.direction == 'INOUT'):
            isPointer = True
         func.add_arg(C.variable(argument.name, dataType.name, pointer=isPointer))
      return func
