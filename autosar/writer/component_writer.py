from autosar.writer.writer_base import WriterBase
import autosar.base
import autosar.workspace
import autosar.constant

class ComponentTypeWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeApplicationSoftwareComponentXML(self,swc,package):
      lines=[]
      assert(isinstance(swc,autosar.component.ApplicationSoftwareComponent))
      lines.append('<APPLICATION-SOFTWARE-COMPONENT-TYPE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%swc.name,1))
      lines.append(self.indent('<PORTS>',1))
      for port in swc.providePorts:
         lines.extend(self.indent(self.writeProvidePortXML(port),2))
      for port in swc.requirePorts:
         lines.extend(self.indent(self.writeRequirePortXML(port),2))
      lines.append(self.indent('</PORTS>',1))
      lines.append('</APPLICATION-SOFTWARE-COMPONENT-TYPE>')
      return lines
   
   def writeRequirePortXML(self, port):
      lines=[]
      assert(port.ref is not None)
      ws=port.rootWS()
      assert(ws is not None)
      portInterface=ws.find(port.portInterfaceRef)
      lines.append('<R-PORT-PROTOTYPE>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%port.name,1))
      if len(port.comspec)==0:
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
   
   def writeProvidePortXML(self, port):
      lines=[]
      assert(port.ref is not None)
      ws=port.rootWS()
      assert(ws is not None)
      portInterface=ws.find(port.portInterfaceRef)
      lines.append('<%s>'%port.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%port.name,1))
      if len(port.comspec)==0:
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
   
   
   def writeApplicationSoftwareComponentCode(self, swc, localvars):
      lines=[]
      package=localvars['package']      
      lines.append("swc = %s.createApplicationSoftwareComponent('%s')"%('package', swc.name))
      localvars['swc']=swc
      if len(swc.providePorts)>0:
         lines.extend(self.writeSWCProvidePortsCode(swc))
      if len(swc.requirePorts)>0:
         lines.extend(self.writeSWCRequirePortsCode(swc))      
      return lines
   
   def writeSWCProvidePortsCode(self,swc):
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

   def writeSWCRequirePortsCode(self,swc):
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
   
   def writeSwcImplementationCode(self, elem, localvars):
      return []
   