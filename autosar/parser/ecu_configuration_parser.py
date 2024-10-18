import autosar.ecuc
from autosar.parser.parser_base import EntityParser, parseElementUUID

class EcuConfigurationParser(EntityParser):
    """
    Ecu Configuration parser
    """

    def __init__(self,version=3.0):
        super().__init__(version)
        self.switcher = {
            'ECUC-MODULE-CONFIGURATION-VALUES': self.parseEcuConfiguration
        }
        
        self.handledTags = ['SHORT-NAME', 'DEFINITION-REF']

    def getSupportedTags(self):
        return self.switcher.keys()

    def getDefinition(self, node):
        definition_node = node.find('DEFINITION-REF')

        def_reference = self.parseTextNode(definition_node)
        def_dest = definition_node.attrib.get('DEST') if definition_node is not None else None

        return def_reference, def_dest

    def getMetaInformation(self, node):
        name = self.parseTextNode(node.find('SHORT-NAME'))
        def_reference, def_dest = self.getDefinition(node)

        return (name, def_reference, def_dest)

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement, parent)
        else:
            return None

    @parseElementUUID
    def parseEcuConfiguration(self, xmlRoot, parent = None):
        ecuConfig = None
        if xmlRoot.tag == 'ECUC-MODULE-CONFIGURATION-VALUES':
            name, def_reference, def_dest = self.getMetaInformation(xmlRoot)
            ecuConfig = autosar.ecuc.EcuConfig(name, def_reference, def_dest, parent)
        else:
            raise NotImplementedError(xmlRoot.tag)

        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag in self.handledTags:
                continue

            if xmlElem.tag == 'CONTAINERS':
                xmlContainers = xmlElem.findall('./ECUC-CONTAINER-VALUE')
                for xmlContainer in xmlContainers:
                    container = self.parseContainer(xmlContainer, ecuConfig)
                    ecuConfig.appendContainer(container)

        return ecuConfig
 
    @parseElementUUID
    def parseContainer(self, xmlElem, parent = None):
        name, def_reference, def_dest = self.getMetaInformation(xmlElem)
        container = autosar.ecuc.Container(name, def_reference, def_dest, parent)

        for node in xmlElem.findall('./*'):
            if node.tag in self.handledTags:
                continue

            if node.tag == 'SUB-CONTAINERS':
                xmlSubContainers = node.findall('./ECUC-CONTAINER-VALUE')
                for xmlSubContainer in xmlSubContainers:
                    subContainer = self.parseContainer(xmlSubContainer, container)

                    container.appendContainer(subContainer)

            elif node.tag == 'REFERENCE-VALUES':
                xmlReferenceValues = node.findall('./ECUC-REFERENCE-VALUE')
                for xmlReferenceValue in xmlReferenceValues:
                    refValue = self.parseReferenceValue(xmlReferenceValue)

                    container.appendRef(refValue)

            elif node.tag == 'PARAMETER-VALUES':
                xmlParameterValues = node.findall('./*')
                for xmlParameterValue in xmlParameterValues:
                    paramValue = self.parseParameterValue(xmlParameterValue)

                    container.appendParam(paramValue)

        return container
    
    def parseReferenceValue(self, xmlElem):
        def_reference, def_dest = self.getDefinition(xmlElem)

        value_node = xmlElem.find('VALUE-REF')
        value_content = self.parseTextNode(value_node)
        value_destination = value_node.attrib.get('DEST') if value_node is not None else None
        
        return autosar.ecuc.ReferenceValue(def_reference, def_dest, value_content, value_destination)

    def parseParameterValue(self, xmlElem):
        def_reference, def_dest = self.getDefinition(xmlElem)

        value_node = xmlElem.find('VALUE')
        value_content = self.parseTextNode(value_node)
        value_destination = value_node.attrib.get('DEST')

        if def_dest == 'ECUC-BOOLEAN-PARAM-DEF':
            value_content = value_content == "true"
        elif def_dest == 'ECUC-INTEGER-PARAM-DEF':
            value_content = int(value_content)
        elif def_dest in ['ECUC-ENUMERATION-PARAM-DEF', 'ECUC-TEXTUAL-PARAM-VALUE']:
            value_content = value_content
        else:
            value_content = None
        
        return autosar.ecuc.ParamValue(def_reference, def_dest, value_content, value_destination)