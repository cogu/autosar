import sys
from autosar.base import splitRef, hasAdminData, parseAdminDataNode
import autosar.component
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.parser_base import EntityParser, parseElementUUID
from autosar.util.errorHandler import handleNotImplementedError, handleValueError

def _getDataElemNameFromComSpec(xmlElem,portInterfaceRef):
    if xmlElem.find('./DATA-ELEMENT-REF') is not None:
        dataElemRef = splitRef(xmlElem.find('./DATA-ELEMENT-REF').text)
        assert(dataElemRef is not None)
        dataElemName = dataElemRef.pop()
        tmp = '/'+'/'.join(dataElemRef)
        if portInterfaceRef == tmp:
            return dataElemName
    return None

def _getOperationNameFromComSpec(xmlElem,portInterfaceRef):
    xmlOperation=xmlElem.find('./OPERATION-REF')
    if xmlOperation is not None:
        operationRef = splitRef(xmlOperation.text)
        assert(operationRef is not None)
        operationName = operationRef.pop()
        tmp = '/'+'/'.join(operationRef)
        if portInterfaceRef == tmp:
            return operationName
    return None

def _getParameterNameFromComSpec(xmlElem,portInterfaceRef):
    if xmlElem.tag == 'PARAMETER-REF':
        parameterRef = splitRef(xmlElem.text)
        assert(parameterRef is not None)
        name = parameterRef.pop()
        tmp = '/'+'/'.join(parameterRef)
        if portInterfaceRef == tmp:
            return name
    return None

def _getVariableNameFromComSpec(xmlElem,portInterfaceRef):
    if xmlElem.tag == 'VARIABLE-REF':
        variableRef = splitRef(xmlElem.text)
        assert(variableRef is not None)
        name = variableRef.pop()
        tmp = '/'+'/'.join(variableRef)
        if portInterfaceRef == tmp:
            return name
    return None

class ComponentTypeParser(EntityParser):
    """
    ComponentType parser
    """

    def __init__(self,version=3.0):
        super().__init__(version)
        if self.version >=4.0:
            self.behavior_parser = BehaviorParser(version)

        if self.version >= 3.0 and self.version < 4.0:
            self.switcher = { 'APPLICATION-SOFTWARE-COMPONENT-TYPE': self.parseSoftwareComponent,
                              'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': self.parseSoftwareComponent,
                              'COMPOSITION-TYPE': self.parseCompositionType,
                              'CALPRM-COMPONENT-TYPE': self.parseSoftwareComponent,
                              'SERVICE-COMPONENT-TYPE': self.parseSoftwareComponent
                             }
        elif self.version >= 4.0:
            self.switcher = {
               'APPLICATION-SW-COMPONENT-TYPE': self.parseSoftwareComponent,
               'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE': self.parseSoftwareComponent,
               'SERVICE-COMPONENT-TYPE': self.parseSoftwareComponent,
               'PARAMETER-SW-COMPONENT-TYPE': self.parseSoftwareComponent,
               'COMPOSITION-SW-COMPONENT-TYPE': self.parseCompositionType,
               'SENSOR-ACTUATOR-SW-COMPONENT-TYPE': self.parseSoftwareComponent,
               'SERVICE-SW-COMPONENT-TYPE': self.parseSoftwareComponent,
               'NV-BLOCK-SW-COMPONENT-TYPE': self.parseSoftwareComponent
            }

    def getSupportedTags(self):
        return self.switcher.keys()

    @parseElementUUID
    def parseElement(self, xmlElement, parent = None):
        parseFunc = self.switcher.get(xmlElement.tag)
        if parseFunc is not None:
            return parseFunc(xmlElement,parent)
        else:
            return None

    @parseElementUUID
    def parseSoftwareComponent(self, xmlRoot, parent=None):
        componentType=None
        handledTags = ['SHORT-NAME']
        if xmlRoot.tag=='APPLICATION-SOFTWARE-COMPONENT-TYPE': #for AUTOSAR 3.x
            componentType = autosar.component.ApplicationSoftwareComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif (xmlRoot.tag=='COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE') or (xmlRoot.tag=='COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE'):
            componentType = autosar.component.ComplexDeviceDriverComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif xmlRoot.tag == 'APPLICATION-SW-COMPONENT-TYPE': #for AUTOSAR 4.x
            componentType = autosar.component.ApplicationSoftwareComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif (xmlRoot.tag == 'SERVICE-COMPONENT-TYPE') or (xmlRoot.tag == 'SERVICE-SW-COMPONENT-TYPE'):
            componentType = autosar.component.ServiceComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif xmlRoot.tag == 'CALPRM-COMPONENT-TYPE': #for AUTOSAR 3.x
            componentType = autosar.component.ParameterComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif xmlRoot.tag == 'PARAMETER-SW-COMPONENT-TYPE': #for AUTOSAR 4.x
            componentType = autosar.component.ParameterComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif xmlRoot.tag == 'SENSOR-ACTUATOR-SW-COMPONENT-TYPE': #for AUTOSAR 4.x
            componentType = autosar.component.SensorActuatorComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        elif xmlRoot.tag == 'NV-BLOCK-SW-COMPONENT-TYPE': #for AUTOSAR 4.x
            componentType = autosar.component.NvBlockComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        else:
            handleNotImplementedError(xmlRoot.tag)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag not in handledTags:
                if xmlElem.tag == 'ADMIN-DATA':
                    componentType.adminData = self.parseAdminDataNode(xmlElem)
                elif xmlElem.tag == 'DESC':
                    pass #Implement later
                elif xmlElem.tag == 'LONG-NAME':
                    pass #Implement later
                elif xmlElem.tag == 'PORTS':
                    self.parseComponentPorts(componentType,xmlRoot)
                elif xmlElem.tag == 'INTERNAL-BEHAVIORS':
                    behaviors = xmlElem.findall('./SWC-INTERNAL-BEHAVIOR')
                    if len(behaviors)>1:
                        handleValueError('%s: an SWC cannot have multiple internal behaviors'%(componentType))
                    elif len(behaviors) == 1:
                        componentType.behavior = self.behavior_parser.parseSWCInternalBehavior(behaviors[0], componentType)
                elif xmlElem.tag == 'NV-BLOCK-DESCRIPTORS' and isinstance(componentType, autosar.component.NvBlockComponent):
                    for descriptorXml in xmlElem.findall('./NV-BLOCK-DESCRIPTOR'):
                        descriptor = self.behavior_parser.parseNvBlockSWCnvBlockDescriptor(descriptorXml, componentType)
                        componentType.nvBlockDescriptors.append(descriptor)
                elif xmlElem.tag == 'CATEGORY':
                    componentType.category = self.parseTextNode(xmlElem)
                elif xmlElem.tag == 'DATA-TYPE-MAPPING-REFS':
                    if not isinstance(componentType, autosar.component.ParameterComponent):
                        handleValueError(f"DATA-TYPE-MAPPING-REFS cannot appear directly inside {xmlRoot.tag}")
                    else:
                        for xmlChild in xmlElem.findall('./*'):
                            if xmlChild.tag == 'DATA-TYPE-MAPPING-REF':
                                tmp = self.parseTextNode(xmlChild)
                                if tmp is not None:
                                    componentType.appendDataTypeMappingRef(tmp)
                elif xmlElem.tag == 'CONSTANT-MAPPING-REFS':
                    if not isinstance(componentType, autosar.component.ParameterComponent):
                        handleValueError(f"CONSTANT-MAPPING-REFS cannot appear directly inside {xmlRoot.tag}")
                    else:
                        for xmlChild in xmlElem.findall('./*'):
                            if xmlChild.tag == 'CONSTANT-MAPPING-REF':
                                tmp = self.parseTextNode(xmlChild)
                                if tmp is not None:
                                    componentType.appendConstantMappingRef(tmp)
                else:
                    print('Unhandled tag: '+xmlElem.tag, file=sys.stderr)
        return componentType

    def _parseRequiredComSpec(self, xmlItem, port, portInterfaceRef):
        if xmlItem.tag == 'CLIENT-COM-SPEC':
            operationName=_getOperationNameFromComSpec(xmlItem,portInterfaceRef)
            comspec=autosar.port.OperationComSpec(operationName)
            port._comspec.required.append(comspec)
        elif xmlItem.tag == 'UNQUEUED-RECEIVER-COM-SPEC' or xmlItem.tag == 'NONQUEUED-RECEIVER-COM-SPEC':
            dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
            comspec = autosar.port.DataElementComSpec(dataElemName)
            if xmlItem.find('./ALIVE-TIMEOUT') is not None:
                comspec.aliveTimeout = self.parseTextNode(xmlItem.find('./ALIVE-TIMEOUT'))
            if self.version >= 4.0:
                xmlElem = xmlItem.find('./INIT-VALUE')
                if xmlElem != None:
                    comspec.initValue, comspec.initValueRef = self._parseAr4InitValue(xmlElem)
            else:
                if xmlItem.find('./INIT-VALUE-REF') != None:
                    comspec.initValueRef = self.parseTextNode(xmlItem.find('./INIT-VALUE-REF'))
            port._comspec.required.append(comspec)
        elif xmlItem.tag == 'QUEUED-RECEIVER-COM-SPEC':
            dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
            comspec = autosar.port.DataElementComSpec(dataElemName)
            if xmlItem.find('./QUEUE-LENGTH') != None:
                comspec.queueLength = self.parseTextNode(xmlItem.find('./QUEUE-LENGTH'))
            port._comspec.required.append(comspec)
        elif xmlItem.tag == 'MODE-SWITCH-RECEIVER-COM-SPEC':
            comspec = self._parseModeSwitchReceiverComSpec(xmlItem)
            port._comspec.required.append(comspec)
        elif xmlItem.tag == 'PARAMETER-REQUIRE-COM-SPEC':
            comspec = self._parseParameterComSpec(xmlItem, portInterfaceRef)
            port._comspec.required.append(comspec)
        elif xmlItem.tag == 'NV-REQUIRE-COM-SPEC':
            comspec = self._parseNvRequireComSpec(xmlItem, portInterfaceRef)
            assert(comspec is not None)
            port._comspec.required.append(comspec)
        else:
            handleNotImplementedError(xmlItem.tag)

    def _parseProvidedComSpec(self, xmlItem, port, portInterfaceRef):
        if xmlItem.tag == 'SERVER-COM-SPEC':
            operationName=_getOperationNameFromComSpec(xmlItem,portInterfaceRef)
            comspec=autosar.port.OperationComSpec(operationName)
            comspec.queueLength=self.parseIntNode(xmlItem.find('QUEUE-LENGTH'))
            port._comspec.provided.append(comspec)
        elif xmlItem.tag == 'UNQUEUED-SENDER-COM-SPEC' or xmlItem.tag == 'NONQUEUED-SENDER-COM-SPEC':
            dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
            comspec = autosar.port.DataElementComSpec(dataElemName)
            if self.version >= 4.0:
                xmlElem = xmlItem.find('./INIT-VALUE')
                if xmlElem != None:
                    comspec.initValue, comspec.initValueRef = self._parseAr4InitValue(xmlElem)
            else:
                if xmlItem.find('./INIT-VALUE-REF') is not None:
                    comspec.initValueRef = self.parseTextNode(xmlItem.find('./INIT-VALUE-REF'))
            if xmlItem.find('./CAN-INVALIDATE') != None:
                comspec.canInvalidate = True if self.parseTextNode(xmlItem.find('./CAN-INVALIDATE'))=='true' else False
            port._comspec.provided.append(comspec)
        elif xmlItem.tag == 'QUEUED-SENDER-COM-SPEC':
            dataElemName = _getDataElemNameFromComSpec(xmlItem,portInterfaceRef)
            comspec = autosar.port.DataElementComSpec(dataElemName)
            assert(comspec is not None)
            port._comspec.provided.append(comspec)
        elif xmlItem.tag == 'PARAMETER-PROVIDE-COM-SPEC':
            comspec = self._parseParameterComSpec(xmlItem, portInterfaceRef)
            assert(comspec is not None)
            port._comspec.provided.append(comspec)
        elif xmlItem.tag == 'MODE-SWITCH-SENDER-COM-SPEC':
            comspec = self._parseModeSwitchSenderComSpec(xmlItem)
            assert(comspec is not None)
            port._comspec.provided.append(comspec)
        elif xmlItem.tag == 'NV-PROVIDE-COM-SPEC':
            comspec = self._parseNvProvideComSpec(xmlItem, portInterfaceRef)
            assert(comspec is not None)
            port._comspec.provided.append(comspec)
        else:
            handleNotImplementedError(xmlItem.tag)

    def parseComponentPorts(self, componentType, xmlRoot):
        xmlPorts=xmlRoot.find('PORTS')
        assert(xmlPorts is not None)
        for xmlPort in xmlPorts.findall('*'):
            if(xmlPort.tag == "R-PORT-PROTOTYPE"):
                portName = xmlPort.find('SHORT-NAME').text
                portInterfaceRef = self.parseTextNode(xmlPort.find('REQUIRED-INTERFACE-TREF'))
                port = autosar.port.RequirePort(portName, portInterfaceRef, autoCreateComSpec = False, parent=componentType)
                port.uuid = xmlPort.attrib.get('UUID', '').lower()
                if hasAdminData(xmlPort):
                    port.adminData=parseAdminDataNode(xmlPort.find('ADMIN-DATA'))
                if xmlPort.findall('./REQUIRED-COM-SPECS') is not None:
                    for xmlItem in xmlPort.findall('./REQUIRED-COM-SPECS/*'):
                        self._parseRequiredComSpec(xmlItem, port, portInterfaceRef)
                componentType.requirePorts.append(port)
            elif(xmlPort.tag == 'P-PORT-PROTOTYPE'):
                portName = xmlPort.find('SHORT-NAME').text
                portInterfaceRef = self.parseTextNode(xmlPort.find('PROVIDED-INTERFACE-TREF'))
                port = autosar.port.ProvidePort(portName, portInterfaceRef, autoCreateComSpec = False, parent = componentType)
                port.uuid = xmlPort.attrib.get('UUID', '').lower()
                if hasAdminData(xmlPort):
                    port.adminData=parseAdminDataNode(xmlPort.find('ADMIN-DATA'))
                if xmlPort.findall('./PROVIDED-COM-SPECS') is not None:
                    for xmlItem in xmlPort.findall('./PROVIDED-COM-SPECS/*'):
                        self._parseProvidedComSpec(xmlItem, port, portInterfaceRef)
                componentType.providePorts.append(port)
            elif(xmlPort.tag == 'PR-PORT-PROTOTYPE'):
                portName = xmlPort.find('SHORT-NAME').text
                portInterfaceRef = self.parseTextNode(xmlPort.find('PROVIDED-REQUIRED-INTERFACE-TREF'))
                port = autosar.port.ProvideRequirePort(portName, portInterfaceRef, autoCreateComSpec = False, parent = componentType)
                port.uuid = xmlPort.attrib.get('UUID', '').lower()
                if hasAdminData(xmlPort):
                    port.adminData=parseAdminDataNode(xmlPort.find('ADMIN-DATA'))
                if xmlPort.findall('./PROVIDED-COM-SPECS') is not None:
                    for xmlItem in xmlPort.findall('./PROVIDED-COM-SPECS/*'):
                        self._parseProvidedComSpec(xmlItem, port, portInterfaceRef)
                if xmlPort.findall('./REQUIRED-COM-SPECS') is not None:
                    for xmlItem in xmlPort.findall('./REQUIRED-COM-SPECS/*'):
                        self._parseRequiredComSpec(xmlItem, port, portInterfaceRef)
                componentType.provideRequirePorts.append(port)

    @parseElementUUID
    def parseCompositionType(self, xmlRoot, parent=None):
        """
        parses COMPOSITION-TYPE
        """
        assert (xmlRoot.tag=='COMPOSITION-TYPE') or (xmlRoot.tag=='COMPOSITION-SW-COMPONENT-TYPE')
        dataTypeMappingRefs = None
        swc=autosar.component.CompositionComponent(self.parseTextNode(xmlRoot.find('SHORT-NAME')),parent)
        self.push()
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='SHORT-NAME':
                continue
            elif xmlElem.tag=='PORTS':
                self.parseComponentPorts(swc,xmlRoot)
            elif xmlElem.tag=='COMPONENTS':
                self.parseComponents(xmlElem,swc)
            elif xmlElem.tag=='CONNECTORS':
                if self.version >= 4.0:
                    self.parseConnectorsV4(xmlElem,swc)
                else:
                    self.parseConnectorsV3(xmlElem,swc)
            elif xmlElem.tag == 'DATA-TYPE-MAPPING-REFS':
                dataTypeMappingRefs = []
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'DATA-TYPE-MAPPING-REF':
                        tmp = self.parseTextNode(xmlChild)
                        assert(tmp is not None)
                        dataTypeMappingRefs.append(tmp)
            elif xmlElem.tag=='PORT-GROUPS':
                print("[ComponentParser] unhandled: %s"%xmlElem.tag)
            else:
                self.defaultHandler(xmlElem)
        if dataTypeMappingRefs is not None:
            swc.dataTypeMappingRefs = dataTypeMappingRefs
        self.pop(swc)
        return swc

    def parseComponents(self,xmlRoot,parent):
        """
        parses <COMPONENTS>
        """
        assert(xmlRoot.tag=='COMPONENTS')
        for elem in xmlRoot.findall('./*'):
            componentTag = 'SW-COMPONENT-PROTOTYPE' if self.version >= 4.0 else 'COMPONENT-PROTOTYPE'
            if elem.tag==componentTag:
                name=self.parseTextNode(elem.find('SHORT-NAME'))
                typeRef=self.parseTextNode(elem.find('TYPE-TREF'))
                parent.components.append(autosar.component.ComponentPrototype(name,typeRef,parent))
            else:
                handleNotImplementedError(elem.tag)

    def parseConnectorsV3(self,xmlRoot,parent=None):
        """
        parses <CONNECTORS> (AUTOSAR 3)
        """
        assert(xmlRoot.tag=='CONNECTORS')
        for elem in xmlRoot.findall('./*'):
            if elem.tag=='ASSEMBLY-CONNECTOR-PROTOTYPE':
                name=self.parseTextNode(elem.find('SHORT-NAME'))
                providerComponentRef=self.parseTextNode(elem.find('./PROVIDER-IREF/COMPONENT-PROTOTYPE-REF'))
                providerPortRef=self.parseTextNode(elem.find('./PROVIDER-IREF/P-PORT-PROTOTYPE-REF'))
                requesterComponentRef=self.parseTextNode(elem.find('./REQUESTER-IREF/COMPONENT-PROTOTYPE-REF'))
                requesterPortRef=self.parseTextNode(elem.find('./REQUESTER-IREF/R-PORT-PROTOTYPE-REF'))
                parent.assemblyConnectors.append(autosar.component.AssemblyConnector(name, autosar.component.ProviderInstanceRef(providerComponentRef,providerPortRef), autosar.component.RequesterInstanceRef(requesterComponentRef,requesterPortRef)))
            elif elem.tag=='DELEGATION-CONNECTOR-PROTOTYPE':
                name=self.parseTextNode(elem.find('SHORT-NAME'))
                innerComponentRef=self.parseTextNode(elem.find('./INNER-PORT-IREF/COMPONENT-PROTOTYPE-REF'))
                innerPortRef=self.parseTextNode(elem.find('./INNER-PORT-IREF/PORT-PROTOTYPE-REF'))
                outerPortRef=self.parseTextNode(elem.find('./OUTER-PORT-REF'))
                parent.delegationConnectors.append(autosar.component.DelegationConnector(name, autosar.component.InnerPortInstanceRef(innerComponentRef,innerPortRef), autosar.component.OuterPortRef(outerPortRef)))
            else:
                handleNotImplementedError(elem.tag)

    @parseElementUUID
    def _parseAssemblySwConnector(self, xmlRoot, parent = None):
        """
        parses <ASSEMBLY-SW-CONNECTOR>
        """
        assert xmlRoot.tag == 'ASSEMBLY-SW-CONNECTOR'
        mappingRef = None
        name=self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        for xmlChild in xmlRoot.findall('./*'):
            if xmlChild.tag == 'SHORT-NAME':
                continue
            elif xmlChild.tag == 'PROVIDER-IREF':
                providerComponentRef=self.parseTextNode(xmlChild.find('./CONTEXT-COMPONENT-REF'))
                providerPortRef=self.parseTextNode(xmlChild.find('./TARGET-P-PORT-REF'))
            elif xmlChild.tag == 'REQUESTER-IREF':
                requesterComponentRef=self.parseTextNode(xmlChild.find('./CONTEXT-COMPONENT-REF'))
                requesterPortRef=self.parseTextNode(xmlChild.find('./TARGET-R-PORT-REF'))
            elif xmlChild.tag == 'MAPPING-REF':
                mappingRef = self.parseTextNode(xmlChild)
            else:
                self.defaultHandler(xmlChild)
        if providerComponentRef is None:
            raise RuntimeError('PROVIDER-IREF/CONTEXT-COMPONENT-REF is missing: item=%s'%name)
        if providerComponentRef is None:
            raise RuntimeError('PROVIDER-IREF/TARGET-P-PORT-REF is missing: item=%s'%name)
        if requesterComponentRef is None:
            raise RuntimeError('REQUESTER-IREF/CONTEXT-COMPONENT-REF is missing: item=%s'%name)
        if requesterPortRef is None:
            raise RuntimeError('REQUESTER-IREF/TARGET-R-PORT-REF is missing: item=%s'%name)

        return autosar.component.AssemblyConnector(
            name,
            autosar.component.ProviderInstanceRef(providerComponentRef,providerPortRef),
            autosar.component.RequesterInstanceRef(requesterComponentRef,requesterPortRef),
            mappingRef,
            parent=parent)

    @parseElementUUID
    def _parseDelegationSwConnector(self, xmlRoot, parent = None):
        """
        parses <DELEGATION-SW-CONNECTOR>
        """
        assert xmlRoot.tag == 'DELEGATION-SW-CONNECTOR'
        name=self.parseTextNode(xmlRoot.find('SHORT-NAME'))
        for xmlChild in xmlRoot.findall('./INNER-PORT-IREF/*'):
            if xmlChild.tag == 'R-PORT-IN-COMPOSITION-INSTANCE-REF':
                innerComponentRef=self.parseTextNode(xmlChild.find('./CONTEXT-COMPONENT-REF'))
                innerPortRef=self.parseTextNode(xmlChild.find('./TARGET-R-PORT-REF'))
            elif xmlChild.tag == 'P-PORT-IN-COMPOSITION-INSTANCE-REF':
                innerComponentRef=self.parseTextNode(xmlChild.find('./CONTEXT-COMPONENT-REF'))
                innerPortRef=self.parseTextNode(xmlChild.find('./TARGET-P-PORT-REF'))
            else:
                handleNotImplementedError(xmlChild.tag)
        outerPortRef=self.parseTextNode(xmlRoot.find('./OUTER-PORT-REF'))

        return autosar.component.DelegationConnector(name, autosar.component.InnerPortInstanceRef(innerComponentRef,innerPortRef), autosar.component.OuterPortRef(outerPortRef), parent=parent)

    @parseElementUUID
    def parseConnectorsV4(self,xmlRoot,parent=None):
        """
        parses <CONNECTORS> (AUTOSAR 4)
        """
        assert(xmlRoot.tag=='CONNECTORS')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag=='ASSEMBLY-SW-CONNECTOR':
                connector = self._parseAssemblySwConnector(xmlElem,parent)
                parent.assemblyConnectors.append(connector)
            elif xmlElem.tag=='DELEGATION-SW-CONNECTOR':
                connector = self._parseDelegationSwConnector(xmlElem,parent)
                parent.delegationConnectors.append(connector)
            else:
                handleNotImplementedError(xmlElem.tag)

    def _parseModeSwitchReceiverComSpec(self, xmlRoot):
        (enhancedMode, supportAsync, modeGroupRef) = (None, None, None)
        assert(xmlRoot.tag == 'MODE-SWITCH-RECEIVER-COM-SPEC')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ENHANCED-MODE-API':
                enhancedMode = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'SUPPORTS-ASYNCHRONOUS-MODE-SWITCH':
                supportAsync = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'MODE-GROUP-REF':
                modeGroupRef = self.parseTextNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return autosar.port.ModeSwitchComSpec(None, enhancedMode, supportAsync, modeGroupRef = modeGroupRef)

    def _parseModeSwitchSenderComSpec(self, xmlRoot):
        (enhancedMode, queueLength, modeSwitchAckTimeout, modeGroupRef) = (None, None, None, None)
        assert(xmlRoot.tag == 'MODE-SWITCH-SENDER-COM-SPEC')
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'ENHANCED-MODE-API':
                enhancedMode = self.parseBooleanNode(xmlElem)
            elif xmlElem.tag == 'MODE-GROUP-REF':
                modeGroupRef = self.parseTextNode(xmlElem)
            elif xmlElem.tag == 'MODE-SWITCHED-ACK':
                for xmlChild in xmlElem.findall('./*'):
                    if xmlChild.tag == 'TIMEOUT':
                        tmp = self.parseFloatNode(xmlChild)
                        if tmp is not None:
                            modeSwitchAckTimeout = int(tmp*1000) #We use milliseconds in our internal model
            elif xmlElem.tag == 'QUEUE-LENGTH':
                queueLength = self.parseIntNode(xmlElem)
            else:
                handleNotImplementedError(xmlElem.tag)
        return autosar.port.ModeSwitchComSpec(None, enhancedMode, None, queueLength, modeSwitchAckTimeout, modeGroupRef)

    def _parseParameterComSpec(self, xmlRoot, portInterfaceRef):
        (initValue, name) = (None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'INIT-VALUE':
                initValue, initValueRef = self._parseAr4InitValue(xmlElem)
            elif xmlElem.tag == 'PARAMETER-REF':
                name = _getParameterNameFromComSpec(xmlElem, portInterfaceRef)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (name is not None):
            return autosar.port.ParameterComSpec(name, initValue, initValueRef)
        else:
            raise RuntimeError('PARAMETER-REQUIRE-COM-SPEC must have a PARAMETER-REF')

    def _parseNvProvideComSpec(self, xmlRoot, portInterfaceRef):
        (romBlockInitValue, romBlockInitValueRef, ramBlockInitValue, ramBlockInitValueRef, name) = (None, None, None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'RAM-BLOCK-INIT-VALUE':
                ramBlockInitValue, ramBlockInitValueRef = self._parseAr4InitValue(xmlElem)
            elif xmlElem.tag == 'ROM-BLOCK-INIT-VALUE':
                romBlockInitValue, romBlockInitValueRef = self._parseAr4InitValue(xmlElem)
            elif xmlElem.tag == 'VARIABLE-REF':
                name = _getVariableNameFromComSpec(xmlElem, portInterfaceRef)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (name is not None):
            return autosar.port.NvProvideComSpec(name, ramBlockInitValue=ramBlockInitValue,
                                                    ramBlockInitValueRef=ramBlockInitValueRef,
                                                    romBlockInitValue=romBlockInitValue,
                                                    romBlockInitValueRef=romBlockInitValueRef)
        else:
            raise RuntimeError('NV-PROVIDE-COM-SPEC must have a VARIABLE-REF')

    def _parseNvRequireComSpec(self, xmlRoot, portInterfaceRef):
        (initValue, initValueRef, name) = (None, None, None)
        for xmlElem in xmlRoot.findall('./*'):
            if xmlElem.tag == 'INIT-VALUE':
                initValue, initValueRef = self._parseAr4InitValue(xmlElem)
            elif xmlElem.tag == 'VARIABLE-REF':
                name = _getVariableNameFromComSpec(xmlElem, portInterfaceRef)
            else:
                handleNotImplementedError(xmlElem.tag)
        if (name is not None):
            return autosar.port.NvRequireComSpec(name, initValue=initValue,
                                                    initValueRef=initValueRef)
        else:
            raise RuntimeError('NV-PROVIDE-COM-SPEC must have a VARIABLE-REF')

