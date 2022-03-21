import abc
from collections import deque
from autosar.base import (AdminData, SpecialDataGroup, SpecialData, SwDataDefPropsConditional, SwPointerTargetProps, SymbolProps)
import autosar.element

def _parseBoolean(value):
    if value is None:
        return None
    if isinstance(value,str):
        if value == 'true': return True
        elif value =='false': return False
    raise ValueError(value)

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
        else:
            raise NotImplementedError(xmlElem.tag)
    
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
                        raise NotImplementedError(xmlChild.tag)
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
                        raise NotImplementedError(subItemXML.tag)
            else:
                raise NotImplementedError(itemXML.tag)
        return variants if len(variants)>0 else None

    def parseSwDataDefPropsConditional(self, xmlRoot):
        assert (xmlRoot.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL')
        (baseTypeRef, implementationTypeRef, swCalibrationAccess, compuMethodRef, dataConstraintRef,
         swPointerTargetPropsXML, swImplPolicy, swAddressMethodRef, unitRef) = (None, None, None, None, None, None, None, None, None)
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
            elif xmlItem.tag == 'ADDITIONAL-NATIVE-TYPE-QUALIFIER':
                pass #implement later
            elif xmlItem.tag == 'SW-CALPRM-AXIS-SET':
                print("[BaseParser] unhandled: %s"%xmlItem.tag)
                pass #implement later
                print("[BaseParser] unhandled: %s"%xmlItem.tag)
            elif xmlItem.tag == 'SW-RECORD-LAYOUT-REF':
                print("[BaseParser] unhandled: %s"%xmlItem.tag)
                pass #implement later
            elif xmlItem.tag == 'INVALID-VALUE':
                print("[BaseParser] unhandled: %s"%xmlItem.tag)
                pass #implement later
            else:
                raise NotImplementedError(xmlItem.tag)
        variant = SwDataDefPropsConditional(baseTypeRef, implementationTypeRef, swAddressMethodRef, swCalibrationAccess, swImplPolicy, None, compuMethodRef, dataConstraintRef, unitRef)
        if swPointerTargetPropsXML is not None:
            variant.swPointerTargetProps = self.parseSwPointerTargetProps(swPointerTargetPropsXML, variant)
        return variant

    def parseSwPointerTargetProps(self, rootXML, parent = None):
        assert (rootXML.tag == 'SW-POINTER-TARGET-PROPS')
        props = SwPointerTargetProps()
        for itemXML in rootXML.findall('./*'):
            if itemXML.tag == 'TARGET-CATEGORY':
                props.targetCategory = self.parseTextNode(itemXML)
            if itemXML.tag == 'SW-DATA-DEF-PROPS':
                props.variants = self.parseSwDataDefProps(itemXML)
        return props

    def parseVariableDataPrototype(self, xmlRoot, parent = None):
        assert(xmlRoot.tag == 'VARIABLE-DATA-PROTOTYPE')
        (typeRef, props_variants, isQueued) = (None, None, False)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'TYPE-TREF':
                typeRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SW-DATA-DEF-PROPS':
                props_variants = self.parseSwDataDefProps(xmlElem)
            elif xmlElem.tag == 'INIT-VALUE':
                pass #Implement later
            else:
                self.defaultHandler(xmlElem)
        if (self.name is not None) and (typeRef is not None):
            dataElement = autosar.element.DataElement(self.name, typeRef, isQueued, category=self.category, parent = parent, adminData = self.adminData)
            if (props_variants is not None) and len(props_variants) > 0:
                dataElement.setProps(props_variants[0])
            self.pop(dataElement)
            return dataElement
        else:
            self.pop()
            raise RuntimeError('SHORT-NAME and TYPE-TREF must not be None')
        
    
    def parseSymbolProps(self, xmlRoot):
        assert(xmlRoot.tag == 'SYMBOL-PROPS')
        name, symbol = None, None
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'SHORT-NAME':
                name = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'SYMBOL':
                symbol = self.parseTextNode(xmlElem)
            else:
                raise NotImplementedError(xmlElem.tag)
        return SymbolProps(name, symbol)
            
class ElementParser(BaseParser, metaclass=abc.ABCMeta):

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
