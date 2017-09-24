import autosar.base
import autosar.component
import autosar.rte.base
from autosar.rte.base import (ReadPortFunction, WritePortFunction, SendPortFunction, ReceivePortFunction, CallPortFunction,
                              CalPrmPortFunction, DataElement, Operation)
import cfile as C
import sys
import autosar.bsw.com

def _type2arg(typeObj,pointer=False):
   if ( isinstance(typeObj,autosar.datatype.IntegerDataType) or isinstance(typeObj,autosar.datatype.BooleanDataType) ):
      return C.variable('data',typeObj.name,pointer=pointer)
   else:
      pointer=True
      return C.variable('data',typeObj.name,pointer=pointer)



class TimerEvent:
   """Runnable triggered by timer"""
   def __init__(self, runnable):      
      self.runnable = runnable


class OperationInvokedEvent:
   """triggered by server invocation"""
   def __init__(self, runnable, port, operation):
      self.runnable = runnable
      self.port = port
      self.operation = operation
      self.runnable.prototype=C.function(runnable.symbol, 'Std_ReturnType', args=operation.arguments)

class ModeSwitchEvent:
   """
   Runnable triggered by mode switch event
   """
   def __init__(self, ws, ar_event, runnable):
      modeDeclaration = ws.find(ar_event.modeInstRef.modeDeclarationRef)
      if modeDeclaration is None:
         raise ValueError("Error: invalid reference: %s"+ar_event.modeInstRef.modeDeclarationRef)
      mode = modeDeclaration.parent
      self.activationType = 'OnEntry' if (ar_event.activationType == 'ON-ENTRY' or ar_event.activationType == 'ENTRY')  else 'OnExit'
      self.name = "%s_%s_%s"%(self.activationType, mode.name, modeDeclaration.name)
      self.mode=mode.name
      self.modeDeclaration=modeDeclaration.name
      self.runnable = runnable

class Port:
   def __init__(self, ws, ar_port, parent):
      self.ws = ws
      self.name = ar_port.name
      self.ar_port = ar_port
      self.parent = parent
      self.connectors=[] #list of connected ports
      self.portAPI={}
      self.data_elements = []
      self.operations = []
      self.mode_groups = []

      port_interface = ws.find(ar_port.portInterfaceRef)
      if port_interface is None:
         raise ValueError("Error: invalid port interface reference: "+ar_port.portInterfaceRef)
      if isinstance(port_interface, autosar.portinterface.SenderReceiverInterface):
         for data_element in port_interface.dataElements:
            data_type=ws.find(data_element.typeRef)
            if data_type is None:
               raise ValueError('Error: Invalid data type reference: %s'%data_element.typeRef)
            initValue = None
            queueLength = None
            if len(ar_port.comspec)>0:
               for comspec in ar_port.comspec:
                  if (comspec.name == data_element.name) and (comspec.initValueRef is not None):
                     initValue = ws.find(comspec.initValueRef)
            self.data_elements.append(DataElement(data_element.name, self, data_type, initValue, data_element.isQueued))
      elif isinstance(port_interface, autosar.portinterface.ClientServerInterface):
         for operation in port_interface.operations:
            arguments = []
            for argument in operation.arguments:
               dataType = ws.find(argument.typeRef)
               if dataType is None:
                  raise ValueError('Error: Invalid type reference: '+argument.typeRef)
               isPointer = False
               if dataType.isComplexType or (argument.direction == 'OUT') or (argument.direction == 'INOUT'):
                  isPointer = True
               arguments.append(C.variable(argument.name, dataType.name, pointer=isPointer))
            self.operations.append(Operation(operation.name, self, arguments, operation))

   def find_data_element(self, name):
      for data_element in self.data_elements:
         if data_element.name == name: return data_element
      raise KeyError("No data element with name "+name)

   def find_operation(self, name):
      for operation in self.operations:
         if operation.name == name: return operation
      raise KeyError("No operation with name "+name)
   
   def process_types(self, ws, type_manager):
      for data_element in self.data_elements:
         type_manager.processType(ws, data_element.dataType)
      for operation in self.operations:
         for argument in operation.ar_operation.arguments:
            data_type = ws.find(argument.typeRef)
            if data_type is None:
               raise ValueError('Invalid Type Reference: '+argument.typeRef)
            type_manager.processType(ws, data_type)
      
   def update_client_api(self, api):
      for port_func in self.portAPI.values():
         if isinstance(port_func, ReadPortFunction):
            api.read[port_func.func.name]=port_func
         elif isinstance(port_func, WritePortFunction):
            api.write[port_func.func.name]=port_func
         elif isinstance(port_func, SendPortFunction):
            api.send[port_func.func.name]=port_func
         elif isinstance(port_func, ReceivePortFunction):
            api.receive[port_func.func.name]=port_func
         elif isinstance(port_func, CallPortFunction):
            api.call[port_func.func.name]=port_func
         elif isinstance(port_func, CalPrmPortFunction):
            api.calprm[port_func.func.name]=port_func

class ProvidePort(Port):
   """
   RTE ProvidePort
   """
   def __init__(self, ws, ar_port, parent):
      """
      ar_port: underlying autosar port
      parent: parent component
      """
      super().__init__(ws, ar_port, parent)

   def create_data_access_api(self, ws, rte_data_element):
      if rte_data_element.isQueued:
         call_type='Send'
      else:
         call_type='Write'
      data_type = rte_data_element.dataType
      pointer=True if data_type.isComplexType else False
      fname='%s_%s_%s_%s_%s'%(self.parent.rte_prefix, call_type, self.parent.name, self.name, rte_data_element.name)
      shortname='%s_%s_%s_%s'%(self.parent.rte_prefix, call_type, self.name, rte_data_element.name)
      type_arg=_type2arg(data_type,pointer)
      func=C.function(fname, 'Std_ReturnType')
      func.add_arg(type_arg)
      if shortname not in self.portAPI:
         rte_port_func = None         
         initValue = None
         ar_port = self.ar_port
         if len(ar_port.comspec)>0:
            for comspec in ar_port.comspec:
               if (comspec.name == rte_data_element.name) and (comspec.initValueRef is not None):
                  initValue = ws.find(comspec.initValueRef)         
         if call_type == 'Send':
            rte_port_func = SendPortFunction(shortname, func, rte_data_element)
         else:
            rte_port_func = WritePortFunction(shortname, func, rte_data_element)
         self.portAPI[shortname] = rte_port_func

class RequirePort(Port):
   """
   RTE RequirePort
   """
   def __init__(self, ws, ar_port, parent):
      """
      ar_port: underlying autosar port
      parent: parent component
      """
      super().__init__(ws, ar_port, parent)

   def create_data_access_api(self, ws, rte_data_element):
      if rte_data_element.isQueued:
         call_type='Receive'
      else:
         call_type='Read'
      pointer=True
      fname='%s_%s_%s_%s_%s'%(self.parent.rte_prefix, call_type, self.parent.name, self.name, rte_data_element.name)
      shortname='%s_%s_%s_%s'%(self.parent.rte_prefix, call_type, self.name, rte_data_element.name)
      data_type = rte_data_element.dataType
      type_arg=_type2arg(data_type,pointer)
      func=C.function(fname, 'Std_ReturnType')
      func.add_arg(type_arg)
      if shortname not in self.portAPI:
         rte_port_func = None         
         initValue = None
         queueLength = None
         ar_port = self.ar_port
         if len(ar_port.comspec)>0:
            for comspec in ar_port.comspec:
               if (comspec.name == rte_data_element.name) and (comspec.initValueRef is not None):
                  initValue = ws.find(comspec.initValueRef)
                  queueLength = comspec.queueLength         
         if call_type == 'Read':
            rte_port_func = ReadPortFunction(shortname, func, rte_data_element)
         else:
            rte_port_func = ReceivePortFunction(shortname, func, rte_data_element)
         self.portAPI[shortname] = rte_port_func
      
   def create_server_call_api(self, ws, rte_operation):      
      assert(ws is not None)
      shortname='_'.join([self.parent.rte_prefix, 'Call', self.name, rte_operation.name])
      func_name='_'.join([self.parent.rte_prefix, 'Call', self.parent.name, self.name, rte_operation.name])
      func = C.function(func_name, 'Std_ReturnType')
      for argument in rte_operation.arguments:
         func.add_arg(argument)      
      self.portAPI[shortname] = CallPortFunction(shortname, func, rte_operation)

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
   RTE Container class for AUTOSAR SWC
   """
   def __init__(self, swc, parent, rte_prefix='Rte'):
      self.parent = parent
      self.name = swc.name
      self.swc = swc
      self.clientAPI = ComponentAPI() #function calls towards the RTE (stuff that the RTE must provide)
#      self.rte_runnables = {}
      self.events = []
      self.runnables = []
      self.data_vars = []
      self.rte_prefix = rte_prefix
      self.is_finalized = False
      self.requirePorts = []
      self.providePorts = []
      ws = swc.rootWS()
      for ar_port in swc.providePorts:
         self.providePorts.append(ProvidePort(ws, ar_port, self))
      for ar_port in swc.requirePorts:
         self.requirePorts.append(RequirePort(ws, ar_port, self))


   def finalize(self,ws, type_manager):
      if not self.is_finalized:         
         for port in self.requirePorts+self.providePorts:
            port.process_types(ws, type_manager)
            port.update_client_api(self.clientAPI)
         self.clientAPI.finalize()         
         self._runnables_finalize()         
      self.is_finalized=True
         
      #self._create_data_elements()

   def get_runnable(self, name):
      return self.rte_runnables[name]

   def find_require_port(self, name):
      for port in self.requirePorts:
         if port.name == name: return port
      raise KeyError("No port found with name "+name)

   def find_provide_port(self, name):
      for port in self.providePorts:
         if port.name == name: return port
      raise KeyError("No port found with name "+name)

   def add_event(self, rte_event):
      self.rte_events.append(rte_event)

   def process_runnables(self, ws):
      if self.swc.behavior is not None:
         for ar_runnable in self.swc.behavior.runnables:
            runnable = Runnable(ar_runnable)
            self.runnables.append(runnable)
            for dataPoint in ar_runnable.dataReceivePoints+ar_runnable.dataSendPoints:
               ar_port=ws.find(dataPoint.portRef)
               if ar_port is None:
                  raise ValueError('Error: Invalid port reference: '+dataPoint.dataPoint.portRef)
               ar_data_element = ws.find(dataPoint.dataElemRef)
               if ar_data_element is None:
                  raise ValueError('Error: Invalid data element reference: '+dataPoint.dataElemRef)
               if isinstance(dataPoint, autosar.behavior.DataSendPoint):
                  port = self.find_provide_port(ar_port.name)
               else:
                  port = self.find_require_port(ar_port.name)
               data_element = port.find_data_element(ar_data_element.name)
               runnable.data_element_access.append(data_element)
               port.create_data_access_api(ws, data_element)               

            for callPoint in ar_runnable.serverCallPoints:
               for instanceRef in callPoint.operationInstanceRefs:
                  ar_port = ws.find(instanceRef.portRef)
                  if ar_port is None:
                     raise ValueError('Error: Invalid port reference: '+instanceRef.portRef)
                  ar_operation = ws.find(instanceRef.operationRef)
                  if ar_operation is None:
                     raise ValueError('Error: Invalid operation reference: '+instanceRef.operationRef)
                  port = self.find_require_port(ar_port.name)
                  operation = port.find_operation(ar_operation.name)
                  runnable.operation_access.append(operation)
                  port.create_server_call_api(ws, operation)
         for ar_event in self.swc.behavior.events:
            ar_runnable = ws.find(ar_event.startOnEventRef)
            if ar_runnable is None:
               raise ValueError('Invalid StartOnEvent reference: '+ar_event.startOnEventRef)
            for runnable in self.runnables:
               if runnable.inner is ar_runnable:
                  break
            else:
               raise ValueError('Runnable not found')
            if isinstance(ar_event, autosar.behavior.TimingEvent):               
               event = TimerEvent(runnable)
            elif isinstance(ar_event, autosar.behavior.ModeSwitchEvent):
               event = ModeSwitchEvent(ws, ar_event, runnable)
            elif isinstance(ar_event, autosar.behavior.OperationInvokedEvent):
               port_refs = autosar.base.splitRef(ar_event.operationInstanceRef.portRef)
               operation_refs = autosar.base.splitRef(ar_event.operationInstanceRef.operationRef)
               port = self.find_provide_port(port_refs[-1])
               assert (port is not None) and (port.ar_port is ws.find(ar_event.operationInstanceRef.portRef))
               operation = port.find_operation(operation_refs[-1])
               assert (operation is not None)               
               event = OperationInvokedEvent(runnable, port, operation)
            else:
               raise NotImplementedError(str(type(event)))
            self.events.append(event)
   
   def _runnables_finalize(self):
      operation_invoke_events = [event for event in self.events if isinstance(event, OperationInvokedEvent)]
      for runnable in self.runnables:
         if runnable.prototype is None:         
            runnable.prototype = (C.function(runnable.symbol, 'void'))
   
   def create_data_elements(self, data_element_map):
      
      for provide_port in self.providePorts:
         for require_port in provide_port.connectors:
            if len(require_port.data_elements)>0:
               for port_func in require_port.portAPI.values():
                  if isinstance(port_func, (ReadPortFunction, ReceivePortFunction)) and port_func.data_element.parent is require_port:
                     data_element = provide_port.find_data_element(port_func.data_element.name)                     
                     assert(data_element is not None)
                     data_element_name = '_'.join([self.name,provide_port.name,data_element.name])
                     if data_element_name not in data_element_map:
                        data_element.symbol = data_element_name
                        data_element_map[data_element_name] = data_element
                        #reassign require_port data element to access the data element from the provide port
                        port_func.data_element = data_element
                        
                     

class Runnable:
   """RTE Runnable"""
   def __init__(self, ar_runnable):
      self.inner = ar_runnable
      self.name = ar_runnable.name
      self.symbol = ar_runnable.symbol
      self.data_element_access=[]
      self.operation_access=[]
      self.prototype = None

class Partition:

   def __init__(self, mode='full', prefix='Rte'):      
      self.prefix=prefix
      self.components = [] #clients (components)
      self.serverAPI = ComponentAPI() #functions that the RTE must support towards its clients
      self.types = autosar.rte.RteTypeManager() #centralized type manager
      self.isFinalized = False      
      self.ws = None
      self.assemblyConnectorMap = {}
      self.data_element_map = {}

   def addComponent(self, swc, runnables = None, name=None):
      """
      adds software component to partition.
      Optional parameters:
      name: Can be used to override name of swc. Default is to use name from swc.
      """
      swc_name = name if name is not None else swc.name
      if isinstance(swc, (autosar.component.AtomicSoftwareComponent, autosar.bsw.com.ComComponent)):
         ws = swc.rootWS()
         assert(ws is not None)
         if self.ws is None:
            self.ws = ws
         else:
            if self.ws is not ws:
               raise ValueError('Cannot add components from different workspaces!')
         component = Component(swc, self)
         self.components.append(component)
      else:
         print("Unsupported component type: "+str(type(swc)), file=sys.stderr)


   def finalize(self):
      if not self.isFinalized:
         for component in self.components:
            component.process_runnables(self.ws)
            component.finalize(self.ws, self.types)            
            self.serverAPI.update(component.clientAPI)
         for component in self.components:
            component.create_data_elements(self.data_element_map)
         self._generate_com_access()
         self.serverAPI.finalize()
      self.isFinalized=True

   def createConnector(self, portRef1, portRef2):
      """
      creates a connector between two ports
      """
      assert (self.ws is not None)
      port1  = self._analyzePortRef(portRef1)
      port2 = self._analyzePortRef(portRef2)

      providePort=None
      requirePort=None
      if isinstance(port1, RequirePort) and isinstance(port2, ProvidePort):
         requirePort, providePort = port1, port2
      elif isinstance(port1, ProvidePort) and isinstance(port2, RequirePort):
         providePort, requirePort = port1, port2
      elif isinstance(port1, RequirePort) and isinstance(port2, RequirePort):
         raise ValueError('cannot create assembly connector between two require ports')
      else:
         raise ValueError('cannot create assembly connector between two provide ports')
      self._createConnectorInternal(providePort, requirePort)

   def autoConnect(self):
      """
      Attemts to create compatible connectors between components
      """
      require_port_list = [] #list of RequirePort
      provide_port_list = [] #list of ProvidePort
      for rte_comp in self.components:         
         for rte_port in rte_comp.requirePorts:
            require_port_list.append(rte_port)
         for rte_port in rte_comp.providePorts:
            provide_port_list.append(rte_port)

      for require_port in require_port_list:
         provide_port = self._findCompatibleProvidePort(require_port, provide_port_list)
         if provide_port is not None:
            self._createConnectorInternal(provide_port, require_port)
   
   def unconnectedPorts(self):
      """
      Returns a generator that yields all unconnected ports of this partition
      """
      for component in self.components:
         for port in component.requirePorts+component.providePorts:
            if len(port.connectors)==0:
               yield port


   def _findCompatibleProvidePort(self, require_port, provide_port_list):
      require_port_interface = self.ws.find(require_port.ar_port.portInterfaceRef)
      if require_port_interface is None: raise ValueError("Invalid port interface ref: %s"%require_port.ar_port.portInterfaceRef)
      for provide_port in provide_port_list:
         provide_port_interface = self.ws.find(provide_port.ar_port.portInterfaceRef)
         if provide_port_interface is None: raise ValueError("Invalid port interface ref: %s"%provide_port.ar_port.portInterfaceRef)
         if require_port_interface==provide_port_interface and (require_port.ar_port.name == provide_port.ar_port.name):
            return provide_port
      return None


   def _createConnectorInternal(self, provide_port, require_port):
      connectorName='_'.join([provide_port.parent.name, provide_port.name, require_port.parent.name, require_port.name])
      if connectorName in self.assemblyConnectorMap:
         raise ValueError('connector "%s" already exists'%connectorName)
      self.assemblyConnectorMap[connectorName]=(provide_port,require_port)
      provide_port.connectors.append(require_port)
      require_port.connectors.append(provide_port)

   # def _process_parameter_ports(self, component, ws, swc):
   #    for port in swc.requirePorts:
   #       portInterface = ws.find(port.portInterfaceRef)
   #       if portInterface is not None:
   #          if isinstance(portInterface, autosar.portinterface.ParameterInterface):
   #             for data_element in portInterface.dataElements:
   #                data_type = ws.find(data_element.typeRef)
   #                if data_type is None:
   #                   raise ValueError("Error: Invalid type reference: "+ data_element.typeRef)
   #                self.types.processType(ws, data_type)
   #                component.create_parameter(ws, port, data_element, data_type)

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
      if len(parts)==2:
         #assume format 'componentName/portName' with ComponentType role set
         port=None
         for component in self.components:
            if component.name == parts[0]:
               for port in component.requirePorts + component.providePorts:
                  if parts[1] == port.name:
                     return port
      return None
   
   def _generate_com_access(self):
      for component in self.components:
         if isinstance(component.swc, autosar.bsw.com.ComComponent):
            for port in component.requirePorts:
               for remote_port in port.connectors:
                  for data_element in remote_port.data_elements:                     
                     isPointer = True if data_element.dataType.isComplexType else False
                     proto = C.function(
                     "%s_Send_%s_%s"%(component.swc.name, remote_port.name, data_element.name),
                     'Std_ReturnType',
                     args = [C.variable('value', data_element.dataType.name, pointer=isPointer)])
                     data_element.com_access['Send'] = proto
                     component.swc.addSendInterface(proto, port, data_element)
            for port in component.providePorts:
               for data_element in port.data_elements:                     
                  isPointer = True
                  proto = C.function(
                  "%s_Receive_%s_%s"%(component.swc.name, remote_port.name, data_element.name),
                  'Std_ReturnType',
                  args = [C.variable('value', data_element.dataType.name, pointer=isPointer)])
                  data_element.com_access['Receive'] = proto
                  component.swc.addReceiveInterface(proto, port, data_element)
                  #remove from internal RTE variables
                  symbol = data_element.symbol
                  data_element.symbol = None
                  if symbol in self.data_element_map:
                     del self.data_element_map[symbol]
   
      

   # def _resolveCallPoints(self, component):
   #    if len(component.clientAPI.call):
   #       for key in component.clientAPI.call:
   #          port_func = component.clientAPI.call[key]
   #          rte_runnable = self._findServerRunnable(component, port_func)
   #          if rte_runnable is None:               
   #             port_func.func = self._createDefaultFunction(component, port_func.port, port_func.operation)
   #          else:
   #             port_func.func = rte_runnable.prototype
   # 
   # 
   # def _findServerRunnable(self, component, port_func):
   #    for component2 in self.components:
   #       if component2 is component:
   #          next
   #       for rte_runnable in component2.rte_runnables.values():
   #          if rte_runnable.isServerRunnable:
   #             if (rte_runnable.serverPortInterface is port_func.portInterface) and (rte_runnable.serverOperation is port_func.operation):
   #                 return rte_runnable
   #    return None
   # 
   # def _resolveParameters(self, component):
   #    ws = component.swc.rootWS()
   #    assert(ws is not None)
   #    for elem in component.parameters:
   #       (componentRef,portRef,dataElemRef)=elem
   #       swc=ws.find(componentRef)
   #       port=ws.find(portRef)
   #       dataElement = ws.find(dataElemRef)
   #       if dataElement is None:
   #          raise ValueError(dataElemRef)
   #       typeObj=ws.find(dataElement.typeRef)
   #       if typeObj is None:
   #          raise ValueError('invalid reference: %s'%dataElement.typeRef)
   #       self.types.processType(ws, typeObj)
   #       ftype='Calprm'
   #       if self.mode == 'single':
   #          fname='%s_%s_%s_%s_%s'%(self.prefix, ftype, swc_name, port.name, dataElement.name)
   #       elif self.mode == 'full':
   #          fname='%s_%s_%s_%s'%(self.prefix, ftype, port.name, dataElement.name)
   #       else:
   #          raise ValueError('invalid mode value. Valid modes are "full" and "single"')
   #       shortname='Rte_%s_%s_%s'%(ftype, port.name, dataElement.name)
   #       func=C.function(fname, typeObj.name)
   #       if shortname in component.clientAPI.__dict__[ftype.lower()]:
   #          raise ValueError('error: %s already defined'%shortname)
   #       component.clientAPI.__dict__[ftype.lower()][shortname] = CalPrmPortFunction(shortname, func)