from autosar.package import Package
from autosar.element import Element
from autosar.base import parseXMLFile,splitref,parseTextNode
import math
import json

#RecordTypeElement=namedtuple('RecordTypeElement',['name','typeRef'])
#CompuConstElement=namedtuple('CompuConstElement','minvalue maxvalue textvalue')
#CompuRationalElement=namedtuple('CompuRationalElement','offset numerator denominator')
#DataTypeUnitElement = namedtuple('DataTypeUnitElement','name displayName')

class ConstElement(object):
   def asdict(self):
      data={'type': self.__class__.__name__}
      data.update(self.__dict__)
      return data


class RecordTypeElement(ConstElement):
   def __init__(self,name,typeRef):
      self.name=name
      self.typeRef=typeRef

class CompuConstElement(ConstElement):
   def __init__(self,minvalue,maxvalue,textvalue):
      self.minval=minvalue
      self.maxval=maxvalue
      self.textval=textvalue

class CompuRationalElement(ConstElement):
   def __init__(self,offset,numerator,denominator):
      self.offset=offset
      self.numerator=numerator
      self.denominator=denominator

class DataTypeUnitElement(Element):
   def __init__(self,name,displayName):
      super().__init__(name)
      self.displayName=displayName

class DataType(Element):
   name = None
   def __init__(self,name):
      super().__init__(name)      


class IntegerDataType(DataType):
   tag = 'INTEGER-TYPE'
   def __init__(self,name,minval=0,maxval=0,compuMethodRef=None):
      super().__init__(name)
      self.minval = minval
      self.maxval = maxval
      if isinstance(compuMethodRef,str):
         self.compuMethodRef=compuMethodRef
      elif hasattr(compuMethodRef,'ref'):
         self.compuMethodRef=compuMethodRef.ref
      else:
         self.compuMethodRef=None
      
class RecordDataType(DataType):
   tag = 'RECORD-TYPE'   
   def __init__(self,name,_elements):
      super().__init__(name)
      self.elements = []
      for elem in _elements:
         self.elements.append(RecordTypeElement(elem['name'],elem['typeRef']))
   def asdict(self):         
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      if self.adminData is not None:
         data['adminData']=self.adminData.asdict()      
      for elem in self.elements:
         data['elements'].append(elem.asdict())
      return data

class ArrayDataType(DataType):
   tag = 'ARRAY-TYPE'
   def __init__(self,name,typeRef,length):
      super().__init__(name)
      self.typeRef = typeRef
      self.length = length

class BooleanDataType(DataType):
   tag = 'BOOLEAN-TYPE'
   def __init__(self,name):
      super().__init__(name)


class StringDataType(DataType):
   tag = 'STRING-TYPE'
   def __init__(self,name,length,encoding):
      super().__init__(name)
      self.length=length
      self.encoding=encoding
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'encoding':self.encoding,'length':self.length}
      return data

      
class RealDataType(DataType):
   tag = 'REAL-TYPE'
   def __init__(self,name,minval,maxval,minvalType='CLOSED',maxvalType='CLOSED',hasNaN=False,encoding='single'):
      super().__init__(name)
      self.minval=minval
      self.maxval=maxval
      self.minvalType = minvalType
      self.maxvalType = maxvalType
      self.hasNaN=hasNaN
      self.encoding=encoding
      
class DataTypeParser(object):
   def __init__(self,handler,version=3):
      if version==3:
         self.version=version
      else:
         raise NotImplementedError('Version of ARXML not supported')
      self.handler=handler
   
   def parse(self,root):
      #for subPackage in root.findall('./SUB-PACKAGES/AR-PACKAGE'):
      #   pkgName = subPackage.find('./SHORT-NAME').text
      #   if pkgName == 'DataTypeSemantics':
      #      self.handler.semanticsPackage = DataTypeSemanticsPackage()
      #      self.handler.semanticsPackage.loadFromXML(subPackage,self.version)
      #   elif pkgName == 'DataTypeUnits':
      #      self.handler.datatypeUnitsPackage = DataTypeUnitsPackage()
      #      self.handler.datatypeUnitsPackage.loadFromXML(subPackage,self.version)
      #   else:
      #      print("unhandled subpackage: %s"%pkgName)
            
      for elem in root.findall('./ELEMENTS/*'):
         parseElement()
   
   def parseElement(self, xmlElement):
      dataType = None
      if xmlElement.tag=='INTEGER-TYPE':
         dataType = self.parseIntegerType(xmlElement)         
      elif xmlElement.tag=='RECORD-TYPE':
         dataType = self.parseRecordType(xmlElement)         
      elif xmlElement.tag=='ARRAY-TYPE':
         dataType = self.parseArrayType(xmlElement)         
      elif xmlElement.tag=='STRING-TYPE':
         dataType = self.parseStringType(xmlElement)         
      elif xmlElement.tag=='BOOLEAN-TYPE':
         dataType = self.parseBooleanType(xmlElement)         
      elif xmlElement.tag=='REAL-TYPE':
         dataType = self.parseRealType(xmlElement)         
      else:
         pass
      if dataType is None:
         print("<%s> not parsed"%xmlElement.tag)
      return dataType   
      
   def parseIntegerType(self,root,rootProject=None,parent=None):      
      if self.version==3:
         name=root.find("./SHORT-NAME").text
         minval = int(root.find("./LOWER-LIMIT").text)
         maxval = int(root.find("./UPPER-LIMIT").text)
         dataDefXML = root.find('./SW-DATA-DEF-PROPS')
         dataType = IntegerDataType(name,minval,maxval)
         if dataDefXML is not None:
            for elem in dataDefXML.findall('./*'):
               if elem.tag=='COMPU-METHOD-REF':
                  dataType.compuMethodRef=parseTextNode(elem)
               else:
                  raise NotImplementedError(elem.tag)
         return dataType
   
   def parseRecordType(self,root,rootProject=None,parent=None):
      if self.version==3:
         elements = []
         name=root.find("./SHORT-NAME").text
         for elem in root.findall('./ELEMENTS/RECORD-ELEMENT'):
            elements.append({"name":elem.find("./SHORT-NAME").text,"typeRef":elem.find("./TYPE-TREF").text})
         return RecordDataType(name,elements);
      
   def parseArrayType(self,root,rootProject=None,parent=None):
      if self.version==3:
         name=root.find("./SHORT-NAME").text
         length=int(root.find('ELEMENT/MAX-NUMBER-OF-ELEMENTS').text)
         typeRef=root.find('ELEMENT/TYPE-TREF').text
         return ArrayDataType(name,typeRef,length);

   def parseBooleanType(self,root,rootProject=None,parent=None):
      if self.version==3:
         name=root.find("./SHORT-NAME").text
         return BooleanDataType(name)

   def parseStringType(self,root,rootProject=None,parent=None):
      if self.version==3:
         name=root.find("./SHORT-NAME").text
         length=int(root.find('MAX-NUMBER-OF-CHARS').text)
         encoding=root.find('ENCODING').text
         return StringDataType(name,length,encoding)

   def parseRealType(self,root,rootProject=None,parent=None):
      if self.version==3:
         name=root.find("./SHORT-NAME").text
         elem = root.find("./LOWER-LIMIT")
         if elem is not None:
            minval = elem.text
            minvalType = elem.attrib['INTERVAL-TYPE']
         elem = root.find("./UPPER-LIMIT")
         if elem is not None:
            maxval = elem.text
            maxvalType = elem.attrib['INTERVAL-TYPE']
         hasNaN = True if root.find("./ALLOW-NAN").text == 'true' else False
         encoding = root.find("./ENCODING").text         
         return RealDataType(name,minval,maxval,minvalType,maxvalType,hasNaN,encoding)

class CompuMethodRational(Element):   
   def __init__(self,name,unitRef,elements):      
      super().__init__(name)
      self.unitRef = unitRef
      self.elements = []
      for elem in elements:
         self.elements.append(CompuRationalElement(**elem))
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data

      
class CompuMethodConst(Element):
   def __init__(self,name,elements):
      super().__init__(name)
      self.elements = []
      for elem in elements:
         if isinstance(elem,str):
            index=len(self.elements)
            self.elements.append(CompuConstElement(minvalue=index,maxvalue=index,textvalue=elem))
         elif isinstance(elem,dict):
            self.elements.append(CompuConstElement(**elem))
         elif isinstance(elem,tuple):
            if len(elem==2):
               self.elements.append(CompuConstElement(minvalue=elem[0],maxvalue=elem[0],textvalue=elem[1]))
            elif len(elem==3):
               self.elements.append(CompuConstElement(*elem))
            else:
               raise ValueError('invalid length: %d'%len(elem))
         else:
            raise ValueError('type not supported:%s'%str(type(elem)))
   def asdict(self):
      data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
      for element in self.elements:
         data['elements'].append(element.asdict())
      return data

   
   def getValueTable(self):
      retval = []
      i = 0
      for elem in self.elements:
         if (elem.minvalue == elem.maxvalue) and elem.minvalue==i:
            retval.append(elem.textvalue)
         else:
            return None
         i+=1      
      return retval if len(retval)>0 else None

class DataTypeSemanticsParser(object):
   def __init__(self,pkg,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.pkg=pkg
      
   def parse(self,root):
      if self.version==3:
         for xmlElement in root.findall('./ELEMENTS/*'):
            element = self.parseElement(xmlElement)
   
   def parseElement(self,xmlElement):
      name = xmlElement.find("./SHORT-NAME").text
              
      if xmlElement.tag == 'COMPU-METHOD':
         pass
      else:
         raise NotImplementedError("<%s>"%elem.tag)
   
   def parseCompuMethod(self,xmlElem,rootProject=None,parent=None):      
      assert (xmlElem.tag == 'COMPU-METHOD')
      name = xmlElem.find("./SHORT-NAME").text
      unitRef = xmlElem.find("./UNIT-REF")
      semanticsType = None
      semanticElements=[]
      xmlCompuScales = xmlElem.findall('./COMPU-INTERNAL-TO-PHYS/COMPU-SCALES/COMPU-SCALE')
      if xmlCompuScales is None:
         raise NotImplementedError("No COMPU-SCALE? item=%s"%name)
      else:                  
         for xmlItem in xmlCompuScales:
            rational = xmlItem.find('./COMPU-RATIONAL-COEFFS')
            const = xmlItem.find('./COMPU-CONST')
            if rational is not None:
               if (semanticsType is not None) and (semanticsType !='compuRational'):
                  raise NotImplementedError('mixed compuscales not supported, item=%s'%name)
               else:
                  semanticsType='compuRational'
                  v=rational.findall('./COMPU-NUMERATOR/V')
                  offset=v[0].text
                  numerator=v[1].text
                  denominator=rational.find('./COMPU-DENOMINATOR/V').text
                  semanticElements.append({'offset':offset, 'numerator':numerator, 'denominator':denominator})                                 
            if const is not None:
               if (semanticsType is not None) and (semanticsType !='compuConst'):
                  raise NotImplementedError('mixed compuscales not supported, item=%s'%name)
               else:
                  semanticsType='compuConst'
                  minvalue = xmlItem.find('./LOWER-LIMIT').text
                  maxvalue = xmlItem.find('./UPPER-LIMIT').text
                  textValue = const.find('./VT').text
                  semanticElements.append({'minvalue':int(minvalue),'maxvalue':int(maxvalue), 'textvalue': textValue})
      if semanticsType == 'compuRational':
         if unitRef is not None: unitRef=unitRef.text
         method=CompuMethodRational(name,unitRef,semanticElements)
         return method
      elif semanticsType == 'compuConst':
         method = CompuMethodConst(name,semanticElements)
         return method
      else:
         raise ValueError("unprocessed semanticsType,item=%s"%name)

class DataTypeUnitsParser(object):
   def __init__(self,handler,version=3):
      if version == 3:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.handler=handler
      
   def parseUnit(self,xmlElem,rootProject=None,parent=None):
      assert (xmlElem.tag == 'UNIT')
      name = xmlElem.find("./SHORT-NAME").text
      displayName = xmlElem.find("./DISPLAY-NAME").text
      return DataTypeUnitElement(name,displayName)

      

class DataTypeGenerator(object):   
   #@staticmethod
   #def _calcBitLenFromMinMax(minval,maxval):
   #   if (maxval-minval)>0:
   #      if minval<0:
   #         return int(math.ceil(math.log(abs(maxval),2)))+1
   #      else:
   #         return int(math.ceil(math.log(maxval,2)))
   #   return 0
   #@staticmethod
   #def _derivePlatformType(minval,maxval):
   #      bits = DataTypeGenerator._calcBitLenFromMinMax(minval,maxval)
   #      if bits > 0:
   #         if minval<0:
   #            if bits<=8:
   #               return 'sint8'
   #            elif bits<=16:
   #               return 'sint16'
   #            elif bits<=32:
   #               return 'sint32'
   #            elif bits<=64:
   #               return 'sint64'
   #            else:
   #               raise ValueError('too many bits')
   #         else:
   #            if bits<=8:
   #               return 'uint8'
   #            elif bits<=16:
   #               return 'uint16'
   #            elif bits<=32:
   #               return 'uint32'
   #            elif bits<=64:
   #               return 'uint64'
   #            else:
   #               raise ValueError('too many bits')
   #
   #      return None
   #def storeAPD(self,dataTypePkg,fp):
   #   for dt in dataTypePkg.integerTypes:
   #      lines = []
   #      platformType = self._derivePlatformType(dt.minval,dt.maxval)
   #      if platformType != None:
   #         lines.append('typedef %s(%s)'%(dt.name,platformType))
   #         fp.write('\n'.join(lines)+'\n')
   #         obj = {'minval':dt.minval, 'maxval':dt.maxval}
   #         if dataTypePkg.semanticsPackage is not None:
   #            compuMethod = dataTypePkg.semanticsPackage.findCompuMethod(dt.name)
   #            if compuMethod is not None:
   #               if isinstance(compuMethod,CompuMethodConst):
   #                  vt = compuMethod.getValueTable()
   #                  if vt is not None: obj['vt']=vt
   #         json.dump(obj,fp,indent=3)
   #         fp.write('\n\n')
            
   def __init__(self,datatypePackage):
      self.datatypePackage = datatypePackage
   
   def genXML(self,fp):
      lines = []
   
   

class DataTypeSemanticsPackage(object):
   def __init__(self):      
      self.elements=[]      
   def loadFromXML(self,root,version=3):
      parser = DataTypeSemanticsParser(self,version)
      parser.parse(root)
   
   def addCompuMethod(self,method):
      if isinstance(method,(CompuMethodConst,CompuMethodRational)):
         self.elements.append(method)
      else:
         raise ValueError('invalid type detected')
   
   def findCompuMethod(self,name):
      for elem in self.elements:
         if name==elem.name:
            return elem
      return None

class DataTypeUnitsPackage(object):
   def __init__(self):
      self.elements=[]
   
   def loadFromXML(self,root,version=3):
      parser = DataTypeUnitsParser(self,version)
      parser.parse(root)
      
   def addUnit(self,name,displayName):
      self.elements.append(DataTypeUnitElement(name,displayName))

#class DataTypePackage(Package):
#   def __init__(self):
#      self.integerTypes = []
#      self.recordTypes = []
#      self.arrayTypes = []
#      self.stringTypes = []
#      self.booleanTypes = []
#      self.realTypes= []
#      self.semanticsPackage = None
#      self.datatypeUnitsPackage = None
#      super().__init__('DataType')
#   
#   def loadFromXML(self,root,version=3):
#      if version == 3:
#         parser = DataTypeParser(self,version)
#         parser.parse(root)
#      else:
#         raise NotImplementedError('Version of ARXML not supported')

#   def storeAPD(self,fp):
#      generator = DataTypeGenerator()
#      generator.storeAPD(self,fp)
   