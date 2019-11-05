import xml.etree.ElementTree as ElementTree
import autosar.base

class Element:
    def __init__(self, name, parent = None, adminData = None, category = None):
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

class DataElement(Element):
    def tag(self,version): return "VARIABLE-DATA-PROTOTYPE" if version >= 4.0 else "DATA-ELEMENT-PROTOTYPE"
    def __init__(self, name, typeRef, isQueued=False, swAddressMethodRef=None, swCalibrationAccess=None, swImplPolicy = None, category = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData, category)
        if isinstance(typeRef,str):
            self.typeRef=typeRef
        elif hasattr(typeRef,'ref'):
            assert(isinstance(typeRef.ref,str))
            self.typeRef=typeRef.ref
        else:
            raise ValueError("unsupported type for argument: typeRef")
        assert(isinstance(isQueued,bool))
        self.isQueued=isQueued
        self.swAddressMethodRef = swAddressMethodRef
        self.swCalibrationAccess = swCalibrationAccess
        self.swImplPolicy = swImplPolicy
        self.dataConstraintRef = None

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

    def setProps(self, variant):
        if isinstance(variant, autosar.base.SwDataDefPropsConditional):
            self.swCalibrationAccess=variant.swCalibrationAccess
            self.swAddressMethodRef = variant.swAddressMethodRef
            self.swImplPolicy = variant.swImplPolicy
            self.dataConstraintRef = variant.dataConstraintRef
        else:
            raise NotImplementedError(type(variant))
