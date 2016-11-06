from autosar.writer.writer_base import WriterBase
import autosar.datatype

class DataTypeWriter(WriterBase):
   def __init__(self,version):
      super().__init__(version)
   
   def writeIntegerTypeXML(self,elem,package):
      assert isinstance(elem,autosar.datatype.IntegerDataType)
      lines = ["<%s>"%elem.tag(self.version)]
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      if elem.compuMethodRef is not None:
         lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
         lines.append(self.indent('<COMPU-METHOD-REF DEST="COMPU-METHOD">%s</COMPU-METHOD-REF>'%elem.compuMethodRef,2))
         lines.append(self.indent("</SW-DATA-DEF-PROPS>",1))
      lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="CLOSED">%d</LOWER-LIMIT>'%elem.minval,1))
      lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="CLOSED">%d</UPPER-LIMIT>'%elem.maxval,1))
      lines.append('</%s>'%elem.tag(self.version))
      return lines
   
   def writeRecordDataTypeXML(self,elem,package):
      assert(isinstance(elem,autosar.datatype.RecordDataType))
      ws=elem.rootWS()
      assert(isinstance(ws,autosar.Workspace))
      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      lines.append(self.indent('<ELEMENTS>',1))
      for childElem in elem.elements:
         lines.append(self.indent('<RECORD-ELEMENT>',2))
         lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%childElem.name,3))         
         dataType=ws.find(childElem.typeRef)
         assert(dataType is not None)
         lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(dataType.tag(self.version),dataType.ref),3))
         lines.append(self.indent('</RECORD-ELEMENT>',2))
      
      lines.append(self.indent('</ELEMENTS>',1))      				
      lines.append('</%s>'%elem.tag(self.version))
      return lines
   
   def writeCompuMethodXML(self,elem,package):
      lines=[]
      lines.append('<COMPU-METHOD>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if isinstance(elem,autosar.datatype.CompuMethodConst):
         lines.extend(self.indent(self.writeCompuMethodConstXml(elem),1))
      else:
         if elem.unitRef is not None:
            lines.append(self.indent('<UNIT-REF DEST="UNIT">%s</UNIT-REF>'%elem.unitRef,1))
         lines.extend(self.indent(self.writeCompuMethodRationalXml(elem),1))
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
   
   def writeCompuMethodRationalXml(self,item):
      lines=[]
      lines.append('<COMPU-INTERNAL-TO-PHYS>')
      lines.append(self.indent('<COMPU-SCALES>',1))
      for elem in item.elements:
         lines.append(self.indent('<COMPU-SCALE>',2))
         lines.append(self.indent('<COMPU-RATIONAL-COEFFS>',3))
         lines.append(self.indent('<COMPU-NUMERATOR>',4))         
         lines.append(self.indent('<V>%s</V>'%elem.offset,5))
         lines.append(self.indent('<V>%s</V>'%elem.numerator,5))
         lines.append(self.indent('</COMPU-NUMERATOR>',4))
         lines.append(self.indent('<COMPU-DENOMINATOR>',4))
         lines.append(self.indent('<V>%s</V>'%elem.denominator,5))
         lines.append(self.indent('</COMPU-DENOMINATOR>',4))
         lines.append(self.indent('</COMPU-RATIONAL-COEFFS>',3))
         lines.append(self.indent('</COMPU-SCALE>',2))
      lines.append(self.indent('</COMPU-SCALES>',1))
      lines.append('</COMPU-INTERNAL-TO-PHYS>')
      return lines

   def writeDataTypeUnitElementXML(self, elem,package):
      lines=[]
      lines.append('<UNIT>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      lines.append(self.indent('<DISPLAY-NAME>%s</DISPLAY-NAME>'%elem.displayName,1))
      lines.append('</UNIT>')
      return lines
   
   def writeArrayDataTypeXml(self, elem,package):
      assert(isinstance(elem,autosar.datatype.ArrayDataType))
      ws=elem.rootWS()
      assert(isinstance(ws,autosar.Workspace))

      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      lines.append(self.indent('<ELEMENT>',1))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,2))
      dataType=ws.find(elem.typeRef)
      assert(dataType is not None)
      lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(dataType.tag(self.version),dataType.ref),2))
      lines.append(self.indent('<MAX-NUMBER-OF-ELEMENTS>%d</MAX-NUMBER-OF-ELEMENTS>'%elem.length,2))
      lines.append(self.indent('</ELEMENT>',1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines
   
   def writeBooleanDataTypeXml(self, elem,package):
      assert(isinstance(elem,autosar.datatype.BooleanDataType))
      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines
   
   def writeRealDataTypeXML(self, elem,package):
      assert(isinstance(elem,autosar.datatype.RealDataType))
      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))      
      if elem.minvalType=="INFINITE":
         lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="INFINITE"></LOWER-LIMIT>',1))
      else:
         lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="%s">%s</LOWER-LIMIT>'%(elem.minvalType,elem.minval),1))
      if elem.maxvalType=="INFINITE":
         lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="INFINITE"></UPPER-LIMIT>',1))
      else:
         lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="%s">%s</UPPER-LIMIT>'%(elem.maxvalType,elem.maxval),1))
      lines.append(self.indent('<ALLOW-NAN>%s</ALLOW-NAN>'%('true' if elem.hasNaN else 'false'),1))
      lines.append(self.indent('<ENCODING>%s</ENCODING>'%elem.encoding,1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines
   
   def writeStringTypeXml(self, elem, package):
      assert(isinstance(elem,autosar.datatype.StringDataType))
      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      lines.append(self.indent('<ENCODING>%s</ENCODING>'%elem.encoding,1))
      lines.append(self.indent('<MAX-NUMBER-OF-CHARS>%d</MAX-NUMBER-OF-CHARS>'%elem.length,1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines
