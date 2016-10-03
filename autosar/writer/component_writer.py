from autosar.writer.writer_base import WriterBase
from autosar.base import splitRef
import autosar.workspace


class ComponentTypeWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeApplicationSoftwareComponentXML(self,swc):
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
                     lines.append(self.indent('</QUEUED-RECEIVER-COM-SPEC>',2))
               else:
                  if self.version<4.0:
                     lines.append(self.indent('<UNQUEUED-RECEIVER-COM-SPEC>',2))
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag,elem.ref),3))
                     lines.append(self.indent('<ALIVE-TIMEOUT>%d</ALIVE-TIMEOUT>'%(comspec.aliveTimeout),3))
                     if comspec.initValueRef is not None:
                        tag = ws.find(comspec.initValueRef).tag
                        lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(tag,comspec.initValueRef),3))
                     lines.append(self.indent('</UNQUEUED-RECEIVER-COM-SPEC>',2))
            else:
               raise NotImplementedError(str(type(elem)))
         lines.append(self.indent('</REQUIRED-COM-SPECS>',1))
      lines.append(self.indent('<REQUIRED-INTERFACE-TREF DEST="%s">%s</REQUIRED-INTERFACE-TREF>'%(portInterface.tag,portInterface.ref),1))
      lines.append('</R-PORT-PROTOTYPE>')
      return lines   
   
   def writeProvidePortXML(self, port):
      lines=[]
      assert(port.ref is not None)
      ws=port.rootWS()
      assert(ws is not None)
      portInterface=ws.find(port.portInterfaceRef)
      lines.append('<%s>'%port.tag)
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
                     lines.append(self.indent('</QUEUED-SENDER-COM-SPEC>',2))
               else:
                  if self.version<4.0:
                     lines.append(self.indent('<UNQUEUED-SENDER-COM-SPEC>',2))                  
                     lines.append(self.indent('<DATA-ELEMENT-REF DEST="%s">%s</DATA-ELEMENT-REF>'%(elem.tag,elem.ref),3))
                     if isinstance(comspec.canInvalidate,bool):
                        lines.append(self.indent('<CAN-INVALIDATE>%s</CAN-INVALIDATE>'%('true' if comspec.canInvalidate else 'false'),3))                     
                     if comspec.initValueRef is not None:
                        tag = ws.find(comspec.initValueRef).tag
                        lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(tag,comspec.initValueRef),3))                  
                     lines.append(self.indent('</UNQUEUED-SENDER-COM-SPEC>',2))
            else:
               raise NotImplementedError(str(type(elem)))
         lines.append(self.indent('</PROVIDED-COM-SPECS>',1))      
      lines.append(self.indent('<PROVIDED-INTERFACE-TREF DEST="%s">%s</PROVIDED-INTERFACE-TREF>'%(portInterface.tag,portInterface.ref),1))
      lines.append('</%s>'%port.tag)      
      return lines
   
   
   def writeApplicationSoftwareComponentCode(self,swc,package):
      lines=[]
      lines.append("ws['%s'].append(ar.ApplicationSoftwareComponent('%s'))"%(package.name,swc.name))
      lines.append("swc=ws['%s/%s']"%(package.name,swc.name))
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
         args=[]
         args.append("'%s'"%port.name)
         portInterface=ws.find(port.portInterfaceRef)
         assert(portInterface is not None)
         if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
            args.append("'%s'"%port.portInterfaceRef)
            if len(port.comspec)>0:
               if len(port.comspec)==1:
                  comspec=port.comspec[0]
                  if comspec.initValueRef is not None:
                     tmp=splitRef(comspec.initValueRef)
                     if len(tmp)==3:
                        valueRef='/'+'/'.join(tmp[:-1])
                     else:
                        valueRef=comspec.initValueRef
                     args.append("initValueRef='%s'"%valueRef)
               else:
                  raise NotImplementedError('multiple comspecs not yet supported')                        
            lines.append('swc.createProvidePort(%s)'%(','.join(args)))
         else:
            raise NotImplementedError(type(portInterface))
      return lines

   def writeSWCRequirePortsCode(self,swc):
      lines=[]
      ws=swc.rootWS()
      assert(isinstance(ws,autosar.Workspace))
      for port in swc.requirePorts:
         args=[]
         args.append("'%s'"%port.name)
         portInterface=ws.find(port.portInterfaceRef)
         assert(portInterface is not None)
         if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
            args.append("'%s'"%port.portInterfaceRef)
            if len(port.comspec)>0:
               if len(port.comspec)==1:
                  comspec=port.comspec[0]
                  if comspec.initValueRef is not None:
                     tmp=splitRef(comspec.initValueRef)
                     if len(tmp)==3:
                        valueRef='/'+'/'.join(tmp[:-1])
                     else:
                        valueRef=comspec.initValueRef
                     args.append("initValueRef='%s'"%valueRef)
                  if comspec.aliveTimeout is not None:
                     args.append("aliveTimeout=%d"%int(comspec.aliveTimeout))
               else:
                  raise NotImplementedError('multiple comspecs not yet supported')                        
            lines.append('swc.createRequirePort(%s)'%(','.join(args)))
         else:
            raise NotImplementedError(type(portInterface))
      return lines
