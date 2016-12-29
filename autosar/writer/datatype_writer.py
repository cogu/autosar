from autosar.writer.writer_base import WriterBase
import autosar.datatype
from fractions import Fraction

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
      lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="%s">%d</LOWER-LIMIT>'%(elem.minValType, elem.minVal),1))
      lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="%s">%d</UPPER-LIMIT>'%(elem.maxValType, elem.maxVal),1))
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
         dataType=ws.find(childElem.typeRef, role='DataType')
         if dataType is None:
            raise ValueError('invalid reference: '+childElem.typeRef)
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
         lines.append(self.indent('<LOWER-LIMIT>%d</LOWER-LIMIT>'%elem.lowerLimit,3))
         lines.append(self.indent('<UPPER-LIMIT>%d</UPPER-LIMIT>'%elem.upperLimit,3))
         lines.append(self.indent('<COMPU-CONST>',3))
         lines.append(self.indent('<VT>%s</VT>'%elem.textValue,4))
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
      if dataType is None: raise ValueError('invalid reference: '+elem.typeRef)
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
      if elem.minValType=="INFINITE":
         lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="INFINITE"></LOWER-LIMIT>',1))
      else:
         lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0}">{1:f}</LOWER-LIMIT>'.format(elem.minValType,elem.minVal),1))
      if elem.maxValType=="INFINITE":
         lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="INFINITE"></UPPER-LIMIT>',1))
      else:
         lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0.maxValType}">{0.maxVal:f}</UPPER-LIMIT>'.format(elem),1))
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
   
   ### Code Generators
   
   def writeArrayDataTypeCode(self, dataType, localvars):
      assert(isinstance(dataType,autosar.datatype.ArrayDataType))
      lines=[]
      ws=localvars['ws']
      params=[repr(dataType.name)]
      childType = ws.find(dataType.typeRef)
      if childType is None:
         raise ValueError('invalid reference: '+dataType.typeRef)
      if ws.roles['DataType'] is not None:
         params.append(repr(childType.name))
      else:
         params.append(repr(childType.ref))
      params.append(str(dataType.length))
      
      if dataType.adminData is not None:
         param = self.writeAdminDataCode(dataType.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
      if hasattr(dataType, 'desc'):         
         lines.append('dataType=package.createArrayDataType(%s)'%(', '.join(params)))
         lines.append('dataType.desc = """%s"""'%dataType.desc)
      else:
         lines.append('package.createArrayDataType(%s)'%(', '.join(params)))
      return lines
      
   def writeBooleanDataTypeCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']      
      #name
      params=[repr(dataType.name)]
      if hasattr(dataType, 'desc'):
         lines.append('dataType=package.createBooleanDataType(%s)'%(', '.join(params)))
         lines.append('dataType.desc = """%s"""'%dataType.desc)
      else:
         lines.append('package.createBooleanDataType(%s)'%(', '.join(params)))
      return lines

   def writeIntegerTypeCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']
      params=[repr(dataType.name)]
      
      if dataType.compuMethodRef is not None:
         compuMethod = ws.find(dataType.compuMethodRef)
         if compuMethod is None:
            raise ValueError('invalid reference: '+dataType.compuMethodRef)         
         if isinstance(compuMethod, autosar.datatype.CompuMethodConst):
            isUnconventionalType=False
            if (dataType.minVal != 0) or (dataType.maxVal != (len(compuMethod.elements)-1)):
               isUnconventionalType=True               
            else:
               params2=[]
               index=0
               for element in compuMethod.elements:
                  if isinstance(element, autosar.datatype.CompuConstElement):
                     if (element.lowerLimit==index) and (element.upperLimit==index):
                        params2.append(repr(element.textValue))
                     else:
                        isUnconventionalType=True
                        break
                  else:
                     raise ValueError('unsupported value found of type: '+str(type(element)))
                  index+=1
            if isUnconventionalType:               
               params.append(str(dataType.minVal))
               params.append(str(dataType.maxVal))
               params2=[]
               for element in compuMethod.elements:
                  if isinstance(element, autosar.datatype.CompuConstElement):
                     if element.lowerLimit==element.upperLimit:
                        params2.append('(%d, %s)'%(element.lowerLimit, repr(element.textValue)))
                     else:
                        params2.append('(%d, %d, %s)'%(element.lowerLimit, element.upperLimit, repr(element.textValue)))
                  else:
                     raise ValueError('unsupported value found of type: '+str(type(element)))               
            text='['+','.join(params2)+']'
            if len(text)>200:
               #this line is way too long, split it
               lines.extend(self.writeListCode('valueTableList',params2))
               params.append('valueTable=valueTableList')
            else:                     
               params.append('valueTable='+text)
         elif isinstance(compuMethod, autosar.datatype.CompuMethodRational):
            params.append(str(dataType.minVal))
            params.append(str(dataType.maxVal))            
            if len(compuMethod.elements)>1:
               raise NotImplementedError('CompuMethodRational with multiple elements not implemented')
            elif len(compuMethod.elements)==1:
               elem =compuMethod.elements[0]
               #offset
               params.append('offset='+str(elem.offset))
               #scaling
               if elem.denominator=="1":
                  params.append("scaling="+elem.numerator)
               else:
                  params.append("scaling=%s/%s"%(elem.numerator,elem.numerator))
               #for now, force float for all scaling factors
               params.append("forceFloatScaling=True")
            #unit
            if compuMethod.unitRef is not None:
               unit = ws.find(compuMethod.unitRef, role="Unit")
               if unit is None:
                  raise ValueError('invalid reference: '+compuMethod.unitRef)
               if ws.roles['Unit'] is not None:
                  ref = unit.name #use name only
               else:
                  ref = unit.ref #use full reference
               params.append('unit='+repr(ref))
         else:
            raise ValueError('unknown type:'+str(type(compuMethod)))
      else:
         params.append(str(dataType.minVal))
         params.append(str(dataType.maxVal))         
      if dataType.adminData is not None:
         param = self.writeAdminDataCode(dataType.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)         
      if hasattr(dataType, 'desc'):
         lines.append('dataType=package.createIntegerDataType(%s)'%(', '.join(params)))
         lines.append('dataType.desc = """%s"""'%dataType.desc)
      else:
         lines.append('package.createIntegerDataType(%s)'%(', '.join(params)))
      return lines
      
   def writeRealDataTypeCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']
      #name
      params=[repr(dataType.name)]
      #minVal
      if dataType.minVal is None:
         params.append('None')
      else:
         params.append('decimal.Decimal("%s")'%(str(dataType.minVal)))
      #maxVal
      if dataType.maxVal is None:
         params.append('None')
      else:
         params.append('decimal.Decimal("%s")'%(str(dataType.maxVal)))
      #minValType
      if dataType.minValType != 'CLOSED':
         params.append('minValType='+repr(dataType.minValType))
      #maxValType
      if dataType.maxValType != 'CLOSED':
         params.append('maxValType='+repr(dataType.maxValType))
      #hasNan
      if dataType.hasNaN:
         params.append('hasNaN=True')
      #encoding
      if dataType.encoding != 'SINGLE':
         params.append('encoding='+repr(dataType.encoding))
      #adminData
      if dataType.adminData is not None:
         param = self.writeAdminDataCode(dataType.adminData, localvars)
         assert(len(param)>0)
         params.append('adminData='+param)
      if hasattr(dataType, 'desc'):                       
         lines.append('dataType=package.createRealDataType(%s)'%(', '.join(params)))
         lines.append('dataType.desc = """{0}"""'.format(dataType.desc))
      else:
         lines.append('package.createRealDataType(%s)'%(', '.join(params)))
      return lines
   
   def writeRecordDataTypeCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']      
      params=[repr(dataType.name)]
      params2=[]
      for elem in dataType.elements:
         childType=ws.find(elem.typeRef)
         if childType is None:
            raise ValueError('invalid reference: '+dataType.typeRef)         
         if ws.roles['DataType'] is not None:            
            ref = childType.name #use only the name
         else:
            ref = childType.ref #use full reference
         params2.append('(%s,%s)'%(repr(elem.name), repr(ref))) #we use the tuple option since this is most convenient
      if len(dataType.elements)>4:      
         lines.extend(self.writeListCode('elementList',params2))
         params.append('elementList')
      else:
         params.append('['+', '.join(params2)+']')
      if hasattr(dataType, 'desc'):
         lines.append('dataType=package.createRecordDataType(%s)'%(', '.join(params)))
         lines.append('dataType.desc = """%s"""'%dataType.desc)
      else:
         lines.append('package.createRecordDataType(%s)'%(', '.join(params)))
      return lines
   
   def writeStringTypeCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']      
      #name
      params=[repr(dataType.name)]
      #length
      params.append(str(dataType.length))
      #encoding
      if dataType.encoding != 'ISO-8859-1':
         params.append('encoding='+repr(dataType.encoding))
      if hasattr(dataType, 'desc'):
         lines.append('dataType=package.createStringDataType(%s)'%(', '.join(params)))
         lines.append('dataType.desc = """%s"""'%dataType.desc) #the r will force a raw string to be created
      else:
         lines.append('package.createStringDataType(%s)'%(', '.join(params)))
      return lines
      
   def writeCompuMethodCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']
      return lines
   
   def CompuMethodRational(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']
      return lines
   
   def writeDataTypeUnitElementCode(self, dataType, localvars):
      lines=[]
      ws=localvars['ws']
      return lines
      