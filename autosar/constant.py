from autosar.element import Element, LabelElement
from autosar.util.errorHandler import handleNotImplementedError

def initializer_string(constant):
    if constant is None:
        return ''
    elif isinstance(constant, IntegerValue):
        return '%d'%(int(constant.value))
    elif isinstance(constant, RecordValue):
        prolog = '{'
        epilog = '}'
        values = []
        for elem in constant.elements:
            values.append(initializer_string(elem))
        return prolog+', '.join(values) + epilog
    else:
        handleNotImplementedError(str(type(constant)))


class Value(Element):
    def __init__(self, name, parent=None, adminData = None, category = None):
        super().__init__(name, parent, adminData, category)

class ValueAR4(LabelElement):
    """Same as Value but uses label as main identifier instead of name"""
    def __init__(self, label, parent=None, adminData = None, category = None):
        super().__init__(label, parent, adminData, category)

    def asdict(self):
        data = {}
        data['type'] = self.__class__.__name__
        data['label'] = self.label
        if self.adminData is not None:
            data['adminData'] = self.adminData.asdict()
        if self.category is not None:
            data['category'] = self.category
        return data

#AUTOSAR 3 constant values
class IntegerValue(Value):

    def tag(self,version=None): return "INTEGER-LITERAL"

    def __init__(self, name, typeRef=None, value=None, parent=None):
        super().__init__(name, parent)
        self.typeRef=typeRef
        self.value=value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        if val is not None:
            self._value=int(val)
        else:
            self._value=None


class StringValue(Value):

    def tag(self,version=None): return "STRING-LITERAL"


    def __init__(self, name, typeRef=None, value=None, parent=None):
        super().__init__(name, parent)
        if value is None:
            value=''
        assert(isinstance(value,str))
        self.typeRef=typeRef
        self.value=value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        if val is not None:
            self._value=str(val)
        else:
            self._value=None


class BooleanValue(Value):

    def tag(self,version=None): return "BOOLEAN-LITERAL"

    def __init__(self, name, typeRef=None, value=None, parent=None):
        super().__init__(name, parent)
        self.typeRef=typeRef
        self.value=value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        if val is not None:
            if isinstance(val,str):
                self._value = True if val=='true' else False
            else:
                self._value=bool(val)
        else:
            self._value=None


class RecordValue(Value):
    """
    typeRef is only necessary for AUTOSAR 3 constants
    """
    def tag(self,version=None): return "RECORD-VALUE-SPECIFICATION" if version >= 4.0 else "RECORD-SPECIFICATION"

    def __init__(self, name, typeRef=None, elements=None, parent=None):
        super().__init__(name, parent)
        self.typeRef=typeRef
        if elements is None:
            self.elements=[]
        else:
            self.elements = list(elements)


class ArrayValue(Value):
    """
    name and typeRef is only necessary for AUTOSAR 3 constants
    """
    def tag(self,version=None): return "ARRAY-VALUE-SPECIFICATION" if version >= 4.0 else "ARRAY-SPECIFICATION"

    def __init__(self, name=None, typeRef=None, elements=None, parent=None):
        super().__init__(name, parent)
        self.typeRef=typeRef
        if elements is None:
            self.elements=[]
        else:
            self.elements = list(elements)


#AUTOSAR 4 constant values
class TextValue(ValueAR4):
    def tag(self, version=None): return "TEXT-VALUE-SPECIFICATION"

    def __init__(self, label, value=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        if value is None:
            value=''
        self.value=value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        if val is not None:
            self._value=str(val)
        else:
            self._value=None

    def asdict(self):
        data = super().asdict()
        data['value'] = self.value
        return data

class NumericalValue(ValueAR4):

    def tag(self, version=None): return "NUMERICAL-VALUE-SPECIFICATION"

    def __init__(self, label = None, value = None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        if value is None:
            value = 0
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        if val is not None:
            self._value = str(val)
        else:
            self._value = None

    def asdict(self):
        data = super().asdict()
        data['value'] = self.value
        return data

class ApplicationValue(ValueAR4):
    """
    (AUTOSAR4)
    Implements <APPLICATION-VALUE-SPECIFICATION>
    """
    def tag(self, version=None): return "APPLICATION-VALUE-SPECIFICATION"

    def __init__(self, label = None, swValueCont = None, swAxisCont = None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        if (swAxisCont is not None) and (not isinstance(swAxisCont, SwAxisCont)):
            raise ValueError('swAxisCont argument must be None or instance of SwAxisCont')
        if (swValueCont is not None) and (not isinstance(swValueCont, SwValueCont)):
            raise ValueError('swValueCont argument must be None or instance of SwValueCont')
        self.swAxisCont = swAxisCont
        self.swValueCont = swValueCont

    def asdict(self):
        data = super().asdict()
        if self.swAxisCont is not None:
            data['swAxisCont'] = self.swAxisCont.asdict()
        if self.swValueCont is not None:
            data['swValueCont'] = self.swValueCont.asdict()
        return data


class ConstantReference(ValueAR4):
    """
    Container class for <CONSTANT-REFERENCE> (AUTOSAR 4)
    """

    def tag(self, version): return 'CONSTANT-REFERENCE'

    def __init__(self, label=None, value=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        self.value = value

    def asdict(self):
        data = super().asdict()
        data['value'] = self.value
        return data

class RecordValueAR4(ValueAR4):
    def tag(self,version=None): return "RECORD-VALUE-SPECIFICATION"

    def __init__(self, label, typeRef=None, elements=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        self.typeRef=typeRef
        if elements is None:
            self.elements=[]
        else:
            self.elements = list(elements)

    def asdict(self):
        data = super().asdict()
        data['typeRef'] = self.typeRef
        data['elements'] = [elem.asdict() for elem in self.elements]
        return data


class ArrayValueAR4(ValueAR4):
    def tag(self,version=None): return "ARRAY-VALUE-SPECIFICATION"

    def __init__(self, label=None, typeRef=None, elements=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        self.typeRef=typeRef
        if elements is None:
            self.elements=[]
        else:
            self.elements = list(elements)

    def asdict(self):
        data = super().asdict()
        data['typeRef'] = self.typeRef
        data['elements'] = [elem.asdict() for elem in self.elements]
        return data

#Common classes
class Constant(Element):

    def tag(self, version): return 'CONSTANT-SPECIFICATION'

    def __init__(self, name, value=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.value=value
        if value is not None:
            value.parent=self

    def find(self,ref):
        if self.value.name==ref:
            return self.value
        return None

class SwValueCont:
    """
    (AUTOSAR4)
    Implements <SW-VALUE-CONT>
    """

    def tag(self, version = None): return 'SW-VALUE-CONT'

    def __init__(self, values = None, unitRef = None, unitDisplayName = None, swArraySize = None):
        if values is None:
            self.values = None
        else:
            if isinstance(values, list):
                self.values = list(values)
            else:
                self.values = values
        if swArraySize is None:
            self.swArraySize = None
        else:
            if isinstance(swArraySize, list):
                self.swArraySize = list(swArraySize)
            else:
                self.swArraySize = swArraySize
        self.unitRef = unitRef
        self.unitDisplayName = unitDisplayName
        self.swArraySize = swArraySize

    def asdict(self):
        data = {}
        data['type'] = self.__class__.__name__
        if self.values is not None:
            data['values'] = [elem.asdict() for elem in self.values]
        if self.unitRef is not None:
            data['unitRef'] = self.unitRef
        if self.unitDisplayName is not None:
            data['unitDisplayName'] = self.unitDisplayName
        if self.swArraySize is not None:
            data['swArraySize'] = self.swArraySize
        return data


class SwAxisCont:
    """
    (AUTOSAR4)
    Implements <SW-AXIS-CONT>
    """

    def tag(self, version = None): return 'SW-AXIS-CONT'

    def __init__(self, values = None, unitRef = None, unitDisplayName = None, swAxisIndex = None, swArraySize = None, category = None):
        self.unitRef = unitRef
        self.unitDisplayName = unitDisplayName
        self.swAxisIndex = swAxisIndex
        if swArraySize is None:
            self.swArraySize = None
        else:
            if isinstance(swArraySize, list):
                self.swArraySize = list(swArraySize)
            else:
                self.swArraySize = swArraySize
        self.category = category
        if values is None:
            self.values = None
        else:
            if isinstance(values, list):
                self.values = list(values)
            else:
                self.values = values

    def asdict(self):
        data = {}
        data['type'] = self.__class__.__name__
        if self.values is not None:
            data['values'] = [elem.asdict() for elem in self.values]
        if self.unitRef is not None:
            data['unitRef'] = self.unitRef
        if self.unitDisplayName is not None:
            data['unitDisplayName'] = self.unitDisplayName
        if self.swAxisIndex is not None:
            data['swAxisIndex'] = self.swAxisIndex
        if self.swArraySize is not None:
            data['swArraySize'] = self.swArraySize
        if self.category is not None:
            data['category'] = self.category
        return data

class PortDefinedArgumentValue:
    def tag(self, version): return 'PORT-DEFINED-ARGUMENT-VALUE'

    def __init__(self, value, valueTypeRef):
        self.value = value
        if value is not None:
            value.parent = self
        self.valueTypeRef = valueTypeRef

    def asdict(self):
        return {'type': self.__class__.__name__, 'value':self.value.asdict(), 'valueTypeRef':self.valueTypeRef}

class ConstantSpecificationMappingSet(Element):
    def tag(self, version): return 'CONSTANT-SPECIFICATION-MAPPING-SET'

    def __init__(self, name, parent = None, adminData = None):
        super().__init__(name, parent, adminData)
        self.mappings = {} #applConstantRef to implConstantRef dictionary

    def createConstantSpecificationMapping(self, applConstantRef, implConstantRef):
        self.mappings[applConstantRef] = implConstantRef
        return ConstantSpecificationMapping(applConstantRef, implConstantRef)

    def add(self, item):
        if isinstance(item, ConstantSpecificationMapping):
                self.createConstantSpecificationMapping(item.applConstantRef, item.implConstantRef)
        else:
            raise ValueError("Item is not an instance of ConstantSpecificationMapping")

    def getMapping(self, applConstantRef):
        """
        Returns an instance of ConstantSpecificationMapping or None if not found.
        """
        implConstantRef = self.mappings.get(applConstantRef, None)
        if implConstantRef is not None:
            return ConstantSpecificationMapping(applConstantRef, implConstantRef)
        return None

    def findMappedConstantRef(self, applConstantRef):
        """
        Returns a reference (str) to the mapped constant or None if not found.
        """
        return self.mappings.get(applConstantRef, None)

    def findMappedConstant(self, applConstantRef):
        """
        Returns the instance of the mapped constant.
        This requires that both the ConstantSpecificationMappingSet and the implementation constant reference are in the same AUTOSAR workspace.
        """
        implConstantRef = self.mappings.get(applConstantRef, None)
        if implConstantRef is not None:
            ws = self.rootWS()
            if ws is None:
                raise RuntimeError("Root workspace not found")
            return ws.find(implConstantRef)
        return None

class ConstantSpecificationMapping:
    """
    Mapping from Application Constant to Implementation Constant
    """

    def __init__(self, applConstantRef, implConstantRef):
        self.applConstantRef = applConstantRef
        self.implConstantRef = implConstantRef

    def tag(self, version): return 'CONSTANT-SPECIFICATION-MAPPING'
