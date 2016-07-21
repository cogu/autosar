from autosar.base import parseXMLFile,splitref,parseTextNode,parseIntNode
from autosar.signal import *

class SignalParser(object):
   def __init__(self,pkg,version=3.0):
      if version == 3.0:
         self.version=version
      else:
         raise NotImplementedError('Version %d of ARXML not supported'%version)
      self.pkg=pkg
   
   def parseSystemSignal(self,xmlRoot,dummy,parent=None):
      """
      parses <SYSTEM-SIGNAL>
      """
      assert(xmlRoot.tag=='SYSTEM-SIGNAL')
      name,dataTypeRef,initValueRef,length,desc=None,None,None,None,None
      for elem in xmlRoot.findall('./*'):         
         if elem.tag=='SHORT-NAME':
            name=parseTextNode(elem)
         elif elem.tag=='DATA-TYPE-REF':
            dataTypeRef=parseTextNode(elem)
         elif elem.tag=='INIT-VALUE-REF':
            initValueRef=parseTextNode(elem)
         elif elem.tag=='LENGTH':
            length=parseIntNode(elem)
         elif elem.tag=='DESC':
            desc=parseTextNode(elem)
         else:
            raise NotImplementedError(elem.tag)
      if (name is not None) and (dataTypeRef is not None) and (initValueRef is not None) and length is not None:         
         return SystemSignal(name,dataTypeRef,initValueRef,length,desc,parent)
      else:
         raise ValueError("failed to parse <SYSTEM-SIGNAL>")

