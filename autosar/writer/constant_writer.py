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
   
   ###code generators
   
   def writeConstantCode(self, constant, localvars):
      lines=[]      
      ws=localvars['ws']      
      if not isinstance(constant, autosar.constant.Constant):
         raise ValueError('expected type autosar.constant.Constant')
      if constant.value is not None:
         dataType = ws.find(constant.value.typeRef, role='DataType')
         constructor=None
         if dataType is None:
            raise ValueError('invalid reference: '+constant.value.typeRef)
         if isinstance(constant.value, autosar.constant.ArrayValue):
            initValue = self._writeArrayValueConstantCode(constant.value, localvars)            
         elif isinstance(constant.value, autosar.constant.IntegerValue):
            initValue = self._writeIntegerValueConstantCode(constant.value, localvars)            
         elif isinstance(constant.value, autosar.constant.StringValue):
            initValue = self._writeStringValueConstantCode(constant.value, localvars)            
         elif isinstance(constant.value, autosar.constant.BooleanValue):
            initValue = self._writeBooleanValueConstantCode(constant.value, localvars)            
         elif isinstance(constant.value, autosar.constant.RecordValue):
            initValue = self._writeRecordValueConstantCode(constant.value, localvars)            
         else:
            raise ValueError('unknown value type: '+type(constant.value))
         params=[repr(constant.name)]
         if ws.roles['DataType'] is not None:
            params.append(repr(dataType.name)) #use name only
         else:
            params.append(repr(dataType.ref)) #use full reference
         if initValue is not None:
            if isinstance(initValue, list):
               lines.extend(self.writeDictCode('initValue', initValue))
               params.append('initValue')
            else:
               params.append(initValue)
         else:
            print(constant.name)
         if constant.adminData is not None:
            param = self.writeAdminDataCode(constant.adminData, localvars)
            assert(len(param)>0)
            params.append('adminData='+param)
         lines.append("package.createConstant(%s)"%(', '.join(params)))
      return lines
   
   def _writeArrayValueConstantCode(self, value, localvars):
      ws=localvars['ws']
      assert(isinstance(value, autosar.constant.ArrayValue))      
      params=[]
      for elem in value.elements:
         if isinstance(elem, autosar.constant.ArrayValue):
            initValue = self._writeArrayValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.IntegerValue):
            initValue = self._writeIntegerValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.StringValue):
            initValue = self._writeStringValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.BooleanValue):
            initValue = self._writeBooleanValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.RecordValue):
            initValue = self._writeRecordValueConstantCode(elem, localvars)
            if isinstance(initValue, list): initValue="{%s}"%(', '.join(initValue)) #join any inner record init values
         else:
            raise ValueError('unknown value type: '+type(constant.value))
         params.append(initValue)
      if len(params)>0:
         return "[%s]"%(', '.join(params))
      return None

   def _writeIntegerValueConstantCode(self, value, localvars):
      return str(value.value)

   def _writeStringValueConstantCode(self, value, localvars):
      return repr(value.value)      

   def _writeBooleanValueConstantCode(self, value, localvars):
      return str(value.value)
   
   def _writeRecordValueConstantCode(self, value, localvars):
      ws=localvars['ws']
      assert(isinstance(value, autosar.constant.RecordValue))      
      params=[]
      for elem in value.elements:
         if isinstance(elem, autosar.constant.ArrayValue):
            initValue = self._writeArrayValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.IntegerValue):
            initValue = self._writeIntegerValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.StringValue):
            initValue = self._writeStringValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.BooleanValue):
            initValue = self._writeBooleanValueConstantCode(elem, localvars)
         elif isinstance(elem, autosar.constant.RecordValue):
            initValue = self._writeRecordValueConstantCode(elem, localvars)
            if isinstance(initValue, list): initValue="{%s}"%(', '.join(initValue)) #join any inner record init values
         else:
            raise ValueError('unknown value type: '+type(constant.value))
         params.append('"%s": %s'%(elem.name, initValue))
      if len(params)>0:
         text = "{%s}"%(', '.join(params))
         if len(text)>200: #line will be way too long
            return params
         else:
            return text
      return None

