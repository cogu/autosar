import sys
from autosar.base import parseXMLFile,splitRef,parseTextNode,hasAdminData,parseAdminDataNode
from autosar.datatype import *
from autosar.parser.parser_base import ElementParser

class DataTypeParser(ElementParser):
   def __init__(self,version=3.0):
      super().__init__(version)

      if self.version >= 3.0 and self.version < 4.0:
         self.switcher = {'ARRAY-TYPE': self.parseArrayType,
                          'BOOLEAN-TYPE': self.parseBooleanType,
                          'INTEGER-TYPE': self.parseIntegerType,
                          'REAL-TYPE': self.parseRealType,
                          'RECORD-TYPE': self.parseRecordType,
                          'STRING-TYPE': self.parseStringType}
      elif self.version >= 4.0:
         self.switcher = {
            'DATA-CONSTR': self.parseDataConstraint,
            'IMPLEMENTATION-DATA-TYPE': self.parseImplementationDataType,
            'SW-BASE-TYPE': self.parseSwBaseType,
            'DATA-TYPE-MAPPING-SET': self.parseDataTypeMappingSet,
            'APPLICATION-PRIMITIVE-DATA-TYPE': self.parseApplicationPrimitiveDataType
         }

   def getSupportedTags(self):
      return self.switcher.keys()

   def parseElement(self, xmlElement, parent = None):
      parseFunc = self.switcher.get(xmlElement.tag)
      if parseFunc is not None:
         return parseFunc(xmlElement,parent)
      else:
         return None


   def parseIntegerType(self,root,parent=None):
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

   def parseRecordType(self,root,parent=None):
      if self.version>=3.0:
         elements = []
         name=root.find("./SHORT-NAME").text
         for elem in root.findall('./ELEMENTS/RECORD-ELEMENT'):
            elements.append({"name":elem.find("./SHORT-NAME").text,"typeRef":elem.find("./TYPE-TREF").text})
         dataType=RecordDataType(name,elements);
         self.parseDesc(root,dataType)
         return dataType

   def parseArrayType(self,root,parent=None):
      if self.version>=3.0:
         name=root.find("./SHORT-NAME").text
         length=int(root.find('ELEMENT/MAX-NUMBER-OF-ELEMENTS').text)
         typeRef=root.find('ELEMENT/TYPE-TREF').text
         dataType=ArrayDataType(name,typeRef,length)
         self.parseDesc(root,dataType)
         return dataType;

   def parseBooleanType(self,root,parent=None):
      if self.version>=3:
         name=root.find("./SHORT-NAME").text
         dataType=BooleanDataType(name)
         self.parseDesc(root,dataType)
         return dataType

   def parseStringType(self,root,parent=None):
      if self.version>=3.0:
         name=root.find("./SHORT-NAME").text

         length=int(root.find('MAX-NUMBER-OF-CHARS').text)
         encoding=root.find('ENCODING').text
         dataType=StringDataType(name,length,encoding)
         self.parseDesc(root,dataType)
         return dataType

   def parseRealType(self,root,parent=None):
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

   def parseDataConstraint(self, xmlRoot, parent=None):
      assert (xmlRoot.tag == 'DATA-CONSTR')
      name = xmlRoot.find("./SHORT-NAME").text
      rules=[]
      for xmlItem in xmlRoot.findall('./DATA-CONSTR-RULES/DATA-CONSTR-RULE/*'):
         if xmlItem.tag == 'INTERNAL-CONSTRS':
            lowerLimitXML = xmlItem.find('./LOWER-LIMIT')
            upperLimitXML = xmlItem.find('./UPPER-LIMIT')
            lowerLimit = parseTextNode(lowerLimitXML)
            upperLimit = parseTextNode(upperLimitXML)
            lowerLimitType = 'CLOSED'
            upperLimitType = 'CLOSED'
            if lowerLimitXML.attrib['INTERVAL-TYPE']=='OPEN':
               lowerLimitType='OPEN'
            if upperLimitXML.attrib['INTERVAL-TYPE']=='OPEN':
               upperLimitType='OPEN'
            try:
               lowerLimit = int(lowerLimit)
            except ValueError:
               lowerLimit = str(lowerLimit)
            try:
               upperLimit = int(upperLimit)
            except ValueError:
               upperLimit = str(upperLimit)
            rules.append({'type': 'internalConstraint', 'lowerLimit':lowerLimit, 'upperLimit':upperLimit, 'lowerLimitType':lowerLimitType, 'upperLimitType':upperLimitType,})
         else:
            raise NotImplementedError(xmlItem.tag)
      elem = DataConstraint(name, rules, parent)
      if hasAdminData(xmlRoot):
         elem.adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
      return elem

   def parseImplementationDataType(self, xmlRoot, parent=None):
      assert (xmlRoot.tag == 'IMPLEMENTATION-DATA-TYPE')
      name = parseTextNode(xmlRoot.find("./SHORT-NAME"))
      category = parseTextNode(xmlRoot.find("./CATEGORY")) #category is a generic string identifier
      dataType = ImplementationDataType(name, category)
      self.parseDesc(xmlRoot,dataType)
      alreadyProcessed = ['SHORT-NAME','CATEGORY']
      for xmlItem in xmlRoot.findall('./*'):
         if xmlItem.tag in alreadyProcessed:
            pass
         elif xmlItem.tag == 'SW-DATA-DEF-PROPS':
            dataType.variants = self.parseSwDataDefProps(xmlItem)
         elif xmlItem.tag == 'ADMIN-DATA':
            dataType.adminData=parseAdminDataNode(xmlItem)
         elif xmlItem.tag == 'DESC':
            self.parseDesc(xmlItem, dataType)
         elif xmlItem.tag == 'TYPE-EMITTER':
            dataType.typeEmitter = parseTextNode(xmlItem)
         elif xmlItem.tag == 'DYNAMIC-ARRAY-SIZE-PROFILE':
            dataType.dynamicArraySize = parseTextNode(xmlItem)
         elif xmlItem.tag == 'SUB-ELEMENTS':
            dataType.subElements = self.parseImplementationDataTypeSubElements(xmlItem, dataType)
         else:
            raise NotImplementedError(xmlItem.tag)
      return dataType


   def parseImplementationDataTypeSubElements(self, xmlRoot, parent):
      assert (xmlRoot.tag == 'SUB-ELEMENTS')
      elements = []
      for xmlItem in xmlRoot.findall('./*'):
         if xmlItem.tag == 'IMPLEMENTATION-DATA-TYPE-ELEMENT':
            elements.append(self.parseImplementationDataTypeElement(xmlItem, parent))
         else:
            raise NotImplementedError(xmlItem.tag)
      return elements

   def parseImplementationDataTypeElement(self, xmlRoot, parent):
      assert (xmlRoot.tag == 'IMPLEMENTATION-DATA-TYPE-ELEMENT')
      (name, category, arraySize, arraySizeSemantics, variants) = (None, None, None, None, None)
      for xmlItem in xmlRoot.findall('./*'):
         if xmlItem.tag == 'SHORT-NAME':
            name = parseTextNode(xmlItem)
         elif xmlItem.tag == 'CATEGORY':
            category = parseTextNode(xmlItem)
         elif xmlItem.tag == 'SW-DATA-DEF-PROPS':
            variants = self.parseSwDataDefProps(xmlItem)
         elif xmlItem.tag == 'ARRAY-SIZE':
            arraySize = parseTextNode(xmlItem)
         elif xmlItem.tag == 'ARRAY-SIZE-SEMANTICS':
            arraySizeSemantics = parseTextNode(xmlItem)
         else:
            raise NotImplementedError(xmlItem.tag)
      return ImplementationDataTypeElement(name, category, arraySize, arraySizeSemantics, variants, parent)

   def parseSwBaseType(self, xmlRoot, parent = None):
      assert (xmlRoot.tag == 'SW-BASE-TYPE')
      name = parseTextNode(xmlRoot.find('SHORT-NAME'))
      size = parseTextNode(xmlRoot.find('BASE-TYPE-SIZE'))
      typeEncoding = parseTextNode(xmlRoot.find('BASE-TYPE-ENCODING'))
      nativeDeclaration = parseTextNode(xmlRoot.find('NATIVE-DECLARATION'))
      category = parseTextNode(xmlRoot.find('CATEGORY'))
      if hasAdminData(xmlRoot):
         adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
      else:
         adminData=None
      elem = SwBaseType(name, size, typeEncoding, nativeDeclaration, category, parent, adminData)
      self.parseDesc(xmlRoot,elem)
      return elem

   def parseDataTypeMappingSet(self, xmlRoot, parent = None):
      assert (xmlRoot.tag == 'DATA-TYPE-MAPPING-SET')
      (name, dataTypeMaps, adminData) = (None, None, None)
      dataTypeMaps = []
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'ADMIN-DATA':
            adminData=parseAdminDataNode(xmlItem)
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'DATA-TYPE-MAPS':
            for xmlChild in xmlElem.findall('./*'):
               if xmlChild.tag == 'DATA-TYPE-MAP':
                  dataTypeMap = self.parseDataTypeMap(xmlChild)
                  assert(dataTypeMap is not None)
                  dataTypeMaps.append(dataTypeMap)
               else:
                  raise NotImplementedError(xmlElem.tag)               
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is None):
         raise RuntimeError('SHORT-NAME cannot be None')         
      elem = DataTypeMappingSet(name, parent, adminData)
      for dataTypeMap in dataTypeMaps:
         elem.add(dataTypeMap)
      return elem

   def parseApplicationPrimitiveDataType(self, xmlRoot, parent = None):
      assert (xmlRoot.tag == 'APPLICATION-PRIMITIVE-DATA-TYPE')
      (name, category, variants, adminData, desc) = (None, None, None, None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'ADMIN-DATA':
            adminData = self.parseAdminData(xmlElem)
         elif xmlElem.tag == 'DESC':
            desc = self.parseDescDirect(xmlElem)
         elif xmlElem.tag == 'SHORT-NAME':
            name = parseTextNode(xmlElem)
         elif xmlElem.tag == 'CATEGORY':
            category = parseTextNode(xmlElem)
         elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
            variants = self.parseSwDataDefProps(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is None):
         raise RuntimeError('SHORT-NAME cannot be None')
      elem = ApplicationPrimitiveDataType(name, category, variants, parent, adminData)      
      if desc is not None:
         elem.desc=desc[0]
         elem.descAttr=desc[1]
      return elem

   def parseDataTypeMap(self, xmlRoot):
      assert (xmlRoot.tag == 'DATA-TYPE-MAP')
      (applicationDataTypeRef, implementationDataTypeRef) = (None, None)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'APPLICATION-DATA-TYPE-REF':
            applicationDataTypeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
            implementationDataTypeRef = self.parseTextNode(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      return DataTypeMap(applicationDataTypeRef, implementationDataTypeRef)
         
      

class DataTypeSemanticsParser(ElementParser):
   def __init__(self,version=3.0):
      self.version=version

   def getSupportedTags(self):
      return ['COMPU-METHOD']

   def parseElement(self, xmlElement, parent = None):
      if xmlElement.tag == 'COMPU-METHOD':
         return self.parseCompuMethod(xmlElement, parent)
      else:
         return None

   def parseCompuMethod(self,xmlRoot,parent=None):
      assert (xmlRoot.tag == 'COMPU-METHOD')
      name = parseTextNode(xmlRoot.find("./SHORT-NAME"))
      category = parseTextNode(xmlRoot.find("./CATEGORY"))
      unitRef = xmlRoot.find("./UNIT-REF")
      semanticsType = None
      semanticElements=[]
      if hasAdminData(xmlRoot):
         adminData=parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
      else:
         adminData=None
      xmlCompuScales = xmlRoot.findall('./COMPU-INTERNAL-TO-PHYS/COMPU-SCALES/COMPU-SCALE')
      if xmlCompuScales is None:
         raise NotImplementedError("No COMPU-SCALE? item=%s"%name)
      else:
         for xmlItem in xmlCompuScales:
            rational = xmlItem.find('./COMPU-RATIONAL-COEFFS')
            const = xmlItem.find('./COMPU-CONST')
            label = self.parseTextNode(xmlItem.find('./SHORT-LABEL'))
            mask = self.parseIntNode(xmlItem.find('./MASK'))
            symbol = self.parseTextNode(xmlItem.find('./SYMBOL'))
            if rational is not None:
               if (semanticsType is not None) and (semanticsType !='compuRational'):
                  raise NotImplementedError('mixed compuscales not supported, item=%s'%name)
               else:
                  semanticsType='compuRational'
                  v=rational.findall('./COMPU-NUMERATOR/V')
                  offset=v[0].text
                  numerator=v[1].text
                  denominator=rational.find('./COMPU-DENOMINATOR/V').text
                  semanticElements.append({'offset':offset, 'numerator':numerator, 'denominator':denominator, 'label':label, 'symbol': symbol})
            if const is not None:
               if (semanticsType is not None) and (semanticsType !='compuConst'):
                  raise NotImplementedError('mixed compuscales not supported, item=%s'%name)
               else:
                  semanticsType='compuConst'
                  lowerLimit = parseTextNode(xmlItem.find('./LOWER-LIMIT'))
                  upperLimit = parseTextNode(xmlItem.find('./UPPER-LIMIT'))
                  textValue = parseTextNode(const.find('./VT'))
                  semanticElements.append({'lowerLimit':int(lowerLimit),'upperLimit':int(upperLimit), 'textValue': textValue, 'label': label, 'symbol': symbol})
            if mask is not None:
               if (semanticsType is not None) and (semanticsType !='compuMask'):
                  raise NotImplementedError('mixed compuscales not supported, item=%s'%name)
               else:
                  semanticsType='compuMask'
                  lowerLimit = parseTextNode(xmlItem.find('./LOWER-LIMIT'))
                  upperLimit = parseTextNode(xmlItem.find('./UPPER-LIMIT'))
                  semanticElements.append({'lowerLimit':int(lowerLimit),'upperLimit':int(upperLimit), 'mask': mask, 'label': label, 'symbol': symbol})

      if semanticsType == 'compuRational':
         if unitRef is not None: unitRef=unitRef.text
         method=CompuMethodRational(name, unitRef, semanticElements, category=category, adminData=adminData)
         return method
      elif semanticsType == 'compuConst':
         method = CompuMethodConst(name, semanticElements, category=category, adminData=adminData)
         return method
      elif semanticsType == 'compuMask':
         method = CompuMethodMask(name, semanticElements, category=category, adminData=adminData)
         return method      
      else:
         raise ValueError("unprocessed semanticsType,item=%s"%name)

class DataTypeUnitsParser(ElementParser):
   def __init__(self,version=3.0):
      super().__init__(version)


   def getSupportedTags(self):
      return ['UNIT']

   def parseElement(self, xmlElement, parent = None):
      if xmlElement.tag == 'UNIT':
         return self.parseUnit(xmlElement, parent)
      else:
         return None

   def parseUnit(self,xmlRoot,rootProject=None,parent=None):
      assert (xmlRoot.tag == 'UNIT')
      name = parseTextNode(xmlRoot.find("./SHORT-NAME"))
      displayName = parseTextNode(xmlRoot.find("./DISPLAY-NAME"))
      if self.version>=4.0:
         factor = parseTextNode(xmlRoot.find("./FACTOR-SI-TO-UNIT"))
         offset = parseTextNode(xmlRoot.find("./OFFSET-SI-TO-UNIT"))
      else:
         (factor,offset) = (None, None)
      return DataTypeUnitElement(name, displayName, factor, offset, parent)


