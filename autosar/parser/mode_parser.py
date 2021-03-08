import sys
from autosar.parser.parser_base import ElementParser
import autosar.datatype

class ModeDeclarationParser(ElementParser):
    def __init__(self,version=3):
        self.version=version

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {'MODE-DECLARATION-GROUP': self.parseModeDeclarationGroup,
                             'MODE-DECLARATIONS': self.parseModeDeclarations
            }
        elif self.version >= 4.0:
            self.switcher = {
               'MODE-DECLARATION-GROUP': self.parseModeDeclarationGroup
            }

    def getSupportedTags(self):
        return self.switcher.keys()

    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement,parent)
        else:
            return None

    def parseModeDeclarationGroup(self,xmlRoot,rootProject=None,parent=None):
        assert(xmlRoot.tag == 'MODE-DECLARATION-GROUP')
        name = self.parseTextNode(xmlRoot.find("./SHORT-NAME"))
        category = self.parseTextNode(xmlRoot.find("./CATEGORY"))
        initialModeRef = self.parseTextNode(xmlRoot.find('./INITIAL-MODE-REF'))
        modeDclrGroup = autosar.mode.ModeDeclarationGroup(name,initialModeRef,None,parent)
        if xmlRoot.find('./MODE-DECLARATIONS') is not None:
            self.parseModeDeclarations(xmlRoot.find('./MODE-DECLARATIONS'), modeDclrGroup)
        if self.hasAdminData(xmlRoot):
            adminData = self.parseAdminDataNode(xmlRoot.find('ADMIN-DATA'))
            modeDclrGroup.adminData = adminData
        if category is not None:
            modeDclrGroup.category = category
        return modeDclrGroup

    def parseModeDeclarations(self,xmlRoot,parent):
        assert(xmlRoot.tag=="MODE-DECLARATIONS")
        assert(isinstance(parent, autosar.mode.ModeDeclarationGroup))
        result = []
        for mode in xmlRoot.findall("./MODE-DECLARATION"):
            declarationName = self.parseTextNode(mode.find("./SHORT-NAME"))
            declarationValue = None
            declarationValueXML = mode.find("./VALUE")
            if declarationValueXML is not None:
                declarationValue = self.parseTextNode(declarationValueXML)
            parent.modeDeclarations.append(autosar.mode.ModeDeclaration(declarationName, declarationValue, parent = parent))
        return result

