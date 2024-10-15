from enum import Enum
import itertools
from types import MappingProxyType
import autosar.base

class Element:
    def __init__(self, name, parent = None, adminData = None, category = None, uuid = None):
        if isinstance(adminData, dict):
            adminDataObj=autosar.base.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or autosar.base.AdminData")
        self.name=name
        self.adminData=adminDataObj
        self.parent=parent
        self.category=category
        self.uuid=uuid

    @property
    def ref(self):
        if self.parent is not None:
            return self.parent.ref+'/%s'%self.name
        else:
            return None

    def rootWS(self):
        if self.parent is None:
            return None
        else:
            return self.parent.rootWS()

    def __deepcopy__(self,memo):
        raise NotImplementedError(type(self))

class LabelElement:
    """Same as Element but uses label as main identifier instead of name"""
    def __init__(self, label, parent = None, adminData = None, category = None):
        if isinstance(adminData, dict):
            adminDataObj=autosar.base.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or autosar.base.AdminData")
        self.label=label
        self.adminData=adminDataObj
        self.parent=parent
        self.category=category

    @property
    def ref(self):
        if self.parent is not None:
            return self.parent.ref+'/%s'%self.label
        else:
            return None

    def rootWS(self):
        if self.parent is None:
            return None
        else:
            return self.parent.rootWS()


class AutosarDataPrototype(Element):
    class Role(Enum):
        Variable='VARIABLE-DATA-PROTOTYPE'
        Parameter='PARAMETER-DATA-PROTOTYPE'
        Argument='ARGUMENT-DATA-PROTOTYPE'

    class _AR3SpecificRole(Enum):
        DataElement='DATA-ELEMENT-PROTOTYPE'
        CalprmElement='CALPRM-ELEMENT-PROTOTYPE'
    
    _AR4_TO_AR3_ROLE_MAP = MappingProxyType({
        Role.Variable: _AR3SpecificRole.DataElement,
        Role.Parameter: _AR3SpecificRole.CalprmElement,
        Role.Argument: Role.Argument
    })

    TAG_TO_ROLE_MAP = MappingProxyType({
        member.value: member
        for member in itertools.chain(Role.__members__.values(), _AR3SpecificRole.__members__.values())
    })

    def tag(self,version):
        return self.role if version >= 4.0 else AutosarDataPrototype._AR4_TO_AR3_ROLE_MAP[self.role]

    def __init__(

        self,
        role: Role,
        name,
        typeRef,
        isQueued=False,
        initValue=None,
        initValueRef=None,
        swAddressMethodRef=None,
        swCalibrationAccess=None,
        swImplPolicy = None,
        category = None,
        parent=None,
        adminData=None
    ):
        super().__init__(name, parent, adminData, category)
        self.role = role
        if isinstance(typeRef,str):
            self.typeRef=typeRef
        elif hasattr(typeRef,'ref'):
            assert(isinstance(typeRef.ref,str))
            self.typeRef=typeRef.ref
        else:
            raise ValueError("unsupported type for argument: typeRef")
        assert(isinstance(isQueued,bool))
        self.swImplPolicy = swImplPolicy
        self.isQueued = isQueued
        self.initValue = initValue
        self.initValueRef = initValueRef
        self.swAddressMethodRef = swAddressMethodRef
        self.swCalibrationAccess = swCalibrationAccess
        self.dataConstraintRef = None
        if self.swImplPolicy is None and self.isQueued:
            self.swImplPolicy = "QUEUED"

    @property
    def swImplPolicy(self):
        return self._swImplPolicy

    @swImplPolicy.setter
    def swImplPolicy(self, value):
        if value is None:
            self._swImplPolicy=None
        else:
            ucvalue=str(value).upper()
            enum_values = ["CONST", "FIXED", "MEASUREMENT-POINT", "QUEUED", "STANDARD"]
            if ucvalue in enum_values:
                self._swImplPolicy = ucvalue
                if ucvalue == 'QUEUED':
                    self.isQueued = True
            else:
                raise ValueError('invalid swImplPolicy value: ' +  value)

    def setProps(self, props):
        if isinstance(props, autosar.base.SwDataDefPropsConditional):
            self.swCalibrationAccess=props.swCalibrationAccess
            self.swAddressMethodRef = props.swAddressMethodRef
            self.swImplPolicy = props.swImplPolicy
            self.dataConstraintRef = props.dataConstraintRef
        else:
            raise NotImplementedError(type(props))

class SoftwareAddressMethod(Element):
    """
    Represents <SW-ADDR-METHOD> (AUTOSAR 3) (AUTOSAR 4)
    """
    def __init__(self, name, parent=None, adminData=None):
        super().__init__(name, parent, adminData)

    def tag(self, version = None): # pylint: disable=unused-argument
        return 'SW-ADDR-METHOD'
