from autosar.writer.writer_base import WriterBase
import autosar.datatype

class DataTypeWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeIntegerTypeXML(self,elem):
      assert isinstance(elem,autosar.datatype.IntegerDataType)
      lines = ["<%s>"%elem.tag]
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.compuMethodRef is not None:
         lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
         lines.append(self.indent('<COMPU-METHOD-REF DEST="COMPU-METHOD">%s</COMPU-METHOD-REF>'%elem.compuMethodRef,2))
         lines.append(self.indent("</SW-DATA-DEF-PROPS>",1))
      lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="CLOSED">%d</LOWER-LIMIT>'%elem.minval,1))
      lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="CLOSED">%d</UPPER-LIMIT>'%elem.maxval,1))
      lines.append('</%s>'%elem.tag)
      return lines
   
   def writeRecordDataTypeXML(self,elem):
      assert(isinstance(elem,autosar.datatype.RecordDataType))
      ws=elem.rootWS()
      assert(isinstance(ws,autosar.Workspace))
      lines=[]
      lines.append("<%s>"%elem.tag)
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      lines.append(self.indent('<ELEMENTS>',1))
      for childElem in elem.elements:
         lines.append(self.indent('<RECORD-ELEMENT>',2))
         lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%childElem.name,3))         
         dataType=ws.find(childElem.typeRef)
         assert(dataType is not None)
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(dataType.tag,dataType.name),3))
         lines.append(self.indent('</RECORD-ELEMENT>',2))
      
      lines.append(self.indent('</ELEMENTS>',1))      				
      lines.append('</%s>'%elem.tag)
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
