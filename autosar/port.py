"""
Python autosar Ports and ComSpec classes.

Copyright (c) 2019-2021 Conny Gustafsson.
See LICENSE file for additional information.
"""

from autosar.element import Element
import autosar.portinterface
import autosar.constant
import autosar.builder
import copy
import collections

sender_receiver_com_spec_arguments_ar4 = {'dataElement', 'initValue', 'initValueRef', 'aliveTimeout', 'queueLength'}
sender_receiver_com_spec_arguments_ar3 = {'dataElement', 'canInvalidate', 'initValueRef', 'aliveTimeout', 'queueLength'}
client_server_com_spec_arguments = {'operation', 'queueLength'}
mode_switch_com_spec_arguments = {'enhancedMode', 'supportAsync', 'queueLength', 'modeSwitchAckTimeout', 'modeGroup'}
parameter_com_spec_arguments = {'parameter', 'initValue'}
nv_data_com_spec_arguments = {'nvData', 'initValue', 'initValueRef', 'ramBlockInitValue', 'ramBlockInitValueRef', 'romBlockInitValue', 'romBlockInitValueRef'}
valid_com_spec_arguments_ar4 = set().union(sender_receiver_com_spec_arguments_ar4, client_server_com_spec_arguments,
    mode_switch_com_spec_arguments, parameter_com_spec_arguments, nv_data_com_spec_arguments)
valid_com_spec_arguments_ar3 = set().union(sender_receiver_com_spec_arguments_ar3, client_server_com_spec_arguments, parameter_com_spec_arguments)

class Port(Element):
    def __init__(self, name, portInterfaceRef, comspec=None, autoCreateComspec = True, parent=None, adminData=None):
        super().__init__(name, parent, adminData)
        self.comspec=[]
        if portInterfaceRef is not None and not isinstance(portInterfaceRef,str):
            raise ValueError('portInterfaceRef needs to be of type None or str')
        self.portInterfaceRef = portInterfaceRef
        ws = self.rootWS()
        assert(ws is not None)
        portInterface=ws.find(portInterfaceRef, role='PortInterface')

        if comspec is None and autoCreateComspec:
            comspec = self._createDefaultComSpecList(portInterface)

        if comspec is not None:
            if isinstance(comspec, ComSpec):
                self.comspec.append(comspec)
            elif isinstance(comspec, collections.abc.Mapping):
                #Typical usage: port interfaces containing a single data element
                comspecObj = self._createComSpecFromDict(ws, portInterface, comspec)
                if comspecObj is None:
                    raise ValueError('Failed to create comspec from comspec data: '+repr(comspec))
                self.comspec.append(comspecObj)
            elif isinstance(comspec, collections.abc.Iterable):
                #Typical usage: port interfaces containing a multiple data elements
                for data in comspec:
                    comspecObj = self._createComSpecFromDict(ws, portInterface, data)
                    if comspecObj is None:
                        raise ValueError('Failed to create comspec from comspec data: '+repr(data))
                    self.comspec.append(comspecObj)
            else:
                raise NotImplementedError("not supported")

    def _createComSpecFromDict(self, ws, portInterface, comspec):
        """
        Creates ComSpec object based on generic key-value settings from a dictionary.
        """
        self._validate_com_spec_keys_against_port_interface(comspec, portInterface)

        if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
            dataElementName = None
            rawInitValue = None
            initValue = None
            initValueRef = None #initValue and initValueRef are mutually exclusive, you cannot have both defined at the same time
            aliveTimeout = 0
            queueLength = None
            canInvalidate = False if isinstance(self,ProvidePort) else None

            if 'dataElement' in comspec: dataElementName=str(comspec['dataElement'])
            if 'initValue' in comspec: rawInitValue=comspec['initValue']
            if 'initValueRef' in comspec: initValueRef=str(comspec['initValueRef'])
            if 'aliveTimeout' in comspec: aliveTimeout=int(comspec['aliveTimeout'])
            if 'queueLength' in comspec: queueLength=int(comspec['queueLength'])
            if 'canInvalidate' in comspec: canInvalidate=bool(comspec['canInvalidate'])
            if (dataElementName is None) and (len(portInterface.dataElements)==1):
                dataElementName=portInterface.dataElements[0].name
            #verify dataElementName
            dataElement=portInterface.find(dataElementName)
            if dataElement is None:
                raise ValueError("Unknown element '%s' of portInterface '%s'"%(dataElementName,portInterface.name))
            #verify compatibility of initValueRef
            if initValueRef is not None:
                initValueTmp = ws.find(initValueRef, role='Constant')
                if initValueTmp is None:
                    raise autosar.base.InvalidInitValueRef(str(initValueRef))
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
            if rawInitValue is not None:
                valueBuilder = autosar.builder.ValueBuilder()
                if isinstance(rawInitValue, autosar.constant.Value):
                    initValue = rawInitValue
                elif isinstance(rawInitValue, (int, float, str)):
                    dataType = ws.find(dataElement.typeRef, role='DataType')
                    if dataType is None:
                        raise autosar.base.InvalidDataTypeRef(dataElement.typeRef)
                    valueBuilder = autosar.builder.ValueBuilder()
                    initValue = valueBuilder.buildFromDataType(dataType, rawInitValue)
                else:
                    raise ValueError('initValue must be an instance of (autosar.constant.Value, int, float, str)')
            return DataElementComSpec(dataElement.name, initValue, initValueRef, aliveTimeout, queueLength, canInvalidate)
        elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            operation = comspec.get('operation', None)
            queueLength = comspec.get('queueLength', 1)
            if operation is not None:
                return OperationComSpec(operation,queueLength)
        elif isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
            enhancedMode = comspec.get('enhancedMode', ws.profile.modeSwitchEnhancedModeDefault)
            supportAsync = comspec.get('supportAsync', ws.profile.modeSwitchSupportAsyncDefault)
            queueLength = comspec.get('queueLength', None)
            modeSwitchAckTimeout = comspec.get('modeSwitchAckTimeout', None)
            modeGroupName = comspec.get('modeGroup', None)
            if modeGroupName is None:
                modeGroupName = portInterface.modeGroup.name
            if isinstance(self, RequirePort):
                return ModeSwitchComSpec(modeGroupName, enhancedMode, supportAsync, None, None)
            else:
                return ModeSwitchComSpec(modeGroupName, enhancedMode, None, queueLength, modeSwitchAckTimeout)
        elif isinstance(portInterface, autosar.portinterface.ParameterInterface):
            parameterName = comspec.get('parameter', None)
            if (parameterName is None) and (len(portInterface.parameters)==1):
                parameterName = portInterface.parameters[0].name
            initValue = comspec.get('initValue', None)
            return ParameterComSpec(parameterName, initValue)
        elif isinstance(portInterface, autosar.portinterface.NvDataInterface):
            nvDataName = None
            if 'nvData' in comspec: nvDataName=str(comspec['nvData'])
            if (nvDataName is None) and (len(portInterface.nvDatas)==1):
                nvDataName=portInterface.nvDatas[0].name
            #verify nvDataName
            nvData=portInterface.find(nvDataName)
            if nvData is None:
                raise ValueError("Unknown element '%s' of portInterface '%s'"%(nvDataName, portInterface.name))

            if isinstance(self, RequirePort):
                rawInitValue = None
                initValue = None
                initValueRef = None #initValue and initValueRef are mutually exclusive, you cannot have both defined at the same time

                if 'initValue' in comspec: rawInitValue=comspec['initValue']
                if 'initValueRef' in comspec: initValueRef=str(comspec['initValueRef'])
                #verify compatibility of initValueRef
                if initValueRef is not None:
                    initValueTmp = ws.find(initValueRef, role='Constant')
                    if initValueTmp is None:
                        raise autosar.base.InvalidInitValueRef(str(initValueRef))
                    if isinstance(initValueTmp,autosar.constant.Constant):
                        initValueRef=initValueTmp.ref
                    elif isinstance(initValueTmp,autosar.constant.Value):
                        initValueRef=initValueTmp.ref
                    else:
                        raise ValueError("reference is not a Constant or Value object: '%s'"%initValueRef)

                if rawInitValue is not None:
                    if isinstance(rawInitValue, autosar.constant.ValueAR4):
                        initValue = rawInitValue
                    elif isinstance(rawInitValue, (int, float, str)):
                        dataType = ws.find(nvData.typeRef, role='DataType')
                        if dataType is None:
                            raise autosar.base.InvalidDataTypeRef(nvData.typeRef)
                        valueBuilder = autosar.builder.ValueBuilder()
                        initValue = valueBuilder.buildFromDataType(dataType, rawInitValue)
                    else:
                        raise ValueError('initValue must be an instance of (autosar.constant.ValueAR4, int, float, str)')
                return NvRequireComSpec(nvData.name, initValue, initValueRef)
            else:
                # Provide com spec.
                rawRamBlockInitValue = None
                ramBlockInitValue = None
                ramBlockInitValueRef = None #ramBlockInitValue and ramBlockInitValueRef are mutually exclusive, you cannot have both defined at the same time
                rawRomBlockInitValue = None
                romBlockInitValue = None
                romBlockInitValueRef = None #romBlockInitValue and romBlockInitValueRef are mutually exclusive, you cannot have both defined at the same time
                if 'ramBlockInitValue' in comspec: rawRamBlockInitValue=comspec['ramBlockInitValue']
                if 'ramBlockInitValueRef' in comspec: ramBlockInitValueRef=str(comspec['ramBlockInitValueRef'])
                if 'romBlockInitValue' in comspec: rawRomBlockInitValue=comspec['romBlockInitValue']
                if 'romBlockInitValueRef' in comspec: romBlockInitValueRef=str(comspec['romBlockInitValueRef'])

                #verify compatibility of ramBlockInitValueRef
                if ramBlockInitValueRef is not None:
                    initValueTmp = ws.find(ramBlockInitValueRef, role='Constant')
                    if initValueTmp is None:
                        raise autosar.base.InvalidInitValueRef(str(ramBlockInitValueRef))
                    if isinstance(initValueTmp,autosar.constant.Constant):
                        ramBlockInitValueRef=initValueTmp.ref
                    elif isinstance(initValueTmp,autosar.constant.Value):
                        ramBlockInitValueRef=initValueTmp.ref
                    else:
                        raise ValueError("reference is not a Constant or Value object: '%s'"%ramBlockInitValueRef)

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

                if rawRamBlockInitValue is not None:
                    if isinstance(rawRamBlockInitValue, autosar.constant.ValueAR4):
                        ramBlockInitValue = rawRamBlockInitValue
                    elif isinstance(rawRamBlockInitValue, (int, float, str)):
                        dataType = ws.find(nvData.typeRef, role='DataType')
                        if dataType is None:
                            raise autosar.base.InvalidDataTypeRef(nvData.typeRef)
                        valueBuilder = autosar.builder.ValueBuilder()
                        ramBlockInitValue = valueBuilder.buildFromDataType(dataType, rawRamBlockInitValue)
                    else:
                        raise ValueError('ramBlockInitValue must be an instance of (autosar.constant.ValueAR4, int, float, str)')

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
                return NvProvideComSpec(nvData.name, ramBlockInitValue, ramBlockInitValueRef, romBlockInitValue, romBlockInitValueRef)
        else:
            raise NotImplementedError(type(portInterface))
        return None

    def _validate_com_spec_keys_against_port_interface(self, comspec, portInterface):
        if portInterface is None:
            return
        ws = self.rootWS()
        assert(ws is not None)
        if ws.version <= 4.0:
            valid_arguments = valid_com_spec_arguments_ar3
        else:
            valid_arguments = valid_com_spec_arguments_ar4
        for key in comspec.keys():
            if key not in valid_arguments:
                raise ValueError("Unsupported comspec argument '{}'".format(key))

        if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
            if ws.version <= 4.0:
                valid_arguments = sender_receiver_com_spec_arguments_ar3
            else:
                valid_arguments = sender_receiver_com_spec_arguments_ar4
        elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            valid_arguments = client_server_com_spec_arguments
        elif isinstance(portInterface, autosar.portinterface.ModeSwitchInterface):
            valid_arguments = mode_switch_com_spec_arguments
        elif isinstance(portInterface, autosar.portinterface.ParameterInterface):
            valid_arguments = parameter_com_spec_arguments
        elif isinstance(portInterface, autosar.portinterface.NvDataInterface):
            valid_arguments = nv_data_com_spec_arguments
        else:
            raise RuntimeError("Unsupported port interface:" + str(type(portInterface)))
        for key in comspec.keys():
            if key not in valid_arguments:
                raise ValueError("Comspec argument '{}' doesn't match interface type {}".format(key, type(portInterface)))

    def _createDefaultComSpecList(self, portInterface):
        if portInterface is None:
            return None
        comspecList = []
        if isinstance(portInterface, autosar.portinterface.SenderReceiverInterface):
            for dataElement in portInterface.dataElements:
                comspecList.append({'dataElement': dataElement.name})
        elif isinstance(portInterface,autosar.portinterface.ClientServerInterface):
            for operation in portInterface.operations:
                comspecList.append({'operation': operation.name})
        elif isinstance(portInterface,autosar.portinterface.ParameterInterface):
            for parameter in portInterface.parameters:
                comspecList.append({'parameter': parameter.name})
        elif isinstance(portInterface,autosar.portinterface.NvDataInterface):
            for nvData in portInterface.nvDatas:
                comspecList.append({'nvData': nvData.name})
        elif isinstance(portInterface,autosar.portinterface.ModeSwitchInterface):
            #TODO: Why are we treating ModeSwitchInterface in a different way from the others?
            modeGroupName = portInterface.modeGroup.name
            comspecList.append({'modeGroup': modeGroupName, 'enhancedMode':False, 'supportAsync': False})
        return None if len(comspecList)==0 else comspecList


class RequirePort(Port):
    def tag(self,version=None): return "R-PORT-PROTOTYPE"
    def __init__(self,name , portInterfaceRef=None, comspec=None, autoCreateComSpec = True, parent=None):
        if isinstance(name, str):
            #normal constructor
            super().__init__(name, portInterfaceRef, comspec, autoCreateComSpec, parent)
        elif isinstance(name, (RequirePort, ProvidePort)):
            other=name #alias
            #copy constructor
            super().__init__(other.name, other.portInterfaceRef, None, False, parent)
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
    def __init__(self, name, portInterfaceRef = None, comspec = None, autoCreateComSpec = True, parent = None):
        if isinstance(name, str):
        #normal constructor
            super().__init__(name, portInterfaceRef, comspec, autoCreateComSpec, parent)
        elif isinstance(name, (RequirePort, ProvidePort)):
            other=name #alias
            #copy constructor
            super().__init__(other.name, other.portInterfaceRef, None, False, parent)
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

class ComSpec:
    def __init__(self, name=None):
        self.name = name

class OperationComSpec(ComSpec):
    def __init__(self, name=None, queueLength=1):
        super().__init__(name)
        self.queueLength=queueLength

class DataElementComSpec(ComSpec):
    def __init__(self, name=None, initValue=None, initValueRef=None, aliveTimeout=None, queueLength=None, canInvalidate=None, useEndToEndProtection = None):
        super().__init__(name)
        if initValue is not None:
            assert(isinstance(initValue, (autosar.constant.Value, autosar.constant.ValueAR4)))
        self.initValue = initValue
        self.initValueRef = str(initValueRef) if initValueRef is not None else None
        self._aliveTimeout = int(aliveTimeout) if aliveTimeout is not None else None
        self._queueLength = int(queueLength) if queueLength is not None else None
        self.canInvalidate = bool(canInvalidate) if canInvalidate is not None else None
        self.useEndToEndProtection = bool(useEndToEndProtection) if useEndToEndProtection is not None else None

    @property
    def aliveTimeout(self):
        return self._aliveTimeout

    @aliveTimeout.setter
    def aliveTimeout(self,val):
        try:
            self._aliveTimeout = int(val)
        except ValueError:
            self._aliveTimeout = str(val)

    @property
    def queueLength(self):
        return self._queueLength

    @queueLength.setter
    def queueLength(self,val):
        if val is None:
            self._queueLength = None
        else:
            val = int(val)
            if (val > 0):
                self._queueLength = int(val)
            else:
                raise ValueError('queueLength must be None or an int greater than zero')

class ModeSwitchComSpec(ComSpec):
    """
    Implementation of <MODE-SWITCH-SENDER-COM-SPEC> and <MODE-SWITCH-RECEIVER-COM-SPEC>

    Attributes:
    name: Name of the ModeGroup in the associated portInterface (str). This has higher precedence than modeGroupRef.
    enhancedMode: Enables/Disables enhanced mode API (None or bool)
    supportAsync: Enables/Disables support for asynchronous call  (None or bool)
    modeGroupRef: Reference to ModeDeclarationGroup (of the same port interface) (None or str)
    queueLength: Length of call queue on the mode user side (None or int)
    modeSwitchAckTimeout: Timeout (in milliseconds) for acknowledgement of the successful processing of the mode switch request (None or int).
    modeGroupRef: Full mode group reference (None or str). This has lower precendence to name (only used when name is None)
    """
    def __init__(self, name=None, enhancedMode=None, supportAsync=None, queueLength = None, modeSwitchAckTimeout = None, modeGroupRef = None):
        super().__init__(name)
        self.enhancedMode = bool(enhancedMode) if enhancedMode is not None else None
        self.supportAsync = bool(supportAsync) if supportAsync is not None else None
        self._queueLength = int(queueLength) if queueLength is not None else None
        self._modeSwitchAckTimeout = int(modeSwitchAckTimeout) if modeSwitchAckTimeout is not None else None
        self.modeGroupRef = str(modeGroupRef) if modeGroupRef is not None else None

    def tag(self, version, parentPort):
        if isinstance(parentPort, ProvidePort):
            return "MODE-SWITCH-SENDER-COM-SPEC"
        else:
            return "MODE-SWITCH-RECEIVER-COM-SPEC"

    @property
    def queueLength(self):
        return self._queueLength

    @queueLength.setter
    def queueLength(self,val):
        if val is None:
            self._queueLength = None
        else:
            if (val > 0):
                self._queueLength = int(val)
            else:
                raise ValueError('queueLength must be None or an int greater than zero')

    @property
    def modeSwitchAckTimeout(self):
        return self._modeSwitchAckTimeout

    @modeSwitchAckTimeout.setter
    def modeSwitchAckTimeout(self,val):
        if val is None:
            self._modeSwitchAckTimeout = None
        else:
            self._modeSwitchAckTimeout = int(val)

class ParameterComSpec(ComSpec):
    def __init__(self, name, initValue=None):
        super().__init__(name)
        self.initValue = initValue

class NvProvideComSpec(ComSpec):
    """
    Implementation of <NV-PROVIDE-COM-SPEC>

    Attributes:
    name: Name of the NvData in the associated portInterface (str). This has higher precedence than modeGroupRef.
    ramBlockInitValue: Ram block init value.
    ramBlockInitValueRef: Ram block init value reference.
    romBlockInitValue: Rom block init value.
    romBlockInitValueRef: Rom block init value reference.
    variableRef: Full NvData reference (None or str). This has lower precendence to name (only used when name is None)
    """
    def __init__(self, name=None, ramBlockInitValue=None, ramBlockInitValueRef=None, romBlockInitValue=None, romBlockInitValueRef=None, variableRef=None):
        super().__init__(name)
        self.ramBlockInitValue = ramBlockInitValue
        self.ramBlockInitValueRef = str(ramBlockInitValueRef) if ramBlockInitValueRef is not None else None
        self.romBlockInitValue = romBlockInitValue
        self.romBlockInitValueRef = str(romBlockInitValueRef) if romBlockInitValueRef is not None else None
        self.variableRef = str(variableRef) if variableRef is not None else None

    def tag(self, version, parentPort):
            return "NV-PROVIDE-COM-SPEC"

class NvRequireComSpec(ComSpec):
    """
    Implementation of <NV-REQUIRE-COM-SPEC>

    Attributes:
    name: Name of the NvData in the associated portInterface (str). This has higher precedence than modeGroupRef.
    initValue: Init value.
    initValueRef: Ram block init value reference.
    variableRef: Full NvData reference (None or str). This has lower precendence to name (only used when name is None)
    """
    def __init__(self, name=None, initValue=None, initValueRef=None, variableRef=None):
        super().__init__(name)
        self.initValue = initValue
        self.initValueRef = str(initValueRef) if initValueRef is not None else None
        self.variableRef = str(variableRef) if variableRef is not None else None

    def tag(self, version, parentPort):
            return "NV-REQUIRE-COM-SPEC"
