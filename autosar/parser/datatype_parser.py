import sys
from autosar.base import parseXMLFile,splitRef,parseTextNode
from autosar.datatype import *
from autosar.parser.parser_base import BaseParser

class DataTypeParser(BaseParser):
   def __init__(self,handler,version=3.0):
      super().__init__(version)
      self.version=version
      self.handler=handler
         
   def parseIntegerType(self,root,rootProject=None,parent=None):    
      if self.version>=3.0:
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
      if self.version>=3.0:
         elements = []
         name=root.find("./SHORT-NAME").text         
         for elem in root.findall('./ELEMENTS/RECORD-ELEMENT'):
            elements.append({"name":elem.find("./SHORT-NAME").text,"typeRef":elem.find("./TYPE-TREF").text})
         dataType=RecordDataType(name,elements);
         self.parseDesc(root,dataType)   
         return dataType
      
   def parseArrayType(self,root,rootProject=None,parent=None):
      if self.version>=3.0:
         name=root.find("./SHORT-NAME").text         
         length=int(root.find('ELEMENT/MAX-NUMBER-OF-ELEMENTS').text)
         typeRef=root.find('ELEMENT/TYPE-TREF').text
         dataType=ArrayDataType(name,typeRef,length)
         self.parseDesc(root,dataType)
         return dataType;

   def parseBooleanType(self,root,rootProject=None,parent=None):
      if self.version>=3:
         name=root.find("./SHORT-NAME").text         
         dataType=BooleanDataType(name)
         self.parseDesc(root,dataType)
         return dataType

   def parseStringType(self,root,rootProject=None,parent=None):
      if self.version>=3.0:
         name=root.find("./SHORT-NAME").text
         
         length=int(root.find('MAX-NUMBER-OF-CHARS').text)
         encoding=root.find('ENCODING').text
         dataType=StringDataType(name,length,encoding)
         self.parseDesc(root,dataType)
         return dataType

   def parseRealType(self,root,rootProject=None,parent=None):
      if self.version>=3.0:
         name=root.find("./SHORT-NAME").text
         
         elem = root.find("./LOWER-LIMIT")
         if elem is not None:
            minval = elem.text
            minvalType = elem.attrib['INTERVAL-TYPE']
         elem = root.find("./UPPER-LIMIT")
         if elem is not None:
            maxval = elem.text
            maxvalType = elem.attrib['INTERVAL-TYPE']
         hasNaNText = parseTextNode(root.find("./ALLOW-NAN"))         
         hasNaN = True if (hasNaNText is not None and hasNaNText == 'true') else False
         encoding = parseTextNode(root.find("./ENCODING"))
         dataType=RealDataType(name,minval,maxval,minvalType,maxvalType,hasNaN,encoding)
         self.parseDesc(root,dataType)
         return dataType
   
   def parseDataConstraint(self, xmlRoot, dummy, parent=None):
      assert (xmlRoot.tag == 'DATA-CONSTR')
      name = xmlRoot.find("./SHORT-NAME").text
      rules=[]
      for xmlItem in xmlRoot.findall('./DATA-CONSTR-RULES/DATA-CONSTR-RULE/*'):
         if xmlItem.tag == 'INTERNAL-CONSTRS':            
            lowerLimit = parseTextNode(xmlItem.find('./LOWER-LIMIT'))
            upperLimit = parseTextNode(xmlItem.find('./UPPER-LIMIT'))
            try:
               lowerLimit = int(lowerLimit)
            except ValueError:
               lowerLimit = str(lowerLimit)
            try:
               upperLimit = int(upperLimit)
            except ValueError:
               upperLimit = str(upperLimit)
            rules.append({'type': 'internalConstraint', 'lowerLimit':lowerLimit, 'upperLimit':upperLimit})
         else:
            raise NotImplementedError(xmlItem.tag)
      return DataConstraint(name, rules, parent)
   
   def parseImplementationDataType(self, xmlRoot, dummy, parent=None):
      assert (xmlRoot.tag == 'IMPLEMENTATION-DATA-TYPE')
      name = parseTextNode(xmlRoot.find("./SHORT-NAME"))
      category = parseTextNode(xmlRoot.find("CATEGORY")) #category is a generic string identifier
      dataType = ImplementationDataType(name, category)
      self.parseDesc(xmlRoot,dataType)
      for xmlItem in xmlRoot.findall('./SW-DATA-DEF-PROPS/SW-DATA-DEF-PROPS-VARIANTS/*'):
         if xmlItem.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL':
            self.parseSwDataDefPropsConditional(xmlItem, dataType)
         else:
            raise NotImplementedError(xmlItem.tag)
      return dataType
      
   def parseSwDataDefPropsConditional(self, xmlRoot, parent=None):
      assert (xmlRoot.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL')
      (baseTypeRef, swCalibrationAccess, compuMethodRef, dataConstraintRef, swPointerTargetPropsXML) = (None, None, None, None, None)
      for xmlItem in xmlRoot.findall('./*'):
         if xmlItem.tag == 'BASE-TYPE-REF':
            baseTypeRef = parseTextNode(xmlItem)
         elif xmlItem.tag == 'SW-CALIBRATION-ACCESS':
            swCalibrationAccess = parseTextNode(xmlItem)
         elif xmlItem.tag == 'COMPU-METHOD-REF':
            compuMethodRef = parseTextNode(xmlItem)
         elif xmlItem.tag == 'DATA-CONSTR-REF':
            dataConstraintRef = parseTextNode(xmlItem)         
         elif xmlItem.tag == 'SW-POINTER-TARGET-PROPS':
            swPointerTargetPropsXML = xmlItem            
         elif xmlItem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
            pass
         else:
            raise NotImplementedError(xmlItem.tag)
         variant = SwDataDefPropsConditional(baseTypeRef, swCalibrationAccess, compuMethodRef, dataConstraintRef, parent)
         if swPointerTargetPropsXML is not None:
            variant.swPointerTargetProps = self.parseSwPointerTargetProps(swPointerTargetPropsXML, variant)
         parent.variants.append(variant)

   def parseSwPointerTargetProps(self, rootXML, parent = None):
      return None

class DataTypeSemanticsParser(object):
   def __init__(self,pkg,version=3.0):
      self.version=version
      self.pkg=pkg
      
   def parse(self,root):
      if self.version>=3.0:
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
      self.version=version
      self.handler=handler
      
   def parseUnit(self,xmlElem,rootProject=None,parent=None):
      assert (xmlElem.tag == 'UNIT')
      name = xmlElem.find("./SHORT-NAME").text
      displayName = xmlElem.find("./DISPLAY-NAME").text
      return DataTypeUnitElement(name,displayName)

