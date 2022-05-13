import copy
import autosar.component
import autosar.portinterface
import autosar.base
from autosar.element import Element, DataElement
import collections


###################################### Events ###########################################
class Event(Element):
    def __init__(self,name,startOnEventRef=None, parent=None):
        super().__init__(name,parent)
        self.startOnEventRef = startOnEventRef
        self.modeDependency=None #for AUTOSAR3
        self.disabledInModes=None #for AUTOSAR4

class ModeSwitchEvent(Event):
    def __init__(self,name,startOnEventRef=None, activationType='ENTRY', parent=None, version=3.0):
        super().__init__(name, startOnEventRef, parent)
        self.modeInstRef=None
        if version < 4.0:
            if (activationType!='ENTRY') and (activationType != 'EXIT'):
                raise ValueError('activationType argument must be either "ENTRY" or "EXIT"')
        elif version >= 4.0:
            if (activationType=='ENTRY'): activationType='ON-ENTRY'
            if (activationType=='EXIT'): activationType='ON-EXIT'
            if (activationType!='ON-ENTRY') and (activationType != 'ON-EXIT'):
                raise ValueError('activationType argument must be either "ON-ENTRY" or "ON-EXIT"')
        self.activationType = activationType

    def tag(self,version): return 'SWC-MODE-SWITCH-EVENT' if version >= 4.0 else 'MODE-SWITCH-EVENT'

class TimingEvent(Event):
    def __init__(self,name,startOnEventRef=None, period=0, parent=None):
        super().__init__(name, startOnEventRef, parent)
        self.period=int(period)

    def tag(self, version=None):
        return 'TIMING-EVENT'


class DataReceivedEvent(Event):
    def __init__(self, name, startOnEventRef=None, parent=None):
        super().__init__(name, startOnEventRef, parent)
        self.dataInstanceRef=None
        self.swDataDefsProps=[]
    def tag(self, version=None):
        return "DATA-RECEIVED-EVENT"


class OperationInvokedEvent(Event):
    def __init__(self, name, startOnEventRef=None, parent=None):
        super().__init__(name, startOnEventRef, parent)
        self.operationInstanceRef=None
        self.swDataDefsProps=[]

    def tag(self, version=None):
        return "OPERATION-INVOKED-EVENT"

class InitEvent(Event):
    def __init__(self,name,startOnEventRef=None, parent=None):
        super().__init__(name, startOnEventRef, parent)

    def tag(self, version=None):
        return 'INIT-EVENT'

class ModeSwitchAckEvent(Event):
    """
    Represents <MODE-SWITCHED-ACK-EVENT> (AUTOSAR 4)
    """
    def __init__(self, name, startOnEventRef=None, eventSourceRef = None, parent=None):
        super().__init__(name, startOnEventRef, parent)
        self.eventSourceRef = eventSourceRef

    def tag(self, version=None):
        return 'MODE-SWITCHED-ACK-EVENT'


####################################################################################################

class ModeDependency(object):
    def __init__(self):
        self.modeInstanceRefs=[]
    def asdict(self):
        data={'type': self.__class__.__name__,'modeInstanceRefs':[]}
        for modeInstanceRef in self.modeInstanceRefs:
            data['modeInstanceRefs'].append(modeInstanceRef.asdict())
        if len(data['modeInstanceRefs'])==0: del data['modeInstanceRefs']

    def append(self, item):
        if isinstance(item, ModeInstanceRef) or isinstance(item, ModeDependencyRef):
            self.modeInstanceRefs.append(item)
        else:
            raise ValueError('invalid type: '+str(type(item)))

class ModeInstanceRef:
    """
    Implementation of MODE-IREF (AUTOSAR3, AUTOSAR4)
    """
    def __init__(self,modeDeclarationRef,modeDeclarationGroupPrototypeRef=None,requirePortPrototypeRef=None):
        self.modeDeclarationRef=modeDeclarationRef #MODE-DECLARATION-REF
        self.modeDeclarationGroupPrototypeRef=modeDeclarationGroupPrototypeRef #MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.requirePortPrototypeRef=requirePortPrototypeRef #R-PORT-PROTOTYPE-REF
    def asdict(self):
        data={'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key]=value
        return data

    def tag(self,version=None):
        return 'MODE-IREF'

class ModeDependencyRef:
    def __init__(self,modeDeclarationRef,modeDeclarationGroupPrototypeRef=None,requirePortPrototypeRef=None):
        self.modeDeclarationRef=modeDeclarationRef #MODE-DECLARATION-REF
        self.modeDeclarationGroupPrototypeRef=modeDeclarationGroupPrototypeRef #MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.requirePortPrototypeRef=requirePortPrototypeRef #R-PORT-PROTOTYPE-REF
    def asdict(self):
        data={'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key]=value
        return data

    def tag(self,version=None):
        return 'DEPENDENT-ON-MODE-IREF'

class DisabledModeInstanceRef(object):
    def __init__(self,modeDeclarationRef,modeDeclarationGroupPrototypeRef=None,requirePortPrototypeRef=None):
        self.modeDeclarationRef=modeDeclarationRef #MODE-DECLARATION-REF
        self.modeDeclarationGroupPrototypeRef=modeDeclarationGroupPrototypeRef #MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.requirePortPrototypeRef=requirePortPrototypeRef #R-PORT-PROTOTYPE-REF
    def asdict(self):
        data={'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key]=value
        return data

    def tag(self,version=None):
        return 'DISABLED-MODE-IREF'

class ModeGroupInstanceRef:
    """
    Base class for RequireModeGroupInstanceRef and ProvideModeGroupInstanceRef
    """
    def __init__(self, modeGroupRef, parent = None):
        """
        This is a very sneaky XML element. Depending on where it is used in the XML schema (XSD)
        it needs to use different XML tags. We solve this by looking at the parent object.
        """
        self.modeGroupRef = modeGroupRef
        self.parent = parent

class RequireModeGroupInstanceRef(ModeGroupInstanceRef):
    def __init__(self, requirePortRef, modeGroupRef):
        super().__init__(modeGroupRef)
        self.requirePortRef = requirePortRef

    def tag(self, version):
        if self.parent is None:
            raise RuntimeError("self.parent cannot be None")
        if version >= 4.0:
            if isinstance(self.parent, ModeAccessPoint):
                return 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
            else:
                return 'MODE-GROUP-IREF'
        else:
            raise RuntimeError('Not supported in v%.1f'%version)

class ProvideModeGroupInstanceRef(ModeGroupInstanceRef):
    def __init__(self, providePortRef, modeGroupRef):
        super().__init__(modeGroupRef)
        self.providePortRef = providePortRef

    def tag(self, version):
        if self.parent is None:
            raise RuntimeError("self.parent cannot be None")
        if version >= 4.0:
            if isinstance(self.parent, ModeAccessPoint):
                return 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
            else:
                return 'MODE-GROUP-IREF'
        else:
            raise RuntimeError('Not supported in v%.1f'%version)

class PortAPIOption():
    def __init__(self,portRef,takeAddress=False,indirectAPI=False):
        self.portRef = portRef
        self.takeAddress = bool(takeAddress)
        self.indirectAPI = bool(indirectAPI)
    def asdict(self):
        data={'type': self.__class__.__name__,'takeAddress':self.takeAddress, 'indirectAPI':self.indirectAPI, 'portRef':self.portRef}
        return data

    def tag(self,version=None): return "PORT-API-OPTION"

class DataReceivePoint:
    def __init__(self,portRef,dataElemRef=None,name=None,parent=None):
        self.portRef=portRef
        self.dataElemRef=dataElemRef
        self.name=name
        self.parent=parent

    def tag(self,version): return "VARIABLE-ACCESS" if version >= 4.0 else "DATA-RECEIVE-POINT"

class DataSendPoint:
    def __init__(self,portRef,dataElemRef=None,name=None,parent=None):
        self.portRef=portRef
        self.dataElemRef=dataElemRef
        self.name=name
        self.parent=parent

    def tag(self,version): return "VARIABLE-ACCESS" if version >= 4.0 else "DATA-SEND-POINT"

class RunnableEntity(Element):
    def __init__(self, name, invokeConcurrently=False, symbol=None, parent=None, adminData=None):
        super().__init__(name,parent,adminData)
        self.invokeConcurrently = invokeConcurrently
        self.minStartInterval = None
        if symbol is None:
            self.symbol=name
        else:
            self.symbol = symbol
        self.dataReceivePoints=[]
        self.dataSendPoints=[]
        self.serverCallPoints=[]
        self.exclusiveAreaRefs=[]
        self.modeAccessPoints=[] #AUTOSAR4 only
        self.modeSwitchPoints=[] #AUTOSAR4 only
        self.parameterAccessPoints = [] #AUTOSAR4 only

    def tag(self,version=None):
        return 'RUNNABLE-ENTITY'

    def find(self, ref):
        if ref is None: return None
        if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
        ref=ref.partition('/')
        name=ref[0]
        foundElem = None
        for elem in self.modeAccessPoints + self.modeSwitchPoints + self.parameterAccessPoints:
            if elem.name == name:
                foundElem = elem
                break
        if foundElem is not None:
            if len(ref[2])>0:
                return foundElem.find(ref[2])
            else:
                return foundElem
        return None


    def append(self,elem):
        if isinstance(elem, autosar.behavior.DataReceivePoint):
            dataReceivePoint=self._verifyDataReceivePoint(copy.copy(elem))
            self.dataReceivePoints.append(dataReceivePoint)
            dataReceivePoint.parent=self
        elif isinstance(elem, autosar.behavior.DataSendPoint):
            dataSendPoint=self._verifyDataSendPoint(copy.copy(elem))
            self.dataSendPoints.append(dataSendPoint)
            dataSendPoint.parent=self
        else:
            raise NotImplementedError(str(type(elem)))

    def _verifyDataReceivePoint(self,dataReceivePoint):
        ws=self.rootWS()
        assert(ws is not None)
        assert(dataReceivePoint.portRef is not None)
        if isinstance(dataReceivePoint.portRef,autosar.port.Port):
            dataReceivePoint.portRef=dataReceivePoint.portRef.ref
        if isinstance(dataReceivePoint.portRef,str):
            port=ws.find(dataReceivePoint.portRef)
            if dataReceivePoint.dataElemRef is None:
                #default rule: set dataElemRef to ref of first dataElement in the portinterface
                portInterface=ws.find(port.portInterfaceRef)
                assert(portInterface is not None)
                if isinstance(portInterface,(autosar.portinterface.SenderReceiverInterface,autosar.portinterface.ParameterInterface)):
                    dataReceivePoint.dataElemRef=portInterface.dataElements[0].ref
                else:
                    raise ValueError('invalid interface type:%s'%(str(type(portInterface))))
            assert(isinstance(dataReceivePoint.dataElemRef,str))
            dataElement = ws.find(dataReceivePoint.dataElemRef)
            if dataReceivePoint.name is None:
                #default rule: set the name to REC_<port.name>_<dataElement.name>
                dataReceivePoint.name="REC_{0.name}_{1.name}".format(port,dataElement)
        else:
            raise ValueError('%s: portRef must be of type string'%self.ref)
        return dataReceivePoint

    def _verifyDataSendPoint(self,dataSendPoint):
        ws=self.rootWS()
        assert(ws is not None)
        assert(dataSendPoint.portRef is not None)
        if isinstance(dataSendPoint.portRef,autosar.port.Port):
            dataSendPoint.portRef=dataSendPoint.portRef.ref
        if isinstance(dataSendPoint.portRef,str):
            port=ws.find(dataSendPoint.portRef)
            if dataSendPoint.dataElemRef is None:
                #default rule: set dataElemRef to ref of first dataElement in the portinterface
                portInterface=ws.find(port.portInterfaceRef)
                assert(portInterface is not None)
                if isinstance(portInterface,(autosar.portinterface.SenderReceiverInterface,autosar.portinterface.ParameterInterface)):
                    dataSendPoint.dataElemRef=portInterface.dataElements[0].ref
                else:
                    raise ValueError('invalid interface type:%s'%(str(type(portInterface))))
            assert(isinstance(dataSendPoint.dataElemRef,str))
            dataElement = ws.find(dataSendPoint.dataElemRef)
            if dataSendPoint.name is None:
                #default rule: set the name to SEND_<port.name>_<dataElement.name>
                dataSendPoint.name="SEND_{0.name}_{1.name}".format(port,dataElement)
        else:
            raise ValueError('%s: portRef must be of type string'%self.ref)
        return dataSendPoint


    def rootWS(self):
        if self.parent is None:
            return autosar.getCurrentWS()
        else:
            return self.parent.rootWS()

    @property
    def ref(self):
        if self.parent is not None:
            return self.parent.ref+'/%s'%self.name
        else:
            return None

class DataElementInstanceRef(object):
    """
    <DATA-ELEMENT-IREF>
    Note: This object seems to be identical to an <DATA-IREF>
    Note 2: Observe that there are multiple <DATA-ELEMENT-IREF> definitions in the AUTOSAR XSD (used for different purposes)
    """
    def __init__(self,portRef,dataElemRef):
        self.portRef = portRef
        self.dataElemRef = dataElemRef
    def asdict(self):
        data={'type': self.__class__.__name__,'portRef':self.portRef, 'dataElemRef':self.dataElemRef}
        return data
    def tag(self, version=None):
        return 'DATA-ELEMENT-IREF'



class DataInstanceRef(object):
    """
    <DATA-IREF>
    Note: This object seems to be identical to an <DATA-ELEMENT-IREF>
    """
    def __init__(self,portRef,dataElemRef):
        self.portRef = portRef
        self.dataElemRef = dataElemRef
    def asdict(self):
        data={'type': self.__class__.__name__,'portRef':self.portRef, 'dataElemRef':self.dataElemRef}
        return data

    def tag(self, version=None):
        return 'DATA-IREF'


class OperationInstanceRef(object):
    """
    <OBJECT-IREF>
    """
    def __init__(self,portRef,operationRef):
        self.portRef = portRef
        self.operationRef = operationRef

    def asdict(self):
        data={'type': self.__class__.__name__,'portRef':self.portRef, 'operationRef':self.operationRef}
        return data

    def tag(self, version=None):
        return 'OPERATION-IREF'




class PerInstanceMemory(Element):
    """
    AUTOSAR 3 <PER-INSTANCE-MEMORY>
    Note: I don't know why this XML object has both <TYPE> and <TYPE-DEFINITION> where a simple TYPE-TREF should suffice.
    Internally use a typeRef for PerInstanceMemory. We can transform it back to <TYPE> and <TYPE-DEFINITION> when serializing to XML
    """
    def __init__(self, name, typeRef, parent=None):
        super().__init__(name, parent)
        self.typeRef=typeRef
    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name, 'typeRef':self.typeRef}
        return data

    def tag(self, version = None):
        return 'PER-INSTANCE-MEMORY'


class SwcNvBlockNeeds(object):
    """
    AUTOSAR 3 representation of SWC-NV-BLOCK-NEEDS
    """
    def __init__(self,name,numberOfDataSets,readOnly,reliability,resistantToChangedSW,
                 restoreAtStart,writeOnlyOnce,writingFrequency,writingPriority,
                 defaultBlockRef,mirrorBlockRef):
        self.name=name
        self.numberOfDataSets=numberOfDataSets
        assert(isinstance(readOnly,bool))
        self.readOnly=readOnly
        self.reliability=reliability
        assert(isinstance(resistantToChangedSW,bool))
        self.resistantToChangedSW=resistantToChangedSW
        assert(isinstance(restoreAtStart,bool))
        self.restoreAtStart=restoreAtStart
        assert(isinstance(writeOnlyOnce,bool))
        self.writeOnlyOnce=writeOnlyOnce
        self.writingFrequency=writingFrequency
        self.writingPriority=writingPriority
        self.defaultBlockRef=defaultBlockRef
        self.mirrorBlockRef=mirrorBlockRef
        self.serviceCallPorts=[]
    def asdict(self):
        data={'type': self.__class__.__name__,'serviceCallPorts':[]}
        for key, value in self.__dict__.items():
            if 'key'=='serviceCallPorts':
                pass
            else:
                data[key]=value
        if len(data['serviceCallPorts'])==0: del data['serviceCallPorts']
        return data

    def tag(self, version=None):
        return 'SWC-NV-BLOCK-NEEDS'

class NvmBlockConfig:
    """
    Represents NVM block config, used inside an NvmBlockNeeds object.
    All options by default is set to None which means "default configuration".
    In practice a None value means that no XML will be generated for that option.
    Option List:
    - numberOfDataSets: None or int
    - numberOfRomBlocks: None or int
    - ramBlockStatusControl: None or str ('NV-RAM-MANAGER', 'API')
    - reliability: None or str('NO-PROTECTION', 'ERROR-DETECTION', 'ERROR-CORRECTION')
    - writingPriority: None or str ('LOW', 'MEDIUM', 'HIGH')
    - writingFrequency: None or int
    - calcRamBlockCrc: None or bool
    - checkStaticBlockId: None or bool
    - readOnly: None or bool
    - resistantToChangedSw: None or bool
    - restoreAtStartup: None or bool
    - storeAtShutdown: None or bool
    - writeVerification: None or bool
    - writeOnlyOnce: None or bool
    - autoValidationAtShutdown: None or bool
    - useCrcCompMechanism: None or bool
    - storeEmergency: None or bool
    - storeImmediate: None or bool
    - storeCyclic: None or bool
    - cyclicWritePeriod: None or float

    """

    def __init__(self, numberOfDataSets = None,
                 numberOfRomBlocks = None,
                 ramBlockStatusControl = None,
                 reliability = None,
                 writingPriority = None,
                 writingFrequency = None,
                 calcRamBlockCrc = None,
                 checkStaticBlockId = None,
                 readOnly = None,
                 resistantToChangedSw = None,
                 restoreAtStartup = None,
                 storeAtShutdown = None,
                 writeVerification = None,
                 writeOnlyOnce = None,
                 autoValidationAtShutdown = None,
                 useCrcCompMechanism = None,
                 storeEmergency = None,
                 storeImmediate = None,
                 storeCyclic = None,
                 cyclicWritePeriod = None,
                 check_input = True):

        self.numberOfDataSets = numberOfDataSets
        self.numberOfRomBlocks = numberOfRomBlocks
        self.ramBlockStatusControl = ramBlockStatusControl
        self.reliability = reliability
        self.writingPriority = writingPriority
        self.writingFrequency = writingFrequency
        self.calcRamBlockCrc = calcRamBlockCrc
        self.checkStaticBlockId = checkStaticBlockId
        self.readOnly = readOnly
        self.resistantToChangedSw = resistantToChangedSw
        self.restoreAtStartup = restoreAtStartup
        self.storeAtShutdown = storeAtShutdown
        self.writeVerification = writeVerification
        self.writeOnlyOnce = writeOnlyOnce
        self.autoValidationAtShutdown = autoValidationAtShutdown
        self.useCrcCompMechanism = useCrcCompMechanism
        self.storeEmergency = storeEmergency
        self.storeImmediate = storeImmediate
        self.storeCyclic = storeCyclic
        self.cyclicWritePeriod = cyclicWritePeriod

        if isinstance(self.cyclicWritePeriod, int):
            self.cyclicWritePeriod = float(self.cyclicWritePeriod)

        if check_input:
            self.check()

    def check(self):
        if not (self.numberOfDataSets is None or isinstance(self.numberOfDataSets, int) ):
            raise ValueError('numberOfDataSets is incorrectly formatted (None or int expected)')
        if not (self.numberOfRomBlocks is None or isinstance(self.numberOfRomBlocks, int) ):
            raise ValueError('numberOfRomBlocks is incorrectly formatted (None or int expected)')
        if not (self.ramBlockStatusControl is None or isinstance(self.ramBlockStatusControl, str) ):
            raise ValueError('ramBlockStatusControl is incorrectly formatted (None or str expected)')
        if not (self.reliability is None or isinstance(self.reliability, str) ):
            raise ValueError('reliability is incorrectly formatted (None or str expected)')
        if not (self.writingPriority is None or isinstance(self.writingPriority, str) ):
            raise ValueError('writingPriority is incorrectly formatted (None or str expected)')
        if not (self.writingFrequency is None or isinstance(self.writingFrequency, int) ):
            raise ValueError('writingFrequency is incorrectly formatted (None or int expected)')
        if not (self.calcRamBlockCrc is None or isinstance(self.calcRamBlockCrc, bool) ):
            raise ValueError('calcRamBlockCrc is incorrectly formatted (None or bool expected)')
        if not (self.checkStaticBlockId is None or isinstance(self.checkStaticBlockId, bool) ):
            raise ValueError('checkStaticBlockId is incorrectly formatted (None or bool expected)')
        if not (self.readOnly is None or isinstance(self.readOnly, bool) ):
            raise ValueError('readOnly is incorrectly formatted (None or bool expected)')
        if not (self.resistantToChangedSw is None or isinstance(self.resistantToChangedSw, bool) ):
            raise ValueError('resistantToChangedSw is incorrectly formatted (None or bool expected)')
        if not (self.restoreAtStartup is None or isinstance(self.restoreAtStartup, bool) ):
            raise ValueError('restoreAtStartup is incorrectly formatted (None or bool expected)')
        if not (self.storeAtShutdown is None or isinstance(self.storeAtShutdown, bool) ):
            raise ValueError('storeAtShutdown is incorrectly formatted (None or bool expected)')
        if not (self.writeVerification is None or isinstance(self.writeVerification, bool) ):
            raise ValueError('writeVerification is incorrectly formatted (None or bool expected)')
        if not (self.writeOnlyOnce is None or isinstance(self.writeOnlyOnce, bool) ):
            raise ValueError('writeOnlyOnce is incorrectly formatted (None or bool expected)')
        if not (self.autoValidationAtShutdown is None or isinstance(self.autoValidationAtShutdown, bool) ):
            raise ValueError('autoValidationAtShutdown is incorrectly formatted (None or bool expected)')
        if not (self.useCrcCompMechanism is None or isinstance(self.useCrcCompMechanism, bool) ):
            raise ValueError('useCrcCompMechanism is incorrectly formatted (None or bool expected)')
        if not (self.storeEmergency is None or isinstance(self.storeEmergency, bool) ):
            raise ValueError('storeEmergency is incorrectly formatted (None or bool expected)')
        if not (self.storeImmediate is None or isinstance(self.storeImmediate, bool) ):
            raise ValueError('storeImmediate is incorrectly formatted (None or bool expected)')
        if not (self.storeCyclic is None or isinstance(self.storeCyclic, bool) ):
            raise ValueError('storeCyclic is incorrectly formatted (None or bool expected)')
        if not (self.cyclicWritePeriod is None or isinstance(self.cyclicWritePeriod, float) ):
            raise ValueError('cyclicWritePeriod is incorrectly formatted (None or float expected)')


class NvmBlockNeeds(Element):
    """
    AUTOSAR 4 representation of NV-BLOCK-NEEDS

    second argument to the init function should be an instance of (a previously configured) NvmBlockConfig

    """
    def __init__(self, name, blockConfig = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        assert(blockConfig is None or isinstance(blockConfig, NvmBlockConfig))
        if blockConfig is None:
            blockConfig = NvmBlockConfig() #create a default configuration
        self.cfg = blockConfig
    def tag(self, version): return 'NV-BLOCK-NEEDS'

class RoleBasedRPortAssignment(object):
    def __init__(self,portRef,role):
        self.portRef=portRef
        self.role=role
    def asdict(self):
        data={'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key]=value
        return data

    def tag(self, version=None):
        return 'ROLE-BASED-R-PORT-ASSIGNMENT'


class CalPrmElemPrototype(Element):
    """
    <CALPRM-ELEMENT-PROTOTYPE>
    """
    def __init__(self,name, typeRef, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef=typeRef
        self.swDataDefsProps=[]
    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef,'swDataDefsProps':[]}
        if self.adminData is not None:
            data['adminData']=self.adminData.asdict()
        for elem in self.swDataDefsProps:
            data['swDataDefsProps'].append(elem)
        return data

    def tag(self, version=None):
        return 'CALPRM-ELEMENT-PROTOTYPE'


class ExclusiveArea(Element):
    def __init__(self, name, parent=None, adminData=None):
        super().__init__(name,parent,adminData)

    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name}
        return data

    def tag(self, version=None):
        return 'EXCLUSIVE-AREA'



class SyncServerCallPoint(object):
    """
    <SYNCHRONOUS-SERVER-CALL-POINT>
    """
    def __init__(self, name, timeout=0.0):
        self.name=name
        self.timeout=timeout
        self.operationInstanceRefs=[]

    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,'timeout':self.timeout}
        data['operationInstanceRefs'] = [x.asdict() for x in self.operationInstanceRefs]
        if len(data['operationInstanceRefs'])==0: del data['operationInstanceRefs']
        return data

class InternalBehaviorCommon(Element):
    """
    Base class for InternalBehavior (AUTOSAR 3) and SwcInternalBehavior (AUTOSAR 4)
    """
    def __init__(self, name, componentRef, multipleInstance=False, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        if not isinstance(componentRef,str): #this is a helper, in case the user called the function with obj instead of obj.ref
            if hasattr(componentRef,'ref'):
                componentRef=componentRef.ref
        if (componentRef is None) or (not isinstance(componentRef,str)):
            raise ValueError('componentRef: invalid reference')
        self.componentRef=str(componentRef)
        self.multipleInstance = bool(multipleInstance)
        self.events = []
        self.portAPIOptions = []
        self.autoCreatePortAPIOptions = False
        self.runnables = []
        self.exclusiveAreas=[]
        self.perInstanceMemories = []
        self.swc = None


    def createPortAPIOptionDefaults(self):
        self.portAPIOptions = []
        self._initSWC()
        ws = self.rootWS()
        tmp = self.swc.providePorts+self.swc.requirePorts
        for port in sorted(tmp,key=lambda x: x.name.lower()):
            self.portAPIOptions.append(PortAPIOption(port.ref))

    def _initSWC(self):
        """
        sets up self.swc if not already setup
        """
        if self.swc is None:
            ws = self.rootWS()
            assert(ws is not None)
            self.swc = ws.find(self.componentRef)
        assert(self.swc is not None)

    def find(self,ref):
        if ref is None: return None
        if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
        ref=ref.partition('/')
        name=ref[0]
        foundElem = None
        for elem in self.runnables + self.perInstanceMemories + self.exclusiveAreas + self.events:
            if elem.name == name:
                foundElem = elem
                break
        if foundElem is not None:
            if len(ref[2])>0:
                return foundElem.find(ref[2])
            else:
                return foundElem
        return None

    def createRunnable(self, name, portAccess=None, symbol=None, concurrent=False, exclusiveAreas=None, modeSwitchPoint = None, minStartInterval = 0, adminData=None):
        """
        Creates a new runnable and appends it to this InternalBehavior instance
        Parameters:
        * name: <SHORT-NAME> (str)
        * portAccess: List of strings containing port names or "port-name/element" where element can be data-element or an operation (list(str))
        * symbol: Optional symbol name (str). Default is to use self.name string
        * concurrent: Enable/Disable if this runnable can run concurrently (bool).
        * exclusiveAreas: List of strings containing which exclusive areas this runnable will access.
          Note: For mode ports you will at best get read access. If you want to set new modes use modeSwitchPoints.
        * modeSwitchPoint: List of strings containing port names that this runnable will explicitly use for setting modes.
        * minStartInterval: Specifies the time in milliseconds by which two consecutive starts of an ExecutableEntity are guaranteed to be separated.
        * adminData: Optional adminData
        """
        runnable = RunnableEntity(name, concurrent, symbol, self, adminData)
        runnable.minStartInterval = minStartInterval
        self.runnables.append(runnable)
        self._initSWC()
        ws = self.rootWS()
        if portAccess is not None:
            if isinstance(portAccess, str):
                portAccess = [portAccess]
            assert (ws is not None)
            for elem in portAccess:
                ref = elem.partition('/')
                if len(ref[1])==0:
                    #this section is for portAccess where only the port name is mentioned.
                    #This method only works if the port interface has only 1 data element,
                    # i.e. no ambiguity as to what data element is meant
                    port = self.swc.find(ref[0])
                    if port is None:
                        raise ValueError('invalid port reference: '+str(elem))
                    portInterface = ws.find(port.portInterfaceRef, role='PortInterface')
                    if portInterface is None:
                        raise ValueError('invalid portinterface reference: '+str(port.portInterfaceRef))
                    if isinstance(portInterface, (autosar.portinterface.SenderReceiverInterface, autosar.portinterface.NvDataInterface)):
                        if len(portInterface.dataElements)==0:
                            continue
                        elif len(portInterface.dataElements)==1:
                            dataElem=portInterface.dataElements[0]
                            self._createSendReceivePoint(port,dataElem,runnable)
                        else:
                            raise NotImplementedError('port interfaces with multiple data elements not supported')
                    elif isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
                        modeGroup = portInterface.modeGroup
                        self._createModeAccessPoint(port, modeGroup, runnable)
                    else:
                        raise NotImplementedError(type(portInterface))
                else:
                    #this section is for portAccess where both port name and dataelement is represented as "portName/dataElementName"
                    port = self.swc.find(ref[0])
                    if port is None:
                        raise ValueError('invalid port reference: '+str(elem))
                    portInterface = ws.find(port.portInterfaceRef)
                    if portInterface is None:
                        raise ValueError('invalid portinterface reference: '+str(port.portInterfaceRef))
                    if isinstance(portInterface, (autosar.portinterface.SenderReceiverInterface, autosar.portinterface.NvDataInterface)):
                        dataElem=portInterface.find(ref[2])
                        if dataElem is None:
                            raise ValueError('invalid data element reference: '+str(elem))
                        self._createSendReceivePoint(port,dataElem,runnable)
                    elif isinstance(portInterface, autosar.portinterface.ClientServerInterface):
                        operation=portInterface.find(ref[2])
                        if operation is None:
                            raise ValueError('invalid operation reference: '+str(elem))
                        self._createSyncServerCallPoint(port,operation,runnable)
                    else:
                        raise NotImplementedError(type(portInterface))
        if exclusiveAreas is not None:
            if isinstance(exclusiveAreas, str):
                exclusiveAreas =[exclusiveAreas]
            if isinstance(exclusiveAreas, collections.abc.Iterable):
                for exclusiveAreaName in exclusiveAreas:
                    found = False
                    for exclusiveArea in self.exclusiveAreas:
                        if exclusiveArea.name == exclusiveAreaName:
                            found = True
                            runnable.exclusiveAreaRefs.append(exclusiveArea.ref)
                            break
                    if not found:
                        raise ValueError('invalid exclusive area name: '+exclusiveAreaName)
            else:
                raise ValueError('exclusiveAreas must be either string or list')
        if modeSwitchPoint is not None:
            if isinstance(modeSwitchPoint, str):
                modeSwitchPoint = [modeSwitchPoint]
            assert (ws is not None)
            for portName in modeSwitchPoint:
                port = self.swc.find(portName)
                if port is None:
                    raise ValueError('invalid port reference: '+str(portName))
                portInterface = ws.find(port.portInterfaceRef, role='PortInterface')
                if portInterface is None:
                    raise ValueError('invalid portinterface reference: '+str(port.portInterfaceRef))
                if isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
                    modeGroup = portInterface.modeGroup
                    self._createModeSwitchPoint(port, modeGroup, runnable)
                else:
                    raise NotImplementedError(str(type(portInterface)))
        return runnable

    def _createSendReceivePoint(self,port,dataElement,runnable):
        """
        internal function that create a DataReceivePoint of the the port is a require port or
        a DataSendPoint if the port is a provide port
        """
        if isinstance(port,autosar.port.RequirePort):
            receivePoint=DataReceivePoint(port.ref,dataElement.ref,'REC_{0.name}_{1.name}'.format(port,dataElement),runnable)
            runnable.dataReceivePoints.append(receivePoint)
        elif isinstance(port,autosar.port.ProvidePort):
            sendPoint=DataSendPoint(port.ref,dataElement.ref,'SEND_{0.name}_{1.name}'.format(port,dataElement),runnable)
            runnable.dataSendPoints.append(sendPoint)
        else:
            raise ValueError('unexpected type: '+str(type(port)))

    def _createSyncServerCallPoint(self,port,operation,runnable):
        """
        internal function that create a SyncServerCallPoint of the the port is a require port or
        a DataSendPoint if the port is a provide port
        """
        if isinstance(port,autosar.port.RequirePort):
            callPoint=SyncServerCallPoint('SC_{0.name}_{1.name}'.format(port,operation))
            callPoint.operationInstanceRefs.append(OperationInstanceRef(port.ref, operation.ref))
            runnable.serverCallPoints.append(callPoint)
        else:
            raise ValueError('unexpected type: '+str(type(port)))

    def _calcModeInstanceComponentsForRequirePort(self, portName, modeValue):
        self._initSWC()
        ws = self.rootWS()
        port = self.swc.find(portName)
        if port is None:
            raise ValueError('%s: Invalid port name: %s'%(self.swc.name, portName))
        if not isinstance(port, autosar.port.RequirePort):
            raise ValueError('%s: port must be a require-port: %s'%(self.swc.name, portName))
        portInterface = ws.find(port.portInterfaceRef, role='PortInterface')
        if (portInterface is None):
            raise ValueError('invalid port interface reference: '+port.portInterfaceRef)
        if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            if (portInterface.modeGroups is None) or (len(portInterface.modeGroups)==0):
                raise ValueError('port interface %s has no valid mode groups'%portInterface.name)
            if len(portInterface.modeGroups)>1:
                raise NotImplementedError('port interfaces with only one mode group is currently supported')
            modeGroup = portInterface.modeGroups[0]
        elif isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
            modeGroup = portInterface.modeGroup
        else:
            raise NotImplementedError(type(portInterface))
        assert(modeGroup is not None)
        dataType = ws.find(modeGroup.typeRef)
        if (dataType is None):
            raise ValueError('%s has invalid typeRef: %s'%(modeGroup.name, modeGroup.typeRef))
        assert(isinstance(dataType,autosar.mode.ModeDeclarationGroup))
        modeDeclarationRef = None
        modeDeclarationGroupRef = modeGroup.ref
        for modeDeclaration in dataType.modeDeclarations:
            if modeDeclaration.name == modeValue:
                modeDeclarationRef = modeDeclaration.ref
                return (modeDeclarationRef,modeDeclarationGroupRef,port.ref)
        raise ValueError('"%s" did not match any of the mode declarations in %s'%(modeValue,dataType.ref))

    def _createModeAccessPoint(self, port, modeGroup, runnable):
        if isinstance(port, autosar.port.ProvidePort):
            modeGroupInstanceRef = ProvideModeGroupInstanceRef(port.ref, modeGroup.ref)
        else:
            assert isinstance(port, autosar.port.RequirePort)
            modeGroupInstanceRef = RequireModeGroupInstanceRef(port.ref, modeGroup.ref)
        name = None #TODO: support user-controlled name?
        modeAccessPoint = ModeAccessPoint(name, modeGroupInstanceRef)
        runnable.modeAccessPoints.append(modeAccessPoint)

    def _createModeSwitchPoint(self, port, modeGroup, runnable):
        if isinstance(port, autosar.port.ProvidePort):
            modeGroupInstanceRef = ProvideModeGroupInstanceRef(port.ref, modeGroup.ref)
        else:
            assert isinstance(port, autosar.port.RequirePort)
            modeGroupInstanceRef = RequireModeGroupInstanceRef(port.ref, modeGroup.ref)
        baseName='SWITCH_{0.name}_{1.name}'.format(port, modeGroup)
        name = autosar.base.findUniqueNameInList(runnable.modeSwitchPoints, baseName)
        modeSwitchPoint = ModeSwitchPoint(name, modeGroupInstanceRef, runnable)
        runnable.modeSwitchPoints.append(modeSwitchPoint)

    def createModeSwitchEvent(self, runnableName, modeRef, activationType='ENTRY', name=None):
        self._initSWC()
        ws = self.rootWS()
        runnable=self.find(runnableName)
        if runnable is None:
            raise ValueError('invalid runnable name: '+runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))

        eventName=name
        if eventName is None:
            baseName = "MST_"+runnable.name
            eventName = self._findEventName(baseName)

        result = modeRef.partition('/')
        if result[1]!='/':
            raise ValueError('invalid modeRef, expected "portName/modeValue", got "%s"'%modeRef)
        portName = result[0]
        modeValue = result[2]
        event = autosar.behavior.ModeSwitchEvent(eventName,runnable.ref, activationType, version=ws.version)
        (modeDeclarationRef,modeDeclarationGroupRef,portRef) = self._calcModeInstanceComponentsForRequirePort(portName,modeValue)
        event.modeInstRef = ModeInstanceRef(modeDeclarationRef, modeDeclarationGroupRef, portRef)
        assert(isinstance(event.modeInstRef, autosar.behavior.ModeInstanceRef))
        self.events.append(event)
        return event

    def createTimerEvent(self, runnableName, period, modeDependency=None, name=None ):
        self._initSWC()
        ws = self.rootWS()

        runnable=self.find(runnableName)
        if runnable is None:
            raise ValueError('invalid runnable name: '+runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))
        eventName=name
        if eventName is None:
            #try to find a suitable name for the event
            baseName = "TMT_"+runnable.name
            eventName = self._findEventName(baseName)

        event = autosar.behavior.TimingEvent(eventName,runnable.ref,period,self)

        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)
        self.events.append(event)
        return event

    def createTimingEvent(self, runnableName, period, modeDependency=None, name=None):
        """
        alias for createTimerEvent
        """
        return self.createTimerEvent(runnableName, period, modeDependency, name)

    def createOperationInvokedEvent(self, runnableName, operationRef, modeDependency=None, name=None ):
        """
        creates a new OperationInvokedEvent
        runnableName: name of the runnable to call (runnable must already exist)
        operationRef: string using the format 'portName/operationName'
        name: optional event name, used to override only
        """
        self._initSWC()
        ws = self.rootWS()

        runnable=self.find(runnableName)
        if runnable is None:
            raise ValueError('invalid runnable name: '+runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))

        if not isinstance(operationRef, str):
            raise ValueError("expected operationRef to be string of the format 'portName/operationName' ")
        parts = autosar.base.splitRef(operationRef)
        if len(parts)!=2:
            raise ValueError("expected operationRef to be string of the format 'portName/operationName' ")
        portName,operationName=parts[0],parts[1]
        eventName=name
        port = self.swc.find(portName)
        if (port is None) or not isinstance(port, autosar.port.Port):
            raise ValueError('invalid port name: '+portName)
        portInterface = ws.find(port.portInterfaceRef)
        if portInterface is None:
            raise ValueError('invalid reference: '+port.portInterface)
        if not isinstance(portInterface, autosar.portinterface.ClientServerInterface):
            raise ValueError('The referenced port "%s" does not have a ClientServerInterface'%(port.name))
        operation = portInterface.find(operationName)
        if (operation is None) or not isinstance(operation, autosar.portinterface.Operation):
            raise ValueError('invalid operation name: '+operationName)
        if eventName is None:
            eventName=self._findEventName('OIT_%s_%s_%s'%(runnable.name, port.name, operation.name))
        event = OperationInvokedEvent(eventName, runnable.ref, self)
        event.operationInstanceRef=OperationInstanceRef(port.ref, operation.ref)

        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)

        self.events.append(event)
        return event

    def createDataReceivedEvent(self, runnableName, dataElementRef, modeDependency=None, name=None ):
        """
        creates a new DataReceivedEvent
        runnableName: name of the runnable to call (runnable must already exist)
        dataElementRef: string using the format 'portName/dataElementName'. Using 'portName' only is also OK as long as the interface only has one element
        name: optional event name, used to override only
        """
        self._initSWC()
        ws = self.rootWS()

        runnable=self.find(runnableName)
        if runnable is None:
            raise autosar.base.InvalidRunnableRef(runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))

        if not isinstance(dataElementRef, str):
            raise autosar.base.InvalidDataElementRef("expected dataElementRef to be string of the format 'portName' or 'portName/dataElementName' ")

        parts = autosar.base.splitRef(dataElementRef)
        if len(parts)==2:
            portName, dataElementName = parts[0], parts[1]
        elif len(parts)==1:
            portName, dataElementName = parts[0], None
        else:
            raise autosar.base.InvalidDataElementRef("expected dataElementRef to be string of the format 'portName' or 'portName/dataElementName' ")

        eventName=name
        port = self.swc.find(portName)
        if (port is None) or not isinstance(port, autosar.port.Port):
            raise autosar.base.InvalidPortRef(portName)
        portInterface = ws.find(port.portInterfaceRef)
        if portInterface is None:
            raise autosar.base.InvalidPortInterfaceRef('invalid reference: {}'.format(port.portInterface))
        if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            if dataElementName is None:
                if len(portInterface.dataElements) == 1:
                    dataElement = portInterface.dataElements[0]
                elif len(portInterface.dataElements) > 1:
                    raise autosar.base.InvalidDataElementRef("expected dataElementRef to be string of the format 'portName/dataElementName' ")
                else:
                    raise autosar.base.InvalidDataElementRef('portInterface "{}" has no data elements'.format(portInterface.name))
            else:
                dataElement = portInterface.find(dataElementName)
                if not isinstance(dataElement, autosar.element.DataElement):
                    raise autosar.base.InvalidDataElementRef(dataElementName)
                elif dataElement is None:
                    raise autosar.base.InvalidDataElementRef('portInterface "{}" has no operation {}'.format(portInterface.name, dataElementName))
        elif isinstance(portInterface, autosar.portinterface.NvDataInterface):
            if dataElementName is None:
                if len(portInterface.nvDatas) == 1:
                    dataElement = portInterface.nvDatas[0]
                elif len(portInterface.nvDatas) > 1:
                    raise autosar.base.InvalidDataElementRef("expected dataElementRef to be string of the format 'portName/dataElementName' ")
                else:
                    raise autosar.base.InvalidDataElementRef('portInterface "{}" has no nvdata elements'.format(portInterface.name))
            else:
                dataElement = portInterface.find(dataElementName)
                if not isinstance(dataElement, autosar.element.DataElement):
                    raise autosar.base.InvalidDataElementRef(dataElementName)
                elif dataElement is None:
                    raise autosar.base.InvalidDataElementRef('portInterface "{}" has no nvdata {}'.format(portInterface.name, dataElementName))
        else:
            raise autosar.base.InvalidPortRef('The referenced port "{}" does not have a SenderReceiverInterface or NvDataInterface'.format(port.name))
        if eventName is None:
            eventName=self._findEventName('DRT_{}_{}_{}'.format(runnable.name, port.name, dataElement.name))
        event = DataReceivedEvent(eventName, runnable.ref, self)
        event.dataInstanceRef = DataInstanceRef(port.ref, dataElement.ref)

        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)

        self.events.append(event)
        return event

    def _findEventName(self, baseName):
        return autosar.base.findUniqueNameInList(self.events, baseName)




    def _processModeDependency(self, event, modeDependencyList, version):
        for dependency in list(modeDependencyList):
            result = dependency.partition('/')
            if result[1]=='/':
                portName=result[0]
                modeValue=result[2]
                (modeDeclarationRef,modeDeclarationGroupPrototypeRef,portRef) = self._calcModeInstanceComponentsForRequirePort(portName,modeValue)
            else:
                raise ValueError('invalid modeRef, expected "portName/modeValue", got "%s"'%dependency)
            if version >= 4.0:
                if event.disabledInModes is None:
                    event.disabledInModes = []
                event.disabledInModes.append(DisabledModeInstanceRef(modeDeclarationRef, modeDeclarationGroupPrototypeRef, portRef))
            else:
                if event.modeDependency is None:
                    event.modeDependency = ModeDependency()
                event.modeDependency.append(ModeDependencyRef(modeDeclarationRef, modeDeclarationGroupPrototypeRef, portRef))

    def createExclusiveArea(self, name):
        """
        creates a new ExclusiveArea
        """
        self._initSWC()
        ws = self.rootWS()
        exclusiveArea = ExclusiveArea(str(name), self)
        self.exclusiveAreas.append(exclusiveArea)
        return exclusiveArea


class InternalBehavior(InternalBehaviorCommon):
    """ InternalBehavior class (AUTOSAR 3)"""
    def __init__(self,name, componentRef, multipleInstance=False,parent=None):
        super().__init__(name, componentRef,multipleInstance, parent)

        self.swcNvBlockNeeds = []
        self.sharedCalParams=[]


    def tag(self, version): return 'INTERNAL-BEHAVIOR'

    def append(self,elem):
        if isinstance(elem,RunnableEntity):
            self.runnables.append(elem)
            elem.parent=self
        else:
            raise NotImplementedError(str(type(elem)))

    def find(self, ref):
        if ref is None: return None
        result = super().find(ref)
        if result is None:
            if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
            ref=ref.partition('/')
            name=ref[0]
            for elem in self.sharedCalParams:
                if elem.name == name: return elem
        else:
            return result
        return None



    def __getitem__(self,key):
        return self.find(key)


    def createPerInstanceMemory(self, name, typeRef):
        """
        creates a new PerInstanceMemory object
        name: name of the object (str)
        typeRef: dataType reference (str)
        """
        self._initSWC()
        ws = self.rootWS()
        dataType = ws.find(typeRef, role='DataType')
        if dataType is None:
            raise ValueError('invalid reference: '+typeRef)
        perInstanceMemory = PerInstanceMemory(name, dataType.ref, self)
        self.perInstanceMemories.append(perInstanceMemory)
        return perInstanceMemory

    def createSharedCalParam(self, name, typeRef, SwAddrMethodRef, adminData=None):
        self._initSWC()
        ws = self.rootWS()
        dataType = ws.find(typeRef, role='DataType')
        if dataType is None:
            raise ValueError('invalid reference: '+typeRef)
        elem = CalPrmElemPrototype(name, dataType.ref, self, adminData)
        elem.swDataDefsProps.append(SwAddrMethodRef)
        self.sharedCalParams.append(elem)
        return elem

    def createNvmBlock(self, name, blockParams):
        """
        creates a new SwcNvBlockNeeds object
        name: name of the object (str)
        blockParams: dict containing additional parameters
        """
        self._initSWC()
        ws = self.rootWS()
        numberOfDataSets= int(blockParams['numberOfDataSets'])
        readOnly= bool(blockParams['readOnly'])
        reliability= str(blockParams['reliability'])
        resistantToChangedSW= bool(blockParams['resistantToChangedSW'])
        restoreAtStart= bool(blockParams['restoreAtStart'])
        writeOnlyOnce= bool(blockParams['writeOnlyOnce'])
        writingFrequency= str(blockParams['writingFrequency'])
        writingPriority= str(blockParams['writingPriority'])
        defaultBlockRef=None
        mirrorBlockRef=None
        #defaultBlockRef
        defaultBlock = blockParams['defaultBlock']
        if '/' in defaultBlock:
            defaultBlockRef = defaultBlock #use as is
        else:
            for sharedCalParam in self.sharedCalParams:
                if sharedCalParam.name == defaultBlock:
                    defaultBlockRef=sharedCalParam.ref
                    break
        if defaultBlockRef is None:
            raise ValueError('no SharedCalParam found with name: ' +defaultBlock)
        #mirrorBlockref
        mirrorBlock = blockParams['mirrorBlock']
        if '/' in mirrorBlock:
            mirrorBlockRef = mirrorBlock #use as is
        else:
            for perInstanceMemory in self.perInstanceMemories:
                if perInstanceMemory.name == mirrorBlock:
                    mirrorBlockRef=perInstanceMemory.ref
                    break
        if mirrorBlockRef is None:
            raise ValueError('no PerInstanceMemory found with name: ' +mirrorBlock)
        elem = SwcNvBlockNeeds(name, numberOfDataSets, readOnly, reliability, resistantToChangedSW, restoreAtStart,
                                          writeOnlyOnce, writingFrequency, writingPriority, defaultBlockRef, mirrorBlockRef)
        #serviceCallPorts
        if isinstance(blockParams['serviceCallPorts'],str):
            serviceCallPorts=[blockParams['serviceCallPorts']]
        else:
            serviceCallPorts = blockParams['serviceCallPorts']
        if isinstance(serviceCallPorts, collections.abc.Iterable):
            for data in serviceCallPorts:
                parts = autosar.base.splitRef(data)
                if len(parts)!=2:
                    raise ValueError('serviceCallPorts must be either string or list of string of the format "portName/operationName"')
                portName,operationName = parts[0],parts[1]
                port = self.swc.find(portName)
                if not isinstance(port, autosar.port.Port):
                    raise ValueError("'%s' is not a valid port name"%portName)
                elem.serviceCallPorts.append(RoleBasedRPortAssignment(port.ref,operationName))
        else:
            raise ValueError('serviceCallPorts must be either string or list of string of format the "portName/operationName"')

        self.swcNvBlockNeeds.append(elem)
        return elem


class SwcInternalBehavior(InternalBehaviorCommon):
    """
    AUTOSAR 4 Internal Behavior
    """
    def __init__(self,name, componentRef, multipleInstance=False,parent=None):
        super().__init__(name, componentRef, multipleInstance, parent)
        self.serviceDependencies = [] #list of SwcServiceDependency objects
        self.parameterDataPrototype = [] #list of ParameterDataPrototye objects
        self.dataTypeMappingRefs = [] #list of strings

    def tag(self, version): return "SWC-INTERNAL-BEHAVIOR"

    def find(self, ref):
        if ref is None: return None
        result = super().find(ref)
        if result is None:
            if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
            ref=ref.partition('/')
            name=ref[0]
            foundElem = None
            for elem in self.parameterDataPrototype:
                if elem.name == name:
                    foundElem = elem
                    break
            if foundElem is not None:
                if len(ref[2])>0:
                    return foundElem.find(ref[2])
                else:
                    return foundElem
        else:
            return result

    def createPerInstanceMemory(self, name, implementationTypeRef, swAddressMethodRef = None, swCalibrationAccess = None):
        """
        AUTOSAR4: Creates a DataElement object and appends to to the internal perInstanceMemories list
        name: name of the object (str)
        implementationTypeRef: dataType reference (str)
        swAddressMethodRef: Software address method reference (str)
        swCalibrationAccess: software calibration access (str)
        """
        self._initSWC()
        ws = self.rootWS()
        dataType = ws.find(implementationTypeRef, role='DataType')
        if dataType is None:
            raise ValueError('invalid reference: '+implementationTypeRef)
        dataElement = DataElement(name, dataType.ref, swAddressMethodRef = swAddressMethodRef, swCalibrationAccess=swCalibrationAccess, parent=self)
        self.perInstanceMemories.append(dataElement)
        return dataElement

    def createSharedDataParameter(self, name, implementationTypeRef, swAddressMethodRef = None, swCalibrationAccess = None, initValue = None):
        """
        AUTOSAR4: Creates a ParameterDataPrototype object and appends it to the internal parameterDataPrototype list
        """
        self._initSWC()
        ws = self.rootWS()
        dataType = ws.find(implementationTypeRef, role='DataType')
        if dataType is None:
            raise ValueError('invalid reference: '+implementationTypeRef)
        parameter = autosar.element.ParameterDataPrototype(name, dataType.ref, swAddressMethodRef = swAddressMethodRef, swCalibrationAccess=swCalibrationAccess, initValue=initValue, parent=self)
        self.parameterDataPrototype.append(parameter)
        return parameter

    def createNvmBlock(self, name, portName, perInstanceMemoryName, nvmBlockConfig = None, defaultValueName = None, perInstanceMemoryRole='ramBlock', defaultValueRole = 'defaultValue', blockAdminData = None):
        """
        AUTOSAR 4: Creates a ServiceNeeds object and appends it to the internal serviceDependencies list
        This assumes the service needed is related to NVM
        """
        self._initSWC()
        ws = self.rootWS()
        if nvmBlockConfig is None:
            nvmBlockConfig = NvmBlockConfig()
        else:
            assert(isinstance(nvmBlockConfig, NvmBlockConfig))

        nvmBlockNeeds = NvmBlockNeeds(name, nvmBlockConfig, adminData = blockAdminData)
        nvmBlockServiceNeeds = NvmBlockServiceNeeds(name, nvmBlockNeeds)
        serviceDependency = SwcServiceDependency(name, nvmBlockServiceNeeds)

        for port in self.swc.requirePorts:
            if port.name == portName:
                serviceDependency.roleBasedPortAssignments.append(RoleBasedPortAssignment(port.ref))
                break
        else:
            raise ValueError('%s: No require port found with name "%s"'%(self.swc.name, portName))

        for pim in self.perInstanceMemories:
            if pim.name == perInstanceMemoryName:
                serviceDependency.roleBasedDataAssignments.append(RoleBasedDataAssignment(perInstanceMemoryRole, localVariableRef = pim.ref))
                break
        else:
            raise ValueError('%s: No per-instance-memory found with name "%s"'%(self.swc.name, perInstanceMemoryName))
        if defaultValueName is not None:
            for param in self.parameterDataPrototype:
                if param.name == defaultValueName:
                    serviceDependency.roleBasedDataAssignments.append(RoleBasedDataAssignment(defaultValueRole, localParameterRef = param.ref))
                    break
            else:
                raise ValueError('%s: No shared data parameter found with name "%s"'%(self.swc.name, defaultValueName))

        self.serviceDependencies.append(serviceDependency)
        return serviceDependency

    def createInitEvent(self, runnableName, modeDependency=None, name=None ):
        self._initSWC()
        ws = self.rootWS()

        runnable=self.find(runnableName)
        if runnable is None:
            raise ValueError('invalid runnable name: '+runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))

        eventName=name
        if eventName is None:
            baseName = "IT_"+runnable.name
            eventName = self._findEventName(baseName)

        event = autosar.behavior.InitEvent(eventName, runnable.ref)

        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)
        self.events.append(event)
        return event

    def createModeSwitchAckEvent(self, runnableName, modeSwitchSource, modeDependency=None, name=None ):
        """
        Creates a new ModeSwitchAckEvent or <MODE-SWITCHED-ACK-EVENT> (AUTOSAR 4)
        Parameters:
        * runnableName: Name of the runnable to trigger on this event (str)
        * modeSwitchSource: Name of the runnable that has the mode switch point. (str)
                            If the source runnable has multiple mode switch points, use the pattern "RunnableName/ModePortName"
                            To select the correct source point.
        * modeDependency: Modes this runnable shall be disabled in (list(str))
        * name: Event name override (str). Default is to create a name automatically.
        """
        self._initSWC()
        ws = self.rootWS()

        triggerRunnable = self.find(runnableName)
        if triggerRunnable is None:
            raise ValueError('Invalid runnable name: '+triggerRunnable)
        if not isinstance(triggerRunnable, autosar.behavior.RunnableEntity):
            raise ValueError('Element with name {} is not a runnable'.format(runnableName))

        baseName = 'MSAT_'+triggerRunnable.name
        eventName = autosar.base.findUniqueNameInList(self.events, baseName)
        ref = modeSwitchSource.partition('/')
        sourceRunnableName = ref[0]
        sourceModeSwitchPoint = None
        sourceRunnable = self.find(sourceRunnableName)
        if sourceRunnable is None:
            raise ValueError('Invalid runnable name: '+triggerRunnable)
        if not isinstance(sourceRunnable, autosar.behavior.RunnableEntity):
            raise ValueError('Element with name {} is not a runnable'.format(sourceRunnableName))
        if len(sourceRunnable.modeSwitchPoints) == 0:
            raise RuntimeError('Runnable {0.name} must have at least one mode switch point'.format(sourceRunnable))
        if len(ref[1])==0:
            #No '/' delimiter was used. This is OK only when the source runnable has only one modeSwitchPoint (no ambiguity)
                if len(sourceRunnable.modeSwitchPoints) > 1:
                    raise ValueError('Ambiguous use of modeSwitchSource "{}". Please use pattern "RunnableName/PortName" in modeSwitchSource argument')
                sourceModeSwitchPoint = sourceRunnable.modeSwitchPoints[0]
        else:
            #Search through all modeSwitchPoints to find port name that matches second half of the partition split
            modePortName = ref[2]
            for elem in sourceRunnable.modeSwitchPoints[0]:
                port = ws.find(elem.modeGroupInstanceRef.providePortRef)
                if port is None:
                    raise autosar.base.InvalidPortRef(elem.modeGroupInstanceRef.providePortRef)
                if port.name == modePortName:
                    sourceModeSwitchPoint = elem
                    break
            else:
                raise ValueError('Invalid modeSwitchSource argument "{0}": Unable to find a ModeSwitchPoint containing the port name in that runnable'.format(modeSwitchSource))
        assert(sourceModeSwitchPoint is not None)
        #Now that we have collected all the pieces we need we can finally create the event
        assert (triggerRunnable.ref is not None) and (sourceModeSwitchPoint.ref is not None)
        event = ModeSwitchAckEvent(eventName, triggerRunnable.ref, sourceModeSwitchPoint.ref)
        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)
        self.events.append(event)
        return event

    def appendDataTypeMappingRef(self, dataTypeMappingRef):
        """
        Adds dataTypeMappingRef to the internal dataTypeMappingRefs list
        """
        self.dataTypeMappingRefs.append(str(dataTypeMappingRef))

class VariableAccess(Element):
    def __init__(self, name, portPrototypeRef, targetDataPrototypeRef, parent=None):
        super().__init__(name, parent)
        self.portPrototypeRef=portPrototypeRef
        self.targetDataPrototypeRef = targetDataPrototypeRef

    def tag(self, version=None):
        return 'VARIABLE-ACCESS'

class ServiceNeeds(Element):
    """
    Represents <SERVICE-NEEDS> (AUTOSAR 4)
    This is a base class, it is expected that different service needs derive from this class
    """
    def tag(self, version): return 'SERVICE-NEEDS'

    def __init__(self, name = None, nvmBlockNeeds = None, parent=None, adminData = None):
        super().__init__(name, parent, adminData)
        self.nvmBlockNeeds = nvmBlockNeeds

class NvmBlockServiceNeeds(ServiceNeeds):
    def __init__(self, name, nvmBlockNeeds = None, parent=None, adminData = None):
        super().__init__(name, parent, adminData)
        assert(nvmBlockNeeds is None or isinstance(nvmBlockNeeds, NvmBlockNeeds))
        self.nvmBlockNeeds = nvmBlockNeeds

class SwcServiceDependency(Element):
    """
    Represents <SWC-SERVICE-DEPENDENCY> (AUTODSAR 4)
    """
    def tag(self, version): return 'SWC-SERVICE-DEPENDENCY'

    def __init__(self, name=None, serviceNeeds = None, parent=None, adminData = None):
        super().__init__(name, parent, adminData)
        self._serviceNeeds = None #None or ServiceNeeds object
        self.roleBasedDataAssignments = []
        self.roleBasedPortAssignments = []
        if serviceNeeds is not None:
            assert(isinstance(serviceNeeds, ServiceNeeds))
            self.serviceNeeds = serviceNeeds #this uses the setter method

    @property
    def serviceNeeds(self):
        return self._serviceNeeds

    @serviceNeeds.setter
    def serviceNeeds(self, elem):
        elem.parent = self
        self._serviceNeeds = elem

class RoleBasedDataAssignment:
    """
    Represents <ROLE-BASED-DATA-ASSIGNMENT> (AUTOSAR 4)
    """
    def __init__(self, role, localVariableRef=None, localParameterRef=None):
        assert(isinstance(role, str))
        assert(localVariableRef is None or isinstance(localVariableRef, str))
        assert(localParameterRef is None or isinstance(localParameterRef, autosar.behavior.LocalParameterRef) or isinstance(localParameterRef, str))
        self.role = role
        self.localVariableRef = localVariableRef
        self.localParameterRef = localParameterRef

    def tag(self, version): return 'ROLE-BASED-DATA-ASSIGNMENT'

class RoleBasedPortAssignment:
    """
    Represents <ROLE-BASED-PORT-ASSIGNMENT> (AUTOSAR 4)
    """
    def __init__(self, portRef, role = None):
        assert(isinstance(portRef, str))
        self.portRef = portRef
        self.role = role

    def tag(self, version): return 'ROLE-BASED-PORT-ASSIGNMENT'

class ParameterDataPrototype(Element):
    """
    Represents <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)
    """
    def __init__(self, name, typeRef, swAddressMethodRef=None, swCalibrationAccess=None, initValue = None, initValueRef = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef = typeRef
        self.swAddressMethodRef = swAddressMethodRef
        self.swCalibrationAccess = swCalibrationAccess
        self.initValue = initValue
        self.initValueRef = initValueRef

    def tag(self, version): return 'PARAMETER-DATA-PROTOTYPE'

class ParameterInstanceRef:
    """
    Represents <AUTOSAR-PARAMETER-IREF> (AUTOSAR 4)
    """
    def __init__(self, portRef, parameterDataRef):
        self.portRef = portRef
        self.parameterDataRef = parameterDataRef

    def tag(self, version): return 'AUTOSAR-PARAMETER-IREF'

class LocalParameterRef:
    """
    Represents <LOCAL-PARAMETER-REF> (AUTOSAR 4)
    """
    def __init__(self, parameterDataRef):
        self.parameterDataRef = parameterDataRef

    def tag(self, version): return 'LOCAL-PARAMETER-REF'

class ParameterAccessPoint(Element):
    """
    Represents <PARAMETER-ACCESS> (AUTOSAR 4)
    """

    def __init__(self, name, accessedParameter = None, parent = None, adminData = None):
        super().__init__(name, parent, adminData)
        self.accessedParameter = accessedParameter #this can be NoneType or LocalParameterRef or ParameterInstanceRef

    def tag(self, version): return 'PARAMETER-ACCESS'

class ModeAccessPoint:
    """
    Represents <MODE-ACCESS-POINT> (AUTOSAR 4)
    In the XSD this is not a first-class element.
    Therefore we do not inherit from Element but instead allow <SHORT-NAME> only as (optional) identifier
    """
    def __init__(self, name = None, modeGroupInstanceRef = None):
        """
        Arguments:
        * name: <SHORT-NAME> (None or str)
        * modeGroupInstanceRef: <MODE-GROUP-IREF> (None or (class derived from) ModeGroupInstanceRef)
        """
        self.name = str(name) if name is not None else None
        self.modeGroupInstanceRef = modeGroupInstanceRef

    def tag(self, version):
        return 'MODE-ACCESS-POINT'

    @property
    def modeGroupInstanceRef(self):
        return self._modeGroupInstanceRef

    @modeGroupInstanceRef.setter
    def modeGroupInstanceRef(self, value):
        if value is not None:
            if not isinstance(value, ModeGroupInstanceRef):
                raise ValueError("Value must be None or an instance of ModeGroupInstanceRef")
            self._modeGroupInstanceRef = value
            value.parent = self
        else:
            self._modeGroupInstanceRef = None

class ModeSwitchPoint(Element):
    """
    Represents <MODE-SWITCH-POINT> (AUTOSAR 4)
    """
    def __init__(self, name, modeGroupInstanceRef = None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.modeGroupInstanceRef = modeGroupInstanceRef

    def tag(self, version):
        return 'MODE-SWITCH-POINT'

    @property
    def modeGroupInstanceRef(self):
        return self._modeGroupInstanceRef

    @modeGroupInstanceRef.setter
    def modeGroupInstanceRef(self, value):
        if value is not None:
            if not isinstance(value, ModeGroupInstanceRef):
                raise ValueError("Value must be None or an instance of ModeGroupInstanceRef")
            self._modeGroupInstanceRef = value
            value.parent = self
        else:
            self._modeGroupInstanceRef = None

# Behavior parts of NvBlockComponent.

def createNvBlockDescriptor(parent, portAccess, **kwargs):
    """
    Creates a new NvBlockDescriptor object.
    * parent: NvBlockComponent to create descriptor in.
    * portAccess: String containing port names or "port-name/element" where element is Nvdata (str)
    * baseName: overide of the default baseName of the object (str).
    """
    descriptor = None
    nvData = None
    ws = parent.rootWS()
    assert (ws is not None)
    assert (isinstance(portAccess, str))

    adminData = kwargs.get('adminData', None)
    baseName = kwargs.get('baseName', None)
    if baseName is None:
        baseName = 'NvBlckDescr'

    ref = portAccess.partition('/')
    port = parent.find(ref[0])
    if port is None:
        raise ValueError('invalid port reference: '+str(portAccess))
    portInterface = ws.find(port.portInterfaceRef)
    if portInterface is None:
        raise ValueError('invalid portinterface reference: '+str(port.portInterfaceRef))

    if isinstance(portInterface, autosar.portinterface.NvDataInterface):
        if len(ref[1]) == 0:
            #this section is for portAccess where only the port name is mentioned.
            #This method only works if the port interface has only 1 data element,
            # i.e. no ambiguity as to what data element is meant
            if len(portInterface.nvDatas)==1:
                nvData=portInterface.nvDatas[0]
                descriptor = NvBlockDescriptor('{0}_{1.name}_{2.name}'.format(baseName, port, nvData), parent, adminData)
            else:
                raise NotImplementedError('port interfaces with multiple data elements not supported')
        else:
            #this section is for portAccess where both port name and dataelement is represented as "portName/dataElementName"
            if isinstance(portInterface, autosar.portinterface.NvDataInterface):
                nvData=portInterface.find(ref[2])
                if nvData is None:
                    raise ValueError('invalid data element reference: '+str(portAccess))
                descriptor = NvBlockDescriptor('{0}_{1.name}_{2.name}'.format(baseName, port, nvData), parent, adminData)
    else:
        raise autosar.base.InvalidPortInterfaceRef(type(portInterface))

    if descriptor is not None:
        dataTypeMappingRefs = kwargs.get('dataTypeMappingRefs', None)
        nvmBlockConfig = kwargs.get('NvmBlockConfig', None)
        timingEventRef = kwargs.get('timingEventRef', None)
        swCalibrationAccess = kwargs.get('swCalibrationAccess', None)
        supportDirtyFlag = kwargs.get('supportDirtyFlag', False)
        ramBlockAdminData = kwargs.get('ramBlockAdminData', None)
        romBlockAdminData = kwargs.get('romBlockAdminData', None)
        romBlockDesc = kwargs.get('romBlockDesc', None)
        romBlockLongName = kwargs.get('romBlockLongName', None)
        romBlockInitValueRef = kwargs.get('romBlockInitValueRef', None)
        rawRomBlockInitValue = kwargs.get('romBlockInitValue', None)
        romBlockInitValue = None

        if nvmBlockConfig is None or not isinstance(nvmBlockConfig, autosar.behavior.NvmBlockConfig):
            raise autosar.base.InvalidDataTypeRef('NvmBlockConfig is missing or is not an autosar.behavior.NvmBlockConfig')

        descriptor.nvBlockNeeds = autosar.behavior.NvmBlockNeeds('NvmBlockNeed', nvmBlockConfig, parent)

        if dataTypeMappingRefs is not None:
            if isinstance(dataTypeMappingRefs, str):
                dataTypeMappingRefs = [dataTypeMappingRefs]
            descriptor.dataTypeMappingRefs.extend(dataTypeMappingRefs)

        if not isinstance(supportDirtyFlag, bool):
            raise ValueError('supportDirtyFlag must be of bool type: '+str(type(supportDirtyFlag)))

        descriptor.supportDirtyFlag = supportDirtyFlag

        if isinstance(timingEventRef, str):
            timingEvent = parent.behavior.find(timingEventRef)
            if timingEvent is None:
                raise ValueError('invalid data element reference: '+str(timingEventRef))
            descriptor.timingEventRef = timingEvent.name

        #verify compatibility of romBlockInitValueRef
        if romBlockInitValueRef is not None:
            initValueTmp = ws.find(romBlockInitValueRef, role='Constant')
            if initValueTmp is None:
                raise autosar.base.InvalidInitValueRef(str(romBlockInitValueRef))
            if isinstance(initValueTmp,autosar.constant.Constant):
                romBlockInitValueRef=initValueTmp.ref
            elif isinstance(initValueTmp,autosar.constant.Value):
                romBlockInitValueRef=initValueTmp.ref
            else:
                raise ValueError("reference is not a Constant or Value object: '%s'"%romBlockInitValueRef)

        if rawRomBlockInitValue is not None:
            if isinstance(rawRomBlockInitValue, autosar.constant.ValueAR4):
                romBlockInitValue = rawRomBlockInitValue
            elif isinstance(rawRomBlockInitValue, (int, float, str)):
                dataType = ws.find(nvData.typeRef, role='DataType')
                if dataType is None:
                    raise autosar.base.InvalidDataTypeRef(nvData.typeRef)
                valueBuilder = autosar.builder.ValueBuilder()
                romBlockInitValue = valueBuilder.buildFromDataType(dataType, rawRomBlockInitValue)
            else:
                raise ValueError('romBlockInitValue must be an instance of (autosar.constant.ValueAR4, int, float, str)')

        dataType = ws.find(nvData.typeRef, role='DataType')
        if dataType is None:
            raise ValueError('invalid reference: '+nvData.typeRef)
        descriptor.romBlock = NvBlockRomBlock('ParameterDataPt', dataType.ref,
                        swCalibrationAccess=swCalibrationAccess,
                        initValue=romBlockInitValue,
                        initValueRef=romBlockInitValueRef,
                        parent=descriptor,
                        adminData=romBlockAdminData)

        if romBlockDesc is not None:
            descriptor.romBlock.desc = romBlockDesc

        if romBlockLongName is not None:
            descriptor.romBlock.longName = romBlockLongName

        descriptor.ramBlock = NvBlockRamBlock('VariableDataPt', dataType.ref, parent = descriptor, adminData = ramBlockAdminData)

        nvBlockDataMapping = NvBlockDataMapping(descriptor)
        nvBlockDataMapping.nvRamBlockElement = NvRamBlockElement(parent=nvBlockDataMapping, localVariableRef=descriptor.ramBlock)

        if isinstance(port, autosar.port.RequirePort):
            nvBlockDataMapping.writtenNvData = WrittenNvData(parent=nvBlockDataMapping, autosarVariablePortRef=port, autosarVariableElementRef=nvData)

        if isinstance(port, autosar.port.ProvidePort):
            nvBlockDataMapping.readNvData = ReadNvData(parent=nvBlockDataMapping, autosarVariablePortRef=port, autosarVariableElementRef=nvData)

        descriptor.nvBlockDataMappings.append(nvBlockDataMapping)
        parent.nvBlockDescriptors.append(descriptor)
    return descriptor

class NvBlockRamBlock(autosar.element.DataElement):
    """
    <RAM-BLOCK>
    """
    def __init__(self, name, typeRef, isQueued=False, swAddressMethodRef=None, swCalibrationAccess=None, swImplPolicy = None, category = None, parent=None, adminData=None):
        super().__init__(name, typeRef, isQueued, swAddressMethodRef, swCalibrationAccess, swImplPolicy, category, parent, adminData)

    @classmethod
    def cast(cls, ramBlock: autosar.element.DataElement):
        """Cast an autosar.element.DataElement into a NvBlockRamBlock."""
        assert isinstance(ramBlock, autosar.element.DataElement)
        ramBlock.__class__ = cls
        assert isinstance(ramBlock, NvBlockRamBlock)
        return ramBlock

    def tag(self, version):
        return 'RAM-BLOCK'

class NvBlockRomBlock(ParameterDataPrototype):
    """
    Represents <ROM-BLOCK>
    """

    def __init__(self, name, typeRef, swAddressMethodRef=None, swCalibrationAccess=None, initValue = None, initValueRef = None, parent=None, adminData=None):
        super().__init__(name=name, parent=parent, typeRef=typeRef, swAddressMethodRef=swAddressMethodRef, swCalibrationAccess=swCalibrationAccess, initValue=initValue, initValueRef=initValueRef, adminData=adminData)

    @classmethod
    def cast(cls, romBlock: ParameterDataPrototype):
        """Cast an ParameterDataPrototype into a NvBlockRomBlock."""
        assert isinstance(romBlock, ParameterDataPrototype)
        romBlock.__class__ = cls
        assert isinstance(romBlock, NvBlockRomBlock)
        return romBlock

    def tag(self, version): return 'ROM-BLOCK'


class NvBlockDescriptor(Element):
    """
    <NV-BLOCK-DESCRIPTOR>
    """
    def __init__(self, name, parent=None, adminData = None):
        super().__init__(name, parent, adminData)
        self.dataTypeMappingRefs = []
        self.nvBlockDataMappings = []
        self.nvBlockNeeds = None
        self.ramBlock = None
        self.romBlock = None
        self.supportDirtyFlag = False
        self.timingEventRef = None

    def find(self, ref):
        parts=ref.partition('/')
        for elem in self.ramBlock, self.romBlock:
            if elem.name == parts[0]:
                return elem
        return None

    def tag(self, version):
        return 'NV-BLOCK-DESCRIPTOR'

class NvBlockDataMapping(object):
    """
    <NV-BLOCK-DATA-MAPPING>
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.nvRamBlockElement = None
        self.readNvData = None
        self.writtenNvData = None
        self.writtenReadNvData = None

    def tag(self, version):
        return 'NV-BLOCK-DATA-MAPPING'

class AutosarVariableRef(object):
    """
    Base class for type AUTOSAR-VARIABLE-REF
    * localVariableRef: This reference is used if the variable is local to the current component.
    * autosarVariablePortRef: Port part of the autosarVariableRef.
    * autosarVariableElementRef: Element part of the autosarVariableRef.
    """
    def tag(self,version):
        return "AUTOSAR-VARIABLE-REF"

    def __init__(self, parent=None, localVariableRef=None, autosarVariablePortRef=None, autosarVariableElementRef=None):
        self.parent = parent

        if isinstance(localVariableRef,str):
            self.localVariableRef=localVariableRef
        elif hasattr(localVariableRef,'ref'):
            assert(isinstance(localVariableRef.ref,str))
            self.localVariableRef=localVariableRef.ref
        else:
            self.localVariableRef=None

        if isinstance(autosarVariablePortRef,str):
            self.autosarVariablePortRef=autosarVariablePortRef
        elif hasattr(autosarVariablePortRef,'ref'):
            assert(isinstance(autosarVariablePortRef.ref,str))
            self.autosarVariablePortRef=autosarVariablePortRef.ref
        else:
            self.autosarVariablePortRef=None

        if isinstance(autosarVariableElementRef,str):
            self.autosarVariableElementRef=autosarVariableElementRef
        elif hasattr(autosarVariableElementRef,'ref'):
            assert(isinstance(autosarVariableElementRef.ref,str))
            self.autosarVariableElementRef=autosarVariableElementRef.ref
        else:
            self.autosarVariableElementRef=None

class NvRamBlockElement(AutosarVariableRef):
    def __init__(self, parent=None, localVariableRef=None):
        super().__init__(parent=parent, localVariableRef=localVariableRef)

    def tag(self,version):
        return "NV-RAM-BLOCK-ELEMENT"

class ReadNvData(AutosarVariableRef):
    def __init__(self, parent=None, autosarVariablePortRef=None, autosarVariableElementRef=None):
        super().__init__(parent=parent, autosarVariablePortRef=autosarVariablePortRef, autosarVariableElementRef=autosarVariableElementRef)

    def tag(self,version):
        return "READ-NV-DATA"

class WrittenNvData(AutosarVariableRef):
    def __init__(self, parent=None, autosarVariablePortRef=None, autosarVariableElementRef=None):
        super().__init__(parent=parent, autosarVariablePortRef=autosarVariablePortRef, autosarVariableElementRef=autosarVariableElementRef)

    def tag(self,version):
        return "WRITTEN-NV-DATA"

class WrittenReadNvData(AutosarVariableRef):
    def __init__(self, parent=None, autosarVariablePortRef=None, autosarVariableElementRef=None):
        super().__init__(parent=parent, autosarVariablePortRef=autosarVariablePortRef, autosarVariableElementRef=autosarVariableElementRef)

    def tag(self,version):
        return "WRITTEN-READ-NV-DATA"
