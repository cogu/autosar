import collections
from autosar.element import (Element, DataElement)
import autosar.base
import autosar.mode

class InvalidationPolicy:
    valid_values = ['DONT-INVALIDATE', 'EXTERNAL-REPLACEMENT', 'KEEP', 'REPLACE']

    def tag(self, version): # pylint: disable=unused-argument
        return 'INVALIDATION-POLICY'

    def __init__(self, dataElementRef, handleInvalid):
        self.dataElementRef = dataElementRef
        self.handleInvalid = handleInvalid

    @property
    def handleInvalid(self):
        return self._handleInvalid

    @handleInvalid.setter
    def handleInvalid(self, value):
        if value not in InvalidationPolicy.valid_values:
            raise ValueError('invalid value: %s'%value)
        self._handleInvalid = value

class PortInterface(Element):
    def __init__(self, name, isService=False, serviceKind = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.isService=bool(isService)
        self.serviceKind = serviceKind

    def __getitem__(self,key):
        if isinstance(key,str):
            return self.find(key)
        else:
            raise ValueError('expected string')

    def find(self, ref):
        raise NotImplementedError(type(self))

class SenderReceiverInterface(PortInterface):

    def tag(self, version = None): #pylint: disable=unused-argument
        return 'SENDER-RECEIVER-INTERFACE'

    def __init__(self, name, isService=False, serviceKind = None, parent=None, adminData=None):
        super().__init__(name, isService, serviceKind, parent, adminData)
        self.dataElements=[]
        self.modeGroups=[] #AUTOSAR3 only
        self.invalidationPolicies=[] #AUTOSAR4 only

    def __iter__(self):
        return iter(self.dataElements)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.isService == other.isService and \
            self.adminData == other.adminData and len(self.dataElements) == len(other.dataElements):
                if (self.modeGroups is not None) and (other.modeGroups is not None) and len(self.modeGroups) == len(other.modeGroups):
                    for i,elem in enumerate(self.modeGroups):
                        if elem != other.modeGroups[i]:
                            return False
                    return True
                for i,elem in enumerate(self.dataElements):
                    if elem != other.dataElements[i]:
                        return False
        return False

    def __ne__(self, other):
        return not (self == other)

    def dir(self):
        return [x.name for x in self.dataElements]

    def find(self,ref):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.dataElements:
            if elem.name==name:
                return elem
        for elem in self.modeGroups:
            if elem.name==name:
                return elem
        return None

    def append(self,elem):
        """
        Adds child element to this port interface
        """
        if isinstance(elem, DataElement):
            self.dataElements.append(elem)
        elif isinstance(elem, autosar.mode.ModeGroup):
            self.modeGroups.append(elem)
        elif isinstance(elem, InvalidationPolicy):
            self.invalidationPolicies.append(elem)
        else:
            raise ValueError("expected elem variable to be of type DataElement")
        elem.parent=self

class ParameterInterface(PortInterface):
    def tag(self,version=None):
        if version>=4.0:
            return 'PARAMETER-INTERFACE'
        else:
            return 'CALPRM-INTERFACE'

    def __init__(self, name, isService=False, serviceKind = None, parent=None, adminData=None):
        super().__init__(name, isService, serviceKind, parent, adminData)
        self.parameters=[]

    def find(self,ref):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.parameters:
            if elem.name==name:
                return elem

    def append(self,elem):
        """
        adds elem to the self.parameters list and sets elem.parent to self (the port interface)
        """
        if not isinstance(elem, autosar.element.ParameterDataPrototype):
            raise ValueError("Expected elem variable to be of type ParameterDataPrototype")
        self.parameters.append(elem)
        elem.parent=self

class ClientServerInterface(PortInterface):
    def __init__(self, name, isService=False, serviceKind = None, parent=None, adminData=None):
        super().__init__(name, isService, serviceKind, parent, adminData)
        self.operations=[]
        self.applicationErrors=[]

    def tag(self, version = None): #pylint: disable=unused-argument
        return 'CLIENT-SERVER-INTERFACE'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.adminData == other.adminData and len(self.operations) == len(other.operations) and \
            len(self.applicationErrors) == len(other.applicationErrors):
                for i,operation in enumerate(self.operations):
                    if operation != other.operations[i]: return False
                for i,applicationError in enumerate(self.applicationErrors):
                    if applicationError != other.applicationErrors[i]: return False
                return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def find(self,ref):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.operations:
            if elem.name==name:
                return elem
        for elem in self.applicationErrors:
            if elem.name==name:
                return elem
        return None

    def append(self,elem):
        """
        Adds elem to the self.operations or self.applicationErrors lists depending on type
        """
        if isinstance(elem, Operation):
            self.operations.append(elem)
        elif isinstance(elem, ApplicationError):
            self.applicationErrors.append(elem)
        else:
            raise ValueError("invalid type: %s"%(str(type(elem))))
        elem.parent=self

class Operation(Element):
    def tag(self,version=None):
        return 'CLIENT-SERVER-OPERATION' if version >=4.0 else 'OPERATION-PROTOTYPE'

    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.arguments=[]
        self.errorRefs=[]


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.adminData == other.adminData and len(self.arguments) == len(other.arguments) and \
            (len(self.errorRefs) == len(other.errorRefs)):
                for i,argument in enumerate(self.arguments):
                    if argument != other.arguments[i]: return False
                for i,errorRef in enumerate(self.errorRefs):
                    if errorRef != other.errorRefs[i]: return False
                return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def createOutArgument(self, name, typeRef, swCalibrationAccess = None, serverArgumentImplPolicy=None):
        ws = self.rootWS()
        assert(ws is not None)
        dataType = ws.find(typeRef, role='DataType')
        if dataType is None:
            raise ValueError("invalid name or reference: "+typeRef)
        argument=Argument(name, dataType.ref, 'OUT', swCalibrationAccess, serverArgumentImplPolicy, parent=self)
        self.arguments.append(argument)
        return argument

    def createInOutArgument(self, name, typeRef, swCalibrationAccess = None, serverArgumentImplPolicy=None):
        ws = self.rootWS()
        assert(ws is not None)
        dataType = ws.find(typeRef, role='DataType')
        if dataType is None:
            raise ValueError("invalid name or reference: "+typeRef)
        argument=Argument(name, dataType.ref, 'INOUT', swCalibrationAccess, serverArgumentImplPolicy)
        self.arguments.append(argument)
        return argument

    def createInArgument(self, name, typeRef, swCalibrationAccess = None, serverArgumentImplPolicy=None):
        ws = self.rootWS()
        assert(ws is not None)
        dataType = ws.find(typeRef, role='DataType')
        if dataType is None:
            raise ValueError("invalid name or reference: "+typeRef)
        argument=Argument(name, dataType.ref, 'IN', swCalibrationAccess, serverArgumentImplPolicy)
        self.arguments.append(argument)
        return argument

    def append(self, elem):
        """
        Adds elem to the self.arguments or self.errorRefs lists depending on type
        """
        if isinstance(elem, Argument):
            self.arguments.append(elem)
        elif isinstance(elem, str):
            self.errorRefs.append(elem)
        else:
            raise ValueError("invalid type: %s"%(str(type(elem))))
        elem.parent=self


    @property
    def possibleErrors(self):
        return None

    @possibleErrors.setter
    def possibleErrors(self, values):
        if self.parent is None:
            raise ValueError('cannot call this method without valid parent object')
        if isinstance(values, str):
            values=[values]

        if isinstance(values, collections.abc.Iterable):
            del self.errorRefs[:]
            for name in values:
                found=False
                for error in self.parent.applicationErrors:
                    if error.name == name:
                        self.errorRefs.append(error.ref)
                        found=True
                        break
                if found==False:
                    raise ValueError('invalid error name: "%s"'%name)
        else:
            raise ValueError("input argument must be string or iterrable")


class Argument(Element):
    def tag(self,version=None):
        return 'ARGUMENT-DATA-PROTOTYPE' if version>=4.0 else 'ARGUMENT-PROTOTYPE'

    def __init__(self, name, typeRef, direction, swCalibrationAccess = None, serverArgumentImplPolicy=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef=typeRef
        self.direction = direction
        self.swCalibrationAccess = swCalibrationAccess
        self.serverArgumentImplPolicy = serverArgumentImplPolicy

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if (value != 'IN') and (value != 'OUT') and (value != 'INOUT'):
            raise ValueError('invalid value :%s'%value)
        self._direction=value

    def __eq__(self, other):
        left_ws = self.rootWS()
        right_ws = other.rootWS()
        assert(left_ws is not None)
        assert(right_ws is not None)
        left_type = left_ws.find(self.typeRef)
        if (left_type is None):
            raise autosar.base.InvalidDataTypeRef(self.typeRef)
        right_type = right_ws.find(other.typeRef)
        if (right_type is None):
            raise autosar.base.InvalidDataTypeRef(other.typeRef)
        if self.direction != other.direction: return False
        if (self.swCalibrationAccess is None and other.swCalibrationAccess is not None) or (self.swCalibrationAccess is not None and other.swCalibrationAccess is None):
            return False
        if self.swCalibrationAccess is not None and other.swCalibrationAccess is not None:
            if self.swCalibrationAccess != other.swCalibrationAccess: return False
        if (self.serverArgumentImplPolicy is None and other.serverArgumentImplPolicy is not None) or (self.serverArgumentImplPolicy is not None and other.serverArgumentImplPolicy is None):
            return False
        if self.serverArgumentImplPolicy is not None and other.serverArgumentImplPolicy is not None:
            if self.serverArgumentImplPolicy != other.serverArgumentImplPolicy: return False
        return left_type == right_type

    def __ne__(self, other):
        return not (self == other)

class ApplicationError(Element):
    def __init__(self, name, errorCode, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.errorCode=int(errorCode)

    def tag(self, version = None):  #pylint: disable=unused-argument
        return 'APPLICATION-ERROR'

    def asdict(self):
        return {'type': self.__class__.__name__, 'name':self.name, 'errorCode':self.errorCode}

class ModeSwitchInterface(PortInterface):
    """
    Implementation of <MODE-SWITCH-INTERFACE> (AUTOSAR 4)
    """

    def tag(self, version = None):  #pylint: disable=unused-argument
        return 'MODE-SWITCH-INTERFACE'

    def __init__(self, name, isService=None, parent=None, adminData=None):
        """
        Arguments:
        name: <SHORT-NAME> (None or str)
        isService: <IS-SERVICE> (None or bool)
        """
        super().__init__(name, isService, parent,adminData)
        self._modeGroup=None

    @property
    def modeGroup(self):
        return self._modeGroup

    @modeGroup.setter
    def modeGroup(self, value):
        if not isinstance(value, autosar.mode.ModeGroup):
            raise ValueError('value must be of ModeGroup type')
        self._modeGroup=value

    def find(self,ref):
        ref = ref.partition('/')
        name = ref[0]
        modeGroup = self.modeGroup
        if modeGroup is not None and modeGroup.name == name:
            return modeGroup
        return None

class NvDataInterface(PortInterface):
    def tag(self,version=None):
        if version>=4.0:
            return 'NV-DATA-INTERFACE'
        else:
            raise ValueError("Autosar 3 is not supported")

    def __init__(self, name, isService=False, serviceKind = None, parent=None, adminData=None):
        super().__init__(name, isService, serviceKind, parent, adminData)
        self.nvDatas=[]

    def find(self,ref):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.nvDatas:
            if elem.name==name:
                return elem

    def append(self,elem):
        """
        adds elem to the self.nvDatas list and sets elem.parent to self (the port interface)
        """
        if not isinstance(elem, DataElement):
            raise ValueError("expected elem variable to be of type DataElement")
        self.nvDatas.append(elem)
        elem.parent=self
