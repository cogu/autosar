from autosar.writer.writer_base import WriterBase
import autosar.behavior

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
      if len(internalBehavior.portAPIOptions)==0:         
         internalBehavior.createPortAPIOptionDefaults() #try to automatically create PortAPIOption objects on behavior object
      if len(internalBehavior.portAPIOptions)>0:
            lines.extend(self.indent(self._writePortAPIOptionsXML(internalBehavior),1))
      if len(internalBehavior.runnables)>0:
         lines.append(self.indent('<RUNNABLES>',1))
         for runnable in internalBehavior.runnables:
            lines.extend(self.indent(self._writeRunnableXML(runnable),2))
         lines.append(self.indent('</RUNNABLES>',1))
      lines.append(self.indent('<SUPPORTS-MULTIPLE-INSTANTIATION>%s</SUPPORTS-MULTIPLE-INSTANTIATION>'%('true' if internalBehavior.multipleInstance else 'false'),1))
      lines.append('</%s>'%internalBehavior.tag(self.version))
      return lines
   
   def _writeRunnableXML(self,runnable):
      ws=runnable.rootWS()
      assert(ws is not None)
      lines=['<RUNNABLE-ENTITY>',
             self.indent('<SHORT-NAME>%s</SHORT-NAME>'%runnable.name,1),
             self.indent('<CAN-BE-INVOKED-CONCURRENTLY>%s</CAN-BE-INVOKED-CONCURRENTLY>'%('true' if runnable.invokeConcurrently else 'false'),1),
            ]
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
      lines.append(self.indent('<SYMBOL>%s</SYMBOL>'%runnable.symbol,1))
      lines.append('</RUNNABLE-ENTITY>')
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
         for item in event.modeDependency:
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
         period = float(event.period)/1000.0
         lines.append(self.indent('<PERIOD>%.9f</PERIOD>'%(period),1))
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
   
