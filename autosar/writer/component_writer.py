from autosar.writer.writer_base import ElementWriter
import autosar.base
import autosar.workspace
import autosar.constant
from autosar.writer.behavior_writer import XMLBehaviorWriter

class XMLComponentTypeWriter(ElementWriter):
   def __init__(self,version, patch):
      super().__init__(version, patch)
      if version >= 4.0:
         self.behavior_writer=XMLBehaviorWriter(version, patch)

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {
                           'ApplicationSoftwareComponent': self.writeApplicationSoftwareComponentXML,
                           'ComplexDeviceDriverComponent': self.writeComplexDeviceDriverComponentXML,
                           'ServiceComponent': self.writeServiceComponentXML,
                           'SwcImplementation': self.writeSwcImplementationXML,
                           'CompositionComponent': self.writeCompositionComponentXML
         }
      elif self.version >= 4.0:
         self.switcher = {
                           'ApplicationSoftwareComponent': self.writeApplicationSoftwareComponentXML,
                           'SwcImplementation': self.writeSwcImplementationXML,                           
                           'CompositionComponent': self.writeCompositionComponentXML
         }
      else:
         switch.keys = {}

   def getSupportedXML(self):
      return self.switcher.keys()

   def getSupportedCode(self):
      return []

   def writeElementXML(self, elem):
      xmlWriteFunc = self.switcher.get(type(elem).__name__)
      if xmlWriteFunc is not None:
         return xmlWriteFunc(elem)
      else:
         return None
   
   def writeElementCode(self, elem, localvars):
      raise NotImplementedError('writeElementCode')

   def writeApplicationSoftwareComponentXML(self,swc):
      assert(isinstance(swc,autosar.component.ApplicationSoftwareComponent))
      return self._writeComponentXML(swc)

   def writeComplexDeviceDriverComponentXML(self,swc):
      assert(isinstance(swc,autosar.component.ComplexDeviceDriverComponent))
      return self._writeComponentXML(swc)

   def writeCompositionComponentXML(self,swc):
      assert(isinstance(swc,autosar.component.CompositionComponent))
      return self._writeComponentXML(swc)

   def writeServiceComponentXML(self,swc):
      assert(isinstance(swc,autosar.component.ServiceComponent))
      return self._writeComponentXML(swc)

   def _writeComponentXML(self, swc):
      lines=[]
      ws = swc.rootWS()
      assert(ws is not None)
      lines=[]
      lines.append('<%s>'%swc.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%swc.name,1))
      if isinstance(swc, autosar.component.ServiceComponent):
         lines.append(self.indent('<CATEGORY>ServiceComponent</CATEGORY>',1))
      lines.append(self.indent('<PORTS>',1))
      for port in swc.providePorts:
         lines.extend(self.indent(self._writeProvidePortXML(port),2))
      for port in swc.requirePorts:
         lines.extend(self.indent(self._writeRequirePortXML(port),2))
      lines.append(self.indent('</PORTS>',1))
      if (self.version >= 4.0) and (isinstance(swc, autosar.component.AtomicSoftwareComponent)) and (swc.behavior is not None):
         lines.append(self.indent('<INTERNAL-BEHAVIORS>',1))         
         lines.extend(self.indent(self.behavior_writer.writeInternalBehaviorXML(swc.behavior),2))
         lines.append(self.indent('</INTERNAL-BEHAVIORS>',1))
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
         if self.version<4.0:
            lines.append(self.indent('<REQUIRED-COM-SPECS></REQUIRED-COM-SPECS>',1))
         
      else:
         lines.append(self.indent('<REQUIRED-COM-SPECS>',1))
         if portInterface is None:
            raise ValueError("%s: invalid reference detected: '%s'"%(port.ref,port.portInterfaceRef))
         for comspec in port.comspec:
            if self.version>=4.0:
               if isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
                  lines.extend(self.indent(self._writeModeSwitchReceiverComSpecXML(ws, portInterface, comspec),2))
               elif isinstance(portInterface, autosar.portinterface.ParameterInterface):
                  lines.extend(self.indent(self._writeParameterRequireComSpecXML(port, portInterface, comspec),2))
               elif isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
                  dataElem=portInterface.find(comspec.name)
                  if dataElem is None:
                     raise ValueError("%s: invalid comspec name '%s'"%(port.ref, comspec.name))
                  lines.extend(self.indent(self._writeDataReceiverComSpecXML(ws, dataElem, comspec),2))
               elif isinstance(portInterface, autosar.portinterface.ClientServerInterface):
                  operation=portInterface.find(comspec.name)
                  if operation is None:
                     raise ValueError("%s: invalid comspec name '%s'"%(port.ref,comspec.name))
                  lines.extend(self.indent(self._writeOperationComSpec(operation),2))
               else:
                  raise NotImplementedError(str(type(portInterface)))
            else:
               if isinstance(portInterface, autosar.portinterface.ClientServerInterface):
                  operation=portInterface.find(comspec.name)
                  if operation is None:
                     raise ValueError("%s: invalid comspec name '%s'"%(port.ref,comspec.name))
                  lines.extend(self.indent(self._writeOperationComSpec(operationc),2))
               else:
                  dataElem=portInterface.find(comspec.name)
                  if dataElem is None:
                     raise ValueError("%s: invalid comspec name '%s'"%(port.ref, comspec.name))
                  lines.extend(self.indent(self._writeDataReceiverComSpecXML(ws, dataElem, comspec),2))
         lines.append(self.indent('</REQUIRED-COM-SPECS>',1))
      lines.append(self.indent('<REQUIRED-INTERFACE-TREF DEST="%s">%s</REQUIRED-INTERFACE-TREF>'%(portInterface.tag(self.version),portInterface.ref),1))
      lines.append('</R-PORT-PROTOTYPE>')
      return lines

   def _writeOperationComSpec(self, operation):
      lines = []
      lines.append('<CLIENT-COM-SPEC>')
      lines.append(self.indent('<OPERATION-REF DEST="%s">%s</OPERATION-REF>'%(operation.tag(self.version),operation.ref),1))
      lines.append('</CLIENT-COM-SPEC>')
      return lines
   
   def _writeDataReceiverComSpecXML(self, ws, dataElem, comspec):
      assert(isinstance(dataElem, autosar.portinterface.DataElement))
      lines = []
      if self.version<4.0:
         if dataElem.isQueued:                        
            lines.append('<QUEUED-RECEIVER-COM-SPEC>',)
            lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(dataElem.tag(self.version),dataElem.ref),1))
            lines.append(self.indent('<QUEUE-LENGTH>%d</QUEUE-LENGTH>'%(int(comspec.queueLength)),1))
            lines.append('</QUEUED-RECEIVER-COM-SPEC>')
         else:                        
            lines.append('<UNQUEUED-RECEIVER-COM-SPEC>')
            lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(dataElem.tag(self.version),dataElem.ref),1))
            lines.append(self.indent('<ALIVE-TIMEOUT>%d</ALIVE-TIMEOUT>'%(comspec.aliveTimeout),1))
            if comspec.initValueRef is not None:
               tag = ws.find(comspec.initValueRef).tag(self.version)
               lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(tag,comspec.initValueRef),1))
            lines.append('</UNQUEUED-RECEIVER-COM-SPEC>')
      else:
         if dataElem.isQueued:                        
            lines.append('<QUEUED-RECEIVER-COM-SPEC>')
            lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(dataElem.tag(self.version),dataElem.ref),1))
            lines.append(self.indent('<QUEUE-LENGTH>%d</QUEUE-LENGTH>'%(int(comspec.queueLength)),1))
            lines.append('</QUEUED-RECEIVER-COM-SPEC>')
         else:
            lines.append('<NONQUEUED-RECEIVER-COM-SPEC>')
            lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(dataElem.tag(self.version),dataElem.ref),1))
            lines.append(self.indent('<USES-END-TO-END-PROTECTION>false</USES-END-TO-END-PROTECTION>',1))

            lines.append(self.indent('<ALIVE-TIMEOUT>%d</ALIVE-TIMEOUT>'%(comspec.aliveTimeout),1))
            lines.append(self.indent('<ENABLE-UPDATE>false</ENABLE-UPDATE>',1))
            lines.append(self.indent('<FILTER>',1))
            lines.append(self.indent('<DATA-FILTER-TYPE>ALWAYS</DATA-FILTER-TYPE>',2))
            lines.append(self.indent('</FILTER>',1))
            lines.append(self.indent('<HANDLE-NEVER-RECEIVED>false</HANDLE-NEVER-RECEIVED>',1))
            if comspec.initValueRef is not None:
               lines.extend(self.indent(self._writeInitValueRefXML(ws, comspec.initValueRef),1))
            if comspec.initValue is not None:
               lines.append(self.indent('<INIT-VALUE>',1))
               lines.extend(self.indent(self.writeValueSpecificationXML(comspec.initValue),2))
               lines.append(self.indent('</INIT-VALUE>',1))
            lines.append('</NONQUEUED-RECEIVER-COM-SPEC>')
      return lines

   def _writeModeSwitchReceiverComSpecXML(self, ws, portInterface, comspec):
      lines = []
      lines.append('<MODE-SWITCH-RECEIVER-COM-SPEC>')
      lines.append(self.indent('<ENHANCED-MODE-API>%s</ENHANCED-MODE-API>'%('true' if comspec.enhancedMode else 'false'),1))
      lines.append(self.indent('<SUPPORTS-ASYNCHRONOUS-MODE-SWITCH>%s</SUPPORTS-ASYNCHRONOUS-MODE-SWITCH>'%('true' if comspec.supportAsync else 'false'),1))
      lines.append('</MODE-SWITCH-RECEIVER-COM-SPEC>')
      return lines
   
   def _writeParameterRequireComSpecXML(self, port, portInterface, comspec):
      lines = []
      parameter = portInterface.find(comspec.name)
      if parameter is None:
         raise ValueError('%s: invalid parameter reference name: %s'%(port.ref, comspec.name))
      lines.append('<PARAMETER-REQUIRE-COM-SPEC>')
      if comspec.initValue is not None:
         lines.append(self.indent('<INIT-VALUE>',1))
         lines.extend(self.indent(self.writeValueSpecificationXML(comspec.initValue),2))
         lines.append(self.indent('</INIT-VALUE>',1))
      lines.append(self.indent('<PARAMETER-REF DEST="%s">%s</PARAMETER-REF>'%(parameter.tag(self.version), parameter.ref),1))
      lines.append('</PARAMETER-REQUIRE-COM-SPEC>')
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
                     lines.append(self.indent('<QUEUED-SENDER-COM-SPEC>',2))
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),3))
                     lines.append(self.indent('<USES-END-TO-END-PROTECTION>false</USES-END-TO-END-PROTECTION>',3))                     
                     lines.append(self.indent('</QUEUED-SENDER-COM-SPEC>',2))
               else:
                  lines.extend(self.indent(self._writeUnqueuedSenderComSpecXML(ws, comspec, elem),2))
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

   def writeSwcImplementationXML(self,elem):
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
      name = 'Default' if self.version >= 4.0 else 'Code'
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%name,3))
      if self.version >= 4.0:
         lines.append(self.indent('<ARTIFACT-DESCRIPTORS>',3))
         lines.append(self.indent('<AUTOSAR-ENGINEERING-OBJECT>',4))
         lines.append(self.indent('<SHORT-LABEL>Default</SHORT-LABEL>',5))
         lines.append(self.indent('<CATEGORY>SWSRC</CATEGORY>',5))
         lines.append(self.indent('</AUTOSAR-ENGINEERING-OBJECT>',4))
         lines.append(self.indent('</ARTIFACT-DESCRIPTORS>',3))
      else:
         lines.append(self.indent('<TYPE>SRC</TYPE>',3))
      lines.append(self.indent('</CODE>',2))
      lines.append(self.indent('</CODE-DESCRIPTORS>',1))
      if self.version < 4.0:
         lines.append(self.indent('<BEHAVIOR-REF DEST="%s">%s</BEHAVIOR-REF>'%(behavior.tag(self.version),elem.behaviorRef),1))
      else:
         lines.append(self.indent('<BEHAVIOR-REF DEST="%s">%s</BEHAVIOR-REF>'%(behavior.tag(self.version),behavior.ref),1))
      lines.append('</SWC-IMPLEMENTATION>')
      return lines

   def _writeComponentsXML(self, ws, components):
      lines=[]
      if len(components)>0:
         lines.append('<COMPONENTS>')
         componentTag = 'SW-COMPONENT-PROTOTYPE' if self.version >= 4.0 else 'COMPONENT-PROTOTYPE'
         for component in components:
            swc = ws.find(component.typeRef)
            if swc is None:
               raise ValueError('Invalid reference: '+component.typeRef)
            lines.append(self.indent('<%s>'%componentTag,1))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%component.name,2))
            lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(swc.tag(self.version),swc.ref),2))
            lines.append(self.indent('</%s>'%componentTag,1))
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
         componentTag = 'CONTEXT-COMPONENT-REF' if self.version >= 4.0 else 'COMPONENT-PROTOTYPE-REF'
         portTag = 'TARGET-P-PORT-REF' if self.version >= 4.0 else 'P-PORT-PROTOTYPE-REF'
         lines.append(self.indent('<%s DEST="%s">%s</%s>'%(componentTag, providerComponent.tag(self.version), providerComponent.ref, componentTag), 2))
         lines.append(self.indent('<%s DEST="%s">%s</%s>'%(portTag, providePort.tag(self.version), providePort.ref, portTag), 2))
         lines.append(self.indent('</%s>'%connector.providerInstanceRef.tag(self.version), 1))
         lines.append(self.indent('<%s>'%connector.requesterInstanceRef.tag(self.version), 1))
         requesterComponent = ws.find(connector.requesterInstanceRef.componentRef)
         if requesterComponent is None:
            raise ValueError('invalid reference: ' +connector.requesterInstanceRef.componentRef)
         requirePort = ws.find(connector.requesterInstanceRef.portRef)
         if requirePort is None:
            raise ValueError('invalid reference: ' +connector.requesterInstanceRef.portRef)         
         portTag = 'TARGET-R-PORT-REF' if self.version >= 4.0 else 'R-PORT-PROTOTYPE-REF'
         lines.append(self.indent('<%s DEST="%s">%s</%s>'%(componentTag, requesterComponent.tag(self.version), requesterComponent.ref, componentTag), 2))
         lines.append(self.indent('<%s DEST="%s">%s</%s>'%(portTag, requirePort.tag(self.version), requirePort.ref, portTag), 2))
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
         if self.version >= 4.0:
            lines.extend(self.indent(self._writeInnerPortRefV4(innerComponent,innerPort),2))
         else:
            lines.extend(self.indent(self._writeInnerPortRefV3(innerComponent,innerPort),2))
         lines.append(self.indent('</%s>'%connector.innerPortInstanceRef.tag(self.version), 1))
         outerPort = ws.find(connector.outerPortRef.portRef)
         if outerPort is None:
            raise ValueError('invalid reference: ' +connector.outerPortRef.portRef)
         lines.append(self.indent('<OUTER-PORT-REF DEST="%s">%s</OUTER-PORT-REF>'%(outerPort.tag(self.version), outerPort.ref), 1))
         lines.append('</%s>'%connector.tag(self.version))
      return lines

   def _writeInnerPortRefV3(self, innerComponent, innerPort):
      lines = []
      lines.append('<COMPONENT-PROTOTYPE-REF DEST="%s">%s</COMPONENT-PROTOTYPE-REF>'%(innerComponent.tag(self.version), innerComponent.ref))
      lines.append('<PORT-PROTOTYPE-REF DEST="%s">%s</PORT-PROTOTYPE-REF>'%(innerPort.tag(self.version), innerPort.ref))
      return lines

   def _writeInnerPortRefV4(self, innerComponent, innerPort):
      lines = []
      if isinstance(innerPort, autosar.component.RequirePort):
         outerTag = 'R-PORT-IN-COMPOSITION-INSTANCE-REF'
         innerTag = 'TARGET-R-PORT-REF'
      else:
         outerTag = 'P-PORT-IN-COMPOSITION-INSTANCE-REF'
         innerTag = 'TARGET-P-PORT-REF'
      lines.append('<%s>'%outerTag)
      lines.append(self.indent('<CONTEXT-COMPONENT-REF DEST="%s">%s</CONTEXT-COMPONENT-REF>'%(innerComponent.tag(self.version), innerComponent.ref), 1))
      lines.append(self.indent('<%s DEST="%s">%s</%s>'%(innerTag, innerPort.tag(self.version), innerPort.ref, innerTag), 1))
      lines.append('</%s>'%outerTag)
      return lines

   def _writeUnqueuedSenderComSpecXML(self, ws, comspec, elem):
      lines=[]
      if self.version<4.0:
         lines.append('<UNQUEUED-SENDER-COM-SPEC>')
         lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),1))
         if isinstance(comspec.canInvalidate,bool):
            lines.append(self.indent('<CAN-INVALIDATE>%s</CAN-INVALIDATE>'%('true' if comspec.canInvalidate else 'false'),1))
         if comspec.initValueRef is not None:
            tag = ws.find(comspec.initValueRef).tag(self.version)
            lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(tag,comspec.initValueRef),1))
         lines.append('</UNQUEUED-SENDER-COM-SPEC>')
      else:
         lines.append('<NONQUEUED-SENDER-COM-SPEC>')
         lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag(self.version),elem.ref),1))
         lines.append(self.indent('<USES-END-TO-END-PROTECTION>false</USES-END-TO-END-PROTECTION>',1))
         if comspec.initValueRef is not None:
            lines.extend(self.indent(self._writeInitValueRefXML(ws, comspec.initValueRef),1))
         if comspec.initValue is not None:
            lines.append(self.indent('<INIT-VALUE>',1))
            lines.extend(self.indent(self.writeValueSpecificationXML(comspec.initValue),2))
            lines.append(self.indent('</INIT-VALUE>',1))
         lines.append('</NONQUEUED-SENDER-COM-SPEC>')
      return lines
   
   def _writeInitValueRefXML(self, ws, initValueRef):
      lines = []
      constant = ws.find(initValueRef)
      if constant is None:
         raise ValueError('Invalid constant reference: %s'%initValueRef)
      lines.append('<INIT-VALUE>')
      lines.append(self.indent('<CONSTANT-REFERENCE>',1))
      lines.append(self.indent('<CONSTANT-REF DEST="%s">%s</CONSTANT-REF>'%(constant.tag(self.version),constant.ref),2))
      lines.append(self.indent('</CONSTANT-REFERENCE>',1))
      lines.append('</INIT-VALUE>')
      return lines

class CodeComponentTypeWriter(ElementWriter):
   def __init__(self,version, patch):
      super().__init__(version, patch)

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {
                          'ApplicationSoftwareComponent': self.writeApplicationSoftwareComponentCode,
                          'ComplexDeviceDriverComponent': self.writeComplexDeviceDriverComponentCode,
                          'ServiceComponent': self.writeServiceComponentCode,
                          'ParameterComponent': self.writeParameterComponentCode,                          
                          'SwcImplementation': self.writeSwcImplementationCode,
                          'CompositionComponent': self.writeCompositionComponentCode,
         }
      elif self.version >= 4.0:
         self.switcher = {
         }
      else:
         switch.keys = {}

   def getSupportedXML(self):
      return []

   def getSupportedCode(self):
      return self.switcher.keys()

   def writeElementXML(self, elem):
      raise NotImplementedError('writeElementXML')
   
   def writeElementCode(self, elem, localvars):
      codeWriteFunc = self.switcher.get(type(elem).__name__)
      if codeWriteFunc is not None:
         return codeWriteFunc(elem, localvars)
      else:
         return None

   def writeApplicationSoftwareComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createApplicationSoftwareComponent', localvars)

   def writeComplexDeviceDriverComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createComplexDeviceDriverComponent', localvars)

   def writeServiceComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createServiceComponent', localvars)

   def writeCompositionComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createCompositionComponent', localvars)

   def writeParameterComponentCode(self, swc, localvars):
      return self._writeComponentCode(swc, 'createParameterComponent', localvars)


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
         if isinstance(portInterface,autosar.portinterface.PortInterface):
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