from autosar.writer.writer_base import WriterBase

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
