from autosar.element import Element
from autosar.base import parseBooleanNode,parseBoolean,parseTextNode,parseIntNode,parseFloatNode,parseAdminDataNode

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
      
class RunnableEntity(object):
   def __init__(self,name,invokeConcurrently,symbol):
      self.name = name
      self.invokeConcurrently = invokeConcurrently
      self.symbol = symbol
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
   def __init__(self,name,componentRef,multipleInstance=False,parent=None):
      super().__init__(name,parent)
      self.componentRef=componentRef
      self.multipleInstance = multipleInstance
      self.events = []
      self.portAPIOptions = []
      self.runnables = []
      self.perInstanceMemories = []
      self.swcNvBlockNeeds = []
      self.sharedCalPrms=[]
      self.exclusiveAreas=[]
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

class BehaviorParser(object):
   def __init__(self,pkg,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.pkg=pkg

   def parseInternalBehavior(self,xmlRoot,dummy,parent=None):
      xmlName = xmlRoot.find('SHORT-NAME')
      xmlComponentRef = xmlRoot.find('COMPONENT-REF')
      xmlSupportMultipleInst = xmlRoot.find('SUPPORTS-MULTIPLE-INSTANTIATION')      
      if (xmlName is not None) and (xmlComponentRef is not None):
         multipleInstance = False
         if (xmlSupportMultipleInst is not None) and (xmlSupportMultipleInst.text == 'true'):
            multipleInstance = True
         internalBehavior = InternalBehavior(xmlName.text,xmlComponentRef.text,multipleInstance)
         for xmlNode in xmlRoot.findall('./*'):
            if (xmlNode.tag == 'SHORT-NAME') or (xmlNode.tag == 'COMPONENT-REF') or (xmlNode.tag == 'SUPPORTS-MULTIPLE-INSTANTIATION'):
               continue
            if xmlNode.tag == 'EVENTS':
               for xmlEvent in xmlNode.findall('./*'):
                  event = None
                  if xmlEvent.tag == 'MODE-SWITCH-EVENT':
                     event = self.parseModeSwitchEvent(xmlEvent,parent)
                  elif xmlEvent.tag == 'TIMING-EVENT':
                     event = self.parseTimingEvent(xmlEvent,parent)
                  elif xmlEvent.tag == 'DATA-RECEIVED-EVENT':
                     event = self.parseDataReceivedEvent(xmlEvent,parent)
                  elif xmlEvent.tag == 'OPERATION-INVOKED-EVENT':
                     event = self.parseOperationInvokedEvent(xmlEvent,parent)
                  else:
                     raise NotImplementedError(xmlEvent.tag)
                  if event is not None:
                     internalBehavior.events.append(event)
                  else:
                     raise ValueError('event')
            elif xmlNode.tag == 'PORT-API-OPTIONS':
               for xmlOption in xmlNode.findall('./PORT-API-OPTION'):                  
                  portAPIOption = PortAPIOption(parseTextNode(xmlOption.find('ENABLE-TAKE-ADDRESS')),parseTextNode(xmlOption.find('INDIRECT-API')),parseTextNode(xmlOption.find('PORT-REF')))
                  if portAPIOption is not None: internalBehavior.portAPIOptions.append(portAPIOption)
            elif xmlNode.tag == 'RUNNABLES':
               for xmRunnable in xmlNode.findall('./RUNNABLE-ENTITY'):
                  xmlDataReceivePoints=None
                  xmlDataSendPoints=None
                  xmlServerCallPoints=None
                  xmlCanEnterExclusiveAreas=None
                  for xmlElem in xmRunnable.findall('*'):
                     if xmlElem.tag=='SHORT-NAME':
                        name=parseTextNode(xmlElem)
                     elif xmlElem.tag=='CAN-BE-INVOKED-CONCURRENTLY':
                        canBeInvokedConcurrently=parseBooleanNode(xmlElem)
                     elif xmlElem.tag=='DATA-RECEIVE-POINTS':
                        xmlDataReceivePoints=xmlElem
                     elif xmlElem.tag=='DATA-SEND-POINTS':
                        xmlDataSendPoints=xmlElem
                     elif xmlElem.tag=='SERVER-CALL-POINTS':
                        xmlServerCallPoints=xmlElem
                     elif xmlElem.tag=='SYMBOL':
                        symbol=parseTextNode(xmlElem)
                     elif xmlElem.tag=='CAN-ENTER-EXCLUSIVE-AREA-REFS':
                        xmlCanEnterExclusiveAreas=xmlElem
                     else:
                        raise NotImplementedError(xmlElem.tag)
                  runnableEntity = RunnableEntity(name,canBeInvokedConcurrently,symbol)                                     
                  if xmlDataReceivePoints is not None:
                     for xmlDataPoint in xmlDataReceivePoints.findall('./DATA-RECEIVE-POINT'):
                        dataElementInstanceRef = self.parseDataElementInstanceRef(xmlDataPoint.find('DATA-ELEMENT-IREF'),'R-PORT-PROTOTYPE-REF')
                        if dataElementInstanceRef is not None: runnableEntity.dataReceivePoints.append(dataElementInstanceRef)
                  if xmlDataSendPoints is not None:
                     for xmlDataPoint in xmlDataSendPoints.findall('./DATA-SEND-POINT'):
                        dataElementInstanceRef = self.parseDataElementInstanceRef(xmlDataPoint.find('DATA-ELEMENT-IREF'),'P-PORT-PROTOTYPE-REF')
                        if dataElementInstanceRef is not None: runnableEntity.dataSendPoints.append(dataElementInstanceRef)
                  if xmlServerCallPoints is not None:
                     for xmlServerCallPoint in xmlServerCallPoints.findall('./SYNCHRONOUS-SERVER-CALL-POINT'):
                        syncServerCallPoint = self.parseSyncServerCallPoint(xmlServerCallPoint,rootProject)
                        if syncServerCallPoint is not None: runnableEntity.syncServerCallPoints.append(syncServerCallPoint)
                  if xmlCanEnterExclusiveAreas is not None:
                     for xmlCanEnterExclusiveAreaRef in xmlCanEnterExclusiveAreas.findall('./CAN-ENTER-EXCLUSIVE-AREA-REF'):
                        runnableEntity.canEnterExclusiveAreas.append(parseTextNode(xmlCanEnterExclusiveAreaRef))                        
                  if runnableEntity is not None: internalBehavior.runnables.append(runnableEntity)
            elif xmlNode.tag == 'PER-INSTANCE-MEMORYS':               
               for xmlElem in xmlNode.findall('./PER-INSTANCE-MEMORY'):
                 perInstanceMemory = PerInstanceMemory(parseTextNode(xmlElem.find('SHORT-NAME')),parseTextNode(xmlElem.find('TYPE-DEFINITION')))
                 if perInstanceMemory is not None: internalBehavior.perInstanceMemories.append(perInstanceMemory)
            elif xmlNode.tag == 'SERVICE-NEEDSS':
               for xmlElem in xmlNode.findall('./*'):
                  if xmlElem.tag=='SWC-NV-BLOCK-NEEDS':
                     swcNvBlockNeeds=self.parseSwcNvBlockNeeds(xmlElem,rootProject)
                     if swcNvBlockNeeds is not None: internalBehavior.swcNvBlockNeeds.append(swcNvBlockNeeds)
                  else:
                     raise NotImplementedError(xmlElem.tag)
            elif xmlNode.tag == 'SHARED-CALPRMS':
               for xmlElem in xmlNode.findall('./*'):
                  if xmlElem.tag=='CALPRM-ELEMENT-PROTOTYPE':
                     calPrmElemPrototype=self.parseCalPrmElemPrototype(xmlElem,rootProject)
                     assert(calPrmElemPrototype is not None)
                     internalBehavior.sharedCalPrms.append(calPrmElemPrototype)
                  else:
                     raise NotImplementedError(xmlElem.tag)
            elif xmlNode.tag == 'EXCLUSIVE-AREAS':
               for xmlElem in xmlNode.findall('./*'):
                  if xmlElem.tag=='EXCLUSIVE-AREA':
                     exclusiveArea=ExclusiveArea(xmlElem.find('SHORT-NAME'))                     
                     internalBehavior.exclusiveAreas.append(exclusiveArea)
                  else:
                     raise NotImplementedError(xmlElem.tag)
            else:
               raise NotImplementedError(xmlNode.tag)   
         return internalBehavior      

   def parseModeInstanceRef(self,xmlRoot,parent=None):
      """parses <MODE-IREF>"""
      assert(xmlRoot.tag == 'MODE-IREF')
      modeDeclarationRef=parseTextNode(xmlRoot.find('MODE-DECLARATION-REF'))
      modeDeclarationGroupPrototypeRef = parseTextNode(xmlRoot.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
      requirePortPrototypeRef = parseTextNode(xmlRoot.find('R-PORT-PROTOTYPE-REF'))
      return ModeInstanceRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)

   def parseModeDependency(self,xmlRoot,parent=None):
      """parses <MODE-DEPENDENCY>"""
      assert(xmlRoot.tag == 'MODE-DEPENDENCY')
      modeDependency=ModeDependency()
      if xmlRoot.find('DEPENDENT-ON-MODE-IREFS') is not None:
         for xmlNode in xmlRoot.findall('./DEPENDENT-ON-MODE-IREFS/DEPENDENT-ON-MODE-IREF'):
            modeInstanceRef = self.parseDependentOnModeInstanceRef(xmlNode)
            if modeInstanceRef is not None:
               modeDependency.modeInstanceRefs.append(modeInstanceRef)
      return modeDependency
   

   def parseDependentOnModeInstanceRef(self,xmlRoot,parent=None):
      """parses <DEPENDENT-ON-MODE-IREF>"""
      assert(xmlRoot.tag == 'DEPENDENT-ON-MODE-IREF')      
      modeDeclarationRef=parseTextNode(xmlRoot.find('MODE-DECLARATION-REF'))
      modeDeclarationGroupPrototypeRef = parseTextNode(xmlRoot.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
      requirePortPrototypeRef = parseTextNode(xmlRoot.find('R-PORT-PROTOTYPE-REF'))
      return ModeInstanceRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)    
      
      
   def parseModeSwitchEvent(self,xmlNode,parent=None):
      """parses <MODE-SWITCH-EVENT>"""
      assert(xmlNode.tag=='MODE-SWITCH-EVENT')
      name = parseTextNode(xmlNode.find('SHORT-NAME'))      
      modeInstRef = self.parseModeInstanceRef(xmlNode.find('MODE-IREF'))
      startOnEventRef = parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
      activation = parseTextNode(xmlNode.find('ACTIVATION'))
      modeSwitchEvent=ModeSwitchEvent(name,startOnEventRef)
      modeSwitchEvent.modeInstRef=modeInstRef
      return modeSwitchEvent

   def parseTimingEvent(self,xmlNode,parent=None):
      name = parseTextNode(xmlNode.find('SHORT-NAME'))      
      startOnEventRef = parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
      period=parseTextNode(xmlNode.find('PERIOD'))      
      timingEvent=TimingEvent(name,startOnEventRef)
      xmlModeDependency = xmlNode.find('MODE-DEPENDENCY')
      if xmlModeDependency is not None:
         timingEvent.modeDependency = self.parseModeDependency(xmlModeDependency,parent)
      if period is not None:
         timingEvent.period = float(period)
      return timingEvent

   
   def parseDataReceivedEvent(self,xmlRoot,rootProject=None):
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))      
      startOnEventRef = parseTextNode(xmlRoot.find('START-ON-EVENT-REF'))
      dataInstanceRef=self.parseDataInstanceRef(xmlRoot.find('DATA-IREF'),'R-PORT-PROTOTYPE-REF')
      dataReceivedEvent=DataReceivedEvent(name,startOnEventRef)
      xmlModeDependency = xmlRoot.find('MODE-DEPENDENCY')
      if xmlModeDependency is not None:
         dataReceivedEvent.modeDependency = self.parseModeDependency(xmlModeDependency,rootProject)
      dataReceivedEvent.dataInstanceRef=dataInstanceRef
      return dataReceivedEvent

   def parseOperationInvokedEvent(self,xmlRoot,rootProject=None):
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))      
      startOnEventRef = parseTextNode(xmlRoot.find('START-ON-EVENT-REF'))
      operationInstanceRef=self.parseOperationInstanceRef(xmlRoot.find('OPERATION-IREF'),'P-PORT-PROTOTYPE-REF')
      operationInvokedEvent=OperationInvokedEvent(name,startOnEventRef)
      xmlModeDependency = xmlRoot.find('MODE-DEPENDENCY')
      if xmlModeDependency is not None:
         operationInvokedEvent.modeDependency = self.parseModeDependency(xmlModeDependency,rootProject)
      operationInvokedEvent.operationInstanceRef=operationInstanceRef
      return operationInvokedEvent

   
   def parseDataInstanceRef(self,xmlRoot,portTag,rootProject=None):
      """parses <DATA-IREF>"""
      assert(xmlRoot.tag=='DATA-IREF')
      assert(xmlRoot.find(portTag) is not None)      
      return DataInstanceRef(parseTextNode(xmlRoot.find(portTag)),parseTextNode(xmlRoot.find('DATA-ELEMENT-PROTOTYPE-REF')))

   def parseOperationInstanceRef(self,xmlRoot,portTag,rootProject=None):
      """parses <OPERATION-IREF>"""
      assert(xmlRoot.tag=='OPERATION-IREF')
      assert(xmlRoot.find(portTag) is not None)      
      return OperationInstanceRef(parseTextNode(xmlRoot.find(portTag)),parseTextNode(xmlRoot.find('OPERATION-PROTOTYPE-REF')))

   def parseDataElementInstanceRef(self,xmlRoot,portTag,rootProject=None):
      """parses <DATA-ELEMENT-IREF>"""
      assert(xmlRoot.tag=='DATA-ELEMENT-IREF')
      assert(xmlRoot.find(portTag) is not None)      
      return DataElementInstanceRef(parseTextNode(xmlRoot.find(portTag)),parseTextNode(xmlRoot.find('DATA-ELEMENT-PROTOTYPE-REF')))

   def parseSwcNvBlockNeeds(self,xmlRoot,rootProject=None):
      name=parseTextNode(xmlRoot.find('SHORT-NAME'))
      numberOfDataSets=parseIntNode(xmlRoot.find('N-DATA-SETS'))
      readonly=parseBooleanNode(xmlRoot.find('READONLY'))
      reliability=parseTextNode(xmlRoot.find('RELIABILITY'))
      resistantToChangedSW=parseBooleanNode(xmlRoot.find('RESISTANT-TO-CHANGED-SW'))
      restoreAtStart=parseBooleanNode(xmlRoot.find('RESTORE-AT-START'))
      writeOnlyOnce=parseBooleanNode(xmlRoot.find('WRITE-ONLY-ONCE'))
      writingFrequency=parseIntNode(xmlRoot.find('WRITING-FREQUENCY'))
      defaultBlockRef=parseTextNode(xmlRoot.find('DEFAULT-BLOCK-REF'))
      mirrorBlockref=parseTextNode(xmlRoot.find('MIRROR-BLOCK-REF'))      
      serviceCallPorts=self.parseServiceCallPorts(xmlRoot.find('SERVICE-CALL-PORTS'),rootProject)
      assert(len(serviceCallPorts)>0)
      swcNvBlockNeeds=SwcNvBlockNeeds(name,numberOfDataSets,readonly,reliability,resistantToChangedSW,restoreAtStart,
                                      writeOnlyOnce,writingFrequency,defaultBlockRef,mirrorBlockref)
      swcNvBlockNeeds.serviceCallPorts=serviceCallPorts
      return swcNvBlockNeeds

   def parseServiceCallPorts(self,xmlRoot,rootProjet=None):
      """parses <SERVICE-CALL-PORTS>"""
      assert(xmlRoot.tag=='SERVICE-CALL-PORTS')
      serviceCallPorts=[]
      for xmlNode in xmlRoot.findall('ROLE-BASED-R-PORT-ASSIGNMENT'):
         roleBasedRPortAssignment=RoleBasedRPortAssignment(parseTextNode(xmlNode.find('R-PORT-PROTOTYPE-REF')),parseTextNode(xmlNode.find('ROLE')))         
         serviceCallPorts.append(roleBasedRPortAssignment)
      return serviceCallPorts
   
   def parseCalPrmElemPrototype(self, xmlRoot,rootProjet=None):
      """
      parses <CALPRM-ELEMENT-PROTOTYPE>
      """
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))
      adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
      typeRef = parseTextNode(xmlRoot.find('TYPE-TREF'))
      calPrmElemPrototype = CalPrmElemPrototype(name,adminData,typeRef)
      for xmlElem in xmlRoot.findall('./SW-DATA-DEF-PROPS/*'):
         if xmlElem.tag=='SW-ADDR-METHOD-REF':
            calPrmElemPrototype.swDataDefsProps.append({'type':'SwAddrMethodRef','value':parseTextNode(xmlElem)})
         else:
            raise NotImplementedError(xmlElem.tag)
      return calPrmElemPrototype
   
   def parseSyncServerCallPoint(self, xmlRoot,rootProjet=None):
      """
      parses <SYNCHRONOUS-SERVER-CALL-POINT>
      """
      assert(xmlRoot.tag=='SYNCHRONOUS-SERVER-CALL-POINT')
      for xmlElem in xmlRoot.findall('*'):
         if xmlElem.tag=='SHORT-NAME':
            name=parseTextNode(xmlElem)            
         elif xmlElem.tag=='OPERATION-IREFS':
            operationInstanceRefs=[]
            for xmlOperation in xmlElem.findall('*'):
               if xmlOperation.tag=='OPERATION-IREF':
                  operationInstanceRefs.append(self.parseOperationInstanceRef(xmlOperation,'R-PORT-PROTOTYPE-REF',rootProjet))
               else:
                  raise NotImplementedError(xmlElem.tag)
         elif xmlElem.tag=='TIMEOUT':
            timeout=parseFloatNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      retval=SyncServerCallPoint(name,timeout)
      retval.operationInstanceRefs=operationInstanceRefs
      return retval


