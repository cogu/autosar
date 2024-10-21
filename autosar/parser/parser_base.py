import abc
from collections import deque
from autosar.base import (AdminData, SpecialDataGroup, SpecialData,
                          SwDataDefPropsConditional, SwCalprmAxis,
                          SwAxisIndividual, SwAxisGrouped,
                          SwPointerTargetProps, SymbolProps)
import autosar.element
import xml
from functools import wraps

from autosar.util.errorHandler import handleNotImplementedError, handleValueError

def _parseBoolean(value):
    if value is None:
        return None
    if isinstance(value,str):
        if value == 'true': return True
        elif value =='false': return False
    handleValueError(value)

def parseElementUUID(parser_func):
    """
    Decorator that adds parsing of the UUID field for autosar.element.Element

    The decorator should be added to methods that parse an xml.etree.ElementTree.Element
    argument and returns a autosar.element.Element. In case the xml element contains
    the UUID attribute, this will be inserted into the Autosar Element.
    """
    @wraps(parser_func)
    def parseUUID(*args, **kwargs):

        # call original parser function
        result = parser_func(*args, **kwargs)

        # if the result is not an Autosar Element, simply return
        if not isinstance(result, autosar.element.Element):
            return result
    
        # search for an argument of type xml.etree.ElementTree.Element    
        xmlElementArgs = []
        for arg in args:
            if isinstance(arg, xml.etree.ElementTree.Element):
                xmlElementArgs.append(arg)
        for _, arg in kwargs.items():
            if isinstance(arg, xml.etree.ElementTree.Element):
                xmlElementArgs.append(arg)
        
        # if we cannot determine in a unique way which argument to use, just return
        if len(xmlElementArgs) != 1:
            return result
    
        # retrieve the UUID from the xml element and attach it to the Autosar Element
        xmlElementArg = xmlElementArgs[0]
        if 'UUID' in xmlElementArg.attrib:
            result.uuid = xmlElementArg.attrib['UUID'].lower()
        return result

    return parseUUID

class CommonTagsResult:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.adminData = None
        self.desc = None
        self.descAttr = None
        self.longName = None
        self.longNameAttr = None
        self.name = None
        self.category = None
        self.displayFormat = None


class BaseParser:
    def __init__(self,version=None):
        self.version = version
        self.common = deque()
    
    def push(self):
        self.common.append(CommonTagsResult())
    
    def pop(self, obj = None):
        if obj is not None:
            self.applyDesc(obj)
            self.applyLongName(obj)
        self.common.pop()

    
        

    def baseHandler(self, xmlElem):
        """
        Alias for defaultHandler
        """
        self.defaultHandler(xmlElem)
        
    def defaultHandler(self, xmlElem):
        """
        A default handler that parses common tags found under most XML elements
        """
        if xmlElem.tag == 'SHORT-NAME':
            self.common[-1].name = self.parseTextNode(xmlElem)
        elif xmlElem.tag == 'ADMIN-DATA':
            self.common[-1].adminData = self.parseAdminDataNode(xmlElem)
        elif xmlElem.tag == 'CATEGORY':
            self.common[-1].category = self.parseTextNode(xmlElem)
        elif xmlElem.tag == 'DESC':
            self.common[-1].desc, self.common[-1].desc_attr = self.parseDescDirect(xmlElem)
        elif xmlElem.tag == 'LONG-NAME':
            self.common[-1].longName, self.common[-1].longName_attr = self.parseLongNameDirect(xmlElem)
        elif xmlElem.tag == 'DISPLAY-FORMAT':
            self.common[-1].displayFormat = None
        elif xmlElem.tag == 'ANNOTATION':
            pass #implement later
        elif xmlElem.tag == 'INTRODUCTION':
            pass #implement later
        else:
            handleNotImplementedError(xmlElem.tag)
    
    def applyDesc(self, obj):
        if self.common[-1].desc is not None:            
            obj.desc=self.common[-1].desc
            obj.descAttr=self.common[-1].desc_attr

    def applyLongName(self, obj):
        if self.common[-1].longName is not None:            
            obj.longName=self.common[-1].longName
            obj.longNameAttr=self.common[-1].longName_attr
    
    @property
    def name(self):
        return self.common[-1].name

    @property
    def adminData(self):
        return self.common[-1].adminData

    @property
    def category(self):
        return self.common[-1].category

    @property
    def desc(self):
        return self.common[-1].desc, self.common[-1].descAttr

    def parseLongName(self, xmlRoot, elem):
        xmlDesc = xmlRoot.find('LONG-NAME')
        if xmlDesc is not None:
            L2Xml = xmlDesc.find('L-4')
            if L2Xml is not None:
                L2Text=self.parseTextNode(L2Xml)
                L2Attr=L2Xml.attrib['L']
                elem.desc=L2Text
                elem.descAttr=L2Attr

    def parseLongNameDirect(self, xmlLongName):
        assert(xmlLongName.tag == 'LONG-NAME')
        L2Xml = xmlLongName.find('L-4')
        if L2Xml is not None:
            L2Text=self.parseTextNode(L2Xml)
            L2Attr=L2Xml.attrib['L']
            return (L2Text, L2Attr)
        return (None, None)

    def parseDesc(self, xmlRoot, elem):
        xmlDesc = xmlRoot.find('DESC')
        if xmlDesc is not None:
            L2Xml = xmlDesc.find('L-2')
            if L2Xml is not None:
                L2Text=self.parseTextNode(L2Xml)
                L2Attr=L2Xml.attrib['L']
                elem.desc=L2Text
                elem.descAttr=L2Attr

    def parseDescDirect(self, xmlDesc):
        assert(xmlDesc.tag == 'DESC')
        L2Xml = xmlDesc.find('L-2')
        if L2Xml is not None:
            L2Text=self.parseTextNode(L2Xml)
            L2Attr=L2Xml.attrib['L']
            return (L2Text, L2Attr)
        return (None, None)

    def parseTextNode(self, xmlElem):
        return None if xmlElem is None else xmlElem.text

    def parseIntNode(self, xmlElem):
        return None if xmlElem is None else int(xmlElem.text)

    def parseFloatNode(self, xmlElem):
        return None if xmlElem is None else float(xmlElem.text)

    def parseBooleanNode(self, xmlElem):
        return None if xmlElem is None else _parseBoolean(xmlElem.text)

    def parseNumberNode(self, xmlElem):
        textValue = self.parseTextNode(xmlElem)
        
        if textValue is None:
            return None
        
        retval = None
        try:
            retval = int(textValue)
        except ValueError:
            try:
                retval = float(textValue)
            except ValueError:
                retval = textValue
        return retval

    def hasAdminData(self, xmlRoot):
        return True if xmlRoot.find('ADMIN-DATA') is not None else False

    def parseAdminDataNode(self, xmlRoot):
        if xmlRoot is None: return None
        assert(xmlRoot.tag=='ADMIN-DATA')
        adminData=AdminData()
        xmlSDGS = xmlRoot.find('./SDGS')
        if xmlSDGS is not None:
            for xmlElem in xmlSDGS.findall('./SDG'):
                SDG_GID=xmlElem.attrib['GID']
                specialDataGroup = SpecialDataGroup(SDG_GID)
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'SD':
                        SD_GID = None
                        TEXT=xmlChild.text
                        try:
                            SD_GID=xmlChild.attrib['GID']
                        except KeyError: pass
                        specialDataGroup.SD.append(SpecialData(TEXT, SD_GID))
                    else:
                        handleNotImplementedError(xmlChild.tag)
                adminData.specialDataGroups.append(specialDataGroup)
        return adminData

    def parseSwDataDefProps(self, xmlRoot):
        assert (xmlRoot.tag == 'SW-DATA-DEF-PROPS')
        variants = []
        for itemXML in xmlRoot.findall('./*'):
            if itemXML.tag == 'SW-DATA-DEF-PROPS-VARIANTS':
                for subItemXML in itemXML.findall('./*'):
                    if subItemXML.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL':
                        variant = self.parseSwDataDefPropsConditional(subItemXML)
                        assert(variant is not None)
                        variants.append(variant)
                    else:
                        handleNotImplementedError(subItemXML.tag)
            else:
                handleNotImplementedError(itemXML.tag)
        return variants if len(variants)>0 else None

    def parseSwDataDefPropsConditional(self, xmlRoot):
        assert (xmlRoot.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL')
        (baseTypeRef, implementationTypeRef, swCalibrationAccess,
         compuMethodRef, dataConstraintRef, swPointerTargetPropsXML,
         swImplPolicy, swAddressMethodRef, unitRef, valueAxisDataTypeRef,
         swRecordLayoutRef, swCalprmAxisSet, swValueBlockSize) = (None,) * 13
        
        swValueBlockSizeMults = []
        for xmlItem in xmlRoot.findall('./*'):
            if xmlItem.tag == 'BASE-TYPE-REF':
                baseTypeRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'SW-CALIBRATION-ACCESS':
                swCalibrationAccess = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'COMPU-METHOD-REF':
                compuMethodRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'DATA-CONSTR-REF':
                dataConstraintRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'SW-POINTER-TARGET-PROPS':
                swPointerTargetPropsXML = xmlItem
            elif xmlItem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementationTypeRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'SW-IMPL-POLICY':
                swImplPolicy = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'SW-ADDR-METHOD-REF':
                swAddressMethodRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'UNIT-REF':
                unitRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'VALUE-AXIS-DATA-TYPE-REF':
                valueAxisDataTypeRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'SW-RECORD-LAYOUT-REF':
                swRecordLayoutRef = self.parseTextNode(xmlItem)
            elif xmlItem.tag == 'SW-CALPRM-AXIS-SET':
                swCalprmAxisSet = self.parseSwCalprmAxisSet(xmlItem)
            elif xmlItem.tag == 'SW-VALUE-BLOCK-SIZE':
                swValueBlockSize = int(self.parseTextNode(xmlItem))
            elif xmlItem.tag == 'SW-VALUE-BLOCK-SIZE-MULTS':
                for sizeItem in xmlItem.findall('./*'):
                    swValueBlockSizeMults.append(int(self.parseTextNode(sizeItem)))
            elif xmlItem.tag == 'ADDITIONAL-NATIVE-TYPE-QUALIFIER':
                pass #implement later
            elif xmlItem.tag == 'INVALID-VALUE':
                print("[BaseParser] unhandled: %s"%xmlItem.tag)
                pass #implement later
            elif xmlItem.tag == 'DISPLAY-FORMAT':
                print("[BaseParser] unhandled: %s"%xmlItem.tag)
                pass #implement later
            else:
                handleNotImplementedError(xmlItem.tag)

        variant = SwDataDefPropsConditional(
            baseTypeRef=baseTypeRef,
            implementationTypeRef=implementationTypeRef,
            swAddressMethodRef=swAddressMethodRef,
            swCalibrationAccess=swCalibrationAccess,
            swImplPolicy=swImplPolicy,
            swPointerTargetProps=None,
            compuMethodRef=compuMethodRef,
            dataConstraintRef=dataConstraintRef,
            unitRef=unitRef,
            valueAxisDataTypeRef=valueAxisDataTypeRef,
            swRecordLayoutRef=swRecordLayoutRef,
            swCalprmAxisSet=swCalprmAxisSet,
            swValueBlockSize=swValueBlockSize,
            swValueBlockSizeMults=swValueBlockSizeMults
        )
        if swPointerTargetPropsXML is not None:
            variant.swPointerTargetProps = self.parseSwPointerTargetProps(swPointerTargetPropsXML, variant)
        return variant

    def parseSwCalprmAxisSet(self, rootXML, parent = None):
        swCalprmAxisSet = []

        for itemXML in rootXML.findall('./*'):
            if itemXML.tag == 'SW-CALPRM-AXIS':
                swCalprmAxisSet.append(self.parseSwCalprmAxis(itemXML))
            else:
                raise RuntimeError("SW-CALPRM-AXIS-SET tag cannot have children other than SW-CALPRM-AXIS")

        return swCalprmAxisSet
    
    def parseSwCalprmAxis(self, rootXML, parent = None):
        (swAxisIndex, category, swAxisIndividual, swAxisGrouped,
         swCalibrationAccess, displayFormat, baseTypeRef) = (None,) * 7
        
        for itemXML in rootXML.findall("./*"):
            tag = itemXML.tag

            if tag == "SW-AXIS-INDEX":
                swAxisIndex = self.parseTextNode(itemXML)
            elif tag == "CATEGORY":
                category = self.parseTextNode(itemXML)
            elif tag == "SW-AXIS-INDIVIDUAL":
                swAxisIndividual = self.parseSwAxisIndividual(itemXML)
            elif tag == "SW-AXIS-GROUPED":
                swAxisGrouped = self.parseSwAxisGrouped(itemXML)
            elif tag == "SW-CALIBRATION-ACCESS":
                swCalibrationAccess = self.parseTextNode(itemXML)
            elif tag == "DISPLAY-FORMAT":
                displayFormat = self.parseTextNode(itemXML)
            elif tag == "BASE-TYPE-REF":
                baseTypeRef = self.parseTextNode(itemXML)
            else:
                raise RuntimeError(f"ERROR: Tag {tag} not recognized")

        return SwCalprmAxis(
            swAxisIndex=swAxisIndex,
            category=category,
            swAxisIndividual=swAxisIndividual,
            swAxisGrouped=swAxisGrouped,
            swCalibrationAccess=swCalibrationAccess,
            displayFormat=displayFormat,
            baseTypeRef=baseTypeRef
        )
    
    def parseSwAxisIndividual(self, rootXML, parent = None):
        (inputVariableTypeRef, swVariableRefs, compuMethodRef,
         unitRef, swMaxAxisPoints, swMinAxisPoints, dataConstrRef, swAxisGeneric) = (None,) * 8

        for itemXML in rootXML.findall("./*"):
            tag = itemXML.tag

            if tag == "INPUT-VARIABLE-TYPE-REF":
                inputVariableTypeRef = self.parseTextNode(itemXML)
            elif tag == "SW-VARIABLE-REFS":
                swVariableRefs = self.parseTextNode(itemXML)
            elif tag == "COMPU-METHOD-REF":
                compuMethodRef = self.parseTextNode(itemXML)
            elif tag == "UNIT-REF":
                unitRef = self.parseTextNode(itemXML)
            elif tag == "SW-MAX-AXIS-POINTS":
                swMaxAxisPoints = self.parseTextNode(itemXML)
            elif tag == "SW-MIN-AXIS-POINTS":
                swMinAxisPoints = self.parseTextNode(itemXML)
            elif tag == "DATA-CONSTR-REF":
                dataConstrRef = self.parseTextNode(itemXML)
            elif tag == "SW-AXIS-GENERIC":
                swAxisGeneric = self.parseTextNode(itemXML)
            else:
                raise RuntimeError(f"ERROR: Tag {tag} not recognized")

        return SwAxisIndividual(
            inputVariableTypeRef=inputVariableTypeRef,
            swVariableRefs=swVariableRefs,
            compuMethodRef=compuMethodRef,
            unitRef=unitRef,
            swMaxAxisPoints=swMaxAxisPoints,
            swMinAxisPoints=swMinAxisPoints,
            dataConstrRef=dataConstrRef,
            swAxisGeneric=swAxisGeneric
        )
    
    def parseSwAxisGrouped(self, rootXML, parent = None):
        (sharedAxisTypeRef, swAxisIndex, accessedParameter) = (None, None, None)

        for itemXML in rootXML.findall("./*"):
            tag = itemXML.tag

            if tag == "SHARED-AXIS-TYPE-REF":
                sharedAxisTypeRef = self.parseTextNode(itemXML)
            elif tag == "SW-AXIS-INDEX":
                swAxisIndex = self.parseTextNode(itemXML)
            elif tag == "AR-PARAMETER":
                # TODO: from specification, the <AR-PARAMETER> tag should also be supported
                #       for the <SW-DATA-DEPENDENCY-ARGS> element which is defined as a descendent
                #       of <SW-DATA-DEF-PROPS>
                for xmlChild in itemXML.findall('./*'):
                    if xmlChild.tag == 'AUTOSAR-PARAMETER-IREF':
                        accessedParameter = self.parseParameterInstanceRef(xmlChild)
                    elif xmlChild.tag == 'LOCAL-PARAMETER-REF':
                        accessedParameter = autosar.behavior.LocalParameterRef(self.parseTextNode(xmlChild))
                    else:
                        handleNotImplementedError(xmlChild.tag)
            else:
                raise RuntimeError(f"ERROR: Tag {tag} not recognized")

        return SwAxisGrouped(
            sharedAxisTypeRef=sharedAxisTypeRef,
            swAxisIndex=swAxisIndex,
            accessedParameter=accessedParameter
        )

    def parseSwPointerTargetProps(self, rootXML, parent = None):
        assert (rootXML.tag == 'SW-POINTER-TARGET-PROPS')
        props = SwPointerTargetProps()
        for itemXML in rootXML.findall('./*'):
            if itemXML.tag == 'TARGET-CATEGORY':
                props.targetCategory = self.parseTextNode(itemXML)
            if itemXML.tag == 'SW-DATA-DEF-PROPS':
                props.variants = self.parseSwDataDefProps(itemXML)
        return props
    
    def parseSymbolProps(self, xmlRoot):
        assert(xmlRoot.tag == 'SYMBOL-PROPS')
        name, symbol = None, None
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SYMBOL':
                symbol = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return SymbolProps(name, symbol)
            
class ElementParser(BaseParser, metaclass=abc.ABCMeta):
    """Parser for ARXML elements"""

    def __init__(self, version=None):
        super().__init__(version)

    @abc.abstractmethod
    def getSupportedTags(self):
        """
        Returns a list of tag-names (strings) that this parser supports.
        A generator returning strings is also OK.
        """
    @abc.abstractmethod
    def parseElement(self, xmlElement, parent = None):
        """
        Invokes the parser

        xmlElem: Element to parse (instance of xml.etree.ElementTree.Element)
        parent: the parent object (usually a package object)
        Should return an object derived from autosar.element.Element
        """

class EntityParser(ElementParser, metaclass=abc.ABCMeta):
    """Parser for AUTOSAR entities"""

    def __init__(self, version=None):
        super().__init__(version)
        from autosar.parser.constant_parser import ConstantParser # avoid circular import
        self.constantParser = ConstantParser(version)

    @parseElementUUID
    def parseAutosarDataPrototype(self, xmlRoot, parent = None):
        assert(xmlRoot.tag in ['VARIABLE-DATA-PROTOTYPE', 'PARAMETER-DATA-PROTOTYPE', 'ARGUMENT-DATA-PROTOTYPE'])
        dataPrototypeRole = autosar.element.AutosarDataPrototype.TAG_TO_ROLE_MAP.get(xmlRoot.tag)
        if dataPrototypeRole is None:
            handleNotImplementedError(xmlRoot.tag)
        (typeRef, props_variants, isQueued, initValue, initValueRef) = (None, None, False, None, None)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                props_variants = self.parseSwDataDefProps(xmlElem)
            elif xmlElem.tag == 'INIT-VALUE':
                initValue, initValueRef = self._parseAr4InitValue(xmlElem)
            else:
                self.defaultHandler(xmlElem)
        if (self.name is not None) and (typeRef is not None):
            specializedAutosarDataPrototype = autosar.element.AutosarDataPrototype(
                dataPrototypeRole,
                self.name,
                typeRef,
                isQueued,
                initValue = initValue,
                initValueRef = initValueRef,
                category = self.category,
                parent = parent,
                adminData = self.adminData
            )
            if (props_variants is not None) and len(props_variants) > 0:
                specializedAutosarDataPrototype.setProps(props_variants[0])
            self.pop(specializedAutosarDataPrototype)
            return specializedAutosarDataPrototype
        else:
            self.pop()
            if self.name is None:
                raise RuntimeError(f'Error in TAG {xmlRoot.tag}: SHORT-NAME and TYPE-TREF must not be None')
            else:
                raise RuntimeError(f'Error in TAG {xmlRoot.tag}: TYPE-TREF not defined for element with SHORT-NAME "{self.name}"')

    def _parseAr4InitValue(self, xmlElem):
        (initValue, initValueRef) = (None, None)
        for xmlChild in xmlElem.findall('./*'):
            if xmlChild.tag == 'CONSTANT-REFERENCE':
                initValueRef = self.parseTextNode(xmlChild.find('./CONSTANT-REF'))
            else:
                values = self.constantParser.parseValueV4(xmlElem, None)
                if len(values) != 1:
                    handleValueError('{0} cannot cannot contain multiple elements'.format(xmlElem.tag))
                else:
                    initValue = values[0]
        return (initValue, initValueRef)
