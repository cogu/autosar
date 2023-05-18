from autosar.element import Element
import autosar.base
import math
import json
import copy
import collections

class RecordTypeElement(Element):
    """
    (AUTOSAR3)
    Implemenetation of <RECORD-ELEMENT> (found inside <RECORD-TYPE>).

    """
    def tag(self, version=None): return 'RECORD-ELEMENT'

    def __init__(self, name, typeRef, parent = None, adminData = None):
        super().__init__(name, parent, adminData)
        self.typeRef=typeRef

    def __eq__(self,other):
        if self is other: return True
        if type(self) == type(other):
            if self.name == other.name:
                lhs = None if self.typeRef is None else self.rootWS().find(self.typeRef)
                rhs = None if other.typeRef is None else other.rootWS().find(other.typeRef)
                if lhs != rhs:
                    print(self.name,self.typeRef)
                return lhs==rhs
        return False

class CompuScaleElement:
    """
    Implementation of <COMPU-SCALE>
    """
    def tag(self, version=None): return 'COMPU-SCALE'

    def __init__(self, lowerLimit, upperLimit, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', label=None, symbol=None, textValue = None, numerator = None, denominator = None, offset = None, mask = None, adminData=None):
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.lowerLimitType = lowerLimitType
        self.upperLimitType = upperLimitType
        self.symbol = symbol
        self.label = label
        self.adminData = adminData
        self.textValue = textValue
        self.offset = offset
        self.numerator = numerator
        self.denominator = denominator
        self.mask = mask

class Unit(Element):
    """
    Implementation of <UNIT>
    """

    def tag(self, version=None): return 'UNIT'

    def __init__(self, name, displayName, factor=None, offset=None, parent=None):
        super().__init__(name, parent)
        self.displayName=displayName
        self.factor = factor       #only supported in AUTOSAR 4 and above
        self.offset = offset       #only supported in AUTOSAR 4 and above
    def __eq__(self,other):
        if self is other: return True
        if type(self) is type(other):
            if (self.name==other.name) and (self.displayName == other.displayName) and (
               self.factor == other.factor) and (self.offset == other.offset):
                return True
        return False

class DataType(Element):
    """
    Base type for DataType (AUTOSAR3)
    """
    def __init__(self, name, parent=None, adminData=None):
        super().__init__(name, parent, adminData)

    @property
    def isComplexType(self):
        return True if isinstance(self, (RecordDataType, ArrayDataType)) else False


class IntegerDataType(DataType):
    """
    IntegerDataType (AUTOSAR3)
    """
    def tag(self,version=None): return 'INTEGER-TYPE'
    def __init__(self, name, minVal=0, maxVal=0, compuMethodRef=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.minVal = int(minVal)
        self.maxVal = int(maxVal)
        self._minValType = 'CLOSED'
        self._maxValType = 'CLOSED'

        if isinstance(compuMethodRef,str):
            self.compuMethodRef=compuMethodRef
        elif hasattr(compuMethodRef,'ref'):
            self.compuMethodRef=compuMethodRef.ref
        else:
            self.compuMethodRef=None
    @property
    def minValType(self):
        return self._minValType
    @minValType.setter
    def minValueType(self, value):
        if (value != "CLOSED") and (value != "OPEN"):
            raise ValueError('value must be either "CLOSED" or "OPEN"')
        self._minValType=value

    @property
    def maxValType(self):
        return self._maxValType
    @maxValType.setter
    def maxValueType(self, value):
        if (value != "CLOSED") and (value != "OPEN"):
            raise ValueError('value must be either "CLOSED" or "OPEN"')
        self._minValType=value


    def __eq__(self,other):
        if self is other: return True
        if type(other) is type(self):
            if (self.name==other.name) and (self.minVal == other.minVal) and (self.maxVal==other.maxVal):
                if (self.compuMethodRef is not None) and (other.compuMethodRef is not None):
                    return self.rootWS().find(self.compuMethodRef) == other.rootWS().find(other.compuMethodRef)
                elif (self.compuMethodRef is None) and (other.compuMethodRef is None):
                    return True

    def __deepcopy__(self,memo):
        obj=type(self)(self.name,self.minVal,self.maxVal,self.compuMethodRef)
        if self.adminData is not None: obj.adminData=copy.deepcopy(self.adminData,memo)
        return obj

class RecordDataType(DataType):
    """
    RecordDataType (AUTOSAR3)
    """
    def tag(self,version=None): return 'RECORD-TYPE'
    def __init__(self, name, elements=None,  parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.elements = []
        if elements is not None:
            for elem in elements:
                if isinstance(elem, RecordTypeElement):
                    self.elements.append(elem)
                    elem.parent=self
                else:
                    raise ValueError('Element must be an instance of RecordTypeElement')
    def __eq__(self, other):
        if self is other: return True
        if (self.name == other.name) and (len(self.elements)==len(other.elements)):
            for i in range(len(self.elements)):
                if self.elements[i] != other.elements[i]: return False
            return True
        return False

    def __deepcopy__(self,memo):
        obj=type(self)(self.name)
        if self.adminData is not None: obj.adminData=copy.deepcopy(self.adminData,memo)
        for elem in self.elements:
            obj.elements.append(RecordTypeElement(elem.name,elem.typeRef,self))
        return obj




class ArrayDataType(DataType):
    """
    ArrayDataType (AUTOSAR 3)
    """
    def tag(self,version=None): return 'ARRAY-TYPE'

    def __init__(self, name, typeRef, length, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef = typeRef
        self.length = length

class BooleanDataType(DataType):
    """
    BooleanDataType (AUTOSAR 3)
    """
    def tag(self,version=None): return 'BOOLEAN-TYPE'

    def __init__(self,name, parent=None, adminData=None):
        super().__init__(name, parent, adminData)


class StringDataType(DataType):
    """
    StringDataType (AUTOSAR 3)
    """
    def tag(self,version=None): return 'STRING-TYPE'

    def __init__(self,name,length,encoding, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.length=length
        self.encoding=encoding
    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,'encoding':self.encoding,'length':self.length}
        return data
    def __eq__(self,other):
        if self is other: return False
        if type(self) == type(other):
            if (self.name==other.name) and (self.length == other.length) and (self.encoding == other.encoding):
                return True
        return False

    def __deepcopy__(self,memo):
        obj=type(self)(self.name,self.length,self.encoding)
        return obj


class RealDataType(DataType):
    """
    RealDataType (AUTOSAR 3)
    """
    def tag(self,version=None): return 'REAL-TYPE'

    def __init__(self, name, minVal, maxVal, minValType='CLOSED', maxValType='CLOSED', hasNaN=False, encoding='SINGLE', parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.minVal=minVal
        self.maxVal=maxVal
        self.minValType = minValType
        self.maxValType = maxValType
        self.hasNaN=hasNaN
        self.encoding=encoding

class Computation:
    """
    Represents one computation (COMPU-INTERNAL-TO-PHYS or COMPU-PHYS-TO-INTERNAL).
    Contains a list of CompuScaleElement objects as well as an optional defaultValue.
    """
    def __init__(self, defaultValue = None):
        self.elements = [] #list of CompuScaleElement
        self.defaultValue = defaultValue

    @property
    def lowerLimit(self):
        """
        Returns lowerLimit of first element
        """
        if len(self.elements) > 0:
            return self.elements[0].lowerLimit
        else:
            raise KeyError('No elements in Computation object')

    @property
    def upperLimit(self):
        """
        Returns upperLimit of last element
        """
        if len(self.elements) > 0:
            return self.elements[-1].upperLimit
        else:
            raise KeyError('No elements in Computation object')

    def createValueTable(self, elements, autoLabel = True):
        """
        Creates a list of CompuScaleElements based on contents of the elements argument

        When elements is a list of strings:
            Creates one CompuScaleElement per list item and automatically calculates lower and upper limits

        When elements is a list of tuples:
            If 2-tuple: First element is both lowerLimit and upperLimit, second element is textValue.
            If 3-tuple: First element is lowerLimit, second element is upperLimit, third element is textValue.

        autoLabel: automatically creates a <SHORT-LABEL> based on the element.textValue (bool). Default=True
        """
        lowerLimitType, upperLimitType = 'CLOSED', 'CLOSED'
        for elem in elements:
            if isinstance(elem, str):
                limit = len(self.elements)
                (lowerLimit, upperLimit, textValue) = (limit, limit, elem)
            elif isinstance(elem, tuple):
                if len(elem) == 2:
                    (limit, textValue) = elem
                    (lowerLimit, upperLimit, textValue) = (limit, limit, textValue)
                elif len(elem) == 3:
                    lowerLimit, upperLimit, textValue = elem
                else:
                    raise ValueError('invalid length: %d'%len(elem))
            else:
                raise ValueError('type not supported:%s'%str(type(elem)))
            label = textValue if autoLabel else None
            self.elements.append(CompuScaleElement(lowerLimit, upperLimit, lowerLimitType, upperLimitType, textValue = textValue, label = label))

    def createRationalScaling(self, offset, numerator, denominator, lowerLimit, upperLimit, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', label = None, symbol = None, adminData = None):
        """
        Creates COMPU-SCALE based on rational scaling
        """
        element = CompuScaleElement(lowerLimit, upperLimit, lowerLimitType, upperLimitType, label = label, symbol = symbol, offset = offset, numerator = numerator, denominator = denominator, adminData = adminData)
        self.elements.append(element)
        return element

    def createBitMask(self, elements, autoLabel = True):
        """
        When elements is a list of tuples:

            If 2-tuple: First element is the bitmask (int), second element is the symbol (str)
        """
        lowerLimitType, upperLimitType = 'CLOSED', 'CLOSED'
        for elem in elements:
            if isinstance(elem, tuple):
                if len(elem) == 2:
                    (mask, symbol) = elem
                    (lowerLimit, upperLimit) = (mask, mask)
                else:
                    raise ValueError('invalid length: %d'%len(elem))
            else:
                raise ValueError('type not supported:%s'%str(type(elem)))
            label = symbol if autoLabel else None
            self.elements.append(CompuScaleElement(lowerLimit, upperLimit, lowerLimitType, upperLimitType, symbol = symbol, label = label, mask = mask))

class CompuMethod(Element):
    """
    CompuMethod class
    """
    def tag(self,version=None): return 'COMPU-METHOD'

    def __init__(self, name, useIntToPhys, usePhysToInt, unitRef = None, category = None, parent = None, adminData = None):
        super().__init__(name, parent, adminData, category)
        self.unitRef = unitRef
        self.intToPhys = None
        self.physToInt = None
        if useIntToPhys:
            self.intToPhys = Computation()
        if usePhysToInt:
            self.physToInt = Computation()

class ConstraintBase:
    def __init__(self, lowerLimit, upperLimit, lowerLimitType, upperLimitType):
        if lowerLimit is not None:
            if isinstance(lowerLimit, str) and lowerLimit != '-INF':
                raise ValueError('Unknown lowerLimit: '+lowerLimit)
            self.lowerLimit = lowerLimit
        if upperLimit is not None:
            if isinstance(upperLimit, str) and upperLimit != 'INF':
                raise ValueError('Unknown upperLimit: '+upperLimit)
            self.upperLimit = upperLimit
        if lowerLimitType == 'CLOSED' or lowerLimitType == 'OPEN':
            self.lowerLimitType = lowerLimitType
        else:
            raise ValueError(lowerLimitType)
        if upperLimitType == 'CLOSED' or upperLimitType == 'OPEN':
            self.upperLimitType = upperLimitType
        else:
            raise ValueError(upperLimitType)

    def check_value(self, value):
        if ((self.lowerLimitType=='CLOSED') and (value<self.lowerLimit)) or ((self.lowerLimitType=='OPEN') and (value<=self.lowerLimit)) :
            raise autosar.base.DataConstraintError('Value {} outside lower data constraint ({}) '.format(str(value), str(self.lowerLimit)))
        if ((self.upperLimitType=='CLOSED') and (value>self.upperLimit)) or ((self.upperLimitType=='OPEN') and (value>=self.upperLimit)) :
            raise autosar.base.DataConstraintError('Value {} outside upper data constraint ({}) '.format(str(value), str(self.upperLimit)))

class InternalConstraint(ConstraintBase):
    def __init__(self, lowerLimit=None, upperLimit=None, lowerLimitType='CLOSED', upperLimitType='CLOSED'):
        super().__init__(lowerLimit, upperLimit, lowerLimitType, upperLimitType)

class PhysicalConstraint(ConstraintBase):
    def __init__(self, lowerLimit=None, upperLimit=None, lowerLimitType='CLOSED', upperLimitType='CLOSED'):
        super().__init__(lowerLimit, upperLimit, lowerLimitType, upperLimitType)

class DataConstraint(Element):
    def tag(self,version=None): return 'DATA-CONSTR'

    def __init__(self, name, rules, constraintLevel=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.level = constraintLevel
        self.rules = []
        for rule in rules:
            if rule['type'] == 'internalConstraint':
                self.rules.append(InternalConstraint(lowerLimit=rule['lowerLimit'], upperLimit=rule['upperLimit'], lowerLimitType=rule['lowerLimitType'], upperLimitType=rule['upperLimitType']))
            elif rule['type'] == 'physicalConstraint':
                self.rules.append(PhysicalConstraint(lowerLimit=rule['lowerLimit'], upperLimit=rule['upperLimit'], lowerLimitType=rule['lowerLimitType'], upperLimitType=rule['upperLimitType']))
            else:
                raise NotImplementedError
    @property
    def constraintLevel(self):
        if self.level is None or isinstance(self.level, int):
            return self.level
        else:
            raise ValueError('Unknown constraintLevel: '+str(self.level))

    @property
    def lowerLimit(self):
        if len(self.rules) == 1:
            return self.rules[0].lowerLimit
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    @property
    def upperLimit(self):
        if len(self.rules) == 1:
            return self.rules[0].upperLimit
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    @property
    def lowerLimitType(self):
        if len(self.rules) == 1:
            return self.rules[0].lowerLimitType
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    @property
    def upperLimitType(self):
        if len(self.rules) == 1:
            return self.rules[0].upperLimitType
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    def checkValue(self, v):
        if len(self.rules) == 1:
            self.rules[0].check_value(v)
        else:
            raise NotImplementedError('Only a single rule constraint supported')

    def findByType(self, constraintType = 'internalConstraint'):
        """
        Returns the first constraint of the given constraint type (internalConstraint or physicalConstraint)
        """
        for rule in self.rules:
            if (isinstance(rule, InternalConstraint) and constraintType == 'internalConstraint') or (isinstance(rule, PhysicalConstraint) and constraintType == 'physicalConstraint'):
                return rule

class ImplementationDataType(Element):
    def tag(self, version=None): return 'IMPLEMENTATION-DATA-TYPE'
    def __init__(self, name, variantProps = None, dynamicArraySizeProfile = None, typeEmitter = None, category='VALUE', parent = None, adminData = None):
        super().__init__(name, parent, adminData, category)
        self.dynamicArraySizeProfile = dynamicArraySizeProfile
        self.typeEmitter = typeEmitter
        self.variantProps = []
        self.subElements = []
        self.symbolProps = None
        if isinstance(variantProps, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
            self.variantProps.append(variantProps)
        elif isinstance(variantProps, collections.abc.Iterable):
            for elem in variantProps:
                if isinstance(elem, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
                    self.variantProps.append(elem)
                else:
                    raise ValueError('Invalid type: ', type(elem))

    def getArrayLength(self):
        """
        Deprecated, use arraySize property instead
        """
        return self.arraySize


    def getTypeReference(self):
        """
        Deprecated, use implementationTypeRef property instead
        """
        return self.implementationTypeRef

    @property
    def arraySize(self):
        if len(self.subElements)>0:
            return self.subElements[0].arraySize
        else:
            return None

    @property
    def implementationTypeRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].implementationTypeRef
        else:
            raise RuntimeError('ImplementationDataType has no variantProps')

    @property
    def baseTypeRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].baseTypeRef
        else:
            raise RuntimeError('Element has no variantProps set')

    @property
    def dataConstraintRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].dataConstraintRef
        else:
            raise RuntimeError('Element has no variantProps set')

    @property
    def compuMethodRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].compuMethodRef
        else:
            raise RuntimeError('Element has no variantProps set')

    def setSymbolProps(self, name, symbol):
        """
        Sets SymbolProps for this data type

        Arguments:
        name: <SHORT-NAME> (str)
        symbol: <SYMBOL> (str)
        """
        self.symbolProps = autosar.base.SymbolProps( str(name), str(symbol))

class SwBaseType(Element):
    def tag(self, version=None): return 'SW-BASE-TYPE'
    def __init__(self, name, size = None, typeEncoding = None, nativeDeclaration = None, category='FIXED_LENGTH', parent = None, adminData = None):
        super().__init__(name, parent, adminData, category)
        self.size = None if size is None else int(size)
        self.nativeDeclaration = nativeDeclaration
        self.typeEncoding = typeEncoding

class ImplementationDataTypeElement(Element):
    def tag(self, version=None): return 'IMPLEMENTATION-DATA-TYPE-ELEMENT'

    def __init__(self, name, category = None, arraySize = None, arraySizeSemantics = None, variantProps = None, parent = None, adminData = None):
        super().__init__(name, parent, adminData, category)
        self.arraySize = arraySize
        self.variantProps = []
        if arraySize is not None:
            if arraySizeSemantics is not None:
                self.arraySizeSemantics = arraySizeSemantics
            else:
                self.arraySizeSemantics = 'FIXED-SIZE'
        else:
            self.arraySizeSemantics = None
        if variantProps is not None:
            if isinstance(variantProps, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
                self.variantProps.append(variantProps)
            elif isinstance(variantProps, collections.abc.Iterable):
                for elem in variantProps:
                    if isinstance(elem, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
                        self.variantProps.append(elem)
                    else:
                        raise ValueError('Invalid type: ', type(elem))

class ApplicationDataType(Element):
    """
    Base type for AUTOSAR application data types (AUTOSAR4)

    Arguments:
    name: <SHORT-NAME> (None or str)
    variantProps: <SW-DATA-DEF-PROPS-VARIANTS> (instance (or list) of autosar.base.SwDataDefPropsConditional)
    category: <CATEGORY> (None or str)
    parent: parent object instance (usually the package it will belong to), (object)
    adminData: <ADMIN-DATA> (instance of autosar.base.AdminData or dict)
    """
    def __init__(self, name, variantProps=None, category=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData, category)
        self.variantProps = []
        if variantProps is not None:
            if isinstance(variantProps, autosar.base.SwDataDefPropsConditional):
                self.variantProps.append(variantProps)
            else:
                self.variantProps = list(variantProps)

    @property
    def compuMethodRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].compuMethodRef
        else:
            raise RuntimeError('Element has no variantProps')

    @property
    def dataConstraintRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].dataConstraintRef
        else:
            raise RuntimeError('Element has no variantProps')

    @property
    def unitRef(self):
        if len(self.variantProps)>0:
            return self.variantProps[0].unitRef
        else:
            raise RuntimeError('Element has no variantProps')

class ApplicationPrimitiveDataType(ApplicationDataType):
    """
    Implementation of <APPLICATION-PRIMITIVE-DATA-TYPE> (AUTOSAR 4)

    Arguments:
    (see base class)
    """
    def tag(self, version): return 'APPLICATION-PRIMITIVE-DATA-TYPE'

    def __init__(self, name, variantProps=None, category=None, parent=None, adminData=None):
        super().__init__(name, variantProps, category, parent, adminData)

class ApplicationArrayDataType(ApplicationDataType):
    """
    Implementation of <APPLICATION-ARRAY-DATA-TYPE> (AUTOSAR 4)

    Arguments:
    element: <ELEMENT> (instance of ApplicationArrayElement)
    """
    def tag(self, version): return 'APPLICATION-ARRAY-DATA-TYPE'

    def __init__(self, name, element, variantProps = None, category = 'ARRAY', parent=None, adminData=None):
        super().__init__(name, variantProps, category, parent, adminData)
        if element is None or isinstance(element, ApplicationArrayElement):
            self.element = element
            element.parent = self
        else:
            raise ValueError("element argument must be None or instance of ApplicationArrayElement")

class ApplicationArrayElement(Element):
    """
    An application array element (AUTOSAR 4).
    This is to be used as the element property of ApplicationArrayDataType.

    arguments:
    name: <SHORT-NAME> (None or str)
    typeRef: <TYPE-TREF> (None or str)
    arraySize: <MAX-NUMBER-OF-ELEMENTS> (None or int)
    sizeHandling: <ARRAY-SIZE-HANDLING> (None or str['ALL-INDICES-DIFFERENT-ARRAY-SIZE', 'ALL-INDICES-SAME-ARRAY-SIZE', 'INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE', ])
    sizeSemantics: <ARRAY-SIZE-SEMANTICS> (None or str['FIXED-SIZE', 'VARIABLE-SIZE']])
    """
    def tag(self, version=None): return 'ELEMENT'

    def __init__(self, name = None, typeRef = None, arraySize = None, sizeHandling = None, sizeSemantics = 'FIXED-SIZE', category = 'VALUE', parent = None, adminData = None):
        super().__init__(name, parent, adminData, category)
        self.typeRef = None if typeRef is None else str(typeRef)
        self.arraySize = None if arraySize is None else int(arraySize)
        self.sizeHandling = None if sizeHandling is None else str(sizeHandling)
        self.sizeSemantics = None if sizeSemantics is None else str(sizeSemantics)

class ApplicationRecordDataType(ApplicationDataType):
    """
    Implementation of <APPLICATION-RECORD-DATA-TYPE> (AUTOSAR 4)

    Arguments:
    elements: list of ApplicationRecordElement or None
    """
    def tag(self, version): return 'APPLICATION-RECORD-DATA-TYPE'

    def __init__(self, name, elements = None, variantProps = None, category = None, parent = None, adminData = None):
        super().__init__(name, variantProps, category, parent, adminData)
        if elements is None:
            self.elements = []
        else:
            self.elements = list(elements)

    def append(self, element):
        """
        Append element to self.elements list
        """
        if not isinstance(element, ApplicationRecordElement):
            raise ValueError('element must be an instance of ApplicationRecordElement')
        element.parent = self
        self.elements.append(element)

    def createElement(self, name, typeRef, category = 'VALUE', adminData = None):
        """
        Creates a new instance of ApplicationRecordElement and appends it to internal elements list
        """
        element = ApplicationRecordElement(name, typeRef, category, self, adminData)
        self.elements.append(element)

class ApplicationRecordElement(Element):
    """
    Implements <APPLICATION-RECORD-ELEMENT> (AUTOSAR4)
    """

    def tag(self, version): return 'APPLICATION-RECORD-ELEMENT'

    def __init__(self, name, typeRef, category = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData, category)
        if not isinstance(typeRef, str):
            raise autosar.base.InvalidDataTypeRef(typeRef)
        self.typeRef = typeRef

class DataTypeMappingSet(Element):
    def tag(self, version): return 'DATA-TYPE-MAPPING-SET'

    def __init__(self, name, parent = None, adminData = None):
        super().__init__(name, parent, adminData)
        self.applicationTypeMap = {} #applicationDataTypeRef to implementationDataTypeRef dictionary
        self.modeRequestMap = {} #modeDeclarationGroupRef to implementationDataTypeRef dictionary

    def createDataTypeMapping(self, applicationDataTypeRef, implementationDataTypeRef):
        self.applicationTypeMap[applicationDataTypeRef] = implementationDataTypeRef
        return DataTypeMap(applicationDataTypeRef,  implementationDataTypeRef)

    def createModeRequestMapping(self, modeDeclarationGroupRef, implementationDataTypeRef):
        self.modeRequestMap[modeDeclarationGroupRef] = implementationDataTypeRef
        return ModeRequestTypeMap(modeDeclarationGroupRef,  implementationDataTypeRef)

    def add(self, item):
        if isinstance(item, DataTypeMap):
                self.createDataTypeMapping(item.applicationDataTypeRef, item.implementationDataTypeRef)
        elif isinstance(item, ModeRequestTypeMap):
                self.createModeRequestMapping(item.modeDeclarationGroupRef, item.implementationDataTypeRef)
        else:
            raise ValueError("Item is neither an instance of DataTypeMap or ModeRequestTypeMap")

    def getDataTypeMapping(self, applicationDataTypeRef):
        """
        Returns an instance of DataTypeMap or None if not found.
        """
        implementationDataTypeRef = self.applicationTypeMap.get(applicationDataTypeRef, None)
        if implementationDataTypeRef is not None:
            return DataTypeMap(applicationDataTypeRef,  implementationDataTypeRef)
        return None

    def getModeRequestMapping(self, modeDeclarationGroupRef):
        """
        Returns an instance of DataTypeMap or None if not found.
        """
        implementationDataTypeRef = self.modeRequestMap.get(modeDeclarationGroupRef, None)
        if implementationDataTypeRef is not None:
            return ModeRequestTypeMap(modeDeclarationGroupRef,  implementationDataTypeRef)
        return None

    def findMappedDataTypeRef(self, applicationDataTypeRef):
        """
        Returns a reference (str) to the mapped implementation data type or None if not found.
        """
        return self.applicationTypeMap.get(applicationDataTypeRef, None)

    def findMappedDataType(self, applicationDataTypeRef):
        """
        Returns the instance of the mapped implementation data type.
        This requires that both the DataTypeMappingSet and the implementation data type reference are in the same AUTOSAR workspace.
        """
        implementationDataTypeRef = self.applicationTypeMap.get(applicationDataTypeRef, None)
        if implementationDataTypeRef is not None:
            ws = self.rootWS()
            if ws is None:
                raise RuntimeError("Root workspace not found")
            return ws.find(implementationDataTypeRef)
        return None

    def findMappedModeRequestRef(self, modeDeclarationGroupRef):
        """
        Returns a reference (str) to the mapped implementation data type or None if not found.
        """
        return self.modeRequestMap.get(modeDeclarationGroupRef, None)

    def findMappedModeRequest(self, modeDeclarationGroupRef):
        """
        Returns the instance of the mapped implementation data type.
        This requires that both the DataTypeMappingSet and the implementation data type reference are in the same AUTOSAR workspace.
        """
        implementationDataTypeRef = self.modeRequestMap.get(modeDeclarationGroupRef, None)
        if implementationDataTypeRef is not None:
            ws = self.rootWS()
            if ws is None:
                raise RuntimeError("Root workspace not found")
            return ws.find(implementationDataTypeRef)
        return None

class DataTypeMap:
    """
    Mapping from ApplicationDataType to ImplementationDataType.
    """

    def __init__(self, applicationDataTypeRef, implementationDataTypeRef):
        self.applicationDataTypeRef = applicationDataTypeRef
        self.implementationDataTypeRef = implementationDataTypeRef

    def tag(self, version): return 'DATA-TYPE-MAP'

class ModeRequestTypeMap:
    """
    Mapping from ModeGroupDeclaration to ImplementationDataType.
    """
    def __init__(self, modeDeclarationGroupRef, implementationDataTypeRef):
        self.modeDeclarationGroupRef = modeDeclarationGroupRef
        self.implementationDataTypeRef = implementationDataTypeRef

    def tag(self, version): return 'MODE-REQUEST-TYPE-MAP'

