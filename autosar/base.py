import xml.etree.ElementTree as ElementTree
import re

class AdminData(object):
   def __init__(self):
      self.data = []
   def asdict(self):
      retval={'type': self.__class__.__name__, 'data':[]}
      for elem in self.data:
         retval['data'].append(elem.asdict())
      return retval

class SpecialDataGroup(object):
   def __init__(self,GID,SD=None,SD_GID=None):
      self.GID=GID
      self.SD=SD
      self.SD_GID=SD_GID
   def asdict(self):
      data = {'type': self.__class__.__name__, 'GID':self.GID}
      if self.SD is not None: data['SD']=self.SD
      if self.SD_GID is not None: data['SD_GID']=self.SD_GID
      return data

def removeNamespace(doc, namespace):
   """Removes XML namespace in place."""
   ns = u'{%s}' % namespace
   nsl = len(ns)
   for elem in doc.getiterator():
      if elem.tag.startswith(ns):
         elem.tag = elem.tag[nsl:]

def parseXMLFile(filename,namespace=None):
   arxml_tree = ElementTree.ElementTree()
   arxml_tree.parse(filename)
   arxml_root = arxml_tree.getroot();
   if namespace is not None:
      removeNamespace(arxml_root,namespace)      
   return arxml_root

def getXMLNamespace(element):
    m = re.match(r'\{(.*)\}', element.tag)
    return m.group(1) if m else None

def splitref(ref):
   """splits an autosar url string into an array"""
   if isinstance(ref,str):
      if ref[0]=='/': return ref[1:].split('/')
      else: return ref.split('/')
   return None

def hasAdminData(xmlRoot):
   return True if xmlRoot.find('ADMIN-DATA') is not None else False
   
def parseAdminDataNode(xmlRoot):
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
         adminData.data.append(SpecialDataGroup(GID,SD,SD_GID))
   return adminData

def parseTextNode(xmlElem):
   return None if xmlElem is None else xmlElem.text
def parseIntNode(xmlElem):
   return None if xmlElem is None else int(xmlElem.text)
def parseFloatNode(xmlElem):
   return None if xmlElem is None else float(xmlElem.text)
def parseBooleanNode(xmlElem):
   return None if xmlElem is None else parseBoolean(xmlElem.text)

def parseBoolean(value):
   if value is None:
      return None   
   if isinstance(value,str):
      if value == 'true': return True
      elif value =='false': return False
   raise ValueError(value)   
