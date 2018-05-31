import autosar.component
import autosar.behavior
import autosar.element
import autosar.portinterface
import autosar.datatype
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


    def asdict(self):
        data={'type':self.__class__.__name__,'name':self.name,'elements':[],'subPackages':[]}
        for element in self.elements:
            if hasattr(element,'asdict'):
                data['elements'].append(element.asdict())
            else:
                print(type(element))
        for subPackage in self.subPackages:
            data['subPackages'].append(subPackage.asdict())
        if len(data['elements'])==0: del data['elements']
        if len(data['subPackages'])==0: del data['subPackages']
        return data

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



    def createSenderReceiverInterface(self,name, dataElements=None, modeGroups=None, isService=False, adminData=None):
        """
        creates a new sender-receiver port interface. dataElements can either be a single instance of DataElement or a list of DataElements.
        The same applies to modeGroups. isService must be boolean
        """

        ws = self.rootWS()
        assert(ws is not None)

        portInterface = autosar.portinterface.SenderReceiverInterface(str(name), isService, adminData=adminData)
        if dataElements is not None:
            if isinstance(dataElements,collections.Iterable):
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
            if isinstance(modeGroups,collections.Iterable):
                for elem in modeGroups:
                    portInterface.append(elem)
            elif isinstance(modeGroups,autosar.portinterface.ModeGroup):
                portInterface.append(modeGroups)
            else:
                raise ValueError("dataElements: expected autosar.portinterface.DataElement instance or list")
        self.append(portInterface)

    def createParameterInterface(self,name,parameters=None,modeDeclarationGroups=None, isService=False, adminData=None):
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
        if isinstance(parameters,collections.Iterable):
            for elem in parameters:
                dataType=ws.find(elem.typeRef, role='DataType')
                #normalize reference to data element
                if dataType is None:
                    raise ValueError('invalid type reference: '+elem.typeRef)
                elem.typeRef=dataType.ref
                if isinstance(autosar.portinterface.DataElement):
                    #convert into Parameter
                    parameter = autosar.portinterface.Parameter(elem.name, elem.typeRef, elem.swAddressMethodRef, adminData=elem.adminData)
                else:
                    parameter = elem
                portInterface.append(parameter)
        elif isinstance(parameters, autosar.portinterface.DataElement):
            dataType=ws.find(parameters.typeRef, role='DataType')
            #normalize reference to data element
            if dataType is None:
                raise ValueError('invalid type reference: '+parameters.typeRef)
            parameters.typeRef=dataType.ref
            parameter = autosar.portinterface.Parameter(parameters.name, parameters.typeRef,
                                                        parameters.swAddressMethodRef, adminData=parameters.adminData)
            portInterface.append(parameter)
        elif isinstance(parameters, autosar.portinterface.Parameter):
            dataType=ws.find(parameters.typeRef, role='DataType')
            #normalize reference to data element
            if dataType is None:
                raise ValueError('invalid type reference: '+parameters.typeRef)
            parameters.typeRef=dataType.ref
            portInterface.append(parameters)
        else:
            raise ValueError("dataElements: expected autosar.DataElement instance or list")
        self.append(portInterface)
        return portInterface

    def createModeSwitchInterface(self, name, modeGroup = None, isService=False, adminData=None):
        portInterface = autosar.portinterface.ModeSwitchInterface(name, isService, self, adminData)
        if modeGroup is not None:
            portInterface.modeGroup = modeGroup
            modeGroup.parent = portInterface
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


    def createApplicationSoftwareComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False):
        """
        Creates a new ApplicationSoftwareComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.

        """
        ws = self.rootWS()
        assert(ws is not None)
        swc = autosar.component.ApplicationSoftwareComponent(swcName,self)
        self.append(swc)
        self._createsInternalBehavior(ws, swc, behaviorName, multipleInstance)
        self._createImplementation(swc, implementationName)
        return swc

    def createServiceComponent(self, swcName, behaviorName=None, implementationName=None, multipleInstance=False):
        """
        Creates a new ApplicationSoftwareComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.
        """
        ws = self.rootWS()
        assert(ws is not None)

        swc = autosar.component.ServiceComponent(swcName,self)
        self.append(swc)
        self._createsInternalBehavior(ws, swc, behaviorName, multipleInstance)
        self._createImplementation(swc, implementationName)
        return swc

    def createComplexDeviceDriverComponent(self,swcName,behaviorName=None,implementationName=None,multipleInstance=False):
        ws = self.rootWS()
        assert(ws is not None)
        swc=autosar.component.ComplexDeviceDriverComponent(swcName, parent=self)
        self.append(swc)
        self._createsInternalBehavior(ws, swc, behaviorName, multipleInstance)
        self._createImplementation(swc, implementationName)
        return swc

    def createCompositionComponent(self, componentName, adminData=None):
        component = autosar.component.CompositionComponent(str(componentName), self)
        self.append(component)
        return component

    def _createsInternalBehavior(self, ws, swc, behaviorName, multipleInstance):
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
        swc.behavior=internalBehavior
        if ws.version < 4.0:
            # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
            self.append(internalBehavior)

    def _createImplementation(self, swc, implementationName):

        if implementationName is None:
            implementationName = swc.name+'_Implementation'
        swc.implementation=autosar.component.SwcImplementation(implementationName,swc.behavior.ref,parent=self)
        self.append(swc.implementation)


    def createModeDeclarationGroup(self, name, modeDeclarations, initialMode, category=None, adminData=None):
        """
        creates an instance of autosar.portinterface.ModeDeclarationGroup
        name: name of the ModeDeclarationGroup
        modeDeclarations: list of strings where each string is a mode name
        initialMode: string with name of the initial mode (must be one of the strings in modeDeclarations list)
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
        group = autosar.portinterface.ModeDeclarationGroup(name,None,None,category,self,adminDataObj)
        for declarationName in modeDeclarations:
            item=autosar.portinterface.ModeDeclaration(declarationName,group)
            group.modeDeclarations.append(item)
            if declarationName == initialMode:
                group.initialModeRef = item.ref
        if group.initialModeRef is None:
            raise ValueError('initalMode "%s" not a valid modeDeclaration name'%initialMode)
        self.append(group)
        return group

    def createClientServerInterface(self, name, operations, errors=None, isService=False, serviceKind=None, adminData=None):
        """
        creates a new client server interface in current package
        name: name of the interface (string)
        operations: names of the operations in the interface (list of strings)
        errors: possible errors dict containing key-value pair where key is the name and value is the error code (must be integer)
        isService: True if this interface is a service interface (bool)
        adminData: optional admindata (dict or autosar.base.AdminData object)
        """
        portInterface = autosar.portinterface.ClientServerInterface(name, isService, serviceKind, self, adminData)
        for name in operations:
            portInterface.append(autosar.portinterface.Operation(name))
        if errors is not None:
            if isinstance(errors, collections.Iterable):
                for error in errors:
                    portInterface.append(error)
            else:
                assert( isinstance(errors, autosar.portinterface.ApplicationError))
                portInterface.append(errors)
        self.append(portInterface)
        return portInterface

    def createSoftwareAddressMethod(self, name):
        item = autosar.portinterface.SoftwareAddressMethod(name)
        self.append(item)
        return item

    def createArrayDataType(self, name, typeRef, length, elementName=None, swCalibrationAccess=None, adminData=None):
        """
        AUTOSAR3:
           Creates an ArrayDataType and adds it to current package
        AUTOSAR4:
           Creates an ImplementationDataType and adds it to current package
        """
        ws = self.rootWS()
        assert(ws is not None)
        if swCalibrationAccess is None:
            swCalibrationAccess = 'NOT-ACCESSIBLE'
        if (not typeRef.startswith('/')) and (ws.roles['DataType'] is not None):
            typeRef=ws.roles['DataType']+'/'+typeRef
        dataType = ws.find(typeRef)
        if dataType is None:
            raise autosar.base.InvalidDataTypeRef(typeRef)
        if ws.version >= 4.0:
            if elementName is None:
                elementName = name
            newType = autosar.datatype.ImplementationDataType(name, 'ARRAY', adminData=adminData)
            outerProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess=swCalibrationAccess)
            newType.variantProps = [outerProps]
            innerProps = autosar.base.SwDataDefPropsConditional(implementationTypeRef=typeRef)
            subElement = autosar.datatype.ImplementationDataTypeElement(elementName, 'TYPE_REFERENCE', length, variantProps=innerProps)
            newType.subElements.append(subElement)
        else:
            newType = autosar.datatype.ArrayDataType(name, typeRef, length, adminData)
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
            dataConstraint = '' #use default rule
            if baseTypeRef is None:
                return self.createApplicationDataType(name, min, max, valueTable, offset, scaling, unit, forceFloatScaling, swCalibrationAccess, typeEmitter, adminData)
            else:
                return self.createImplementationDataType(name, baseTypeRef, 'VALUE', min, max, valueTable, None, offset, scaling, unit, forceFloatScaling, dataConstraint, swCalibrationAccess, typeEmitter, adminData)
        else:
            (compuMethodRef, unitRef, dataConstraintRef) = self._createCompuMethodUnitDataConstraint(ws, name, min, max, valueTable, None, offset, scaling, unit, forceFloatScaling, dataConstraint)
            minVal, maxVal = min, max
            if compuMethodRef is not None:
                compuMethod = ws.find(compuMethodRef)
                if isinstance(compuMethod, autosar.datatype.CompuMethodConst):
                    if minVal is None:
                        minVal = compuMethod.elements[0].lowerLimit
                    if maxVal is None:
                        maxVal = compuMethod.elements[-1].upperLimit
            newType=autosar.datatype.IntegerDataType(name, minVal, maxVal, compuMethodRef=compuMethodRef, adminData=adminData)
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

    def createRecordDataType(self, name, elements, swCalibrationAccess = None, adminData=None):
        """
        AUTOSAR3: Create a new instance of RecordDataType and appends it to current package
        AUTOSAR4: Creates a new ImplementationDataType and appends it to current package
        """
        ws = self.rootWS()
        assert(ws is not None)
        if ws.version < 4.0:
            dataType=autosar.datatype.RecordDataType(name, elements, self, adminData)
        else:
            if swCalibrationAccess is None:
                swCalibrationAccess = 'NOT-ACCESSIBLE'
            props = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess)
            dataType = autosar.datatype.ImplementationDataType(name, 'STRUCTURE', props, adminData = adminData)
            for element in elements:
                if not isinstance(element, tuple):
                    raise ValueError('element must be a tuple')
                (elementName, elemTypeRef) = element
                elemType = ws.find(elemTypeRef, role='DataType')
                if elemType is None:
                    raise ValueError('Unknown data type name: '+elemTypeRef)
                if isinstance(elemType, autosar.datatype.ImplementationDataType):
                    props = autosar.base.SwDataDefPropsConditional(implementationTypeRef = elemType.ref)
                elif isinstance(elemType, autosar.datatype.SwBaseType):
                    props = autosar.base.SwDataDefPropsConditional(baseTypeRef = elemType.ref)
                else:
                    raise NotImplementedError(type(elemType))
                implementationDataTypeElement = autosar.datatype.ImplementationDataTypeElement(elementName, 'TYPE_REFERENCE', variantProps=props)
                dataType.subElements.append(implementationDataTypeElement)
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

    def createConstant(self, name, typeRef, initValue, adminData=None):
        """
        create a new instance of autosar.constant.Constant and appends it to the current package
        """
        ws=self.rootWS()
        assert(ws is not None)
        dataType = ws.find(typeRef, role='DataType')
        value=None
        if dataType is None:
            raise autosar.base.InvalidDataTypeRef(str(typeRef))
        if ws.version < 4.0:
            self._createConstantV3(ws, name, dataType, initValue, adminData)
        else:
            self._createConstantV4(ws, name, dataType, initValue, adminData)

    def _createConstantV3(self, ws, name, dataType, initValue, adminData=None):
        """Creates an AUTOSAR 3 Constant"""
        if isinstance(dataType, autosar.datatype.IntegerDataType):
            if not isinstance(initValue, int):
                raise ValueError('initValue: expected type int, got '+str(type(initValue)))
            value=autosar.constant.IntegerValue(name, dataType.ref, initValue)
        elif isinstance(dataType, autosar.datatype.RecordDataType):
            if isinstance(initValue, collections.Mapping) or isinstance(initValue, collections.Iterable):
                pass
            else:
                raise ValueError('initValue: expected type Mapping or Iterable, got '+str(type(initValue)))
            value=self._createRecordValueV3(ws, name, dataType, initValue)
        elif isinstance(dataType, autosar.datatype.ArrayDataType):
            if isinstance(initValue, collections.Iterable):
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
            value=autosar.constant.RealValue(name, dataType.ref, initValue)
        else:
            raise ValueError('unrecognized type: '+str(type(dataType)))
        assert(value is not None)
        constant = autosar.constant.Constant(name, value, adminData=adminData)
        self.append(constant)
        return constant

    def _createRecordValueV3(self, ws, name, dataType, initValue, parent=None):
        value = autosar.constant.RecordValue(name, dataType.ref, parent)
        if isinstance(initValue, collections.Mapping):
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
                        if isinstance(v, collections.Mapping) or isinstance(v, collections.Iterable):
                            pass
                        else:
                            raise ValueError('v: expected type Mapping or Iterable, got '+str(type(v)))
                        value.elements.append(self._createRecordValueV3(ws, elem.name, childType, v, value))
                    elif isinstance(childType, autosar.datatype.ArrayDataType):
                        if isinstance(v, collections.Iterable):
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
                        value.elements.append(autosar.constant.RealValue(elem.name, childType.ref, v, value))
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
            raise ValueError('invalid reference: '+str(elem.typeRef))
        if isinstance(initValue, collections.Iterable):
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
                    if isinstance(v, collections.Mapping) or isinstance(v, collections.Iterable):
                        pass
                    else:
                        raise ValueError('v: expected type Mapping or Iterable, got '+str(type(v)))
                        value.elements.append(self._createRecordValueV3(ws, elemName, childType, v, value))
                elif isinstance(childType, autosar.datatype.ArrayDataType):
                    if isinstance(v, collections.Iterable):
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
                    value.elements.append(autosar.constant.RealValue(elemName, childType.ref, v, value))
                else:
                    raise ValueError('unrecognized type: '+str(type(childType)))
        else:
            raise NotImplementedError(type(initValue))
        return value

    def _createConstantV4(self, ws, name, dataType, initValue, adminData=None):
        value = self._createValueV4(ws, name, dataType, initValue)
        assert(value is not None)
        constant = autosar.constant.Constant(name, value, parent=self, adminData=adminData)
        self.append(constant)
        return constant

    def _createValueV4(self, ws, name, dataType, rawValue, parent = None):
        if isinstance(dataType, (autosar.datatype.ImplementationDataType, autosar.datatype.ApplicationPrimitiveDataType)):
            value = None
            dataConstraint = None
            if isinstance(dataType, autosar.datatype.ImplementationDataType):
                variantProps = dataType.variantProps[0]
            if variantProps is not None:
                if variantProps.dataConstraintRef is not None:
                    dataConstraint = ws.find(variantProps.dataConstraintRef, role='DataConstraint')
                    if dataConstraint is None:
                        raise ValueError('{0.name}: Invalid DataConstraint reference: {1.dataConstraintRef}'.format(dataType, variantProps))
                if variantProps.compuMethodRef is not None:
                    compuMethod = ws.find(variantProps.compuMethodRef, role='CompuMethod')
                    if compuMethod is None:
                        raise ValueError('{0.name}: Invalid CompuMethod reference: {1.compuMethodRef}'.format(dataType, variantProps))
                    if isinstance(compuMethod, autosar.datatype.CompuMethodConst):
                        textValue = compuMethod.textValue(rawValue)
                        if textValue is None:
                            raise ValueError('{0.name}: Could not find a text value that matches numerical value {1:d}'.format(dataType, rawValue) )
                        value = autosar.constant.TextValue(name,textValue)
                    elif isinstance(compuMethod, autosar.datatype.CompuMethodRational):
                        if dataConstraint is not None:
                            dataConstraint.check_value(rawValue)
                        value = autosar.constant.NumericalValue(name, rawValue)
                    else:
                        raise NotImplementedError(type(compuMethod))
            if value is None:
                if dataType.category == 'VALUE':
                    if isinstance(rawValue, str):
                        value = autosar.constant.TextValue(name, rawValue)
                    else:
                        if dataConstraint is not None:
                            dataConstraint.check_value(rawValue)
                        value = autosar.constant.NumericalValue(name, rawValue)
                elif dataType.category == 'ARRAY':
                    value = self._createArrayValueV4(ws, name, dataType, rawValue, parent)
                elif dataType.category == 'STRUCTURE':
                    value = self._createRecordValueV4(ws, name, dataType, rawValue, parent)
                elif dataType.category == 'TYPE_REFERENCE':
                    referencedTypeRef = dataType.getTypeReference()
                    referencedType = ws.find(referencedTypeRef, role='DataType')
                    if referencedType is None:
                        raise ValueError('Invalid reference: '+str(referencedTypeRef))
                    value = self._createValueV4(ws, name, referencedType, rawValue, parent)
                else:
                    raise NotImplementedError(dataType.category)
        else:
            raise NotImplementedError(type(dataType))
        return value

    def _createRecordValueV4(self, ws, name, dataType, initValue, parent=None):
        value = autosar.constant.RecordValue(name, dataType.ref, parent)
        if isinstance(initValue, collections.abc.Mapping):
            a = set() #datatype elements
            b = set() #initvalue elements
            for subElem in dataType.subElements:
                a.add(subElem.name)
            for key in initValue.keys():
                b.add(key)
            extra_keys = b-a
            for elem in extra_keys:
                print('Unknown name in initializer: %s.%s'%(name,elem), file=sys.stderr)
            for elem in dataType.subElements:
                if elem.name in initValue:
                    v = initValue[elem.name]
                    childProps = elem.variantProps[0]
                    if childProps.implementationTypeRef is not None:
                        childTypeRef = childProps.implementationTypeRef
                    else:
                        raise NotImplementedError('could not deduce the type of element "%s"'%(elem.name))
                    childType = ws.find(childTypeRef, role='DataType')
                    if childType is None:
                        raise autosar.base.InvalidDataTypeRef(str(childTypeRef))
                    childValue = self._createValueV4(ws, elem.name, childType, v, value)
                    assert(childValue is not None)
                    value.elements.append(childValue)
                else:
                    raise ValueError('%s: missing initValue field: %s'%(name, elem.name))
        else:
            raise ValueError('initValue must be a dict')
        return value

    def _createArrayValueV4(self, ws, name, dataType, initValue, parent=None):
        value = autosar.constant.ArrayValue(name, dataType.ref, None, parent)
        typeArrayLength = dataType.getArrayLength()
        if not isinstance(typeArrayLength, int):
            raise ValueError('dataType has no valid array length')
        if isinstance(initValue, collections.abc.Sequence):
            if isinstance(initValue, str):
                initValue = list(initValue)
                if len(initValue)<typeArrayLength:
                    #pad with zeros until length matches
                    initValue += [0]*(typeArrayLength-len(initValue))
                    assert(len(initValue) == typeArrayLength)
            if len(initValue) > typeArrayLength:
                print("%s: Excess array init values detected. Expected length=%d, got %d items"%(name, typeArrayLength, len(initValue)), file=sys.stderr)
            if len(initValue) < typeArrayLength:
                print("%s: Not enough array init values. Expected length=%d, got %d items"%(name, typeArrayLength, len(initValue)), file=sys.stderr)
            i=0
            for v in initValue:
                if isinstance(v, str):
                    value.elements.append(autosar.constant.TextValue(None, v))
                else:
                    value.elements.append(autosar.constant.NumericalValue(None, v))
                i+=1
                if i>=typeArrayLength:
                    break
        return value

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

    def createInternalDataConstraint(self, name, lowerLimit, upperLimit, lowerLimitType="CLOSED", upperLimitType="CLOSED"):
        ws = self.rootWS()
        assert(ws is not None)
        dataConstraintPackage = None
        if ws.roles['DataConstraint'] is None:
            raise RuntimeError("no package found with role='DataConstraint'")
        dataConstraintPackage=ws.find(ws.roles['DataConstraint'])
        rules=[]
        try:
            lowerLimit = int(lowerLimit)
        except ValueError:
            lowerLimit = str(lowerLimit)
        try:
            upperLimit = int(upperLimit)
        except ValueError:
            upperLimit = str(upperLimit)
        rules.append({'type': 'internalConstraint', 'lowerLimit':lowerLimit, 'upperLimit':upperLimit, 'lowerLimitType':lowerLimitType, 'upperLimitType':upperLimitType})
        constraint = autosar.datatype.DataConstraint(name, rules, self)
        dataConstraintPackage.append(constraint)
        return constraint

    def createSwBaseType(self, name, size, encoding=None, nativeDeclaration=None, adminData=None):
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
        baseType = autosar.datatype.SwBaseType(name, size, encoding, nativeDeclaration, 'FIXED_LENGTH', self, adminData)
        self.append(baseType)
        return baseType

    def createBaseType(self, name, size, encoding=None, nativeDeclaration=None, adminData=None):
        """
        AUTOSAR4

        alias for createSwBaseType
        """
        return self.createSwBaseType(name, size, encoding, nativeDeclaration, adminData)

    def createImplementationDataTypeRef(self, name, implementationTypeRef, minVal = None, maxVal = None, valueTable = None, bitmask = None, offset = None, scaling = None, unit = None, forceFloatScaling = False, dataConstraint = '', swCalibrationAccess = None, typeEmitter = None, adminData = None):
        """
        AUTOSAR4

        Creates an implementation data type that is a reference (typedef) of another implementation data type
        name: name of the new data type
        typeRef: reference to implementation data type
        """
        ws=self.rootWS()
        assert(ws is not None)

        adminDataObj = self._checkAdminData(adminData)

        (compuMethodRef, unitRef, dataConstraintRef) = self._createCompuMethodUnitDataConstraint(ws, name, minVal, maxVal, valueTable, bitmask, offset, scaling, unit, forceFloatScaling, dataConstraint)
        variantProps = autosar.base.SwDataDefPropsConditional(swCalibrationAccess = swCalibrationAccess,
                                                              compuMethodRef = compuMethodRef,
                                                              dataConstraintRef = dataConstraintRef,
                                                              implementationTypeRef = implementationTypeRef,
                                                              unitRef = unitRef)
        implementationDataType = autosar.datatype.ImplementationDataType(name, 'TYPE_REFERENCE', variantProps, parent = self, adminData = adminDataObj)
        self.append(implementationDataType)
        return implementationDataType

    def createImplementationTypeReference(self, name, implementationTypeRef, adminData = None):
        if not _supress_warnings:
            print("WARNING: createImplementationTypeReference has been deprecated. Use createImplementationDataTypeRef instead.", file=sys.stderr)
        self.createImplementationDataTypeRef(name, implementationTypeRef, adminData)

    def createImplementationDataTypePtr(self, name, baseTypeRef, swImplPolicy=None, adminData = None):
        """
        Creates an implementation type that is a C-type pointer to another type
        """
        ws=self.rootWS()
        assert(ws is not None)

        adminDataObj = self._checkAdminData(adminData)

        targetProps = autosar.base.SwPointerTargetProps('VALUE', autosar.base.SwDataDefPropsConditional(baseTypeRef = baseTypeRef, swImplPolicy=swImplPolicy))
        variantProps =  autosar.base.SwDataDefPropsConditional(swPointerTargetProps = targetProps)
        implementationDataType = autosar.datatype.ImplementationDataType(name, 'DATA_REFERENCE', variantProps, parent = self, adminData = adminDataObj)
        self.append(implementationDataType)
        return implementationDataType

    def createImplementationDataReference(self, name, baseTypeRef, swImplPolicy=None, adminData = None):
        """
        Deprecated method name, use createImplementationPtrDataType instead
        """
        if not _supress_warnings:
            print("WARNING: createImplementationDataReference has been deprecated. Use createImplementationDataTypePtr instead.", file=sys.stderr)
        self.createImplementationDataTypePtr(name, baseTypeRef, swImplPolicy, adminData)

    def createImplementationDataType(self, name, baseTypeRef, category='VALUE', minVal = None, maxVal = None, valueTable = None, bitmask = None, offset = None, scaling = None, unit = None, forceFloatScaling = False, dataConstraint='', swCalibrationAccess = None, typeEmitter = None, adminData = None):
        """
        Creates an implementation data type that wraps a base type. Defaults to value type category
        """
        ws=self.rootWS()
        assert(ws is not None)

        adminDataObj = self._checkAdminData(adminData)

        (compuMethodRef, unitRef, dataConstraintRef) = self._createCompuMethodUnitDataConstraint(ws, name, minVal, maxVal, valueTable, bitmask, offset, scaling, unit, forceFloatScaling, dataConstraint)
        variantProps = autosar.base.SwDataDefPropsConditional(baseTypeRef = baseTypeRef,
                                                              swCalibrationAccess = swCalibrationAccess,
                                                              compuMethodRef = compuMethodRef,
                                                              dataConstraintRef = dataConstraintRef,
                                                              unitRef = unitRef)

        implementationDataType = autosar.datatype.ImplementationDataType(name, category, variantProps, typeEmitter=typeEmitter, parent = self, adminData = adminDataObj)
        self.append(implementationDataType)
        return implementationDataType

    def createApplicationDataType(self, name, minVal, maxVal, valueTable, offset, scaling, unit, forceFloatScaling, swCalibrationAccess, typeEmitter, adminData):
        raise NotImplementedError('createApplicationDataType')

    def _checkAdminData(self, adminData):
        if isinstance(adminData, dict):
            adminDataObj=ws.createAdminData(adminData)
        else:
            adminDataObj = adminData
        if (adminDataObj is not None) and not isinstance(adminDataObj, autosar.base.AdminData):
            raise ValueError("adminData must be of type dict or AdminData")
        return adminDataObj

    def _createCompuMethodUnitDataConstraint(self, ws, name, minVal, maxVal, valueTable, bitmask, offset, scaling, unit, forceFloatScaling, dataConstraint):
        """
        AUTOSAR3:

        If both compuMethod and unit: Returns (compuMethodRef, unitRef, None)
        Else if compuMethod only: Returns (compuMethodRef, None, None)
        Else: Returns (None, None, None)

        AUTOSAR4:

        If both compuMethod and unit: Returns (compuMethodRed, unitRed, dataConstraintRef)
        Else if  compuMethod only: Returns (compuMethodRef, None, dataConstraintRef
        Else: Returns (None, None, None)
        """
        semanticsPackage = None
        unitPackage = None
        dataConstraintPackage = None
        compuMethodElem = None
        dataConstraintElem = None
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
        if ws.roles['DataConstraint'] is not None:
            dataConstraintPackage=ws.find(ws.roles['DataConstraint'])
            if dataConstraintPackage is None:
                raise RuntimeError("no package found with role='DataConstraint'")

        if (minVal is None) and (maxVal is None) and (valueTable is None) and (bitmask is None) and (offset is None) and (scaling is None) and (unit is None):
            return (None, None, None)

        if ws.version >= 4.0:
            if dataConstraint is None: #disable rule
                dataConstraintName = None
            elif dataConstraint=='': #default rule
                dataConstraintName = name+'_DataConstr'
            else:
                dataConstraintName = str(dataConstraint) #overide rule (lets the user select the name)

        if (valueTable is not None) and (minVal is not None) and (maxVal is not None):
            #used for enumeration types with explicit min and max
            category = 'TEXTTABLE' if ws.version >= 4.0 else None
            compuMethodElem=autosar.CompuMethodConst(str(name), list(valueTable), category)
            if (ws.version >= 4.0) and (dataConstraintName is not None):
                dataConstraintElem = self.createInternalDataConstraint(dataConstraintName, minVal, maxVal)

        elif (valueTable is not None) and (minVal is None) and (maxVal is None):
            #used for enumeration types with implicit min and max
            category = 'TEXTTABLE' if ws.version >= 4.0 else None
            compuMethodElem=autosar.CompuMethodConst(str(name),list(valueTable), category)
            if (ws.version >= 4.0) and (dataConstraintName is not None):
                dataConstraintElem = self.createInternalDataConstraint(dataConstraintName, compuMethodElem.elements[0].lowerLimit, compuMethodElem.elements[-1].upperLimit)

        elif (bitmask is not None):
            if ws.version < 3.0:
                raise RunTimeError('bit masks not supported in AUTOSAR3')
            compuMethodElem = autosar.datatype.CompuMethodMask(name, bitmask, category='BITFIELD_TEXTTABLE')
            dataConstraintElem = self.createInternalDataConstraint(dataConstraintName, compuMethodElem.minVal, compuMethodElem.maxVal)

        elif (offset is not None) and (scaling is not None):
            if forceFloatScaling:
                semanticElements=[{'offset':offset, 'numerator':scaling, 'denominator':1}]
            else:
                f=Fraction.from_float(scaling)
                if f.denominator > 1000: #use the float version in case its not a rational number
                    semanticElements=[{'offset':offset, 'numerator':scaling, 'denominator':1}]
                else:
                    semanticElements=[{'offset':offset, 'numerator':f.numerator, 'denominator':f.denominator}]
            compuMethodElem=autosar.datatype.CompuMethodRational(name,None,semanticElements)
            if (minVal is not None) and (maxVal is not None):
                if (ws.version >= 4.0) and (dataConstraintName is not None):
                    dataConstraintElem = self.createInternalDataConstraint(dataConstraintName, minVal, maxVal)
            elif (minVal is not None) or (maxVal is not None):
                raise ValueError('Invalid combination of arguments')

        elif (minVal is not None) and (maxVal is not None):
            if (ws.version >= 4.0) and (dataConstraintName is not None):
                dataConstraintElem = self.createInternalDataConstraint(dataConstraintName, minVal, maxVal)
        else:
            raise ValueError('Invalid combination of arguments')

        if unit is not None:
            unitElem = None
            if unitPackage is not None:
                unitElem = ws.find(unit, role='Unit')
            if unitElem is None:
                unitElem = autosar.datatype.DataTypeUnitElement(unit,unit)

        compuMethodRef, unitRef, dataConstraintRef = None, None, None
        if compuMethodElem is not None:
            if semanticsPackage is not None:
                semanticsPackage.append(compuMethodElem)
                compuMethodRef = compuMethodElem.ref
            else:
                raise RuntimeError("no package found with role='CompuMethod'")
        if unitElem is not None:
            if unitPackage is not None:
                if unitElem.ref is None:
                    unitPackage.append(unitElem)
                unitRef = unitElem.ref
                if isinstance(compuMethodElem, autosar.datatype.CompuMethodRational):
                    compuMethodElem.unitRef = unitRef
            else:
                raise RuntimeError("no package found with role='Unit'")
        if dataConstraintElem is not None:
            if dataConstraintPackage is not None:
                dataConstraintPackage.append(dataConstraintElem)
                dataConstraintRef = dataConstraintElem.ref
            else:
                raise RuntimeError("no package found with role='DataConstraint'")
        return (compuMethodRef, unitRef, dataConstraintRef)