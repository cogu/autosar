import abc
from autosar.base import (AdminData, SpecialDataGroup, SpecialData, SwDataDefPropsConditional, SwPointerTargetProps)
from autosar.element import DataElement

def _parseBoolean(value):
   if value is None:
      return None   
   if isinstance(value,str):
      if value == 'true': return True
      elif value =='false': return False
   raise ValueError(value) 

class BaseParser():
   def __init__(self,version=None):
      self.version=version

   def parseDesc(self,xmlRoot,elem):
      xmlDesc = xmlRoot.find('DESC')
      if xmlDesc is not None:
         L2Xml = xmlDesc.find('L-2')
         if L2Xml is not None:
            L2Text=self.parseTextNode(L2Xml)
            L2Attr=L2Xml.attrib['L']
            elem.desc=L2Text
            elem.descAttr=L2Attr
   
   def parseDescDirect(self,xmlDesc):
      assert(xmlDesc.tag == 'DESC')
      L2Xml = xmlDesc.find('L-2')
      if L2Xml is not None:
         L2Text=self.parseTextNode(L2Xml)
         L2Attr=L2Xml.attrib['L']
         return (L2Text, L2Attr)
      return (None, None)

   def parseTextNode(self, xmlElem):
      return None if xmlElem is None else xmlElem.text
   
   def parseIntNode(self, xmlElem):
      return None if xmlElem is None else int(xmlElem.text)
      
   def parseFloatNode(self, xmlElem):
      return None if xmlElem is None else float(xmlElem.text)
   
   def parseBooleanNode(self, xmlElem):
      return None if xmlElem is None else _parseBoolean(xmlElem.text)

   def hasAdminData(self, xmlRoot):
      return True if xmlRoot.find('ADMIN-DATA') is not None else False
      
   def parseAdminDataNode(self, xmlRoot):
      if xmlRoot is None: return None
      assert(xmlRoot.tag=='ADMIN-DATA')      
      adminData=AdminData()
      xmlSDGS = xmlRoot.find('./SDGS')
      if xmlSDGS is not None:
         for xmlElem in xmlSDGS.findall('./SDG'):
            SDG_GID=xmlElem.attrib['GID']
            specialDataGroup = SpecialDataGroup(SDG_GID)
            for xmlChild in xmlElem.findall('./*'):
               if xmlChild.tag == 'SD':
                  SD_GID = None
                  TEXT=xmlChild.text
                  try:
                     SD_GID=xmlChild.attrib['GID']
                  except KeyError: pass
                  specialDataGroup.SD.append(SpecialData(TEXT, SD_GID))   
               else:
                  raise NotImplementedError(xmlChild.tag)
            adminData.specialDataGroups.append(specialDataGroup)
      return adminData
   
   def parseSwDataDefProps(self, xmlRoot):
      assert (xmlRoot.tag == 'SW-DATA-DEF-PROPS')
      variants = []
      for itemXML in xmlRoot.findall('./*'):
         if itemXML.tag == 'SW-DATA-DEF-PROPS-VARIANTS':
            for subItemXML in itemXML.findall('./*'):
               if subItemXML.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL':
                  variant = self.parseSwDataDefPropsConditional(subItemXML)
                  assert(variant is not None)
                  variants.append(variant)
               else:
                  raise NotImplementedError(subItemXML.tag)
         else:
            raise NotImplementedError(itemXML.tag)
      return variants

   def parseSwDataDefPropsConditional(self, xmlRoot):
      assert (xmlRoot.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL')
      (baseTypeRef, implementationTypeRef, swCalibrationAccess, compuMethodRef, dataConstraintRef,
       swPointerTargetPropsXML, swImplPolicy, swAddressMethodRef, unitRef) = (None, None, None, None, None, None, None, None, None)
      for xmlItem in xmlRoot.findall('./*'):
         if xmlItem.tag == 'BASE-TYPE-REF':
            baseTypeRef = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'SW-CALIBRATION-ACCESS':
            swCalibrationAccess = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'COMPU-METHOD-REF':
            compuMethodRef = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'DATA-CONSTR-REF':
            dataConstraintRef = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'SW-POINTER-TARGET-PROPS':
            swPointerTargetPropsXML = xmlItem
         elif xmlItem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
            implementationTypeRef = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'SW-IMPL-POLICY':
            swImplPolicy = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'SW-ADDR-METHOD-REF':
            swAddressMethodRef = self.parseTextNode(xmlItem)
         elif xmlItem.tag == 'UNIT-REF':
            unitRef = self.parseTextNode(xmlItem)
         else:
            raise NotImplementedError(xmlItem.tag)
      variant = SwDataDefPropsConditional(baseTypeRef, implementationTypeRef, swAddressMethodRef, swCalibrationAccess, swImplPolicy, compuMethodRef, dataConstraintRef, unitRef)
      if swPointerTargetPropsXML is not None:
         variant.swPointerTargetProps = self.parseSwPointerTargetProps(swPointerTargetPropsXML, variant)
      return variant

   def parseSwPointerTargetProps(self, rootXML, parent = None):
      assert (rootXML.tag == 'SW-POINTER-TARGET-PROPS')
      props = SwPointerTargetProps()
      for itemXML in rootXML.findall('./*'):
         if itemXML.tag == 'TARGET-CATEGORY':
            props.targetCategory = self.parseTextNode(itemXML)
         if itemXML.tag == 'SW-DATA-DEF-PROPS':
            props.variants = self.parseSwDataDefProps(itemXML)
      return props

   def parseVariableDataPrototype(self, xmlRoot, parent):
      assert(xmlRoot.tag == 'VARIABLE-DATA-PROTOTYPE')
      (name, typeRef, props_variants, isQueued) = (None, None, None, False)
      for xmlElem in xmlRoot.findall('./*'):
         if xmlElem.tag == 'SHORT-NAME':
            name = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'TYPE-TREF':
            typeRef = self.parseTextNode(xmlElem)
         elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
            props_variants = self.parseSwDataDefProps(xmlElem)
         else:
            raise NotImplementedError(xmlElem.tag)
      if (name is not None) and (typeRef is not None):
         dataElement = DataElement(name, typeRef, isQueued, parent=parent)
         dataElement.setProps(props_variants[0])
         return dataElement
      else:
         raise RuntimeError('SHORT-NAME and TYPE-TREF must not be None')

class ElementParser(BaseParser, metaclass=abc.ABCMeta):
   
   def __init__(self, version=None):
      super().__init__(version)
   
   @abc.abstractmethod
   def getSupportedTags(self):
      """
      Returns a list of tag-names (strings) that this parser supports.
      A generator returning strings is also OK.
      """
   @abc.abstractmethod
   def parseElement(self, xmlElement, parent = None):
      """
      Invokes the parser
      
      xmlElem: Element to parse (instance of xml.etree.ElementTree.Element)      
      parent: the parent object (usually a package object)
      Should return an object derived from autosar.element.Element
      """
 

