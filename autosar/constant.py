from autosar.element import Element, LabelElement

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
        raise NotImplementedError(str(type(constant)))


class Value(Element):
    def __init__(self, name, parent=None, adminData = None, category = None):
        super().__init__(name, parent, adminData, category)

class ValueAR4(LabelElement):
    """Same as Value but uses label as main identifier instead of name"""
    def __init__(self, label, parent=None, adminData = None, category = None):
        super().__init__(label, parent, adminData, category)

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


class ConstantReference(ValueAR4):
    """
    Container class for <CONSTANT-REFERENCE> (AUTOSAR 4)
    """

    def tag(self, version): return 'CONSTANT-REFERENCE'

    def __init__(self, label=None, value=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        self.value = value

class RecordValueAR4(ValueAR4):
    def tag(self,version=None): return "RECORD-VALUE-SPECIFICATION"

    def __init__(self, label, typeRef=None, elements=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        self.typeRef=typeRef
        if elements is None:
            self.elements=[]
        else:
            self.elements = list(elements)


class ArrayValueAR4(ValueAR4):
    def tag(self,version=None): return "ARRAY-VALUE-SPECIFICATION"

    def __init__(self, label=None, typeRef=None, elements=None, category = None, parent = None, adminData = None):
        super().__init__(label, parent, adminData, category)
        self.typeRef=typeRef
        if elements is None:
            self.elements=[]
        else:
            self.elements = list(elements)

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
        self.unitRef = unitRef
        self.unitDisplayName = unitDisplayName
        self.swArraySize = swArraySize


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
        self.swArraySize = swArraySize
        self.category = category
        if values is None:
            self.values = None
        else:
            if isinstance(values, list):
                self.values = list(values)
            else:
                self.values = values
