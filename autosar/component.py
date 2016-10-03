from autosar.element import Element
import autosar.portinterface
import autosar.constant
import copy

class ComponentType(Element):
   
   def __init__(self,name,parent=None):
      super().__init__(name,parent)      
      self.requirePorts=[]
      self.providePorts=[]
      self.behavior=None
      self.implementation=None
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'requirePorts':[],'providePorts':[]}
      for port in self.requirePorts:
         data['requirePorts'].append(port.asdict())
      for port in self.providePorts:
         data['providePorts'].append(port.asdict())
      if len(data['requirePorts'])==0: del data['requirePorts']
      if len(data['providePorts'])==0: del data['providePorts']
      return data
   
   def find(self,ref):
      ref=ref.partition('/')      
      for port in self.requirePorts:
         if port.name == ref[0]:
            return port
      for port in self.providePorts:
         if port.name == ref[0]:
            return port
      return None
   
   def append(self, elem):
      if isinstance(elem,RequirePort):
         self.requirePorts.append(elem)
         elem.parent=self
      elif isinstance(elem,ProvidePort):
         self.providePorts.append(elem)
         elem.parent=self
      else:
         raise ValueError("unexpected type:" + str(type(elem)))
   
   def __getitem__(self,key):
      return self.find(key)

   def createProvidePort(self,name,portInterfaceRef,elemName=None,initValueRef=None,canInvalidate=False):
      comspec={'canInvalidate':canInvalidate}
      if initValueRef is not None:
         comspec['initValueRef']=initValueRef
      if elemName is not None:
         comspec['name']=elemName
      port = ProvidePort(name,portInterfaceRef,comspec,parent=self)
      self.providePorts.append(port)

   def createRequirePort(self,name,portInterfaceRef,elemName=None,initValueRef=None,aliveTimeout=0,canInvalidate=False):
      comspec={'canInvalidate':canInvalidate,'aliveTimeout':aliveTimeout}
      if initValueRef is not None:
         comspec['initValueRef']=initValueRef
      if elemName is not None:
         comspec['name']=elemName
      port = RequirePort(name,portInterfaceRef,comspec,parent=self)
      self.requirePorts.append(port)



class ApplicationSoftwareComponent(ComponentType):
   @property
   def tag(self): return "APPLICATION-SOFTWARE-COMPONENT-TYPE"
   
   def __init__(self,name,parent=None):
      super().__init__(name,parent)

class ComplexDeviceDriverSoftwareComponent(ComponentType):
   @property
   def tag(self): return "COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE"
   
   def __init__(self,name,parent=None):
      super().__init__(name,parent)

class Port(object):
   def __init__(self,name,portInterfaceRef,parent=None):
      self.name = name      
      if portInterfaceRef is not None and not isinstance(portInterfaceRef,str):
         raise ValueError('portInterfaceRef needs to be of type None or str')
      self.portInterfaceRef = portInterfaceRef
      self.comspec=[] 
      self.parent=parent
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return '/%s'%self.name

   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.rootWS()
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name, 'portInterfaceRef':self.portInterfaceRef, 'attributes':[]}
      for attribute in self.attributes:
         data['attributes'].append(attribute.asdict())
      if len(data['attributes'])==0: del data['attributes']
      return data
   
   def createComSpecFromDict(self,ws,portInterfaceRef,comspec):
      assert(ws is not None)
      assert(isinstance(comspec,dict))
      portInterface=ws.find(portInterfaceRef)
      if portInterface is None:
         raise ValueError("port interface not found: "+portInterfaceRef)
      if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
         name=None
         initValueRef=None
         aliveTimeout=0
         queueLength=None
         canInvalidate=False if isinstance(self,ProvidePort) else None
         if 'name' in comspec: name=str(comspec['name'])
         if 'initValueRef' in comspec: initValueRef=str(comspec['initValueRef'])
         if 'aliveTimeout' in comspec: aliveTimeout=int(comspec['aliveTimeout'])
         if 'queueLength' in comspec: queueLength=int(comspec['queueLength'])
         if 'canInvalidate' in comspec: canInvalidate=bool(comspec['canInvalidate'])
         if name is None:
            name=portInterface.dataElements[0].name #pick the name of the first available data element in portInterface
         #verify (user-supplied) name
         dataElement=portInterface.find(name)
         if dataElement is None:
            raise ValueError("unknown element '%s' of portInterface '%s'"%(name,portInterface.name))
         #verify compatibility of initValueRef
         if initValueRef is not None:
            initValue = ws.find(initValueRef)
            if initValue is None:
               raise ValueError("invalid reference detected: '%s'"%initValueRef)
            if isinstance(initValue,autosar.constant.Constant):
               #this is a convenience implementation for the user. Actually initValueRef needs to point to the value inside the Constant
               if dataElement.typeRef != initValue.value.typeRef:
                  raise ValueError("constant value has different type from data element, expected '%s', found '%s'"%(dataElement.typeRef,initValue.value.typeRef))
               initValueRef=initValue.value.ref #correct the reference to the actual value
            elif isinstance(initValue,autosar.constant.Value):
               initValueRef=initValue.ref
            else:               
               raise ValueError("reference is not a Constant or Value object: '%s'"%initValueRef)
         self.comspec.append(DataElementComSpec(name,initValueRef,aliveTimeout,queueLength,canInvalidate))
            
      
class RequirePort(Port):
   @property
   def tag(self): return "R-PORT-PROTOTYPE"
   def __init__(self,name,portInterfaceRef=None,comspec=None,parent=None):      
      if isinstance(name,str):
         #normal constructor
         super().__init__(name,portInterfaceRef,parent)
         if comspec is not None:
            ws = autosar.getCurrentWS()
            assert(ws is not None)
            if isinstance(comspec,dict):
               self.createComSpecFromDict(ws,portInterfaceRef,comspec)               
            else:
               raise NotImplementedError("not yet supported")
      elif isinstance(name,RequirePort):
         other=name #alias
         #copy constructor
         super().__init__(other.name,other.portInterfaceRef,None)
         self.comspec=copy.deepcopy(other.comspec)
      else:
         raise NotImplementedError(type(name))

class ProvidePort(Port):
   @property
   def tag(self): return "P-PORT-PROTOTYPE"
   
   def __init__(self,name,portInterfaceRef=None,comspec=None,parent=None):
      if isinstance(name,str):
      #normal constructor      
         super().__init__(name,portInterfaceRef,parent)
         if comspec is not None:
            ws = autosar.getCurrentWS()
            assert(ws is not None)
            if isinstance(comspec,dict):
               self.createComSpecFromDict(ws,portInterfaceRef,comspec)
            else:
               raise NotImplementedError("not yet supported")
      elif isinstance(name,ProvidePort):
         other=name #alias
         #copy constructor
         super().__init__(other.name,other.portInterfaceRef,None)
         self.comspec=copy.deepcopy(other.comspec)
      else:
         raise NotImplementedError(type(name))
            

class OperationComSpec(object):
   def __init__(self,name=None,queueLength=None):
      self.name = name
      self.queueLength=None
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name}
      if self.queueLength is not None:
         data['queueLength']=self.queueLength

class DataElementComSpec(object):
   def __init__(self,name=None,initValueRef=None,aliveTimeout=None,queueLength=None,canInvalidate=None):
      self.name = name
      self.initValueRef = str(initValueRef) if initValueRef is not None else None
      self._aliveTimeout = int(aliveTimeout) if aliveTimeout is not None else None
      self._queueLength = int(queueLength) if queueLength is not None else None
      self.canInvalidate = bool(canInvalidate) if canInvalidate is not None else None

   @property
   def aliveTimeout(self):
      return self._aliveTimeout
   
   @aliveTimeout.setter
   def aliveTimeout(self,val):      
      self._aliveTimeout = int(val)

   @property
   def queueLength(self):
      return self._queueLength
   
   @queueLength.setter
   def queueLength(self,val):      
      self._queueLength = int(val)
      
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name}
      if self.initValueRef is not None: data['initValueRef']=self.initValueRef
      if self.aliveTimeout is not None: data['aliveTimeout']=self.aliveTimeout
      if self.queueLength is not None: data['queueLength']=self.queueLength
      if self.canInvalidate is not None: data['canInvalidate']=self.canInvalidate
      return data

class SwcImplementation(Element):
   def __init__(self,name,behaviorRef,parent=None):
      super().__init__(name,parent)
      self.behaviorRef=behaviorRef

class Composition(Element):
   @property
   def tag(self): return "COMPOSITION-TYPE"
   
   def __init__(self,name,parent=None):
      super().__init__(name,parent) 
      self.requirePorts=[]
      self.providePorts=[]
      self.components=[]
      self.assemblyConnectors=[]
      self.delegationConnectors=[]
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'requirePorts':[],'providePorts':[],'components':[],
         'assemblyConnectors':[], 'delegationConnectors':[]}
      for port in self.requirePorts:
         data['requirePorts'].append(port.asdict())
      for port in self.providePorts:
         data['providePorts'].append(port.asdict())
      for component in self.components:
         data['components'].append(component.asdict())
      for connector in self.assemblyConnectors:
         data['assemblyConnectors'].append(connector.asdict())
      for connector in self.delegationConnectors:
         data['delegationConnectors'].append(connector.asdict())
      if len(data['requirePorts'])==0: del data['requirePorts']
      if len(data['providePorts'])==0: del data['providePorts']
      if len(data['components'])==0: del data['components']
      if len(data['assemblyConnectors'])==0: del data['assemblyConnectors']
      if len(data['delegationConnectors'])==0: del data['delegationConnectors']
      return data

class ComponentPrototype:
   def __init__(self,name,typeRef,parent=None):
      self.name=name
      self.typeRef=typeRef
      self.parent=parent
   def asdict(self):
      return {'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef}
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return '/%s'%self.name




class ProviderInstanceRef:
   """
   <PROVIDER-IREF>
   """
   def __init__(self,componentRef,providePortRef):
      self.componentRef=componentRef
      self.providePortRef=providePortRef
   def asdict(self):
      return {'type': self.__class__.__name__,'componentRef':self.componentRef,'providePortRef':self.providePortRef}


class RequesterInstanceRef:
   """
   <REQUESTER-IREF>
   """
   def __init__(self,componentRef,requirePortRef):
      self.componentRef=componentRef
      self.requirePortRef=requirePortRef
   def asdict(self):
      return {'type': self.__class__.__name__,'componentRef':self.componentRef,'requirePortRef':self.requirePortRef}

class InnerPortInstanceRef:
   """
   <INNER-PORT-IREF>
   """
   def __init__(self,componentRef,portRef):
      self.componentRef=componentRef
      self.portRef=portRef
   def asdict(self):
      return {'type': self.__class__.__name__,'componentRef':self.componentRef,'portRef':self.portRef}
   
class AssemblyConnector(object):
   """
   <ASSEMBLY-CONNECTOR-PROTOTYPE>
   """
   def __init__(self,name,providerInstanceRef,requesterInstanceRef):
      assert(isinstance(providerInstanceRef,ProviderInstanceRef))
      assert(isinstance(requesterInstanceRef,RequesterInstanceRef))
      self.name=name
      self.providerInstanceRef=providerInstanceRef
      self.requesterInstanceRef=requesterInstanceRef
   def asdict(self):
      return {'type': self.__class__.__name__,'providerInstanceRef':self.providerInstanceRef.asdict(),'requesterInstanceRef':self.requesterInstanceRef.asdict()}

class DelegationConnector:
   """
   <DELEGATION-CONNECTOR-PROTOTYPE>
   """
   def __init__(self,name,innerPortInstanceRef):
      assert(isinstance(innerPortInstanceRef,InnerPortInstanceRef))
      self.name=name
      self.innerPortInstanceRef=innerPortInstanceRef
   def asdict(self):
      return {'type': self.__class__.__name__,'innerPortInstanceRef':self.innerPortInstanceRef.asdict()}


   

