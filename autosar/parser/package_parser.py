import autosar.package
import autosar.element
import autosar.parser.parser_base
import sys
from autosar.base import parseTextNode

class PackageParser:
    def __init__(self,version):
        assert(isinstance(version, float))
        self.version=version
        self.registeredParsers={}
        self.switcher={}

    def registerElementParser(self, elementParser):
        """
        Registers a new element parser into the package parser
        """
        assert(isinstance(elementParser, autosar.parser.parser_base.ElementParser))
        name = type(elementParser).__name__
        if name not in self.registeredParsers:
            for tagname in elementParser.getSupportedTags():
                self.switcher[tagname]=elementParser
            self.registeredParsers[name] = elementParser

    def loadXML(self, package, xmlRoot):
        """
        Loads an XML package by repeatedly invoking its registered element parsers
        """
        assert(self.switcher is not None)
        if xmlRoot.find('ELEMENTS'):
            elementNames = set([x.name for x in package.elements])
            for xmlElement in xmlRoot.findall('./ELEMENTS/*'):
                parserObject = self.switcher.get(xmlElement.tag)
                if parserObject is not None:
                    element = parserObject.parseElement(xmlElement,package)
                    if element is None:
                        print("[PackageParser] No return value: %s"%xmlElement.tag)
                        continue
                    element.parent=package
                    if isinstance(element,autosar.element.Element):
                        if element.name not in elementNames:
                            #ignore duplicated items
                            package.append(element)
                            elementNames.add(element.name)
                    else:
                        #raise ValueError("parse error: %s"%type(element))
                        raise ValueError("parse error: %s"%xmlElement.tag)
                else:
                    package.unhandledParser.add(xmlElement.tag)

        if self.version >= 3.0 and self.version < 4.0:
            if xmlRoot.find('SUB-PACKAGES'):
                for xmlPackage in xmlRoot.findall('./SUB-PACKAGES/AR-PACKAGE'):
                    name = xmlPackage.find("./SHORT-NAME").text
                    subPackage = autosar.package.Package(name)
                    package.append(subPackage)
                    self.loadXML(subPackage,xmlPackage)
        elif self.version >= 4.0:
            for subPackageXML in xmlRoot.findall('./AR-PACKAGES/AR-PACKAGE'):
                name = parseTextNode(subPackageXML.find("./SHORT-NAME"))
                subPackage = package.find(name)
                if subPackage is None:
                    subPackage = autosar.package.Package(name)
                    package.append(subPackage)
                self.loadXML(subPackage, subPackageXML)
