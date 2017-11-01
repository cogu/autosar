from autosar.writer.writer_base import ElementWriter
import autosar.base
import autosar.datatype
from fractions import Fraction

class XMLDataTypeWriter(ElementWriter):
   def __init__(self,version, patch):
      super().__init__(version, patch)
      
      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {
                           'ArrayDataType': self.writeArrayDataTypeXML,
                           'BooleanDataType': self.writeBooleanDataTypeXML,
                           'IntegerDataType': self.writeIntegerTypeXML,
                           'RealDataType': self.writeRealDataTypeXML,
                           'RecordDataType': self.writeRecordDataTypeXML,
                           'StringDataType': self.writeStringTypeXML,                           
                           'CompuMethodConst': self.writeCompuMethodXML,
                           'CompuMethodRational': self.writeCompuMethodXML,
                           'DataTypeUnitElement': self.writeDataTypeUnitElementXML,
         }
      elif self.version >= 4.0:
         self.switcher = {
                           'CompuMethodConst': self.writeCompuMethodXML,
                           'CompuMethodRational': self.writeCompuMethodXML,
                           'CompuMethodMask': self.writeCompuMethodXML,
                           'DataConstraint': self.writeDataConstraintXML,
                           'ImplementationDataType': self.writeImplementationDataTypeXML,
                           'SwBaseType': self.writeSwBaseTypeXML,
                           'DataTypeUnitElement': self.writeDataTypeUnitElementXML,
                           'DataTypeMappingSet': self.writeDataTypeMappingSetXML,
                           'ApplicationPrimitiveDataType': self.writeApplicationPrimitiveDataTypeXML,
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

   def writeIntegerTypeXML(self, elem):
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

   def writeRecordDataTypeXML(self, elem):
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

   def writeCompuMethodXML(self, elem):
      lines=[]
      lines.append('<COMPU-METHOD>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.category is not None:
         lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      if isinstance(elem,autosar.datatype.CompuMethodConst):
         lines.extend(self.indent(self.writeCompuMethodConstXML(elem),1))
      elif isinstance(elem,autosar.datatype.CompuMethodMask):
         lines.extend(self.indent(self.writeCompuMethodMaskXML(elem),1))
      else:
         if elem.unitRef is not None:
            lines.append(self.indent('<UNIT-REF DEST="UNIT">%s</UNIT-REF>'%elem.unitRef,1))
         lines.extend(self.indent(self.writeCompuMethodRationalXML(elem),1))
      lines.append('</COMPU-METHOD>')
      return lines

   def writeCompuMethodConstXML(self,item):
      lines=[]
      lines.append('<COMPU-INTERNAL-TO-PHYS>')
      lines.append(self.indent('<COMPU-SCALES>',1))
      for elem in item.elements:
         lines.append(self.indent('<COMPU-SCALE>',2))
         if elem.label is not None:
            lines.append(self.indent('<SHORT-LABEL>%s</SHORT-LABEL>'%elem.label,3))
         if self.version>=4.0:
            lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="CLOSED">%d</LOWER-LIMIT>'%elem.lowerLimit,3))
            lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="CLOSED">%d</UPPER-LIMIT>'%elem.upperLimit,3))
         else:
            lines.append(self.indent('<LOWER-LIMIT>%d</LOWER-LIMIT>'%elem.lowerLimit,3))
            lines.append(self.indent('<UPPER-LIMIT>%d</UPPER-LIMIT>'%elem.upperLimit,3))
         lines.append(self.indent('<COMPU-CONST>',3))
         lines.append(self.indent('<VT>%s</VT>'%elem.textValue,4))
         lines.append(self.indent('</COMPU-CONST>',3))
         lines.append(self.indent('</COMPU-SCALE>',2))
      lines.append(self.indent('</COMPU-SCALES>',1))
      lines.append('</COMPU-INTERNAL-TO-PHYS>')
      return lines

   def writeCompuMethodMaskXML(self,item):
      lines=[]
      lines.append('<COMPU-INTERNAL-TO-PHYS>')
      lines.append(self.indent('<COMPU-SCALES>',1))
      for elem in item.elements:
         lines.append(self.indent('<COMPU-SCALE>',2))
         if elem.label is not None:
            lines.append(self.indent('<SHORT-LABEL>%s</SHORT-LABEL>'%elem.label,3))
            if elem.symbol is not None:
               lines.append(self.indent('<SYMBOL>%s</SYMBOL>'%elem.symbol,3))
            lines.append(self.indent('<MASK>%d</MASK>'%elem.mask,3))
            lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="CLOSED">%d</LOWER-LIMIT>'%elem.lowerLimit,3))
            lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="CLOSED">%d</UPPER-LIMIT>'%elem.upperLimit,3))
         lines.append(self.indent('</COMPU-SCALE>',2))
      lines.append(self.indent('</COMPU-SCALES>',1))
      lines.append('</COMPU-INTERNAL-TO-PHYS>')
      return lines

   def writeCompuMethodRationalXML(self,item):
      lines=[]
      lines.append('<COMPU-INTERNAL-TO-PHYS>')
      lines.append(self.indent('<COMPU-SCALES>',1))
      for elem in item.elements:
         lines.append(self.indent('<COMPU-SCALE>',2))
         if elem.label is not None:
            lines.append(self.indent('<SHORT-LABEL>%s</SHORT-LABEL>'%elem.label,3))
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

   def writeDataTypeUnitElementXML(self, elem):
      lines=[]
      lines.append('<UNIT>')
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.displayName is not None:
         lines.append(self.indent('<DISPLAY-NAME>%s</DISPLAY-NAME>'%elem.displayName,1))
      if self.version >= 4.0:
         if elem.factor is not None:
            lines.append(self.indent('<FACTOR-SI-TO-UNIT>%s</FACTOR-SI-TO-UNIT>'%elem.factor,1))
         if elem.offset is not None:
            lines.append(self.indent('<OFFSET-SI-TO-UNIT>%s</OFFSET-SI-TO-UNIT>'%elem.offset,1))
      lines.append('</UNIT>')
      return lines

   def writeArrayDataTypeXML(self, elem):
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

   def writeBooleanDataTypeXML(self, elem):
      assert(isinstance(elem,autosar.datatype.BooleanDataType))
      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeRealDataTypeXML(self, elem):
      assert(isinstance(elem,autosar.datatype.RealDataType))
      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      if elem.minValType=="INFINITE":
         lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="INFINITE"></LOWER-LIMIT>',1))
      else:
         if isinstance(elem.minVal, str):
            lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0.minValType}">{0.minVal}</LOWER-LIMIT>'.format(elem),1))
         else:
            lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0.minValType}">{0.minVal:f}</LOWER-LIMIT>'.format(elem),1))
      if elem.maxValType=="INFINITE":
         lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="INFINITE"></UPPER-LIMIT>',1))
      else:
         if isinstance(elem.maxVal, str):
            lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0.maxValType}">{0.maxVal}</UPPER-LIMIT>'.format(elem),1))
         else:
            lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0.maxValType}">{0.maxVal:f}</UPPER-LIMIT>'.format(elem),1))
      lines.append(self.indent('<ALLOW-NAN>%s</ALLOW-NAN>'%('true' if elem.hasNaN else 'false'),1))
      lines.append(self.indent('<ENCODING>%s</ENCODING>'%elem.encoding,1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeStringTypeXML(self, elem):
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

   def writeDataConstraintXML(self, elem):
      assert(isinstance(elem,autosar.datatype.DataConstraint))
      ws=elem.rootWS()
      assert(isinstance(ws,autosar.Workspace))

      lines=[]
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      lines.append(self.indent('<DATA-CONSTR-RULES>', 1))
      for rule in elem.rules:
         lines.extend(self.indent(self.writeDataConstraintRuleXML(rule), 2))
      lines.append(self.indent('</DATA-CONSTR-RULES>', 1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeDataConstraintRuleXML(self, rule):
      lines = []
      lines.append("<DATA-CONSTR-RULE>")
      if isinstance(rule, autosar.datatype.InternalConstraint):
         lines.append(self.indent('<INTERNAL-CONSTRS>', 1))
         lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0}">{1}</LOWER-LIMIT>'.format(rule.lowerLimitType, rule.lowerLimit), 2))
         lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0}">{1}</UPPER-LIMIT>'.format(rule.lowerLimitType, rule.upperLimit), 2))
         lines.append(self.indent('</INTERNAL-CONSTRS>', 1))
      else:
         raise NotImplementedError(str(type(rule)))
      lines.append("</DATA-CONSTR-RULE>")
      return lines

   def writeImplementationDataTypeXML(self, elem):
      assert(isinstance(elem, autosar.datatype.ImplementationDataType))
      ws=elem.rootWS()
      assert(ws is not None)
      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent("<SHORT-NAME>%s</SHORT-NAME>"%elem.name, 1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      lines.append(self.indent("<CATEGORY>%s</CATEGORY>" % elem.category, 1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
      if len(elem.variants)>=0:
         lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variants),2))
      lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
      if elem.dynamicArraySize is not None:
         lines.append(self.indent("<DYNAMIC-ARRAY-SIZE-PROFILE>%s</DYNAMIC-ARRAY-SIZE-PROFILE>"%(str(elem.dynamicArraySize)), 1))
      if len(elem.subElements)>0:
         lines.append(self.indent("<SUB-ELEMENTS>", 1))
         for subElem in elem.subElements:
            lines.extend(self.indent(self.writeImplementationDataElementXML(ws, subElem),2))
         lines.append(self.indent("</SUB-ELEMENTS>", 1))
      if elem.typeEmitter is not None:
         lines.append(self.indent("<TYPE-EMITTER>%s</TYPE-EMITTER>"%(elem.typeEmitter), 1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeSwPointerTargetPropsXML(self, ws, elem):
      assert(isinstance(elem, autosar.base.SwPointerTargetProps))
      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      if elem.targetCategory is not None:
         lines.append(self.indent('<TARGET-CATEGORY>%s</TARGET-CATEGORY>'%(elem.targetCategory),1))
      lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
      if len(elem.variants)>=0:
         lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variants),2))
      lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeSwBaseTypeXML(self, elem):
      assert(isinstance(elem, autosar.datatype.SwBaseType))
      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None: lines.extend(self.indent(tmp,1))
      if elem.category is not None:
         lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      lines.append(self.indent('<BASE-TYPE-SIZE>%d</BASE-TYPE-SIZE>'%elem.size,1))
      if elem.typeEncoding is None:
         lines.append(self.indent('<BASE-TYPE-ENCODING>NONE</BASE-TYPE-ENCODING>',1))
      else:
         lines.append(self.indent('<BASE-TYPE-ENCODING>%s</BASE-TYPE-ENCODING>'%elem.typeEncoding,1))
      if elem.nativeDeclaration is not None:
         lines.append(self.indent('<NATIVE-DECLARATION>%s</NATIVE-DECLARATION>'%elem.nativeDeclaration,1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeImplementationDataElementXML(self, ws, elem):
      assert(isinstance(elem, autosar.datatype.ImplementationDataTypeElement))
      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      if elem.category is not None:
         lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
      if elem.adminData is not None:
         lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
      if elem.arraySize is not None:
         lines.append(self.indent('<ARRAY-SIZE>%s</ARRAY-SIZE>'%elem.arraySize,1))
      if elem.arraySizeSemantics is not None:
         lines.append(self.indent('<ARRAY-SIZE-SEMANTICS>%s</ARRAY-SIZE-SEMANTICS>'%elem.arraySizeSemantics,1))
      if len(elem.variants)>=0:
         lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
         lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variants),2))
         lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeDataTypeMappingSetXML(self, elem):
      assert(isinstance(elem, autosar.datatype.DataTypeMappingSet))
      ws=elem.rootWS()
      assert(ws is not None)

      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      dataTypeMaps = []
      for key in sorted(elem.map.keys()):
         dataTypeMaps.append(elem.get(key))
      if len(dataTypeMaps) > 0:
         lines.append(self.indent('<DATA-TYPE-MAPS>',1))
         for dataTypeMap in dataTypeMaps:
            lines.extend(self.indent(self.writeDataTypeMapXML(ws, dataTypeMap),2))
         lines.append(self.indent('</DATA-TYPE-MAPS>',1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines
   
   def writeDataTypeMapXML(self, ws, elem):
      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      applicationDataType = ws.find(elem.applicationDataTypeRef)
      if applicationDataType is None:
         raise ValueError('Invalid type refernce:' + elem.applicationDataTypeRef)
      implementationDataType = ws.find(elem.implementationDataTypeRef)
      if implementationDataType is None:
         raise ValueError('Invalid type refernce:' + elem.implementationDataTypeRef)
      lines.append(self.indent('<APPLICATION-DATA-TYPE-REF DEST="%s">%s</APPLICATION-DATA-TYPE-REF>'%(applicationDataType.tag(self.version), applicationDataType.ref),1))
      lines.append(self.indent('<IMPLEMENTATION-DATA-TYPE-REF DEST="%s">%s</IMPLEMENTATION-DATA-TYPE-REF>'%(implementationDataType.tag(self.version), implementationDataType.ref),1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

   def writeApplicationPrimitiveDataTypeXML(self, elem):
      assert(isinstance(elem, autosar.datatype.ApplicationPrimitiveDataType))
      ws=elem.rootWS()
      assert(ws is not None)

      lines = []
      lines.append("<%s>"%elem.tag(self.version))
      lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
      tmp = self.writeDescXML(elem)
      if tmp is not None:
         lines.extend(self.indent(tmp,1))
      if elem.category is not None:
         lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
      if len(elem.variants)>=0:
         lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
         lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variants),2))
         lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
      lines.append("</%s>"%elem.tag(self.version))
      return lines

class CodeDataTypeWriter(ElementWriter):
   def __init__(self, version, patch):
      super().__init__(version, patch)

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {
                           'ArrayDataType': self.writeArrayDataTypeCode,
                           'BooleanDataType': self.writeBooleanDataTypeCode,
                          'IntegerDataType': self.writeIntegerTypeCode,
                          'RealDataType': self.writeRealDataTypeCode,
                          'RecordDataType': self.writeRecordDataTypeCode,
                          'StringDataType': self.writeStringTypeCode,
                          'CompuMethodConst': self.writeCompuMethodCode,
                          'CompuMethodRational': self.writeCompuMethodCode,
                          'DataTypeUnitElement': self.writeDataTypeUnitElementCode
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

   def writeImplementationDataTypeCode(self, dataType, localvars):
      lines = []
      return lines

   def writeDataConstraintCode(self, dataType, localvars):
      lines = []
      return lines