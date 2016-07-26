import autosar.datatype
import autosar.portinterface
import autosar.behavior
from autosar.base import splitref

class WriterBase(object):
   def __init__(self,version=3):
      self.version=version
      self.lines=[]
      self.indentChar='\t'
      
   def indent(self,lines,indent):
      if isinstance(lines,list):
         return ['%s%s'%(self.indentChar*indent,x) for x in lines]
      elif isinstance(lines,str):
         return '%s%s'%(self.indentChar*indent,lines)
      else:
         raise NotImplementedError(type(lines))
   
   def beginFile(self):
      lines=[]
      lines.append('<?xml version="1.0" encoding="UTF-8"?>')
      if self.version == 3:
         lines.append('<AUTOSAR xsi:schemaLocation="http://autosar.org/3.0.2 autosar_302_ext.xsd" xmlns="http://autosar.org/3.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
         lines.append(self.indentChar+'<TOP-LEVEL-PACKAGES>')
      return lines
   
   def endFile(self):
      lines=[]
      if self.version == 3:
         lines.append(self.indentChar+'</TOP-LEVEL-PACKAGES>')
      else:
         lines.append(self.indentChar+'</AR-PACKAGES>')
      lines.append('</AUTOSAR>')
      return lines
   
   def beginPackage(self, name,indent=None):
      lines = []
      lines.append('<AR-PACKAGE>')
      lines.append(self.indentChar+'<SHORT-NAME>%s</SHORT-NAME>'%name)
      return lines
   
   def endPackage(self,indent=None):
      lines = []
      lines.append('</AR-PACKAGE>')
      return lines

class WorkspaceWriter(WriterBase):
   def __init__(self,version=3):
      super().__init__(version)
      self.packageWriter=PackageWriter(self.version)
   
   def saveXML(self,fp,ws,packages=None):
      fp.write(self.toXML(ws,packages))

   def toXML(self,ws,packages=None):      
      lines=self.beginFile()
      result='\n'.join(lines)+'\n'
      for package in ws.packages:
         if (isinstance(packages,list) and package.name in packages) or (packages is None):
            lines=self.indent(self.packageWriter.toXML(package),2)
            result+='\n'.join(lines)+'\n'
      lines=self.endFile()
      return result+'\n'.join(lines)+'\n'
   
   def toCode(self,ws,packages=None):
      lines=['import autosar as ar','','ws=ar.workspace()']
      result='\n'.join(lines)+'\n'
      for package in ws.packages:
         if (isinstance(packages,list) and package.name in packages) or (packages is None):
            lines=self.packageWriter.toCode(package)
            result+='\n'.join(lines)+'\n'
      return result
      
      

class PackageWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
      self.dataTypeWriter = DataTypeWriter(version)
      self.constantWriter = ConstantWriter(version)
      self.componentTypeWriter = ComponentTypeWriter(version)
      self.behaviorWriter = BehaviorWriter(version)
      if self.version >= 3.0:
         self.switcherXML = {'ARRAY-TYPE': None,
                          'BOOLEAN-TYPE': None,
                          'IntegerDataType': self.dataTypeWriter.writeIntegerTypeXML,
                          'REAL-TYPE': None,
                          'RECORD-TYPE': None,
                          'STRING-TYPE': None,
                          'ApplicationSoftwareComponent': self.componentTypeWriter.writeApplicationSoftwareComponentXML,
                          'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': None,
                          'InternalBehavior': self.behaviorWriter.writeInternalBehaviorXML,
                          'SWC-IMPLEMENTATION': None,
                          'CompuMethodConst': self.dataTypeWriter.writeCompuMethodXML,
                          'UNIT': None,
                          'SW-ADDR-METHOD': None,
                          'MODE-DECLARATION-GROUP': None,
                          'SENDER-RECEIVER-INTERFACE': None,
                          'CALPRM-INTERFACE': None,
                          'CLIENT-SERVER-INTERFACE': None,
                          'Constant': self.constantWriter.writeConstantXML,
                          'COMPOSITION-TYPE': None,
                          'SYSTEM-SIGNAL': None,
                          'SYSTEM': None
                          }
         self.switcherCode = {'ARRAY-TYPE': None,
                          'BOOLEAN-TYPE': None,
                          'IntegerDataType': None,
                          'REAL-TYPE': None,
                          'RECORD-TYPE': None,
                          'STRING-TYPE': None,
                          'ApplicationSoftwareComponent': self.componentTypeWriter.writeApplicationSoftwareComponentCode,
                          'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': None,
                          'InternalBehavior': None,
                          'SWC-IMPLEMENTATION': None,
                          'CompuMethodConst': None,
                          'UNIT': None,
                          'SW-ADDR-METHOD': None,
                          'MODE-DECLARATION-GROUP': None,
                          'SENDER-RECEIVER-INTERFACE': None,
                          'CALPRM-INTERFACE': None,
                          'CLIENT-SERVER-INTERFACE': None,
                          'Constant': None,
                          'COMPOSITION-TYPE': None,
                          'SYSTEM-SIGNAL': None,
                          'SYSTEM': None
                          }
      else:
         raise NotImplementedError("AUTOSAR version not yet supported")
   
   def toXML(self,package):      
      lines=[]
      lines.extend(self.beginPackage(package.name))
      lines.append(self.indent("<ELEMENTS>",1))
      for elem in package.elements:
         writerFunc = self.switcherXML.get(elem.__class__.__name__)
         if writerFunc is not None:            
            lines.extend(self.indent(writerFunc(elem),2))
         else:
            print("skipped: %s"%str(type(elem)))
      lines.append(self.indent("</ELEMENTS>",1))
      if len(package.subPackages)>0:
         lines.append(self.indent("<SUB-PACKAGES>",1))
         for subPackage in package.subPackages:
            lines.extend(self.indent(self.toXML(subPackage),2))
         lines.append(self.indent("</SUB-PACKAGES>",1))
      lines.extend(self.endPackage())
      return lines
   
   def toCode(self,package):
      lines=[]
      lines.append("ws.append(ar.Package('%s'))"%package.name)
      for elem in package.elements:
         writerFunc = self.switcherCode.get(elem.__class__.__name__)
         if writerFunc is not None:
            lines.extend(writerFunc(elem,package))
         else:
            raise NotImplementedError(type(elem))
      return lines

class DataTypeWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeIntegerTypeXML(self,elem):
      assert isinstance(elem,autosar.datatype.IntegerDataType)
      lines = ["<INTEGER-TYPE>"]
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.compuMethodRef is not None:
         lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
         lines.append(self.indent('<COMPU-METHOD-REF DEST="COMPU-METHOD">%s</COMPU-METHOD-REF>'%elem.compuMethodRef,2))
         lines.append(self.indent("</SW-DATA-DEF-PROPS>",1))
      lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="CLOSED">%d</LOWER-LIMIT>'%elem.minval,1))
      lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="CLOSED">%d</UPPER-LIMIT>'%elem.maxval,1))
      lines.append('</INTEGER-TYPE>')
      return lines
   
   def writeCompuMethodXML(self,elem):
      lines=[]
      lines.append('<COMPU-METHOD>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if isinstance(elem,autosar.datatype.CompuMethodConst):
         lines.extend(self.indent(self.writeCompuMethodConstXml(elem),1))
      lines.append('</COMPU-METHOD>')
      return lines
   
   def writeCompuMethodConstXml(self,item):
      lines=[]
      lines.append('<COMPU-INTERNAL-TO-PHYS>')
      lines.append(self.indent('<COMPU-SCALES>',1))
      for elem in item.elements:
         lines.append(self.indent('<COMPU-SCALE>',2))
         lines.append(self.indent('<LOWER-LIMIT>%d</LOWER-LIMIT>'%elem.minval,3))
         lines.append(self.indent('<UPPER-LIMIT>%d</UPPER-LIMIT>'%elem.maxval,3))
         lines.append(self.indent('<COMPU-CONST>',3))
         lines.append(self.indent('<VT>%s</VT>'%elem.textval,4))
         lines.append(self.indent('</COMPU-CONST>',3))
         lines.append(self.indent('</COMPU-SCALE>',2))
      lines.append(self.indent('</COMPU-SCALES>',1))
      lines.append('</COMPU-INTERNAL-TO-PHYS>')
      return lines

class ConstantWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeConstantXML(self,elem):
      lines = []
      assert(isinstance(elem,autosar.constant.Constant))
      lines.append('<CONSTANT-SPECIFICATION>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      lines.extend(self.indent(self.writeValueXML(elem.value),1))
      lines.append('</CONSTANT-SPECIFICATION>')
      return lines
   
   def writeValueXML(self,elem):
      lines=[]
      if isinstance(elem,autosar.constant.IntegerValue):
         lines.append('<VALUE>')
         lines.append(self.indent('<INTEGER-LITERAL>',1))
         lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,2))
         tag = elem.findWS().find(elem.typeRef).tag
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),2))
         lines.append(self.indent('<VALUE>%d</VALUE>'%elem.value,2))
         lines.append(self.indent('</INTEGER-LITERAL>',1))
         lines.append('</VALUE>')
      return lines

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
      ws=port.findWS()
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
      ws=port.findWS()
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
      lines.append("print(swc.name)")
      return lines

class BehaviorWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeInternalBehaviorXML(self,elem):
      assert(isinstance(elem,autosar.behavior.InternalBehavior))
      lines=[]
      ws = elem.findWS()
      assert(ws is not None)
      lines.append('<%s>'%elem.tag)
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      componentType=ws.find(elem.componentRef)
      assert(componentType is not None)
      lines.append(self.indent('<COMPONENT-REF DEST="%s">%s</COMPONENT-REF>'%(componentType.tag,componentType.ref),1))      
      if len(elem.runnables)>0:
         lines.append(self.indent('<RUNNABLES>',1))
         for runnable in elem.runnables:
            lines.extend(self.indent(self.writeRunnableXML(runnable),2))
         lines.append(self.indent('</RUNNABLES>',1))
      lines.append(self.indent('<SUPPORTS-MULTIPLE-INSTANTIATION>%s</SUPPORTS-MULTIPLE-INSTANTIATION>'%('true' if elem.multipleInstance else 'false'),1))
      lines.append('</%s>'%elem.tag)
      return lines
   
   def writeRunnableXML(self,runnable):
      ws=runnable.findWS()
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
            assert(port is not dataElement)            
            lines.append(self.indent('<R-PORT-PROTOTYPE-REF DEST="%s">%s</R-PORT-PROTOTYPE-REF>'%(port.tag,port.ref),4))
            lines.append(self.indent('<DATA-ELEMENT-PROTOTYPE-REF DEST="%s">%s</DATA-ELEMENT-PROTOTYPE-REF>'%(dataElement.tag,dataElement.ref),4))
            lines.append(self.indent('</DATA-ELEMENT-IREF>',3))
            lines.append(self.indent('</DATA-RECEIVE-POINT>',2))
         lines.append(self.indent('</DATA-RECEIVE-POINTS>',1))
      lines.append(self.indent('<SYMBOL>%s</SYMBOL>'%runnable.symbol,1))
      lines.append('</RUNNABLE-ENTITY>')
      return lines
   


