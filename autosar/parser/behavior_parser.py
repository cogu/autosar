from autosar.base import parseBooleanNode,parseBoolean,parseTextNode,parseIntNode,parseFloatNode,parseAdminDataNode
from autosar.behavior import *
from autosar.parser.parser_base import ElementParser

class BehaviorParser(ElementParser):
   def __init__(self,version=3.0):
      self.version=version

   def getSupportedTags(self):
      if (self.version >=3.0) and (self.version < 4.0):
         return ['INTERNAL-BEHAVIOR']
      elif self.version >= 4.0:
         return ['SWC-INTERNAL-BEHAVIOR']
      else:
         return []

   def parseElement(self, xmlElement, parent = None):
      if (self.version >=3.0) and (self.version < 4.0) and xmlElement.tag == 'INTERNAL-BEHAVIOR':
         return self.parseInternalBehavior(xmlElement, parent)
      elif (self.version >= 4.0) and (xmlElement.tag == 'SWC-INTERNAL-BEHAVIOR'):
         return self.parseSWCInternalBehavior(xmlElement, parent)
      else:
         return None

   def parseInternalBehavior(self,xmlRoot,parent):
      """AUTOSAR 3 Internal Behavior"""
      assert(xmlRoot.tag == 'INTERNAL-BEHAVIOR')
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))
      componentRef = parseTextNode(xmlRoot.find('COMPONENT-REF'))
      multipleInstance = False
      xmlSupportMultipleInst = xmlRoot.find('SUPPORTS-MULTIPLE-INSTANTIATION')
      if (xmlSupportMultipleInst is not None) and (xmlSupportMultipleInst.text == 'true'):
         multipleInstance = True
      ws = parent.rootWS()
      assert(ws is not None)
      if (name is not None) and (componentRef is not None):
         internalBehavior = InternalBehavior(name, componentRef, multipleInstance, parent)
         swc = ws.find(componentRef)
         if swc is not None:
            swc.behavior=internalBehavior
         for xmlNode in xmlRoot.findall('./*'):
            if (xmlNode.tag == 'SHORT-NAME') or (xmlNode.tag == 'COMPONENT-REF') or (xmlNode.tag == 'SUPPORTS-MULTIPLE-INSTANTIATION'):
               continue
            if xmlNode.tag == 'EVENTS':
               for xmlEvent in xmlNode.findall('./*'):
                  event = None
                  if xmlEvent.tag == 'MODE-SWITCH-EVENT':
                     event = self.parseModeSwitchEvent(xmlEvent,internalBehavior)
                  elif xmlEvent.tag == 'TIMING-EVENT':
                     event = self.parseTimingEvent(xmlEvent,internalBehavior)
                  elif xmlEvent.tag == 'DATA-RECEIVED-EVENT':
                     event = self.parseDataReceivedEvent(xmlEvent,internalBehavior)
                  elif xmlEvent.tag == 'OPERATION-INVOKED-EVENT':
                     event = self.parseOperationInvokedEvent(xmlEvent,internalBehavior)
                  else:
                     raise NotImplementedError(xmlEvent.tag)
                  if event is not None:
                     internalBehavior.events.append(event)
                  else:
                     raise ValueError('event')
            elif xmlNode.tag == 'PORT-API-OPTIONS':
               for xmlOption in xmlNode.findall('./PORT-API-OPTION'):
                  portAPIOption = PortAPIOption(parseTextNode(xmlOption.find('PORT-REF')),parseBooleanNode(xmlOption.find('ENABLE-TAKE-ADDRESS')),parseBooleanNode(xmlOption.find('INDIRECT-API')))
                  if portAPIOption is not None: internalBehavior.portAPIOptions.append(portAPIOption)
            elif xmlNode.tag == 'RUNNABLES':
               for xmRunnable in xmlNode.findall('./RUNNABLE-ENTITY'):
                  runnableEntity = self.parseRunnableEntity(xmRunnable, internalBehavior)
                  if runnableEntity is not None:
                     internalBehavior.runnables.append(runnableEntity)
            elif xmlNode.tag == 'PER-INSTANCE-MEMORYS':
               for xmlElem in xmlNode.findall('./PER-INSTANCE-MEMORY'):
                 perInstanceMemory = PerInstanceMemory(parseTextNode(xmlElem.find('SHORT-NAME')),parseTextNode(xmlElem.find('TYPE-DEFINITION')), internalBehavior)
                 if perInstanceMemory is not None: internalBehavior.perInstanceMemories.append(perInstanceMemory)
            elif xmlNode.tag == 'SERVICE-NEEDSS':
               for xmlElem in xmlNode.findall('./*'):
                  if xmlElem.tag=='SWC-NV-BLOCK-NEEDS':
                     swcNvBlockNeeds=self.parseSwcNvBlockNeeds(xmlElem)
                     if swcNvBlockNeeds is not None: internalBehavior.swcNvBlockNeeds.append(swcNvBlockNeeds)
                  else:
                     raise NotImplementedError(xmlElem.tag)
            elif xmlNode.tag == 'SHARED-CALPRMS':
               for xmlElem in xmlNode.findall('./*'):
                  if xmlElem.tag=='CALPRM-ELEMENT-PROTOTYPE':
                     calPrmElemPrototype=self.parseCalPrmElemPrototype(xmlElem, internalBehavior)
                     assert(calPrmElemPrototype is not None)
                     internalBehavior.sharedCalParams.append(calPrmElemPrototype)
                  else:
                     raise NotImplementedError(xmlElem.tag)
            elif xmlNode.tag == 'EXCLUSIVE-AREAS':
               for xmlElem in xmlNode.findall('./*'):
                  if xmlElem.tag=='EXCLUSIVE-AREA':
                     exclusiveArea=ExclusiveArea(parseTextNode(xmlElem.find('SHORT-NAME')), internalBehavior)
                     internalBehavior.exclusiveAreas.append(exclusiveArea)
                  else:
                     raise NotImplementedError(xmlElem.tag)
            else:
               raise NotImplementedError(xmlNode.tag)
         return internalBehavior

   def parseSWCInternalBehavior(self, xmlRoot, parent):
      """AUTOSAR 4 internal behavior"""
      assert(xmlRoot.tag == 'SWC-INTERNAL-BEHAVIOR')
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))
      multipleInstance = False
      xmlSupportMultipleInst = xmlRoot.find('SUPPORTS-MULTIPLE-INSTANTIATION')
      if xmlSupportMultipleInst is not None:
         multipleInstance = self.parseBooleanNode(xmlSupportMultipleInst)
         assert(multipleInstance is not None)
      ws = parent.rootWS()
      assert(ws is not None)
      if (name is not None):
         handledXML = ['SHORT-NAME', 'SUPPORTS-MULTIPLE-INSTANTIATION']
         internalBehavior = SwcInternalBehavior(name, parent.ref, multipleInstance, parent)
         for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag in handledXML:
               pass
            elif xmlElem.tag == 'DATA-TYPE-MAPPING-REFS':
               for xmlChild in xmlElem.findall('./*'):
                  if xmlChild.tag == 'DATA-TYPE-MAPPING-REF':
                     tmp = self.parseTextNode(xmlChild)
                     assert(tmp is not None)
                     internalBehavior.dataTypeMappingRefs.append(tmp)
            elif xmlElem.tag == 'EVENTS':
                  for xmlEvent in xmlElem.findall('./*'):
                     event = None
                     if xmlEvent.tag == 'INIT-EVENT':
                        event = self.parseInitEvent(xmlEvent,internalBehavior)
                     elif xmlEvent.tag == 'SWC-MODE-SWITCH-EVENT':
                        event = self.parseModeSwitchEvent(xmlEvent,internalBehavior)
                     elif xmlEvent.tag == 'TIMING-EVENT':
                        event = self.parseTimingEvent(xmlEvent,internalBehavior)
                     elif xmlEvent.tag == 'DATA-RECEIVED-EVENT':
                        event = self.parseDataReceivedEvent(xmlEvent,internalBehavior)
                     elif xmlEvent.tag == 'OPERATION-INVOKED-EVENT':
                        event = self.parseOperationInvokedEvent(xmlEvent,internalBehavior)
                     else:
                        raise NotImplementedError(xmlEvent.tag)
                     if event is not None:
                        internalBehavior.events.append(event)
                     else:
                        raise NotImplementedError(xmlEvent.tag)
            elif xmlElem.tag == 'PORT-API-OPTIONS':
               for xmlOption in xmlElem.findall('./PORT-API-OPTION'):
                  portAPIOption = PortAPIOption(parseTextNode(xmlOption.find('PORT-REF')),parseBooleanNode(xmlOption.find('ENABLE-TAKE-ADDRESS')),parseBooleanNode(xmlOption.find('INDIRECT-API')))
                  if portAPIOption is not None: internalBehavior.portAPIOptions.append(portAPIOption)
            elif xmlElem.tag == 'RUNNABLES':
               for xmRunnable in xmlElem.findall('./RUNNABLE-ENTITY'):
                  runnableEntity = self.parseRunnableEntity(xmRunnable, internalBehavior)
                  if runnableEntity is not None:
                     internalBehavior.runnables.append(runnableEntity)
            elif xmlElem.tag == 'AR-TYPED-PER-INSTANCE-MEMORYS':
               for xmlChild in xmlElem.findall('./*'):
                  if xmlChild.tag == 'VARIABLE-DATA-PROTOTYPE':
                     dataElement = self.parseVariableDataPrototype(xmlChild, internalBehavior)
                     internalBehavior.perInstanceMemories.append(dataElement)
                  else:
                     raise NotImplementedError(xmlChild.tag)
            elif xmlElem.tag == 'SERVICE-DEPENDENCYS':
               for xmlChildElem in xmlElem.findall('./*'):
                  if xmlChildElem.tag == 'SWC-SERVICE-DEPENDENCY':
                     swcServiceDependency = self.parseSwcServiceDependency(xmlChildElem, internalBehavior)
                     internalBehavior.serviceDependencies.append(swcServiceDependency)
                  else:
                     raise NotImplementedError(childElem.tag)
            elif xmlElem.tag == 'SHARED-PARAMETERS':
               for xmlChildElem in xmlElem.findall('./*'):
                  if xmlChildElem.tag == 'PARAMETER-DATA-PROTOTYPE':
                     tmp = self.parseParameterDataPrototype(xmlChildElem, internalBehavior)
                     if tmp is not None:
                        internalBehavior.parameterDataPrototype.append(tmp)                     
                  else:
                     raise NotImplementedError(childElem.tag)
            elif xmlElem.tag == 'EXCLUSIVE-AREAS':
               for xmlChild in xmlElem.findall('./*'):
                  if xmlChild.tag=='EXCLUSIVE-AREA':
                     exclusiveArea=ExclusiveArea(parseTextNode(xmlChild.find('SHORT-NAME')), internalBehavior)
                     internalBehavior.exclusiveAreas.append(exclusiveArea)
                  else:
                     raise NotImplementedError(xmlChild.tag)
            else:
               raise NotImplementedError(xmlElem.tag)
         return internalBehavior

   def parseRunnableEntity(self, xmlRoot, parent):
      xmlDataReceivePoints=None
      xmlDataSendPoints=None
      xmlServerCallPoints=None
      xmlCanEnterExclusiveAreas=None
      adminData = None
      xmlModeAccessPoints = None
      xmlParameterAccessPoints = None
      if self.version < 4.0:
         for xmlElem in xmlRoot.findall('*'):
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
            elif xmlElem.tag=='ADMIN-DATA':
               adminData=parseAdminDataNode(xmlElem)
            else:
               raise NotImplementedError(xmlElem.tag)
      else:
         for xmlElem in xmlRoot.findall('*'):
            if xmlElem.tag=='SHORT-NAME':
               name=parseTextNode(xmlElem)
            elif xmlElem.tag=='CAN-BE-INVOKED-CONCURRENTLY':
               canBeInvokedConcurrently=parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'MODE-ACCESS-POINTS':
               xmlModeAccessPoints = xmlElem
            elif xmlElem.tag=='DATA-RECEIVE-POINT-BY-ARGUMENTS':
               xmlDataReceivePoints=xmlElem
            elif xmlElem.tag=='DATA-SEND-POINTS':
               xmlDataSendPoints=xmlElem
            elif xmlElem.tag=='SERVER-CALL-POINTS':
               xmlServerCallPoints=xmlElem
            elif xmlElem.tag=='SYMBOL':
               symbol=parseTextNode(xmlElem)
            elif xmlElem.tag=='CAN-ENTER-EXCLUSIVE-AREA-REFS':
               xmlCanEnterExclusiveAreas=xmlElem               
            elif xmlElem.tag == 'MINIMUM-START-INTERVAL':
               pass #not implemented
            elif xmlElem.tag =='ADMIN-DATA':
               adminData=parseAdminDataNode(xmlElem)
            elif xmlElem.tag == 'PARAMETER-ACCESSS':
               xmlParameterAccessPoints = xmlElem
            else:
               raise NotImplementedError(xmlElem.tag)
      runnableEntity = RunnableEntity(name, canBeInvokedConcurrently, symbol, parent)
      if xmlDataReceivePoints is not None:
         if self.version < 4.0:
            for xmlDataPoint in xmlDataReceivePoints.findall('./DATA-RECEIVE-POINT'):
               name=parseTextNode(xmlDataPoint.find('SHORT-NAME'))
               dataElementInstanceRef = self.parseDataElementInstanceRef(xmlDataPoint.find('DATA-ELEMENT-IREF'),'R-PORT-PROTOTYPE-REF')
               if dataElementInstanceRef is not None:
                  dataReceivePoint=DataReceivePoint(dataElementInstanceRef.portRef,dataElementInstanceRef.dataElemRef,name)
                  runnableEntity.append(dataReceivePoint)
         else:
            for xmlVariableAcess in xmlDataReceivePoints.findall('VARIABLE-ACCESS'):
               name=parseTextNode(xmlVariableAcess.find('SHORT-NAME'))
               accessedVariable = self.parseAccessedVariable(xmlVariableAcess.find('./ACCESSED-VARIABLE'))
               assert(accessedVariable is not None)
               dataReceivePoint=DataReceivePoint(accessedVariable.portPrototypeRef,accessedVariable.targetDataPrototypeRef,name)
               runnableEntity.append(dataReceivePoint)
      if xmlDataSendPoints is not None:
         if self.version < 4.0:
            for xmlDataPoint in xmlDataSendPoints.findall('./DATA-SEND-POINT'):
               name=parseTextNode(xmlDataPoint.find('SHORT-NAME'))
               dataElementInstanceRef = self.parseDataElementInstanceRef(xmlDataPoint.find('DATA-ELEMENT-IREF'),'P-PORT-PROTOTYPE-REF')
               if dataElementInstanceRef is not None:
                  dataSendPoint=DataSendPoint(dataElementInstanceRef.portRef,dataElementInstanceRef.dataElemRef,name)
                  runnableEntity.append(dataSendPoint)
         else:
            for xmlVariableAcess in xmlDataSendPoints.findall('VARIABLE-ACCESS'):
               name=parseTextNode(xmlVariableAcess.find('SHORT-NAME'))
               accessedVariable = self.parseAccessedVariable(xmlVariableAcess.find('./ACCESSED-VARIABLE'))
               assert(accessedVariable is not None)
               dataSendPoint=DataSendPoint(accessedVariable.portPrototypeRef,accessedVariable.targetDataPrototypeRef,name)
               runnableEntity.append(dataSendPoint)
      if xmlModeAccessPoints is not None:
         for xmlElem in xmlModeAccessPoints.findall('./*'):
            if xmlElem.tag == 'MODE-ACCESS-POINT':
               modeAccessPoint = self.parseModeAccessPoint(xmlElem)
               assert(modeAccessPoint is not None)
               runnableEntity.modeAccessPoints.append(modeAccessPoint)
            else:
               raise NotImplementedError(xmlElem.tag)
      if xmlServerCallPoints is not None:
         for xmlServerCallPoint in xmlServerCallPoints.findall('./SYNCHRONOUS-SERVER-CALL-POINT'):
            syncServerCallPoint = self.parseSyncServerCallPoint(xmlServerCallPoint)
            if syncServerCallPoint is not None: runnableEntity.serverCallPoints.append(syncServerCallPoint)
      if xmlCanEnterExclusiveAreas is not None:
         for xmlCanEnterExclusiveAreaRef in xmlCanEnterExclusiveAreas.findall('./CAN-ENTER-EXCLUSIVE-AREA-REF'):
            runnableEntity.exclusiveAreaRefs.append(parseTextNode(xmlCanEnterExclusiveAreaRef))
      if self.version >= 4.0 and xmlParameterAccessPoints is not None:
         for xmlChild in xmlParameterAccessPoints.findall('./*'):
            if xmlChild.tag == 'PARAMETER-ACCESS':
               tmp = self.parseParameterAccessPoint(xmlChild, runnableEntity)
               if tmp is not None:
                  runnableEntity.parameterAccessPoints.append(tmp)
            else:
               raise NotImplementedError('xmlChild.tag')
      
      if runnableEntity is not None:
         runnableEntity.adminData = adminData
      return runnableEntity

   def parseModeAccessPoint(self, xmlRoot):
      """parses <MODE-ACCESS-POINT>"""
      assert(xmlRoot.tag == 'MODE-ACCESS-POINT')
      modeGroupInstanceRef = None
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'MODE-GROUP-IREF':
            for childElem in xmlElem.findall('./*'):
               if childElem.tag == 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF':
                  if modeGroupInstanceRef is None:
                     modeGroupInstanceRef=self._parseModeGroupInstanceRef(childElem)
                  else:
                     NotImplementedError('Multiple instances of R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF not implemented')
               else:
                  raise NotImplementedError(childElem.tag)
         else:
            raise NotImplementedError(xmlElem.tag)
      if modeGroupInstanceRef is None:
         raise RuntimeError('R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF not set')
      return modeGroupInstanceRef

   def parseParameterAccessPoint(self, xmlRoot, parent = None):
      assert(xmlRoot.tag == 'PARAMETER-ACCESS')
      (name, accessedParameter) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'ACCESSED-PARAMETER':
            for xmlChild in xmlElem.findall('./*'):
               if xmlChild.tag == 'AUTOSAR-PARAMETER-IREF':
                  accessedParameter = self.parseParameterInstanceRef(xmlChild)
               elif xmlChild.tag == 'LOCAL-PARAMETER-REF':
                  accessedParameter = LocalParameterRef(self.parseTextNode(xmlChild))
               else:
                  raise NotImplementedError(xmlChild.tag)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None) and (accessedParameter is not None):
         return ParameterAccessPoint(name, accessedParameter)
      
   def _parseModeGroupInstanceRef(self, xmlRoot):
      """parses <R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF>"""
      assert(xmlRoot.tag == 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF')
      (requirePortRef, modeGroupRef ) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'CONTEXT-R-PORT-REF':
            requirePortRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'TARGET-MODE-GROUP-REF':
            modeGroupRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if requirePortRef is None:
         raise RuntimeError('CONTEXT-R-PORT-REF not set')
      if requirePortRef is None:
         raise RuntimeError('TARGET-MODE-GROUP-REF not set')
      return ModeGroupInstanceRef(requirePortRef, modeGroupRef)


   def parseModeInstanceRef(self, xmlRoot):
      """parses <MODE-IREF>"""
      assert(xmlRoot.tag == 'MODE-IREF')
      if self.version < 4.0:
         modeDeclarationRef=self.parseTextNode(xmlRoot.find('MODE-DECLARATION-REF'))
         modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlRoot.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
         requirePortPrototypeRef = self.parseTextNode(xmlRoot.find('R-PORT-PROTOTYPE-REF'))
      elif self.version >= 4.0:
         modeDeclarationRef=self.parseTextNode(xmlRoot.find('TARGET-MODE-DECLARATION-REF'))
         modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlRoot.find('CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
         requirePortPrototypeRef = self.parseTextNode(xmlRoot.find('CONTEXT-PORT-REF'))
      else:
         raise NotImplemented('version: '+self.version)
      return ModeInstanceRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)

   def parseParameterInstanceRef(self, xmlRoot):
      """parses <AUTOSAR-PARAMETER-IREF>"""
      assert(xmlRoot.tag == 'AUTOSAR-PARAMETER-IREF')
      portRef = self.parseTextNode(xmlRoot.find('PORT-PROTOTYPE-REF'))
      parameterDataRef = self.parseTextNode(xmlRoot.find('TARGET-DATA-PROTOTYPE-REF'))
      return ParameterInstanceRef(portRef, parameterDataRef)
   
   def _parseModeDependency(self,xmlRoot,parent=None):
      """parses <MODE-DEPENDENCY>"""
      assert(xmlRoot.tag == 'MODE-DEPENDENCY')
      modeDependency=ModeDependency()
      if xmlRoot.find('DEPENDENT-ON-MODE-IREFS') is not None:
         for xmlNode in xmlRoot.findall('./DEPENDENT-ON-MODE-IREFS/DEPENDENT-ON-MODE-IREF'):
            modeInstanceRef = self._parseDependentOnModeInstanceRef(xmlNode)
            if modeInstanceRef is not None:
               modeDependency.modeInstanceRefs.append(modeInstanceRef)
      return modeDependency

   def _parseDependentOnModeInstanceRef(self,xmlRoot,parent=None):
      """parses <DEPENDENT-ON-MODE-IREF>"""
      assert(xmlRoot.tag == 'DEPENDENT-ON-MODE-IREF')
      modeDeclarationRef=parseTextNode(xmlRoot.find('MODE-DECLARATION-REF'))
      modeDeclarationGroupPrototypeRef = parseTextNode(xmlRoot.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
      requirePortPrototypeRef = parseTextNode(xmlRoot.find('R-PORT-PROTOTYPE-REF'))
      return ModeDependencyRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)

   def _parseDisabledModesInstanceRefs(self,xmlRoot,parent=None):
      """parses <DISABLED-MODE-IREFS>"""
      assert(xmlRoot.tag == 'DISABLED-MODE-IREFS')
      disabledInModes = []
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'DISABLED-MODE-IREF':
            disabledInModes.append(self._parseDisabledModeInstanceRef(xmlElem))
         else:
            raise NotImplementedError(xmlElem.tag)
      return disabledInModes

   def _parseDisabledModeInstanceRef(self, xmlRoot):
      """parses <DISABLED-MODE-IREF>"""
      (requirePortPrototypeRef, modeDeclarationGroupPrototypeRef, modeDeclarationRef) = (None, None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'CONTEXT-PORT-REF':
            requirePortPrototypeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF':
            modeDeclarationGroupPrototypeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'TARGET-MODE-DECLARATION-REF':
            modeDeclarationRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (modeDeclarationRef is not None) and (modeDeclarationGroupPrototypeRef is not None) and (requirePortPrototypeRef is not None):
         return DisabledModeInstanceRef(modeDeclarationRef,modeDeclarationGroupPrototypeRef,requirePortPrototypeRef)
      else:
         raise RuntimeError('Parse Error: <CONTEXT-PORT-REF DEST>, <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF> and <TARGET-MODE-DECLARATION-REF> must be defined')

   def parseInitEvent(self,xmlNode,parent=None):
      name = parseTextNode(xmlNode.find('SHORT-NAME'))
      startOnEventRef = parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
      initEvent=InitEvent(name, startOnEventRef, parent)
      return initEvent

   def parseModeSwitchEvent(self,xmlNode,parent=None):
      """parses AUTOSAR3 <MODE-SWITCH-EVENT>"""
      if self.version < 4.0:
         assert(xmlNode.tag=='MODE-SWITCH-EVENT')
         name = parseTextNode(xmlNode.find('SHORT-NAME'))
         modeInstRef = self.parseModeInstanceRef(xmlNode.find('MODE-IREF'))
         startOnEventRef = parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
         activation = parseTextNode(xmlNode.find('ACTIVATION'))
         modeSwitchEvent=ModeSwitchEvent(name, startOnEventRef, activation, parent, self.version)
         modeSwitchEvent.modeInstRef=modeInstRef
      elif self.version >= 4.0:
         assert(xmlNode.tag=='SWC-MODE-SWITCH-EVENT')
         name = parseTextNode(xmlNode.find('SHORT-NAME'))
         modeInstanceRefs = []
         for xmlElem in xmlNode.findall('./MODE-IREFS/*'):
            if xmlElem.tag == 'MODE-IREF':
               modeInstanceRefs.append(self.parseModeInstanceRef(xmlElem))
            else:
               raise NotImplementedError(xmlElem.tag)
         startOnEventRef = parseTextNode(xmlNode.find('START-ON-EVENT-REF'))
         activation = parseTextNode(xmlNode.find('ACTIVATION'))
         modeSwitchEvent=ModeSwitchEvent(name, startOnEventRef, activation, parent, self.version)
         modeSwitchEvent.modeInstRef=modeInstanceRefs[0]
      else:
         raise NotImplementedError('version: '+self.version)
      return modeSwitchEvent

   def parseTimingEvent(self,xmlNode,parent=None):
      (name, startOnEventRef, period, xmlModeDepency, xmlDisabledModeRefs) = (None, None, None, None, None)
      for xmlElem in xmlNode.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif self.version >= 4.0 and xmlElem.tag == 'DISABLED-MODE-IREFS':
            xmlDisabledModeRefs =xmlElem
         elif self.version < 4.0 and xmlElem.tag == 'MODE-DEPENDENCY':
            xmlModeDepency =xmlElem
         elif xmlElem.tag == 'START-ON-EVENT-REF':
            startOnEventRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'PERIOD':
            period = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)

      if (name is not None) and (startOnEventRef is not None) and (period is not None):
         timingEvent=TimingEvent(name, startOnEventRef, float(period)*1000, parent)
         if xmlModeDepency is not None:
            timingEvent.modeDependency = self._parseModeDependency(xmlModeDepency, parent)
         elif xmlDisabledModeRefs is not None:
            timingEvent.disabledInModes = self._parseDisabledModesInstanceRefs(xmlDisabledModeRefs, parent)
         return timingEvent
      else:
         raise RuntimeError('Parse error: <SHORT-NAME> and <START-ON-EVENT-REF> and <PERIOD> must be defined')




   def parseDataReceivedEvent(self,xmlRoot,parent=None):
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))
      startOnEventRef = parseTextNode(xmlRoot.find('START-ON-EVENT-REF'))
      portTag = 'CONTEXT-R-PORT-REF' if self.version >= 4.0 else 'R-PORT-PROTOTYPE-REF'
      dataInstanceRef=self.parseDataInstanceRef(xmlRoot.find('DATA-IREF'),portTag)
      dataReceivedEvent=DataReceivedEvent(name, startOnEventRef, parent)
      xmlModeDependency = xmlRoot.find('MODE-DEPENDENCY')
      if xmlModeDependency is not None:
         dataReceivedEvent.modeDependency = self._parseModeDependency(xmlModeDependency)
      dataReceivedEvent.dataInstanceRef=dataInstanceRef
      return dataReceivedEvent

   def parseOperationInvokedEvent(self,xmlRoot,parent=None):
      (name, startOnEventRef, modeDependency, operationInstanceRef) = (None, None, None, None)      
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'START-ON-EVENT-REF':
            startOnEventRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'OPERATION-IREF':
            portTag = 'CONTEXT-P-PORT-REF' if self.version >= 4.0 else 'P-PORT-PROTOTYPE-REF'            
            operationInstanceRef = self.parseOperationInstanceRef(xmlElem, portTag)
         elif xmlElem.tag == 'MODE-DEPENDENCY':
            modeDependency = self._parseModeDependency(xmlModeDependency)
         else:
            raise NotImplementedError(xmlElem.tag)
      operationInvokedEvent=OperationInvokedEvent(name, startOnEventRef, parent)
      operationInvokedEvent.modeDependency = modeDependency      
      operationInvokedEvent.operationInstanceRef = operationInstanceRef
      return operationInvokedEvent

   def parseDataInstanceRef(self, xmlRoot, portTag):
      """parses <DATA-IREF>"""
      assert(xmlRoot.tag=='DATA-IREF')
      dataElemTag = 'TARGET-DATA-ELEMENT-REF' if self.version >= 4.0 else 'DATA-ELEMENT-PROTOTYPE-REF'
      (portRef, dataElemRef) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == portTag:
            portRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == dataElemTag:
            dataElemRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)         
      return DataInstanceRef(portRef,dataElemRef)

   def parseOperationInstanceRef(self,xmlRoot,portTag):
      """parses <OPERATION-IREF>"""
      assert(xmlRoot.tag=='OPERATION-IREF')
      assert(xmlRoot.find(portTag) is not None)

      if self.version >= 4.0:
         if portTag == 'CONTEXT-P-PORT-REF':
            operationTag = 'TARGET-PROVIDED-OPERATION-REF'
         else:
            operationTag = 'TARGET-REQUIRED-OPERATION-REF'
      else:
         operationTag = 'OPERATION-PROTOTYPE-REF'
      return OperationInstanceRef(parseTextNode(xmlRoot.find(portTag)),parseTextNode(xmlRoot.find(operationTag)))


   def parseDataElementInstanceRef(self,xmlRoot,portTag):
      """parses <DATA-ELEMENT-IREF>"""
      assert(xmlRoot.tag=='DATA-ELEMENT-IREF')
      assert(xmlRoot.find(portTag) is not None)
      return DataElementInstanceRef(parseTextNode(xmlRoot.find(portTag)),parseTextNode(xmlRoot.find('DATA-ELEMENT-PROTOTYPE-REF')))

   def parseSwcNvBlockNeeds(self,xmlRoot):
      name=parseTextNode(xmlRoot.find('SHORT-NAME'))
      numberOfDataSets=parseIntNode(xmlRoot.find('N-DATA-SETS'))
      readOnly=parseBooleanNode(xmlRoot.find('READONLY'))
      reliability=parseTextNode(xmlRoot.find('RELIABILITY'))
      resistantToChangedSW=parseBooleanNode(xmlRoot.find('RESISTANT-TO-CHANGED-SW'))
      restoreAtStart=parseBooleanNode(xmlRoot.find('RESTORE-AT-START'))
      writeOnlyOnce=parseBooleanNode(xmlRoot.find('WRITE-ONLY-ONCE'))
      writingFrequency=parseIntNode(xmlRoot.find('WRITING-FREQUENCY'))
      writingPriority=parseTextNode(xmlRoot.find('WRITING-PRIORITY'))
      defaultBlockRef=parseTextNode(xmlRoot.find('DEFAULT-BLOCK-REF'))
      mirrorBlockRef=parseTextNode(xmlRoot.find('MIRROR-BLOCK-REF'))
      serviceCallPorts=self.parseServiceCallPorts(xmlRoot.find('SERVICE-CALL-PORTS'))
      assert(len(serviceCallPorts)>0)
      swcNvBlockNeeds=SwcNvBlockNeeds(name,numberOfDataSets,readOnly,reliability,resistantToChangedSW,restoreAtStart,
                                      writeOnlyOnce,writingFrequency,writingPriority,defaultBlockRef,mirrorBlockRef)
      swcNvBlockNeeds.serviceCallPorts=serviceCallPorts
      return swcNvBlockNeeds

   def parseServiceCallPorts(self,xmlRoot):
      """parses <SERVICE-CALL-PORTS>"""
      assert(xmlRoot.tag=='SERVICE-CALL-PORTS')
      serviceCallPorts=[]
      for xmlNode in xmlRoot.findall('ROLE-BASED-R-PORT-ASSIGNMENT'):
         roleBasedRPortAssignment=RoleBasedRPortAssignment(parseTextNode(xmlNode.find('R-PORT-PROTOTYPE-REF')),parseTextNode(xmlNode.find('ROLE')))
         serviceCallPorts.append(roleBasedRPortAssignment)
      return serviceCallPorts

   def parseCalPrmElemPrototype(self, xmlRoot, parent):
      """
      parses <CALPRM-ELEMENT-PROTOTYPE>
      """
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))
      adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
      typeRef = parseTextNode(xmlRoot.find('TYPE-TREF'))
      calPrmElemPrototype = CalPrmElemPrototype(name, typeRef, parent, adminData)
      for xmlElem in xmlRoot.findall('./SW-DATA-DEF-PROPS/*'):
         if xmlElem.tag=='SW-ADDR-METHOD-REF':
            calPrmElemPrototype.swDataDefsProps.append(parseTextNode(xmlElem))
         else:
            raise NotImplementedError(xmlElem.tag)
      return calPrmElemPrototype

   def parseSyncServerCallPoint(self, xmlRoot):
      """
      parses <SYNCHRONOUS-SERVER-CALL-POINT>
      """
      assert(xmlRoot.tag=='SYNCHRONOUS-SERVER-CALL-POINT')
      if self.version >= 4.0:
         operationInstanceRefs=[]
         for xmlElem in xmlRoot.findall('*'):
            if xmlElem.tag=='SHORT-NAME':
               name=parseTextNode(xmlElem)
            elif xmlElem.tag=='OPERATION-IREF':
               operationInstanceRefs.append(self.parseOperationInstanceRef(xmlElem,'CONTEXT-R-PORT-REF'))
            elif xmlElem.tag=='TIMEOUT':
               timeout=parseFloatNode(xmlElem)
            else:
               raise NotImplementedError(xmlElem.tag)
      else:
         for xmlElem in xmlRoot.findall('*'):
            if xmlElem.tag=='SHORT-NAME':
               name=parseTextNode(xmlElem)
            elif xmlElem.tag=='OPERATION-IREFS':
               operationInstanceRefs=[]
               for xmlOperation in xmlElem.findall('*'):
                  if xmlOperation.tag=='OPERATION-IREF':
                     operationInstanceRefs.append(self.parseOperationInstanceRef(xmlOperation,'R-PORT-PROTOTYPE-REF'))
                  else:
                     raise NotImplementedError(xmlElem.tag)
            elif xmlElem.tag=='TIMEOUT':
               timeout=parseFloatNode(xmlElem)
            else:
               raise NotImplementedError(xmlElem.tag)
      retval=SyncServerCallPoint(name,timeout)
      retval.operationInstanceRefs=operationInstanceRefs
      return retval

   def parseAccessedVariable(self, xmlRoot):
      assert(xmlRoot.tag == 'ACCESSED-VARIABLE')
      xmlPortPrototypeRef = xmlRoot.find('./AUTOSAR-VARIABLE-IREF/PORT-PROTOTYPE-REF')
      xmlTargetDataPrototypeRef = xmlRoot.find('./AUTOSAR-VARIABLE-IREF/TARGET-DATA-PROTOTYPE-REF')
      assert (xmlPortPrototypeRef is not None)
      assert (xmlTargetDataPrototypeRef is not None)
      return VariableAccess(parseTextNode(xmlRoot.find('SHORT-NAME')),parseTextNode(xmlPortPrototypeRef), parseTextNode(xmlTargetDataPrototypeRef))

   def parseSwcServiceDependency(self, xmlRoot, parent = None):
      """parses <SWC-SERVICE-DEPENDENCY>"""
      assert(xmlRoot.tag == 'SWC-SERVICE-DEPENDENCY')
      (name, desc, serviceNeeds) = (None, None, None)
      roleBasedDataAssignments = []
      roleBasedPortAssignments = []
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DESC':
            desc = self.parseDescDirect(xmlElem)
         elif xmlElem.tag == 'ASSIGNED-DATAS':
            for xmlChildElem in xmlElem.findall('./*'):
               if xmlChildElem.tag == 'ROLE-BASED-DATA-ASSIGNMENT':
                  tmp = self._parseRoleBasedDataAssignment(xmlChildElem)
                  if tmp is not None: roleBasedDataAssignments.append(tmp)
               else:
                  raise NotImplementedError(xmlChildElem.tag)
         elif xmlElem.tag == 'ASSIGNED-PORTS':
            for xmlChildElem in xmlElem.findall('./*'):
               if xmlChildElem.tag == 'ROLE-BASED-PORT-ASSIGNMENT':
                  tmp = self._parseRoleBasedPortAssignment(xmlChildElem)
                  if tmp is not None: roleBasedPortAssignments.append(tmp)
               else:
                  raise NotImplementedError(xmlChildElem.tag)
         elif xmlElem.tag == 'SERVICE-NEEDS':
            serviceNeeds = self.parseServiceNeeds(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      swcServiceDependency = SwcServiceDependency(name, parent)
      if desc is not None:
         swcServiceDependency.desc=desc[0]
         swcServiceDependency.descAttr=desc[1]
      if serviceNeeds is not None:
         swcServiceDependency.serviceNeeds = serviceNeeds
      if len(roleBasedDataAssignments) > 0:
         swcServiceDependency.roleBasedDataAssignments = roleBasedDataAssignments
      if len(roleBasedPortAssignments) > 0:
         swcServiceDependency.roleBasedPortAssignments = roleBasedPortAssignments
      return swcServiceDependency


   def parseParameterDataPrototype(self, xmlRoot, parent = None):
      """parses <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)"""
      assert(xmlRoot.tag == 'PARAMETER-DATA-PROTOTYPE')
      (name, desc, variants, typeRef, swAddressMethodRef, swCalibrationAccess) = (None, None, None, None, None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DESC':
            desc = self.parseDescDirect(xmlElem)
         elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
            variants = self.parseSwDataDefProps(xmlElem)
            if len(variants) > 0:
               swAddressMethodRef = variants[0].swAddressMethodRef
               swCalibrationAccess = variants[0].swCalibrationAccess
         elif xmlElem.tag == 'TYPE-TREF':
            typeRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None) and (typeRef is not None):
         elem = ParameterDataPrototype(name, typeRef, swAddressMethodRef, swCalibrationAccess, parent)
         if desc is not None:
            elem.desc=desc[0]
            elem.descAttr=desc[1]
         return elem
      return None
      

   def parseServiceNeeds(self, xmlRoot, parent = None):
      """parses <SERVICE-NEEDS> (AUTOSAR 4)"""
      assert(xmlRoot.tag == 'SERVICE-NEEDS')
      (xmlNvBlockNeeds, nvBlockNeeds) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'NV-BLOCK-NEEDS':
            xmlNvBlockNeeds = xmlElem
         else:
            raise NotImplementedError(xmlElem.tag)
      serviceNeeds = ServiceNeeds(None, parent)
      if xmlNvBlockNeeds is not None:
         serviceNeeds.nvBlockNeeds = self.parseNvBlockNeeds(xmlElem, serviceNeeds)
      return serviceNeeds


   def parseNvBlockNeeds(self, xmlRoot, parent = None):
      """parses <NV-BLOCK-NEEDS> (AUTOSAR 4)"""
      (name, adminData, numberOfDataSets, ramBlockStatusControl, reliability, restoreAtStart, storeAtShutdown) = (
         None, None, None, None, None, None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'ADMIN-DATA':
            adminData = self.parseAdminDataNode(xmlElem)
         elif xmlElem.tag == 'N-DATA-SETS':
            numberOfDataSets = self.parseIntNode(xmlElem)
         elif xmlElem.tag == 'RAM-BLOCK-STATUS-CONTROL':
            ramBlockStatusControl = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'RELIABILITY':
            reliability = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'RESTORE-AT-START':
            restoreAtStart = self.parseBooleanNode(xmlElem)
         elif xmlElem.tag == 'STORE-AT-SHUTDOWN':
            storeAtShutdown = self.parseBooleanNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      #TODO: check if any of the below items has default values that can be set automatically if item is missing
      if name is None:
         raise RuntimeError('<SHORT-NAME> is missing or incorrectly formatted')
      if numberOfDataSets is None:
         raise RuntimeError('<N-DATA-SETS> is missing or incorrectly formatted')
      if ramBlockStatusControl is None:
         raise RuntimeError('<RAM-BLOCK-STATUS-CONTROL> is missing or incorrectly formatted')
      if reliability is None:
         raise RuntimeError('<RELIABILITY> is missing or incorrectly formatted')
      if restoreAtStart is None:
         raise RuntimeError('<RESTORE-AT-START> is missing or incorrectly formatted')
      if storeAtShutdown is None:
         raise RuntimeError('<STORE-AT-SHUTDOWN> is missing or incorrectly formatted')
      return NvBlockNeeds(name, numberOfDataSets, ramBlockStatusControl, reliability, restoreAtStart, storeAtShutdown, parent, adminData)

   def _parseRoleBasedDataAssignment(self, xmlRoot):
      assert(xmlRoot.tag == 'ROLE-BASED-DATA-ASSIGNMENT')
      (role, localVariableRef, localParameterRef) = (None, None, None)
      
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'ROLE':
            role = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'USED-DATA-ELEMENT':
            for xmlChild in xmlElem.findall('./*'):
               if xmlChild.tag == 'LOCAL-VARIABLE-REF':
                  localVariableRef = self.parseTextNode(xmlChild)
               else:
                  raise NotImplementedError(xmlChild.tag)
         elif xmlElem.tag == 'USED-PARAMETER-ELEMENT':
            pass
            for xmlChild in xmlElem.findall('./*'):
               if xmlChild.tag == 'LOCAL-PARAMETER-REF':
                  localParameterRef = LocalParameterRef(self.parseTextNode(xmlChild))
               else:
                  raise NotImplementedError(xmlChild.tag)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (role is not None) and ( (localVariableRef is not None) or (localParameterRef is not None) ):
         return RoleBasedDataAssignment(role, localVariableRef, localParameterRef)
      return None


   def _parseRoleBasedPortAssignment(self, xmlRoot):
      assert(xmlRoot.tag == 'ROLE-BASED-PORT-ASSIGNMENT')
      portRef = None
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'PORT-PROTOTYPE-REF':
            portRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if portRef is not None:
         return RoleBasedPortAssignment(portRef)
      return None