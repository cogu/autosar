from autosar.base import parseXMLFile,splitRef,parseTextNode,parseIntNode,hasAdminData,parseAdminDataNode
from autosar.system import *
from autosar.parser.parser_base import EntityParser, parseElementUUID
from autosar.util.errorHandler import handleNotImplementedError

class SystemParser(EntityParser):
    def __init__(self,version=3.0):
        super().__init__(version)

    def getSupportedTags(self):
        return ['SYSTEM']

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        if xmlElement.tag == 'SYSTEM':
            return self.parseSystem(xmlElement, parent)
        else:
            return None

    @parseElementUUID
    def parseSystem(self,xmlRoot,parent=None):
        """
        parses <SYSTEM>
        """
        assert(xmlRoot.tag=='SYSTEM')
        xmlName = xmlRoot.find('SHORT-NAME')
        if xmlName is not None:
            system=System(parseTextNode(xmlName),parent)
            for xmlElem in xmlRoot.findall('./*'):
                if xmlElem.tag=='SHORT-NAME':
                    pass
                elif xmlElem.tag=='CATEGORY':
                    system.category=parseTextNode(xmlElem)
                elif xmlElem.tag=='MAPPINGS':
                    print("Unhandled: %s"%xmlElem.tag)
                elif xmlElem.tag=='ROOT-SOFTWARE-COMPOSITIONS':
                    self.parseRootSoftwareCompositions(xmlElem,system)
                elif xmlElem.tag=='ADMIN-DATA':
                    system.adminData=parseAdminDataNode(xmlElem)
                elif xmlElem.tag=='FIBEX-ELEMENT-REFS':
                    self.parseFibexElementRefs(xmlElem,system)
                elif xmlElem.tag=='FIBEX-ELEMENTS':
                    self.parseFibexElementRefConditionals(xmlElem,system)
                elif xmlElem.tag=='MAPPING':
                    self.parseSystemMapping(xmlElem,system)
                else:
                    handleNotImplementedError(xmlElem.tag)
            return system
        else:
            raise KeyError('expected to find <SHORT-NAME> inside <SYSTEM> tag')

    def parseRootSoftwareCompositions(self,xmlRoot,system):
        """parses <ROOT-SOFTWARE-COMPOSITIONS>"""
        assert(xmlRoot.tag=='ROOT-SOFTWARE-COMPOSITIONS')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='ROOT-SW-COMPOSITION-PROTOTYPE':
                rootSwCompositionPrototype = self.parseRootSwCompositionPrototype(xmlElem,system)
                if rootSwCompositionPrototype is not None:
                    system.rootSoftwareCompositions.append(rootSwCompositionPrototype)        
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseFibexElementRefs(self,xmlRoot,system):
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='FIBEX-ELEMENT-REF':
                system.fibexElementRefs.append(parseTextNode(xmlElem))
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseFibexElementRefConditionals(self,xmlRoot,system):
        """parses <FIBEX-ELEMENTS>"""
        assert(xmlRoot.tag=='FIBEX-ELEMENTS')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='FIBEX-ELEMENT-REF-CONDITIONAL':
                refXmlElem = xmlElem.find('FIBEX-ELEMENT-REF')
                if refXmlElem is not None:
                    system.fibexElementRefConditionals.append(parseTextNode(refXmlElem))
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseSystemMapping(self,xmlRoot,system):
        """parses <MAPPING>"""
        assert(xmlRoot.tag=='MAPPING')
        name=parseTextNode(xmlRoot.find('SHORT-NAME'))
        system.mapping = Mapping(name,system)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SHORT-NAME':
                pass
            elif xmlElem.tag=='DATA-MAPPINGS':
                self.parseDataMapping(xmlElem,system.mapping.data)
            elif xmlElem.tag=='SW-IMPL-MAPPINGS':
                self.parseSwImplMapping(xmlElem,system.mapping)
            elif xmlElem.tag=='SW-MAPPINGS':
                self.parseSwMapping(xmlElem,system.mapping)
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseDataMapping(self,xmlRoot,dataMapping):
        """parses <DATA-MAPPINGS>"""
        assert(xmlRoot.tag=='DATA-MAPPINGS')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SWC-TO-IMPL-MAPPING':
                pass
            elif xmlElem.tag=='SENDER-RECEIVER-TO-SIGNAL-MAPPING':
                dataMapping.senderReceiverToSignal.append(self.parseSenderReceiverToSignalMapping(xmlElem))
            elif xmlElem.tag=='SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING':
                dataMapping.senderReceiverToSignalGroup.append(self.parseSenderReceiverToSignalGroupMapping(xmlElem))
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseSwImplMapping(self,xmlRoot,mapping):
        """parses <SW-IMPL-MAPPINGS>"""
        assert(xmlRoot.tag=='SW-IMPL-MAPPINGS')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SWC-TO-IMPL-MAPPING':
                pass
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseSwMapping(self,xmlRoot,mapping):
        """parses <SW-MAPPINGS>"""
        assert(xmlRoot.tag=='SW-MAPPINGS')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SWC-TO-ECU-MAPPING':
                pass
            else:
                handleNotImplementedError(xmlElem.tag)

    def parseRootSwCompositionPrototype(self,xmlRoot,system):
        """parses <ROOT-SW-COMPOSITION-PROTOTYPE>"""
        assert(xmlRoot.tag=='ROOT-SW-COMPOSITION-PROTOTYPE')
        compositionTref, flatMapRef = None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SOFTWARE-COMPOSITION-TREF':
                compositionTref = self.parseTextNode(xmlElem)
            elif xmlElem.tag=='FLAT-MAP-REF':
                flatMapRef = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        obj = RootSwCompositionPrototype(self.name, compositionTref, flatMapRef, self.adminData, self.category, system)
        self.pop(obj)
        return obj


    def parseSenderReceiverToSignalMapping(self,xmlRoot):
        """parses <'SENDER-RECEIVER-TO-SIGNAL-MAPPING'>"""
        assert(xmlRoot.tag=='SENDER-RECEIVER-TO-SIGNAL-MAPPING')
        dataElemIRef=None
        signalRef=None
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='DATA-ELEMENT-IREF':
                dataElemIRef=self.parseDataElemInstanceRef(xmlElem)
            elif xmlElem.tag=='SIGNAL-REF':
                signalRef=parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (dataElemIRef is not None) and (signalRef is not None):
            return SenderReceiverToSignalMapping(dataElemIRef,signalRef)
        else:
            raise Exception("failed to parse SENDER-RECEIVER-TO-SIGNAL-MAPPING")

    def parseSenderReceiverToSignalGroupMapping(self,xmlRoot):
        """parses <'SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING'>"""
        assert(xmlRoot.tag=='SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING')
        dataElemIRef=None
        signalGroupRef=None
        typeMapping=None
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'DATA-ELEMENT-IREF': #minOccurs=0, maxOccurs=1
                dataElemIRef=self.parseDataElemInstanceRef(xmlElem)
            elif xmlElem.tag == 'SIGNAL-GROUP-REF': #minOccurs=0, maxOccurs=
                signalGroupRef=parseTextNode(xmlElem)
            elif xmlElem.tag == 'TYPE-MAPPING': #minOccurs=0, maxOccurs=1
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag=='SENDER-REC-ARRAY-TYPE-MAPPING':
                        typeMapping = ArrayElementMapping()
                        for xmlItem in xmlChild.findall('./ARRAY-ELEMENT-MAPPINGS/SENDER-REC-ARRAY-TYPE-MAPPING'):
                            print("SENDER-REC-ARRAY-TYPE-MAPPING not implemented")
                    elif xmlChild.tag=='SENDER-REC-RECORD-TYPE-MAPPING':
                        typeMapping=RecordElementMapping()
                        for xmlItem in xmlChild.findall('./RECORD-ELEMENT-MAPPINGS/SENDER-REC-RECORD-ELEMENT-MAPPING'):
                            typeMapping.elements.append(self.parseSenderRecRecordElementMapping(xmlItem))
                    else:
                        handleNotImplementedError(xmlChild.tag)
            else:
                handleNotImplementedError(xmlElem.tag)
        return SenderReceiverToSignalGroupMapping(dataElemIRef,signalGroupRef,typeMapping)

    def parseDataElemInstanceRef(self,xmlRoot):
        dataElemRef=parseTextNode(xmlRoot.find('DATA-ELEMENT-REF'))
        assert(dataElemRef is not None)
        dataElemIRef=SignalDataElementInstanceRef(dataElemRef)
        for xmlChild in xmlRoot.findall('./*'):
            if xmlChild.tag=='DATA-ELEMENT-REF':
                pass
            elif xmlChild.tag=='SOFTWARE-COMPOSITION-REF':
                dataElemIRef.softwareCompositionRef=parseTextNode(xmlChild)
            elif xmlChild.tag=='COMPONENT-PROTOTYPE-REF':
                dataElemIRef.componentPrototypeRef.append(parseTextNode(xmlChild))
            elif xmlChild.tag=='PORT-PROTOTYPE-REF':
                dataElemIRef.portPrototypeRef=parseTextNode(xmlChild)
            else:
                handleNotImplementedError(xmlChild.tag)
        return dataElemIRef

    def parseSenderRecRecordElementMapping(self,xmlRoot):
        """parses <'SENDER-REC-RECORD-ELEMENT-MAPPING'>"""
        assert(xmlRoot.tag=='SENDER-REC-RECORD-ELEMENT-MAPPING')
        recordElementRef=None
        signalRef=None
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='RECORD-ELEMENT-REF': #minOccurs="0" maxOccurs="1"
                recordElementRef=parseTextNode(xmlElem)
            elif xmlElem.tag=='SIGNAL-REF': #minOccurs="0" maxOccurs="1"
                signalRef=parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return SenderRecRecordElementMapping(recordElementRef,signalRef)

    def parseSenderRecArrayElementMapping(self,xmlRoot):
        """parses <'SENDER-REC-RECORD-ELEMENT-MAPPING'>"""
        assert(xmlRoot.tag=='SENDER-REC-RECORD-ELEMENT-MAPPING')
        handleNotImplementedError(xmlRoot.tag)
