from autosar.element import Element
import autosar.portinterface
import autosar.constant
import copy
import collections
import sys

class ComponentType(Element):
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.requirePorts=[]
        self.providePorts=[]

    def asdict(self):
        data={'type': self.__class__.__name__, 'name':self.name, 'requirePorts':[], 'providePorts':[]}
        for port in self.requirePorts:
            data['requirePorts'].append(port.asdict())
        for port in self.providePorts:
            data['providePorts'].append(port.asdict())
        if len(data['requirePorts'])==0: del data['requirePorts']
        if len(data['providePorts'])==0: del data['providePorts']
        return data

    def find(self,ref):
        ref=ref.partition('/')
        for port in self.requirePorts:
            if port.name == ref[0]:
                return port
        for port in self.providePorts:
            if port.name == ref[0]:
                return port
        return None

    def append(self, elem):
        if isinstance(elem,RequirePort):
            self.requirePorts.append(elem)
            elem.parent=self
        elif isinstance(elem,ProvidePort):
            self.providePorts.append(elem)
            elem.parent=self
        else:
            raise ValueError("unexpected type:" + str(type(elem)))

    def __getitem__(self,key):
        return self.find(key)

    def createProvidePort(self,name,portInterfaceRef,elemName=None,initValueRef=None,canInvalidate=False):
        ws = self.rootWS()
        assert(ws is not None)
        portInterface = ws.find(portInterfaceRef, role='PortInterface')
        if portInterface is None:
            raise ValueError('invalid reference: '+portInterfaceRef)
        if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            comspec={'canInvalidate':canInvalidate}
            if initValueRef is not None:
                comspec['initValueRef']=initValueRef
            if elemName is not None:
                comspec['name']=elemName
        elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            comspec=[]
            for operation in portInterface.operations:
                comspec.append({'operation': operation.name})
        elif isinstance(portInterface,autosar.portinterface.ParameterInterface):
            pass
        else:
            raise NotImplementedError(type(portInterface))
        port = ProvidePort(name,portInterface.ref,comspec,parent=self)
        self.providePorts.append(port)
        return port

    def createRequirePort(self, name, portInterfaceRef, elemName=None, initValue=None, initValueRef=None, aliveTimeout=0, canInvalidate=False, queueLength=None):
        """
        creates a require port on this ComponentType
        The ComponentType must have a valid ref (must belong to a valid package in a valid workspace).
        """
        comspec = None
        assert (self.ref is not None)
        ws = self.rootWS()
        assert(ws is not None)
        portInterface = ws.find(portInterfaceRef, role='PortInterface')
        if portInterface is None:
            raise ValueError('invalid reference: '+portInterfaceRef)
        if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
            if len(portInterface.dataElements)>0:
                comspec={'canInvalidate':canInvalidate,'aliveTimeout':aliveTimeout}
                if initValue is not None:
                    if initValueRef is not None:
                        raise ValueError('A port cannot have both initValue and initValueRef set at the same time')
                    comspec['initValue']=initValue
                if initValueRef is not None:
                    if initValue is not None:
                        raise ValueError('A port cannot have both initValue and initValueRef set at the same time')
                    comspec['initValueRef']=initValueRef
                if elemName is not None:
                    comspec['name']=elemName
                if queueLength is not None:
                    comspec['queueLength']=int(queueLength)
        elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            comspec=[]
            for operation in portInterface.operations:
                comspec.append({'operation': operation.name})
        elif isinstance(portInterface,autosar.portinterface.ParameterInterface):
            comspec={}
            if initValue is not None:
                comspec['initValue']=initValue
        elif isinstance(portInterface,autosar.portinterface.ModeSwitchInterface):
            comspec={'enhancedMode':False, 'supportAsync':False}
        else:
            raise NotImplementedError(type(portInterface))
        port = RequirePort(name,portInterface.ref,comspec,parent=self)
        self.requirePorts.append(port)
        return port

    def apply(self, template, **kwargs):
        """
        Applies template to this component
        This is typically used for port templates
        """
        if len(kwargs) == 0:
            template.apply(self)
        else:
            template.apply(self, **kwargs)
        template.usageCount+=1

    def copyPort(self, otherPort):
        """
        Adds a copy of a port (from another component)
        """
        self.append(otherPort.copy())

    def mirrorPort(self, otherPort):
        """
        Adds a mirrored copy of a port (from another component)
        """
        self.append(otherPort.mirror())

class AtomicSoftwareComponent(ComponentType):
    """
    base class for ApplicationSoftwareComponent and ComplexDeviceDriverComponent
    """
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.behavior=None
        self.implementation=None

    def find(self,ref):
        ws = self.rootWS()
        ref=ref.partition('/')
        for port in self.requirePorts:
            if port.name == ref[0]:
                return port
        for port in self.providePorts:
            if port.name == ref[0]:
                return port
        if (ws is not None) and (ws.version >= 4.0) and (self.behavior is not None):
            if self.behavior.name == ref[0]:
                if len(ref[2])>0:
                    return self.behavior.find(ref[2])
                else:
                    return self.behavior
        return None


class ApplicationSoftwareComponent(AtomicSoftwareComponent):

    def tag(self,version=None): return 'APPLICATION-SW-COMPONENT-TYPE' if version>=4.0 else 'APPLICATION-SOFTWARE-COMPONENT-TYPE'

    def __init__(self,name,parent=None):
        super().__init__(name,parent)

class ComplexDeviceDriverComponent(AtomicSoftwareComponent):
    def tag(self,version=None): return "COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE"

    def __init__(self,name,parent=None):
        super().__init__(name,parent)

class ServiceComponent(AtomicSoftwareComponent):
    def tag(self,version=None): return "SERVICE-COMPONENT-TYPE"

    def __init__(self,name,parent=None):
        super().__init__(name,parent)

class ParameterComponent(AtomicSoftwareComponent):
    def tag(self,version=None):
        if version < 4.0:
            return "CALPRM-COMPONENT-TYPE"
        else:
            return "PARAMETER-SW-COMPONENT-TYPE"

    def __init__(self,name,parent=None):
        super().__init__(name,parent)

class CompositionComponent(ComponentType):
    """
    Composition Component
    """
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.components=[]
        self.assemblyConnectors=[]
        self.delegationConnectors=[]

    def tag(self,version): return 'COMPOSITION-SW-COMPONENT-TYPE' if version >= 4.0 else 'COMPOSITION-TYPE'

    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name,'requirePorts':[],'providePorts':[],'components':[],
           'assemblyConnectors':[], 'delegationConnectors':[]}
        for port in self.requirePorts:
            data['requirePorts'].append(port.asdict())
        for port in self.providePorts:
            data['providePorts'].append(port.asdict())
        for component in self.components:
            data['components'].append(component.asdict())
        for connector in self.assemblyConnectors:
            data['assemblyConnectors'].append(connector.asdict())
        for connector in self.delegationConnectors:
            data['delegationConnectors'].append(connector.asdict())
        if len(data['requirePorts'])==0: del data['requirePorts']
        if len(data['providePorts'])==0: del data['providePorts']
        if len(data['components'])==0: del data['components']
        if len(data['assemblyConnectors'])==0: del data['assemblyConnectors']
        if len(data['delegationConnectors'])==0: del data['delegationConnectors']
        return data

    def find(self,ref):
        parts=ref.partition('/')
        for elem in self.components:
            if elem.name == parts[0]:
                return elem
        for elem in self.assemblyConnectors:
            if elem.name == parts[0]:
                return elem
        for elem in self.delegationConnectors:
            if elem.name == parts[0]:
                return elem
        return super().find(ref)


    def createComponentRef(self, componentRef):
        """
        creates a new ComponentPrototype object and appends it to the CompositionComponent
        """
        ws = self.rootWS()
        component = ws.find(componentRef, role='ComponentType')
        if component is None:
            raise ValueError('invalid reference: '+componentRef)
        elem = ComponentPrototype(component.name, component.ref, self)
        self.components.append(elem)
        return elem


    def createConnector(self, portRef1, portRef2):
        """
        creates a connector between an inner and outer port or between two inner ports
        portRef1 and portRef2 can be of either formats:
        'componentName/portName', 'portName' or 'componentRef/portName'
        """
        ws = self.rootWS()
        assert (ws is not None)
        port1, component1 = self._analyzePortRef(ws, portRef1)
        port2, component2 = self._analyzePortRef(ws, portRef2)

        if isinstance(component1, ComponentPrototype) and isinstance(component2, ComponentPrototype):
            #create an assembly port between the two ports
            providePort=None
            requirePort=None
            if isinstance(port1, RequirePort) and isinstance(port2, ProvidePort):
                requesterComponent, providerComponent = component1, component2
                requirePort, providePort = port1, port2
            elif isinstance(port2, RequirePort) and isinstance(port1, ProvidePort):
                requesterComponent, providerComponent = component2, component1
                requirePort, providePort = port2, port1
            elif isinstance(port2, RequirePort) and isinstance(port1, RequirePort):
                raise ValueError('cannot create assembly connector between two require ports')
            else:
                raise ValueError('cannot create assembly connector between two provide ports')
            return self._createAssemblyPortInternal(providerComponent, providePort, requesterComponent, requirePort)
        elif isinstance(component1, ComponentPrototype):
            #create a delegation port between port1 and port2
            innerComponent, innerPort=component1,port1
            outerPort = port2
        elif component1 is self and isinstance(component2, ComponentPrototype):
            #create a delegation port between port1 and port2
            innerComponent, innerPort=component2, port2
            outerPort = port1
        else:
            raise ValueError('invalid connector arguments ("%s", "%s")'%(portRef1, portRef2))
        #create delegation connector
        return self._createDelegationConnectorInternal(innerComponent, innerPort, outerPort)

    def _createAssemblyPortInternal(self, providerComponent, providePort, requesterComponent, requirePort):
        connectorName='_'.join([providerComponent.name, providePort.name, requesterComponent.name, requirePort.name])
        connector = AssemblyConnector(connectorName, ProviderInstanceRef(providerComponent.ref,providePort.ref), RequesterInstanceRef(requesterComponent.ref,requirePort.ref))
        if self.find(connectorName) is not None:
            raise ValueError('connector "%s" already exists'%connectorName)
        self.assemblyConnectors.append(connector)
        return connector

    def _createDelegationConnectorInternal(self, innerComponent, innerPort, outerPort):
        if isinstance(outerPort, ProvidePort):
            connectorName = '_'.join([innerComponent.name, innerPort.name, outerPort.name])
        else:
            connectorName = '_'.join([outerPort.name, innerComponent.name, innerPort.name])
        connector = DelegationConnector(connectorName, InnerPortInstanceRef(innerComponent.ref, innerPort.ref), OuterPortRef(outerPort.ref))
        self.delegationConnectors.append(connector)
        return connector

    def _analyzePortRef(self, ws, portRef):
        parts=autosar.base.splitRef(portRef)
        if len(parts)>1:
            if len(parts)==2:
                #assume format 'componentName/portName' with ComponentType role set
                port=None
                for innerComponent in self.components:
                    component = ws.find(innerComponent.typeRef)
                    if component is None:
                        raise ValueError('invalid reference: '+innerComponent.typeRef)
                    if component.name == parts[0]:
                        port = component.find(parts[1])
                        component = innerComponent
                        if port is None:
                            raise ValueError('component %s does not have port with name %s'%(component.name,parts[1]))
                        break
            else:
                #assume portRef1 is a full reference
                port = ws.find(portRef)
        else:
            port = self.find(parts[0])
            component=self
        if port is None or not isinstance(port, Port):
            raise ValueError('%s: invalid port name: %s'%(self.name,parts[-1]))
        return port,component

    def autoConnect(self):
        """
        Connect ports with matching names and matching port interface references
        """
        ws = self.rootWS()
        assert (ws is not None)
        inner_require_port_map, inner_provide_port_map = self._buildInnerPortMap(ws)
        self._autoCreateAssemblyConnectors(inner_require_port_map, inner_provide_port_map)
        self._autoCreateDelegationConnectors(inner_require_port_map, inner_provide_port_map)

    def _buildInnerPortMap(self, ws):
        require_ports = {}
        provide_ports = {}
        #build inner map
        for innerComponent in self.components:
            actualComponent = ws.find(innerComponent.typeRef)
            if actualComponent is None:
                raise ValueError('invalid reference: '+innerComponent.typeRef)
            for innerPort in actualComponent.requirePorts:
                if innerPort.name not in require_ports:
                    require_ports[innerPort.name] = []
                require_ports[innerPort.name].append((innerComponent, innerPort))
            for innerPort in actualComponent.providePorts:
                if innerPort.name not in provide_ports:
                    provide_ports[innerPort.name] = []
                provide_ports[innerPort.name].append((innerComponent, innerPort))
        return require_ports, provide_ports

    def _autoCreateAssemblyConnectors(self, inner_require_port_map, inner_provide_port_map):
        for name in sorted(inner_provide_port_map.keys()):
            if len(inner_provide_port_map[name])>1:
                print("Warning: Multiple components are providing the same port '%s': "%name+', '.join([x[0].name for x in inner_provide_port_map[name]]), file=sys.stderr)
            (providerComponent, providePort) = inner_provide_port_map[name][0]
            if name in inner_require_port_map:
                for (requesterComponent, requirePort) in inner_require_port_map[name]:
                    if requirePort.portInterfaceRef == providePort.portInterfaceRef:
                        self._createAssemblyPortInternal(providerComponent, providePort, requesterComponent, requirePort)

    def _autoCreateDelegationConnectors(self, inner_require_port_map, inner_provide_port_map):
        for outerPort in sorted(self.providePorts, key=lambda x: x.name):
            if outerPort.name and outerPort.name in inner_provide_port_map:
                for (innerComponent, innerPort) in inner_provide_port_map[outerPort.name]:
                    if innerPort.portInterfaceRef == outerPort.portInterfaceRef:
                        self._createDelegationConnectorInternal(innerComponent, innerPort, outerPort)
        for outerPort in sorted(self.requirePorts, key=lambda x: x.name):
            if outerPort.name and outerPort.name in inner_require_port_map:
                for (innerComponent, innerPort) in inner_require_port_map[outerPort.name]:
                    if innerPort.portInterfaceRef == outerPort.portInterfaceRef:
                        self._createDelegationConnectorInternal(innerComponent, innerPort, outerPort)

    def findUnconnectedPorts(self):
        """
        Returns a list unconnected ports found in this composition
        """
        ws = self.rootWS()
        assert (ws is not None)
        unconnected = []
        inner_require_port_map, inner_provide_port_map = self._buildInnerPortMap(ws)
        for name in sorted(inner_provide_port_map.keys()):
            for (innerComponent, providePort) in inner_provide_port_map[name]:
                if self._isUnconnectedPortInner(ws, providePort):
                    unconnected.append(providePort)
        for name in sorted(inner_require_port_map.keys()):
            for (innerComponent, requirePort) in inner_require_port_map[name]:
                if self._isUnconnectedPortInner(ws, requirePort):
                    unconnected.append(requirePort)
        for port in sorted(self.providePorts,key=lambda x: x.name)+sorted(self.requirePorts,key=lambda x: x.name):
            if self._isUnconnectedPortOuter(ws, port):
                unconnected.append(port)
        return unconnected

    def _isUnconnectedPortInner(self, ws, innerPort):
        innerPortRef = innerPort.ref
        portInterface = ws.find(innerPort.portInterfaceRef)
        if portInterface is None:
            raise ValueError('invalid reference: '+innerPort.portInterfaceRef)
        if not isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            return False
        for connector in self.assemblyConnectors:
            if (connector.providerInstanceRef.portRef == innerPortRef) or (connector.requesterInstanceRef.portRef == innerPortRef):
                return False
        for connector in self.delegationConnectors:
            if connector.innerPortInstanceRef.portRef == innerPortRef:
                return False
        return True

    def _isUnconnectedPortOuter(self, ws, outerPort):
        outerPortRef = outerPort.ref
        portInterface = ws.find(outerPort.portInterfaceRef)
        if portInterface is None:
            raise ValueError('invalid reference: '+outerPort.portInterfaceRef)
        if not isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            return False
        for connector in self.delegationConnectors:
            if connector.outerPortRef.portRef == outerPortRef:
                return False
        return True

class Port(Element):
    def __init__(self,name, portInterfaceRef, comspec=None, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        if portInterfaceRef is not None and not isinstance(portInterfaceRef,str):
            raise ValueError('portInterfaceRef needs to be of type None or str')
        self.portInterfaceRef = portInterfaceRef
        self.comspec=[]

        if comspec is not None:
            ws = self.rootWS()
            assert(ws is not None)
            if isinstance(comspec, collections.Mapping):
                comspecObj = self.createComSpecFromDict(ws,portInterfaceRef,comspec)
                if comspecObj is None:
                    raise ValueError('failed to create comspec from comspec data: '+repr(comspec))
                self.comspec.append(comspecObj)
            elif isinstance(comspec, collections.Iterable):
                for data in comspec:
                    comspecObj = self.createComSpecFromDict(ws,portInterfaceRef,data)
                    if comspecObj is None:
                        raise ValueError('failed to create comspec from comspec data: '+repr(data))
                    self.comspec.append(comspecObj)
            else:
                raise NotImplementedError("not supported")

    @property
    def ref(self):
        if self.parent is not None:
            return self.parent.ref+'/%s'%self.name
        else:
            return '/%s'%self.name

    def rootWS(self):
        if self.parent is None:
            return None
        else:
            return self.parent.rootWS()

    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name, 'portInterfaceRef':self.portInterfaceRef, 'attributes':[]}
        for attribute in self.attributes:
            data['attributes'].append(attribute.asdict())
        if len(data['attributes'])==0: del data['attributes']
        return data

    def createComSpecFromDict(self,ws,portInterfaceRef,comspec):
        assert(ws is not None)
        assert(isinstance(comspec,dict))
        portInterface=ws.find(portInterfaceRef, role='PortInterface')
        if portInterface is None:
            raise ValueError("invalid reference: "+portInterfaceRef)
        if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
            name=None
            userInitValue=None
            initValueRef=None #initValue and initValueRef are mutually exclusive, you cannot have both defined at the same time
            aliveTimeout=0
            queueLength=None
            canInvalidate=False if isinstance(self,ProvidePort) else None
            if 'name' in comspec: name=str(comspec['name'])
            if 'initValue' in comspec: userInitValue=comspec['initValue']
            if 'initValueRef' in comspec: initValueRef=str(comspec['initValueRef'])
            if 'aliveTimeout' in comspec: aliveTimeout=int(comspec['aliveTimeout'])
            if 'queueLength' in comspec: queueLength=int(comspec['queueLength'])
            if 'canInvalidate' in comspec: canInvalidate=bool(comspec['canInvalidate'])
            if name is None:
                #pick the name of the first available data element in portInterface
                name=portInterface.dataElements[0].name
            #verify (user-supplied) name
            dataElement=portInterface.find(name)
            if dataElement is None:
                raise ValueError("unknown element '%s' of portInterface '%s'"%(name,portInterface.name))
            #verify compatibility of initValueRef
            if initValueRef is not None:
                initValueTmp = ws.find(initValueRef, role='Constant')
                if initValueTmp is None:
                    raise ValueError("invalid reference: "+str(initValueRef))
                if isinstance(initValueTmp,autosar.constant.Constant):
                    if ws.version < 4.0:
                        #this is a convenience implementation for the user. For AUTOSAR3, initValueRef needs to point to the value inside the Constant
                        if dataElement.typeRef != initValueTmp.value.typeRef:
                            raise ValueError("constant value has different type from data element, expected '%s', found '%s'"%(dataElement.typeRef,initValue.value.typeRef))
                        initValueRef=initValueTmp.value.ref #correct the reference to the actual value
                    else:
                        initValueRef=initValueTmp.ref
                elif isinstance(initValueTmp,autosar.constant.Value):
                    initValueRef=initValueTmp.ref
                else:
                    raise ValueError("reference is not a Constant or Value object: '%s'"%initValueRef)
            #automatically set default value of queueLength  to 1 in case the dataElement is queued
            if isinstance(self, RequirePort) and dataElement.isQueued and ( (queueLength is None) or queueLength==0):
                queueLength=1
            if userInitValue is not None:
                if not isinstance(userInitValue, autosar.constant.Value):
                    raise ValueError('initValue must be an instance of autosar.constant.Value or one of its derived classes')
            return DataElementComSpec(name, userInitValue, initValueRef, aliveTimeout, queueLength, canInvalidate)
        elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            operation = comspec.get('operation',None)
            queueLength = comspec.get('queueLength',1)
            if operation is not None:
                return OperationComSpec(operation,queueLength)
        elif isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
            enhancedMode = comspec.get('enhancedMode', False)
            supportAsync = comspec.get('supportAsync', False)
            return ModeSwitchComSpec(enhancedMode, supportAsync)
        elif isinstance(portInterface, autosar.portinterface.ParameterInterface):
            name=portInterface.elements[0].name
            initValue=comspec.get('initValue', None)
            return ParameterComSpec(name, initValue)
        else:
            raise NotImplementedError(type(portInterface))
        return None




class RequirePort(Port):
    def tag(self,version=None): return "R-PORT-PROTOTYPE"
    def __init__(self,name,portInterfaceRef=None,comspec=None,parent=None):
        if isinstance(name,str):
            #normal constructor
            super().__init__(name, portInterfaceRef, comspec, parent)
        elif isinstance(name,RequirePort):
            other=name #alias
            #copy constructor
            super().__init__(other.name, other.portInterfaceRef, parent)
            self.comspec=copy.deepcopy(other.comspec)
        elif isinstance(name,ProvidePort):
            other=name #alias
            #copy constructor
            super().__init__(other.name, other.portInterfaceRef, parent)
            self.comspec=copy.deepcopy(other.comspec)
        else:
            raise NotImplementedError(type(name))

    def copy(self):
        """
        returns a copy of itself
        """
        return RequirePort(self)

    def mirror(self):
        """
        returns a mirrored copy of itself
        """
        return ProvidePort(self)


class ProvidePort(Port):
    def tag(self,version=None): return "P-PORT-PROTOTYPE"
    def __init__(self,name,portInterfaceRef=None,comspec=None,parent=None):
        if isinstance(name,str):
        #normal constructor
            super().__init__(name, portInterfaceRef, comspec, parent)
        elif isinstance(name,ProvidePort):
            other=name #alias
            #copy constructor
            super().__init__(other.name,other.portInterfaceRef,None)
            self.comspec=copy.deepcopy(other.comspec)
        elif isinstance(name,RequirePort):
            other=name #alias
            #copy constructor
            super().__init__(other.name, other.portInterfaceRef, parent)
            self.comspec=copy.deepcopy(other.comspec)
        else:
            raise NotImplementedError(type(name))

    def copy(self):
        """
        returns a copy of itself
        """
        return ProvidePort(self)

    def mirror(self):
        """
        returns a mirrored copy of itself
        """
        return RequirePort(self)


class OperationComSpec(object):
    def __init__(self,name=None,queueLength=1):
        self.name = name
        self.queueLength=queueLength
    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name}
        if self.queueLength is not None:
            data['queueLength']=self.queueLength

class DataElementComSpec(object):
    def __init__(self, name=None, initValue=None, initValueRef=None, aliveTimeout=None, queueLength=None, canInvalidate=None):
        self.name = name
        if initValue is not None:
            assert(isinstance(initValue, autosar.constant.Value))
        self.initValue = initValue
        self.initValueRef = str(initValueRef) if initValueRef is not None else None
        self._aliveTimeout = int(aliveTimeout) if aliveTimeout is not None else None
        self._queueLength = int(queueLength) if queueLength is not None else None
        self.canInvalidate = bool(canInvalidate) if canInvalidate is not None else None


    @property
    def aliveTimeout(self):
        return self._aliveTimeout

    @aliveTimeout.setter
    def aliveTimeout(self,val):
        self._aliveTimeout = int(val)

    @property
    def queueLength(self):
        return self._queueLength

    @queueLength.setter
    def queueLength(self,val):
        self._queueLength = int(val)


    def asdict(self):
        data={'type': self.__class__.__name__,'name':self.name}
        if self.initValueRef is not None: data['initValueRef']=self.initValueRef
        if self.aliveTimeout is not None: data['aliveTimeout']=self.aliveTimeout
        if self.queueLength is not None: data['queueLength']=self.queueLength
        if self.canInvalidate is not None: data['canInvalidate']=self.canInvalidate
        return data

class ModeSwitchComSpec:
    def __init__(self, enhancedMode=False, supportAsync=False):
        self.enhancedMode = enhancedMode
        self.supportAsync = supportAsync

class ParameterComSpec:
    def __init__(self, name, initValue=None):
        self.name = name
        self.initValue = initValue

class SwcImplementation(Element):
    def __init__(self,name,behaviorRef,parent=None):
        super().__init__(name,parent)
        self.behaviorRef=behaviorRef

class ComponentPrototype(Element):
    def __init__(self,name,typeRef,parent=None):
        super().__init__(name,parent)
        self.typeRef=typeRef
    def asdict(self):
        return {'type': self.__class__.__name__,'name':self.name,'typeRef':self.typeRef}

    def tag(self, version=None): return 'SW-COMPONENT-PROTOTYPE' if version >= 4.0 else'COMPONENT-PROTOTYPE'

class ProviderInstanceRef:
    """
    <PROVIDER-IREF>
    """
    def __init__(self,componentRef, portRef):
        self.componentRef=componentRef
        self.portRef=portRef
    def asdict(self):
        return {'type': self.__class__.__name__,'componentRef':self.componentRef,'portRef':self.portRef}
    def tag(self, version=None):
        return 'PROVIDER-IREF'


class RequesterInstanceRef:
    """
    <REQUESTER-IREF>
    """
    def __init__(self,componentRef, portRef):
        self.componentRef=componentRef
        self.portRef=portRef
    def asdict(self):
        return {'type': self.__class__.__name__,'componentRef':self.componentRef,'portRef':self.portRef}
    def tag(self, version=None):
        return 'REQUESTER-IREF'


class InnerPortInstanceRef:
    """
    <INNER-PORT-IREF>
    """
    def __init__(self,componentRef,portRef):
        self.componentRef=componentRef
        self.portRef=portRef
    def asdict(self):
        return {'type': self.__class__.__name__,'componentRef':self.componentRef,'portRef':self.portRef}
    def tag(self, version=None):
        return 'INNER-PORT-IREF'


class OuterPortRef:
    """
    <OUTER-PORT-REF>
    """
    def __init__(self,portRef):
        self.portRef=portRef
    def asdict(self):
        return {'type': self.__class__.__name__, 'portRef':self.portRef}
    def tag(self, version=None):
        return 'OUTER-PORT-REF'


class AssemblyConnector(Element):
    """
    <ASSEMBLY-CONNECTOR-PROTOTYPE>
    """
    def __init__(self,name,providerInstanceRef,requesterInstanceRef,parent=None):
        assert(isinstance(providerInstanceRef,ProviderInstanceRef))
        assert(isinstance(requesterInstanceRef,RequesterInstanceRef))
        super().__init__(name, parent)
        self.providerInstanceRef=providerInstanceRef
        self.requesterInstanceRef=requesterInstanceRef
    def asdict(self):
        return {'type': self.__class__.__name__,'providerInstanceRef':self.providerInstanceRef.asdict(),'requesterInstanceRef':self.requesterInstanceRef.asdict()}

    def tag(self, version):
        return 'ASSEMBLY-SW-CONNECTOR' if version >= 4.0 else 'ASSEMBLY-CONNECTOR-PROTOTYPE'


class DelegationConnector(Element):
    """
    <DELEGATION-CONNECTOR-PROTOTYPE>
    """
    def __init__(self, name, innerPortInstanceRef, outerPortRef, parent=None):
        assert(isinstance(innerPortInstanceRef,InnerPortInstanceRef))
        assert(isinstance(outerPortRef,OuterPortRef))
        super().__init__(name, parent)
        self.innerPortInstanceRef = innerPortInstanceRef
        self.outerPortRef = outerPortRef

    def asdict(self):
        return {'type': self.__class__.__name__,'innerPortInstanceRef':self.innerPortInstanceRef.asdict()}

    def tag(self, version): return 'DELEGATION-SW-CONNECTOR' if version >= 4.0 else 'DELEGATION-CONNECTOR-PROTOTYPE'
