import sys
from autosar.parser.parser_base import ElementParser
import autosar.datatype

class DataTypeParser(ElementParser):
    def __init__(self,version=3.0):
        super().__init__(version)

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = {'ARRAY-TYPE': self.parseArrayType,
                             'BOOLEAN-TYPE': self.parseBooleanType,
                             'INTEGER-TYPE': self.parseIntegerType,
                             'REAL-TYPE': self.parseRealType,
                             'RECORD-TYPE': self.parseRecordType,
                             'STRING-TYPE': self.parseStringType}
        elif self.version >= 4.0:
            self.switcher = {
               'DATA-CONSTR': self.parseDataConstraint,
               'IMPLEMENTATION-DATA-TYPE': self.parseImplementationDataType,
               'SW-BASE-TYPE': self.parseSwBaseType,
               'DATA-TYPE-MAPPING-SET': self.parseDataTypeMappingSet,
               'APPLICATION-PRIMITIVE-DATA-TYPE': self.parseApplicationPrimitiveDataType,
               'APPLICATION-ARRAY-DATA-TYPE' : self.parseApplicationArrayDataType,
               'APPLICATION-RECORD-DATA-TYPE': self.parseApplicationRecordDataTypeXML,
            }

    def getSupportedTags(self):
        return self.switcher.keys()

    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement,parent)
        else:
            return None


    def parseIntegerType(self,root,parent=None):
        if self.version>=3.0:
            name=root.find("./SHORT-NAME").text
            minval = int(root.find("./LOWER-LIMIT").text)
            maxval = int(root.find("./UPPER-LIMIT").text)
            dataDefXML = root.find('./SW-DATA-DEF-PROPS')
            dataType = autosar.datatype.IntegerDataType(name,minval,maxval)
            self.parseDesc(root,dataType)
            if dataDefXML is not None:
                for elem in dataDefXML.findall('./*'):
                    if elem.tag=='COMPU-METHOD-REF':
                        dataType.compuMethodRef=self.parseTextNode(elem)
                    else:
                        raise NotImplementedError(elem.tag)
            return dataType

    def parseRecordType(self,root,parent=None):
        if self.version>=3.0:
            elements = []
            name=root.find("./SHORT-NAME").text
            for elem in root.findall('./ELEMENTS/RECORD-ELEMENT'):
                elemName = self.parseTextNode(elem.find("./SHORT-NAME"))
                elemTypeRef = self.parseTextNode(elem.find("./TYPE-TREF"))
                elements.append(autosar.datatype.RecordTypeElement(elemName, elemTypeRef))
            dataType=autosar.datatype.RecordDataType(name,elements);
            self.parseDesc(root,dataType)
            return dataType

    def parseArrayType(self,root,parent=None):
        if self.version>=3.0:
            name=root.find("./SHORT-NAME").text
            length=int(root.find('ELEMENT/MAX-NUMBER-OF-ELEMENTS').text)
            typeRef=root.find('ELEMENT/TYPE-TREF').text
            dataType=autosar.datatype.ArrayDataType(name,typeRef,length)
            self.parseDesc(root,dataType)
            return dataType;

    def parseBooleanType(self,root,parent=None):
        if self.version>=3:
            name=root.find("./SHORT-NAME").text
            dataType=autosar.datatype.BooleanDataType(name)
            self.parseDesc(root,dataType)
            return dataType

    def parseStringType(self,root,parent=None):
        if self.version>=3.0:
            name=root.find("./SHORT-NAME").text

            length=int(root.find('MAX-NUMBER-OF-CHARS').text)
            encoding=root.find('ENCODING').text
            dataType=autosar.datatype.StringDataType(name,length,encoding)
            self.parseDesc(root,dataType)
            return dataType

    def parseRealType(self,root,parent=None):
        if self.version>=3.0:
            name=root.find("./SHORT-NAME").text

            elem = root.find("./LOWER-LIMIT")
            if elem is not None:
                minval = elem.text
                minvalType = elem.attrib['INTERVAL-TYPE']
            elem = root.find("./UPPER-LIMIT")
            if elem is not None:
                maxval = elem.text
                maxvalType = elem.attrib['INTERVAL-TYPE']
            hasNaNText = self.parseTextNode(root.find("./ALLOW-NAN"))
            hasNaN = True if (hasNaNText is not None and hasNaNText == 'true') else False
            encoding = self.parseTextNode(root.find("./ENCODING"))
            dataType=autosar.datatype.RealDataType(name,minval,maxval,minvalType,maxvalType,hasNaN,encoding)
            self.parseDesc(root,dataType)
            return dataType

    def parseDataConstraint(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'DATA-CONSTR')
        rules=[]
        constraintLevel = None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'DATA-CONSTR-RULES':
                for xmlChildElem in xmlElem.findall('./DATA-CONSTR-RULE/*'):
                    if xmlChildElem.tag == 'INTERNAL-CONSTRS':
                        rules.append(self._parseDataConstraintRule(xmlChildElem, 'internalConstraint'))
                    elif xmlChildElem.tag == 'PHYS-CONSTRS':
                        rules.append(self._parseDataConstraintRule(xmlChildElem, 'physicalConstraint'))
                    elif xmlChildElem.tag == 'CONSTR-LEVEL':
                        constraintLevel = self.parseIntNode(xmlChildElem)
                    else:
                        raise NotImplementedError(xmlChildElem.tag)
            else:
                self.defaultHandler(xmlElem)
        elem = autosar.datatype.DataConstraint(self.name, rules, constraintLevel, parent, self.adminData)
        self.pop(elem)
        return elem

    def _parseDataConstraintRule(self, xmlElem, constraintType):
        lowerLimitXML = xmlElem.find('./LOWER-LIMIT')
        upperLimitXML = xmlElem.find('./UPPER-LIMIT')
        lowerLimit = None if lowerLimitXML is None else self.parseNumberNode(lowerLimitXML)
        upperLimit = None if upperLimitXML is None else self.parseNumberNode(upperLimitXML)
        lowerLimitType = 'CLOSED'
        upperLimitType = 'CLOSED'
        key = 'INTERVAL-TYPE'
        if lowerLimitXML is not None and key in lowerLimitXML.attrib and lowerLimitXML.attrib[key]=='OPEN':
            lowerLimitType='OPEN'
        if upperLimitXML is not None and key in upperLimitXML.attrib and upperLimitXML.attrib[key]=='OPEN':
            upperLimitType='OPEN'
        return {
            'type': constraintType,
            'lowerLimit': lowerLimit,
            'upperLimit': upperLimit,
            'lowerLimitType': lowerLimitType,
            'upperLimitType': upperLimitType}


    def parseImplementationDataType(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'IMPLEMENTATION-DATA-TYPE')
        variantProps, typeEmitter, parseTextNode, dynamicArraySizeProfile, subElementsXML, symbolProps = None, None, None, None, None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SW-DATA-DEF-PROPS':
                variantProps = self.parseSwDataDefProps(xmlElem)
            elif xmlElem.tag == 'TYPE-EMITTER':
                typeEmitter = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DYNAMIC-ARRAY-SIZE-PROFILE':
                dynamicArraySizeProfile = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SUB-ELEMENTS':
                subElementsXML = xmlElem
            elif xmlElem.tag == 'SYMBOL-PROPS':
                symbolProps = self.parseSymbolProps(xmlElem)
            else:
                self.defaultHandler(xmlElem)

        dataType = autosar.datatype.ImplementationDataType(
            self.name,
            variantProps = variantProps,
            dynamicArraySizeProfile = dynamicArraySizeProfile,
            typeEmitter = typeEmitter,
            category = self.category,
            parent = parent,
            adminData = self.adminData
            )
        if subElementsXML is not None:
            dataType.subElements = self.parseImplementationDataTypeSubElements(subElementsXML, dataType)
        if symbolProps is not None:
            dataType.symbolProps = symbolProps
        self.pop(dataType)
        return dataType

    def parseImplementationDataTypeSubElements(self, xmlRoot, parent):
        assert (xmlRoot.tag == 'SUB-ELEMENTS')
        elements = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'IMPLEMENTATION-DATA-TYPE-ELEMENT':
                elements.append(self.parseImplementationDataTypeElement(xmlElem, parent))
            else:
                raise NotImplementedError(xmlElem.tag)
        return elements

    def parseImplementationDataTypeElement(self, xmlRoot, parent):
        assert (xmlRoot.tag == 'IMPLEMENTATION-DATA-TYPE-ELEMENT')
        (arraySize, arraySizeSemantics, variants) = (None, None, None)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SW-DATA-DEF-PROPS':
                variants = self.parseSwDataDefProps(xmlElem)
            elif xmlElem.tag == 'ARRAY-SIZE':
                arraySize = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ARRAY-SIZE-SEMANTICS':
                arraySizeSemantics = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SUB-ELEMENTS':
                pass #implement later
            else:
                self.defaultHandler(xmlElem)
        elem = autosar.datatype.ImplementationDataTypeElement(self.name, self.category, arraySize, arraySizeSemantics, variants, parent, self.adminData)
        self.pop(elem)
        return elem


    def parseSwBaseType(self, xmlRoot, parent = None):
        assert (xmlRoot.tag == 'SW-BASE-TYPE')
        baseTypeSize, baseTypeEncoding, nativeDeclaration = None, None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'BASE-TYPE-SIZE':
                baseTypeSize = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'BASE-TYPE-ENCODING':
                baseTypeEncoding = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'NATIVE-DECLARATION':
                nativeDeclaration = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'MEM-ALIGNMENT':
                pass #implement later
            elif xmlElem.tag == 'BYTE-ORDER':
                pass #implement later
            else:
                self.defaultHandler(xmlElem)
        elem = autosar.datatype.SwBaseType(self.name, baseTypeSize, baseTypeEncoding, nativeDeclaration, self.category, parent, self.adminData)
        self.pop(elem)
        return elem

    def parseDataTypeMappingSet(self, xmlRoot, parent = None):
        assert (xmlRoot.tag == 'DATA-TYPE-MAPPING-SET')
        (name, dataTypeMaps, adminData) = (None, None, None)
        dataTypeMaps = []
        modeRequestTypeMaps = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ADMIN-DATA':
                adminData=self.parseAdminDataNode(xmlElem)
            elif xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'DATA-TYPE-MAPS':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'DATA-TYPE-MAP':
                        dataTypeMap = self._parseDataTypeMapXML(xmlChild)
                        assert(dataTypeMap is not None)
                        dataTypeMaps.append(dataTypeMap)
                    else:
                        raise NotImplementedError(xmlElem.tag)
            elif xmlElem.tag == 'MODE-REQUEST-TYPE-MAPS':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'MODE-REQUEST-TYPE-MAP':
                        modeRequestTypeMap = self._parseModeRequestTypeMapXML(xmlChild)
                        assert(modeRequestTypeMap is not None)
                        modeRequestTypeMaps.append(modeRequestTypeMap)
                    else:
                        raise NotImplementedError(xmlElem.tag)
            else:
                raise NotImplementedError(xmlElem.tag)
        if (name is None):
            raise RuntimeError('SHORT-NAME cannot be None')
        elem = autosar.datatype.DataTypeMappingSet(name, parent, adminData)
        for mapping in dataTypeMaps + modeRequestTypeMaps:
            elem.add(mapping)
        return elem

    def parseApplicationPrimitiveDataType(self, xmlRoot, parent = None):
        assert (xmlRoot.tag == 'APPLICATION-PRIMITIVE-DATA-TYPE')
        variantProps = None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SW-DATA-DEF-PROPS':
                variantProps = self.parseSwDataDefProps(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        if (self.name is None):
            raise RuntimeError('SHORT-NAME cannot be None')
        elem = autosar.datatype.ApplicationPrimitiveDataType(self.name, variantProps, self.category, parent, self.adminData)
        self.pop(elem)
        return elem

    def parseApplicationArrayDataType(self, xmlRoot, parent = None):
        assert (xmlRoot.tag == 'APPLICATION-ARRAY-DATA-TYPE')
        element, variantProps = None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ELEMENT':
                element = self.parseApplicationArrayElement(xmlElem)
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                variantProps = self.parseSwDataDefProps(xmlElem)
            elif xmlElem.tag == 'DYNAMIC-ARRAY-SIZE-PROFILE':
                pass #implement later
            else:
                self.defaultHandler(xmlElem)
        if element is None:
            raise RuntimeError('No <ELEMENT> object found')
        elem = autosar.datatype.ApplicationArrayDataType(self.name, element, variantProps, self.category, parent, self.adminData)
        self.pop(elem)
        return elem

    def parseApplicationArrayElement(self, xmlRoot):
        assert (xmlRoot.tag == 'ELEMENT')
        (typeRef, arraySize, sizeHandling, sizeSemantics) = (None, None, None, None)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ARRAY-SIZE-HANDLING':
                sizeHandling = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ARRAY-SIZE-SEMANTICS':
                sizeSemantics = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'MAX-NUMBER-OF-ELEMENTS':
                arraySize = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        elem = autosar.datatype.ApplicationArrayElement(self.name, typeRef, arraySize, sizeHandling, sizeSemantics, self.category, adminData = self.adminData)
        self.pop(elem)
        return elem

    def parseApplicationRecordDataTypeXML(self, xmlRoot, parent = None):
        assert (xmlRoot.tag == 'APPLICATION-RECORD-DATA-TYPE')
        elementsXML, variantProps = None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ELEMENTS':
                elementsXML = xmlElem
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                variantProps = self.parseSwDataDefProps(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        elem = autosar.datatype.ApplicationRecordDataType(self.name, None, variantProps, self.category, parent, self.adminData)
        if elementsXML is not None:
            for xmlChild in elementsXML.findall('./'):
                if xmlChild.tag == 'APPLICATION-RECORD-ELEMENT':
                    elem.elements.append(self._parseApplicationRecordElementXML(xmlChild, parent = elem))
                else:
                    raise NotImplementedError(xmlChild.tag)
        self.pop(elem)
        return elem

    def _parseApplicationRecordElementXML(self, xmlRoot, parent):
        assert (xmlRoot.tag == 'APPLICATION-RECORD-ELEMENT')
        typeRef, variantProps = None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                variantProps = self.parseSwDataDefProps(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        elem = autosar.datatype.ApplicationRecordElement(self.name, typeRef, self.category, parent, self.adminData)
        self.pop(elem)
        return elem


    def _parseDataTypeMapXML(self, xmlRoot):
        assert (xmlRoot.tag == 'DATA-TYPE-MAP')
        (applicationDataTypeRef, implementationDataTypeRef) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'APPLICATION-DATA-TYPE-REF':
                applicationDataTypeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementationDataTypeRef = self.parseTextNode(xmlElem)
            else:
                raise NotImplementedError(xmlElem.tag)
        return autosar.datatype.DataTypeMap(applicationDataTypeRef, implementationDataTypeRef)

    def _parseModeRequestTypeMapXML(self, xmlRoot):
        assert (xmlRoot.tag == 'MODE-REQUEST-TYPE-MAP')
        (modeDeclarationGroupRef, implementationDataTypeRef) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'MODE-GROUP-REF':
                modeDeclarationGroupRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementationDataTypeRef = self.parseTextNode(xmlElem)
            else:
                raise NotImplementedError(xmlElem.tag)
        return autosar.datatype.ModeRequestTypeMap(modeDeclarationGroupRef, implementationDataTypeRef)

class DataTypeSemanticsParser(ElementParser):
    def __init__(self,version=3.0):
        super().__init__(version)

    def getSupportedTags(self):
        return ['COMPU-METHOD']

    def parseElement(self, xmlElement, parent = None):
        if xmlElement.tag == 'COMPU-METHOD':
            return self._parseCompuMethodXML(xmlElement, parent)
        else:
            return None

    def _parseCompuMethodXML(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'COMPU-METHOD')
        compuInternalToPhys, compuPhysToInternal, unitRef = None, None, None

        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'COMPU-INTERNAL-TO-PHYS':
                compuInternalToPhys = self._parseComputationXML(xmlElem)
                assert(compuInternalToPhys is not None)
            elif xmlElem.tag == 'COMPU-PHYS-TO-INTERNAL':
                compuPhysToInternal = self._parseComputationXML(xmlElem)
                assert(compuPhysToInternal is not None)
            elif xmlElem.tag == 'UNIT-REF':
                unitRef = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        compuMethod = autosar.datatype.CompuMethod(self.name, False, False, unitRef, self.category, parent, self.adminData)
        self.pop(compuMethod)
        if compuInternalToPhys is not None:
            compuMethod.intToPhys = compuInternalToPhys
        if compuPhysToInternal is not None:
            compuMethod.physToInt = compuPhysToInternal
        return compuMethod

    def _parseComputationXML(self, xmlRoot):
        assert (xmlRoot.tag == 'COMPU-INTERNAL-TO-PHYS') or (xmlRoot.tag == 'COMPU-PHYS-TO-INTERNAL')
        computation = autosar.datatype.Computation()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'COMPU-SCALES':
                for compuScaleXml in xmlElem.findall('COMPU-SCALE'):
                    compuScale = self._parseCompuScaleXML(compuScaleXml)
                    computation.elements.append(compuScale)
            elif xmlElem.tag == 'COMPU-DEFAULT-VALUE':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'V':
                        computation.defaultValue = self.parseNumberNode(xmlChild)
                        break
                    elif xmlChild.tag == 'VT':
                        computation.defaultValue = self.parseTextNode(xmlChild)
                        break
                    elif xmlChild.tag == 'VF':
                        computation.defaultValue = self.parseNumberNode(xmlChild)
                        break
                    else:
                        raise NotImplementedError(xmlChild.tag)
            else:
                raise NotImplementedError(xmlElem.tag)
        return computation

    def _parseCompuScaleXML(self, xmlRoot):
        assert(xmlRoot.tag == 'COMPU-SCALE')
        label, lowerLimit, upperLimit, lowerLimitType, upperLimitType, symbol, adminData = None, None, None, None, None, None, None
        offset, numerator, denominator, textValue, mask = None, None, None, None, None

        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'DESC':
                pass #implement later
            elif xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'LOWER-LIMIT':
                lowerLimit = self.parseNumberNode(xmlElem)
                if (self.version >= 4.0) and 'INTERVAL-TYPE' in xmlElem.attrib:
                    lowerLimitType = xmlElem.attrib['INTERVAL-TYPE']
            elif xmlElem.tag == 'UPPER-LIMIT':
                upperLimit = self.parseNumberNode(xmlElem)
                if (self.version >= 4.0) and 'INTERVAL-TYPE' in xmlElem.attrib:
                    upperLimitType = xmlElem.attrib['INTERVAL-TYPE']
            elif xmlElem.tag == 'COMPU-RATIONAL-COEFFS':
                offset, numerator, denominator = self._parseCompuRationalXML(xmlElem)
            elif xmlElem.tag == 'SYMBOL':
                symbol = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ADMIN-DATA':
                adminData = self.parseAdminDataNode(xmlElem)
            elif xmlElem.tag == 'COMPU-CONST':
                textValue = self.parseTextNode(xmlElem.find('./VT'))
            elif xmlElem.tag == 'MASK':
                mask = self.parseIntNode(xmlElem)
            else:
                raise NotImplementedError(xmlElem.tag)
        compuScale = autosar.datatype.CompuScaleElement(lowerLimit, upperLimit, lowerLimitType, upperLimitType, label, symbol, adminData)
        compuScale.offset = offset
        compuScale.numerator = numerator
        compuScale.denominator = denominator
        compuScale.textValue = textValue
        compuScale.mask = mask
        return compuScale

    def _parseCompuRationalXML(self, xmlRoot):
        assert(xmlRoot.tag == 'COMPU-RATIONAL-COEFFS')
        numXml = xmlRoot.findall('./COMPU-NUMERATOR/V')
        denXml = xmlRoot.findall('./COMPU-DENOMINATOR/V')
        assert(numXml is not None)
        assert(len(numXml) == 2)
        assert(denXml is not None)
        if self.parseTextNode(numXml[0]):
            offset = self.parseNumberNode(numXml[0])
        else:
            offset = 0
        if self.parseTextNode(numXml[1]):
            numerator = self.parseNumberNode(numXml[1])
        else:
            numerator = 1
        denominator = self.parseNumberNode(denXml[0])
        return offset, numerator, denominator

class DataTypeUnitsParser(ElementParser):
    def __init__(self,version=3.0):
        super().__init__(version)


    def getSupportedTags(self):
        return ['UNIT']

    def parseElement(self, xmlElement, parent = None):
        if xmlElement.tag == 'UNIT':
            return self._parseUnit(xmlElement, parent)
        else:
            return None

    def _parseUnit(self, xmlRoot, parent=None):
        assert (xmlRoot.tag == 'UNIT')
        name = self.parseTextNode(xmlRoot.find("./SHORT-NAME"))
        displayName = self.parseTextNode(xmlRoot.find("./DISPLAY-NAME"))
        if self.version>=4.0:
            factor = self.parseTextNode(xmlRoot.find("./FACTOR-SI-TO-UNIT"))
            offset = self.parseTextNode(xmlRoot.find("./OFFSET-SI-TO-UNIT"))
        else:
            (factor,offset) = (None, None)
        return autosar.datatype.Unit(name, displayName, factor, offset, parent)
