from autosar.element import Element
import autosar.constant
from autosar.base import hasAdminData,parseAdminDataNode
from autosar.parser.parser_base import ElementParser

class ConstantParser(ElementParser):
    """
    Constant package parser
    """
    def __init__(self,version=3.0):
        super().__init__(version)

    def getSupportedTags(self):
        return ['CONSTANT-SPECIFICATION']

    def parseElement(self, xmlElement, parent = None):
        if xmlElement.tag == 'CONSTANT-SPECIFICATION':
            return self.parseConstantSpecification(xmlElement, parent)
        else:
            return None

    def parseConstantSpecification(self, xmlElem, rootProject=None, parent=None):
        assert(xmlElem.tag == 'CONSTANT-SPECIFICATION')
        (xmlValue, xmlValueSpec) = (None, None)
        self.push()
        for xmlElem in xmlElem.findall('./*'):
            if self.version < 4.0 and xmlElem.tag == 'VALUE':
                xmlValue = xmlElem
            elif self.version >= 4.0 and xmlElem.tag == 'VALUE-SPEC':
                xmlValueSpec = xmlElem
            elif xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            else:
                self.defaultHandler(xmlElem)

        if (self.name is not None) and ((xmlValue is not None) or (xmlValueSpec is not None)):
            constant = autosar.constant.Constant(self.name, parent=parent, adminData=self.adminData)
            if xmlValue is not None:
                constant.value = self._parseValueV3(xmlValue.find('./*') , constant)
            elif xmlValueSpec is not None:
                values = self.parseValueV4(xmlValueSpec, constant)
                if len(values) != 1:
                    raise ValueError('A value specification must contain exactly one element')
                constant.value = values[0]
            retval = constant
        else:
            retval = None
        self.pop(retval)
        return retval

    def _parseValueV3(self, xmlValue, parent):
        constantValue = None
        xmlName = xmlValue.find('SHORT-NAME')
        if xmlName is not None:
            name=xmlName.text
            if xmlValue.tag == 'INTEGER-LITERAL':
                typeRef = xmlValue.find('./TYPE-TREF').text
                innerValue = xmlValue.find('./VALUE').text
                constantValue = autosar.constant.IntegerValue(name, typeRef, innerValue, parent)
            elif xmlValue.tag=='STRING-LITERAL':
                typeRef = xmlValue.find('./TYPE-TREF').text
                innerValue = xmlValue.find('./VALUE').text
                constantValue = autosar.constant.StringValue(name, typeRef, innerValue, parent)
            elif xmlValue.tag=='BOOLEAN-LITERAL':
                typeRef = xmlValue.find('./TYPE-TREF').text
                innerValue = xmlValue.find('./VALUE').text
                constantValue = autosar.constant.BooleanValue(name, typeRef, innerValue, parent)
            elif xmlValue.tag == 'RECORD-SPECIFICATION' or xmlValue.tag == 'ARRAY-SPECIFICATION':
                typeRef = xmlValue.find('./TYPE-TREF').text
                if xmlValue.tag == 'RECORD-SPECIFICATION':
                    constantValue=autosar.constant.RecordValue(name, typeRef, parent=parent)
                else:
                    constantValue=autosar.constant.ArrayValue(name, typeRef, parent=parent)
                for innerElem in xmlValue.findall('./ELEMENTS/*'):
                    innerConstant = self._parseValueV3(innerElem, constantValue)
                    if innerConstant is not None:
                        constantValue.elements.append(innerConstant)
        return constantValue

    def parseValueV4(self, xmlValue, parent):
        result = []
        for xmlElem in xmlValue.findall('./*'):
            if xmlElem.tag == 'TEXT-VALUE-SPECIFICATION':
                result.append(self._parseTextValueSpecification(xmlElem, parent))
            elif xmlElem.tag == 'RECORD-VALUE-SPECIFICATION':
                result.append(self._parseRecordValueSpecification(xmlElem, parent))
            elif xmlElem.tag == 'NUMERICAL-VALUE-SPECIFICATION':
                result.append(self._parseNumericalValueSpecification(xmlElem, parent))
            elif xmlElem.tag == 'ARRAY-VALUE-SPECIFICATION':
                result.append(self._parseArrayValueSpecification(xmlElem, parent))
            elif xmlElem.tag == 'CONSTANT-REFERENCE':
                result.append(self._parseConstantReference(xmlElem, parent))
            elif xmlElem.tag == 'APPLICATION-VALUE-SPECIFICATION':
                result.append(self._parseApplicationValueSpecification(xmlElem, parent))
            else:
                raise NotImplementedError(xmlElem.tag)
        return result

    def _parseTextValueSpecification(self, xmlValue, parent):
        (label, value) = (None, None)
        for xmlElem in xmlValue.findall('./*'):
            if xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'VALUE':
                value = self.parseTextNode(xmlElem)
            else:
                raise NotImplementedError(xmlElem.tag)

        if value is not None:
            return autosar.constant.TextValue(label, value, parent)
        else:
            raise RuntimeError("Value must not be None")

    def _parseNumericalValueSpecification(self, xmlValue, parent):
        (label, value) = (None, None)
        for xmlElem in xmlValue.findall('./*'):
            if xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'VALUE':
                value = self.parseTextNode(xmlElem)
            else:
                raise NotImplementedError(xmlElem.tag)

        if value is not None:
            return autosar.constant.NumericalValue(label, value, parent)
        else:
            raise RuntimeError("value must not be None")

    def _parseRecordValueSpecification(self, xmlValue, parent):
        (label, xmlFields) = (None, None)
        for xmlElem in xmlValue.findall('./*'):
            if xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'FIELDS':
                xmlFields = xmlElem
            else:
                raise NotImplementedError(xmlElem.tag)

        if (xmlFields is not None):
            record = autosar.constant.RecordValue(label, parent=parent)
            record.elements = self.parseValueV4(xmlFields, record)
            return record
        else:
            raise RuntimeError("<FIELDS> must not be None")

    def _parseArrayValueSpecification(self, xmlValue, parent):
        (label, xmlElements) = (None, None)
        for xmlElem in xmlValue.findall('./*'):
            if xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'ELEMENTS':
                xmlElements = xmlElem
            else:
                raise NotImplementedError(xmlElem.tag)

        if (xmlElements is not None):
            array = autosar.constant.ArrayValueAR4(label, parent=parent)
            array.elements = self.parseValueV4(xmlElements, array)
            return array

        else:
            raise RuntimeError("<ELEMENTS> must not be None")

    def _parseConstantReference(self, xmlRoot, parent):
        label, constantRef = None, None
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'CONSTANT-REF':
                constantRef = self.parseTextNode(xmlElem)
            else:
                self.baseHandler(xmlElem)
        if constantRef is not None:
            obj = autosar.constant.ConstantReference(label, constantRef, parent, self.adminData)
            self.pop(obj)
            return obj
        else:
            raise RuntimeError('<CONSTANT-REF> must not be None')

    def _parseApplicationValueSpecification(self, xmlRoot, parent):
        label, swValueCont, swAxisCont, category = None, None, None, None

        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-LABEL':
                label = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'CATEGORY':
                category = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-VALUE-CONT':
                swValueCont = self._parseSwValueCont(xmlElem)
            elif xmlElem.tag == 'SW-AXIS-CONTS':
                xmlChild = xmlElem.find('./SW-AXIS-CONT')
                if xmlChild is not None:
                    swAxisCont = self._parseSwAxisCont(xmlChild)
            else:
                raise NotImplementedError(xmlElem.tag)
        value = autosar.constant.ApplicationValue(label, swValueCont = swValueCont, swAxisCont = swAxisCont, category = category, parent = parent)
        return value

    def _parseSwValueCont(self, xmlRoot):
        unitRef = None
        valueList = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'UNIT-REF':
                unitRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-VALUES-PHYS':
                for xmlChild in xmlElem.findall('./*'):
                    if (xmlChild.tag == 'V') or (xmlChild.tag == 'VF'):
                        valueList.append(self.parseNumberNode(xmlChild))
                    elif xmlChild.tag == 'VT':
                        valueList.append(self.parseTextNode(xmlChild))
                    else:
                        raise NotImplementedError(xmlChild.tag)
            else:
                raise NotImplementedError(xmlElem.tag)
        if len(valueList)==0:
            valueList = None
        return autosar.constant.SwValueCont(valueList, unitRef)

    def _parseSwAxisCont(self, xmlRoot):
        unitRef = None
        valueList = []
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'UNIT-REF':
                unitRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-VALUES-PHYS':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'V':
                        valueList.append(self.parseNumberNode(xmlChild))
                    else:
                        raise NotImplementedError(xmlChild.tag)
            else:
                raise NotImplementedError(xmlElem.tag)
        if len(valueList)==0:
            valueList = None
        return autosar.constant.SwAxisCont(valueList, unitRef)