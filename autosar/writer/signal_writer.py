from autosar.writer.writer_base import ElementWriter
import autosar.datatype

class SignalWriter(ElementWriter):
    def __init__(self,version, patch):
        super().__init__(version, patch)

    def getSupportedXML(self):
        return ['SYSTEM-SIGNAL']

    def getSupportedCode(self):
        return []

    def writeElementXML(self, elem):
        if type(elem).__name__ == 'SYSTEM-SIGNAL':
            return self.writeSignalXML(elem)
        else:
            return None

    def writeElementCode(self, elem, localvars):
        raise NotImplementedError('writeElementCode')

    def writeSignalXML(self,elem):
        assert isinstance(elem,autosar.signal.SystemSignal)
        lines = []
        lines.append('<SYSTEM-SIGNAL>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        if elem.desc is not None:
            tmp = self.writeDescXML(elem)
            if tmp is not None: lines.extend(self.indent(tmp,1))
        if elem.dataTypeRef is not None:
            ws = elem.rootWS()
            typeElem = ws.find(elem.dataTypeRef, role="DataType")
            if (typeElem is None):
                raise ValueError("invalid type reference: '%s'"%elem.typeRef)
            else:
                lines.append(self.indent('<DATA-TYPE-REF DEST="%s">%s</DATA-TYPE-REF>'%(typeElem.tag(self.version),typeElem.ref),1))
        if elem.initValueRef is not None:
            ws = elem.rootWS()
            constantElem=ws.find(elem.initValueRef,role="Constant")
            if (constantElem is None): ##   start cheating patch for handle "role" for arrays & records constant refs, looking at datatype instead of Const REC element type. Shall be same for a consitant designed system.
                datatypeElem=ws.find(elem.dataTypeRef, role="DataType")
                if datatypeElem.tag(self.version) == 'INTEGER-TYPE':
                    xmlValueTypeTxt= 'INTEGER-LITERAL'
                elif datatypeElem.tag(self.version) == 'STRING-TYPE':
                    xmlValueTypeTxt= 'STRING-LITERAL'
                elif datatypeElem.tag(self.version) == 'BOOLEAN-TYPE':
                    xmlValueTypeTxt= 'BOOLEAN-LITERAL'   ## end cheating patch for record arrays
                else:
                    raise ValueError("invalid type reference: '%s'" % elem.typeRef)
            else:
                xmlValueTypeTxt=constantElem.tag(self.version)

            lines.append(self.indent('<INIT-VALUE-REF DEST="%s">%s</INIT-VALUE-REF>'%(xmlValueTypeTxt,elem.initValueRef),1))
        if elem.length is not None:
            lines.append(self.indent('<LENGTH>%s</LENGTH>'%(elem.length),1))
        lines.append('</SYSTEM-SIGNAL>')
        return lines
