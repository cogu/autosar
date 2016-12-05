import copy
import autosar.component
import autosar.portinterface
from autosar.base import splitRef,parseBoolean
from autosar.element import Element


class Event(Element):
   def __init__(self,name,startOnEventRef=None):
      super().__init__(name)
      self.startOnEventRef = startOnEventRef

class ModeSwitchEvent(Event):
   def __init__(self,name,startOnEventRef=None):
      super().__init__(name,startOnEventRef)
      self.modeInstRef=None

class TimingEvent(Event):
   def __init__(self,name,startOnEventRef=None):
      super().__init__(name,startOnEventRef)
      self.modeDependency=None
      self.period=None

class DataReceivedEvent(Event):
   def __init__(self,name,startOnEventRef=None):
      super().__init__(name,startOnEventRef)
      self.modeDependency=None
      self.dataInstanceRef=None
      self.swDataDefsProps=[]

class OperationInvokedEvent(Event):
   def __init__(self,name,startOnEventRef=None):
      super().__init__(name,startOnEventRef)
      self.modeDependency=None
      self.operationInstanceRef=None
      self.swDataDefsProps=[]
   

class ModeDependency(object):
   def __init__(self):      
      self.modeInstanceRefs=[]
   def asdict(self):
      data={'type': self.__class__.__name__,'modeInstanceRefs':[]}
      for modeInstanceRef in self.modeInstanceRefs:
         data['modeInstanceRefs'].append(modeInstanceRef.asdict())
      if len(data['modeInstanceRefs'])==0: del data['modeInstanceRefs']

#used for both DEPENDENT-ON-MODE-IREF and MODE-IREF (do they have the same complex type definition in xsd?)
class ModeInstanceRef(object):
   def __init__(self,modeDeclarationRef,modeDeclarationGroupPrototypeRef=None,requirePortPrototypeRef=None):      
      self.modeDeclarationRef=modeDeclarationRef #MODE-DECLARATION-REF
      self.modeDeclarationGroupPrototypeRef=modeDeclarationGroupPrototypeRef #MODE-DECLARATION-GROUP-PROTOTYPE-REF
      self.requirePortPrototypeRef=requirePortPrototypeRef #R-PORT-PROTOTYPE-REF
   def asdict(self):
      data={'type': self.__class__.__name__}
      for key, value in self.__dict__.items():
         data[key]=value
      return data

class PortAPIOption(object):
   def __init__(self,takeAddress,indirectAPI,portRef):
      self.takeAddress = parseBoolean(takeAddress)
      self.indirectAPI = parseBoolean(indirectAPI)
      self.portRef = portRef
   def asdict(self):
      data={'type': self.__class__.__name__,'takeAddress':self.takeAddress, 'indirectAPI':self.indirectAPI, 'portRef':self.portRef}
      return data
   
class DataReceivePoint:
   def __init__(self,portRef,dataElemRef=None,name=None,parent=None):
      self.portRef=portRef
      self.dataElemRef=dataElemRef
      self.name=name
      self.parent=parent
   
   def tag(self,version=None): return "DATA-RECEIVE-POINT"

class DataSendPoint:
   def __init__(self,portRef,dataElemRef=None,name=None,parent=None):
      self.portRef=portRef
      self.dataElemRef=dataElemRef
      self.name=name
      self.parent=parent
   
   def tag(self,version=None): return "DATA-SEND-POINT"
      
class RunnableEntity(object):
   def __init__(self,name,invokeConcurrently=False,symbol=None,parent=None):
      self.name = name
      self.invokeConcurrently = invokeConcurrently
      if symbol is None:
         self.symbol=name
      else:
         self.symbol = symbol
      self.parent=parent
      self.dataReceivePoints=[]
      self.dataSendPoints=[]
      self.syncServerCallPoints=[]
      self.canEnterExclusiveAreas=[]
   def asdict(self):
      data={'type': self.__class__.__name__,
            'name':self.name,
            'invokeConcurrently':self.invokeConcurrently,
            'symbol':self.symbol,
            'dataReceivePoints':[],
            'dataSendPoints':[]}
      for dataReceivePoint in self.dataReceivePoints:
         data['dataReceivePoints'].append(dataReceivePoint.asdict())
      for dataSendPoint in self.dataSendPoints:
         data['dataSendPoints'].append(dataSendPoint.asdict())
      if len(self.syncServerCallPoints)>0:
         data['syncServerCallPoints']=[x.asdict for x in self.syncServerCallPoints]
      if len(self.canEnterExclusiveAreas)>0:
         data['canEnterExclusiveAreas']=[x for x in self.canEnterExclusiveAreas]
      if len(data['dataReceivePoints'])==0: del data['dataReceivePoints']
      if len(data['dataSendPoints'])==0: del data['dataSendPoints']
      return data
   
   def append(self,elem):
      if isinstance(elem,DataReceivePoint):
         dataReceivePoint=self._verifyDataReceivePoint(copy.copy(elem))
         self.dataReceivePoints.append(dataReceivePoint)
         dataReceivePoint.parent=self
      if isinstance(elem,DataSendPoint):
         dataSendPoint=self._verifyDataSendPoint(copy.copy(elem))
         self.dataSendPoints.append(dataSendPoint)
         dataSendPoint.parent=self
      else:
         raise NotImplementedError(str(type(elem)))
   
   def _verifyDataReceivePoint(self,dataReceivePoint):
      ws=self.rootWS()
      assert(ws is not None)
      assert(dataReceivePoint.portRef is not None)
      if isinstance(dataReceivePoint.portRef,autosar.component.Port):
         dataReceivePoint.portRef=dataReceivePoint.portRef.ref
      if isinstance(dataReceivePoint.portRef,str):
         port=ws.find(dataReceivePoint.portRef)
         if dataReceivePoint.dataElemRef is None:
            #default rule: set dataElemRef to ref of first dataElement in the portinterface
            portInterface=ws.find(port.portInterfaceRef)
            assert(portInterface is not None)
            if isinstance(portInterface,(autosar.portinterface.SenderReceiverInterface,autosar.portinterface.ParameterInterface)):
               dataReceivePoint.dataElemRef=portInterface.dataElements[0].ref
            else:
               raise ValueError('invalid interface type:%s'%(str(type(portInterface))))
         assert(isinstance(dataReceivePoint.dataElemRef,str))
         dataElement = ws.find(dataReceivePoint.dataElemRef)
         if dataReceivePoint.name is None:
            #default rule: set the name to REC_<port.name>_<dataElement.name>
            dataReceivePoint.name="REC_{0.name}_{1.name}".format(port,dataElement)
      else:
         raise ValueError('%s: portRef must be of type string'%self.ref)
      return dataReceivePoint
   
   def _verifyDataSendPoint(self,dataSendPoint):
      ws=self.rootWS()
      assert(ws is not None)
      assert(dataSendPoint.portRef is not None)
      if isinstance(dataSendPoint.portRef,autosar.component.Port):
         dataSendPoint.portRef=dataSendPoint.portRef.ref
      if isinstance(dataSendPoint.portRef,str):
         port=ws.find(dataSendPoint.portRef)
         if dataSendPoint.dataElemRef is None:
            #default rule: set dataElemRef to ref of first dataElement in the portinterface
            portInterface=ws.find(port.portInterfaceRef)
            assert(portInterface is not None)
            if isinstance(portInterface,(autosar.portinterface.SenderReceiverInterface,autosar.portinterface.ParameterInterface)):
               dataSendPoint.dataElemRef=portInterface.dataElements[0].ref
            else:
               raise ValueError('invalid interface type:%s'%(str(type(portInterface))))
         assert(isinstance(dataSendPoint.dataElemRef,str))
         dataElement = ws.find(dataSendPoint.dataElemRef)
         if dataSendPoint.name is None:
            #default rule: set the name to SEND_<port.name>_<dataElement.name>
            dataSendPoint.name="SEND_{0.name}_{1.name}".format(port,dataElement)
      else:
         raise ValueError('%s: portRef must be of type string'%self.ref)
      return dataSendPoint   

   
   def rootWS(self):
      if self.parent is None:
         return autosar.getCurrentWS()
      else:
         return self.parent.rootWS()

   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return None

class DataElementInstanceRef(object):
   """
   <DATA-ELEMENT-IREF>
   Note: This object seems to be identical to an <DATA-IREF>
   Note 2: Observe that there are multiple <DATA-ELEMENT-IREF> definitions in the AUTOSAR XSD (used for different purposes)
   """
   def __init__(self,portRef,dataElemRef):
      self.portRef = portRef
      self.dataElemRef = dataElemRef
   def asdict(self):
      data={'type': self.__class__.__name__,'portRef':self.portRef, 'dataElemRef':self.dataElemRef}
      return data

class DataInstanceRef(object):
   """
   <DATA-IREF>
   Note: This object seems to be identical to an <DATA-ELEMENT-IREF>
   """
   def __init__(self,portRef,dataElemRef):
      self.portRef = portRef
      self.dataElemRef = dataElemRef
   def asdict(self):
      data={'type': self.__class__.__name__,'portRef':self.portRef, 'dataElemRef':self.dataElemRef}
      return data

class OperationInstanceRef(object):
   """
   <OBJECT-IREF>   
   """
   def __init__(self,portRef,operationRef):
      self.portRef = portRef
      self.operationRef = operationRef
   def asdict(self):
      data={'type': self.__class__.__name__,'portRef':self.portRef, 'operationRef':self.operationRef}
      return data


class PerInstanceMemory(object):
   """
   <PER-INSTANCE-MEMORY>
   Note: I don't know why this XML object has both <TYPE> and <TYPE-DEFINITION> where a simple TYPE-TREF should suffice.
   Internally use a typeRef for PerInstanceMemory. We can transform it back to <TYPE> and <TYPE-DEFINITION> when serializing to XML
   """
   def __init__(self,name,typeRef):
      self.name=name
      self.typeRef=typeRef
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name, 'typeRef':self.typeRef}
      return data

class SwcNvBlockNeeds(object):
   def __init__(self,name,numberOfDataSets,readOnly,reliability,resistantToChangedSW,
                writeOnlyOnce,writingFrequency,writingPriority,defaultBlockRef,
                mirrorBlockRef):
      self.name=name      
      self.numberOfDataSets=numberOfDataSets
      assert(isinstance(readOnly,bool))
      self.readOnly=readOnly
      self.reliability=reliability
      assert(isinstance(resistantToChangedSW,bool))
      self.resistantToChangedSW=resistantToChangedSW
      assert(isinstance(writeOnlyOnce,bool))
      self.writeOnlyOnce=writeOnlyOnce
      self.writingFrequency=writingFrequency
      self.writingPriority=writingPriority
      self.defaultBlockRef=defaultBlockRef
      self.mirrorBlockRef=mirrorBlockRef
      self.serviceCallPorts=[]      
   def asdict(self):
      data={'type': self.__class__.__name__,'serviceCallPorts':[]}
      for key, value in self.__dict__.items():
         if 'key'=='serviceCallPorts':
            pass
         else:
            data[key]=value
      if len(data['serviceCallPorts'])==0: del data['serviceCallPorts']
      return data

class RoleBasedRPortAssignment(object):
   def __init__(self,portRef,role):
      self.portRef=portRef
      self.role=role
   def asdict(self):
      data={'type': self.__class__.__name__}
      for key, value in self.__dict__.items():
         data[key]=value
      return data

class CalPrmElemPrototype(object):
   """
   <CALPRM-ELEMENT-PROTOTYPE>
   """
   def __init__(self,name,adminData,typeRef):
      self.name=name
      self.adminData=adminData
      self.typeRef=typeRef
      self.swDataDefsProps=[]
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef,'swDataDefsProps':[]}
      if self.adminData is not None:
         data['adminData']=self.adminData.asdict()
      for elem in self.swDataDefsProps:
         data['swDataDefsProps'].append(elem)         
      return data

class ExclusiveArea(object):
   def __init__(self,name):
      self.name=name
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name}
      return data
      
 
class SyncServerCallPoint(object):
   """
   <SYNCHRONOUS-SERVER-CALL-POINT>
   """
   def __init__(self,name,timeout=0.0):
      self.name=name
      self.timeout=timeout
      self.operationInstanceRefs=[]
   
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'timeout':self.timeout}
      data['operationInstanceRefs'] = [x.asdict() for x in self.operationInstanceRefs]
      if len(data['operationInstanceRefs'])==0: del data['operationInstanceRefs']
      return data
   
class InternalBehavior(Element):
   """ InternalBehavior class """
   def __init__(self,name,componentRef,multipleInstance=False,parent=None):
      super().__init__(name,parent)
      if not isinstance(componentRef,str): #this is a helper, in case the user called the function with obj instead of obj.ref
         if hasattr(componentRef,'ref'):
            componentRef=componentRef.ref
      if (componentRef is None) or (not isinstance(componentRef,str)):
         raise ValueError('componentRef: invalid reference')
      self.componentRef=str(componentRef)
      self.parent=parent
      self.multipleInstance = bool(multipleInstance)
      self.events = []
      self.portAPIOptions = []
      self.runnables = []
      self.perInstanceMemories = []
      self.swcNvBlockNeeds = []
      self.sharedCalPrms=[]
      self.exclusiveAreas=[]
      self.swc = None
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name, 'multipleInstance':self.multipleInstance,
            'componentRef':self.componentRef, 'events':[],'portAPIOptions':[],'runnables':[],'perInstanceMemories':[],
            'swcNvBlockNeeds':[],'sharedCalPrms':[],'exclusiveAreas':[]}
      for event in self.events:
         data['events'].append(event.asdict())
      for portAPIOption in self.portAPIOptions:
         data['portAPIOptions'].append(portAPIOption.asdict())
      for runnable in self.runnables:
         data['runnables'].append(runnable.asdict())
      for perInstanceMemory in self.perInstanceMemories:
         data['perInstanceMemories'].append(perInstanceMemory.asdict())
      for swcNvBlockNeed in self.swcNvBlockNeeds:
         data['swcNvBlockNeeds'].append(swcNvBlockNeed.asdict())
      for sharedCalPrm in self.sharedCalPrms:
         data['sharedCalPrms'].append(sharedCalPrm.asdict())
      for exclusiveArea in self.exclusiveAreas:
         data['exclusiveAreas'].append(exclusiveArea.asdict())
      if len(data['events'])==0: del data['events']
      if len(data['portAPIOptions'])==0: del data['portAPIOptions']
      if len(data['runnables'])==0: del data['runnables']
      if len(data['perInstanceMemories'])==0: del data['perInstanceMemories']
      if len(data['swcNvBlockNeeds'])==0: del data['swcNvBlockNeeds']
      if len(data['sharedCalPrms'])==0: del data['sharedCalPrms']
      if len(data['exclusiveAreas'])==0: del data['exclusiveAreas']
      return data
   
   
   def tag(self,version=None): return "INTERNAL-BEHAVIOR"

   def append(self,elem):
      if isinstance(elem,RunnableEntity):
         self.runnables.append(elem)
         elem.parent=self
      else:
         raise NotImplementedError(str(type(elem)))

   def find(self,ref):      
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref=ref.partition('/')
      name=ref[0]
      for runnable in self.runnables:
         if runnable.name == name:
            return runnable
      return None
   
   def __getitem__(self,key):
      return self.find(key)
   
   def createRunnable(self,name,invokeConcurrently=False,symbol=None, portAccess=None):
      runnable = RunnableEntity(name,invokeConcurrently,symbol,self)
      self.runnables.append(runnable)
      if portAccess is not None:
         if self.swc is None:
            ws = self.rootWS()
            assert(ws is not None)
            self.swc = ws.find(self.componentRef)
         assert(self.swc is not None)
         for elem in portAccess:
            ref = elem.partition('/')
            if len(ref[1])==0:
               port = self.swc.find(ref[0])               
               if port is None:
                  raise ValueError('invalid port reference: '+str(elem))
               portInterface = ws.find(port.portInterfaceRef)
               if portInterface is None:
                  raise ValueError('invalid portinterface reference: '+str(port.portInterfaceRef))
               if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
                  if len(portInterface.dataElements)==0:
                     continue
                  elif len(portInterface.dataElements)==1:
                     dataElem=portInterface.dataElements[0]
                     self._createSendReceivePoint(port,dataElem,runnable)
                  else:
                     raise NotImplementedError('port interfaces with multiple data elements not supported')
               else:
                  raise NotImplementedError(type(portInterface))
            else:
               port = self.swc.find(ref[0])               
               if port is None:
                  raise ValueError('invalid port reference: '+str(elem))
               portInterface = ws.find(port.portInterfaceRef)
               if portInterface is None:
                  raise ValueError('invalid portinterface reference: '+str(port.portInterfaceRef))
               if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
                  dataElem=portInterface.find(ref[2])
                  if dataElem is None:
                     raise ValueError('invalid data element reference: '+str(elem))
                  self._createSendReceivePoint(port,dataElem,runnable)
               else:
                  raise NotImplementedError(type(portInterface))

      return runnable

   def _createSendReceivePoint(self,port,dataElement,runnable):
      if isinstance(port,autosar.component.RequirePort):
         receivePoint=DataReceivePoint(port.ref,dataElement.ref,'REC_{0.name}_{1.name}'.format(port,dataElement),runnable)
         runnable.dataReceivePoints.append(receivePoint)
      elif isinstance(port,autosar.component.ProvidePort):
         sendPoint=DataSendPoint(port.ref,dataElement.ref,'SEND_{0.name}_{1.name}'.format(port,dataElement),runnable)
         runnable.dataSendPoints.append(sendPoint)
      else:
         raise ValueError('unexpected type: '+str(type(port)))
