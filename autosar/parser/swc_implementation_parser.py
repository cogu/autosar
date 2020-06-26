"""
Implements the class SwcImplementationParser
"""
import sys
from autosar.base import splitRef, hasAdminData, parseAdminDataNode
import autosar.component
from autosar.parser.parser_base import ElementParser

class SwcImplementationParser(ElementParser):
    """
    ComponentType parser
    """

    def __init__(self,version=3.0):
        super().__init__(version)
        self.classTag = 'SWC-IMPLEMENTATION'

    def getSupportedTags(self):
        return [self.classTag]

    def parseElement(self, xmlElement, parent = None):
        """
        parser for the class.
        """
        assert (xmlElement.tag=='SWC-IMPLEMENTATION')
        ws = parent.rootWS()
        assert(ws is not None)
        name = self.parseTextNode(xmlElement.find('SHORT-NAME'))
        behaviorRef = self.parseTextNode(xmlElement.find('BEHAVIOR-REF'))
        implementation = autosar.component.SwcImplementation(name, behaviorRef, parent=parent)
        self.push()
        for xmlElem in xmlElement.findall('./*'):
            if xmlElem.tag   == 'SHORT-NAME':
                continue
            elif xmlElem.tag == 'BEHAVIOR-REF':
                continue
            elif xmlElem.tag == 'BUILD-ACTION-MANIFESTS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'CODE-DESCRIPTORS':
                # Create the list to indicate that the base element exists.
                implementation.codeDescriptors = []
                for codeElem in xmlElem.findall('./*'):
                    if codeElem.tag  == 'CODE':
                        implementation.codeDescriptors.append(self.parseCodeDescriptor(codeElem, parent=implementation))
                    else:
                        raise NotImplementedError(codeElem.tag)
            elif xmlElem.tag == 'COMPILERS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'GENERATED-ARTIFACTS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'HW-ELEMENT-REFS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'LINKERS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'MC-SUPPORT':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'PROGRAMMING-LANGUAGE':
                implementation.programmingLanguage = self.parseTextNode(xmlElem)
                continue
            elif xmlElem.tag == 'REQUIRED-ARTIFACTS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'REQUIRED-GENERATOR-TOOLS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'RESOURCE-CONSUMPTION':
                implementation.resourceConsumption = self.parseResourceConsumption(xmlElem, parent=implementation)
                continue
            elif xmlElem.tag == 'SW-VERSION':
                implementation.swVersion = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SWC-BSW-MAPPING-REF':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'USED-CODE-GENERATOR':
                implementation.useCodeGenerator = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'VENDOR-ID':
                implementation.vendorId = self.parseIntNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)

        self.pop(implementation)

        # Find the SWC and connect the swc to the implementation.
        behavior = ws.find(behaviorRef)
        if behavior is not None:
            swc = ws.find(behavior.componentRef)
            if swc is not None:
                swc.implementation = implementation

        return implementation

    def parseCodeDescriptor(self, xmlElement, parent = None):
        """
        Parser for implementation code descriptor.
        """
        assert (xmlElement.tag=='CODE')
        name = self.parseTextNode(xmlElement.find('SHORT-NAME'))
        code = autosar.component.SwcImplementationCodeDescriptor(name, parent=parent)
        self.push()
        for xmlElem in xmlElement.findall('./*'):
            if xmlElem.tag   == 'SHORT-NAME':
                continue
            elif xmlElem.tag == 'ARTIFACT-DESCRIPTORS':
                code.artifactDescriptors = []
                for descElem in xmlElem.findall('./*'):
                    if descElem.tag  == 'AUTOSAR-ENGINEERING-OBJECT':
                        engineeringObject = autosar.component.EngineeringObject(code)
                        for elem in descElem.findall('./*'):
                            if elem.tag  == 'SHORT-LABEL':
                                engineeringObject.shortLabel = self.parseTextNode(elem)
                            elif elem.tag  == 'CATEGORY':
                                engineeringObject.category = self.parseTextNode(elem)
                            elif elem.tag == 'REVISION-LABELS':
                                engineeringObject.revisionLabels = []
                                for labelElem in elem.findall('./*'):
                                    if labelElem.tag  == 'REVISION-LABEL':
                                        engineeringObject.revisionLabels.append(self.parseTextNode(labelElem))
                            elif elem.tag  == 'DOMAIN':
                                engineeringObject.domain = self.parseTextNode(elem)
                        code.artifactDescriptors.append(engineeringObject)
            elif xmlElem.tag == 'CALLBACK-HEADER-REFS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'TYPE':
                # Only valid in Autosar 3.
                code.type = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)

        self.pop(code)
        return code

    def parseResourceConsumption(self, xmlElement, parent = None):
        """
        Parser for implementation resource consumption.
        """
        assert (xmlElement.tag=='RESOURCE-CONSUMPTION')
        name = self.parseTextNode(xmlElement.find('SHORT-NAME'))
        res = autosar.component.ResourceConsumption(name, parent=parent)
        self.push()
        for xmlElem in xmlElement.findall('./*'):
            if xmlElem.tag   == 'SHORT-NAME':
                continue
            elif xmlElem.tag == 'EXECUTION-TIMES':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'HEAP-USAGES':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'MEMORY-SECTIONS':
                res.memorySections = []
                for xmlSection in xmlElem.findall('./*'):
                    res.memorySections.append(self.parseMemorySection(xmlSection, res))
            elif xmlElem.tag == 'SECTION-NAME-PREFIXS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'STACK-USAGES':
                #TODO: Implement later
                continue
            else:
                self.defaultHandler(xmlElem)

        self.pop(res)
        return res

    def parseMemorySection(self, xmlElement, parent = None):
        """
        Parser for memory section.
        """
        assert (xmlElement.tag=='MEMORY-SECTION')
        name = self.parseTextNode(xmlElement.find('SHORT-NAME'))
        section = autosar.component.MemorySection(name, parent=parent)
        self.push()
        for xmlElem in xmlElement.findall('./*'):
            if xmlElem.tag   == 'SHORT-NAME':
                continue
            elif xmlElem.tag == 'ALIGNMENT':
                section.aligment = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'EXECUTABLE-ENTITY-REFS':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'MEM-CLASS-SYMBOL':
                section.memClassSymbol = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'OPTIONS':
                section.options = []
                for xmlOption in xmlElem.findall('./*'):
                    section.options.append(self.parseTextNode(xmlOption))
            elif xmlElem.tag == 'PREFIX-REF':
                #TODO: Implement later
                continue
            elif xmlElem.tag == 'SIZE':
                section.size = self.parseIntNode(xmlElem)
            elif xmlElem.tag == 'SW-ADDRMETHOD-REF':
                section.swAddrmethodRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SYMBOL':
                section.symbol = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)

        self.pop(section)
        return section
