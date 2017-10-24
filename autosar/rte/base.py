import autosar.datatype
import copy
import cfile as C

#PortInstance = namedtuple('PortRef', 'component port')
#PortConnector = namedtuple('PortConnector', 'provide require')

innerIndentDefault = 3

def type2arg(typeObj, pointer=False, name='data'):
   return C.variable(name,typeObj.name,pointer=pointer)


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
         if port_interface.modeGroups is not None:
            for group in port_interface.modeGroups:
               data_type=ws.find(group.typeRef)
               if data_type is None:
                  raise ValueError('Error: Invalid data type reference: %s'%group.typeRef)
               self.mode_groups.append(ModeGroup(group.name, self, data_type))
               
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
         for argument in operation.inner.arguments:
            data_type = ws.find(argument.typeRef)
            if data_type is None:
               raise ValueError('Invalid Type Reference: '+argument.typeRef)
            type_manager.processType(ws, data_type)
      for group in self.mode_groups:
         type_manager.processType(ws,  group.data_type)
      

   def update_client_api(self, api):
      for port_func in self.portAPI.values():
         if isinstance(port_func, ReadPortFunction):
            api.read[port_func.proto.name]=port_func
         elif isinstance(port_func, WritePortFunction):
            api.write[port_func.proto.name]=port_func
         elif isinstance(port_func, SendPortFunction):
            api.send[port_func.proto.name]=port_func
         elif isinstance(port_func, ReceivePortFunction):
            api.receive[port_func.proto.name]=port_func
         elif isinstance(port_func, CallPortFunction):
            api.call[port_func.proto.name]=port_func
         elif isinstance(port_func, CalPrmPortFunction):
            api.calprm[port_func.proto.name]=port_func
         else:
            raise NotImplementedError(type(port_func))

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
      fname='_'.join([self.parent.rte_prefix, call_type, self.parent.name, self.name, rte_data_element.name])
      shortname='_'.join([self.parent.rte_prefix, call_type, self.name, rte_data_element.name])
      type_arg=type2arg(data_type,pointer)
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
      fname='_'.join([self.parent.rte_prefix, call_type, self.parent.name, self.name, rte_data_element.name])
      shortname='_'.join([self.parent.rte_prefix, call_type, self.name, rte_data_element.name])
      data_type = rte_data_element.dataType
      type_arg=type2arg(data_type,pointer)
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

   def create_server_call_api(self, operation):      
      shortname='_'.join([self.parent.rte_prefix, 'Call', self.name, operation.name])
      if len(self.connectors)==0:
         func_name='_'.join([self.parent.rte_prefix, 'Call', self.parent.name, self.name, operation.name])
      elif len(self.connectors)==1:         
         server_port = self.connectors[0]
         for event in server_port.parent.events:
            if isinstance(event, OperationInvokedEvent) and (event.operation.name == operation.name):
               func_name=event.runnable.name
               break
         else:
            raise ValueError('No event found to service operation %s/%s'%(self.parent.name, self.name))
      else:
         raise ValueError('Error: Operation %s/%s seems to have multiple servers'%(self.parent.name, self.name))
      return_type = 'Std_ReturnType' if len(operation.inner.errorRefs)>0 else 'void'
      proto = C.function(func_name, return_type)
      for argument in operation.arguments:
         proto.add_arg(argument)
      port_func = CallPortFunction(shortname, proto, operation)
      self.portAPI[shortname] = port_func
      return port_func


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
   def __init__(self, shortname, proto):
      self.shortname = shortname
      self.proto = proto

class ReadPortFunction(PortFunction):
   """port function for Rte_Read actions"""
   def __init__(self, shortname, proto, data_element):
      super().__init__(shortname, proto)
      self.data_element = data_element

class WritePortFunction(PortFunction):
   """port function for Rte_Write actions"""
   def __init__(self, shortname, proto, data_element):
      super().__init__(shortname, proto)
      self.data_element = data_element

class SendPortFunction(PortFunction):
   """port function for Rte_Read actions"""
   def __init__(self, shortname, proto, data_element):
      super().__init__(shortname, proto)
      self.data_element = data_element

class ReceivePortFunction(PortFunction):
   """port function for Rte_Write actions"""
   def __init__(self, shortname, proto, data_element):
      super().__init__(shortname, proto)
      self.data_element = data_element

class CallPortFunction(PortFunction):
   """port function for Rte_Call actions"""
   def __init__(self, shortname, proto, operation):
      super().__init__(shortname, proto)
      self.operation = operation

class CalPrmPortFunction(PortFunction):
   """port function for Rte_Call actions"""
   def __init__(self, shortname, proto):
      super().__init__(shortname, proto)

class GetPortFunction(PortFunction):
   """MockRte getter function"""
   def __init__(self, shortname, proto, data_element):
      super().__init__(shortname, proto)
      self.data_element = data_element

class SetReadDataFunction:
   """
   MockRte setter function
   """
   def __init__(self, prefix, component, port, data_element, var_name):
      data_type = data_element.dataType
      func_name='%s_SetReadData_%s_%s_%s'%(prefix, component.name, port.name, data_element.name)
      shortname='%s_SetReadData_%s_%s'%(prefix, port.name, data_element.name)
      proto=C.function(func_name, 'void')
      proto.add_arg(C.variable('data', data_type.name, pointer=data_type.isComplexType))
      self.shortname = shortname
      self.data_element = data_element
      self.proto=proto
      body = C.block(innerIndent=innerIndentDefault)
      if isinstance(data_type, autosar.datatype.ArrayDataType):               
         body.append(C.statement('memcpy(&%s[0], %s, sizeof(%s)'%(var_name, proto.args[0].name, var_name)))
      elif isinstance(data_type, autosar.datatype.RecordDataType):               
         body.append(C.statement('memcpy(&%s, %s, sizeof(%s)'%(var_name, proto.args[0].name, var_name)))
      else:
         body.append(C.statement('%s = %s'%(var_name, proto.args[0].name)))
      self.body=body

class SetReadResultFunction:
   """MockRte rteval function"""
   def __init__(self, prefix, component, port, data_element):
      func_name='%s_SetReadResult_%s_%s_%s'%(prefix, component.name, port.name, data_element.name)
      shortname='%s_SetReadResult_%s_%s'%(prefix, port.name, data_element.name)
      proto=C.function(func_name, 'void')
      
      proto.add_arg(C.variable('value', 'Std_ReturnType'))
      self.shortname = shortname
      self.proto=proto
      self.data_element = data_element
      data_element.result_var = C.variable('m_ReadResult_%s_%s_%s'%(component.name, port.name, data_element.name), 'Std_ReturnType', static=True)
      self.static_var = data_element.result_var
      body = C.block(innerIndent=innerIndentDefault)
      body.append(C.statement('%s = %s'%(self.static_var.name, proto.args[0].name)))
      self.body=body
      
      
class SetCallHandlerFunction(PortFunction):
   def __init__(self, shortname, proto, operation, varname):
      super().__init__(shortname, proto)
      self.operation = operation
      self.varname = varname
      self.body = self._create_body(proto)

   def _create_body(self, proto):
      body = C.block(innerIndent=3)
      body.append(C.statement('%s = %s'%(self.varname, proto.args[0].name)))
      return body

class ServerCallFunction(PortFunction):
   def __init__(self, proto, body):
      super().__init__(proto.name, proto)
      self.body=body

class DataElement:
   """
   RTE wrapper around an autosar.portinterface.DataElement
   """
   def __init__(self, name, parent, dataType, initValue = None, isQueued=False, queueLength=None):
      self.symbol = None
      self.result_var = None
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
   def __init__(self, name, parent, arguments, inner):
      self.name = name
      self.parent=parent
      self.arguments = arguments
      self.inner = inner

class DataElementFunction:
   def __init__(self, proto, port, data_element):
      self.proto = proto
      self.port = port
      self.data_element = data_element
      self.body = None

class DataElementPortAccess:
   def __init__(self, port, data_element, runnable):
      self.port = port
      self.data_element = data_element
      self.runnable = runnable

class OperationPortAccess:
   def __init__(self, port, operation, runnable):
      self.port = port
      self.operation = operation
      self.runnable = runnable
      self.func = None

class Event:
   """Event Base Class"""
   def __init__(self, ar_event, runnable):
      self.inner = ar_event
      self.name = ar_event.name
      self.runnable = runnable
      self.symbol = None

class TimerEvent(Event):
   """Runnable triggered by timer"""
   def __init__(self, ar_event, runnable):
      super().__init__(ar_event, runnable)

class OperationInvokedEvent(Event):
   """triggered by server invocation"""
   def __init__(self, ar_event, runnable, port, operation):
      super().__init__(ar_event, runnable)
      self.port = port
      self.operation = operation      
      return_type = 'Std_ReturnType' if len(operation.inner.errorRefs)>0 else 'void'
      self.runnable.prototype=C.function(runnable.symbol, return_type, args=operation.arguments)

class ModeSwitchEvent(Event):
   """
   Runnable triggered by mode switch event
   """
   def __init__(self, ws, ar_event, runnable):
      super().__init__(ar_event, runnable)
      modeDeclaration = ws.find(ar_event.modeInstRef.modeDeclarationRef)
      if modeDeclaration is None:
         raise ValueError("Error: invalid reference: %s"+ar_event.modeInstRef.modeDeclarationRef)
      mode = modeDeclaration.parent
      self.activationType = 'OnEntry' if (ar_event.activationType == 'ON-ENTRY' or ar_event.activationType == 'ENTRY')  else 'OnExit'
      self.name = "%s_%s_%s"%(self.activationType, mode.name, modeDeclaration.name)
      self.mode=mode.name
      self.modeDeclaration=modeDeclaration.name

class ModeGroup:
   """
   RTE wrapper around an autosar.portinterface.ModeGroup
   """
   def __init__(self, name, parent, dataType):
      self.name = name
      self.parent = parent
      self.data_type = dataType

class ModeSwitchFunction:
   def __init__(self, event):      
      self.body = C.block(innerIndent = innerIndentDefault)
      self.calls = {}
      self.typename = 'Rte_ModeType_'+event.mode
      self.proto = C.function('Rte_SetMode_'+event.mode, 'void', args = [C.variable('newMode', self.typename)])
      self.static_var = C.variable('m_'+event.mode, self.typename, static=True)
      self._init_body(event)
   
   def _init_body(self, event):
      self.body.append(C.statement('%s %s = %s'%(self.typename, 'previousMode', self.static_var.name)))
      self.body.append(C.statement('%s = %s'%(self.static_var.name, self.proto.args[0].name)))

   
   def generate_on_entry_code(self, event, callback_name):
      code = C.sequence()
      else_str = 'else ' if len(self.calls) > 0 else ''
      code.append(C.line(else_str+'if ( (previousMode != RTE_MODE_{0}) && (newMode == RTE_MODE_{0}) )'.format(event.mode+'_'+event.modeDeclaration)))
      block = C.block(innerIndent = innerIndentDefault)
      block.append(C.statement(C.fcall(callback_name)))
      code.append(block)
      self.add_event_to_call(event, callback_name)
      self.body.extend(code)

   def generate_on_exit_code(self, event, callback_name):
      code = C.sequence()
      else_str = 'else ' if len(self.calls) > 0 else ''
      code.append(C.line(else_str+'if ( (previousMode == RTE_MODE_{0}) && (newMode != RTE_MODE_{0}) )'.format(event.mode+'_'+event.modeDeclaration)))
      block = C.block(innerIndent = innerIndentDefault)
      block.append(C.statement(C.fcall(callback_name)))
      code.append(block)
      self.add_event_to_call(event, callback_name)
      self.body.extend(code)

   def add_event_to_call(self, event, callback_name):
      if callback_name not in self.calls:
         self.calls[callback_name]=[]
      self.calls[callback_name].append(event)