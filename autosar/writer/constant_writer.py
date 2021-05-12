from autosar.writer.writer_base import ElementWriter
import autosar.constant

class XMLConstantWriter(ElementWriter):
    def __init__(self,version, patch):
        super().__init__(version, patch)

    def getSupportedXML(self):
        return ['Constant']

    def getSupportedCode(self):
        return []

    def writeElementXML(self, elem):
        if type(elem).__name__ == 'Constant':
            return self.writeConstantXML(elem)
        else:
            return None

    def writeElementCode(self, elem, localvars):
        raise NotImplementedError('writeElementCode')

    def writeConstantXML(self,elem):
        lines = []
        assert(isinstance(elem,autosar.constant.Constant))
        lines.append('<CONSTANT-SPECIFICATION>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        if elem.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
        if self.version>=4.0:
            lines.extend(self.indent(self._writeValueXMLV4(elem.value),1))
        else:
            lines.extend(self.indent(self._writeValueXMLV3(elem.value),1))
        lines.append('</CONSTANT-SPECIFICATION>')
        return lines

    def _writeValueXMLV3(self,elem):
        lines=[]
        lines.append('<VALUE>')
        lines.extend(self.indent(self._writeLiteralValueXML(elem),1))
        lines.append('</VALUE>')
        return lines

    def _writeLiteralValueXML(self,elem):
        if isinstance(elem,autosar.constant.IntegerValue):
            return self._writeIntegerLiteralXML(elem)
        elif isinstance(elem,autosar.constant.RecordValue):
            return self._writeRecordSpecificationXML(elem)
        elif isinstance(elem,autosar.constant.StringValue):
            return self._writeStringLiteralXML(elem)
        elif isinstance(elem,autosar.constant.BooleanValue):
            return self._writeBooleanLiteralXML(elem)
        elif isinstance(elem,autosar.constant.ArrayValue):
            return self._writeArraySpecificationXML(elem)
        else:
            raise NotImplementedError(type(elem))

    def _writeIntegerLiteralXML(self,elem):
        assert(isinstance(elem,autosar.constant.IntegerValue))
        lines=[]
        lines.append('<INTEGER-LITERAL>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tag = elem.rootWS().find(elem.typeRef).tag(self.version)
        lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
        lines.append(self.indent('<VALUE>%d</VALUE>'%elem.value,1))
        lines.append('</INTEGER-LITERAL>')
        return lines

    def _writeRecordSpecificationXML(self,elem):
        assert(isinstance(elem,autosar.constant.RecordValue))
        lines=[]
        lines.append('<RECORD-SPECIFICATION>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tag = elem.rootWS().find(elem.typeRef).tag(self.version)
        lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
        if len(elem.elements)==0: lines.append('<ELEMENTS/>')
        else:
            lines.append(self.indent('<ELEMENTS>',1))
            for childElem in elem.elements:
                lines.extend(self.indent(self._writeLiteralValueXML(childElem),2))
            lines.append(self.indent('</ELEMENTS>',1))
        lines.append('</RECORD-SPECIFICATION>')
        return lines

    def _writeStringLiteralXML(self,elem):
        assert(isinstance(elem,autosar.constant.StringValue))
        lines=[]
        lines.append('<STRING-LITERAL>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tag = elem.rootWS().find(elem.typeRef).tag(self.version)
        lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
        lines.append(self.indent('<VALUE>%s</VALUE>'%elem.value,1))
        lines.append('</STRING-LITERAL>')
        return lines

    def _writeBooleanLiteralXML(self,elem):
        assert(isinstance(elem,autosar.constant.BooleanValue))
        lines=[]
        lines.append('<BOOLEAN-LITERAL>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tag = elem.rootWS().find(elem.typeRef).tag(self.version)
        lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
        lines.append(self.indent('<VALUE>%s</VALUE>'%('true' if elem.value is True else 'false'),1))
        lines.append('</BOOLEAN-LITERAL>')
        return lines

    def _writeArraySpecificationXML(self,elem):
        assert(isinstance(elem,autosar.constant.ArrayValue))
        lines=[]
        lines.append('<ARRAY-SPECIFICATION>')
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tag = elem.rootWS().find(elem.typeRef).tag(self.version)
        lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(tag,elem.typeRef),1))
        if len(elem.elements)==0: lines.append('<ELEMENTS/>')
        else:
            lines.append(self.indent('<ELEMENTS>',1))
            for childElem in elem.elements:
                lines.extend(self.indent(self._writeLiteralValueXML(childElem),2))
            lines.append(self.indent('</ELEMENTS>',1))

        lines.append('</ARRAY-SPECIFICATION>')
        return lines

    def _writeValueXMLV4(self, value):
        lines=[]
        lines.append('<VALUE-SPEC>')
        lines.extend(self.indent(self.writeValueSpecificationXML(value),1))
        lines.append('</VALUE-SPEC>')
        return lines

class CodeConstantWriter(ElementWriter):
    def __init__(self,version, patch):
        super().__init__(version, patch)

    def getSupportedXML(self):
        return []

    def getSupportedCode(self):
        return ['Constant']

    def writeElementXML(self, elem):
        raise NotImplementedError('writeElementXML')

    def writeElementCode(self, elem, localvars):
        if type(elem).__name__ == 'Constant':
            return self.writeConstantCode(elem, localvars)
        else:
            return None

    def writeConstantCode(self, constant, localvars):
        lines=[]
        ws=localvars['ws']
        if not isinstance(constant, autosar.constant.Constant):
            raise ValueError('expected type autosar.constant.Constant')
        if constant.value is not None:
            dataType = ws.find(constant.value.typeRef, role='DataType')
            constructor=None
            if dataType is None:
                raise ValueError('invalid reference: '+constant.value.typeRef)
            if isinstance(constant.value, autosar.constant.ArrayValue):
                initValue = self._writeArrayValueConstantCode(constant.value, localvars)
            elif isinstance(constant.value, autosar.constant.IntegerValue):
                initValue = self._writeIntegerValueConstantCode(constant.value, localvars)
            elif isinstance(constant.value, autosar.constant.StringValue):
                initValue = self._writeStringValueConstantCode(constant.value, localvars)
            elif isinstance(constant.value, autosar.constant.BooleanValue):
                initValue = self._writeBooleanValueConstantCode(constant.value, localvars)
            elif isinstance(constant.value, autosar.constant.RecordValue):
                initValue = self._writeRecordValueConstantCode(constant.value, localvars)
            else:
                raise ValueError('unknown value type: '+type(constant.value))
            params=[repr(constant.name)]
            if ws.roles['DataType'] is not None:
                params.append(repr(dataType.name)) #use name only
            else:
                params.append(repr(dataType.ref)) #use full reference
            if initValue is not None:
                if isinstance(initValue, list):
                    lines.extend(self.writeDictCode('initValue', initValue))
                    params.append('initValue')
                else:
                    params.append(initValue)
            else:
                print(constant.name)
            if constant.adminData is not None:
                param = self.writeAdminDataCode(constant.adminData, localvars)
                assert(len(param)>0)
                params.append('adminData='+param)
            lines.append("package.createConstant(%s)"%(', '.join(params)))
        return lines

    def _writeArrayValueConstantCode(self, value, localvars):
        ws=localvars['ws']
        assert(isinstance(value, autosar.constant.ArrayValue))
        params=[]
        for elem in value.elements:
            if isinstance(elem, autosar.constant.ArrayValue):
                initValue = self._writeArrayValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.IntegerValue):
                initValue = self._writeIntegerValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.StringValue):
                initValue = self._writeStringValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.BooleanValue):
                initValue = self._writeBooleanValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.RecordValue):
                initValue = self._writeRecordValueConstantCode(elem, localvars)
                if isinstance(initValue, list): initValue="{%s}"%(', '.join(initValue)) #join any inner record init values
            else:
                raise ValueError('unknown value type: '+type(elem.value))
            params.append(initValue)
        if len(params)>0:
            return "[%s]"%(', '.join(params))
        return None

    def _writeIntegerValueConstantCode(self, value, localvars):
        return str(value.value)

    def _writeStringValueConstantCode(self, value, localvars):
        return repr(value.value)

    def _writeBooleanValueConstantCode(self, value, localvars):
        return str(value.value)

    def _writeRecordValueConstantCode(self, value, localvars):
        ws=localvars['ws']
        assert(isinstance(value, autosar.constant.RecordValue))
        params=[]
        for elem in value.elements:
            if isinstance(elem, autosar.constant.ArrayValue):
                initValue = self._writeArrayValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.IntegerValue):
                initValue = self._writeIntegerValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.StringValue):
                initValue = self._writeStringValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.BooleanValue):
                initValue = self._writeBooleanValueConstantCode(elem, localvars)
            elif isinstance(elem, autosar.constant.RecordValue):
                initValue = self._writeRecordValueConstantCode(elem, localvars)
                if isinstance(initValue, list): initValue="{%s}"%(', '.join(initValue)) #join any inner record init values
            else:
                raise ValueError('unknown value type: '+type(elem.value))
            params.append('"%s": %s'%(elem.name, initValue))
        if len(params)>0:
            text = "{%s}"%(', '.join(params))
            if len(text)>200: #line will be way too long
                return params
            else:
                return text
        return None
