import autosar.base
import autosar.component
import autosar.rte.base
from autosar.rte.base import (ReadPortFunction, WritePortFunction, SendPortFunction, ReceivePortFunction, CallPortFunction,
                              CalPrmPortFunction, DataElement, Operation, RequirePort, ProvidePort)
import cfile as C
import sys
import autosar.bsw.com


innerIndentDefault=3 #(number of spaces)


   

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
      self.get = {}
      self.setReadData = {}
      self.setReadResult = {}

      self.final = {
                     'read': [],
                     'write': [],
                     'receive': [],
                     'send': [],
                     'mode': [],
                     'call': [],
                     'calprm': [],
                     'modeswitch': [],
                     'get': [],           #FOR UNIT TEST PURPOSES
                     'setReadData': [],           #FOR UNIT TEST PURPOSES
                     'setReadResult': [],        #FOR UNIT TEST PURPOSES
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
      if len(self.get)>0:
         self.final['get']=[self.get[k] for k in sorted(self.get.keys())]
      if len(self.setReadData)>0:
         self.final['setReadData']=[self.setReadData[k] for k in sorted(self.setReadData.keys())]
      if len(self.setReadResult)>0:
         self.final['setReadResult']=[self.setReadResult[k] for k in sorted(self.setReadResult.keys())]

   def get_all(self):
      for func in self.final['read']:
         yield func
      for func in self.final['write']:
         yield func
      for func in self.final['receive']:
         yield func
      for func in self.final['send']:
         yield func
      for func in self.final['mode']:
         yield func
      for func in self.final['call']:
         yield func
      for func in self.final['calprm']:
         yield func
      for func in self.final['get']:
         yield func
      for func in self.final['setReadData']:
         yield func
      for func in self.final['setReadResult']:
         yield func

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
      self.inner = swc
      self.clientAPI = ComponentAPI() #function calls towards the RTE (stuff that the RTE must provide)
      self.events = []
      self.runnables = []
      self.data_vars = []
      self.rte_prefix = rte_prefix
      self.is_finalized = False
      self.requirePorts = []
      self.providePorts = []
      self.data_element_port_access = {}
      self.operation_port_access = {}
      ws = swc.rootWS()
      assert(ws is not None)
      self._process_ports(ws)
      self._process_runnables(ws)
      self._process_events(ws)
      
      

   def _process_ports(self, ws):
      for ar_port in self.inner.providePorts:
         self.providePorts.append(ProvidePort(ws, ar_port, self))
      for ar_port in self.inner.requirePorts:
         self.requirePorts.append(RequirePort(ws, ar_port, self))      
      
   # def pre_finalize(self, ws, type_manager):
   #    if not self.is_finalized:
   #       self._process_runnables(ws)
   #       self._process_events(ws)

   def finalize(self,ws, type_manager):
      if not self.is_finalized:      
         self._process_port_access()
         for port in self.requirePorts+self.providePorts:
            port.process_types(ws, type_manager)
            port.update_client_api(self.clientAPI)
         self.clientAPI.finalize()
         self._runnables_finalize()
      self.is_finalized=True

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

   def _process_runnables(self, ws):
      if self.inner.behavior is not None:
         for ar_runnable in self.inner.behavior.runnables:
            runnable = Runnable(self, ar_runnable)
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
               self.data_element_port_access['%s/%s'%(port.name, data_element.name)]=autosar.rte.base.DataElementPortAccess(port, data_element, runnable)

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
                  self.operation_port_access['%s/%s'%(port.name, operation.name)]=autosar.rte.base.OperationPortAccess(port, operation, runnable)

   def _process_events(self, ws):
      if self.inner.behavior is None:
         return
      for ar_event in self.inner.behavior.events:
         ar_runnable = ws.find(ar_event.startOnEventRef)
         if ar_runnable is None:
            raise ValueError('Invalid StartOnEvent reference: '+ar_event.startOnEventRef)
         for runnable in self.runnables:
            if runnable.inner is ar_runnable:
               break
         else:
            raise ValueError('Runnable not found')
         if isinstance(ar_event, autosar.behavior.TimingEvent):
            event = autosar.rte.base.TimerEvent(ar_event, runnable)
         elif isinstance(ar_event, autosar.behavior.ModeSwitchEvent):
            if ar_event.modeInstRef is not None:
               event = autosar.rte.base.ModeSwitchEvent(ws, ar_event, runnable)
         elif isinstance(ar_event, autosar.behavior.OperationInvokedEvent):
            port_refs = autosar.base.splitRef(ar_event.operationInstanceRef.portRef)
            operation_refs = autosar.base.splitRef(ar_event.operationInstanceRef.operationRef)
            port = self.find_provide_port(port_refs[-1])
            assert (port is not None) and (port.ar_port is ws.find(ar_event.operationInstanceRef.portRef))
            operation = port.find_operation(operation_refs[-1])
            assert (operation is not None)
            event = autosar.rte.base.OperationInvokedEvent(ar_event, runnable, port, operation)
         else:
            raise NotImplementedError(str(type(event)))
         self.events.append(event)
            
   def _process_port_access(self):
      for access in self.operation_port_access.values():
         if isinstance(access, autosar.rte.base.OperationPortAccess):
            proto = access.port.create_server_call_api(access.operation)
         else:
            raise NotImplementedError(str(type(access)))
   def _runnables_finalize(self):
      #operation_invoke_events = [event for event in self.events if isinstance(event, OperationInvokedEvent)]         
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
                     variable_name = '_'.join([self.name,provide_port.name,data_element.name])
                     if variable_name not in data_element_map:
                        data_element.symbol = variable_name
                        data_element_map[variable_name] = data_element
                        #reassign require_port data element to access the data element from the provide port
                        port_func.data_element = data_element



class Runnable:
   """RTE Runnable"""
   def __init__(self, parent, ar_runnable):
      self.parent = parent
      self.inner = ar_runnable
      self.name = ar_runnable.name
      self.symbol = ar_runnable.symbol
      self.data_element_access=[]
      self.operation_access=[]
      self.prototype = None
      self.event_triggers=[]
      self.processed=False

class Partition:

   def __init__(self, mode='full', prefix='Rte'):
      self.prefix=prefix
      self.components = [] #clients (components)
      self.upperLayerAPI = ComponentAPI() #functions that the RTE must support towards its clients
      self.lowerLayerAPI = {}
      self.types = autosar.rte.RteTypeManager() #centralized type manager
      self.isFinalized = False
      self.ws = None
      self.assemblyConnectorMap = {}
      self.data_element_map = {}
      self.mode_switch_functions = {}
      self.static_vars = {}


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
#         for component in self.components:            
#            component.pre_finalize(self.ws, self.types)
         for component in self.components:
            component.finalize(self.ws, self.types)
            self.upperLayerAPI.update(component.clientAPI)
         for component in self.components:
            component.create_data_elements(self.data_element_map)
         self._generate_com_access()
         self.upperLayerAPI.finalize()
         for component in self.components:
            self._process_mode_switch_events(component)
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

   # def _process_events(self, component, ws, swc, runnables=None):
   #    for event in swc.behavior.events:
   #       ar_runnable = ws.find(event.startOnEventRef)
   #       rte_runnable = component.get_runnable(ar_runnable.name)
   #       if isinstance(event, autosar.behavior.TimingEvent):
   #          rte_event = TimerEvent(event.name, rte_runnable)
   #          component.add_event(rte_event)
   #       elif isinstance(event, autosar.behavior.ModeSwitchEvent):
   #          if ar_runnable is None:
   #             raise ValueError('invalid reference: '+event.startOnEventRef)
   #          if runnables is None or ar_runnable.name in runnables:
   #             rte_event = ModeSwitchEvent(ws, event, rte_runnable)
   #             rte_runnable.events.append(rte_event)
   #             component.add_event(rte_event)
   #       elif isinstance(event, autosar.behavior.OperationInvokedEvent):
   #          pass #already processed
   #       else:
   #          raise NotImplementedError(type(event))

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
         if isinstance(component.inner, autosar.bsw.com.ComComponent):
            for port in component.requirePorts:
               for remote_port in port.connectors:
                  for data_element in remote_port.data_elements:
                     isPointer = True if data_element.dataType.isComplexType else False
                     proto = C.function(
                     "%s_Send_%s_%s"%(component.inner.name, remote_port.name, data_element.name),
                     'Std_ReturnType',
                     args = [C.variable('value', data_element.dataType.name, pointer=isPointer)])
                     data_element.com_access['Send'] = proto
                     component.inner.addSendInterface(proto, port, data_element)
            for port in component.providePorts:
               for data_element in port.data_elements:
                  isPointer = True
                  proto = C.function(
                  "%s_Receive_%s_%s"%(component.inner.name, remote_port.name, data_element.name),
                  'Std_ReturnType',
                  args = [C.variable('value', data_element.dataType.name, pointer=isPointer)])
                  data_element.com_access['Receive'] = proto
                  component.inner.addReceiveInterface(proto, port, data_element)
                  #remove from internal RTE variables
                  symbol = data_element.symbol
                  data_element.symbol = None
                  if symbol in self.data_element_map:
                     del self.data_element_map[symbol]
   
   def _process_mode_switch_events(self, component):      
      for event in component.events:
         if isinstance(event, autosar.rte.base.ModeSwitchEvent):
            if event.mode not in self.mode_switch_functions:
               func = autosar.rte.base.ModeSwitchFunction(event)
               self.mode_switch_functions[event.mode] = func
               if func.static_var not in self.static_vars:
                  self.static_vars[func.static_var.name] = func.static_var
            function_name = "_".join(['os', 'task', event.activationType, event.mode, event.modeDeclaration])
            if function_name not in self.mode_switch_functions[event.mode].calls:
               if (event.activationType == 'OnEntry'):
                  self.mode_switch_functions[event.mode].generate_on_entry_code(event, function_name)
               else:
                  self.mode_switch_functions[event.mode].generate_on_exit_code(event, function_name)
            else:
               self.mode_switch_functions[event.mode].add_event_to_call(event, function_name)