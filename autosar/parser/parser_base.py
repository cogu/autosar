import abc
from autosar.base import AdminData, SpecialDataGroup, SwDataDefPropsConditional, SwPointerTargetProps

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
      descXml = xmlRoot.find('DESC')
      if descXml is not None:
         L2Xml = descXml.find('L-2')
         if L2Xml is not None:
            L2Text=self.parseTextNode(L2Xml)
            L2Attr=L2Xml.attrib['L']
            elem.desc=L2Text
            elem.descAttr=L2Attr

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
            GID=xmlElem.attrib['GID']
            SD=None
            SD_GID=None
            xmlSD = xmlElem.find('SD')
            if xmlSD is not None:
               SD=xmlSD.text
               try:
                  SD_GID=xmlSD.attrib['GID']
               except KeyError: pass
            adminData.specialDataGroups.append(SpecialDataGroup(GID,SD,SD_GID))
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
       swPointerTargetPropsXML, swImplPolicy, swAddressMethodRef) = (None, None, None, None, None, None, None, None)
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
         else:
            raise NotImplementedError(xmlItem.tag)
      variant = SwDataDefPropsConditional(baseTypeRef, implementationTypeRef, swAddressMethodRef, swCalibrationAccess, compuMethodRef, dataConstraintRef)
      if swPointerTargetPropsXML is not None:
         variant.swPointerTargetProps = self.parseSwPointerTargetProps(swPointerTargetPropsXML, variant)
      if swImplPolicy is not None:
         variant.swImplPolicy = swImplPolicy
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
 

