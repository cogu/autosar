from autosar.writer.writer_base import WriterBase
import autosar.constant

class ConstantWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeConstantXML(self,elem,package):
      lines = []
      assert(isinstance(elem,autosar.constant.Constant))
      lines.append('<CONSTANT-SPECIFICATION>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      lines.extend(self.indent(self.writeValueXML(elem.value),1))
      lines.append('</CONSTANT-SPECIFICATION>')
      return lines
   
   def writeValueXML(self,elem):
      lines=[]      
      lines.append('<VALUE>')
      lines.extend(self.indent(self.writeLiteralValueXML(elem),1))
      lines.append('</VALUE>')      
      return lines
   
   def writeLiteralValueXML(self,elem):
      if isinstance(elem,autosar.constant.IntegerValue):
         return self.writeIntegerLiteralXML(elem)
      elif isinstance(elem,autosar.constant.RecordValue):
         return self.writeRecordSpecificationXML(elem)
      elif isinstance(elem,autosar.constant.StringValue):
         return self.writeStringLiteralXML(elem)
      elif isinstance(elem,autosar.constant.BooleanValue):
         return self.writeBooleanLiteralXML(elem)
      elif isinstance(elem,autosar.constant.ArrayValue):
         return self.writeArraySpecificationXML(elem)
      else:
         raise NotImplementedError(type(elem))
   
   def writeIntegerLiteralXML(self,elem):
      assert(isinstance(elem,autosar.constant.IntegerValue))
      lines=[]
      lines.append('<INTEGER-LITERAL>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tag = elem.rootWS().find(elem.typeRef).tag(self.version)
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
      lines.append(self.indent('<VALUE>%d</VALUE>'%elem.value,1))
      lines.append('</INTEGER-LITERAL>')
      return lines
   
   def writeRecordSpecificationXML(self,elem):
      assert(isinstance(elem,autosar.constant.RecordValue))      
      lines=[]
      lines.append('<RECORD-SPECIFICATION>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tag = elem.rootWS().find(elem.typeRef).tag(self.version)
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
      if len(elem.elements)==0: lines.append('<ELEMENTS/>')
      else:
         lines.append(self.indent('<ELEMENTS>',1))
         for childElem in elem.elements:
            lines.extend(self.indent(self.writeLiteralValueXML(childElem),2))
         lines.append(self.indent('</ELEMENTS>',1))      
      lines.append('</RECORD-SPECIFICATION>')
      return lines

   def writeStringLiteralXML(self,elem):
      assert(isinstance(elem,autosar.constant.StringValue))
      lines=[]
      lines.append('<STRING-LITERAL>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tag = elem.rootWS().find(elem.typeRef).tag(self.version)
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
      lines.append(self.indent('<VALUE>%s</VALUE>'%elem.value,1))
      lines.append('</STRING-LITERAL>')
      return lines

   def writeBooleanLiteralXML(self,elem):
      assert(isinstance(elem,autosar.constant.BooleanValue))
      lines=[]
      lines.append('<BOOLEAN-LITERAL>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tag = elem.rootWS().find(elem.typeRef).tag(self.version)
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
      lines.append(self.indent('<VALUE>%s</VALUE>'%('true' if elem.value is True else 'false'),1))
      lines.append('</BOOLEAN-LITERAL>')
      return lines

   def writeArraySpecificationXML(self,elem):
      assert(isinstance(elem,autosar.constant.ArrayValue))
      lines=[]
      lines.append('<ARRAY-SPECIFICATION>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tag = elem.rootWS().find(elem.typeRef).tag(self.version)
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
      if len(elem.elements)==0: lines.append('<ELEMENTS/>')
      else:
         lines.append(self.indent('<ELEMENTS>',1))
         for childElem in elem.elements:
            lines.extend(self.indent(self.writeLiteralValueXML(childElem),2))
         lines.append(self.indent('</ELEMENTS>',1))      
     
      lines.append('</ARRAY-SPECIFICATION>')
      return lines
      