from autosar.writer.writer_base import WriterBase
import autosar.base
import autosar.workspace
import autosar.constant

class ComponentTypeWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeApplicationSoftwareComponentXML(self,swc,package):
      assert(isinstance(swc,autosar.component.ApplicationSoftwareComponent))
      return self._writeComponentXML(swc)

   def writeComplexDeviceDriverComponentXML(self,swc,package):
      assert(isinstance(swc,autosar.component.ComplexDeviceDriverComponent))
      return self._writeComponentXML(swc)

   def writeCompositionComponentXML(self,swc,package):
      assert(isinstance(swc,autosar.component.CompositionComponent))
      return self._writeComponentXML(swc)
   
   def _writeComponentXML(self, swc):
      lines=[]
      ws = swc.rootWS()
      assert(ws is not None)
      lines=[]
      lines.append('<%s>'%swc.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%swc.name,1))
      lines.append(self.indent('<PORTS>',1))
      for port in swc.providePorts:
         lines.extend(self.indent(self._writeProvidePortXML(port),2))
      for port in swc.requirePorts:
         lines.extend(self.indent(self._writeRequirePortXML(port),2))
      lines.append(self.indent('</PORTS>',1))
      if isinstance(swc, autosar.component.CompositionComponent):
         lines.extend(self.indent(self._writeComponentsXML(ws, swc.components),1))
         if (len(swc.assemblyConnectors)>0) or (len(swc.delegationConnectors)>0):
            lines.append(self.indent('<CONNECTORS>',1))
            if len(swc.assemblyConnectors)>0:
               lines.extend(self.indent(self._writeAssemblyConnectorsXML(ws, swc.assemblyConnectors),2))
            if len(swc.delegationConnectors)>0:
               lines.extend(self.indent(self._writeDelegationConnectorsXML(ws, swc.delegationConnectors),2))
            lines.append(self.indent('</CONNECTORS>',1))
      lines.append('</%s>'%swc.tag(self.version))
      return lines
      
   
   def _writeRequirePortXML(self, port):
      lines=[]
      assert(port.ref is not None)
      ws=port.rootWS()
      assert(ws is not None)
      portInterface=ws.find(port.portInterfaceRef)
      lines.append('<R-PORT-PROTOTYPE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%port.name,1))
      if isinstance(portInterface, autosar.portinterface.ClientServerInterface) and isinstance(port.parent, autosar.component.CompositionComponent) or len(port.comspec)==0:
         lines.append(self.indent('<REQUIRED-COM-SPECS></REQUIRED-COM-SPECS>',1))
      else:
         lines.append(self.indent('<REQUIRED-COM-SPECS>',1))
         if portInterface is None:
            raise ValueError("%s: invalid reference detected: '%s'"%(port.ref,port.portInterfaceRef))
         for comspec in port.comspec:
            elem=portInterface.find(comspec.name)
            if elem is None:
               raise ValueError("%s: invalid comspec name '%s'"%(port.ref,comspec.name))
            if isinstance(elem,autosar.portinterface.DataElement):
               if elem.isQueued:
                  if self.version<4.0:
                     lines.append(self.indent('<QUEUED-RECEIVER-COM-SPEC>',2))
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),3))
                     lines.append(self.indent('<QUEUE-LENGTH>%d</QUEUE-LENGTH>'%(int(comspec.queueLength)),3))
                     lines.append(self.indent('</QUEUED-RECEIVER-COM-SPEC>',2))
               else:
                  if self.version<4.0:
                     lines.append(self.indent('<UNQUEUED-RECEIVER-COM-SPEC>',2))
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),3))
                     lines.append(self.indent('<ALIVE-TIMEOUT>%d</ALIVE-TIMEOUT>'%(comspec.aliveTimeout),3))
                     if comspec.initValueRef is not None:
                        tag = ws.find(comspec.initValueRef).tag(self.version)
                        lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(tag,comspec.initValueRef),3))
                     lines.append(self.indent('</UNQUEUED-RECEIVER-COM-SPEC>',2))
            elif isinstance(elem,autosar.portinterface.Operation):
               lines.append(self.indent('<CLIENT-COM-SPEC>',2))
               lines.append(self.indent('<OPERATION-REF DEST="%s">%s</OPERATION-REF>'%(elem.tag(self.version),elem.ref),3))
               lines.append(self.indent('</CLIENT-COM-SPEC>',2))
            else:
               raise NotImplementedError(str(type(elem)))
         lines.append(self.indent('</REQUIRED-COM-SPECS>',1))
      lines.append(self.indent('<REQUIRED-INTERFACE-TREF DEST="%s">%s</REQUIRED-INTERFACE-TREF>'%(portInterface.tag(self.version),portInterface.ref),1))
      lines.append('</R-PORT-PROTOTYPE>')
      return lines   
   
   def _writeProvidePortXML(self, port):
      lines=[]
      assert(port.ref is not None)
      ws=port.rootWS()
      assert(ws is not None)
      portInterface=ws.find(port.portInterfaceRef)
      lines.append('<%s>'%port.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%port.name,1))
      if isinstance(portInterface, autosar.portinterface.ClientServerInterface) and isinstance(port.parent, autosar.component.CompositionComponent) or len(port.comspec)==0:
         lines.append(self.indent('<PROVIDED-COM-SPECS></PROVIDED-COM-SPECS>',1))
      else:
         lines.append(self.indent('<PROVIDED-COM-SPECS>',1))
         if portInterface is None:
            raise ValueError("%s: invalid reference detected: '%s'"%(port.ref,port.portInterfaceRef))
         for comspec in port.comspec:         
            elem=portInterface.find(comspec.name)
            if elem is None:
               raise ValueError("%s: invalid comspec name '%s'"%(port.ref,comspec.name))
            if isinstance(elem,autosar.portinterface.DataElement):                              
               if elem.isQueued:
                  if self.version<4.0:
                     lines.append(self.indent('<QUEUED-SENDER-COM-SPEC>',2))
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),3))
                     lines.append(self.indent('</QUEUED-SENDER-COM-SPEC>',2))
               else:
                  if self.version<4.0:
                     lines.append(self.indent('<UNQUEUED-SENDER-COM-SPEC>',2))                  
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),3))
                     if isinstance(comspec.canInvalidate,bool):
                        lines.append(self.indent('<CAN-INVALIDATE>%s</CAN-INVALIDATE>'%('true' if comspec.canInvalidate else 'false'),3))                     
                     if comspec.initValueRef is not None:
                        tag = ws.find(comspec.initValueRef).tag(self.version)
                        lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(tag,comspec.initValueRef),3))                  
                     lines.append(self.indent('</UNQUEUED-SENDER-COM-SPEC>',2))
            elif isinstance(elem,autosar.portinterface.Operation):
               lines.append(self.indent('<SERVER-COM-SPEC>',2))
               lines.append(self.indent('<OPERATION-REF DEST="%s">%s</OPERATION-REF>'%(elem.tag(self.version),elem.ref),3))
               lines.append(self.indent('<QUEUE-LENGTH>%d</QUEUE-LENGTH>'%(int(comspec.queueLength)),3))
               lines.append(self.indent('</SERVER-COM-SPEC>',2))
            else:
               raise NotImplementedError(str(type(elem)))
         lines.append(self.indent('</PROVIDED-COM-SPECS>',1))      
      lines.append(self.indent('<PROVIDED-INTERFACE-TREF DEST="%s">%s</PROVIDED-INTERFACE-TREF>'%(portInterface.tag(self.version),portInterface.ref),1))
      lines.append('</%s>'%port.tag(self.version))      
      return lines

   def writeSwcImplementationXML(self,elem,package):
      assert(isinstance(elem,autosar.component.SwcImplementation))
      lines=[]
      ws = elem.rootWS()
      assert(ws is not None)
      behavior = ws.find(elem.behaviorRef)
      if behavior is None:
         raise ValueError('invalid reference: '+str(elem.behaviorRef))
      lines=['<SWC-IMPLEMENTATION>',
             self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1)        
            ]
      lines.append(self.indent('<CODE-DESCRIPTORS>',1))
      lines.append(self.indent('<CODE>',2))
      lines.append(self.indent('<SHORT-NAME>Code</SHORT-NAME>',3))
      lines.append(self.indent('<TYPE>SRC</TYPE>',3))
      lines.append(self.indent('</CODE>',2))
      lines.append(self.indent('</CODE-DESCRIPTORS>',1))
      lines.append(self.indent('<BEHAVIOR-REF DEST="%s">%s</BEHAVIOR-REF>'%(behavior.tag(self.version),elem.behaviorRef),1))
      lines.append('</SWC-IMPLEMENTATION>')
      return lines
   
   def _writeComponentsXML(self, ws, components):
      lines=[]
      if len(components)>0:
         lines.append('<COMPONENTS>')
         for component in components:
            swc = ws.find(component.typeRef)
            if swc is None:
               raise ValueError('Invalid reference: '+component.typeRef)
            lines.append(self.indent('<COMPONENT-PROTOTYPE>',1))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%component.name,2))
            lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(swc.tag(self.version),swc.ref),2))
            lines.append(self.indent('</COMPONENT-PROTOTYPE>',1))
         lines.append('</COMPONENTS>')
      return lines   

   def _writeAssemblyConnectorsXML(self, ws, connectors):
      lines=[]
      for connector in connectors:
         lines.append('<%s>'%connector.tag(self.version))
         lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%connector.name, 1))
         lines.append(self.indent('<%s>'%connector.providerInstanceRef.tag(self.version), 1))
         providerComponent = ws.find(connector.providerInstanceRef.componentRef)
         if providerComponent is None:
            raise ValueError('invalid reference: ' +connector.providerInstanceRef.componentRef)
         providePort = ws.find(connector.providerInstanceRef.portRef)
         if providePort is None:
            raise ValueError('invalid reference: ' +connector.providerInstanceRef.portRef)
         lines.append(self.indent('<COMPONENT-PROTOTYPE-REF DEST="%s">%s</COMPONENT-PROTOTYPE-REF>'%(providerComponent.tag(self.version), providerComponent.ref), 2))
         lines.append(self.indent('<P-PORT-PROTOTYPE-REF DEST="%s">%s</P-PORT-PROTOTYPE-REF>'%(providePort.tag(self.version), providePort.ref), 2))
         lines.append(self.indent('</%s>'%connector.providerInstanceRef.tag(self.version), 1))
         lines.append(self.indent('<%s>'%connector.requesterInstanceRef.tag(self.version), 1))
         requesterComponent = ws.find(connector.requesterInstanceRef.componentRef)
         if requesterComponent is None:
            raise ValueError('invalid reference: ' +connector.requesterInstanceRef.componentRef)
         requirePort = ws.find(connector.requesterInstanceRef.portRef)
         if requirePort is None:
            raise ValueError('invalid reference: ' +connector.requesterInstanceRef.portRef)
         lines.append(self.indent('<COMPONENT-PROTOTYPE-REF DEST="%s">%s</COMPONENT-PROTOTYPE-REF>'%(requesterComponent.tag(self.version), requesterComponent.ref), 2))
         lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(requirePort.tag(self.version), requirePort.ref), 2))
         lines.append(self.indent('</%s>'%connector.requesterInstanceRef.tag(self.version), 1))
         lines.append('</%s>'%connector.tag(self.version))
      return lines

   def _writeDelegationConnectorsXML(self, ws, connectors):
      lines=[]
      for connector in connectors:
         lines.append('<%s>'%connector.tag(self.version))
         lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%connector.name, 1))
         lines.append(self.indent('<%s>'%connector.innerPortInstanceRef.tag(self.version), 1))
         innerComponent = ws.find(connector.innerPortInstanceRef.componentRef)
         if innerComponent is None:
            raise ValueError('invalid reference: ' +connector.innerPortInstanceRef.componentRef)
         innerPort = ws.find(connector.innerPortInstanceRef.portRef)
         if innerPort is None:
            raise ValueError('invalid reference: ' +connector.innerPortInstanceRef.portRef)
         lines.append(self.indent('<COMPONENT-PROTOTYPE-REF DEST="%s">%s</COMPONENT-PROTOTYPE-REF>'%(innerComponent.tag(self.version), innerComponent.ref), 2))
         lines.append(self.indent('<PORT-PROTOTYPE-REF DEST="%s">%s</PORT-PROTOTYPE-REF>'%(innerPort.tag(self.version), innerPort.ref), 2))
         lines.append(self.indent('</%s>'%connector.innerPortInstanceRef.tag(self.version), 1))
         outerPort = ws.find(connector.outerPortRef.portRef)
         if outerPort is None:
            raise ValueError('invalid reference: ' +connector.outerPortRef.portRef)
         lines.append(self.indent('<OUTER-PORT-REF DEST="%s">%s</OUTER-PORT-REF>'%(outerPort.tag(self.version), outerPort.ref), 1))         
         lines.append('</%s>'%connector.tag(self.version))
      return lines
         
   ### Code generators   
   def writeApplicationSoftwareComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createApplicationSoftwareComponent', localvars)
   
   def writeComplexDeviceDriverComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createComplexDeviceDriverComponent', localvars)

   def writeCompositionComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createCompositionComponent', localvars)

   def _writeComponentCode(self, swc, methodName, localvars):
      lines=[]
      ws = localvars['ws']
      lines.append("swc = package.%s(%s)"%(methodName,repr(swc.name)))
      localvars['swc']=swc
      if len(swc.providePorts)>0:
         lines.extend(self._writeComponentProvidePortsCode(swc))
      if len(swc.requirePorts)>0:
         lines.extend(self._writeComponentRequirePortsCode(swc))                  
      if isinstance(swc, autosar.component.CompositionComponent):
         if len(swc.components)>0:
            lines.extend(self._writeComponentsCode(swc.components, localvars))
         if len(swc.assemblyConnectors)>0:
            lines.extend(self._writeAssemblyConnectorsCode(swc.assemblyConnectors, localvars))
         if len(swc.delegationConnectors)>0:
            lines.extend(self._writeDelegationConnectorsCode(swc.delegationConnectors, localvars))
      return lines
   
   def _writeComponentProvidePortsCode(self,swc):
      lines=[]
      ws=swc.rootWS()
      assert(isinstance(ws,autosar.Workspace))
      for port in swc.providePorts:
         params=[]
         #name
         params.append(repr(port.name))
         portInterface=ws.find(port.portInterfaceRef, role='PortInterface')
         if portInterface is None:
            raise ValueError('invalid reference: '+port.portInterfaceRef)         
         if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface) or isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            #portInterfaceRef
            if ws.roles['PortInterface'] is not None:
               params.append(repr(portInterface.name)) #use name only
            else:
               params.append(repr(portInterface.ref)) #use full reference            
            if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
               #comspec
               if len(port.comspec)>0:
                  if len(port.comspec)==1:
                     comspec=port.comspec[0]
                     if comspec.initValueRef is not None:
                        initValue = ws.find(comspec.initValueRef)
                        if initValue is None:
                           raise ValueError('invalid reference: '+comspec.initValueRef)                                          
                        if isinstance(initValue, autosar.constant.Constant):
                           pass
                        elif isinstance(initValue, autosar.constant.Value):
                           initValue = initValue.parent #we can shorten the ref string by pointing to its direct parent instead
                        else:
                           raise ValueError('invalid reference type "%s" for "%s", expected Constant or Value'%(str(type(initValue)), initValue.ref))
                        if ws.roles['Constant'] is not None:
                           params.append('initValueRef='+repr(initValue.name)) #use name only
                        else:
                           params.append('initValueRef='+repr(initValue.ref)) #use full reference
                  else:
                     raise NotImplementedError('multiple comspecs not yet supported')                                    
         else:
            raise NotImplementedError(type(portInterface))
         lines.append('swc.createProvidePort(%s)'%(', '.join(params)))
      return lines

   def _writeComponentRequirePortsCode(self,swc):
      lines=[]
      ws=swc.rootWS()
      assert(isinstance(ws,autosar.Workspace))
      for port in swc.requirePorts:
         params=[]
         #name
         params.append(repr(port.name))
         portInterface=ws.find(port.portInterfaceRef, role='PortInterface')
         if portInterface is None:
            raise ValueError('invalid reference: '+port.portInterfaceRef)         
         if isinstance(portInterface,autosar.portinterface.PortInterface):
            #portInterfaceRef
            if ws.roles['PortInterface'] is not None:
               params.append(repr(portInterface.name)) #use name only
            else:
               params.append(repr(portInterface.ref)) #use full reference            
            if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
               if len(port.comspec)>0:
                  if len(port.comspec)==1:
                     comspec=port.comspec[0]
                     if comspec.initValueRef is not None:
                        initValue = ws.find(comspec.initValueRef)
                        if initValue is None:
                           raise ValueError('invalid reference: '+comspec.initValueRef)                                          
                        if isinstance(initValue, autosar.constant.Constant):
                           pass
                        elif isinstance(initValue, autosar.constant.Value):
                           initValue = initValue.parent #we can shorten the ref string by pointing to its direct parent instead
                        else:
                           raise ValueError('invalid reference type "%s" for "%s", expected Constant or Value'%(str(type(initValue)), initValue.ref))
                        if ws.roles['Constant'] is not None:
                           params.append('initValueRef='+repr(initValue.name)) #use name only
                        else:
                           params.append('initValueRef='+repr(initValue.ref)) #use full reference
                     if (comspec.aliveTimeout is not None) and int(comspec.aliveTimeout)>0:
                        params.append("aliveTimeout=%d"%int(comspec.aliveTimeout))
                     if (comspec.queueLength is not None) and int(comspec.queueLength)!=1:
                        params.append("queueLength=%d"%int(comspec.queueLength))
                  else:
                     raise NotImplementedError('multiple comspecs not yet supported')            
         else:
            raise NotImplementedError(type(portInterface))         
         lines.append('swc.createRequirePort(%s)'%(', '.join(params)))
      return lines

   
   def writeSwcImplementationCode(self, elem, localvars):
      """
      No need to generate python code for explicitly creating SwcImplementation object
      """
      return []
   
   
   def _writeComponentsCode(self, components, localvars):
      lines=[]
      assert('swc' in localvars)
      for component in components:
         params=[]
         assert(isinstance(component, autosar.component.ComponentPrototype))         
         params.append(repr(self._createComponentRef(component.typeRef, localvars)))
         lines.append('swc.createComponentRef(%s)'%(', '.join(params)))
      return lines
  
   def _writeAssemblyConnectorsCode(self, connectors, localvars):
      lines=[]
      ws = localvars['ws']
      swc = localvars['swc']
      
      assert(ws is not None)
      for connector in connectors:
         params=[]
         assert(isinstance(connector, autosar.component.AssemblyConnector))
         providePort = ws.find(connector.providerInstanceRef.portRef)
         if providePort is None:
            raise ValueError('invalid reference: ' + connector.providerInstanceRef.portRef)
         provideCompRef = self._createComponentRef(providePort.parent.ref, localvars)
         requirePort = ws.find(connector.requesterInstanceRef.portRef)
         if requirePort is None:
            raise ValueError('invalid reference: ' + connector.requesterInstanceRef.portRef)
         requireCompRef = self._createComponentRef(requirePort.parent.ref, localvars)
                  
         params.append(repr('%s/%s'%(provideCompRef,providePort.name)))
         params.append(repr('%s/%s'%(requireCompRef,requirePort.name)))
         lines.append('swc.createConnector(%s)'%(', '.join(params)))
      return lines
   
   def _writeDelegationConnectorsCode(self, connectors, localvars):
      lines=[]
      ws = localvars['ws']
      swc = localvars['swc']
      
      assert(ws is not None)
      for connector in connectors:
         params=[]
         assert(isinstance(connector, autosar.component.DelegationConnector))
         innerPort = ws.find(connector.innerPortInstanceRef.portRef)
         if innerPort is None:
            raise ValueError('invalid reference: ' + connector.innerPortInstanceRef.portRef)
         innerComponentRef = self._createComponentRef(innerPort.parent.ref, localvars)
         
         parts = autosar.base.splitRef(connector.outerPortRef.portRef)
         outerPort = swc.find(parts[-1])
         if outerPort is None or not isinstance(outerPort, autosar.component.Port):
            raise ValueError('no port with name "%s" found in Component %s'%(parts[-1], swc.ref))
         params.append(repr(outerPort.name))
         params.append(repr('%s/%s'%(innerComponentRef,innerPort.name)))         
         lines.append('swc.createConnector(%s)'%(', '.join(params)))
      return lines
