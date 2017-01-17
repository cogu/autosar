class ApxSignature(object):
   def __init__(self,mainType,name,dsg,attr=""):
      self.mainType=mainType
      self.name=name
      self.dsg=dsg
      self.attr=attr
   def __str__(self):
      if (self.attr != None) and len(self.attr)>0:
         return '%s"%s"%s:%s'%(self.mainType,self.name,self.dsg,self.attr)
      else:
         return '%s"%s"%s'%(self.mainType,self.name,self.dsg)

class ApxType(object):
   @staticmethod
   def _calcUIntTypeLen(dataType):
      if dataType['type']=='integer':
         if dataType['min'] == 0:
            return int(math.ceil(math.log(dataType['max'],2)))
      return None

   @staticmethod
   def _calcIntTypeLen(dataType):
      if dataType['type']=='integer':
         if dataType['min'] < 0:
            return int(math.ceil(math.log(abs(dataType['max']),2)))+1
      return None
   
   @staticmethod
   def _calcDataSignature(dataType):
      global typeData
      global args
      typeCode = None
            
      if dataType['type']=='boolean':
         return 'C(0,1)'
      if dataType['type']=='integer':      
         return ApxType._getIntegerTypeCode(dataType)
      elif dataType['type'] == 'array':
         typeCode = ApxType._getIntegerTypeCode(typeData.find(dataType['typeRef']))
         if typeCode != None:
            return "%s[%d]"%(typeCode,int(dataType['length']))
         else:
            raise Exception("unsupported type: %s"%typeData.find(dataType['typeRef']))
      elif dataType['type'] == 'string':
         typeCode = 'a'
         if typeCode != None:
            return "%s[%d]"%(typeCode,int(dataType['length'])+1)            
      elif dataType['type'] == 'record':
         result="{"
         for elem in dataType['elements']:
            #uncomment to remove _RE from end of element names
            #if elem['name'].endswith('_RE'):
            #elem['name']=elem['name'][:-3]
            childType = typeData.find(elem['typeRef'])
            result+='"%s"%s'%(elem['name'],ApxType._calcDataSignature(childType))
               
         result+="}"
         return result
      else: raise Exception('uhandled data type: %s'%dataType['type'])
      return ""
   
   @staticmethod
   def _getIntegerTypeCode(dataType):
      global args
      if dataType['min'] >= 0:
         bits = ApxType._calcUIntTypeLen(dataType)      
         if bits <=8:
            if (dataType['min']>0) or (dataType['max']<255):
               return 'C(%d,%d)'%(dataType['min'],dataType['max'])
            else:
               return 'C'
         elif bits <=16:
            return 'S'
         elif bits <=32:
            return 'L'
         elif bits <=64:
            return 'U'
      elif dataType['min']<0:
         bits = ApxType._calcIntTypeLen(dataType)      
         if bits <=8:
            if (dataType['min']>-128) or dataType['max']<127:
               return 'c(%d,%d)'%(dataType['min'],dataType['max'])
            else:
               return 'c'
         elif bits <=16:
            return 's'
         elif bits <=32:
            return 'l'
         elif bits <=64:
            return 'u'
      else:
         print("not implemented (min=%s)"%dataType['min'])

   @staticmethod
   def _calcAttribute(dataType):
      if dataType['type']=='integer':
         typeSemantics = typeData.find('/DataType/Semantics/%s'%dataType['name'])
         if (typeSemantics != None) and ('valueTable' in typeSemantics):
               v=','.join(['"%s"'%x for x in typeSemantics['valueTable']])
               return "VT(%s)"%v
      return None
   
   def __init__(self,dataType):
      self.name = dataType['name']      
      self.signature = ApxSignature('T',dataType['name'],ApxType._calcDataSignature(dataType),ApxType._calcAttribute(dataType))
         

class ApxPort(object):
   def __init__(self,name,typeIndex,attrib):
      self.name = name
      self.typeIndex = typeIndex
      self.attrib=attrib
   def getAttrStr(self):
      result=""
      if self.attrib['initValue']!=None:
         result+="=%s"%self.attrib['initValue']
      if self.attrib['isQueued']:
         if self.attrib['queueLen']!=None:
            result+="Q[%d]"%self.attrib['queueLen']
         else:
            result+="Q"
      if self.attrib['isParameter']:
         result+="P"
      return result
