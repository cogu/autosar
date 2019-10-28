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

class ModeInstanceRef(object):
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

class ModeDependencyRef(object):
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
    def __init__(self, requirePortRef, modeGroupRef):
        self.requirePortRef = requirePortRef
        self.modeGroupRef = modeGroupRef

    def tag(self, version):
        if version >= 4.0:
            return 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
        else:
            raise RuntimeError('not supported in v%.1f'%version)

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
        self.minStartInterval = 0
        if symbol is None:
            self.symbol=name
        else:
            self.symbol = symbol
        self.dataReceivePoints=[]
        self.dataSendPoints=[]
        self.serverCallPoints=[]
        self.exclusiveAreaRefs=[]
        self.modeAccessPoints=[] #AUTOSAR4 only
        self.parameterAccessPoints = [] #AUTOSAR4 only

    def tag(self,version=None):
        return 'RUNNABLE-ENTITY'

    def asdict(self):
        data={'type': self.__class__.__name__,
              'name':self.name,
              'invokeConcurrently':self.invokeConcurrently,
              'symbol':self.symbol,
              'dataReceivePoints':[],
              'dataSendPoints':[]}
        for dataReceivePoint in self.dataReceivePoints:
            data['dataReceivePoints'].append(dataReceivePoint.asdict())
        for dataSendPoint in self.dataSendPoints:
            data['dataSendPoints'].append(dataSendPoint.asdict())
        if len(self.syncServerCallPoints)>0:
            data['syncServerCallPoints']=[x.asdict for x in self.syncServerCallPoints]
        if len(self.exclusiveAreaRefs)>0:
            data['exclusiveAreaRefs']=[x for x in self.exclusiveAreaRefs]
        if len(data['dataReceivePoints'])==0: del data['dataReceivePoints']
        if len(data['dataSendPoints'])==0: del data['dataSendPoints']
        return data

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
        if isinstance(dataReceivePoint.portRef,autosar.component.Port):
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
        if isinstance(dataSendPoint.portRef,autosar.component.Port):
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

class NvBlockNeeds(Element):
    """
    AUTOSAR 4 representation of NV-BLOCK-NEEDS
    """
    def __init__(self, name, numberOfDataSets = 0, ramBlockStatusControl = 'NV-RAM-MANAGER', reliability='NO-PROTECTION', restoreAtStart=True, storeAtShutdown=True, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.numberOfDataSets=numberOfDataSets
        self.ramBlockStatusControl = ramBlockStatusControl
        self.reliability = reliability
        assert(isinstance(restoreAtStart,bool))
        self.restoreAtStart = restoreAtStart
        assert(isinstance(storeAtShutdown,bool))
        self.storeAtShutdown = storeAtShutdown

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
    def __init__(self,name,timeout=0.0):
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
        for elem in self.runnables:
            if elem.name == name: return elem
        for elem in self.perInstanceMemories:
            if elem.name == name: return elem
        for elem in self.exclusiveAreas:
            if elem.name == name: return elem
        return None

    def createRunnable(self, name, portAccess=None, symbol=None, concurrent=False, exclusiveAreas=None, adminData=None):
        runnable = RunnableEntity(name, concurrent, symbol, self, adminData)
        self.runnables.append(runnable)
        if portAccess is not None:
            self._initSWC()
            ws = self.rootWS()
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
                    if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
                        if len(portInterface.dataElements)==0:
                            continue
                        elif len(portInterface.dataElements)==1:
                            dataElem=portInterface.dataElements[0]
                            self._createSendReceivePoint(port,dataElem,runnable)
                        else:
                            raise NotImplementedError('port interfaces with multiple data elements not supported')
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
                    if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
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
            if isinstance(exclusiveAreas, collections.Iterable):
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
        return runnable

    def _createSendReceivePoint(self,port,dataElement,runnable):
        """
        internal function that create a DataReceivePoint of the the port is a require port or
        a DataSendPoint if the port is a provide port
        """
        if isinstance(port,autosar.component.RequirePort):
            receivePoint=DataReceivePoint(port.ref,dataElement.ref,'REC_{0.name}_{1.name}'.format(port,dataElement),runnable)
            runnable.dataReceivePoints.append(receivePoint)
        elif isinstance(port,autosar.component.ProvidePort):
            sendPoint=DataSendPoint(port.ref,dataElement.ref,'SEND_{0.name}_{1.name}'.format(port,dataElement),runnable)
            runnable.dataSendPoints.append(sendPoint)
        else:
            raise ValueError('unexpected type: '+str(type(port)))

    def _createSyncServerCallPoint(self,port,operation,runnable):
        """
        internal function that create a SyncServerCallPoint of the the port is a require port or
        a DataSendPoint if the port is a provide port
        """
        if isinstance(port,autosar.component.RequirePort):
            callPoint=SyncServerCallPoint('SC_{0.name}_{1.name}'.format(port,operation))
            callPoint.operationInstanceRefs.append(OperationInstanceRef(port.ref, operation.ref))
            runnable.serverCallPoints.append(callPoint)
        else:
            raise ValueError('unexpected type: '+str(type(port)))
    def calcModeInstanceComponents(self, portName, modeValue):
        self._initSWC()
        ws = self.rootWS()
        port = self.swc.find(portName)
        if port is None:
            raise ValueError('%s: Invalid port name: %s'%(self.swc.name, portName))
        if not isinstance(port, autosar.component.RequirePort):
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
        assert(isinstance(dataType,autosar.portinterface.ModeDeclarationGroup))
        modeDeclarationRef = None
        modeDeclarationGroupRef = modeGroup.ref
        for modeDeclaration in dataType.modeDeclarations:
            if modeDeclaration.name == modeValue:
                modeDeclarationRef = modeDeclaration.ref
                return (modeDeclarationRef,modeDeclarationGroupRef,port.ref)
        raise ValueError('"%s" did not match any of the mode declarations in %s'%(modeValue,dataType.ref))


    def createModeSwitchEvent(self, runnableName, modeRef, activationType='ENTRY', name=None):
        self._initSWC()
        ws = self.rootWS()
        runnable=self.find(runnableName)
        if runnable is None:
            raise ValueError('invalid runnable name: '+runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))
        nameBase = "MST_"+runnable.name
        index = 0
        #try to find a suitable name for the event
        eventName = name
        if eventName is None:
            while(True):
                eventName= "%s_%d"%(nameBase,index)
                found = False
                for event in self.events:
                    if event.name == eventName:
                        found = True
                        break
                if found:
                    index+=1
                else:
                    break

        result = modeRef.partition('/')
        if result[1]!='/':
            raise ValueError('invalid modeRef, expected "portName/modeValue", got "%s"'%modeRef)
        portName=result[0]
        modeValue=result[2]
        event = autosar.behavior.ModeSwitchEvent(eventName,runnable.ref,activationType, version=ws.version)
        (modeDeclarationRef,modeDeclarationGroupRef,portRef) = self.calcModeInstanceComponents(portName,modeValue)
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

        event = autosar.behavior.TimingEvent(eventName,runnable.ref,period)

        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)
        self.events.append(event)
        return event

    def createTimingEvent(self, runnableName, period, modeDependency=None, name=None):
        """
        alias for createTimerEvent
        """
        self.createTimerEvent(runnableName, period, modeDependency, name)

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
        if (port is None) or not isinstance(port, autosar.component.Port):
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
            raise ValueError('invalid runnable name: '+runnableName)
        assert(isinstance(runnable, autosar.behavior.RunnableEntity))

        if not isinstance(dataElementRef, str):
            raise ValueError("expected dataElementRef to be string of the format 'portName/dataElementName' ")
        parts = autosar.base.splitRef(dataElementRef)
        if len(parts)==2:
            raise ValueError("expected dataElementRef to be string of the format 'portName/dataElementName' ")
            portName,dataElementName=parts[0],parts[1]
        elif len(parts)==1:
            portName,dataElementName=parts[0],None
        eventName=name
        port = self.swc.find(portName)
        if (port is None) or not isinstance(port, autosar.component.Port):
            raise ValueError('invalid port name: '+portName)
        portInterface = ws.find(port.portInterfaceRef)
        if portInterface is None:
            raise ValueError('invalid reference: '+port.portInterface)
        if not isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            raise ValueError('The referenced port "%s" does not have a SenderReceiverInterface'%(port.name))
        if dataElementName is None:
            if len(portInterface.dataElements)==1:
                dataElement=portInterface.dataElements[0]
            elif len(portInterface.dataElements)>1:
                raise ValueError("expected dataElementRef to be string of the format 'portName/dataElementName' ")
            else:
                raise ValueError('portInterface "%s" has no data elements'%portInterface.name)
        else:
            dataElement = portInterface.find(dataElementName)
            if (dataElement is None) or not isinstance(dataElement, autosar.portinterface.Operation):
                raise ValueError('invalid data element name: ' + dataElementName )
        if eventName is None:
            eventName=self._findEventName('DRT_%s_%s_%s'%(runnable.name, port.name, dataElement.name))
        event = DataReceivedEvent(eventName, runnable.ref, self)
        event.dataInstanceRef=DataInstanceRef(port.ref, dataElement.ref)

        if modeDependency is not None:
            self._processModeDependency(event, modeDependency, ws.version)

        self.events.append(event)
        return event

    def _findEventName(self, baseName):
        found = False
        for event in self.events:
            if event.name == self.events:
                found = True
                break
        if found:
            event.name=event.name+'_0'
            index = 1
            eventName = None
            while(True):
                eventName= "%s_%d"%(baseName,index)
                found = False
                for event in self.events:
                    if event.name == eventName:
                        found = True
                        break
                if found:
                    index+=1
                else:
                    break
        else:
            eventName = baseName
        return eventName

    def _processModeDependency(self, event, modeDependencyList, version):
        for dependency in list(modeDependencyList):
            result = dependency.partition('/')
            if result[1]=='/':
                portName=result[0]
                modeValue=result[2]
                (modeDeclarationRef,modeDeclarationGroupPrototypeRef,portRef) = self.calcModeInstanceComponents(portName,modeValue)
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


    # def asdict(self):
    #    data={'type': self.__class__.__name__,'name':self.name, 'multipleInstance':self.multipleInstance,
    #          'componentRef':self.componentRef, 'events':[],'portAPIOptions':[],'runnables':[],'perInstanceMemories':[],
    #          'swcNvBlockNeeds':[],'sharedCalPrms':[],'exclusiveAreas':[]}
    #    for event in self.events:
    #       data['events'].append(event.asdict())
    #    for portAPIOption in self.portAPIOptions:
    #       data['portAPIOptions'].append(portAPIOption.asdict())
    #    for runnable in self.runnables:
    #       data['runnables'].append(runnable.asdict())
    #    for perInstanceMemory in self.perInstanceMemories:
    #       data['perInstanceMemories'].append(perInstanceMemory.asdict())
    #    for swcNvBlockNeed in self.swcNvBlockNeeds:
    #       data['swcNvBlockNeeds'].append(swcNvBlockNeed.asdict())
    #    for sharedCalPrm in self.sharedCalPrms:
    #       data['sharedCalPrms'].append(sharedCalPrm.asdict())
    #    for exclusiveArea in self.exclusiveAreas:
    #       data['exclusiveAreas'].append(exclusiveArea.asdict())
    #    if len(data['events'])==0: del data['events']
    #    if len(data['portAPIOptions'])==0: del data['portAPIOptions']
    #    if len(data['runnables'])==0: del data['runnables']
    #    if len(data['perInstanceMemories'])==0: del data['perInstanceMemories']
    #    if len(data['swcNvBlockNeeds'])==0: del data['swcNvBlockNeeds']
    #    if len(data['sharedCalPrms'])==0: del data['sharedCalPrms']
    #    if len(data['exclusiveAreas'])==0: del data['exclusiveAreas']
    #    return data


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
        if isinstance(serviceCallPorts, collections.Iterable):
            for data in serviceCallPorts:
                parts = autosar.base.splitRef(data)
                if len(parts)!=2:
                    raise ValueError('serviceCallPorts must be either string or list of string of the format "portName/operationName"')
                portName,operationName = parts[0],parts[1]
                port = self.swc.find(portName)
                if not isinstance(port, autosar.component.Port):
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
            for elem in self.parameterDataPrototype:
                if elem.name == name: return elem
        else:
            return result
        return None

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

    def createSharedParameter(self, name, implementationTypeRef, swAddressMethodRef = None, swCalibrationAccess = None):
        """
        AUTOSAR4: Creates a ParameterDataPrototype object and appends it to the internal parameterDataPrototype list
        """
        self._initSWC()
        ws = self.rootWS()
        dataType = ws.find(implementationTypeRef, role='DataType')
        if dataType is None:
            raise ValueError('invalid reference: '+implementationTypeRef)
        parameter = ParameterDataPrototype(name, dataType.ref, swAddressMethodRef = swAddressMethodRef, swCalibrationAccess=swCalibrationAccess, parent=self)
        self.parameterDataPrototype.append(parameter)
        return parameter

    def createNvmBlock(self, name, portName, perInstanceMemoryName, perInstanceMemoryRole='ramBlock', nvBlockNeeds = None):
        """
        AUTOSAR 4: Creates a ServiceNeeds object and appends it to the internal serviceDependencies list
        This assumes the service needed is related to NVM
        """
        self._initSWC()
        ws = self.rootWS()
        if nvBlockNeeds is None:
            nvBlockNeeds = NvBlockNeeds(name)
        dependency = SwcServiceDependency(name)
        service = dependency.serviceNeeds = ServiceNeeds()
        service.nvBlockNeeds = nvBlockNeeds

        for port in self.swc.requirePorts:
            if port.name == portName:
                dependency.roleBasedPortAssignments.append(RoleBasedPortAssignment(port.ref))
                break
        else:
            raise ValueError('%s: No require port found with name "%s"'%(self.swc.name, portName))

        for pim in self.perInstanceMemories:
            if pim.name == perInstanceMemoryName:
                dependency.roleBasedDataAssignments.append(RoleBasedDataAssignment(perInstanceMemoryRole, pim.ref))
                break
        else:
            raise ValueError('%s: No per-instance-memory found with name "%s"'%(self.swc.name, perInstanceMemoryName))
        self.serviceDependencies.append(dependency)
        return dependency


class VariableAccess(Element):
    def __init__(self, name, portPrototypeRef, targetDataPrototypeRef, parent=None):
        super().__init__(name, parent)
        self.portPrototypeRef=portPrototypeRef
        self.targetDataPrototypeRef = targetDataPrototypeRef

    def tag(self, version=None):
        return 'VARIABLE-ACCESS'

class ServiceNeeds(Element):
    """
    Represents <SERVICE-NEEDS> (AUTODSAR 4)
    """
    def tag(self, version): return 'SERVICE-NEEDS'

    def __init__(self, name = None, nvBlockNeeds = None, parent=None, adminData = None):
        super().__init__(name, parent, adminData)
        self.nvBlockNeeds = nvBlockNeeds

class SwcServiceDependency(Element):
    """
    Represents <SWC-SERVICE-DEPENDENCY> (AUTODSAR 4)
    """
    def tag(self, version): return 'SWC-SERVICE-DEPENDENCY'

    def __init__(self, name=None, parent=None, adminData = None):
        super().__init__(name, parent, adminData)
        self._serviceNeeds = None
        self.roleBasedDataAssignments = []
        self.roleBasedPortAssignments = []

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
        self.role = role
        self.localVariableRef = localVariableRef
        self.localParameterRef = localParameterRef

    def tag(self, version): return 'ROLE-BASED-DATA-ASSIGNMENT'

class RoleBasedPortAssignment:
    """
    Represents <ROLE-BASED-PORT-ASSIGNMENT> (AUTOSAR 4)
    """
    def __init__(self, portRef):
        self.portRef = portRef

    def tag(self, version): return 'ROLE-BASED-PORT-ASSIGNMENT'

class ParameterDataPrototype(Element):
    """
    Represents <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)
    """

    def __init__(self, name, typeRef, swAddressMethodRef=None, swCalibrationAccess=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.typeRef = typeRef
        self.swAddressMethodRef = swAddressMethodRef
        self.swCalibrationAccess = swCalibrationAccess

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
