import autosar.component
import autosar.behavior
import autosar.element
import autosar.portinterface
import autosar.datatype
import autosar.mode
import autosar.builder
import copy
import autosar.base
import re
from fractions import Fraction
import collections
import decimal
import sys

_supress_warnings = True

class Package(object):
    packageName = None
    def __init__(self, name, parent=None, role=None):
        self.name = name
        self.elements = []
        self.subPackages = []
        self.parent=parent
        self.role=role
        self.map={'elements':{}, 'packages':{}}
        self.unhandledParser = set() #[PackageParser] unhandled
        self.unhandledWriter =set() #[PackageWriter] Unhandled

    def __getitem__(self,key):
        if isinstance(key,str):
            return self.find(key)
        else:
            raise ValueError('expected string')

    @property
    def ref(self):
        if self.parent is not None:
            return self.parent.ref+'/%s'%self.name
        else:
            return None

    def find(self,ref):
        if ref.startswith('/'): return self.parent.find(ref)
        ref = ref.partition('/')
        name = ref[0]
        if name in self.map['packages']:
            package=self.map['packages'][name]
            if len(ref[2])>0:
                return package.find(ref[2])
            else:
                return package
        if name in self.map['elements']:
            elem=self.map['elements'][name]
            if len(ref[2])>0:
                return elem.find(ref[2])
            else:
                return elem
        return None

    def findall(self,ref):
        """
        experimental find-method that has some rudimentary support for globs.
        """
        if ref is None: return None
        if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
        ref = ref.partition('/')
        if ref[0]=='*' and len(ref[2])==0:
            result=list(self.elements)
            result.extend(self.subPackages)
        else:
            result=[]
            for item in (self.elements+self.subPackages):
                if item.name == ref[0] or ref[0]=='*':
                    if len(ref[2])>0:
                        result.extend(item.findall(ref[2]))
                    else:
                        result.append(item)
            if (len(result)==0) and ('*' in ref[0]):
                p = re.compile(ref[0].replace('*','.*'))
                for item in (self.elements+self.subPackages):
                    m = p.match(item.name)
                    if m is not None:
                        if len(ref[2])>0:
                            result.extend(item.findall(ref[2]))
                        else:
                            result.append(item)
        return result

    def dir(self,ref=None,_prefix=''):
        if ref==None:
            return [_prefix+x.name for x in self.subPackages]+[_prefix+x.name for x in self.elements]
        else:
            ref = ref.partition('/')
            result=self.find(ref[0])
            if result is not None:
                return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
            else:
                return None

    def delete(self, ref):
        if ref is None: return
        if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
        ref = ref.partition('/')
        for i,element in enumerate(self.elements):
            if element.name == ref[0]:
                if len(ref[2])>0:
                    return element.delete(ref[2])
                else:
                    del self.elements[i]
                    del self.map['elements'][ref[0]]
                    break

    def createSenderReceiverInterface(self, name, dataElements=None, modeGroups=None, isService=False, serviceKind = None, adminData=None):
        """
        creates a new sender-receiver port interface. dataElements can either be a single instance of DataElement or a list of DataElements.
        The same applies to modeGroups. isService must be boolean
        """

        ws = self.rootWS()
        assert(ws is not None)

        portInterface = autosar.portinterface.SenderReceiverInterface(str(name), isService, adminData=adminData)
        if dataElements is not None:
            if isinstance(dataElements,collections.abc.Iterable):
                for elem in dataElements:
                    dataType=ws.find(elem.typeRef, role='DataType')
                    if dataType is None:
                        raise ValueError('invalid type reference: '+elem.typeRef)
                    elem.typeRef=dataType.ref #normalize reference to data element
                    portInterface.append(elem)
            elif isinstance(dataElements,autosar.portinterface.DataElement):
                dataType=ws.find(dataElements.typeRef, role='DataType')
                if dataType is None:
                    raise ValueError('invalid type reference: '+dataElements.typeRef)
                dataElements.typeRef=dataType.ref #normalize reference to data element
                portInterface.append(dataElements)
            else:
                raise ValueError("dataElements: expected autosar.portinterface.DataElement instance or list")
        if modeGroups is not None:
            if isinstance(modeGroups,collections.abc.Iterable):
                for elem in modeGroups:
                    portInterface.append(elem)
            elif isinstance(modeGroups,autosar.mode.ModeGroup):
                portInterface.append(modeGroups)
            else:
                raise ValueError("dataElements: expected autosar.portinterface.DataElement instance or list")
        self.append(portInterface)
        return portInterface

    def createParameterInterface(self, name, parameters=None, modeDeclarationGroups=None, isService=False, adminData=None):
        """
        Creates a new parameter port interface. parameter can either be a single instance of Parameter or a list of Parameters.
        The same applies to modeDeclarationGroups. isService must be boolean.
        In a previous version of this function the class DataElement was used instead of Parameter.
        In order to be backward compatible with old code, this method converts from old to new datatype internally
        """
        ws = self.rootWS()
        assert(ws is not None)

        if isinstance(adminData, dict):
            adminDataObj=ws.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or AdminData")
        portInterface = autosar.portinterface.ParameterInterface(str(name), adminData=adminDataObj)
        if parameters is not None:
            if isinstance(parameters,collections.abc.Iterable):
                for elem in parameters:
                    dataType=ws.find(elem.typeRef, role='DataType')
                    #normalize reference to data element
                    if dataType is None:
                        raise ValueError('invalid type reference: '+elem.typeRef)
                    elem.typeRef=dataType.ref
                    if isinstance(autosar.portinterface.DataElement):
                        #convert into Parameter
                        parameter = autosar.element.ParameterDataPrototype(elem.name, elem.typeRef, elem.swAddressMethodRef, adminData=elem.adminData)
                    else:
                        parameter = elem
                    portInterface.append(parameter)
            elif isinstance(parameters, autosar.portinterface.DataElement):
                dataType=ws.find(parameters.typeRef, role='DataType')
                #normalize reference to data element
                if dataType is None:
                    raise ValueError('invalid type reference: '+parameters.typeRef)
                parameters.typeRef=dataType.ref
                parameter = autosar.element.ParameterDataPrototype(parameters.name, parameters.typeRef,
                                                            parameters.swAddressMethodRef, adminData=parameters.adminData)
                portInterface.append(parameter)
            elif isinstance(parameters, autosar.element.ParameterDataPrototype):
                dataType=ws.find(parameters.typeRef, role='DataType')
                #normalize reference to data element
                if dataType is None:
                    raise ValueError('invalid type reference: '+parameters.typeRef)
                parameters.typeRef=dataType.ref
                portInterface.append(parameters)
            else:
                raise ValueError("parameters: Expected instance of autosar.element.ParameterDataPrototype or list")
        self.append(portInterface)
        return portInterface

    def createModeSwitchInterface(self, name, modeGroup = None, isService=False, adminData=None):
        portInterface = autosar.portinterface.ModeSwitchInterface(name, isService, self, adminData)
        if modeGroup is not None:
            if isinstance(modeGroup, autosar.mode.ModeGroup):
                ws = self.rootWS()
                assert (ws is not None)
                modeDeclarationGroup = ws.find(modeGroup.typeRef, role='ModeDclrGroup')
                if modeDeclarationGroup is None:
                    raise ValueError('invalid type reference: '+modeGroup.typeRef)
                modeGroup.typeRef=modeDeclarationGroup.ref #normalize reference string
                portInterface.modeGroup = modeGroup
                modeGroup.parent = portInterface
            else:
                raise ValueError('modeGroup must be an instance of autosar.mode.ModeGroup or None')
        self.append(portInterface)
        return portInterface

    def createNvDataInterface(self, name, nvDatas=None, isService=False, serviceKind = None, adminData=None):
        """
        creates a new nv-data port interface. nvDatas can either be a single instance of DataElement or a list of DataElements.
        isService must be boolean
        """

        ws = self.rootWS()
        assert(ws is not None)

        portInterface = autosar.portinterface.NvDataInterface(str(name), isService=isService, serviceKind=serviceKind, adminData=adminData)
        if nvDatas is not None:
            if isinstance(nvDatas,collections.abc.Iterable):
                for elem in nvDatas:
                    dataType=ws.find(elem.typeRef, role='DataType')
                    if dataType is None:
                        raise ValueError('invalid type reference: '+elem.typeRef)
                    elem.typeRef=dataType.ref #normalize reference to data element
                    portInterface.append(elem)
            elif isinstance(nvDatas,autosar.portinterface.DataElement):
                dataType=ws.find(nvDatas.typeRef, role='DataType')
                if dataType is None:
                    raise ValueError('invalid type reference: '+nvDatas.typeRef)
                nvDatas.typeRef=dataType.ref #normalize reference to data element
                portInterface.append(nvDatas)
            else:
                raise ValueError("dataElements: expected autosar.portinterface.DataElement instance or list")
        self.append(portInterface)
        return portInterface

    def createSubPackage(self, name, role=None):
        pkg = Package(name)
        self.append(pkg)
        if role is not None:
            ws = self.rootWS()
            assert(ws is not None)
            ws.setRole(pkg.ref, role)
        return pkg

    def rootWS(self):
        if self.parent is None:
            return None
        else:
            return self.parent.rootWS()

    def append(self,elem):
        """appends elem to the self.elements list"""
        isNewElement = True
        if elem.name in self.map['elements']:
            isNewElement = False
            existingElem = self.map['elements'][elem.name]
            if type(elem) != type(existingElem):
                raise TypeError('Error: element %s %s already exists in package %s with different type from new element %s'%(str(type(existingElem)), existingElem.name, self.name, str(type(elem))))
            else:
                if elem != existingElem:
                    raise ValueError('Error: element %s %s already exist in package %s using different definition'%(existingElem.name, str(type(existingElem)), self.name))
        if isNewElement:
            if isinstance(elem,autosar.element.Element):
                self.elements.append(elem)
                elem.parent=self
                self.map['elements'][elem.name]=elem
            elif isinstance(elem,Package):
                self.subPackages.append(elem)
                elem.parent=self
                self.map['packages'][elem.name]=elem
            else:
                raise ValueError('unexpected value type %s'%str(type(elem)))

    def update(self,other):
        """copies/clones each element from other into self.elements"""
        if type(self) == type(other):
            for otherElem in other.elements:
                newElem=copy.deepcopy(otherElem)
                assert(newElem is not None)
                try:
                    i=self.index('elements',otherElem.name)
                    oldElem=self.elements[i]
                    self.elements[i]=newElem
                    oldElem.parent=None
                except ValueError:
                    self.elements.append(newElem)
                newElem.parent=self
        else:
            raise ValueError('cannot update from object of different type')

    def index(self,container,name):
        if container=='elements':
            lst=self.elements
        elif container=='subPackages':
            lst=self.subPackages
        else:
            raise KeyError("%s not in %s"%(container,self.__class__.__name__))
        return autosar.base.indexByName(lst,name)


    def createApplicationSoftwareComponent(self, swcName, behaviorName=None, implementationName=None, multipleInstance=False, autoCreatePortAPIOptions=True):
        """
        Creates a new ApplicationSoftwareComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.

        """
        ws = self.rootWS()
        assert(ws is not None)
        swc = autosar.component.ApplicationSoftwareComponent(swcName,self)
        self.append(swc)
        self._createInternalBehavior(ws, swc, behaviorName, multipleInstance, autoCreatePortAPIOptions)
        self._createImplementation(swc, implementationName)
        return swc

    def createServiceComponent(self, swcName, behaviorName=None, implementationName=None, multipleInstance=False, autoCreatePortAPIOptions=True):
        """
        Creates a new ApplicationSoftwareComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.
        """
        ws = self.rootWS()
        assert(ws is not None)

        swc = autosar.component.ServiceComponent(swcName,self)
        self.append(swc)
        self._createInternalBehavior(ws, swc, behaviorName, multipleInstance, autoCreatePortAPIOptions)
        self._createImplementation(swc, implementationName)
        return swc

    def createComplexDeviceDriverComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False, autoCreatePortAPIOptions=True):
        ws = self.rootWS()
        assert(ws is not None)
        swc=autosar.component.ComplexDeviceDriverComponent(swcName, parent=self)
        self.append(swc)
        self._createInternalBehavior(ws, swc, behaviorName, multipleInstance, autoCreatePortAPIOptions)
        self._createImplementation(swc, implementationName)
        return swc

    def createNvBlockComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False, autoCreatePortAPIOptions=False):
        """
        Creates a new NvBlockComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.

        """
        ws = self.rootWS()
        assert(ws is not None)
        swc = autosar.component.NvBlockComponent(swcName,self)
        self.append(swc)
        self._createInternalBehavior(ws, swc, behaviorName, multipleInstance, autoCreatePortAPIOptions)
        self._createImplementation(swc, implementationName)
        return swc

    def createCompositionComponent(self, componentName, adminData=None):
        component = autosar.component.CompositionComponent(str(componentName), self)
        self.append(component)
        return component

    def _createInternalBehavior(self, ws, swc, behaviorName, multipleInstance, autoCreatePortAPIOptions):
        """
        Initializes swc.behavior object
        For AUTOSAR3, an instance of InternalBehavior is created
        For AUTOSAR4, an instance of SwcInternalBehavior is created
        """
        if behaviorName is None:
            behaviorName = swc.name+'_InternalBehavior'
        if ws.version < 4.0:
            # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
            internalBehavior = autosar.behavior.InternalBehavior(behaviorName,swc.ref,multipleInstance,self)
        else:
            # In AUTOSAR 4.x the internal behavior is a sub-element of the swc.
            internalBehavior = autosar.behavior.SwcInternalBehavior(behaviorName,swc.ref,multipleInstance, swc)
        internalBehavior.autoCreatePortAPIOptions=autoCreatePortAPIOptions
        swc.behavior=internalBehavior
        if ws.version < 4.0:
            # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
            self.append(internalBehavior)

    def _createImplementation(self, swc, implementationName):

        if implementationName is None:
            implementationName = swc.name+'_Implementation'
        swc.implementation = autosar.component.SwcImplementation(implementationName, swc.behavior.ref, parent=self)

        self.append(swc.implementation)


    def createModeDeclarationGroup(self, name, modeDeclarations = None, initialMode = None, category=None, adminData=None):
        """
        creates an instance of autosar.portinterface.ModeDeclarationGroup
        name: name of the ModeDeclarationGroup
        modeDeclarations: list of strings where each string is a mode name. It can also be a list of tuples of type (int, str).
        initialMode: string with name of the initial mode (must be one of the strings in modeDeclarations list)
        category: optional category string
        adminData: optional adminData object (use ws.createAdminData() as constructor)
        """
        ws = self.rootWS()
        assert(ws is not None)
        if isinstance(adminData, dict):
            adminDataObj=ws.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or AdminData")
        group = autosar.mode.ModeDeclarationGroup(name, None, None, category, self,adminDataObj)
        if modeDeclarations is not None:
            for declaration in modeDeclarations:
                if isinstance(declaration, str):
                    declarationName = declaration
                    item=autosar.mode.ModeDeclaration(declarationName, parent = group)
                elif isinstance(declaration, tuple):
                    declarationValue = declaration[0]
                    declarationName = declaration[1]
                    assert(isinstance(declarationValue, int))
                    assert(isinstance(declarationName, str))
                    item=autosar.mode.ModeDeclaration(declarationName, declarationValue, group)
                else:
                    raise NotImplementedError(type(declaration))
                group.modeDeclarations.append(item)
                if (initialMode is not None) and (declarationName == initialMode):
                    group.initialModeRef = item.ref
            if (initialMode is not None) and (group.initialModeRef is None):
                raise ValueError('initalMode "%s" not a valid modeDeclaration name'%initialMode)
            self.append(group)
        return group

    def createClientServerInterface(self, name, operations, errors=None, isService=False, serviceKind=None, adminData=None):
        """
        creates a new client server interface in current package
        name: name of the interface (string)
        operations: names of the operations in the interface (list of strings)
        errors: Possible errors that can be returned. Can be a single instance of ApplicationError or a list of ApplicationError
        isService: True if this interface is a service interface (bool)
        adminData: optional admindata (dict or autosar.base.AdminData object)
        """
        portInterface = autosar.portinterface.ClientServerInterface(name, isService, serviceKind, self, adminData)
        for name in operations:
            portInterface.append(autosar.portinterface.Operation(name))
        if errors is not None:
            if isinstance(errors, collections.abc.Iterable):
                for error in errors:
                    portInterface.append(error)
            else:
                assert( isinstance(errors, autosar.portinterface.ApplicationError))
                portInterface.append(errors)
        self.append(portInterface)
        return portInterface

    def createSoftwareAddressMethod(self, name):
        item = autosar.element.SoftwareAddressMethod(name)
        self.append(item)
        return item

    def createArrayDataType(self, name, typeRef, arraySize, elementName=None, adminData=None):
        """
        AUTOSAR3:
           Creates an ArrayDataType and adds it to current package
        """
        ws = self.rootWS()
        assert(ws is not None)
        if ws.version >= 4.0:
            raise RuntimeError("This method is only valid in AUTOSAR3")
        else:
            if typeRef.startswith('/'):
                dataType = ws.find(typeRef)
            else:
                dataType = ws.find(typeRef, role='DataType')
            if dataType is None:
                raise autosar.base.InvalidDataTypeRef(typeRef)
            newType = autosar.datatype.ArrayDataType(name, typeRef, arraySize, adminData)
            self.append(newType)
            return newType

    def createIntegerDataType(self, name, min=None, max=None, valueTable=None, offset=None, scaling=None, unit=None, baseTypeRef=None, adminData=None, swCalibrationAccess='NOT-ACCESSIBLE', typeEmitter=None, forceFloatScaling=False, dataConstraint=''):
        """
        AUTOSAR3:
        Helper method for creating integer datatypes in a package.
        In order to use this function you must have a subpackage present with role='CompuMethod'.

        AUTOSAR4:
        Helper method for creating implementation datatypes or application datatypes.
        """
        ws=self.rootWS()
        assert(ws is not None)
        if ws.version >= 4.0:
            raise RuntimeError("This method is only valid in AUTOSAR3")
        else:
            compuMethodRef = self._createCompuMethodAndUnitV3(ws, name, min, max, valueTable, None, offset, scaling, unit, forceFloatScaling)
            lowerLimit, upperLimit = min, max
            if compuMethodRef is not None:
                compuMethod = ws.find(compuMethodRef)
                if lowerLimit is None:
                    lowerLimit = compuMethod.intToPhys.lowerLimit
                if upperLimit is None:
                    upperLimit = compuMethod.intToPhys.upperLimit
            newType=autosar.datatype.IntegerDataType(name, lowerLimit, upperLimit, compuMethodRef=compuMethodRef, adminData=adminData)
            assert(newType is not None)
            self.append(newType)
            return newType

    def createRealDataType(self, name, minVal, maxVal, minValType='CLOSED', maxValType='CLOSED', hasNaN=False, encoding='SINGLE', baseTypeRef=None, typeEmitter=None, adminData=None):
        """
        AUTOSAR 4: Creates a new ImplementationDataType
        AUTOSAR 3: Creates a new instance of autosar.datatype.RealDataType and appends it to current package
        """
        ws=self.rootWS()
        assert(ws is not None)
        if ws.version >= 4.0:
            if baseTypeRef is None:
                raise ValueError('baseTypeRef argument must be given to this method')
            if (minVal == '-INFINITE' or minVal == 'INFINITE'): minVal = '-INF'
            if (maxVal == 'INFINITE'): maxVal = 'INF'
            if minVal == '-INF' and minValType == 'CLOSED':
                minValType = 'OPEN' #automatic correction
            if maxVal == 'INF' and maxValType == 'CLOSED':
                maxValType = 'OPEN' #automatic correction
            dataConstraint = self.createInternalDataConstraint(name+'_DataConstr', minVal, maxVal, minValType, maxValType)
            newType = autosar.datatype.ImplementationDataType(name, 'VALUE', typeEmitter=typeEmitter)
            props = autosar.base.SwDataDefPropsConditional(baseTypeRef=baseTypeRef,
                                                               swCalibrationAccess='NOT-ACCESSIBLE',
                                                               dataConstraintRef=dataConstraint.ref)
            newType.variantProps = [props]
        else:
            if ( (minVal == '-INFINITE') or (minVal == '-INF') or (minVal == 'INFINITE') or (minVal == 'INF') ):
                #automatic correction
                minVal = None
                minValType = 'INFINITE'
            if ( (maxVal == 'INF') or (maxVal == 'INFINITE') ):
                #automatic correction
                maxVal = None
                maxValType = 'INFINITE'
            newType=autosar.datatype.RealDataType(name, minVal, maxVal, minValType, maxValType, hasNaN, encoding, self, adminData)
        self.append(newType)
        return newType

    def createRecordDataType(self, name, elements, adminData=None):
        """
        AUTOSAR3: Create a new instance of RecordDataType and appends it to current package
        """
        ws = self.rootWS()
        assert(ws is not None)
        if ws.version >= 4.0:
            raise RuntimeError("This method is only for AUTOSAR3")
        else:
            processed = []
            for elem in elements:
                elemUnitRef = None
                if isinstance(elem, autosar.datatype.RecordTypeElement):
                    processed.append(elem)
                elif isinstance(elem, tuple):
                    elemName = elem[0]
                    elemUnitRef = elem[1]
                elif isinstance(elem, collections.abc.Mapping):
                    elemName = elem['name']
                    elemUnitRef = elem['typeRef']
                else:
                    raise ValueError('element must be either Mapping, RecordTypeElement or tuple')
                if elemUnitRef is not None:
                    if elemUnitRef.startswith('/'):
                        dataType = ws.find(elemUnitRef)
                    else:
                        dataType = ws.find(elemUnitRef, role='DataType')
                    if dataType is None:
                        raise autosar.base.InvalidDataTypeRef(elemUnitRef)
                    elem = autosar.datatype.RecordTypeElement(elemName, dataType.ref)
                    processed.append(elem)
            dataType = autosar.datatype.RecordDataType(name, processed, self, adminData)
            self.append(dataType)
            return dataType

    def createStringDataType(self, name, length, encoding='ISO-8859-1', adminData=None):
        """
        create a new instance of autosar.datatype.StringDataType and appends it to current package
        """
        dataType=autosar.datatype.StringDataType(name, length, encoding, self, adminData)
        self.append(dataType)
        return dataType

    def createBooleanDataType(self, name, adminData=None):
        """
        create a new instance of autosar.datatype.BooleanDataType and appends it to current package
        """
        dataType=autosar.datatype.BooleanDataType(name, self, adminData)
        self.append(dataType)
        return dataType

    def createConstant(self, name, typeRef, initValue, label = '', adminData=None):
        """
        create a new instance of autosar.constant.Constant and appends it to the current package
        """
        ws=self.rootWS()
        assert(ws is not None)
        if typeRef is not None:
            dataType = ws.find(typeRef, role='DataType')
            if dataType is None:
                raise autosar.base.InvalidDataTypeRef(str(typeRef))
        else:
            if ws.version < 4.0:
                raise ValueError('typeRef argument cannot be None')
            else:
                dataType = None
        if ws.version < 4.0:
            return self._createConstantV3(ws, name, dataType, initValue, adminData)
        else:
            return self._createConstantV4(ws, name, dataType, initValue, label, adminData)

    def _createConstantV3(self, ws, name, dataType, initValue, adminData=None):
        """Creates an AUTOSAR 3 Constant"""
        if isinstance(dataType, autosar.datatype.IntegerDataType):
            if not isinstance(initValue, int):
                raise ValueError('initValue: expected type int, got '+str(type(initValue)))
            value=autosar.constant.IntegerValue(name, dataType.ref, initValue)
        elif isinstance(dataType, autosar.datatype.RecordDataType):
            if isinstance(initValue, collections.abc.Mapping) or isinstance(initValue, collections.abc.Iterable):
                pass
            else:
                raise ValueError('initValue: expected type Mapping or Iterable, got '+str(type(initValue)))
            value=self._createRecordValueV3(ws, name, dataType, initValue)
        elif isinstance(dataType, autosar.datatype.ArrayDataType):
            if isinstance(initValue, collections.abc.Iterable):
                pass
            else:
                raise ValueError('initValue: expected type Iterable, got '+str(type(initValue)))
            value=self._createArrayValueV3(ws, name, dataType, initValue)
        elif isinstance(dataType, autosar.datatype.BooleanDataType):
            if isinstance(initValue, bool):
                pass
            elif isinstance(initValue, str) or isinstance(initValue, int):
                initValue=bool(initValue)
            else:
                raise ValueError('initValue: expected type bool or str, got '+str(type(initValue)))
            value=autosar.constant.BooleanValue(name, dataType.ref, initValue)
        elif isinstance(dataType, autosar.datatype.StringDataType):
            if isinstance(initValue, str):
                pass
            else:
                raise ValueError('initValue: expected type str, got '+str(type(initValue)))
            value=autosar.constant.StringValue(name, dataType.ref, initValue)
        elif isinstance(dataType, autosar.datatype.RealDataType):
            if isinstance(initValue, float) or isinstance(initValue, decimal.Decimal) or isinstance(initValue, int):
                pass
            else:
                raise ValueError('initValue: expected type int, float or Decimal, got '+str(type(initValue)))
            raise NotImplementedError("Creating constants from RealDataType not implemented")
        else:
            raise ValueError('unrecognized type: '+str(type(dataType)))
        assert(value is not None)
        constant = autosar.constant.Constant(name, value, adminData=adminData)
        self.append(constant)
        return constant

    def _createRecordValueV3(self, ws, name, dataType, initValue, parent=None):
        value = autosar.constant.RecordValue(name, dataType.ref, parent = parent)
        if isinstance(initValue, collections.abc.Mapping):
            for elem in dataType.elements:
                if elem.name in initValue:
                    v = initValue[elem.name]
                    childType = ws.find(elem.typeRef, role='DataType')
                    if childType is None:
                        raise ValueError('invalid reference: '+str(elem.typeRef))
                    if isinstance(childType, autosar.datatype.IntegerDataType):
                        if not isinstance(v, int):
                            raise ValueError('v: expected type int, got '+str(type(v)))
                        value.elements.append(autosar.constant.IntegerValue(elem.name, childType.ref, v, value))
                    elif isinstance(childType, autosar.datatype.RecordDataType):
                        if isinstance(v, collections.abc.Mapping) or isinstance(v, collections.abc.Iterable):
                            pass
                        else:
                            raise ValueError('v: expected type Mapping or Iterable, got '+str(type(v)))
                        value.elements.append(self._createRecordValueV3(ws, elem.name, childType, v, value))
                    elif isinstance(childType, autosar.datatype.ArrayDataType):
                        if isinstance(v, collections.abc.Iterable):
                            pass
                        else:
                            raise ValueError('v: expected type Iterable, got '+str(type(v)))
                        value.elements.append(self._createArrayValueV3(ws, elem.name, childType, v, value))
                    elif isinstance(childType, autosar.datatype.BooleanDataType):
                        if isinstance(v, bool):
                            pass
                        elif isinstance(v, str) or isinstance(v, int):
                            v=bool(v)
                        else:
                            raise ValueError('v: expected type bool or str, got '+str(type(v)))
                        value.elements.append(autosar.constant.BooleanValue(elem.name, childType.ref, v, value))
                    elif isinstance(childType, autosar.datatype.StringDataType):
                        if isinstance(v, str):
                            pass
                        else:
                            raise ValueError('v: expected type str, got '+str(type(v)))
                        value.elements.append(autosar.constant.StringValue(elem.name, childType.ref, v, value))
                    elif isinstance(childType, autosar.datatype.RealDataType):
                        if isinstance(v, float) or isinstance(v, decimal.Decimal) or isinstance(v, int):
                            pass
                        else:
                            raise ValueError('v: expected type int, float or Decimal, got '+str(type(v)))
                        raise NotImplementedError("Creating constants from RealDataType not implemented")
                    else:
                        raise ValueError('unrecognized type: '+str(type(childType)))
                else:
                    raise ValueError('%s: missing initValue field: %s'%(name, elem.name))
        else:
            raise NotImplementedError(type(initValue))
        return value


    def _createArrayValueV3(self, ws, name, dataType, initValue, parent=None):
        value = autosar.constant.ArrayValue(name, dataType.ref, parent=parent)
        childType = ws.find(dataType.typeRef, role='DataType')
        if childType is None:
            raise ValueError('invalid reference: '+str(dataType.typeRef))
        if isinstance(initValue, collections.abc.Iterable):
            for i in range(dataType.length):
                try:
                    v=initValue[i]
                except IndexError:
                    raise ValueError('%s: too few elements in initValue, expected %d items, got %d'%(name, int(dataType.length), len(initValue)))
                elemName='%s_%d'%(childType.name,i)
                if isinstance(childType, autosar.datatype.IntegerDataType):
                    if not isinstance(v, int):
                        raise ValueError('v: expected type int, got '+str(type(v)))
                    value.elements.append(autosar.constant.IntegerValue(elemName, childType.ref, v, value))
                elif isinstance(childType, autosar.datatype.RecordDataType):
                    if isinstance(v, collections.abc.Mapping) or isinstance(v, collections.abc.Iterable):
                        value.elements.append(self._createRecordValueV3(ws, elemName, childType, v, value))
                    else:
                        raise ValueError('v: expected type Mapping or Iterable, got '+str(type(v)))
                elif isinstance(childType, autosar.datatype.ArrayDataType):
                    if isinstance(v, collections.abc.Iterable):
                        pass
                    else:
                        raise ValueError('v: expected type Iterable, got '+str(type(v)))
                    value.elements.append(self._createArrayValueV3(ws, elemName, childType, v, value))
                elif isinstance(childType, autosar.datatype.BooleanDataType):
                    if isinstance(v, bool):
                        pass
                    elif isinstance(v, str) or isinstance(v, int):
                        v=bool(v)
                    else:
                        raise ValueError('v: expected type bool or str, got '+str(type(v)))
                    value.elements.append(autosar.constant.BooleanValue(elemName, childType.ref, v, value))
                elif isinstance(childType, autosar.datatype.StringDataType):
                    if isinstance(v, str):
                        pass
                    else:
                        raise ValueError('v: expected type str, got '+str(type(v)))
                    value.elements.append(autosar.constant.StringValue(elemName, childType.ref, v, value))
                elif isinstance(childType, autosar.datatype.RealDataType):
                    if isinstance(v, float) or isinstance(v, decimal.Decimal) or isinstance(v, int):
                        pass
                    else:
                        raise ValueError('v: expected type int, float or Decimal, got '+str(type(v)))
                    raise NotImplementedError("Creating constants from RealDataType not implemented")
                else:
                    raise ValueError('unrecognized type: '+str(type(childType)))
        else:
            raise NotImplementedError(type(initValue))
        return value

    def _createConstantV4(self, ws, name, dataType, initValue, label, adminData=None):
        """
        If label argument is an empty string, the label of the created value is the same as
        the name of the constant.
        """
        if isinstance(label, str) and len(label) == 0:
            label = name
        builder = autosar.builder.ValueBuilder()
        if dataType is None:
            value = builder.build(label, initValue)
        else:
            value = builder.buildFromDataType(dataType, initValue, label, ws)
        assert(value is not None)
        constant = autosar.constant.Constant(name, value, parent=self, adminData=adminData)
        self.append(constant)
        return constant


    def createTextValueConstant(self, name, value):
        """AUTOSAR 4 text value constant"""
        constant = autosar.constant.Constant(name, None, self)
        constant.value = autosar.constant.TextValue(name, value, constant)
        self.append(constant)
        return constant

    def createNumericalValueConstant(self, name, value):
        """AUTOSAR 4 numerical value constant"""
        constant = autosar.constant.Constant(name, None, self)
        constant.value = autosar.constant.NumericalValue(name, value, constant)
        self.append(constant)
        return constant

    def createApplicationValueConstant(self, name, swValueCont = None, swAxisCont = None, valueCategory = None, valueLabel = None):
        """
        (AUTOSAR4)
        Creates a new Constant containing a application value specification
        """
        ws=self.rootWS()
        assert(ws is not None)
        constant = autosar.constant.Constant(name, None, self)
        innerValue = autosar.constant.ApplicationValue(valueLabel, swValueCont, swAxisCont, valueCategory, parent = self)
        constant.value = innerValue
        self.append(constant)
        return constant

    def createConstantFromValue(self, name, value):
        """
        (AUTOSAR4)
        Wraps an already created value in a constant object
        """
        if not isinstance(value, autosar.constant.ValueAR4):
            raise ValueError("value argument must inherit from class ValueAR4 (got {})".format(type(value)))
        ws=self.rootWS()
        assert(ws is not None)
        constant = autosar.constant.Constant(name, value, self)
        self.append(constant)
        return constant



    def createInternalDataConstraint(self, name, lowerLimit, upperLimit, lowerLimitType="CLOSED", upperLimitType="CLOSED", adminData = None):
        ws=self.rootWS()
        assert(ws is not None)
        return self._checkAndCreateDataConstraint(ws, name, 'internalConstraint', lowerLimit, upperLimit, lowerLimitType, upperLimitType, adminData)

    def createPhysicalDataConstraint(self, name, lowerLimit, upperLimit, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', adminData = None):
        ws=self.rootWS()
        assert(ws is not None)
        return self._checkAndCreateDataConstraint(ws, name, 'physicalConstraint', lowerLimit, upperLimit, lowerLimitType, upperLimitType, adminData)


    def createSwBaseType(self, name, size=None, encoding=None, nativeDeclaration=None, category='FIXED_LENGTH', adminData=None):
        """
        Creates a SwBaseType object
        """
        ws=self.rootWS()
        assert(ws is not None)

        if isinstance(adminData, dict):
            adminDataObj=ws.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or AdminData")
        baseType = autosar.datatype.SwBaseType(name, size, encoding, nativeDeclaration, category, self, adminData)
        self.append(baseType)
        return baseType

    def createBaseType(self, name, size, encoding=None, nativeDeclaration=None, adminData=None):
        """
        AUTOSAR4

        alias for createSwBaseType
        """
        return self.createSwBaseType(name, size, encoding, nativeDeclaration, adminData)


    def createApplicationPrimitiveDataType(self, name, dataConstraint = '', compuMethod = None, unit = None, swCalibrationAccess = None, category = None, adminData = None):
        """
        AUTOSAR4

        Creates a new ApplicationPrimitiveDataType in current package.

        name: <SHORT-NAME> (str)
        dataConstraint: Name or reference to autosar.datatype.DataConstraint object (or None). Default is to automatically create a constraint based on given compuMethod
        compuMethod: Name or reference to autosar.datatype.CompuMethod object (or None).
        swCalibrationAccess: Sets the SW-CALIBRATION-ACCESS property (str['NOT-ACCESSIBLE', 'READ-ONLY', 'READ-WRITE']).
        category: The category of this element (str)
        """
        ws=self.rootWS()
        assert(ws is not None)

        adminDataObj = self._checkAdminData(adminData)
        unitObj = self._checkAndCreateUnit(ws, unit)
        dataConstraintObj, compuMethodObj = None, None
        if compuMethod is not None:
            compuMethodObj = self._findElementByRole(ws, compuMethod, 'CompuMethod')
            if compuMethodObj is None:
                raise autosar.base.InvalidCompuMethodRef(compuMethod)
        if dataConstraint is not None:
            if len(dataConstraint)==0:
                dataConstraintName = self._createDataConstraintName(ws, name)
                if compuMethodObj is not None:
                    dataConstraintObj = self._checkAndCreateDataConstraintFromCompuMethod(ws, dataConstraintName, compuMethodObj)
            else:
                dataConstraintObj = self._findElementByRole(ws, dataConstraint, 'DataConstraint')
                if dataConstraintObj is None:
                    raise autosar.base.InvalidDataConstraintRef(dataConstraint)

        unitRef = None if unitObj is None else unitObj.ref
        compuMethodRef = None if compuMethodObj is None else compuMethodObj.ref
        dataConstraintRef = None if dataConstraintObj is None else dataConstraintObj.ref

        if swCalibrationAccess is not None or dataConstraintRef is not None or compuMethodRef is not None or unitRef is not None:
            variantProps = autosar.base.SwDataDefPropsConditional(
                swCalibrationAccess = swCalibrationAccess,
                dataConstraintRef = dataConstraintRef,
                compuMethodRef = compuMethodRef,
                unitRef = unitRef
                )
        else:
            variantProps = None
        dataType = autosar.datatype.ApplicationPrimitiveDataType(name, variantProps, category, parent = self, adminData = adminDataObj)
        self.append(dataType)
        return dataType

    def createApplicationArrayDataType(self, name, element, swCalibrationAccess = None, category = 'ARRAY', adminData = None):
        """
        AUTOSAR4

        Creates a new createApplicationArrayDataType in current package.

        name: <SHORT-NAME> (str)
        swCalibrationAccess: Sets the SW-CALIBRATION-ACCESS property (str['NOT-ACCESSIBLE', 'READ-ONLY', 'READ-WRITE']).
        element: <ELEMENT> (autosar.datatype.ApplicationArrayElement)
        category: The category of this element (str). Default='ARRAY'
        """
        ws=self.rootWS()
        assert(ws is not None)

        adminDataObj = self._checkAdminData(adminData)
        if swCalibrationAccess is not None:
            variantProps = autosar.base.SwDataDefPropsConditional(
                swCalibrationAccess = swCalibrationAccess
                )
        else:
            variantProps = None
        dataType = autosar.datatype.ApplicationArrayDataType(name, element, variantProps, category, parent = self, adminData = adminDataObj)
        self.append(dataType)
        return dataType

    def createApplicationRecordDataType(self, name, elements = None, swCalibrationAccess = None, category = 'STRUCTURE', adminData = None):
        """
        (AUTOSAR4)
        Creates a new ImplementationDataType containing sub elements
        """
        ws=self.rootWS()
        assert(ws is not None)
        adminDataObj = self._checkAdminData(adminData)
        if swCalibrationAccess is not None and len(swCalibrationAccess)==0:
            swCalibrationAccess = ws.profile.swCalibrationAccessDefault

        if swCalibrationAccess is not None:
            variantProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess)
        else:
            variantProps = None

        dataType = autosar.datatype.ApplicationRecordDataType(name, variantProps = variantProps, category = category, adminData = adminDataObj)
        if elements is not None:
            for element in elements:
                if not isinstance(element, tuple):
                    raise ValueError('element must be a tuple')
                (elemName, elemTypeRef) = element
                elemType = ws.find(elemTypeRef, role='DataType')
                if elemType is None:
                    raise autosar.base.InvalidDataTypeRef(elemTypeRef)
                dataType.createElement(elemName, elemType.ref)
        self.append(dataType)
        return dataType

    def createImplementationDataTypeRef(self, name, implementationTypeRef, lowerLimit = None, upperLimit = None, valueTable = None, bitmask = None, offset = None, scaling = None, unit = None, forceFloat = False, dataConstraint = '', swCalibrationAccess = '', typeEmitter = None, lowerLimitType = None, upperLimitType = None, category = 'TYPE_REFERENCE', adminData = None):
        """
        AUTOSAR4

        Creates an implementation data type that is a reference (typedef) of another implementation data type
        name: name of the new data type
        typeRef: reference to implementation data type
        """
        return self._createImplementationDataTypeInternal(
            name,
            None,
            implementationTypeRef,
            lowerLimit,
            upperLimit,
            valueTable,
            bitmask,
            offset,
            scaling,
            unit,
            forceFloat,
            dataConstraint,
            swCalibrationAccess,
            typeEmitter,
            lowerLimitType,
            upperLimitType,
            category,
            adminData
        )

    def createImplementationDataTypePtr(self, name, baseTypeRef, swImplPolicy=None, category = 'DATA_REFERENCE', targetCategory = 'VALUE', adminData = None):
        """
        Creates an implementation type that is a C-type pointer to another type
        """
        ws=self.rootWS()
        assert(ws is not None)

        adminDataObj = self._checkAdminData(adminData)

        targetProps = autosar.base.SwPointerTargetProps(targetCategory, autosar.base.SwDataDefPropsConditional(baseTypeRef = baseTypeRef, swImplPolicy=swImplPolicy))
        variantProps =  autosar.base.SwDataDefPropsConditional(swPointerTargetProps = targetProps)
        implementationDataType = autosar.datatype.ImplementationDataType(name, variantProps, category = category, parent = self, adminData = adminDataObj)
        self.append(implementationDataType)
        return implementationDataType

    def createImplementationArrayDataType(self, name, implementationTypeRef, arraySize, elementName = None, swCalibrationAccess = '', typeEmitter = None, category = 'ARRAY', targetCategory = 'TYPE_REFERENCE', adminData = None):
        """
        (AUTOSAR4)
        Creates a new ImplementationDataType that references another type as an array
        """
        ws=self.rootWS()
        assert(ws is not None)
        if elementName is None:
            elementName = name
        if  swCalibrationAccess is not None and len(swCalibrationAccess)==0:
            swCalibrationAccess = ws.profile.swCalibrationAccessDefault

        if implementationTypeRef.startswith('/'):
            dataType = ws.find(implementationTypeRef)
        else:
            dataType = ws.find(implementationTypeRef, role='DataType')
        if dataType is None:
            raise autosar.base.InvalidDataTypeRef(implementationTypeRef)

        newType = autosar.datatype.ImplementationDataType(name, category = category, adminData = adminData)
        outerProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess)
        newType.variantProps = [outerProps]
        innerProps = autosar.base.SwDataDefPropsConditional(implementationTypeRef = implementationTypeRef)
        subElement = autosar.datatype.ImplementationDataTypeElement(elementName, targetCategory, arraySize, variantProps = innerProps)
        newType.subElements.append(subElement)
        self.append(newType)
        return newType

    def createImplementationDataType(self, name, baseTypeRef, lowerLimit = None, upperLimit = None, valueTable = None, bitmask = None, offset = None, scaling = None, unit = None, forceFloat = False, dataConstraint='', swCalibrationAccess = '', typeEmitter = None, lowerLimitType = None, upperLimitType = None, category='VALUE', adminData = None):
        return self._createImplementationDataTypeInternal(
            name,
            baseTypeRef,
            None,
            lowerLimit,
            upperLimit,
            valueTable,
            bitmask,
            offset,
            scaling,
            unit,
            forceFloat,
            dataConstraint,
            swCalibrationAccess,
            typeEmitter,
            lowerLimitType,
            upperLimitType,
            category,
            adminData
        )
    def _createImplementationDataTypeInternal(self, name, baseTypeRef, implementationTypeRef, lowerLimit, upperLimit, valueTable, bitmask, offset, factor, unit, forceFloat, dataConstraint, swCalibrationAccess, typeEmitter, lowerLimitType, upperLimitType, category, adminData):
        """
        Creates an implementation data type that wraps a base type. Defaults to value type category
        """
        ws=self.rootWS()
        assert(ws is not None)

        lowerLimit = self._convertNumber(lowerLimit)
        upperLimit = self._convertNumber(upperLimit)

        if swCalibrationAccess is not None and len(swCalibrationAccess)==0:
            swCalibrationAccess = ws.profile.swCalibrationAccessDefault

        adminDataObj = self._checkAdminData(adminData)
        unitObj = self._checkAndCreateUnit(ws, unit)

        if implementationTypeRef is not None:
            referencedType = ws.find(implementationTypeRef)
            if referencedType is None:
                raise autosar.base.InvalidDataTypeRef(implementationTypeRef)
        else:
            referencedType = None

        compuMethodObj = self._checkAndCreateCompuMethod(ws, self._createCompuMethodName(ws, name), unitObj, lowerLimit, upperLimit, offset, factor, bitmask, valueTable, referencedType, forceFloat)
        if dataConstraint is None:
            dataConstraintObj = None
        else:
            if not isinstance(dataConstraint, str):
                raise ValueError('dataConstraint argument must be None or str')
            if len(dataConstraint)==0:
            #Automatically create a data constraint on empty string
                if compuMethodObj is not None:
                    dataConstraintObj = self._checkAndCreateDataConstraintFromCompuMethod(ws, self._createDataConstraintName(ws, name), compuMethodObj)
                else:
                    if lowerLimit is None and upperLimit is None:
                        dataConstraintObj = None
                    else:
                        if upperLimit is None:
                            raise ValueError('lowerLimit cannot be None')
                        if upperLimit is None:
                            raise ValueError('upperLimit cannot be None')
                        if lowerLimitType is None:
                            lowerLimitType = 'CLOSED'
                        if upperLimitType is None:
                            upperLimitType = 'CLOSED'
                        dataConstraintObj = self._checkAndCreateDataConstraint(ws, self._createDataConstraintName(ws, name), 'internalConstraint', lowerLimit, upperLimit, lowerLimitType, upperLimitType)
            else:
                if dataConstraint.startswith('/'):
                    dataConstraintObj = ws.find(dataConstraint)
                else:
                    dataConstraintObj = ws.find(dataConstraint, role = 'DataConstraint')
                if dataConstraintObj is None:
                    raise autosar.base.InvalidDataConstraintRef(dataConstraint)

        unitRef = None if unitObj is None else unitObj.ref
        compuMethodRef = None if compuMethodObj is None else compuMethodObj.ref
        dataConstraintRef = None if dataConstraintObj is None else dataConstraintObj.ref

        variantProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess,
                                                              compuMethodRef = compuMethodRef,
                                                              dataConstraintRef = dataConstraintRef,
                                                              baseTypeRef = baseTypeRef,
                                                              implementationTypeRef = implementationTypeRef,
                                                              unitRef = unitRef)
        implementationDataType = autosar.datatype.ImplementationDataType(name, variantProps, typeEmitter=typeEmitter, category = category, parent = self, adminData = adminDataObj)
        self.append(implementationDataType)
        return implementationDataType

    def createImplementationRecordDataType(self, name, elements, swCalibrationAccess = '', category = 'STRUCTURE', adminData = None):
        """
        (AUTOSAR4)
        Creates a new ImplementationDataType containing sub elements
        """
        ws=self.rootWS()
        assert(ws is not None)

        if swCalibrationAccess is not None and len(swCalibrationAccess)==0:
            swCalibrationAccess = ws.profile.swCalibrationAccessDefault

        if swCalibrationAccess is not None:
            variantProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess)
        else:
            variantProps = None
        dataType = autosar.datatype.ImplementationDataType(name, variantProps, category = category, adminData = adminData)
        for element in elements:
            if not isinstance(element, tuple):
                raise ValueError('element must be a tuple')
            (elementName, elemTypeRef) = element
            elemType = ws.find(elemTypeRef, role='DataType')
            if elemType is None:
                raise autosar.base.InvalidDataTypeRef(elemTypeRef)
            if isinstance(elemType, autosar.datatype.ImplementationDataType):
                elementProps = autosar.base.SwDataDefPropsConditional(implementationTypeRef = elemType.ref)
            elif isinstance(elemType, autosar.datatype.SwBaseType):
                elementProps = autosar.base.SwDataDefPropsConditional(baseTypeRef = elemType.ref)
            else:
                raise NotImplementedError(type(elemType))
            implementationDataTypeElement = autosar.datatype.ImplementationDataTypeElement(elementName, 'TYPE_REFERENCE', variantProps = elementProps)
            dataType.subElements.append(implementationDataTypeElement)
        self.append(dataType)
        return dataType


    def createUnit(self, shortName, displayName = None, offset = None, scaling = None,):
        ws = self.rootWS()
        assert(ws is not None)
        if ws.roles['Unit'] is None:
            unitPackage = self
        else:
            unitPackage = ws.find(ws.roles['Unit'])
        unitElem = self._checkAndCreateUnit(ws, shortName, displayName, scaling, offset, unitPackage)
        return unitElem

    def createCompuMethodLinear(self, name, offset, scaling, lowerLimit = None, upperLimit = None, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', unit = None, defaultValue = None, label = 'SCALING', forceFloat = True, category = 'LINEAR', adminData = None):
        """
        Alias for createCompuMethodRational
        """
        return self.createCompuMethodRational(name, offset, scaling, lowerLimit, upperLimit, lowerLimitType, upperLimitType, unit, defaultValue, label, forceFloat, category, adminData)

    def createCompuMethodRationalPhys(self, name, offset, scaling, lowerLimit = None, upperLimit = None, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', unit = None, defaultValue = None, label = 'SCALING', forceFloat = False, useIntToPhys=False, usePhysToInt = True, category = 'LINEAR', adminData = None):
        """
        Alias for createCompuMethodRational but creates a PHYSICAL-TO-INTERNAL mapping by default
        """
        return self.createCompuMethodRational(name, offset, scaling, lowerLimit, upperLimit, lowerLimitType, upperLimitType, unit, defaultValue, label, forceFloat, useIntToPhys, usePhysToInt, category, adminData)

    def createCompuMethodRational(self, name, offset, scaling, lowerLimit = None, upperLimit = None, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', unit = None, defaultValue = None, label = 'SCALING', forceFloat = False, useIntToPhys=True, usePhysToInt = False, category = 'LINEAR', adminData = None):
        """
        Creates a new CompuMethodRational object and appends it to the package with package-role 'CompuMethod'

        name: <SHORT-NAME> (str)
        offset: offset (int or float)
        scaling: scaling factor (int, float or rational number). This together with offset creates the numerator and denominator.
        lowerLimit: <LOWER-LIMIT> (int). Default = None.
        uppwerLimit: <UPPER-LIMIT> (int). Default = None.
        lowerLimitType: "INTERVAL-TYPE" of lowerLimit, str['OPEN', 'CLOSED']. Default='CLOSED'. Only applies when lowerLimit is not None.
        upperLimitType: "INTERVAL-TYPE" of upperLimit, str['OPEN', 'CLOSED']. Default='CLOSED'. Only applies when lowerLimit is not None.
        unit: Name of the unit (str). Default = None
        defaultValue: default value for the computation (None, int, float, str). Default = None.
        label: Label for the internally created <COMPU-SCALE> (str). Default = 'SCALING'.
        forceFloat: Forces numerator to become a floating point number (bool). Default = False.
        intToPhys: Enable internal-to-physical computation (bool). Default = True.
        physToInt: Enable physical-to-internal computation (bool). Default = False.
        category: <CATEGORY> of the CompuMethodRational (str). Default = 'LINEAR'.
        adminData: <ADMIN-DATA> for <COMPU-METHOD> (dict). Default = None.

        """
        ws = self.rootWS()
        assert(ws is not None)

        if ws.roles['CompuMethod'] is None:
            compuMethodPackage = self
        else:
            compuMethodPackage = ws.find(ws.roles['CompuMethod'])

        unitRef = None
        unitObj = self._checkAndCreateUnit(ws, unit)
        if unitObj is not None:
            unitRef = unitObj.ref

        adminDataObj = self._checkAdminData(adminData)

        compuMethod = autosar.datatype.CompuMethod(name, useIntToPhys, usePhysToInt, unitRef, category, compuMethodPackage, adminDataObj)
        (numerator, denominator) = self._calcNumeratorDenominator(scaling, forceFloat)
        if useIntToPhys:
            compuMethod.intToPhys.createRationalScaling(
                offset,
                numerator,
                denominator,
                lowerLimit,
                upperLimit,
                lowerLimitType,
                upperLimitType,
                label = label
                )
            if defaultValue is not None:
                compuMethod.intToPhys.defaultValue = defaultValue
        elif usePhysToInt:
            compuMethod.physToInt.createRationalScaling(
                offset,
                numerator,
                denominator,
                lowerLimit,
                upperLimit,
                lowerLimitType,
                upperLimitType,
                label = label
                )
            if defaultValue is not None:
                if useIntToPhys:
                    compuMethod.intToPhys.defaultValue = defaultValue
                elif usePhysToInt:
                    compuMethod.physToInt.defaultValue = defaultValue

        compuMethodPackage.append(compuMethod)
        return compuMethod

    def createCompuMethodConst(self, name, valueTable, unit = None, defaultValue = None, category = 'TEXTTABLE', adminData = None):
        useIntToPhys, usePhysToInt = True, False

        ws = self.rootWS()
        assert(ws is not None)

        if ws.roles['CompuMethod'] is None:
            compuMethodPackage = self
        else:
            compuMethodPackage = ws.find(ws.roles['CompuMethod'])
        unitRef = None
        unitObj = self._checkAndCreateUnit(ws, unit)
        if unitObj is not None:
            unitRef = unitObj.ref
        if isinstance(adminData, dict):
            adminData = autosar.base.createAdminData(adminData)

        compuMethod = autosar.datatype.CompuMethod(name, useIntToPhys, usePhysToInt, unitRef, category, compuMethodPackage, adminData)
        compuMethod.intToPhys.createValueTable(valueTable)
        if defaultValue is not None:
            compuMethod.intToPhys.defaultValue = defaultValue

        compuMethodPackage.append(compuMethod)
        return compuMethod

    def createDataTypeMappingSet(self, name, adminData = None):
        dataTypeMappingSet = autosar.datatype.DataTypeMappingSet(name, adminData = adminData)
        self.append(dataTypeMappingSet)
        return dataTypeMappingSet

    def _calcNumeratorDenominator(self, scalingFactor, forceFloat = False):

        if forceFloat:
           (numerator, denominator) = (float(scalingFactor), 1)
        else:
            f=Fraction.from_float(scalingFactor)
            if f.denominator > 10000: #use the float version in case its not a rational number
                (numerator, denominator) = (float(scalingFactor), 1)
            else:
                (numerator, denominator) = (f.numerator, f.denominator)
        return (numerator, denominator)

    def _checkAndCreateCompuMethod(self, ws, name, unitObj, lowerLimit, upperLimit, offset, scaling, bitmaskTable, valueTable, referencedType, forceFloatScaling, useCategory = True, autoLabel = True):
        """
        Returns CompuMethod object from the package with role 'CompuMethod'.
        If no CompuMethod exists with that name it will be created and then returned.
        """
        if name is None:
            return None

        category = None
        computation = autosar.datatype.Computation()
        if bitmaskTable is not None:
            category = 'BITFIELD_TEXTTABLE'
            computation.createBitMask(bitmaskTable)
        elif valueTable is not None:
            category = 'TEXTTABLE'
            computation.createValueTable(valueTable, autoLabel)
        elif offset is not None and scaling is not None:
            category = 'LINEAR'
            (numerator, denominator) = self._calcNumeratorDenominator(scaling, forceFloatScaling)
            if (lowerLimit is None) and (referencedType is not None) and (referencedType.dataConstraintRef is not None):
                constraint = ws.find(referencedType.dataConstraintRef)
                if constraint is None:
                    raise autosar.base.InvalidDataConstraintRef
                lowerLimit = constraint.lowerLimit
            if (upperLimit is None) and (referencedType is not None) and (referencedType.dataConstraintRef is not None):
                constraint = ws.find(referencedType.dataConstraintRef)
                if constraint is None:
                    raise autosar.base.InvalidDataConstraintRef
                upperLimit = constraint.upperLimit
            computation.createRationalScaling(offset, numerator, denominator, lowerLimit, upperLimit)
        if category is None:
            return None #Creating a compu method does not seem necessary

        compuMethodPackage = None
        if ws.roles['CompuMethod'] is not None:
            compuMethodPackage=ws.find(ws.roles['CompuMethod'])
        if compuMethodPackage is None:
            raise RuntimeError("No package found with role='CompuMethod'")
        compuMethodObj = compuMethodPackage.find(name)
        if compuMethodObj is not None: #Element already exists with that name?
            return compuMethodObj
        unitRef = None if unitObj is None else unitObj.ref

        useIntToPhys, usePhysToInt = True, False
        if not useCategory:
            category = None
        compuMethodObj = autosar.datatype.CompuMethod(name, useIntToPhys, usePhysToInt, unitRef, category, compuMethodPackage)
        compuMethodObj.intToPhys = computation
        compuMethodPackage.append(compuMethodObj)
        return compuMethodObj

    def _checkAndCreateDataConstraintFromCompuMethod(self, ws, name, compuMethodObj):
        constraintType = 'internalConstraint'
        if compuMethodObj.category == 'BITFIELD_TEXTTABLE':
            lowerLimit = 0
            tmp = compuMethodObj.intToPhys.upperLimit
            upperLimit = 2**int.bit_length(tmp)-1
        else:
            lowerLimit = compuMethodObj.intToPhys.lowerLimit
            upperLimit = compuMethodObj.intToPhys.upperLimit
        if (lowerLimit is not None) and upperLimit is not None:
            return self._checkAndCreateDataConstraint(ws, name, constraintType, lowerLimit, upperLimit)
        else:
            return None

    def _checkAndCreateDataConstraint(self, ws, name, constraintType, lowerLimit, upperLimit, lowerLimitType = 'CLOSED', upperLimitType = 'CLOSED', adminData = None):
        if name is None:
            return None
        dataConstraintPackage = None
        if ws.roles['DataConstraint'] is not None:
            dataConstraintPackage = ws.find(ws.roles['DataConstraint'])
        if dataConstraintPackage is None:
            raise RuntimeError("No package found with role='DataConstraint'")
        dataConstraintObj = dataConstraintPackage.find(name)
        if dataConstraintObj is not None: #Element already exists with that name?
            return dataConstraintObj
        else:
            return self._createDataConstraintInPackage(dataConstraintPackage, name, constraintType, lowerLimit, upperLimit, lowerLimitType, upperLimitType, adminData)

    def _findElementByRole(self, ws, name, role):
        if name.startswith('/'):
            return ws.find(name)
        else:
            return ws.find(name, role = role)

    def _createDataConstraintInPackage(self, dataConstraintPackage, name, constraintType, lowerLimit, upperLimit, lowerLimitType, upperLimitType, adminData):
        """
        Returns DataConstraint object from the package with role 'DataConstraint'.
        If no DataConstraint exists with that name it will be created and then returned.
        """
        rules=[]

        rules.append({'type': constraintType, 'lowerLimit':lowerLimit, 'upperLimit':upperLimit, 'lowerLimitType':lowerLimitType, 'upperLimitType':upperLimitType})
        constraint = autosar.datatype.DataConstraint(name, rules, parent=self)
        dataConstraintPackage.append(constraint)
        return constraint

    def _checkAdminData(self, adminData):
        if isinstance(adminData, dict):
            adminDataObj=autosar.base.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or AdminData")
        return adminDataObj

    def _createCompuMethodAndUnitV3(self, ws, name, lowerLimit, upperLimit, valueTable, bitmask, offset, scaling, unit, forceFloatScaling):
        """
        AUTOSAR3:

        If both compuMethod and unit: Returns (compuMethodRef, unitRef)
        Else if compuMethod only: Returns (compuMethodRef, None)
        Else: Returns (None, None)
        """
        semanticsPackage = None
        unitPackage = None
        compuMethodElem = None
        unitElem = None
        assert(ws is not None)
        if ws.roles['CompuMethod'] is not None:
            semanticsPackage=ws.find(ws.roles['CompuMethod'])
            if semanticsPackage is None:
                raise RuntimeError("no package found with role='CompuMethod'")
        if ws.roles['Unit'] is not None:
            unitPackage=ws.find(ws.roles['Unit'])
            if unitPackage is None:
                raise RuntimeError("no package found with role='Unit'")

        if (lowerLimit is None) and (upperLimit is None) and (valueTable is None) and (bitmask is None) and (offset is None) and (scaling is None) and (unit is None):
            return None

        if unit is not None:
            unitElem = self._checkAndCreateUnit(ws, unit, unitPackage = unitPackage)
        compuMethodElem = self._checkAndCreateCompuMethod(ws, self._createCompuMethodName(ws, name), unitElem, lowerLimit, upperLimit, offset, scaling, None, valueTable, None, forceFloatScaling, useCategory = False, autoLabel = False)
        if (compuMethodElem is not None) and (unitElem is not None):
            compuMethodElem.unitRef = unitElem.ref
        return None if compuMethodElem is None else compuMethodElem.ref

    def _checkAndCreateUnit(self, ws, shortName, displayName = None, factor = None, offset = None, unitPackage = None):
        if shortName is None:
            return None
        if unitPackage is None:
            unitPackage = ws.find(ws.roles['Unit'])
            if unitPackage is None:
                raise RuntimeError("no package found with role='Unit'")
        assert(isinstance(unitPackage, autosar.package.Package))
        unitElem = unitPackage.find(shortName)
        if unitElem is None:
            unitElem = self._createUnitInPackage(unitPackage, shortName, displayName, factor, offset)
        return unitElem

    def _createUnitInPackage(self, unitPackage, shortName, displayName, factor, offset):
        if displayName is None:
            displayName = shortName
        unitElem = autosar.datatype.Unit(shortName, displayName, factor, offset)
        unitPackage.append(unitElem)
        return unitElem

    def _convertNumber(self, number):
        """
        Attempts to convert argument to int.
        If that fails it tries to convert to float.
        If that fails it returns the argument as a string.
        """
        retval = None
        if number is not None:
            try:
                retval = int(number)
            except ValueError:
                try:
                    retval = float(number)
                except ValueError:
                    retval = str(number)
        return retval

    def _createCompuMethodName(self, ws, name):
        return name + ws.profile.compuMethodSuffix

    def _createDataConstraintName(self, ws, name):
        return name + ws.profile.dataConstraintSuffix
