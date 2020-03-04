from autosar.writer.writer_base import BaseWriter, ElementWriter
from autosar.base import applyFilter
import collections.abc
import autosar.behavior
import autosar.component

class PackageWriter(BaseWriter):
    def __init__(self, version, patch):
        super().__init__(version, patch)
        self.registeredWriters={}
        self.xmlSwitcher={}
        self.codeSwitcher={}

    def registerElementWriter(self, elementWriter):
        """
        registers a new element writer into this package writer
        """
        assert(isinstance(elementWriter, ElementWriter))
        writerName = type(elementWriter).__name__
        if writerName not in self.registeredWriters:
            list_or_generator = elementWriter.getSupportedXML()
            if list_or_generator is not None:
                if isinstance(list_or_generator, str):
                    list_or_generator = [list_or_generator]
                for elementName in list_or_generator:
                    self.xmlSwitcher[elementName] = elementWriter
            list_or_generator = elementWriter.getSupportedCode()
            if list_or_generator is not None:
                if isinstance(list_or_generator, str):
                    list_or_generator = [list_or_generator]
                for elementName in list_or_generator:
                    self.codeSwitcher[elementName] = elementWriter
            self.registeredWriters[writerName] = elementWriter

    def toXML(self, package, filters, ignore):
        lines=[]
        lines.extend(self.beginPackage(package.name))
        if len(package.elements)>0:
            lines.append(self.indent("<ELEMENTS>",1))
            for elem in package.elements:
                elemRef = elem.ref
                ignoreElem=True if (isinstance(ignore, collections.abc.Iterable) and elemRef in ignore) else False
                #if SWC was ignored by user, also ignore its InternalBehavior and SwcImplementation elements in case they are in the same package
                if not ignoreElem and isinstance(elem, autosar.behavior.InternalBehavior):
                    if (isinstance(ignore, collections.abc.Iterable) and elem.componentRef in ignore):
                        ignoreElem = True
                if not ignoreElem and isinstance(elem, autosar.component.SwcImplementation):
                    behavior = package.rootWS().find(elem.behaviorRef)
                    if behavior is not None:
                        if (isinstance(ignore, collections.abc.Iterable) and behavior.componentRef in ignore):
                            ignoreElem = True
                if not ignoreElem and applyFilter(elemRef, filters):
                    elementName = elem.__class__.__name__
                    elementWriter = self.xmlSwitcher.get(elementName)
                    if elementWriter is not None:
                        result = elementWriter.writeElementXML(elem)
                        if result is None:
                            print("[PackageWriter] No return value: %s"%elementName)
                            continue
                        else:
                            lines.extend(self.indent(result,2))
                    else:
                        package.unhandledWriter.add(elementName)
            lines.append(self.indent("</ELEMENTS>",1))
        else:
            if self.version<4.0:
                lines.append(self.indent("<ELEMENTS/>",1))
        if len(package.subPackages)>0:
            numPackets = 0
            if self.version >= 3.0 and self.version < 4.0:
                for subPackage in package.subPackages:
                    if applyFilter(subPackage.ref, filters):
                        if numPackets == 0:
                            lines.append(self.indent("<SUB-PACKAGES>",1))
                        lines.extend(self.indent(self.toXML(subPackage, filters, ignore),2))
                        numPackets += 1
                if numPackets > 0:
                    lines.append(self.indent("</SUB-PACKAGES>",1))
            elif self.version >= 4.0:
                for subPackage in package.subPackages:
                    if applyFilter(subPackage.ref, filters):
                        if numPackets == 0:
                            lines.append(self.indent("<AR-PACKAGES>",1))
                        lines.extend(self.indent(self.toXML(subPackage, filters, ignore),2))
                        numPackets += 1
                if numPackets > 0:
                    lines.append(self.indent("</AR-PACKAGES>",1))
        lines.extend(self.endPackage())
        return lines

    def toCode(self, package, filters, ignore, localvars, isTemplate):
        lines=[]
        if not isTemplate:
            if package.role is not None:
                lines.append('package=ws.createPackage("%s", role="%s")'%(package.name, package.role))
            else:
                lines.append('package=ws.createPackage("%s")'%(package.name))
            localvars['package']=package
            for subPackage in package.subPackages:
                if subPackage.role is not None:
                    lines.append('package.createSubPackage("%s", role="%s")'%(subPackage.name, subPackage.role))
                else:
                    lines.append('package.createSubPackage("%s")'%(subPackage.name))
        for elem in package.elements:
            elemRef = elem.ref
            ignoreElem=True if (isinstance(ignore, str) and ignore==elemRef) or (isinstance(ignore, collections.abc.Iterable) and elemRef in ignore) else False

            #if SWC was ignored by user, also ignore its InternalBehavior and SwcImplementation elements in case they are in the same package
            if not ignoreElem and isinstance(elem, autosar.behavior.InternalBehavior):
                if (isinstance(ignore, str) and ignore==elem.componentRef) or (isinstance(ignore, collections.abc.Iterable) and elem.componentRef in ignore): ignoreElem = True
            if not ignoreElem and isinstance(elem, autosar.component.SwcImplementation):
                behavior = package.rootWS().find(elem.behaviorRef)
                if behavior is not None:
                    if (isinstance(ignore, str) and ignore==behavior.componentRef) or (isinstance(ignore, collections.abc.Iterable) and behavior.componentRef in ignore): ignoreElem = True
            if not ignoreElem and applyFilter(elemRef, filters):
                elementName = elem.__class__.__name__
                elementWriter = self.codeSwitcher.get(elementName)
                if elementWriter is not None:
                    result = elementWriter.writeElementCode(elem, localvars)
                    if result is None:
                        print("[PackageWriter] No return value: %s"%elementName)
                        continue
                    else:
                        lines.extend(result)
                else:
                    package.unhandledWriter.add(elementName)
            else:
                pass
        return lines
