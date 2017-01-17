import autosar
import math

def _getIntegerTypeCode(dataType):
   global args
   if dataType.minVal >= 0:
      bits = _calcUIntTypeLen(dataType)      
      if bits <=8:
         if (dataType.minVal>0) or (dataType.maxVal<255):
            return 'C(%d,%d)'%(dataType.minVal,dataType.maxVal)
         else:
            return 'C'
      elif bits <=16:
         return 'S'
      elif bits <=32:
         return 'L'
      elif bits <=64:
         return 'U'
   elif dataType.minVal<0:
      bits = _calcIntTypeLen(dataType)      
      if bits <=8:
         if (dataType.minval>-128) or dataType.maxVal<127:
            return 'c(%d,%d)'%(dataType.minval,dataType.maxVal)
         else:
            return 'c'
      elif bits <=16:
         return 's'
      elif bits <=32:
         return 'l'
      elif bits <=64:
         return 'u'
   else:
      print("not implemented (min=%s)"%dataType.minval)

def _calcUIntTypeLen(dataType):
   if isinstance(dataType,autosar.datatype.IntegerDataType):
      if dataType.minVal == 0:
         return int(math.ceil(math.log(dataType.maxVal,2)))
   return None

def _calcIntTypeLen(dataType):
   if isinstance(dataType,autosar.datatype.IntegerDataType):
      if dataType.minval < 0:
         return int(math.ceil(math.log(abs(dataType.maxVal),2)))+1
   return None


class Port:
   def __init__(self,name,typeId):
      self.name = name
      self.typeId = typeId

   def _calcAttribute(self,ws,port):
      if (len(port.comspec)==1) and isinstance(port.comspec[0],autosar.component.DataElementComSpec):
         if port.comspec[0].initValueRef is not None:
            initValue = ws.find(port.comspec[0].initValueRef)
            return "="+self._deriveInitValue(initValue)
      return None
   
   def _deriveInitValue(self,item):      
      if isinstance(item,autosar.constant.IntegerValue):
         if (item.value>255):
            return "0x%02X"%item.value
         else:
            return "%d"%item.value
      elif isinstance(item,autosar.constant.StringValue):
            return '="%s"'%item.value
      elif isinstance(item,autosar.constant.RecordValue):
         tmp = [self._deriveInitValue(x) for x in item.elements]
         return "{"+','.join(tmp)+"}"
      elif isinstance(item,autosar.constant.ArrayValue):
         tmp = [self._deriveInitValue(x) for x in item.elements]
         return "{"+','.join(tmp)+"}"
      else:
         raise NotImplementedError(str(type(item)))

      

class RequirePort(Port):
   def __init__(self, name, typeId, ws=None, port=None):
      super().__init__(name,typeId)
      if (ws is not None) and (port is not None):
         self.attr = self._calcAttribute(ws,port)
   
   def __str__(self):
      if self.attr is not None:
         return 'R"%s"T[%d]:%s'%(self.name,self.typeId,self.attr)
      else:
         return 'R"%s"T[%d]'%(self.name,self.typeId)
   
   def mirror(self):
      other = ProvidePort(self.name, self.typeId)
      other.attr = self.attr
      return other

class ProvidePort(Port):
   def __init__(self, name, typeId, ws=None, port=None):
      super().__init__(name,typeId)
      if (ws is not None) and (port is not None):
         self.attr = self._calcAttribute(ws,port)
   
   def __str__(self):
      if self.attr is not None:
         return 'P"%s"T[%d]:%s'%(self.name,self.typeId,self.attr)
      else:
         return 'P"%s"T[%d]'%(self.name,self.typeId)

   def mirror(self):
      other = RequirePort(self.name, self.typeId)
      other.attr = self.attr
      return other

      
class DataType:
   def __init__(self,ws,dataType):
      self.name=dataType.name
      self.dsg=self._calcDataSignature(ws,dataType)
      typeSemantics = ws.find('/DataType/DataTypeSemantics/%s'%dataType.name)
      if typeSemantics is not None:
         self.attr = self._calcAttribute(dataType,typeSemantics)
      else:
         self.attr=None      
   
   def __str__(self):
      if self.attr is not None:
         return 'T"%s"%s:%s'%(self.name,self.dsg,self.attr)
      else:
         return 'T"%s"%s'%(self.name,self.dsg)
   
   def _calcAttribute(self,dataType,typeSemantics):
      if isinstance(typeSemantics,autosar.datatype.CompuMethodConst):
         values=[]
         for elem in typeSemantics.elements:
            assert(isinstance(elem,autosar.datatype.CompuConstElement))
            values.append(elem.textValue)
         v=','.join(['"%s"'%x for x in values])
         return "VT(%s)"%v
      return None

   def _calcDataSignature(self,ws,dataType):      
      if isinstance(dataType,autosar.datatype.BooleanDataType):
         return 'C(0,1)'
      if isinstance(dataType,autosar.datatype.IntegerDataType):      
         return _getIntegerTypeCode(dataType)
      elif isinstance(dataType,autosar.datatype.ArrayDataType):
         typeCode = _getIntegerTypeCode(typeData.find(dataType['typeRef']))
         if typeCode != None:
            return "%s[%d]"%(typeCode,int(dataType.length))
         else:
            raise Exception("unsupported type: %s"%typeData.find(dataType['typeRef']))
      elif isinstance(dataType,autosar.datatype.StringDataType):
         typeCode = 'a'
         if typeCode != None:
            return "%s[%d]"%(typeCode,int(dataType.length)+1)            
      elif isinstance(dataType,autosar.datatype.RecordDataType):
         result="{"
         for elem in dataType.elements:
            #remove _RE from end of element names
            if elem.name.endswith('_RE'):
               elem.name=elem.name[:-3]
            childType = ws.find(elem.typeRef)
            result+='"%s"%s'%(elem.name, self._calcDataSignature(ws, childType))            
         result+="}"
         return result
      else: raise Exception('uhandled data type: %s'%type(dataType))
      return ""
