from autosar.base import parseXMLFile,splitRef,parseTextNode
from autosar.datatype import *
from autosar.parser.parser_base import BaseParser

class DataTypeParser(BaseParser):
   def __init__(self,handler,version=3.0):
      super().__init__(version)
      if version!=3.0:
         raise NotImplementedError('Version of ARXML not supported')
      self.handler=handler
         
   def parseIntegerType(self,root,rootProject=None,parent=None):    
      if self.version==3:         
         name=root.find("./SHORT-NAME").text
         minval = int(root.find("./LOWER-LIMIT").text)
         maxval = int(root.find("./UPPER-LIMIT").text)
         dataDefXML = root.find('./SW-DATA-DEF-PROPS')
         dataType = IntegerDataType(name,minval,maxval)
         self.parseDesc(root,dataType)
         if dataDefXML is not None:
            for elem in dataDefXML.findall('./*'):
               if elem.tag=='COMPU-METHOD-REF':
                  dataType.compuMethodRef=parseTextNode(elem)
               else:
                  raise NotImplementedError(elem.tag)
         return dataType
   
   def parseRecordType(self,root,rootProject=None,parent=None):
      if self.version==3.0:
         elements = []
         name=root.find("./SHORT-NAME").text         
         for elem in root.findall('./ELEMENTS/RECORD-ELEMENT'):
            elements.append({"name":elem.find("./SHORT-NAME").text,"typeRef":elem.find("./TYPE-TREF").text})
         dataType=RecordDataType(name,elements);
         self.parseDesc(root,dataType)   
         return dataType
      
   def parseArrayType(self,root,rootProject=None,parent=None):
      if self.version==3.0:
         name=root.find("./SHORT-NAME").text         
         length=int(root.find('ELEMENT/MAX-NUMBER-OF-ELEMENTS').text)
         typeRef=root.find('ELEMENT/TYPE-TREF').text
         dataType=ArrayDataType(name,typeRef,length)
         self.parseDesc(root,dataType)
         return dataType;

   def parseBooleanType(self,root,rootProject=None,parent=None):
      if self.version==3:
         name=root.find("./SHORT-NAME").text         
         dataType=BooleanDataType(name)
         self.parseDesc(root,dataType)
         return dataType

   def parseStringType(self,root,rootProject=None,parent=None):
      if self.version==3.0:
         name=root.find("./SHORT-NAME").text
         
         length=int(root.find('MAX-NUMBER-OF-CHARS').text)
         encoding=root.find('ENCODING').text
         dataType=StringDataType(name,length,encoding)
         self.parseDesc(root,dataType)
         return dataType

   def parseRealType(self,root,rootProject=None,parent=None):
      if self.version==3.0:
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
         dataType=RealDataType(name,minval,maxval,minvalType,maxvalType,hasNaN,encoding)
         self.parseDesc(root,dataType)
         return dataType


class DataTypeSemanticsParser(object):
   def __init__(self,pkg,version=3.0):
      if version == 3.0:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.pkg=pkg
      
   def parse(self,root):
      if self.version==3.0:
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
                  lowerLimit = parseTextNode(xmlItem.find('./LOWER-LIMIT'))
                  upperLimit = parseTextNode(xmlItem.find('./UPPER-LIMIT'))
                  textValue = parseTextNode(const.find('./VT'))
                  semanticElements.append({'lowerLimit':int(lowerLimit),'upperLimit':int(upperLimit), 'textValue': textValue})
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
   def __init__(self,handler,version=3.0):
      if version == 3.0:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.handler=handler
      
   def parseUnit(self,xmlElem,rootProject=None,parent=None):
      assert (xmlElem.tag == 'UNIT')
      name = xmlElem.find("./SHORT-NAME").text
      displayName = xmlElem.find("./DISPLAY-NAME").text
      return DataTypeUnitElement(name,displayName)
