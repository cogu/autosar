from autosar.element import Element
import autosar.portinterface
import autosar.constant
import autosar.builder
import autosar.port
import copy
import collections
import sys
from autosar._swc_implementation import SwcImplementation, SwcImplementationCodeDescriptor, EngineeringObject, ResourceConsumption, MemorySection

class ComponentType(Element):
    """
    Base class for all software component prototype classes.
    """
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.requirePorts=[]
        self.providePorts=[]

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
        if isinstance(elem,autosar.port.RequirePort):
            self.requirePorts.append(elem)
            elem.parent=self
        elif isinstance(elem,autosar.port.ProvidePort):
            self.providePorts.append(elem)
            elem.parent=self
        else:
            raise ValueError("unexpected type:" + str(type(elem)))

    def __getitem__(self,key):
        return self.find(key)

    def createProvidePort(self, name, portInterfaceRef, **kwargs):
        """
        Creates a provide port on this ComponentType
        The ComponentType must have a valid ref (must belong to a valid package in a valid workspace).
        Parameters:

        - name: Name of the port
        - portInterfaceRef: Reference to existing port interface
        - comspec: This is an advanced way to create comspecs directly in the port.

        For SenderReceiver port interfaces which contains exactly one data element there is another way of creating ComSpecs.
        - comspec: Should be left as None.
        - initValue: Used to set an init value literal.
        - initValueRef: Used instead of initValue when you want to reference an existing constant specification.
        - aliveTimeout: Alive timeout setting (in seconds).
        - queueLength (None or int): Length of queue (only applicable for port interface with isQueued property).
        - canInvalidate: Invalidation property (boolean). (AUTOSAR3 only?)

        For Parameter port interfaces you can use these parameters:
        - initValue (int, float or str): Init value literal

        For ModeSwitch port interfaces these parameters are valid for building port comspec:
        - enhancedMode (bool): Sets the enhancedMode (API) property
        - modeSwitchAckTimeout (None or int): Sets the modeSwitchAckTimeout property (milliseconds)
        - queueLength (None or int): Length of call queue on the mode user side.

        For NvDataInterface port interfaces which contains one data element there is another way of creating ComSpecs.
        - ramBlockInitValue (int, float, str): Used to set an init value literal.
        - ramBlockInitValueRef (str): Used when you want an existing constant specification as your initValue.
        - romBlockInitValue (int, float, str): Used to set an init value literal.
        - romBlockInitValueRef (str): Used when you want an existing constant specification as your initValue.
        """

        comspec = kwargs.get('comspec', None)
        if comspec is not None:
            if isinstance(comspec, collections.abc.Mapping):
                comspecList = [comspec]
            elif isinstance(comspec, collections.abc.Iterable):
                comspecList = list(comspec)
            else:
                raise ValueError('comspec argument must be of type dict or list')
        else:
            comspecList = None
        assert (self.ref is not None)
        ws = self.rootWS()
        assert(ws is not None)
        portInterface = ws.find(portInterfaceRef, role='PortInterface')
        if portInterface is None:
            raise autosar.base.InvalidPortInterfaceRef(portInterfaceRef)
        if comspecList is None:
            comspecDict = kwargs if len(kwargs) > 0 else None
            port = autosar.port.ProvidePort(name, portInterface.ref, comspecDict, parent=self)
        else:
            port = autosar.port.ProvidePort(name, portInterface.ref, comspecList, parent=self)
        assert(isinstance(port, autosar.port.Port))
        self.providePorts.append(port)
        return port

    def createRequirePort(self, name, portInterfaceRef, **kwargs):
        """
        Creates a require port on this ComponentType
        The ComponentType must have a valid ref (must belong to a valid package in a valid workspace).
        Parameters:

        - name: Name of the port
        - portInterfaceRef: Reference to existing port interface

        For SenderReceiver port interfaces which contains one data element there is another way of creating ComSpecs.
        - initValue (int, float, str): Used to set an init value literal.
        - initValueRef (str): Used when you want an existing constant specification as your initValue.
        - aliveTimeout(int): Alive timeout setting (in seconds).
        - queueLength(int): Length of queue (only applicable for port interface with isQueued property).
        - canInvalidate(bool): Invalidation property (boolean). (AUTOSAR3 only)

        For Parameter port interfaces you can use these parameters:
        - initValue (int, float or str): Init value literal

        For ModeSwitch port interfaces these parameters are valid:
        - modeGroup: The name of the mode group in the port interface (None or str)
        - enhancedMode: sets the enhancedMode property  (bool)
        - supportAsync: sets the supportAsync property  (bool)

        For NvDataInterface port interfaces which contains one data element there is another way of creating ComSpecs.
        - initValue (int, float, str): Used to set an init value literal.
        - initValueRef (str): Used when you want an existing constant specification as your initValue.
        """
        comspec = kwargs.get('comspec', None)
        if comspec is not None:
            comspecList = comspec
        else:
            comspecList = None
        assert (self.ref is not None)
        ws = self.rootWS()
        assert(ws is not None)
        portInterface = ws.find(portInterfaceRef, role='PortInterface')
        if portInterface is None:
            raise autosar.base.InvalidPortInterfaceRef(portInterfaceRef)
        if comspecList is None:
            comspecDict = kwargs if len(kwargs) > 0 else None
            port = autosar.port.RequirePort(name, portInterface.ref, comspecDict, parent=self)
        else:
            port = autosar.port.RequirePort(name, portInterface.ref, comspecList, parent=self)
        assert(isinstance(port, autosar.port.Port))
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
    def tag(self,version=None): return 'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE' if version>=4.0 else 'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE'

    def __init__(self,name,parent=None):
        super().__init__(name,parent)

class ServiceComponent(AtomicSoftwareComponent):
    def tag(self,version=None):
        if version < 4.0:
            return "SERVICE-COMPONENT-TYPE"
        else:
            return "SERVICE-SW-COMPONENT-TYPE"

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


class SensorActuatorComponent(AtomicSoftwareComponent):
    def tag(self,version=None):
        return "SENSOR-ACTUATOR-SW-COMPONENT-TYPE"

    def __init__(self, name, parent=None):
        super().__init__(name, parent)

class NvBlockComponent(AtomicSoftwareComponent):
    def tag(self,version=None):
        return "NV-BLOCK-SW-COMPONENT-TYPE"

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.nvBlockDescriptors = []

    def find(self, ref):
        parts=ref.partition('/')
        for elem in self.nvBlockDescriptors:
            if elem.name == parts[0]:
                if len(parts[2]) > 0:
                    return elem.find(parts[2])
                else:
                    return elem
        return super().find(ref)

class CompositionComponent(ComponentType):
    """
    Composition Component
    """
    def __init__(self,name,parent=None):
        super().__init__(name,parent)
        self.components = []
        self.assemblyConnectors = []
        self.delegationConnectors = []
        self.dataTypeMappingRefs = []

    def tag(self,version): return 'COMPOSITION-SW-COMPONENT-TYPE' if version >= 4.0 else 'COMPOSITION-TYPE'

    def find(self, ref):
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
        Alias for createComponentPrototype
        """
        return self.createComponentPrototype(componentRef)

    def createComponentPrototype(self, componentRef, name = None):
        """
        creates a new ComponentPrototype object and appends it to the CompositionComponent
        """
        ws = self.rootWS()
        component = ws.find(componentRef, role='ComponentType')
        if component is None:
            raise ValueError('invalid reference: '+componentRef)
        if name is None:
            name = component.name
        elem = ComponentPrototype(name, component.ref, self)
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
            if isinstance(port1, autosar.port.RequirePort) and isinstance(port2, autosar.port.ProvidePort):
                requesterComponent, providerComponent = component1, component2
                requirePort, providePort = port1, port2
            elif isinstance(port2, autosar.port.RequirePort) and isinstance(port1, autosar.port.ProvidePort):
                requesterComponent, providerComponent = component2, component1
                requirePort, providePort = port2, port1
            elif isinstance(port2, autosar.port.RequirePort) and isinstance(port1, autosar.port.RequirePort):
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
        if isinstance(outerPort, autosar.port.ProvidePort):
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
                #assume format 'componentName/portName' where componentName is an inner component
                port=None
                for innerComponent in self.components:
                    component = ws.find(innerComponent.typeRef)
                    if component is None:
                        raise ValueError('invalid reference: '+innerComponent.typeRef)
                    if component.name == parts[0]:
                        port = component.find(parts[1])
                        component = innerComponent
                        if port is None:
                            raise ValueError('Component "{0}" does not seem to have port with name "{1}"'.format(component.name, parts[1]))
                        break
            else:
                #assume portRef is a full reference
                port = ws.find(portRef)
                if port is None:
                    raise autosar.base.InvalidPortRef(portRef)
                if not isinstance(port, autosar.port.Port):
                    raise ValueError('Reference "{0}" is not a port or duplicate references exists in the workspace'.format(parts[0]))
                parentRef = port.parent.ref
                for innerComponent in self.components:
                    if innerComponent.typeRef == parentRef:
                        component = innerComponent
                        break
                else:
                    raise ValueError('Reference "{0}" does not seem to be a port where the (parent) component is part of this composition'.format(portRef))
        else:
            port = self.find(parts[0])
            component=self
        if port is None:
            raise ValueError('Component "{0}" does not seem to have port with name "{1}"'.format(component.name, parts[0]))
        if not isinstance(port, autosar.port.Port):
            raise ValueError('Port name "{0}" is ambiguous. This might be due to duplicate references exists in the workspace '.format(parts[0]))
        return port, component

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

    def findMappedDataTypeRef(self, applicationDataTypeRef):
        """
        Returns a reference to the mapped implementation data type or None if not in map
        """
        ws = self.rootWS()
        assert(ws is not None)
        alreadyProcessed = set()
        for mappingRef in self.dataTypeMappingRefs:
            if mappingRef in alreadyProcessed:
                continue
            else:
                alreadyProcessed.add(mappingRef)
                mappingSet = ws.find(mappingRef)
                if mappingSet is None:
                    raise autosar.base.InvalidMappingRef()
                typeRef = mappingSet.findMappedDataTypeRef(applicationDataTypeRef)
                if typeRef is not None:
                    return typeRef
        return None

class ComponentPrototype(Element):
    def __init__(self,name,typeRef,parent=None):
        super().__init__(name,parent)
        self.typeRef=typeRef

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
