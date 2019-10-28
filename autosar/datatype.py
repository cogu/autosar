from autosar.element import Element
import autosar.base
import math
import json
import copy
import collections

class ConstElement:
    def __init__(self,parent=None):
        self.parent=parent

    def asdict(self):
        data={'type': self.__class__.__name__}
        data.update(self.__dict__)
        return data
    def find(self,ref):
        if ref.startswith('/'):
            return self.root().find(ref)
        return None
    def rootWS(self):
        if self.parent is None: return None
        return self.parent.rootWS()

class RecordTypeElement(ConstElement):
    def __init__(self,name,typeRef,parent=None):
        super().__init__(parent)
        self.name=name
        self.typeRef=typeRef
    def __eq__(self,other):
        if self is other: return True
        if type(self) == type(other):
            if self.name == other.name:
                lhs = None if self.typeRef is None else self.find(self.typeRef)
                rhs = None if other.typeRef is None else other.find(other.typeRef)
                if lhs != rhs:
                    print(self.name,self.typeRef)
                return lhs==rhs
        return False

class CompuConstElement(ConstElement):
    def __init__(self, lowerLimit, upperLimit, textValue, label=None, symbol=None, adminData=None):
        self.lowerLimit=lowerLimit
        self.upperLimit=upperLimit
        self.textValue=textValue
        self.symbol=symbol
        self.label=label
        self.adminData=adminData
    def __eq__(self,other):
        if self is other: return True
        if type(self) is type(other):
            return (self.lowerLimit == other.lowerLimit) and (self.upperLimit == other.upperLimit) and (self.textValue == self.textValue)
        return False


class CompuRationalElement(ConstElement):
    def __init__(self, offset, numerator, denominator, label=None, symbol = None, adminData=None):
        self.offset=offset
        self.numerator=numerator
        self.denominator=denominator
        self.label=label
        self.symbol=symbol
        self.adminData=adminData
    def __eq__(self,other):
        if self is other: return True
        if type(self) is type(other):
            return (self.offset == other.offset) and (self.numerator == other.numerator) and (self.denominator == self.denominator)
        return False

class CompuMaskElement(ConstElement):
    def __init__(self, lowerLimit, upperLimit, mask, label=None, symbol=None, adminData=None):
        self.lowerLimit=lowerLimit
        self.upperLimit=upperLimit
        self.label=label
        self.mask=mask
        self.symbol=symbol
        self.adminData=adminData
    def __eq__(self,other):
        if self is other: return True
        if type(self) is type(other):
            return (self.lowerLimit == other.lowerLimit) and (self.upperLimit == other.upperLimit) and (self.mask == self.mask)
        return False

class DataTypeUnitElement(Element):
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
    def __init__(self, name, parent=None, adminData=None):
        super().__init__(name, parent, adminData)

    @property
    def isComplexType(self):
        return True if isinstance(self, (RecordDataType, ArrayDataType)) else False


class IntegerDataType(DataType):

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
                    return self.findWS().find(self.compuMethodRef) == other.findWS().find(other.compuMethodRef)
                elif (self.compuMethodRef is None) and (other.compuMethodRef is None):
                    return True

    def __deepcopy__(self,memo):
        obj=type(self)(self.name,self.minVal,self.maxVal,self.compuMethodRef)
        if self.adminData is not None: obj.adminData=copy.deepcopy(self.adminData,memo)
        return obj

class RecordDataType(DataType):
    def tag(self,version=None): return 'RECORD-TYPE'
    def __init__(self, name, elements=None,  parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.elements = []
        if elements is not None:
            for elem in elements:
                if isinstance(elem, RecordTypeElement):
                    self.elements.append(elem)
                    elem.parent=self
                elif isinstance(elem, tuple):
                    self.elements.append(RecordTypeElement(elem[0],elem[1],self))
                elif isinstance(elem, collections.Mapping):
                    self.elements.append(RecordTypeElement(elem['name'],elem['typeRef'],self))
                else:
                    raise ValueError('element must be either Mapping, RecordTypeElement or tuple')
    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
        if self.adminData is not None:
            data['adminData']=self.adminData.asdict()
        for elem in self.elements:
            data['elements'].append(elem.asdict())
        return data
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

    def tag(self,version=None): return 'ARRAY-TYPE'

    def __init__(self, name, typeRef, length, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef = typeRef
        self.length = length

class BooleanDataType(DataType):

    def tag(self,version=None): return 'BOOLEAN-TYPE'

    def __init__(self,name, parent=None, adminData=None):
        super().__init__(name, parent, adminData)


class StringDataType(DataType):
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
    def tag(self,version=None): return 'REAL-TYPE'

    def __init__(self, name, minVal, maxVal, minValType='CLOSED', maxValType='CLOSED', hasNaN=False, encoding='SINGLE', parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.minVal=minVal
        self.maxVal=maxVal
        self.minValType = minValType
        self.maxValType = maxValType
        self.hasNaN=hasNaN
        self.encoding=encoding


class CompuMethodRational(Element):
    def tag(self,version=None): return 'COMPU-INTERNAL-TO-PHYS'
    def __init__(self,name,unitRef,elements, category=None, adminData=None):
        super().__init__(name)
        self.category=category
        self.unitRef = unitRef
        self.adminData = adminData
        self.elements = []

        for elem in elements:
            self.elements.append(CompuRationalElement(**elem))
    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
        for element in self.elements:
            data['elements'].append(element.asdict())
        return data

    def find(self,ref):
        if ref.startswith('/'):
            root=self.rootWS()
            return root.find(ref)
        return None

    def __eq__(self,other):
        if self is other: return True
        if self.name == other.name:
            lhs = None if self.unitRef is None else self.find(self.unitRef)
            rhs = None if other.unitRef is None else other.find(other.unitRef)
            if lhs == rhs:
                if len(self.elements)!=len(other.elements): return False
                for i in range(len(self.elements)):
                    if self.elements[i] != other.elements[i]: return False
                return True
        return False


class CompuMethodConst(Element):
    def tag(self, version=3.0): return 'COMPU-METHOD'
    def __init__(self, name, elements, category=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.elements = []
        self.category=category
        for elem in elements:
            if isinstance(elem,str):
                index=len(self.elements)
                self.elements.append(CompuConstElement(lowerLimit=index,upperLimit=index,textValue=elem))
            elif isinstance(elem,dict):
                self.elements.append(CompuConstElement(**elem))
            elif isinstance(elem,tuple):
                if len(elem)==2:
                    self.elements.append(CompuConstElement(lowerLimit=elem[0],upperLimit=elem[0],textValue=elem[1]))
                elif len(elem)==3:
                    self.elements.append(CompuConstElement(*elem))
                else:
                    raise ValueError('invalid length: %d'%len(elem))
            else:
                raise ValueError('type not supported:%s'%str(type(elem)))
    # def asdict(self):
    #    data={'type': self.__class__.__name__,'name':self.name,'elements':[]}
    #    for element in self.elements:
    #       data['elements'].append(element.asdict())
    #    return data

    def getValueTable(self):
        retval = []
        i = 0
        for elem in self.elements:
            if (elem.lowerLimit == elem.upperLimit) and elem.lowerLimit==i:
                retval.append(elem.textValue)
            else:
                return None
            i+=1
        return retval if len(retval)>0 else None

    def textValue(self, numericValue):
        for elem in self.elements:
            if (elem.lowerLimit <= numericValue) and (numericValue <= elem.upperLimit):
                return (elem.textValue)
        return None

    def __eq__(self,other):
        if self is other: return True
        if self.name == other.name:
            if len(self.elements)!=len(other.elements): return False
            for i in range(len(self.elements)):
                if self.elements[i] != other.elements[i]: return False
            return True
        return False

class CompuMethodMask(Element):
    def __init__(self, name, elements, parent=None, category=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.elements = []
        self.category=category
        self.minVal = 0
        self.maxVal = 0
        for elem in elements:
            if isinstance(elem,str):
                mask= (1 << len(self.elements))
                self.elements.append(CompuMaskElement(lowerLimit=mask, upperLimit=mask, mask=mask, label=elem, symbol=elem))
            elif isinstance(elem,dict):
                self.elements.append(CompuMaskElement(**elem))
            else:
                raise ValueError('type not supported:%s'%str(type(elem)))
        self._calc_maxVal()

    def __eq__(self,other):
        if self is other: return True
        if self.name == other.name:
            if len(self.elements)!=len(other.elements): return False
            for i in range(len(self.elements)):
                if self.elements[i] != other.elements[i]: return False
            return True
        return False

    def _calc_maxVal(self):
        tmp = 0
        for elem in self.elements:
            if elem.upperLimit > tmp:
                tmp = elem.upperLimit
        self.maxVal = 2**int.bit_length(tmp)-1

class InternalConstraint:
    def __init__(self, lowerLimit=None, upperLimit=None, lowerLimitType='CLOSED', upperLimitType='CLOSED'):
        if lowerLimit is not None:
            if isinstance(lowerLimit, str) and lowerLimit != '-INF':
                raise ValueError('Unknown lowerLimit: '+lowerLimit)
            self.lowerLimit = lowerLimit
        if upperLimit is not None:
            if isinstance(upperLimit, str) and upperLimit != 'INF':
                raise ValueError('Unknown lowerLimit: '+upperLimit)
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

class DataConstraint(Element):
    def tag(self,version=None): return 'DATA-CONSTR'

    def __init__(self, name, rules, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.rules = []
        for rule in rules:
            if rule['type'] == 'internalConstraint':
                self.rules.append(InternalConstraint(lowerLimit=rule['lowerLimit'], upperLimit=rule['upperLimit'], lowerLimitType=rule['lowerLimitType'], upperLimitType=rule['upperLimitType']))

    def check_value(self, v):
        if len(self.rules) == 1:
            self.rules[0].check_value(v)
        else:
            raise NotImplementedError('Only a single rule supported')


class ImplementationDataType(Element):
    def tag(self, version=None): return 'IMPLEMENTATION-DATA-TYPE'
    def __init__(self, name, category='VALUE', variantProps=None, dynamicArraySizeProfile=None, typeEmitter=None, adminData=None, parent=None):
        super().__init__(name, parent, adminData)
        self.category = category
        self.dynamicArraySizeProfile = dynamicArraySizeProfile
        self.typeEmitter = typeEmitter
        self.variantProps = []
        self.subElements = []
        if isinstance(variantProps, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
            self.variantProps.append(variantProps)
        elif isinstance(variantProps, collections.Iterable):
            for elem in variantProps:
                if isinstance(elem, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
                    self.variantProps.append(elem)
                else:
                    raise ValueError('Invalid type: ', type(elem))

    def getArrayLength(self):
        if self.category == 'ARRAY' and len(self.subElements)>0:
            return self.subElements[0].arraySize
        else:
            raise RunTimeError('Not categorized as an array: '+self.name)

    def getTypeReference(self):
        if self.category == 'TYPE_REFERENCE' and len(self.variantProps)>0:
            return self.variantProps[0].implementationTypeRef
        else:
            raise RunTimeError('Not categorized as a type reference: '+self.name)


class SwBaseType(Element):
    def tag(self, version=None): return 'SW-BASE-TYPE'
    def __init__(self, name, size, typeEncoding=None, nativeDeclaration=None, category=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.size = int(size)
        self.typeEncoding=typeEncoding
        self.nativeDeclaration=nativeDeclaration
        if category is None: category='FIXED_LENGTH'
        self.category = category

class ImplementationDataTypeElement(Element):
    def tag(self, version=None): return 'IMPLEMENTATION-DATA-TYPE-ELEMENT'

    @classmethod
    def createTypeRef(cls, name, arraySize=None, arraySizeSemantics=None, variantProps=None, parent=None, adminData=None):
        return ImplementationDataTypeElement(name, 'TYPE_REFERENCE', arraySize, arraySizeSemantics, variantProps, parent, adminData)

    def __init__(self, name, category=None, arraySize=None, arraySizeSemantics=None, variantProps=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.category=category
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
            elif isinstance(variantProps, collections.Iterable):
                for elem in variantProps:
                    if isinstance(elem, (autosar.base.SwDataDefPropsConditional, autosar.base.SwPointerTargetProps)):
                        self.variantProps.append(elem)
                    else:
                        raise ValueError('Invalid type: ', type(elem))

class ApplicationPrimitiveDataType(Element):
    def tag(self, version=None): return 'APPLICATION-PRIMITIVE-DATA-TYPE'
    def __init__(self, name, category=None, variantProps=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.category=category
        self.variantProps = []
        if variantProps is not None:
            if isinstance(variantProps, autosar.base.SwDataDefPropsConditional):
                self.variantProps.append(variantProps)
            else:
                self.variantProps = list(variantProps)

class DataTypeMappingSet(Element):
    def tag(self, version): return 'DATA-TYPE-MAPPING-SET'

    def __init__(self, name, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.map = {} #applicationDataTypeRef to implementationDataTypeRef dictionary

    def addDirect(self, applicationDataTypeRef, implementationDataTypeRef):
        self.map[applicationDataTypeRef] = implementationDataTypeRef

    def add(self, dataTypeMap):
        assert (isinstance(dataTypeMap, DataTypeMap))
        self.addDirect(dataTypeMap.applicationDataTypeRef, dataTypeMap.implementationDataTypeRef)

    def get(self, applicationDataTypeRef):
        if applicationDataTypeRef in self.map:
            return DataTypeMap(applicationDataTypeRef,  self.map[applicationDataTypeRef])
        return None

class DataTypeMap:
    def __init__(self, applicationDataTypeRef, implementationDataTypeRef):
        self.applicationDataTypeRef = applicationDataTypeRef
        self.implementationDataTypeRef = implementationDataTypeRef

    def tag(self, version): return 'DATA-TYPE-MAP'
