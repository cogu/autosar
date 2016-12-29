from autosar.base import parseTextNode

class BaseParser:
   def __init__(self,version=None):
      self.version=version
      
   def parseDesc(self,xmlRoot,elem):
      descXml = xmlRoot.find('DESC')      
      if descXml is not None:
         L2Xml = descXml.find('L-2')
         if L2Xml is not None:
            L2Text=parseTextNode(L2Xml)
            L2Attr=L2Xml.attrib['L']
            elem.desc=L2Text
            elem.descAttr=L2Attr         
      
      
