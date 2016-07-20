import autosar.datatype

def destXMLTag(obj):
   if isinstance(obj,autosar.datatype.IntegerDataType):
      return "INTEGER-TYPE"
   else:
      raise NotImplementedError(str(type(obj)))

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
      

class PackageWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
      self.dataTypeWriter = DataTypeWriter(version)
      self.constantWriter = ConstantWriter(version)
      if self.version == 3:
         self.switcher = {'ARRAY-TYPE': None,
                          'BOOLEAN-TYPE': None,
                          'IntegerDataType': self.dataTypeWriter.writeIntegerTypeXML,
                          'REAL-TYPE': None,
                          'RECORD-TYPE': None,
                          'STRING-TYPE': None,
                          'APPLICATION-SOFTWARE-COMPONENT-TYPE': None,
                          'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': None,
                          'INTERNAL-BEHAVIOR': None,
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
      else:
         raise NotImplementedError("AUTOSAR version not yet supported")
   
   def toXML(self,package):      
      lines=[]
      lines.extend(self.beginPackage(package.name))
      lines.append(self.indent("<ELEMENTS>",1))
      for elem in package.elements:
         #fullname=elem.__class__.__module__+'.'+elem.__class__.__name__
         #print(fullname)
         #writerFunc = self.switcher.get(fullname)
         writerFunc = self.switcher.get(elem.__class__.__name__)
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
         tag = destXMLTag(elem.findWS().find(elem.typeRef))
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),2))
         lines.append(self.indent('<VALUE>%d</VALUE>'%elem.value,2))
         lines.append(self.indent('</INTEGER-LITERAL>',1))
         lines.append('</VALUE>')
      return lines
