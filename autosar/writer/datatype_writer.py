from autosar.writer.writer_base import ElementWriter
import autosar.base
import autosar.datatype
from fractions import Fraction

class XMLDataTypeWriter(ElementWriter):
    def __init__(self,version, patch):
        super().__init__(version, patch)

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {
                              'ArrayDataType': self.writeArrayDataTypeXML,
                              'BooleanDataType': self.writeBooleanDataTypeXML,
                              'IntegerDataType': self.writeIntegerTypeXML,
                              'RealDataType': self.writeRealDataTypeXML,
                              'RecordDataType': self.writeRecordDataTypeXML,
                              'StringDataType': self.writeStringTypeXML,
                              'CompuMethod': self.writeCompuMethodXML,
                              'Unit': self.writeUnitXML,
            }
        elif self.version >= 4.0:
            self.switcher = {
                              'CompuMethod': self.writeCompuMethodXML,
                              'DataConstraint': self.writeDataConstraintXML,
                              'ImplementationDataType': self.writeImplementationDataTypeXML,
                              'SwBaseType': self.writeSwBaseTypeXML,
                              'Unit': self.writeUnitXML,
                              'DataTypeMappingSet': self.writeDataTypeMappingSetXML,
                              'ApplicationPrimitiveDataType': self.writeApplicationPrimitiveDataTypeXML,
                              'ApplicationArrayDataType': self.writeApplicationArrayDataTypeXML,
                              'ApplicationRecordDataType': self.writeApplicationRecordDataTypeXML
            }
        else:
            self.switcher = {}

    def getSupportedXML(self):
        return self.switcher.keys()

    def getSupportedCode(self):
        return []

    def writeElementXML(self, elem):
        xmlWriteFunc = self.switcher.get(type(elem).__name__)
        if xmlWriteFunc is not None:
            return xmlWriteFunc(elem)
        else:
            return None

    def writeElementCode(self, elem, localvars):
        raise NotImplementedError('writeElementCode')

    def writeIntegerTypeXML(self, elem):
        assert isinstance(elem,autosar.datatype.IntegerDataType)
        lines = ["<%s>"%elem.tag(self.version)]
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        if elem.compuMethodRef is not None:
            lines.append(self.indent('<SW-DATA-DEF-PROPS>',1))
            lines.append(self.indent('<COMPU-METHOD-REF DEST="COMPU-METHOD">%s</COMPU-METHOD-REF>'%elem.compuMethodRef,2))
            lines.append(self.indent("</SW-DATA-DEF-PROPS>",1))
        lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="%s">%d</LOWER-LIMIT>'%(elem.minValType, elem.minVal),1))
        lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="%s">%d</UPPER-LIMIT>'%(elem.maxValType, elem.maxVal),1))
        lines.append('</%s>'%elem.tag(self.version))
        return lines

    def writeRecordDataTypeXML(self, elem):
        assert(isinstance(elem,autosar.datatype.RecordDataType))
        ws=elem.rootWS()
        assert(isinstance(ws,autosar.Workspace))
        lines=[]
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        lines.append(self.indent('<ELEMENTS>',1))
        for childElem in elem.elements:
            lines.append(self.indent('<RECORD-ELEMENT>',2))
            lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%childElem.name,3))
            dataType=ws.find(childElem.typeRef, role='DataType')
            if dataType is None:
                raise ValueError('invalid reference: '+childElem.typeRef)
            lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(dataType.tag(self.version),dataType.ref),3))
            lines.append(self.indent('</RECORD-ELEMENT>',2))

        lines.append(self.indent('</ELEMENTS>',1))
        lines.append('</%s>'%elem.tag(self.version))
        return lines

    def writeCompuMethodXML(self, elem):
        assert(isinstance(elem, autosar.datatype.CompuMethod))
        ws=elem.rootWS()
        assert(isinstance(ws,autosar.Workspace))
        lines=[]
        lines.append('<{}>'.format(elem.tag(self.version)))
        lines.append(self.indent('<SHORT-NAME>{}</SHORT-NAME>'.format(elem.name),1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>{}</CATEGORY>'.format(elem.category),1))
        if elem.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
        if elem.unitRef is not None:
            unit = ws.find(elem.unitRef)
            if unit is None:
                raise autosar.base.InvalidUnitRef(elem.unitRef)
            lines.append(self.indent('<UNIT-REF DEST="{0}">{1}</UNIT-REF>'.format(unit.tag(self.version),elem.unitRef),1))
        if elem.intToPhys is not None:
            tag = 'COMPU-INTERNAL-TO-PHYS'
            lines.extend(self.indent(self._writeComputationXML(ws, elem.intToPhys, tag),1))
        if elem.physToInt is not None:
            tag = 'COMPU-PHYS-TO-INTERNAL'
            lines.extend(self.indent(self._writeComputationXML(ws, elem.physToInt, tag),1))
        lines.append('</{}>'.format(elem.tag(self.version)))
        return lines

    def _writeComputationXML(self, ws, computation, tag):
        assert(isinstance(computation, autosar.datatype.Computation))
        lines=[]
        lines.append('<{}>'.format(tag))
        lines.append(self.indent('<COMPU-SCALES>',1))
        for compuScale in computation.elements:
            lines.extend(self.indent(self._writeCompuScaleXML(ws, compuScale), 2))
        lines.append(self.indent('</COMPU-SCALES>',1))
        if computation.defaultValue is not None:
            lines.append(self.indent('<COMPU-DEFAULT-VALUE>', 1))
            if isinstance(computation.defaultValue, (float, int)):
                lines.append(self.indent('<V>{}</V>'.format(self._numberToString(computation.defaultValue)), 2))
            else:
                lines.append(self.indent('<VT>{}</VT>'.format(str(computation.defaultValue)), 2))
            lines.append(self.indent('</COMPU-DEFAULT-VALUE>', 1))
        lines.append('</{}>'.format(tag))
        return lines

    def _writeCompuScaleXML(self, ws, elem):
        lines = []
        lines.append('<{}>'.format(elem.tag(self.version)))
        if elem.label is not None:
            lines.append(self.indent('<SHORT-LABEL>%s</SHORT-LABEL>'%elem.label, 1))
        if elem.symbol is not None:
            lines.append(self.indent('<SYMBOL>%s</SYMBOL>'%elem.symbol, 1))
        if elem.mask is not None:
            lines.append(self.indent('<MASK>%d</MASK>'%elem.mask, 1))

        if elem.lowerLimit is not None or elem.upperLimit is not None:
            if self.version>=4.0:
                lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0}">{1}</LOWER-LIMIT>'.format(elem.lowerLimitType,elem.lowerLimit), 1))
                lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0}">{1}</UPPER-LIMIT>'.format(elem.upperLimitType,elem.upperLimit), 1))
            else:
                lines.append(self.indent('<LOWER-LIMIT>%d</LOWER-LIMIT>'%elem.lowerLimit, 1))
                lines.append(self.indent('<UPPER-LIMIT>%d</UPPER-LIMIT>'%elem.upperLimit, 1))
        if elem.offset is not None or elem.numerator is not None or elem.denominator is not None:
            lines.extend(self.indent(self._writeCompuRationalXML(elem),1))
        if elem.textValue is not None:
            lines.extend(self.indent(self._writeCompuConstXML(elem),1))
        lines.append('</{}>'.format(elem.tag(self.version)))
        return lines

    def _writeCompuRationalXML(self, elem):
        lines = []
        lines.append('<COMPU-RATIONAL-COEFFS>')
        lines.append(self.indent('<COMPU-NUMERATOR>', 1))
        lines.append(self.indent('<V>{}</V>'.format(elem.offset), 2))
        lines.append(self.indent('<V>{}</V>'.format(elem.numerator), 2))
        lines.append(self.indent('</COMPU-NUMERATOR>', 1))
        lines.append(self.indent('<COMPU-DENOMINATOR>',1))
        lines.append(self.indent('<V>{}</V>'.format(elem.denominator),2))
        lines.append(self.indent('</COMPU-DENOMINATOR>', 1))
        lines.append('</COMPU-RATIONAL-COEFFS>')
        return lines

    def _writeCompuConstXML(self, elem):
        lines = []
        lines.append('<COMPU-CONST>')
        lines.append(self.indent('<VT>{0}</VT>'.format(elem.textValue), 1))
        lines.append('</COMPU-CONST>')
        return lines

    def writeUnitXML(self, elem):
        lines=[]
        lines.append('<{}>'.format(elem.tag(self.version)))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        if elem.displayName is not None:
            lines.append(self.indent('<DISPLAY-NAME>%s</DISPLAY-NAME>'%elem.displayName,1))
        if self.version >= 4.0:
            if elem.factor is not None:
                lines.append(self.indent('<FACTOR-SI-TO-UNIT>%s</FACTOR-SI-TO-UNIT>'%elem.factor,1))
            if elem.offset is not None:
                lines.append(self.indent('<OFFSET-SI-TO-UNIT>%s</OFFSET-SI-TO-UNIT>'%elem.offset,1))
        lines.append('</{}>'.format(elem.tag(self.version)))
        return lines

    def writeArrayDataTypeXML(self, elem):
        assert(isinstance(elem,autosar.datatype.ArrayDataType))
        ws=elem.rootWS()
        assert(isinstance(ws,autosar.Workspace))

        lines=[]
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        lines.append(self.indent('<ELEMENT>',1))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,2))
        dataType=ws.find(elem.typeRef)
        if dataType is None: raise ValueError('invalid reference: '+elem.typeRef)
        lines.append(self.indent('<TYPE-TREF DEST="%s">%s</TYPE-TREF>'%(dataType.tag(self.version),dataType.ref),2))
        lines.append(self.indent('<MAX-NUMBER-OF-ELEMENTS>%d</MAX-NUMBER-OF-ELEMENTS>'%elem.length,2))
        lines.append(self.indent('</ELEMENT>',1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeBooleanDataTypeXML(self, elem):
        assert(isinstance(elem,autosar.datatype.BooleanDataType))
        lines=[]
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeRealDataTypeXML(self, elem):
        assert(isinstance(elem,autosar.datatype.RealDataType))
        lines=[]
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        if elem.minValType=="INFINITE":
            lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="INFINITE"></LOWER-LIMIT>',1))
        else:
            if isinstance(elem.minVal, str):
                lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0.minValType}">{0.minVal}</LOWER-LIMIT>'.format(elem),1))
            else:
                lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0.minValType}">{0.minVal:f}</LOWER-LIMIT>'.format(elem),1))
        if elem.maxValType=="INFINITE":
            lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="INFINITE"></UPPER-LIMIT>',1))
        else:
            if isinstance(elem.maxVal, str):
                lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0.maxValType}">{0.maxVal}</UPPER-LIMIT>'.format(elem),1))
            else:
                lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0.maxValType}">{0.maxVal:f}</UPPER-LIMIT>'.format(elem),1))
        lines.append(self.indent('<ALLOW-NAN>%s</ALLOW-NAN>'%('true' if elem.hasNaN else 'false'),1))
        lines.append(self.indent('<ENCODING>%s</ENCODING>'%elem.encoding,1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeStringTypeXML(self, elem):
        assert(isinstance(elem,autosar.datatype.StringDataType))
        lines=[]
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        lines.append(self.indent('<ENCODING>%s</ENCODING>'%elem.encoding,1))
        lines.append(self.indent('<MAX-NUMBER-OF-CHARS>%d</MAX-NUMBER-OF-CHARS>'%elem.length,1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeDataConstraintXML(self, elem):
        assert(isinstance(elem,autosar.datatype.DataConstraint))
        ws=elem.rootWS()
        assert(isinstance(ws,autosar.Workspace))

        lines=[]
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        if elem.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
        lines.append(self.indent('<DATA-CONSTR-RULES>', 1))
        for rule in elem.rules:
            lines.extend(self.indent(self.writeDataConstraintRuleXML(rule, elem.constraintLevel), 2))
        lines.append(self.indent('</DATA-CONSTR-RULES>', 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeDataConstraintRuleXML(self, rule, constraintLevel):
        lines = []
        lines.append("<DATA-CONSTR-RULE>")
        if isinstance(constraintLevel, int):
            lines.append(self.indent('<{0}>{1}</{0}>'.format('CONSTR-LEVEL', str(constraintLevel)), 1))
        if isinstance(rule, autosar.datatype.InternalConstraint):
            tag_name = 'INTERNAL-CONSTRS'
        elif isinstance(rule, autosar.datatype.PhysicalConstraint):
            tag_name = 'PHYS-CONSTRS'
        else:
            raise NotImplementedError(str(type(rule)))
        lines.append(self.indent('<{}>'.format(tag_name), 1))
        lowerLimit = self._numberToString(rule.lowerLimit)
        upperLimit = self._numberToString(rule.upperLimit)

        lines.append(self.indent('<LOWER-LIMIT INTERVAL-TYPE="{0}">{1}</LOWER-LIMIT>'.format(rule.lowerLimitType, lowerLimit), 2))
        lines.append(self.indent('<UPPER-LIMIT INTERVAL-TYPE="{0}">{1}</UPPER-LIMIT>'.format(rule.lowerLimitType, upperLimit), 2))
        lines.append(self.indent('</{}>'.format(tag_name), 1))
        lines.append("</DATA-CONSTR-RULE>")
        return lines

    def writeImplementationDataTypeXML(self, elem):
        assert(isinstance(elem, autosar.datatype.ImplementationDataType))
        ws=elem.rootWS()
        assert(ws is not None)
        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent("<SHORT-NAME>%s</SHORT-NAME>"%elem.name, 1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        lines.append(self.indent("<CATEGORY>%s</CATEGORY>" % elem.category, 1))
        if elem.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
        lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
        if len(elem.variantProps)>=0:
            lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variantProps),2))
        lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
        if elem.dynamicArraySizeProfile is not None:
            lines.append(self.indent("<DYNAMIC-ARRAY-SIZE-PROFILE>%s</DYNAMIC-ARRAY-SIZE-PROFILE>"%(str(elem.dynamicArraySizeProfile)), 1))
        if len(elem.subElements)>0:
            lines.append(self.indent("<SUB-ELEMENTS>", 1))
            for subElem in elem.subElements:
                lines.extend(self.indent(self.writeImplementationDataElementXML(ws, subElem),2))
            lines.append(self.indent("</SUB-ELEMENTS>", 1))
        if elem.symbolProps is not None:
            lines.extend(self.indent(self.writeSymbolPropsXML(elem.symbolProps),1))
        if elem.typeEmitter is not None:
            lines.append(self.indent("<TYPE-EMITTER>%s</TYPE-EMITTER>"%(elem.typeEmitter), 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeSwPointerTargetPropsXML(self, ws, elem):
        assert(isinstance(elem, autosar.base.SwPointerTargetProps))
        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        if elem.targetCategory is not None:
            lines.append(self.indent('<TARGET-CATEGORY>%s</TARGET-CATEGORY>'%(elem.targetCategory),1))
        lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
        if len(elem.variants)>=0:
            lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variants),2))
        lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeSwBaseTypeXML(self, elem):
        assert(isinstance(elem, autosar.datatype.SwBaseType))
        ws = elem.rootWS()
        assert(ws is not None)
        lines = []
        lines.append("<{}>".format(elem.tag(self.version)))
        lines.append(self.indent('<SHORT-NAME>{}</SHORT-NAME>'.format(elem.name),1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>{}</CATEGORY>'.format(elem.category),1))
        if elem.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
        if elem.size is not None:
            lines.append(self.indent('<BASE-TYPE-SIZE>{:d}</BASE-TYPE-SIZE>'.format(elem.size),1))
        if elem.typeEncoding is None and ws.profile.swBaseTypeEncodingDefault is not None:
            lines.append(self.indent('<BASE-TYPE-ENCODING>{}</BASE-TYPE-ENCODING>'.format(str(ws.profile.swBaseTypeEncodingDefault)),1))
        else:
            lines.append(self.indent('<BASE-TYPE-ENCODING>{}</BASE-TYPE-ENCODING>'.format(elem.typeEncoding),1))
        if elem.nativeDeclaration is not None:
            lines.append(self.indent('<NATIVE-DECLARATION>{}</NATIVE-DECLARATION>'.format(elem.nativeDeclaration),1))
        lines.append("</{}>".format(elem.tag(self.version)))
        return lines

    def writeImplementationDataElementXML(self, ws, elem):
        assert(isinstance(elem, autosar.datatype.ImplementationDataTypeElement))
        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None: lines.extend(self.indent(tmp,1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
        if elem.adminData is not None:
            lines.extend(self.indent(self.writeAdminDataXML(elem.adminData),1))
        if elem.arraySize is not None:
            lines.append(self.indent('<ARRAY-SIZE>%s</ARRAY-SIZE>'%elem.arraySize,1))
        if elem.arraySizeSemantics is not None:
            lines.append(self.indent('<ARRAY-SIZE-SEMANTICS>%s</ARRAY-SIZE-SEMANTICS>'%elem.arraySizeSemantics,1))
        if len(elem.variantProps)>=0:
            lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
            lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variantProps),2))
            lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeDataTypeMappingSetXML(self, elem):
        assert(isinstance(elem, autosar.datatype.DataTypeMappingSet))
        ws=elem.rootWS()
        assert(ws is not None)

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        dataTypeMappings = []
        modeRequestMappings = []
        for key in sorted(elem.applicationTypeMap.keys()):
            dataTypeMappings.append(elem.getDataTypeMapping(key))
        for key in sorted(elem.modeRequestMap.keys()):
            modeRequestMappings.append(elem.getModeRequestMapping(key))
        if len(dataTypeMappings) > 0:
            lines.append(self.indent('<DATA-TYPE-MAPS>',1))
            for dataTypeMapping in dataTypeMappings:
                lines.extend(self.indent(self.writeDataTypeMapXML(ws, dataTypeMapping),2))
            lines.append(self.indent('</DATA-TYPE-MAPS>',1))
        if len(modeRequestMappings) > 0:
            lines.append(self.indent('<MODE-REQUEST-TYPE-MAPS>',1))
            for modeRequestMapping in modeRequestMappings:
                lines.extend(self.indent(self.writeModeRequestMapXML(ws, modeRequestMapping),2))
            lines.append(self.indent('</MODE-REQUEST-TYPE-MAPS>',1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeDataTypeMapXML(self, ws, elem):
        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        applicationDataType = ws.find(elem.applicationDataTypeRef)
        if applicationDataType is None:
            raise ValueError('Invalid type reference:' + elem.applicationDataTypeRef)
        implementationDataType = ws.find(elem.implementationDataTypeRef)
        if implementationDataType is None:
            raise ValueError('Invalid type reference:' + elem.implementationDataTypeRef)
        lines.append(self.indent('<APPLICATION-DATA-TYPE-REF DEST="%s">%s</APPLICATION-DATA-TYPE-REF>'%(applicationDataType.tag(self.version), applicationDataType.ref),1))
        lines.append(self.indent('<IMPLEMENTATION-DATA-TYPE-REF DEST="%s">%s</IMPLEMENTATION-DATA-TYPE-REF>'%(implementationDataType.tag(self.version), implementationDataType.ref),1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeModeRequestMapXML(self, ws, elem):
        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        modeDeclarationGroup = ws.find(elem.modeDeclarationGroupRef)
        if modeDeclarationGroup is None:
            raise ValueError('Invalid type reference:' + elem.implementationDataTypeRef)
        implementationDataType = ws.find(elem.implementationDataTypeRef)
        if implementationDataType is None:
            raise ValueError('Invalid type reference:' + elem.implementationDataTypeRef)
        lines.append(self.indent('<IMPLEMENTATION-DATA-TYPE-REF DEST="%s">%s</IMPLEMENTATION-DATA-TYPE-REF>'%(implementationDataType.tag(self.version), implementationDataType.ref),1))
        lines.append(self.indent('<MODE-GROUP-REF DEST="%s">%s</MODE-GROUP-REF>'%(modeDeclarationGroup.tag(self.version), modeDeclarationGroup.ref),1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeApplicationPrimitiveDataTypeXML(self, elem):
        assert(isinstance(elem, autosar.datatype.ApplicationPrimitiveDataType))
        ws=elem.rootWS()
        assert(ws is not None)

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None:
            lines.extend(self.indent(tmp,1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
        if len(elem.variantProps)>=0:
            lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
            lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variantProps),2))
            lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeApplicationArrayDataTypeXML(self, elem):
        assert(isinstance(elem, autosar.datatype.ApplicationArrayDataType))
        ws=elem.rootWS()
        assert(ws is not None)

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        lines.append(self.indent('<SHORT-NAME>%s</SHORT-NAME>'%elem.name,1))
        tmp = self.writeDescXML(elem)
        if tmp is not None:
            lines.extend(self.indent(tmp,1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>%s</CATEGORY>'%elem.category,1))
        if len(elem.variantProps)>=0:
            lines.append(self.indent("<SW-DATA-DEF-PROPS>", 1))
            lines.extend(self.indent(self.writeSwDataDefPropsVariantsXML(ws, elem.variantProps),2))
            lines.append(self.indent("</SW-DATA-DEF-PROPS>", 1))
        lines.extend(self.indent(self.writeApplicationArrayDataElementXml(ws, elem.element), 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeApplicationArrayDataElementXml(self, ws, elem):
        assert(isinstance(elem, autosar.datatype.ApplicationArrayElement))

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        if elem.name is not None:
            lines.append(self.indent('<SHORT-NAME>{}</SHORT-NAME>'.format(elem.name),1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>{}</CATEGORY>'.format(elem.category),1))
        if elem.typeRef is not None:
            dataType = ws.find(elem.typeRef)
            if dataType is None:
                raise autosar.base.InvalidDataTypeRef(elem.typeRef)
            lines.append(self.indent('<TYPE-TREF DEST="{0}">{1}</TYPE-TREF>'.format(dataType.tag(ws.version), elem.typeRef),1))
        if elem.sizeHandling is not None:
            lines.append(self.indent('<ARRAY-SIZE-HANDLING>{}</ARRAY-SIZE-HANDLING>'.format(elem.sizeHandling),1))
        if elem.sizeSemantics is not None:
            lines.append(self.indent('<ARRAY-SIZE-SEMANTICS>{}</ARRAY-SIZE-SEMANTICS>'.format(elem.sizeSemantics),1))
        if elem.arraySize is not None:
            lines.append(self.indent('<MAX-NUMBER-OF-ELEMENTS>{:d}</MAX-NUMBER-OF-ELEMENTS>'.format(elem.arraySize),1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def writeApplicationRecordDataTypeXML(self, elem):
        assert(isinstance(elem, autosar.datatype.ApplicationRecordDataType))
        ws=elem.rootWS()
        assert(ws is not None)

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        if elem.name is not None:
            lines.append(self.indent('<SHORT-NAME>{}</SHORT-NAME>'.format(elem.name),1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>{}</CATEGORY>'.format(elem.category),1))
        lines.append(self.indent('<ELEMENTS>', 1))
        for childElem in elem.elements:
            lines.extend(self.indent(self._ApplicationRecordElementXML(ws, childElem), 2))
        lines.append(self.indent('</ELEMENTS>', 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines

    def _ApplicationRecordElementXML(self, ws, elem):
        assert(isinstance(elem, autosar.datatype.ApplicationRecordElement))

        lines = []
        lines.append("<%s>"%elem.tag(self.version))
        if elem.name is not None:
            lines.append(self.indent('<SHORT-NAME>{}</SHORT-NAME>'.format(elem.name), 1))
        if elem.category is not None:
            lines.append(self.indent('<CATEGORY>{}</CATEGORY>'.format(elem.category),1))
        if elem.typeRef is not None:
            dataType = ws.find(elem.typeRef, role = 'DataType')
            if dataType is None:
                raise autosar.base.InvalidDataTypeRef(elem.typeRef)
            lines.append(self.indent('<TYPE-TREF DEST="{0}">{1}</TYPE-TREF>'.format(dataType.tag(self.version), dataType.ref), 1))
        lines.append("</%s>"%elem.tag(self.version))
        return lines


class CodeDataTypeWriter(ElementWriter):
    def __init__(self, version, patch):
        super().__init__(version, patch)

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {
                              'ArrayDataType': self.writeArrayDataTypeCode,
                              'BooleanDataType': self.writeBooleanDataTypeCode,
                             'IntegerDataType': self.writeIntegerTypeCode,
                             'RealDataType': self.writeRealDataTypeCode,
                             'RecordDataType': self.writeRecordDataTypeCode,
                             'StringDataType': self.writeStringTypeCode,
                             'CompuMethodConst': self.writeCompuMethodCode,
                             'CompuMethodRational': self.writeCompuMethodCode,
                             'DataTypeUnitElement': self.writeDataTypeUnitElementCode
            }
        elif self.version >= 4.0:
            self.switcher = {
            }
        else:
            self.switcher = {}

    def getSupportedXML(self):
        return []

    def getSupportedCode(self):
        return self.switcher.keys()

    def writeElementXML(self, elem):
        raise NotImplementedError('writeElementXML')

    def writeElementCode(self, elem, localvars):
        codeWriteFunc = self.switcher.get(type(elem).__name__)
        if codeWriteFunc is not None:
            return codeWriteFunc(elem, localvars)
        else:
            return None

    def writeArrayDataTypeCode(self, dataType, localvars):
        assert(isinstance(dataType,autosar.datatype.ArrayDataType))
        lines=[]
        ws=localvars['ws']
        params=[repr(dataType.name)]
        childType = ws.find(dataType.typeRef)
        if childType is None:
            raise ValueError('invalid reference: '+dataType.typeRef)
        if ws.roles['DataType'] is not None:
            params.append(repr(childType.name))
        else:
            params.append(repr(childType.ref))
        params.append(str(dataType.length))

        if dataType.adminData is not None:
            param = self.writeAdminDataCode(dataType.adminData, localvars)
            assert(len(param)>0)
            params.append('adminData='+param)
        if hasattr(dataType, 'desc'):
            lines.append('dataType=package.createArrayDataType(%s)'%(', '.join(params)))
            lines.append('dataType.desc = """%s"""'%dataType.desc)
        else:
            lines.append('package.createArrayDataType(%s)'%(', '.join(params)))
        return lines

    def writeBooleanDataTypeCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        #name
        params=[repr(dataType.name)]
        if hasattr(dataType, 'desc'):
            lines.append('dataType=package.createBooleanDataType(%s)'%(', '.join(params)))
            lines.append('dataType.desc = """%s"""'%dataType.desc)
        else:
            lines.append('package.createBooleanDataType(%s)'%(', '.join(params)))
        return lines

    def writeIntegerTypeCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        params=[repr(dataType.name)]

        if dataType.compuMethodRef is not None:
            compuMethod = ws.find(dataType.compuMethodRef)
            if compuMethod is None:
                raise ValueError('invalid reference: '+dataType.compuMethodRef)
            if isinstance(compuMethod, autosar.datatype.CompuMethodConst):
                isUnconventionalType=False
                if (dataType.minVal != 0) or (dataType.maxVal != (len(compuMethod.elements)-1)):
                    isUnconventionalType=True
                else:
                    params2=[]
                    index=0
                    for element in compuMethod.elements:
                        if isinstance(element, autosar.datatype.CompuConstElement):
                            if (element.lowerLimit==index) and (element.upperLimit==index):
                                params2.append(repr(element.textValue))
                            else:
                                isUnconventionalType=True
                                break
                        else:
                            raise ValueError('unsupported value found of type: '+str(type(element)))
                        index+=1
                if isUnconventionalType:
                    params.append(str(dataType.minVal))
                    params.append(str(dataType.maxVal))
                    params2=[]
                    for element in compuMethod.elements:
                        if isinstance(element, autosar.datatype.CompuConstElement):
                            if element.lowerLimit==element.upperLimit:
                                params2.append('(%d, %s)'%(element.lowerLimit, repr(element.textValue)))
                            else:
                                params2.append('(%d, %d, %s)'%(element.lowerLimit, element.upperLimit, repr(element.textValue)))
                        else:
                            raise ValueError('unsupported value found of type: '+str(type(element)))
                text='['+','.join(params2)+']'
                if len(text)>200:
                    #this line is way too long, split it
                    lines.extend(self.writeListCode('valueTableList',params2))
                    params.append('valueTable=valueTableList')
                else:
                    params.append('valueTable='+text)
            elif isinstance(compuMethod, autosar.datatype.CompuMethodRational):
                params.append(str(dataType.minVal))
                params.append(str(dataType.maxVal))
                if len(compuMethod.elements)>1:
                    raise NotImplementedError('CompuMethodRational with multiple elements not implemented')
                elif len(compuMethod.elements)==1:
                    elem =compuMethod.elements[0]
                    #offset
                    params.append('offset='+str(elem.offset))
                    #scaling
                    if elem.denominator=="1":
                        params.append("scaling="+elem.numerator)
                    else:
                        params.append("scaling=%s/%s"%(elem.numerator,elem.numerator))
                    #for now, force float for all scaling factors
                    params.append("forceFloatScaling=True")
                #unit
                if compuMethod.unitRef is not None:
                    unit = ws.find(compuMethod.unitRef, role="Unit")
                    if unit is None:
                        raise ValueError('invalid reference: '+compuMethod.unitRef)
                    if ws.roles['Unit'] is not None:
                        ref = unit.name #use name only
                    else:
                        ref = unit.ref #use full reference
                    params.append('unit='+repr(ref))
            else:
                raise ValueError('unknown type:'+str(type(compuMethod)))
        else:
            params.append(str(dataType.minVal))
            params.append(str(dataType.maxVal))
        if dataType.adminData is not None:
            param = self.writeAdminDataCode(dataType.adminData, localvars)
            assert(len(param)>0)
            params.append('adminData='+param)
        if hasattr(dataType, 'desc'):
            lines.append('dataType=package.createIntegerDataType(%s)'%(', '.join(params)))
            lines.append('dataType.desc = """%s"""'%dataType.desc)
        else:
            lines.append('package.createIntegerDataType(%s)'%(', '.join(params)))
        return lines

    def writeRealDataTypeCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        #name
        params=[repr(dataType.name)]
        #minVal
        if dataType.minVal is None:
            params.append('None')
        else:
            params.append('decimal.Decimal("%s")'%(str(dataType.minVal)))
        #maxVal
        if dataType.maxVal is None:
            params.append('None')
        else:
            params.append('decimal.Decimal("%s")'%(str(dataType.maxVal)))
        #minValType
        if dataType.minValType != 'CLOSED':
            params.append('minValType='+repr(dataType.minValType))
        #maxValType
        if dataType.maxValType != 'CLOSED':
            params.append('maxValType='+repr(dataType.maxValType))
        #hasNan
        if dataType.hasNaN:
            params.append('hasNaN=True')
        #encoding
        if dataType.encoding != 'SINGLE':
            params.append('encoding='+repr(dataType.encoding))
        #adminData
        if dataType.adminData is not None:
            param = self.writeAdminDataCode(dataType.adminData, localvars)
            assert(len(param)>0)
            params.append('adminData='+param)
        if hasattr(dataType, 'desc'):
            lines.append('dataType=package.createRealDataType(%s)'%(', '.join(params)))
            lines.append('dataType.desc = """{0}"""'.format(dataType.desc))
        else:
            lines.append('package.createRealDataType(%s)'%(', '.join(params)))
        return lines

    def writeRecordDataTypeCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        params=[repr(dataType.name)]
        params2=[]
        for elem in dataType.elements:
            childType=ws.find(elem.typeRef)
            if childType is None:
                raise ValueError('invalid reference: '+dataType.typeRef)
            if ws.roles['DataType'] is not None:
                ref = childType.name #use only the name
            else:
                ref = childType.ref #use full reference
            params2.append('(%s,%s)'%(repr(elem.name), repr(ref))) #we use the tuple option since this is most convenient
        if len(dataType.elements)>4:
            lines.extend(self.writeListCode('elementList',params2))
            params.append('elementList')
        else:
            params.append('['+', '.join(params2)+']')
        if hasattr(dataType, 'desc'):
            lines.append('dataType=package.createRecordDataType(%s)'%(', '.join(params)))
            lines.append('dataType.desc = """%s"""'%dataType.desc)
        else:
            lines.append('package.createRecordDataType(%s)'%(', '.join(params)))
        return lines

    def writeStringTypeCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        #name
        params=[repr(dataType.name)]
        #length
        params.append(str(dataType.length))
        #encoding
        if dataType.encoding != 'ISO-8859-1':
            params.append('encoding='+repr(dataType.encoding))
        if hasattr(dataType, 'desc'):
            lines.append('dataType=package.createStringDataType(%s)'%(', '.join(params)))
            lines.append('dataType.desc = """%s"""'%dataType.desc) #the r will force a raw string to be created
        else:
            lines.append('package.createStringDataType(%s)'%(', '.join(params)))
        return lines

    def writeCompuMethodCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        return lines

    def CompuMethodRational(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        return lines

    def writeDataTypeUnitElementCode(self, dataType, localvars):
        lines=[]
        ws=localvars['ws']
        return lines

    def writeImplementationDataTypeCode(self, dataType, localvars):
        lines = []
        return lines

    def writeDataConstraintCode(self, dataType, localvars):
        lines = []
        return lines
