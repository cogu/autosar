#! /bin/python3
#Copyright (c) 2015-2016, Conny Gustafsson

import math
import re
import sys

START_SECTION=0
NODE_SECTION=1
TYPE_SECTION=2
PROVIDE_SECTION=3
REQUIRE_SECTION=4


def _matchPair(s,left,right):   
   if (len(s)>0) and (s[0]==left):
      count=1
      for i in range(1,len(s)):            
         if s[i]==right:
            count-=1
            if count==0:
               return (s[1:i],s[i+1:])
         elif s[i]==left:
            count+=1 #nested pair
      return (None,"")
   return (None,s)
      
def _parseStr(s):
   return _matchPair(s,'"','"')

_p0=re.compile(r'([\+\-A-Z]+)')
_p1=re.compile(r'([^:]*)')
def ApxSplitLine(s):
   r0=_p0.match(s)
   if r0 is not None:
      lineType=r0.group(1)
      remain=s[len(lineType):]
      (name,remain) = _parseStr(remain)
      if len(remain)>0:
         r1 = _p1.match(remain)
         if r1 is not None:
            dsg=r1.group(1)
            remain=remain[len(dsg):]
            if len(remain)>0:
               if remain[0]==':':
                  remain=remain[1:]
               return (lineType,name,dsg,remain)
         return (lineType,name,dsg,None)
      else:
         return (lineType,name)
   return None,s

class ApxParser(object):
   @staticmethod
   def _parseHeaderLine(s):
      """returns string with major and minor version of APX header or None if line cannot be parsed"""
      p=re.compile(r'APX/(\d)\.(\d)')
      r = p.match(s)
      if r != None:         
         return "%s.%s"%(r.group(1),r.group(2))
      return None   
   
   def _processLine(self, line):
      parts = ApxSplitLine(line)         
      if parts != None and len(parts)>0:            
         if self.cs == START_SECTION:            
            if parts[0]=='N': #Node Line
               self.cs=NODE_SECTION
               apxNode = ApxNode(parts[1])
               self._applyNode(apxNode)
         elif self.cs == NODE_SECTION:            
            if parts[0]=='T':
               self.cs=TYPE_SECTION
               apxType = ApxType(parts[1],parts[2],parts[3])
               self._applyType(apxType)
            elif parts[0]=='P':
               self.cs=PROVIDE_SECTION
               portLine = ApxProvidePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)                  
            elif parts[0]=='R':
               self.cs=REQUIRE_SECTION
               portLine = ApxRequirePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)
         elif self.cs == TYPE_SECTION:            
            if parts[0]=='T':               
               typeLine = ApxType(parts[1],parts[2],parts[3])
               self._applyType(typeLine)
            elif parts[0]=='P':
               self.cs=PROVIDE_SECTION
               portLine = ApxProvidePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)
            elif parts[0]=='R':
               self.cs=REQUIRE_SECTION
               portLine = ApxRequirePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)
         elif self.cs == PROVIDE_SECTION:
            if parts[0]=='P':
               portLine = ApxProvidePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)
            elif parts[0]=='R':
               self.cs=REQUIRE_SECTION
               portLine = ApxRequirePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)
         elif self.cs == REQUIRE_SECTION:
            if parts[0]=='R':
               portLine = ApxRequirePort(parts[1],parts[2],parts[3])
               self._applyPort(portLine)
         else:
            print("syntax error on line '%d'"%self.ln)
      else:
         print("syntax error on line '%d'"%self.ln)      
   
   def _parseV12(self,fp,firstLine):
      """parses APX version 1.2 file"""
      while True:
         if firstLine != None:
            line = firstLine #reparse firstLine in case it was given to us as an argument
            firstLine = None
         else:
            line = fp.readline() #read next line from file handle
            if len(line)==0:
               break
            self.ln+=1
            line=line.rstrip('\r\n')
            self._processLine(line)
      return self.node   
   
   def __init__(self):      
      self.node = None
   
   def load(self,fp):
      self.cs=None
      self.ln=1
      firstLine = fp.readline()
      firstLine=firstLine.rstrip('\r\n')
      parsedVersion=ApxParser._parseHeaderLine(firstLine)
      if parsedVersion == None:
         version = "1.2"
      else:
         version = parsedVersion      
      if version == "1.2":
         self.cs = START_SECTION
         if parsedVersion==None:
            return self._parseV12(fp,firstLine) #firstLine did not contain APX version line
         else:
            self.ln+=1
            return self._parseV12(fp,None) #firstLine contained APX version line      
      else:
         raise NotImplementedError

   def loads(self, text):
      self.cs=None
      self.ln=1
      lines = text.split('\n')
      skipLine=0
      firstLine = lines[0]
      firstLine=firstLine.rstrip('\r\n')
      parsedVersion=ApxParser._parseHeaderLine(firstLine)
      if parsedVersion == None:
         version = "1.2"
      else:
         version = parsedVersion      
      if version == "1.2":
         self.cs = START_SECTION
         if parsedVersion is not None:
            skipLine=1         
      else:
         raise NotImplementedError
      for line in lines:
         if skipLine>0:
            self.ln+=1
            skipLine-=1
            continue
         else:         
            self._processLine(line)
            self.ln+=1
      self.node.text=text
      return self.node

   def _applyNode(self,apxNode):
      self.node = apxNode
   
   def _applyType(self,apxType):
      self.node.addType(apxType)
   
   def _applyPort(self,apxPort):
      if isinstance(apxPort,ApxProvidePort):
         self.node.addProvidePort(apxPort)
      elif isinstance(apxPort,ApxRequirePort):
         self.node.addRequirePort(apxPort)
      else:
         raise ValueError
   
class ApxNode(object):
   def __init__(self,name=None,dim=[]):
      self.name=name
      self.dim=dim
      self.typeList = []
      self.providePortList = []
      self.requirePortList = []
      self.generator={}
   
   def addType(self,item):
      self.typeList.append(item)
   
   def addProvidePort(self,port):
      port.id=len(self.providePortList)
      self.providePortList.append(port)      
   
   def addRequirePort(self,port):
      port.id=len(self.requirePortList)
      self.requirePortList.append(port)
   
   def getType(self,index):
      return self.typeList[index]


class ApxDataSignature(object):      
   def __init__(self,dsg):
      if isinstance(dsg,dict):
         self.data=dsg
         self.str=None
      else:
         (signature,remain)=ApxDataSignature._parseDataSignature(dsg)
         if len(remain)>0:
            raise Exception("string '%s' not fully parsed"%dsg)
         self.data=signature
         self.str=dsg
      self.typeList=None
      
   def __str__(self):
      return self.str
     
   def packLen(self,typeList=None):
      result=0
      stack = []      
      i = iter([self.data])
      
      while True:
         try:
            node = next(i)
         except StopIteration:
            try:
               i = stack.pop()
               continue
            except IndexError:
               break
         if node['type']=='record':
            stack.append(i)
            i=iter(node['elements'])
         else:
            elemSize=self.calcElemSize(node,typeList)
            result+=elemSize
               
      return result

   def calcElemSize(self,node,typeList):
      if node['type']=='C' or node['type']=='c' or node['type']=='E' or node['type']=='a' or node['type']=='b': elemSize=1
      elif node['type']=='S' or node['type']=='s': elemSize=2
      elif node['type']=='L' or node['type']=='l': elemSize=4
      elif node['type']=='u' or node['type']=='U': elemSize=8
      elif node['type']=='n': elemSize=4
      elif node['type']=='N': elemSize=8
      elif node['type']=='typeRef':
         if not isinstance(typeList,list):
            raise ValueError("typeList must be of type list")
         dataType=typeList[self.data['refId']]
         return self.calcElemSize(dataType.dsg.data,typeList)
      else:
         elemSize=0
         for elem in node['elements']:
            elemSize+=self.calcElemSize(elem,typeList)
      if node['isArray']:
         return elemSize*node['arrayLen']
      else:      
         return elemSize
      
      
   def typename(self,typeList=None):
      """
      Returns the type name of the data signature as a string. This return value can be used for code generation in C/C++ code.
      """
      if self.data['type']=='typeRef':
         return typeList[self.data['refId']].name
      else:
         (s,pre,post)=ApxGenBase.deriveTypeStr(self.data)
         return s
   def isComplexType(self,typeList=None):
      """
      Returns True of the type is record, array or string. Otherwise it returns False
      """
      obj=self.resolveType(typeList)
      if ( (obj.data['type']=='record') or (obj.data['type']=='string') or
            ( ('isArray' in obj.data) and (obj.data['isArray']==True) ) ):
         return True
      return False
   def isArray(self,typeList=None):
      """
      Returns True of the type is array. Otherwise it returns False
      """
      obj=self.resolveType(typeList)
      if ('isArray' in obj.data) and (obj.data['isArray']==True):
         return True
      return False
   def resolveType(self,typeList=None):
      """
      Returns type object
      """
      if self.data['type']=='typeRef':
         if typeList is not None:
            obj=typeList[self.data['refId']].dsg
         elif self.typeList is not None:
            obj=self.typeList[self.data['refId']].dsg
         else:
            raise ValueError('no typelist avaliable')
         
      else:
         obj=self
      return obj

   @staticmethod
   def _parseRecordSignature(remain):
      elements=[]
      while len(remain)>0:
         (name,remain)=_matchPair(remain,'"','"')
         if len(remain)>0:            
            (elem,remain)=ApxDataSignature._parseDataSignature(remain)
            if elem == None:
               if remain[0] == '}':
                  return {'type':'record','elements':elements,'isArray':False},remain[1:]
               else:
                  raise Exception('syntax error while parsing record')
            else:
               elem['name']=name
               elements.append(elem)
      return (None,remain)
   
   @staticmethod
   def _parseExtendedTypeCode(c,data):
      values=re.split(r'\s*,\s*',data)
      if len(values)<2:
         raise Exception("min,max missing from %s"%data)
      attr = {'min':int(values[0]),'max':int(values[1])}
      return {'type':c,'isArray':False,'attr':attr}
   
   @staticmethod   
   def _parseDataSignature(s):
      remain=s
      c=remain[0]      
      if c=='{': #start of record 
         remain = remain[1:]
         return ApxDataSignature._parseRecordSignature(remain)      
      if c=='T': #typeRef         
         (data,remain2)=_matchPair(remain[1:],'[',']')
         if data!=None and len(remain2)==0:            
            return({'type':'typeRef','refId':int(data)},remain2)
         else:
            raise Exception("parse failure '%s'"%remain)
      else:
         typeCodes=['a','c','s','l','u','n','C','S','L','U','N']
         try:
            i = typeCodes.index(c)
         except ValueError:
            return (None,remain)
         if (len(remain)>1) and (remain[1]=='['):
               (data,remain)=_matchPair(remain[1:],'[',']')
               return ({'type':c,'isArray':True,'arrayLen':int(data)},remain)
         if (len(remain)>1) and (remain[1]=='('):
               (data,remain)=_matchPair(remain[1:],'(',')')
               return (ApxDataSignature._parseExtendedTypeCode(c,data),remain)
         else:
            remain=remain[1:]
            return ({'type':c,'isArray':False},remain)         
         
class ApxType(object):   
   def __init__(self,name,dsg,attr=None):
      self.name=name
      self.dsg=ApxDataSignature(dsg)
      self.attr=ApxTypeAttribute(attr)
      self.usage={'read':False, 'write':False}
   
class ApxProvidePort(object):      
   def __init__(self,name,dsg,attr=None):
      self.name=name
      self.dsg=ApxDataSignature(dsg)      
      self.attr=ApxPortAttribute(attr)
      self.generator={}
      self.id=None

class ApxRequirePort(object):      
   def __init__(self,name,dsg,attr=None):
      self.name=name
      self.dsg=ApxDataSignature(dsg)
      self.attr=ApxPortAttribute(attr)
      self.generator={}
      self.id=None

class ApxPortAttribute(object):
   _p2=re.compile(r'0x([0-9A-Fa-f]+)|(\d+)|"([^"]*)"')
   _p3=re.compile(r'\[(\d+)\]')
   def _parseInitValue(self,remain):      
      remain=remain.lstrip()   
      if remain.startswith('{'):
         (match,remain2)=_matchPair(remain,'{','}')
         elements=[]         
         while len(match)>0:
            match=match.lstrip()
            (elem,match)=self._parseInitValue(match)
            elements.append(elem)
            match=match.lstrip()
            if match.startswith(','):
               match=match[1:]
               match=match.lstrip()
            elif len(match)==0:
               return ({'type':'record','elements':elements},remain2)
            else:
               raise SyntaxError
      else:
         m=ApxPortAttribute._p2.match(remain)
         if m:
            remain=remain[m.end():]
            if m.group(1):
               return ({'type': 'integer', 'value': int(m.group(1),16)},remain)
            elif m.group(2):
               return ({'type': 'integer', 'value': int(m.group(2),10)},remain)
            elif m.group(3):
               return ({'type': 'string', 'value': m.group(3)},remain)
      return (None,remain)         

   
   def __init__(self,text):
      self.isQueued=False
      self.isParameter=False
      self.queueLength=None
      self.initValue=None
      self.str = text
      if text==None or len(text)==0:
         return
      remain=text
      while len(remain)>0:
         remain=remain.lstrip()
         if remain.startswith('='):
            remain=remain[1:]
            (initValue,remain)=self._parseInitValue(remain)
            self.initValue=initValue            
         elif remain.startswith('Q'):
            self.isQueued=True
            remain=remain[1:]
            m=ApxPortAttribute._p3.match(remain)
            if m:
               self.queueLength=m.group(1)
               remain=remain[m.end():]
            break
         elif remain.startswith('P'):
            self.isParameter=True
            remain=remain[1:]
         else:
            raise SyntaxError
   def __str__(self):
      return self.str
   
class ApxTypeAttribute(object):
   def __init__(self,text):
      self.valueTable = None
      self.str=text
      if text==None or len(text)==0:
         return
      remain = text
      while len(remain)>0:
         if remain.startswith('VT('):            
            (result,remain) = _matchPair(remain[2:],'(',')')
            if result == None:
               raise SyntaxError
            else:
               self.valueTable = []
               strings = result.split(',')
               for string in strings:
                  (name,remain2)=_parseStr(string)
                  self.valueTable.append(name)
         else:
            raise SyntaxError


class ApxGenBase(object):
   @staticmethod
   def _writeStructDef(fp,typeName,dsg):
      fp.write('typedef struct\n{\n')
      for elem in dsg['elements']:
         elemName = elem['name']
         (typeStr,pre,post)=ApxGenBase.deriveTypeStr(elem)
         fp.write('  %s %s%s%s;\n'%(typeStr,pre,elemName,post))
      fp.write('} %s;\n'%(typeName))
   
   @staticmethod
   def deriveTypeStr(item):
      pre=""
      post=""
      if item['type']=='c': s = 'sint8'
      elif item['type']=='C': s = 'uint8'
      elif item['type']=='s': s = 'sint16'
      elif item['type']=='S': s = 'sint16'
      elif item['type']=='l': s = 'sint32'
      elif item['type']=='L': s = 'uint32'
      elif item['type']=='a': s = 'uint8'
      else:
         raise NotImplementedError
      if item['isArray']:
         post='[%d]'%item['arrayLen']
      return (s,pre,post)


if __name__ == '__main__':
   print(ApxSplitLine('N"AuxiliaryBrakes_UOCtrl"'))
   print(ApxSplitLine('T"Percent8bit125NegOffset_T"C'))
   print(ApxSplitLine('P"PS_AuxBrakesDwngrdMode"T[9]:=7'))
   print(ApxSplitLine('R"TimeoutAuxiliaryBrakesIconRemove_P1AZ0"T[7]:P'))
   
