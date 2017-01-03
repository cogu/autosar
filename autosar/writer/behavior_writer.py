from autosar.writer.writer_base import WriterBase
import autosar.behavior
import autosar.base
import autosar.portinterface

class BehaviorWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeInternalBehaviorXML(self,internalBehavior,package):
      
      assert(isinstance(internalBehavior,autosar.behavior.InternalBehavior))
      lines=[]
      ws = internalBehavior.rootWS()
      assert(ws is not None)
      lines.append('<%s>'%internalBehavior.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%internalBehavior.name,1))
      swc=ws.find(internalBehavior.componentRef)
      assert(swc is not None)      
      lines.append(self.indent('<COMPONENT-REF DEST="%s">%s</COMPONENT-REF>'%(swc.tag(self.version),swc.ref),1))
      if len(internalBehavior.events):
         lines.append(self.indent('<EVENTS>',1))
         for event in internalBehavior.events:
            lines.extend(self.indent(self._writeEventXML(ws,event),2))
         lines.append(self.indent('</EVENTS>',1))
      if len(internalBehavior.exclusiveAreas)>0:
         lines.append(self.indent('<EXCLUSIVE-AREAS>',1))
         for exclusiveArea in internalBehavior.exclusiveAreas:
            lines.extend(self.indent(self._writeExclusiveAreaXML(ws,exclusiveArea),2))
         lines.append(self.indent('</EXCLUSIVE-AREAS>',1))                        
      if len(internalBehavior.portAPIOptions)==0:         
         internalBehavior.createPortAPIOptionDefaults() #try to automatically create PortAPIOption objects on behavior object
      if len(internalBehavior.perInstanceMemories)>0:
         lines.append(self.indent('<PER-INSTANCE-MEMORYS>',1))
         for memory in internalBehavior.perInstanceMemories:
            lines.extend(self.indent(self._writePerInstanceMemoryXML(ws,memory),2))
         lines.append(self.indent('</PER-INSTANCE-MEMORYS>',1))               
      if len(internalBehavior.portAPIOptions)>0:
            lines.extend(self.indent(self._writePortAPIOptionsXML(internalBehavior),1))
      if len(internalBehavior.runnables)>0:
         lines.append(self.indent('<RUNNABLES>',1))
         for runnable in internalBehavior.runnables:
            lines.extend(self.indent(self._writeRunnableXML(runnable),2))
         lines.append(self.indent('</RUNNABLES>',1))
      if len(internalBehavior.swcNvBlockNeeds)>0:
         lines.append(self.indent('<SERVICE-NEEDSS>',1))
         for elem in internalBehavior.swcNvBlockNeeds:
            lines.extend(self.indent(self._writeSwcNvBlockNeedsXML(ws, elem),2))
         lines.append(self.indent('</SERVICE-NEEDSS>',1))
      if len(internalBehavior.sharedCalParams)>0:
         lines.append(self.indent('<SHARED-CALPRMS>',1))
         for elem in internalBehavior.sharedCalParams:
            lines.extend(self.indent(self._writeSharedCalParamXML(ws, elem),2))
         lines.append(self.indent('</SHARED-CALPRMS>',1))
      lines.append(self.indent('<SUPPORTS-MULTIPLE-INSTANTIATION>%s</SUPPORTS-MULTIPLE-INSTANTIATION>'%('true' if internalBehavior.multipleInstance else 'false'),1))
      lines.append('</%s>'%internalBehavior.tag(self.version))
      return lines
   
   def _writeRunnableXML(self,runnable):
      ws=runnable.rootWS()
      assert(ws is not None)
      lines=['<RUNNABLE-ENTITY>',
             self.indent('<SHORT-NAME>%s</SHORT-NAME>'%runnable.name,1),             
            ]
      if runnable.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(runnable.adminData),1))
      lines.append(self.indent('<CAN-BE-INVOKED-CONCURRENTLY>%s</CAN-BE-INVOKED-CONCURRENTLY>'%('true' if runnable.invokeConcurrently else 'false'),1))
      if len(runnable.exclusiveAreaRefs)>0:
         lines.append(self.indent('<CAN-ENTER-EXCLUSIVE-AREA-REFS>',1))
         for exclusiveAreaRef in runnable.exclusiveAreaRefs:
            exclusiveArea = ws.find(exclusiveAreaRef)
            if exclusiveArea is None:
               raise ValueError('invalid reference:' + exclusiveAreaRef)
            lines.append(self.indent('<CAN-ENTER-EXCLUSIVE-AREA-REF DEST="%s">%s</CAN-ENTER-EXCLUSIVE-AREA-REF>'%(exclusiveArea.tag(self.version),exclusiveArea.ref),2))
         lines.append(self.indent('</CAN-ENTER-EXCLUSIVE-AREA-REFS>',1))
      if len(runnable.dataReceivePoints)>0:
         lines.append(self.indent('<DATA-RECEIVE-POINTS>',1))
         for dataReceivePoint in runnable.dataReceivePoints:
            lines.append(self.indent('<DATA-RECEIVE-POINT>',2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%dataReceivePoint.name,3))
            lines.append(self.indent('<DATA-ELEMENT-IREF>',3))
            assert(dataReceivePoint.portRef is not None) and (dataReceivePoint.dataElemRef is not None)
            port = ws.find(dataReceivePoint.portRef)
            assert(port is not None)
            dataElement = ws.find(dataReceivePoint.dataElemRef)
            assert(port is not None)            
            lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(port.tag(self.version),port.ref),4))
            lines.append(self.indent('<DATA-ELEMENT-PROTOTYPE-REF DEST="%s">%s</DATA-ELEMENT-PROTOTYPE-REF>'%(dataElement.tag(self.version),dataElement.ref),4))
            lines.append(self.indent('</DATA-ELEMENT-IREF>',3))
            lines.append(self.indent('</DATA-RECEIVE-POINT>',2))
         lines.append(self.indent('</DATA-RECEIVE-POINTS>',1))
      if len(runnable.dataSendPoints)>0:
         lines.append(self.indent('<DATA-SEND-POINTS>',1))
         for dataSendPoint in runnable.dataSendPoints:
            lines.append(self.indent('<%s>'%dataSendPoint.tag(self.version),2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%dataSendPoint.name,3))
            lines.append(self.indent('<DATA-ELEMENT-IREF>',3))
            assert(dataSendPoint.portRef is not None) and (dataSendPoint.dataElemRef is not None)
            port = ws.find(dataSendPoint.portRef)
            assert(port is not None)
            dataElement = ws.find(dataSendPoint.dataElemRef)
            assert(port is not None)            
            lines.append(self.indent('<P-PORT-PROTOTYPE-REF DEST="%s">%s</P-PORT-PROTOTYPE-REF>'%(port.tag(self.version),port.ref),4))
            lines.append(self.indent('<DATA-ELEMENT-PROTOTYPE-REF DEST="%s">%s</DATA-ELEMENT-PROTOTYPE-REF>'%(dataElement.tag(self.version),dataElement.ref),4))
            lines.append(self.indent('</DATA-ELEMENT-IREF>',3))
            lines.append(self.indent('</%s>'%dataSendPoint.tag(self.version),2))         
         lines.append(self.indent('</DATA-SEND-POINTS>',1))
      if len(runnable.serverCallPoints)>0:
         lines.append(self.indent('<SERVER-CALL-POINTS>',1))
         for callPoint in runnable.serverCallPoints:            
            lines.extend(self.indent(self._writeServerCallPointXML(ws, runnable, callPoint),2))
         lines.append(self.indent('</SERVER-CALL-POINTS>',1))
      lines.append(self.indent('<SYMBOL>%s</SYMBOL>'%runnable.symbol,1))
      lines.append('</RUNNABLE-ENTITY>')
      return lines
   
   def _writeServerCallPointXML(self, ws, runnable, callPoint):
      lines=[]
      if isinstance(callPoint, autosar.behavior.SyncServerCallPoint):
         lines.append('<SYNCHRONOUS-SERVER-CALL-POINT>')
         lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%callPoint.name,1))
         lines.append(self.indent('<OPERATION-IREFS>',1))
         for operationIRef in callPoint.operationInstanceRefs:
            lines.extend(self.indent(self._writeOperationInstanceRefXML(ws, runnable, operationIRef),2))
         lines.append(self.indent('</OPERATION-IREFS>',1))
         lines.append(self.indent('<TIMEOUT>%.9f</TIMEOUT>'%float(callPoint.timeout),1))
         lines.append('</SYNCHRONOUS-SERVER-CALL-POINT>')         								
      else:
         raise NotImplementedError(type(callPoint))
      return lines
   
   def _writePortAPIOptionsXML(self,internalBehavior):
      ws=internalBehavior.rootWS()
      assert(ws is not None)
      assert(isinstance(internalBehavior,autosar.behavior.InternalBehavior))
      lines=['<PORT-API-OPTIONS>']
      for option in internalBehavior.portAPIOptions:
         lines.extend(self.indent(self._writePortAPIOption(ws,option),1))         
      lines.append('</PORT-API-OPTIONS>')
      return lines
      
   def _writePortAPIOption(self, ws,option):
      lines=['<%s>'%option.tag(self.version)]
      lines.append(self.indent('<ENABLE-TAKE-ADDRESS>%s</ENABLE-TAKE-ADDRESS>'%('true' if option.takeAddress else 'false'),1))
      lines.append(self.indent('<INDIRECT-API>%s</INDIRECT-API>'%('true' if option.indirectAPI else 'false'),1))
      port = ws.find(option.portRef)
      if port is None:
         raise ValueError('invalid reference: '+option.portRef)
      lines.append(self.indent('<PORT-REF DEST="%s">%s</PORT-REF>'%(port.tag(self.version),port.ref),1))
      lines.append('</%s>'%option.tag(self.version))
      return lines

   def _writeEventXML(self, ws, event):
      lines = []
      tag = event.tag(self.version)
      lines.append('<%s>'%tag)
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%event.name,1))
      if event.modeDependency is not None:
         lines.append(self.indent('<MODE-DEPENDENCY>',1))
         lines.append(self.indent('<DEPENDENT-ON-MODE-IREFS>',2))
         for item in event.modeDependency.modeInstanceRefs:
            lines.extend(self.indent(self._writeModeInstanceRefXML(ws, item),3))         
         lines.append(self.indent('</DEPENDENT-ON-MODE-IREFS>',2))         
         lines.append(self.indent('</MODE-DEPENDENCY>',1))
      runnableEntity = ws.find(event.startOnEventRef)
      assert(runnableEntity is not None)
      lines.append(self.indent('<START-ON-EVENT-REF DEST="%s">%s</START-ON-EVENT-REF>'%(runnableEntity.tag(self.version),runnableEntity.ref),1))
      if isinstance(event, autosar.behavior.ModeSwitchEvent):         
         lines.append(self.indent('<ACTIVATION>%s</ACTIVATION>'%(event.activationType),1))
         lines.extend(self.indent(self._writeModeInstanceRefXML(ws,event.modeInstRef),1))
      elif isinstance(event, autosar.behavior.TimingEvent):
         if event.period==0:
            lines.append(self.indent('<PERIOD>0</PERIOD>',1))
         else:
            period = float(event.period)/1000.0
            lines.append(self.indent('<PERIOD>%.9f</PERIOD>'%(period),1))
      elif isinstance(event, autosar.behavior.OperationInvokedEvent):
         assert(event.operationInstanceRef is not None)
         lines.extend(self.indent(self._writeOperationInstanceRefXML(ws, event, event.operationInstanceRef),1))
      elif isinstance(event, autosar.behavior.DataReceivedEvent):
         assert(event.dataInstanceRef is not None)
         lines.extend(self.indent(self._writeDataInstanceRefXML(ws, event, event.dataInstanceRef),1))         
      else:
         raise NotImplementedError(str(type(event)))
      lines.append('</%s>'%tag)      
      return lines
   
   def _writeModeInstanceRefXML(self,ws,modeInstRef):
      lines = []
      tag = modeInstRef.tag(self.version)
      lines.append('<%s>'%tag)
      port = ws.find(modeInstRef.requirePortPrototypeRef)
      if port is None:
         raise ValueError('%s has invalid requirePortPrototypeRef: %s'%(modeInstRef,modeInstRef.requirePortPrototypeRef))
      modeDeclarationGroup = ws.find(modeInstRef.modeDeclarationGroupPrototypeRef)
      if modeDeclarationGroup is None:
         raise ValueError('%s has invalid modeDeclarationGroupPrototypeRef: %s'%(modeInstRef,modeInstRef.modeDeclarationGroupPrototypeRef))
      modeDeclaration = ws.find(modeInstRef.modeDeclarationRef)
      if modeDeclaration is None:
         raise ValueError('%s has invalid modeDeclarationRef: %s'%(modeInstRef,modeInstRef.modeDeclarationRef))
      lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">%s</R-PORT-PROTOTYPE-REF>'%(port.ref),1))
      lines.append(self.indent('<MODE-DECLARATION-GROUP-PROTOTYPE-REF DEST="%s">%s</MODE-DECLARATION-GROUP-PROTOTYPE-REF>'%(modeDeclarationGroup.tag(self.version), modeDeclarationGroup.ref),1))
      lines.append(self.indent('<MODE-DECLARATION-REF DEST="%s">%s</MODE-DECLARATION-REF>'%(modeDeclaration.tag(self.version) ,modeDeclaration.ref),1))
      lines.append('</%s>'%tag)            
      return lines
   
   def _writeOperationInstanceRefXML(self, ws, parent, operationIRef):
      lines = []
      lines.append('<%s>'%operationIRef.tag(self.version))
      port = ws.find(operationIRef.portRef)
      if port is None:
         raise ValueError('invalid reference "%s" found in callPoint.portRef of item "%s"'%(operationIRef.portRef, parent.ref))
      operation = ws.find(operationIRef.operationRef)
      if operation is None:
         raise ValueError('invalid reference "%s" found in callPoint.operation of item "%s"'%(operationIRef.operationRef, parent.ref))
      if isinstance(port, autosar.component.RequirePort):
         lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(port.tag(self.version), port.ref),1))
      else:
         lines.append(self.indent('<P-PORT-PROTOTYPE-REF DEST="%s">%s</P-PORT-PROTOTYPE-REF>'%(port.tag(self.version), port.ref),1))
      lines.append(self.indent('<OPERATION-PROTOTYPE-REF DEST="%s">%s</OPERATION-PROTOTYPE-REF>'%(operation.tag(self.version), operation.ref),1))
      lines.append('</%s>'%operationIRef.tag(self.version))
      return lines


   def _writeDataInstanceRefXML(self, ws, parent, dataIRef):
      lines = []
      lines.append('<%s>'%dataIRef.tag(self.version))
      port = ws.find(dataIRef.portRef)
      if port is None:
         raise ValueError('invalid reference "%s" found in dataIRef.portRef of item "%s"'%(dataIRef.portRef, parent.ref))
      dataElement = ws.find(dataIRef.dataElemRef)
      if dataElement is None:
         raise ValueError('invalid reference "%s" found in dataIRef.dataElemRef of item "%s"'%(dataIRef.dataElemRef, parent.ref))
      if isinstance(port, autosar.component.RequirePort):
         lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(port.tag(self.version), port.ref),1))
      else:
         lines.append(self.indent('<P-PORT-PROTOTYPE-REF DEST="%s">%s</P-PORT-PROTOTYPE-REF>'%(port.tag(self.version), port.ref),1))
      lines.append(self.indent('<DATA-ELEMENT-PROTOTYPE-REF DEST="%s">%s</DATA-ELEMENT-PROTOTYPE-REF>'%(dataElement.tag(self.version), dataElement.ref),1))
      lines.append('</%s>'%dataIRef.tag(self.version))
      return lines

   def _writePerInstanceMemoryXML(self, ws, memory):
      lines = []
      lines.append('<%s>'%memory.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%memory.name,1))
      dataType = ws.find(memory.typeRef)
      if dataType is None:
         raise ValueError('invalid reference "%s" in PerInstanceMemory object "%s"'%(memory.typeRef, memory.ref))
      lines.append(self.indent('<TYPE>%s</TYPE>'%dataType.name,1))
      lines.append(self.indent('<TYPE-DEFINITION>%s</TYPE-DEFINITION>'%dataType.ref,1))
      lines.append('</%s>'%memory.tag(self.version))
      return lines
   
   def _writeSwcNvBlockNeedsXML(self, ws, elem):
      lines = []
      lines.append('<%s>'%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      lines.append(self.indent('<N-DATA-SETS>%d</N-DATA-SETS>'%(int(elem.numberOfDataSets)),1))
      lines.append(self.indent('<READONLY>%s</READONLY>'%('true' if elem.readOnly else 'false'),1))
      lines.append(self.indent('<RELIABILITY>%s</RELIABILITY>'%(elem.reliability),1))
      lines.append(self.indent('<RESISTANT-TO-CHANGED-SW>%s</RESISTANT-TO-CHANGED-SW>'%('true' if elem.resistantToChangedSW else 'false'),1))
      lines.append(self.indent('<RESTORE-AT-START>%s</RESTORE-AT-START>'%('true' if elem.restoreAtStart else 'false'),1))
      lines.append(self.indent('<WRITE-ONLY-ONCE>%s</WRITE-ONLY-ONCE>'%('true' if elem.writeOnlyOnce else 'false'),1))
      lines.append(self.indent('<WRITING-FREQUENCY>%d</WRITING-FREQUENCY>'%(int(elem.writingFrequency)),1))
      lines.append(self.indent('<WRITING-PRIORITY>%s</WRITING-PRIORITY>'%(elem.writingPriority),1))
      defaultBlock = ws.find(elem.defaultBlockRef)
      if defaultBlock is None:
         raise ValueError('invalid reference "%s" in SwcNvBlockNeeds "%s"'%(elem.defaultBlockRef,elem.name))
      lines.append(self.indent('<DEFAULT-BLOCK-REF DEST="%s">%s</DEFAULT-BLOCK-REF>'%(defaultBlock.tag(self.version), defaultBlock.ref),1))
      mirrorBlock = ws.find(elem.mirrorBlockRef)
      if mirrorBlock is None:
         raise ValueError('invalid reference "%s" in SwcNvBlockNeeds "%s"'%(elem.mirrorBlockRef,elem.name))
      lines.append(self.indent('<MIRROR-BLOCK-REF DEST="%s">%s</MIRROR-BLOCK-REF>'%(mirrorBlock.tag(self.version), mirrorBlock.ref),1))
      lines.append(self.indent('<SERVICE-CALL-PORTS>',1))
      for callPoint in elem.serviceCallPorts:
         lines.append(self.indent('<ROLE-BASED-R-PORT-ASSIGNMENT>',2))
         port = ws.find(callPoint.portRef)
         if port is None:
            raise ValueError('invalid reference "%s" in SwcNvBlockNeeds "%s"'%(callPoint.portRef, elem.name))
         lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(port.tag(self.version), port.ref),3))
         lines.append(self.indent('<ROLE>%s</ROLE>'%callPoint.role,3))   
         lines.append(self.indent('</ROLE-BASED-R-PORT-ASSIGNMENT>',2))      
      lines.append(self.indent('</SERVICE-CALL-PORTS>',1))
      lines.append('</%s>'%elem.tag(self.version))
      return lines
   
   def _writeSharedCalParamXML(self, ws, elem):
      lines = []
      lines.append('<%s>'%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
      for ref in elem.swDataDefsProps:
         item = ws.find(ref)
         if item is None:
            raise ValueError('invalid reference "%s" in %s'%(ref,elem.name))         
         lines.append(self.indent('<SW-ADDR-METHOD-REF DEST="%s">%s</SW-ADDR-METHOD-REF>'%(item.tag(self.version), ref),2))
      lines.append(self.indent('</SW-DATA-DEF-PROPS>',1))
      dataType=ws.find(elem.typeRef)
      if dataType is None:
         raise ValueError('invalid reference "%s" in %s'%(elem.typeRef,elem.name))      
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(dataType.tag(self.version), dataType.ref),1))
      lines.append('</%s>'%elem.tag(self.version))
      return lines

   def _writeExclusiveAreaXML(self, ws, elem):
      lines=[]
      lines.append('<%s>'%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      lines.append('</%s>'%elem.tag(self.version))
      return lines

   ### code generators
   def writeInternalBehaviorCode(self, behavior, localvars):
      lines=[]      
      localvars['swc.behavior']=behavior
      localvars['swc']=localvars['ws'].find(behavior.componentRef)
      for exclusiveArea in behavior.exclusiveAreas:
         lines.extend(self._writeExclusiveAreaCode(exclusiveArea, localvars))
      for perInstanceMemory in behavior.perInstanceMemories:
         lines.extend(self._writePerInstanceMemoryCode(perInstanceMemory, localvars))
      for sharedCalParam in behavior.sharedCalParams:
         lines.extend(self._writeSharedCalParamCode(sharedCalParam, localvars))
      for swcNvBlockNeed in behavior.swcNvBlockNeeds:
         lines.extend(self._writeSwcNvBlockNeedCode(swcNvBlockNeed, localvars))      
      for runnable in behavior.runnables:
         lines.extend(self._writeRunnableCode(runnable, localvars))
      for event in behavior.events:
         lines.extend(self._writeEventCode(event, localvars))
      return lines           

   def _writeRunnableCode(self, runnable, localvars):
      ws=localvars['ws']
      
      lines=[]
      #name
      params=[repr(runnable.name)]
      params2=[]
      if len(runnable.dataReceivePoints)>0:
         for receivePoint in runnable.dataReceivePoints:
            params2.append(repr(self._createPortAccessString(runnable, receivePoint)))
      if len(runnable.dataSendPoints)>0:
         for sendPoint in runnable.dataSendPoints:
            params2.append(repr(self._createPortAccessString(runnable, sendPoint)))
      if len(runnable.serverCallPoints)>0:
         for callPoint in runnable.serverCallPoints:
            for instanceRef in callPoint.operationInstanceRefs:
               params2.append(repr(self._createPortAccessString(runnable, instanceRef)))
      assert( 'swc.behavior' in localvars)
      
      if len(params2)>0:
         if len(params2)<4:
            params.append('portAccess=[%s]'%(', '.join(params2)))            
         else:            
            lines.extend(self.writeListCode('portAccessList',params2))
            params.append('portAccess=portAccessList')
      if runnable.invokeConcurrently:
         params.append('concurrent=True')      
      #exclusive areas
      params2=[]
      for exclusiveAreaRef in runnable.exclusiveAreaRefs:
         exclusiveArea=ws.find(exclusiveAreaRef)
         if exclusiveArea is None:
            raise ValueError('invalid reference: '+exclusiveAreaRef)         
         params2.append(repr(exclusiveArea.name))      
      if len(params2)>0:
         if len(params2)==1:
            params.append('exclusiveAreas='+params2[0])
         else:
            params.append('exclusiveAreas=[%s]'%(', '.join(params2)))         
      if runnable.adminData is not None:
         param = self.writeAdminDataCode(runnable.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)      
      lines.append('swc.behavior.createRunnable(%s)'%(', '.join(params)))
      return lines
   
   def _writeEventCode(self, event, localvars):
      ws=localvars['ws']
      assert(ws is not None)
      assert('swc.behavior' in localvars)
      lines=[]
      
      runnableName = autosar.base.splitRef(event.startOnEventRef)[-1]
      params = [repr(runnableName)]
      if isinstance(event, autosar.behavior.ModeSwitchEvent):
         assert(event.modeInstRef is not None)         
         modeDeclParts = autosar.base.splitRef(event.modeInstRef.modeDeclarationRef)
         requirePortParts = autosar.base.splitRef(event.modeInstRef.requirePortPrototypeRef)
         modeRef = '/'.join([requirePortParts[-1],modeDeclParts[-1]])
         params.append(repr(modeRef))
         if event.activationType != 'ENTRY':
            params.append(repr(str(event.activationType)))
         constructor='createModeSwitchEvent'
      elif isinstance(event, autosar.behavior.TimingEvent):
         params.append('period='+str(event.period))
         constructor='createTimingEvent'
      elif isinstance(event, autosar.behavior.DataReceivedEvent):         
         port = ws.find(event.dataInstanceRef.portRef)
         if port is None:
            raise ValueError('invalid port reference: ' + event.dataInstanceRef.portRef)
         portInterface = ws.find(port.portInterfaceRef)
         if portInterface is None:
            raise ValueError('invalid portInterface reference: ' + port.portInterfaceRef)
         dataElement = ws.find(event.dataInstanceRef.dataElemRef)
         if dataElement is None:
            raise ValueError('invalid dataElement reference: ' + event.dataInstanceRef.dataElemRef)
         if len(portInterface.dataElements)>1:
            params.append("'%s/%s'"%(port.name, dataElement.name)) #it is enough to just write the name of port/dataElement
         elif len(portInterface.dataElements)==1:
            params.append(repr(port.name)) #it is enough to just write the name of the port
         else:
            raise ValueError('portInterface without any data elements')
         if len(event.swDataDefsProps)>0:
            raise NotImplementedError('event has swDataDefsProps')
         constructor='createDataReceivedEvent'
      elif isinstance(event, autosar.behavior.OperationInvokedEvent):
         parts1=autosar.base.splitRef(event.operationInstanceRef.portRef)
         parts2=autosar.base.splitRef(event.operationInstanceRef.operationRef)
         params.append("'%s/%s'"%(parts1[-1],parts2[-1])) #it is enough information to just write the names, not the full references
         if len(event.swDataDefsProps)>0:
            raise NotImplementedError('event has swDataDefsProps')
         constructor = 'createOperationInvokedEvent'
      else:
         raise NotImplementedError(type(event))
      if event.modeDependency is not None:
         params2=[]
         for iref in event.modeDependency.modeInstanceRefs:
            assert(isinstance(iref, autosar.behavior.ModeDependencyRef))
            requirePort = ws.find(iref.requirePortPrototypeRef)
            modeDeclaration = ws.find(iref.modeDeclarationRef)
            if requirePort is None:
               raise ValueError('invalid port reference: '+iref.requirePortPrototypeRef)
            if modeDeclaration is None:
               raise ValueError('invalid mode declaration reference: '+iref.modeDeclarationRef)
            #we can recreate the entire ModeDependencyRef object later using only the port name and the name of the mode declaration            
            params2.append("'%s/%s'"%(requirePort.name, modeDeclaration.name))
         if len(params2)>3:
            lines.extend(self.writeListCode('modeDependencyList',params2))
            params.append('modeDependency=modeDependencyList')
         else:
            params.append('modeDependency=[%s]'%(', '.join(params2)))
      lines.append('swc.behavior.%s(%s)'%(constructor, ', '.join(params)))
      return lines
   
   def _createPortAccessString(self, runnable, sendReceiveCallPoint):
      """
      creates a port access string of the form 'port' or 'port/dataElem' or 'port/operationName'
      sendReceiveCallPoint can be of type DataInstanceRef, OperationInstanceRef
      """
      ws=runnable.rootWS()
      assert(ws is not None)
      port=ws.find(sendReceiveCallPoint.portRef)
      if port is None:
         raise ValueError('Invalid portRef "%s" in runnable "%s"'(self.portRef,runnable.ref))
      portInterface = ws.find(port.portInterfaceRef)
      if portInterface is None:
         raise ValueError('Invalid portInterfaceRef "%s" in port "%s"'(port.portInterfaceRef,port.ref))
      if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface) or isinstance(portInterface, autosar.portinterface.ParameterInterface):
         if len(portInterface.dataElements)==1:
            #there is only one data element in this interface, only the port name is required since there is ambiguity
            return port.name
         else:
            #there is possible ambiguity what element we mean, create a portaccess reference in the form "portName/dataElementName"
            parts=autosar.base.splitRef(sendReceiveCallPoint.dataElemRef)
            return '/'.join([port.name,parts[-1]])
      elif isinstance(portInterface, autosar.portinterface.ClientServerInterface):
         parts=autosar.base.splitRef(sendReceiveCallPoint.operationRef)
         return '/'.join([port.name,parts[-1]])
      else:
         raise NotImplementedError(type(portInterface))

   def _writeExclusiveAreaCode(self, exclusiveArea, localvars):
      """
      creates a call to create an ExclusiveArea object
      """      
      return [('swc.behavior.createExclusiveArea(%s)'%(repr(exclusiveArea.name)))]
   
   def _writePerInstanceMemoryCode(self, perInstanceMemory, localvars):
      """
      create a call to create a PerInstanceMemory object
      """
      lines=[]
      ws = localvars['ws']
      #name
      params=[repr(perInstanceMemory.name)]
      #typeref
      dataType = ws.find(perInstanceMemory.typeRef)
      if dataType is None:
         raise ValueError('invalid reference: '+perInstanceMemory.typeRef)
      if ws.roles['DataType'] is not None:
         params.append(repr(dataType.name)) #use name only
      else:
         params.append(repr(dataType.ref)) #use full reference
      lines.append('swc.behavior.createPerInstanceMemory(%s)'%(', '.join(params)))
      return lines
   
   def _writeSharedCalParamCode(self, sharedCalParam, localvars):      
      lines=[]
      ws = localvars['ws']
      #name
      params=[repr(sharedCalParam.name)]
      #typeref
      dataType = ws.find(sharedCalParam.typeRef)
      if dataType is None:
         raise ValueError('invalid reference: '+perInstanceMemory.typeRef)
      if ws.roles['DataType'] is not None:
         params.append(repr(dataType.name)) #use name only
      else:
         params.append(repr(dataType.ref)) #use full reference
      if len(sharedCalParam.swDataDefsProps)!=1:
         raise NotImplementedError('expected one element in swDataDefsProps')
      params.append(repr(sharedCalParam.swDataDefsProps[0]))
      if sharedCalParam.adminData is not None:
         param = self.writeAdminDataCode(sharedCalParam.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)      
      lines.append('swc.behavior.createSharedCalParam(%s)'%(', '.join(params)))
      return lines

   def _writeSwcNvBlockNeedCode(self, swcNvBlockNeed, localvars):
      lines=[]
      ws = localvars['ws']
      #name
      params=[repr(swcNvBlockNeed.name)]
      params2=self._createNvmBlockOpts(swcNvBlockNeed, localvars)
      lines.extend(self.writeDictCode('blockParams',params2))
      params.append('blockParams')
      lines.append('swc.behavior.createNvmBlock(%s)'%(', '.join(params)))
      return lines
   
   def _createNvmBlockOpts(self, swcNvBlockNeed, localvars):
      lines=[]
      ws = localvars['ws']
      behavior=localvars['swc.behavior']
      assert((ws is not None) and (behavior is not None))
      lines.append("'numberOfDataSets': "+(repr(swcNvBlockNeed.numberOfDataSets)))
      lines.append("'readOnly': "+(repr(swcNvBlockNeed.readOnly)))
      lines.append("'reliability': "+(repr(swcNvBlockNeed.reliability)))
      lines.append("'resistantToChangedSW': "+(repr(swcNvBlockNeed.resistantToChangedSW)))
      lines.append("'restoreAtStart': "+(repr(swcNvBlockNeed.restoreAtStart)))
      lines.append("'writeOnlyOnce': "+(repr(swcNvBlockNeed.writeOnlyOnce)))
      lines.append("'writingFrequency': "+(repr(swcNvBlockNeed.writingFrequency)))
      lines.append("'writingPriority': "+(repr(swcNvBlockNeed.writingPriority)))
      defaultBlock = ws.find(swcNvBlockNeed.defaultBlockRef)
      if (defaultBlock is not None) and (defaultBlock.parent is behavior):
         lines.append("'defaultBlock': "+(repr(defaultBlock.name)))
      else:
         lines.append("'defaultBlock': "+(repr(swcNvBlockNeed.defaultBlockRef)))
      mirrorBlock = ws.find(swcNvBlockNeed.mirrorBlockRef)
      if (defaultBlock is not None) and (defaultBlock.parent is behavior):
         lines.append("'mirrorBlock': "+(repr(mirrorBlock.name)))
      else:
         lines.append("'mirrorBlock': "+(repr(swcNvBlockNeed.mirrorBlockRef)))            
      params=[]
      for roleBasedRPortAssignment in swcNvBlockNeed.serviceCallPorts:
         port = ws.find(roleBasedRPortAssignment.portRef)
         if port is None:
            raise ValueError('invalid port reference: '+roleBasedRPortAssignment.portRef)         
         params.append("'%s/%s'"%(port.name, roleBasedRPortAssignment.role )) #it seems like the ClientServer operation is in this part of the XML is called "role" for some inexplicable reason
      if len(params)>0:
         if len(params)==1:
            lines.append("'serviceCallPorts': %s"%(params[0]))
         else:
            lines.append("'serviceCallPorts': [%s]"%(', '.join(params)))
      return lines