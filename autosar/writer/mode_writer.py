from autosar.writer.writer_base import ElementWriter
import autosar.behavior

class XMLModeWriter(ElementWriter):
    def __init__(self, version, patch):
        super().__init__(version, patch)

    def getSupportedXML(self):
        return 'ModeDeclarationGroup'

    def getSupportedCode(self):
        return []

    def writeElementXML(self, elem):
        if type(elem).__name__ == 'ModeDeclarationGroup':
            return self.writeModeDeclarationGroupXML(elem)
        else:
            return None

    def writeElementCode(self, elem, localvars):
        raise NotImplementedError('writeElementCode')

    def writeModeDeclarationGroupXML(self, modeDeclGroup):
        assert(isinstance(modeDeclGroup,autosar.mode.ModeDeclarationGroup))
        lines=[]
        ws = modeDeclGroup.rootWS()
        assert(ws is not None)

        lines.append('<%s>'%modeDeclGroup.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%modeDeclGroup.name,1))
        if modeDeclGroup.category is not None:
            lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%modeDeclGroup.category,1))
        if modeDeclGroup.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(modeDeclGroup.adminData),1))
        if modeDeclGroup.initialModeRef is not None:
            modeElem = ws.find(modeDeclGroup.initialModeRef)
            if (modeElem is None):
                raise ValueError("invalid mode reference: '%s'"%modeDeclGroup.typeRef)
            else:
                lines.append(self.indent('<INITIAL-MODE-REF DEST="%s">%s</INITIAL-MODE-REF>'%(modeElem.tag(self.version),modeElem.ref),1))
        if len(modeDeclGroup.modeDeclarations)>0:
            lines.append(self.indent('<MODE-DECLARATIONS>',1))
            for elem in modeDeclGroup.modeDeclarations:
                lines.append(self.indent('<%s>'%elem.tag(self.version),2))
                lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,3))
                if elem.value is not None:
                    lines.append(self.indent('<VALUE>{:d}</VALUE>'.format(elem.value),3))
                lines.append(self.indent('</%s>'%elem.tag(self.version),2))
            lines.append(self.indent('</MODE-DECLARATIONS>',1))
        lines.append('</%s>'%modeDeclGroup.tag(self.version))
        return lines
