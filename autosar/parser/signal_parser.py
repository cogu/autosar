from autosar.base import parseXMLFile,splitRef,parseTextNode,parseIntNode
from autosar.signal import *
from autosar.parser.parser_base import ElementParser

class SignalParser(ElementParser):
    def __init__(self,version=3):
        self.version=version

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {'SYSTEM-SIGNAL': self.parseSystemSignal,
                             'SYSTEM-SIGNAL-GROUP': self.parseSystemSignalGroup
            }
        elif self.version >= 4.0:
            self.switcher = {
            }

    def getSupportedTags(self):
        return self.switcher.keys()

    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement,parent)
        else:
            return None

    def parseSystemSignal(self,xmlRoot,parent=None):
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
                descXml = xmlRoot.find('DESC')
                if descXml is not None:
                    L2Xml = descXml.find('L-2')
                    if L2Xml is not None:
                        desc = parseTextNode(L2Xml)
            else:
                raise NotImplementedError(elem.tag)
#      if (name is not None) and (dataTypeRef is not None) and (initValueRef is not None) and length is not None:
        if (name is not None) and length is not None:  #All signals doesn't have IV constant Ref or DatatypeRef
            return SystemSignal(name, dataTypeRef, initValueRef, length, desc, parent)
        else:
            raise RuntimeError('failed to parse %s'%xmlRoot.tag)

    def parseSystemSignalGroup(self, xmlRoot, parent=None):
        name,systemSignalRefs=None,None
        for elem in xmlRoot.findall('./*'):
            if elem.tag=='SHORT-NAME':
                name=parseTextNode(elem)
            elif elem.tag=='SYSTEM-SIGNAL-REFS':
                systemSignalRefs=[]
                for childElem in elem.findall('./*'):
                    if childElem.tag=='SYSTEM-SIGNAL-REF':
                        systemSignalRefs.append(parseTextNode(childElem))
                    else:
                        raise NotImplementedError(childElem.tag)
            else:
                raise NotImplementedError(elem.tag)

        if (name is not None) and (isinstance(systemSignalRefs,list)):
            return SystemSignalGroup(name,systemSignalRefs)
        else:
            raise RuntimeError('failed to parse %s'%xmlRoot.tag)
