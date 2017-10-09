import abc
from autosar.base import parseTextNode

class BaseParser():
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
      ws: current workspace
      parent: the parent object (usually a package object)
      """
      


