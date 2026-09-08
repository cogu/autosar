"""Software component elements."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Union

from autosar.base import Searchable, split_ref
from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import ARElement, Identifiable
from autosar.xml.elements.common import DataFilter, Trigger
from autosar.xml.elements.constant import (
    InitValueArgType,
    ValueSpecification,
    ValueSpecificationElement,
)
from autosar.xml.elements.data_type import (
    SwDataDefProps,
    SymbolProps,
    VariableDataPrototype,
)
from autosar.xml.elements.mode_declaration import ModeDeclarationGroupPrototype
from autosar.xml.elements.port_interface import (
    ClientServerInterface,
    ClientServerOperation,
    ModeSwitchInterface,
    PortInterface,
    SenderReceiverInterface,
    TriggerInterface,
)
from autosar.xml.elements.system_template import EndToEndTransformationComSpecProps
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except
from autosar.xml.reference import (
    AbstractProvidedPortPrototypeRef,
    AbstractRequiredPortPrototypeRef,
    AutosarDataPrototypeRef,
    ClientServerOperationRef,
    ModeDeclarationGroupPrototypeRef,
    ModeDeclarationRef,
    ParameterDataPrototypeRef,
    PortInterfaceRef,
    PortPrototypeRef,
    SwComponentPrototypeRef,
    SwComponentTypeRef,
    TriggerRef,
    VariableDataPrototypeRef,
)

if TYPE_CHECKING:
    from autosar.xml.elements.internal_behavior import SwcInternalBehavior, VariableAccess


def _get_variable_access_class():
    from autosar.xml.elements.internal_behavior import VariableAccess
    return VariableAccess


def _get_swc_internal_behavior_class():
    from autosar.xml.elements.internal_behavior import SwcInternalBehavior
    return SwcInternalBehavior


PortPrototypeElement = Union[
    "ProvidePortPrototype",
    "RequirePortPrototype",
    "PRPortPrototype",
]

SwConnectorElement = Union[
    "AssemblySwConnector",
    "DelegationSwConnector",
    "PassThroughSwConnector",
]


class ModeSwitchedAckRequest(ARObject):
    """
    Complex type AR:MODE-SWITCHED-ACK-REQUEST
    Tag variants: 'MODE-SWITCHED-ACK'
    """

    def __init__(self, timeout: float | None = None) -> None:
        super().__init__()
        self.timeout: float | None = None
        self._assign_optional("timeout", timeout, float)


class TransmissionAcknowledgementRequest(ARObject):
    """
    Complex type AR:TRANSMISSION-ACKNOWLEDGEMENT-REQUEST
    Tag variants: 'TRANSMISSION-ACKNOWLEDGE'
    """

    def __init__(self,
                 timeout: float | int | None = None) -> None:
        super().__init__()
        self.timeout: float | None = None  # .TIMEOUT
        self._assign_optional("timeout", timeout, float)


class TransmissionComSpecProps(ARObject):
    """
    Complex type AR:TRANSMISSION-COM-SPEC-PROPS
    Tag variants: 'TRANSMISSION-PROPS'

    This only exists in AUTOSAR 4.6 or newer (schema version >= 49)
    """

    def __init__(self,
                 data_update_period: float | int | None = None,
                 minimum_send_interval: float | int | None = None,
                 transmission_mode: ar_enum.TransmissionMode | None = None
                 ) -> None:
        super().__init__()
        self.data_update_period: float | int | None = None  # .DATA-UPDATE-PERIOD
        self.minimum_send_interval: float | int | None = None  # .MINIMUM-SEND-INTERVAL
        self.transmission_mode: ar_enum.TransmissionMode | None = None  # .TRANSMISSION-MODE
        self._assign_optional("data_update_period", data_update_period, float)
        self._assign_optional("minimum_send_interval", minimum_send_interval, float)
        self._assign_optional("transmission_mode", transmission_mode, ar_enum.TransmissionMode)


class ProvidePortComSpec(ARObject):
    """
    Group AR:P-PORT-COM-SPEC
    """

    @convenience_function
    @classmethod
    def make_from_port_interface(cls, port_interface: PortInterface, **kwargs) -> "ProvidePortComSpec":
        """

        Creates P-PORT com-spec from port interface

        For SenderReceiverInterface:
        If interface has a single element: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple elements: kwargs is a dict of dict where
                                            outer dict keys are element names and each value
                                            is another dict containing key-value pairs for one com-spec

        For ClientServerInterface:
        If interface has a single operation: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple operations: kwargs is a dict of dict where
                                              outer dict keys are operation names and each value
                                              is another dict containing key-value pairs for one com-spec

        For ModeSwitchInterface:
        kwargs is a dict with key-value pairs for one com-spec
        Note: Avoid manually setting the mode_group_ref option, it will be automatically set for you.
        """
        if isinstance(port_interface, SenderReceiverInterface):
            if len(port_interface.data_elements) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one element")
            if len(port_interface.data_elements) == 1:
                data_element: VariableDataPrototype = port_interface.data_elements[0]
                if data_element.is_queued:
                    return QueuedSenderComSpec(data_element_ref=data_element.ref(), **kwargs)
                else:
                    return cls.make_non_queued_sender_com_spec(data_element_ref=data_element.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for element_name, value in kwargs.items():
                    unprocessed.add(element_name)
                    if not isinstance(value, dict):
                        msg = f"{port_interface.name}.{element_name}: Expected dict type, got {str(type(value))}"
                        raise TypeError(msg)
                for data_element in port_interface.data_elements:
                    if data_element.name in unprocessed:
                        unprocessed.remove(data_element.name)
                        com_spec_args = kwargs[data_element.name]
                        if data_element.is_queued:
                            com_spec = QueuedSenderComSpec(data_element_ref=data_element.ref(),
                                                           **com_spec_args)
                        else:
                            com_spec = cls.make_non_queued_sender_com_spec(data_element_ref=data_element.ref(),
                                                                           **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    element_names = ', '.join(list(unprocessed))
                    msg = f"{port_interface.name}: Data element(s) not found in port interface: '{element_names}'"
                    raise ValueError(msg)
                return com_spec_list
        if isinstance(port_interface, ClientServerInterface):
            if len(port_interface.operations) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one operation")
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
                return ServerComSpec(operation_ref=operation.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for operation_name in kwargs:
                    unprocessed.add(operation_name)
                for operation in port_interface.operations:
                    if operation.name in unprocessed:
                        unprocessed.remove(operation.name)
                        com_spec_args = kwargs[operation.name]
                        com_spec = ServerComSpec(operation_ref=operation.ref(), **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    operations = ', '.join(list(unprocessed))
                    raise ValueError(f"{port_interface.name}: Operation(s) not found in port interface: '{operations}'")
                return com_spec_list
        elif isinstance(port_interface, ModeSwitchInterface):
            if port_interface.mode_group is None:
                raise ValueError(f"{port_interface.name}: Port interface doesn't have a mode group set")
            assert port_interface.mode_group.ref() is not None
            return ModeSwitchSenderComSpec(mode_group_ref=port_interface.mode_group.ref(), **kwargs)
        else:
            raise NotImplementedError(str(type(port_interface)))

    @convenience_function
    @classmethod
    def make_non_queued_sender_com_spec(cls,
                                        init_value: InitValueArgType | None = None,
                                        **kwargs
                                        ) -> "NonqueuedSenderComSpec":
        """

        Convenience method for creating NonqueuedSenderComSpec
        """
        init_value = ValueSpecification.make_value_with_check(init_value)
        return NonqueuedSenderComSpec(init_value=init_value, **kwargs)


class SenderComSpec(ProvidePortComSpec):
    """
    Group AR:SENDER-COM-SPEC
    """

    def __init__(self,
                 data_element_ref: AutosarDataPrototypeRef | VariableDataPrototypeRef | None = None,
                 handle_out_of_range: ar_enum.HandleOutOfRange | None = None,
                 network_representation: SwDataDefProps | None = None,
                 transmission_acknowledge: TransmissionAcknowledgementRequest | float | None = None,
                 tranmsission_props: TransmissionComSpecProps | None = None,
                 uses_end_to_end_protection: bool | None = None
                 ) -> None:
        super().__init__()
        # .COMPOSITE-NETWORK-REPRESENTATIONS not supported
        self.data_element_ref: AutosarDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        # .DATA-UPDATE-PERIOD not supported (Status Removed)
        self.handle_out_of_range: ar_enum.HandleOutOfRange | None = None  # .HANDLE-OUT-OF-RANGE
        self.network_representation: SwDataDefProps | None = None  # .NETWORK-REPRESENTATION
        # .SENDER-INTENT not supported (Adaptive Platform)
        self.transmission_acknowledge: TransmissionAcknowledgementRequest | None = None  # .TRANSMISSION-ACKNOWLEDGE
        self.tranmsission_props: TransmissionComSpecProps | None = None  # .TRANSMISSION-PROPS
        self.uses_end_to_end_protection: bool | None = None  # .USES-END-TO-END-PROTECTION
        if data_element_ref is not None:
            if isinstance(data_element_ref, AutosarDataPrototypeRef):
                self.data_element_ref = data_element_ref
            elif isinstance(data_element_ref, VariableDataPrototypeRef):
                self.data_element_ref = AutosarDataPrototypeRef(data_element_ref.value,
                                                                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
            else:
                raise ar_except.AssignmentTypeError("data_element_ref",
                                                    ("AutosarDataPrototypeRef", "VariableDataPrototypeRef"),
                                                    data_element_ref)
        self._assign_optional("handle_out_of_range", handle_out_of_range, ar_enum.HandleOutOfRange)
        self._assign_optional_strict("network_representation", network_representation, SwDataDefProps)
        self._assign_optional_strict("tranmsission_props", tranmsission_props, TransmissionComSpecProps)
        self._assign_optional("uses_end_to_end_protection", uses_end_to_end_protection, bool)
        if transmission_acknowledge is not None:
            if isinstance(transmission_acknowledge, (int, float)):
                self.transmission_acknowledge = TransmissionAcknowledgementRequest(transmission_acknowledge)
            elif isinstance(transmission_acknowledge, TransmissionAcknowledgementRequest):
                self.transmission_acknowledge = transmission_acknowledge
            else:
                msg_part1 = f"Invalid type '{str(type(transmission_acknowledge))}'"
                msg_part2 = "Expected (TransmissionAcknowledgementRequest, float)"
                raise TypeError(f"transmission_acknowledge: {msg_part1}. {msg_part2}.")


class ModeSwitchSenderComSpec(ProvidePortComSpec):
    """
    Complex type AR:MODE-SWITCH-SENDER-COM-SPEC
    Tag variants: 'MODE-SWITCH-SENDER-COM-SPEC'
    """

    def __init__(self,
                 mode_group_ref: str | ModeDeclarationGroupPrototypeRef | None = None,
                 enhanced_mode_api: bool | None = None,
                 mode_switched_ack: ModeSwitchedAckRequest | float | None = None,
                 queue_length: int | None = None
                 ) -> None:
        super().__init__()
        self.mode_group_ref: ModeDeclarationGroupPrototypeRef | None = None  # .ENHANCED-MODE-API
        self.enhanced_mode_api: bool | None = None  # .MODE-GROUP-REF
        self.mode_switched_ack: ModeSwitchedAckRequest | None = None  # .MODE-SWITCHED-ACK
        self.queue_length = None  # .QUEUE-LENGTH
        self._assign_optional("mode_group_ref", mode_group_ref, ModeDeclarationGroupPrototypeRef)
        self._assign_optional("enhanced_mode_api", enhanced_mode_api, bool)
        if mode_switched_ack is not None:
            if isinstance(mode_switched_ack, (int, float)):
                self.mode_switched_ack = ModeSwitchedAckRequest(mode_switched_ack)
            elif isinstance(mode_switched_ack, ModeSwitchedAckRequest):
                self.mode_switched_ack = mode_switched_ack
            else:
                msg = f"Invalid type. Expected (ModeSwitchedAckRequest, str), got '{str(type(mode_switched_ack))}'"
                raise TypeError("mode_switched_ack: " + msg)
        self._assign_optional_positive_int("queue_length", queue_length)


class QueuedSenderComSpec(SenderComSpec):
    """
    Complex type AR:QUEUED-SENDER-COM-SPEC
    Tag variants: 'QUEUED-SENDER-COM-SPEC'

    Doesn't need its own constuctor, we can use the one defined by base class
    """


class NonqueuedSenderComSpec(SenderComSpec):
    """
    Complex type AR:NONQUEUED-SENDER-COM-SPEC
    Tag variants: 'NONQUEUED-SENDER-COM-SPEC'
    """

    def __init__(self,
                 init_value: ValueSpecificationElement | None = None,
                 data_filter: DataFilter | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.data_filter: DataFilter | None = None  # .DATA-FILTER
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self._assign_optional_strict("data_filter", data_filter, DataFilter)
        self._assign_optional_strict("init_value", init_value, ValueSpecification)


class NvProvideComSpec(ProvidePortComSpec):
    """
    Complex type AR:NV-PROVIDE-COM-SPEC
    Tag variants: 'NV-PROVIDE-COM-SPEC'
    """

    def __init__(self,
                 variable_ref: VariableDataPrototypeRef | None = None,
                 ram_block_init_value: ValueSpecificationElement | None = None,
                 rom_block_init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.ram_block_init_value: ValueSpecificationElement | None = None  # .RAM-BLOCK-INIT-VALUE
        self.rom_block_init_value: ValueSpecificationElement | None = None  # .RAM-BLOCK-INIT-VALUE
        self.variable_ref: VariableDataPrototypeRef | None = None         # .VARIABLE-REF
        self._assign_optional_strict("ram_block_init_value", ram_block_init_value, ValueSpecification)
        self._assign_optional_strict("rom_block_init_value", rom_block_init_value, ValueSpecification)
        self._assign_optional("variable_ref", variable_ref, VariableDataPrototypeRef)


class ParameterProvideComSpec(ProvidePortComSpec):
    """
    Complex type AR:PARAMETER-PROVIDE-COM-SPEC
    Tag variants: 'PARAMETER-PROVIDE-COM-SPEC'
    """

    def __init__(self,
                 parameter_ref: ParameterDataPrototypeRef | str | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.parameter_ref: VariableDataPrototypeRef | None = None  # .PARAMETER-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("parameter_ref", parameter_ref, ParameterDataPrototypeRef)


EndToEndTransformationComSpecPropsArgTypes = Union[EndToEndTransformationComSpecProps,
                                                   list[EndToEndTransformationComSpecProps]]


class ServerComSpec(ProvidePortComSpec):
    """
    Complex type AR:SERVER-COM-SPEC
    Tag variants: 'SERVER-COM-SPEC'
    """

    def __init__(self,
                 operation_ref: ClientServerOperationRef | None = None,
                 queue_length: int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None
                 ) -> None:
        super().__init__()
        # .GETTER-REF not supported (Adaptive Platform)
        self.operation_ref: ClientServerOperationRef | None = None  # .OPERATION-REF
        self.queue_length: int | None = None  # .QUEUE-LENGTH
        # .SETTER-REF not supported (Adaptive Platform)
        # .TRANSFORMATION-COM-SPEC-PROPSS
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        # USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet supported under transformation_com_spec_props
        self._assign_optional("operation_ref", operation_ref, ClientServerOperationRef)
        self._assign_optional_positive_int("queue_length", queue_length)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(props)
        else:
            raise TypeError("props must be of type EndToEndTransformationComSpecProps")


class ReceptionComSpecProps(ARObject):
    """
    Complex type AR:RECEPTION-COM-SPEC-PROPS
    Tag variants: 'RECEPTION-PROPS'
    """

    def __init__(self,
                 data_update_period: float | None = None,
                 timeout: float | None = None,
                 ) -> None:
        super().__init__()
        self.data_update_period: float | None = None  # .DATA-UPDATE-PERIOD
        self.timeout: float | None = None  # .TIMEOUT
        self._assign_optional("data_update_period", data_update_period, float)
        self._assign_optional("timeout", timeout, float)


class RequirePortComSpec(ARObject):
    """
    Group AR:R-PORT-COM-SPEC
    """

    @convenience_function
    @classmethod
    def make_from_port_interface(cls, port_interface: PortInterface, **kwargs) -> "RequirePortComSpec":
        """

        Creates R-PORT com-spec from port-interface

        For SenderReceiverInterface:
        If interface has a single element: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple elements: kwargs is a dict of dict where
                                            outer dict keys are element names and each value
                                            is another dict containing key-value pairs for one com-spec

        Note: Avoid manually setting the data_element_ref option, it will be automatically set for you.

        For ClientServerInterface:
        If interface has a single operation: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple operations: kwargs is a dict of dict where
                                              outer dict keys are operation names and each value
                                              is another dict containing key-value pairs for one com-spec
        Note: Avoid manually setting the operation_ref option, it will be automatically set for you.

        For ModeSwitchInterface:
        kwargs is a dict with key-value pairs for one com-spec
        Note: Avoid manually setting the mode_group_ref option, it will be automatically set for you.
        """
        if isinstance(port_interface, SenderReceiverInterface):
            if len(port_interface.data_elements) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one element")
            if len(port_interface.data_elements) == 1:
                data_element: VariableDataPrototype = port_interface.data_elements[0]
                if data_element.is_queued:
                    assert data_element.ref() is not None
                    return QueuedReceiverComSpec(data_element_ref=data_element.ref(), **kwargs)
                else:
                    return cls.make_non_queued_receiver_com_spec(data_element_ref=data_element.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for element_name, value in kwargs.items():
                    unprocessed.add(element_name)
                    if not isinstance(value, dict):
                        msg = f"{port_interface.name}.{element_name}: Expected dict type, got {str(type(value))}"
                        raise TypeError(msg)
                for data_element in port_interface.data_elements:
                    if data_element.name in unprocessed:
                        unprocessed.remove(data_element.name)
                        com_spec_args = kwargs[data_element.name]
                        assert data_element.ref() is not None
                        if data_element.is_queued:
                            com_spec = QueuedReceiverComSpec(data_element_ref=data_element.ref(),
                                                             **com_spec_args)
                        else:
                            com_spec = cls.make_non_queued_receiver_com_spec(data_element_ref=data_element.ref(),
                                                                             **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    element_names = ', '.join(list[unprocessed])
                    msg = f"{port_interface.name}: Data element(s) not found in port interface: '{element_names}'"
                    raise ValueError(msg)
                return com_spec_list
        elif isinstance(port_interface, ClientServerInterface):
            if len(port_interface.operations) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one operation")
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
                return ClientComSpec(operation_ref=operation.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for operation_name in kwargs:
                    unprocessed.add(operation_name)
                for operation in port_interface.operations:
                    if operation.name in unprocessed:
                        unprocessed.remove(operation.name)
                        com_spec_args = kwargs[operation.name]
                        assert operation.ref() is not None
                        com_spec = ClientComSpec(operation_ref=operation.ref(), **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    operations = ', '.join(list[unprocessed])
                    raise ValueError(f"{port_interface.name}: Operation(s) not found in port interface: '{operations}'")
                return com_spec_list
        elif isinstance(port_interface, ModeSwitchInterface):
            if port_interface.mode_group is None:
                raise ValueError(f"{port_interface.name}: Port interface doesn't have a mode group set")
            assert port_interface.mode_group.ref() is not None
            return ModeSwitchReceiverComSpec(mode_group_ref=port_interface.mode_group.ref(), **kwargs)
        else:
            raise NotImplementedError(str(type(port_interface)))

    @convenience_function
    @classmethod
    def make_non_queued_receiver_com_spec(cls,
                                          init_value: InitValueArgType | None = None,
                                          **kwargs
                                          ) -> "NonqueuedReceiverComSpec":
        """

        Convenience method for creating NonqueuedReceiverComSpec
        """
        init_value = ValueSpecification.make_value_with_check(init_value)
        return NonqueuedReceiverComSpec(init_value=init_value, **kwargs)


class ReceiverComSpec(RequirePortComSpec):
    """
    Group AR:RECEIVER-COM-SPEC
    """

    def __init__(self,
                 data_element_ref: AutosarDataPrototypeRef | VariableDataPrototypeRef | None = None,
                 handle_out_of_range: ar_enum.HandleOutOfRange | None = None,
                 handle_out_of_range_status: ar_enum.HandleOutOfRangeStatus | None = None,
                 max_delta_counter_init: int | None = None,
                 max_no_new_repeated_data: int | None = None,
                 network_representation: SwDataDefProps | None = None,
                 reception_props: ReceptionComSpecProps | None = None,
                 replace_with: Union["VariableAccess", None] = None,
                 sync_counter_init: int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None,
                 uses_end_to_end_protection: bool | None = None
                 ) -> None:
        super().__init__()
        # .COMPOSITE-NETWORK-REPRESENTATIONS not supported
        self.data_element_ref: AutosarDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        # .DATA-UPDATE-PERIOD not supported (Status Removed)
        # .EXTERNAL-REPLACEMENT-REF not supported (Status Removed)
        self.handle_out_of_range: ar_enum.HandleOutOfRange | None = None  # .HANDLE-OUT-OF-RANGE
        self.handle_out_of_range_status: ar_enum.HandleOutOfRangeStatus | None = None  # .HANDLE-OUT-OF-RANGE-STATUS
        self.max_delta_counter_init: int | None = None   # .MAX-DELTA-COUNTER-INIT
        self.max_no_new_repeated_data: int | None = None   # .MAX-NO-NEW-OR-REPEATED-DATA
        self.network_representation: SwDataDefProps | None = None  # .NETWORK-REPRESENTATION
        # .RECEIVER-INTENT not supported (adaptive platform)
        self.reception_props: ReceptionComSpecProps | None = None  # .RECEPTION-PROPS
        self.replace_with: VariableAccess | None = None  # .REPLACE-WITH
        self.sync_counter_init: int | None = None   # .SYNC-COUNTER-INIT
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        self.uses_end_to_end_protection: bool | None = None  # .USES-END-TO-END-PROTECTION
        if data_element_ref is not None:
            if isinstance(data_element_ref, AutosarDataPrototypeRef):
                self.data_element_ref = data_element_ref
            elif isinstance(data_element_ref, VariableDataPrototypeRef):
                self.data_element_ref = AutosarDataPrototypeRef(data_element_ref.value,
                                                                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
            else:
                raise ar_except.AssignmentTypeError("data_element_ref",
                                                    ("AutosarDataPrototypeRef", "VariableDataPrototypeRef"),
                                                    data_element_ref)

        self._assign_optional("handle_out_of_range", handle_out_of_range, ar_enum.HandleOutOfRange)
        self._assign_optional("handle_out_of_range_status", handle_out_of_range_status, ar_enum.HandleOutOfRangeStatus)
        self._assign_optional_positive_int("max_delta_counter_init", max_delta_counter_init)
        self._assign_optional_positive_int("max_no_new_repeated_data", max_no_new_repeated_data)
        self._assign_optional_strict("network_representation", network_representation, SwDataDefProps)
        self._assign_optional_strict("reception_props", reception_props, ReceptionComSpecProps)
        if replace_with is not None:
            self._assign_optional_strict("replace_with", replace_with, _get_variable_access_class())
        self._assign_optional_positive_int("sync_counter_init", sync_counter_init)
        self._assign_optional("uses_end_to_end_protection", uses_end_to_end_protection, bool)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, com_spec_props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(com_spec_props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(com_spec_props)
        else:
            raise TypeError("com_spec_props must be of type EndToEndTransformationComSpecProps")


class QueuedReceiverComSpec(ReceiverComSpec):
    """
    Complex type AR:QUEUED-RECEIVER-COM-SPEC
    Tag variants: 'QUEUED-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 queue_length: int | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.queue_length: int | None = None  # .QUEUE-LENGTH
        self._assign_optional_positive_int("queue_length", queue_length)


class NonqueuedReceiverComSpec(ReceiverComSpec):
    """
    Complex type AR:NONQUEUED-RECEIVER-COM-SPEC
    Tag variants: 'NONQUEUED-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 alive_timeout: int | float | None = None,
                 enable_update: bool | None = None,
                 data_filter: DataFilter | None = None,
                 handle_data_status: bool | None = None,
                 handle_never_received: bool | None = None,
                 handle_timeout_type: ar_enum.HandleTimeout | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 timeout_substitution_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.alive_timeout: int | float | None = None  # .ALIVE-TIMEOUT
        self.enable_update: bool | None = None  # .ENABLE-UPDATE
        self.data_filter: DataFilter | None = None  # .FILTER
        self.handle_data_status: bool | None = None  # .HANDLE-DATA-STATUS
        self.handle_never_received: bool | None = None  # .HANDLE-NEVER-RECEIVED
        self.handle_timeout_type: ar_enum.HandleTimeout | None = None  # .HANDLE-TIMEOUT-TYPE
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.timeout_substitution_value: ValueSpecificationElement | None = None  # .TIMEOUT-SUBSTITUTION-VALUE
        self._assign_optional("alive_timeout", alive_timeout, float)
        self._assign_optional("enable_update", enable_update, bool)
        self._assign_optional_strict("data_filter", data_filter, DataFilter)
        self._assign_optional("handle_data_status", handle_data_status, bool)
        self._assign_optional("handle_never_received", handle_never_received, bool)
        self._assign_optional("handle_timeout_type", handle_timeout_type, ar_enum.HandleTimeout)
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional_strict("timeout_substitution_value", timeout_substitution_value, ValueSpecification)


class NvRequireComSpec(RequirePortComSpec):
    """
    Complex type AR:NV-REQUIRE-COM-SPEC
    Tag variants: 'NV-REQUIRE-COM-SPEC'
    """

    def __init__(self,
                 variable_ref: VariableDataPrototypeRef | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.variable_ref: VariableDataPrototypeRef | None = None  # .VARIABLE-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("variable_ref", variable_ref, VariableDataPrototypeRef)


class ParameterRequireComSpec(RequirePortComSpec):
    """
    Complex type AR:PARAMETER-REQUIRE-COM-SPEC
    Tag variants: 'PARAMETER-REQUIRE-COM-SPEC'
    """

    def __init__(self,
                 parameter_ref: ParameterDataPrototypeRef | str | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.parameter_ref: VariableDataPrototypeRef | None = None  # .PARAMETER-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("parameter_ref", parameter_ref, ParameterDataPrototypeRef)


class ModeSwitchReceiverComSpec(RequirePortComSpec):
    """
    Complex type AR:MODE-SWITCH-RECEIVER-COM-SPEC
    Tag variants: 'MODE-SWITCH-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 mode_group_ref: str | ModeDeclarationGroupPrototypeRef | None = None,
                 enhanced_mode_api: bool | None = None,
                 supports_async: bool | None = None,
                 ) -> None:
        super().__init__()
        self.mode_group_ref: ModeDeclarationGroupPrototypeRef | None = None  # .ENHANCED-MODE-API
        self.enhanced_mode_api: bool | None = None  # .MODE-GROUP-REF
        self.supports_async: bool | None = None  # .SUPPORTS-ASYNCHRONOUS-MODE-SWITCH
        self._assign_optional("mode_group_ref", mode_group_ref, ModeDeclarationGroupPrototypeRef)
        self._assign_optional("enhanced_mode_api", enhanced_mode_api, bool)
        self._assign_optional("supports_async", supports_async, bool)


class ClientComSpec(RequirePortComSpec):
    """
    Complex type AR:CLIENT-COM-SPEC
    Tag variants: 'CLIENT-COM-SPEC'
    """

    def __init__(self,
                 operation_ref: ClientServerOperationRef | None = None,
                 e2e_call_respone_timeout: float | int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None
                 ) -> None:
        super().__init__()
        # .CLIENT-INTENT not supported (Adaptive Platform)
        # .GETTER-REF not supported (Adaptive Platform)
        self.operation_ref: ClientServerOperationRef | None = None  # .OPERATION-REF
        self.e2e_call_respone_timeout: float | None = None  # .END-TO-END-CALL-RESPONSE-TIMEOUT
        # .SETTER-REF not supported (Adaptive Platform)
        # .TRANSFORMATION-COM-SPEC-PROPSS
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        # USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet supported under transformation_com_spec_props
        self._assign_optional("operation_ref", operation_ref, ClientServerOperationRef)
        self._assign_optional("e2e_call_respone_timeout", e2e_call_respone_timeout, float)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(props)
        else:
            raise TypeError("props must be of type EndToEndTransformationComSpecProps")


class PortPrototype(Identifiable):
    """
    Group AR:PORT-PROTOTYPE
    """
    # .CLIENT-SERVER-ANNOTATIONS not supported
    # .DELEGATED-PORT-ANNOTATION not supported
    # .IO-HW-ABSTRACTION-SERVER-ANNOTATIONS not supported
    # .MODE-PORT-ANNOTATIONS not supported
    # .NV-DATA-PORT-ANNOTATIONS not supported
    # .PARAMETER-PORT-ANNOTATIONS not supported
    # .PORT-PROTOTYPE-PROPS not supported
    # .SENDER-RECEIVER-ANNOTATIONS not supported
    # .TRIGGER-PORT-ANNOTATIONS not supported
    # .VARIATION-POINT not supported


class ProvidePortPrototype(PortPrototype):
    """
    Complex type AR:P-PORT-PROTOTYPE
    Tag variants: 'P-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.com_spec: list[ProvidePortComSpec] = []  # .PROVIDED-COM-SPECS
        self.port_interface_ref: PortInterfaceRef | None = None  # .PROVIDED-INTERFACE-TREF
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        if com_spec is not None:
            if isinstance(com_spec, ProvidePortComSpec):
                self.append_com_spec(com_spec)
            elif isinstance(com_spec, (list, tuple)):
                for com_spec_elem in com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("com_spec must be of a type derived from ProvidePortComSpec")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: ProvidePortComSpec) -> None:
        """
        Adds comspec to internal list of com-specs
        """
        if isinstance(com_spec, ProvidePortComSpec):
            self.com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of a type derived from ProvidePortComSpec")


class RequirePortPrototype(PortPrototype):
    """
    Complex type AR:R-PORT-PROTOTYPE
    Tag variants: 'R-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                 allow_unconnected: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.com_spec: list[RequirePortComSpec] = []  # .REQUIRED-COM-SPECS
        self.allow_unconnected: bool | None = None  # .MAY-BE-UNCONNECTED
        self.port_interface_ref: PortInterfaceRef | None = None  # .REQUIRED-INTERFACE-TREF
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        self._assign_optional("allow_unconnected", allow_unconnected, bool)
        if com_spec is not None:
            if isinstance(com_spec, RequirePortComSpec):
                self.append_com_spec(com_spec)
            elif isinstance(com_spec, (list, tuple)):
                for com_spec_elem in com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                msg = "com_spec: Needs be of a type derived from RequirePortComSpec."
                raise TypeError(msg + f" Got {str(type(com_spec))}")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: RequirePortComSpec) -> None:
        """
        Adds comspec to internal list of com-specs
        """
        if isinstance(com_spec, RequirePortComSpec):
            self.com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of type RequirePortComSpec")


class PRPortPrototype(PortPrototype):
    """
    Complex type AR:PR-PORT-PROTOTYPE
    Tag variants: 'PR-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE and AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 provided_com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                 required_com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.port_interface_ref: PortInterfaceRef | None = None
        self.provided_com_spec: list[ProvidePortComSpec] = []
        self.required_com_spec: list[RequirePortComSpec] = []
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        if provided_com_spec is not None:
            if isinstance(provided_com_spec, ProvidePortComSpec):
                self.append_com_spec(provided_com_spec)
            elif isinstance(required_com_spec, (list, tuple)):
                for com_spec_elem in provided_com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("provided_com_spec must be of a type derived from ProvidePortComSpec")
        if required_com_spec is not None:
            if isinstance(required_com_spec, RequirePortComSpec):
                self.append_com_spec(required_com_spec)
            elif isinstance(required_com_spec, (list, tuple)):
                for com_spec_elem in required_com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("required_com_spec must be of a type derived from RequirePortComSpec")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: ProvidePortComSpec | RequirePortComSpec) -> None:
        """
        Append com-spec to internal list(s) of com-specs
        """
        if isinstance(com_spec, ProvidePortComSpec):
            self.provided_com_spec.append(com_spec)
        elif isinstance(com_spec, RequirePortComSpec):
            self.required_com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of either type ProvidePortComSpec, RequirePortComSpec")


class SwComponentType(ARElement, Searchable):
    """
    Group AR:SW-COMPONENT-TYPE
    """

    def __init__(self,
                 name: str,
                 ports: PortPrototypeElement | list[PortPrototypeElement] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .SW-COMPONENT-DOCUMENTATIONS not supported
        # .CONSISTENCY-NEEDSS not supported
        self.ports: list[PortPrototypeElement] = []  # .PORTS
        # .PORT_GROUPS not yet supported
        # .SWC-MAPPING-CONSTRAINT-REFS not yet supported
        # .UNIT-GROUP-REFS not yet supported
        if ports is not None:
            if isinstance(ports, PortPrototype):
                self.append_port(ports)
            elif isinstance(ports, list):
                for port in ports:
                    self.append_port(port)
            else:
                msg_part_1 = "ports: Type must be ProvidePortPrototype, RequirePortPrototype, PRPortPrototype"
                msg_part_2 = " or a list of those types."
                raise TypeError(msg_part_1 + msg_part_2 + f" Got {str(type(ports))}")

    def append_port(self, port: PortPrototypeElement):
        """
        Adds port to internal list of ports
        """
        if isinstance(port, PortPrototype):
            port.parent = self
            self.ports.append(port)
        else:
            msg = "port type must be one of: ProvidePortPrototype, RequirePortPrototype, PRPortPrototype."
            raise TypeError(msg + f" Got {str(type(port))}")

    @property
    def provide_ports(self) -> Iterator[ProvidePortPrototype]:
        """
        P-PORTS
        """
        for port in self.ports:
            if isinstance(port, ProvidePortPrototype):
                yield port

    @property
    def require_ports(self) -> Iterator[RequirePortPrototype]:
        """
        R-PORTS
        """
        for port in self.ports:
            if isinstance(port, RequirePortPrototype):
                yield port

    @property
    def pr_ports(self) -> Iterator[PRPortPrototype]:
        """
        PR-PORTS
        """
        for port in self.ports:
            if isinstance(port, PRPortPrototype):
                yield port

    def find(self, ref: str) -> Identifiable | None:
        """
        Searches port names for a match in ref
        """
        parts = ref.partition('/')
        for elem in self.ports:
            if elem.name == parts[0]:
                return elem
        return None

    @convenience_function
    def create_p_port(self,
                      name: str,
                      port_interface: PortInterface | None = None,
                      com_spec: dict | list[tuple[str, dict]] | ProvidePortComSpec | list[ProvidePortComSpec] | None = None,  # noqa E501 pylint: disable=C0301
                      **kwargs) -> ProvidePortPrototype:
        """

        Creates a new provide-port and adds it to the internal list of ports
        """
        if com_spec is not None:
            if isinstance(com_spec, dict):
                com_spec = ProvidePortComSpec.make_from_port_interface(port_interface, **com_spec)
                assert com_spec is not None
            elif isinstance(com_spec, Iterable):
                processed = []
                unprocessed = {}
                for elem in com_spec:
                    if isinstance(elem, ProvidePortComSpec):
                        processed.append(elem)
                    elif isinstance(elem, tuple):
                        if not len(elem) == 2:
                            raise NotImplementedError("Com-spec element must be a 2-tuple containing [str, dict]. "
                                                      f"Got tuple with length {len(elem)}")
                        unprocessed[elem[0]] = elem[1]
                    else:
                        raise TypeError(f"Unsupported type in com-spec element: {str(type(elem))}")
                if len(unprocessed):
                    processed.extend(ProvidePortComSpec.make_from_port_interface(port_interface, **unprocessed))
                com_spec = processed
            else:
                com_spec = None  # Clear when not implemented
        port = ProvidePortPrototype(name, port_interface.ref(), com_spec, **kwargs)
        self.append_port(port)
        return port

    @convenience_function
    def create_provide_port(self,
                            name: str,
                            port_interface: PortInterface | None = None,
                            com_spec: dict | list[tuple[str, dict]] | ProvidePortComSpec | list[ProvidePortComSpec] | None = None,  # noqa E501 pylint: disable=C0301
                            **kwargs) -> ProvidePortPrototype:
        """

        Alias for create_p_port
        """
        return self.create_p_port(name, port_interface, com_spec, **kwargs)

    @convenience_function
    def create_r_port(self,
                      name: str,
                      port_interface: PortInterface,
                      com_spec: dict | list[dict] | RequirePortComSpec | list[RequirePortComSpec] | None = None,
                      allow_unconnected: bool | None = None,
                      **kwargs) -> RequirePortPrototype:
        """

        Creates a new require-port and adds it to the internal list of ports
        """
        if com_spec is not None:
            if isinstance(com_spec, dict):
                com_spec = RequirePortComSpec.make_from_port_interface(port_interface, **com_spec)
                assert com_spec is not None
            elif isinstance(com_spec, Iterable):
                processed = []
                unprocessed = {}
                for elem in com_spec:
                    if isinstance(elem, RequirePortComSpec):
                        processed.append(elem)
                    elif isinstance(elem, tuple):
                        if not len(elem) == 2:
                            raise NotImplementedError("Com-spec element must be a 2-tuple containing [str, dict]. "
                                                      f"Got tuple with length {len(elem)}")
                        unprocessed[elem[0]] = elem[1]
                    else:
                        raise TypeError(f"Unsupported type in com-spec element: {str(type(elem))}")
                if len(unprocessed):
                    processed.extend(RequirePortComSpec.make_from_port_interface(port_interface, **unprocessed))
                com_spec = processed
            else:
                com_spec = None  # Clear when not implemented
        port = RequirePortPrototype(name, port_interface.ref(), com_spec, allow_unconnected, **kwargs)
        self.append_port(port)
        return port

    @convenience_function
    def create_require_port(self,
                            name: str,
                            port_interface: PortInterface,
                            com_spec: dict | list[dict] | RequirePortComSpec | list[RequirePortComSpec] | None = None,
                            allow_unconnected: bool | None = None,
                            **kwargs) -> RequirePortPrototype:
        """

        Alias for create_r_port
        """
        return self.create_r_port(name, port_interface, com_spec, allow_unconnected, **kwargs)

    @convenience_function
    def create_pr_port(self,
                       name: str,
                       port_interface: PortInterface | None = None,
                       provided_com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                       required_com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                       **kwargs) -> PRPortPrototype:
        """

        Creates a new pr-port and adds it to the internal list of ports
        """
        if provided_com_spec is not None:
            if isinstance(provided_com_spec, dict):
                provided_com_spec = ProvidePortComSpec.make_from_port_interface(port_interface, **provided_com_spec)
                assert provided_com_spec is not None
        if required_com_spec is not None:
            if isinstance(required_com_spec, dict):
                required_com_spec = RequirePortComSpec.make_from_port_interface(port_interface, **required_com_spec)
                assert required_com_spec is not None
        port = PRPortPrototype(name, port_interface.ref(), provided_com_spec, required_com_spec, **kwargs)
        self.append_port(port)
        return port

    def find_r_port(self, port_name: str) -> RequirePortPrototype | PRPortPrototype | None:
        """
        Finds r-port by name
        """
        for port in self.ports:
            if isinstance(port, (RequirePortPrototype, PRPortPrototype)) and port.name == port_name:
                return port
        return None

    def find_p_port(self, port_name: str) -> ProvidePortPrototype | PRPortPrototype | None:
        """
        Finds p-port by name
        """
        for port in self.ports:
            if isinstance(port, (ProvidePortPrototype, PRPortPrototype)) and port.name == port_name:
                return port
        return None

    def get_data_element_in_port(self,
                                 port: RequirePortPrototype | ProvidePortPrototype,
                                 data_element_name: str | None = None,
                                 ) -> VariableDataPrototype | None:
        """
        Finds data element in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, SenderReceiverInterface):
            if not data_element_name:
                if not len(port_interface.data_elements) == 1:
                    msg = "data_element_name: Undefined value is not allowed when "\
                          "the port interface has more than one data element"
                    raise ValueError(msg)
                return port_interface.data_elements[0]
            else:
                for elem in port_interface.data_elements:
                    if elem.name == data_element_name:
                        return elem
        else:
            raise TypeError(f"Only SenderReceiverInterface is currently supported, got {str(type(port_interface))}")
        return None

    def get_operation_in_port(self,
                              port: PortPrototype,
                              operation_name: str
                              ) -> ClientServerOperation:
        """
        Finds client-server operation in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, ClientServerInterface):
            if not operation_name:
                if not len(port_interface.operations) == 1:
                    msg = "operation_name: Undefined value is not allowed when "\
                          "the port interface has more than one operation"
                    raise ValueError(msg)
                return port_interface.operations[0]
            else:
                for operation in port_interface.operations:
                    if operation.name == operation_name:
                        return operation
        else:
            raise TypeError(f"port: '{port.name}' doesn't reference port with ClientServerInterface")
        return None

    def get_mode_declaration_group_in_port(self,
                                           port: PortPrototype,
                                           ) -> ModeDeclarationGroupPrototype | None:
        """
        Finds mode declaration group in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, ModeSwitchInterface):
            return port_interface.mode_group
        else:
            raise TypeError(f"port: Expected a port referencing a ModeSwitchInterface, got {str(type(port_interface))}")
        return None

    def get_trigger_in_port(self,
                            port: RequirePortPrototype | ProvidePortPrototype,
                            trigger_name: str | None = None,
                            ) -> Trigger | None:
        """
        Finds specific trigger in given port
        """
        workspace = port.root_collection()
        assert workspace is not None
        port_interface = workspace.find(port.port_interface_ref)
        if port_interface is None:
            raise ar_except.InvalidReferenceError(str(port.port_interface_ref))
        if isinstance(port_interface, TriggerInterface):
            if not trigger_name:
                if not len(port_interface.triggers) == 1:
                    msg = "trigger_name: Undefined value is not allowed when "\
                          "the port interface has more than one trigger"
                    raise ValueError(msg)
                return port_interface.triggers[0]
            else:
                for trigger in port_interface.triggers:
                    if trigger.name == trigger_name:
                        return trigger
        else:
            raise TypeError(f"port: Expected a port referencing a TriggerInterface, got {str(type(port_interface))}")
        return None


class AtomicSoftwareComponentType(SwComponentType):
    """
    Group AR:ATOMIC-SW-COMPONENT-TYPE
    """

    def __init__(self,
                 name: str,
                 internal_behavior: Union["SwcInternalBehavior", None] = None,
                 symbol_props: SymbolProps | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self._internal_behavior: SwcInternalBehavior | None = None
        self.symbol_props: SymbolProps | None = None  # AR:SYMBOL-PROPS
        if internal_behavior is not None:
            self._assign_optional_strict("_internal_behavior", internal_behavior, _get_swc_internal_behavior_class())
        self._assign_optional_strict("symbol_props", symbol_props, SymbolProps)

    @property
    def internal_behavior(self) -> Union["SwcInternalBehavior", None]:
        """
        Internal behavior getter
        """
        return self._internal_behavior

    @internal_behavior.setter
    def internal_behavior(self, value: Union["SwcInternalBehavior", None]):
        """
        Internal behavior setter
        """
        self._internal_behavior = value
        if value is not None:
            value.parent = self

    @convenience_function
    def create_internal_behavior(self, name: str = None, **kwargs) -> "SwcInternalBehavior":
        """
        Creates an empty internal behavior object and adds it to the component.
        If the name argument is left as None, a default name will be created based on the name of
        the software component
        """
        if name is None:
            name = self.name + "_InternalBehavior"
        SwcInternalBehavior = _get_swc_internal_behavior_class()
        self.internal_behavior = SwcInternalBehavior(name, **kwargs)
        self.internal_behavior.parent = self
        return self.internal_behavior


class ApplicationSoftwareComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:APPLICATION-SW-COMPONENT-TYPE
    Tag variants: 'APPLICATION-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE)


class ComplexDeviceDriverSwComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE
    Tag variants: 'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.COMPLEX_DEVICE_DRIVER_SW_COMPONENT_TYPE)


class EcuAbstractionSwComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:ECU-ABSTRACTION-SW-COMPONENT-TYPE
    Tag variants: 'ECU-ABSTRACTION-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.ECU_ABSTRACTION_SW_COMPONENT_TYPE)


class NvBlockSwComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:NV-BLOCK-SW-COMPONENT-TYPE
    Tag variants: 'NV-BLOCK-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.NV_BLOCK_SW_COMPONENT_TYPE)


class SensorActuatorSwComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:SENSOR-ACTUATOR-SW-COMPONENT-TYPE
    Tag variants: 'SENSOR-ACTUATOR-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.SENSOR_ACTUATOR_SW_COMPONENT_TYPE)


class ServiceSwComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:SERVICE-SW-COMPONENT-TYPE
    Tag variants: 'SERVICE-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.SERVICE_SW_COMPONENT_TYPE)


class ServiceProxySwComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:SERVICE-PROXY-SW-COMPONENT-TYPE
    Tag variants: 'SERVICE-PROXY-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.SERVICE_PROXY_SW_COMPONENT_TYPE)


class SwComponentPrototype(Identifiable):
    """
    Complex type AR:SW-COMPONENT-PROTOTYPE
    Tag variants: 'SW-COMPONENT-PROTOTYPE'
    """

    def __init__(self,
                 name: str,
                 type_ref: SwComponentTypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: SwComponentTypeRef | None = None
        self._assign_optional_strict("type_ref", type_ref, SwComponentTypeRef)

    def ref(self) -> SwComponentPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwComponentPrototypeRef(ref_str)


class PortInCompositionTypeInstanceRef(ARObject):
    """
    Complex type AR:P-PORT-IN-COMPOSITION-INSTANCE-REF
    Merge of Complex Types AR:P-PORT-IN-COMPOSITION-INSTANCE-REF and AR:R-PORT-IN-COMPOSITION-INSTANCE-REF
    Tag variants: 'P-PORT-IN-COMPOSITION-INSTANCE-REF' | 'PROVIDER-IREF' |
                  'R-PORT-IN-COMPOSITION-INSTANCE-REF' | 'REQUESTER-IREF'
    """

    def __init__(self,
                 component_ref: SwComponentPrototypeRef | None = None,
                 port_ref: PortPrototypeRef | None = None,
                 ) -> None:
        super().__init__()
        self.component_ref: SwComponentPrototypeRef | None = None  # .CONTEXT-COMPONENT-REF
        self.port_ref: PortPrototypeRef | None = None  # .TARGET-P-PORT-REF or .TARGET-R-PORT-REF
        self._assign_optional_strict("component_ref", component_ref, SwComponentPrototypeRef)
        self._assign_optional_strict("port_ref", port_ref, PortPrototypeRef)


class SwConnector(Identifiable):
    """
    Group AR:SW-CONNECTOR
    """

    def __init__(self,
                 name: str,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MAPPING-REF not yet supported
        # .VARIATION-POINT not supported


class AssemblySwConnector(SwConnector):
    """
    Complex type AR:ASSEMBLY-SW-CONNECTOR
    Tag variants: 'ASSEMBLY-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 provide_port: PortInCompositionTypeInstanceRef | None = None,
                 require_port: PortInCompositionTypeInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.provide_port: PortInCompositionTypeInstanceRef | None = None  # .PROVIDER-IREF
        self.require_port: PortInCompositionTypeInstanceRef | None = None  # .REQUESTER-IREF
        self._assign_optional_strict("provide_port", provide_port, PortInCompositionTypeInstanceRef)
        self._assign_optional_strict("require_port", require_port, PortInCompositionTypeInstanceRef)


class DelegationSwConnector(SwConnector):
    """
    Complex type AR:DELEGATION-SW-CONNECTOR
    Tag variants: 'DELEGATION-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 inner_port: PortInCompositionTypeInstanceRef | None = None,
                 outer_port: PortPrototypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.inner_port: PortInCompositionTypeInstanceRef | None = None  # .INNER-PORT-IREF
        self.outer_port: PortPrototypeRef | None = None  # .OUTER-PORT-REF"
        self._assign_optional_strict("inner_port", inner_port, PortInCompositionTypeInstanceRef)
        self._assign_optional_strict("outer_port", outer_port, PortPrototypeRef)

    @property
    def xml_tag(self) -> str | None:
        """
        Returns a suitable XML-tag for inner_port_ref based on port reference type.
        Raises exception is port reference isn't set or if port-reference contains invalid value
        """
        if self.inner_port.port_ref is not None:
            if self.inner_port.port_ref.is_provide_port_ref:
                return "P-PORT-IN-COMPOSITION-INSTANCE-REF"
            if self.inner_port.port_ref.is_require_port_ref:
                return "R-PORT-IN-COMPOSITION-INSTANCE-REF"
        return None


class PassThroughSwConnector(SwConnector):
    """
    Complex type AR:PASS-THROUGH-SW-CONNECTOR
    Tag variants: 'PASS-THROUGH-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 provide_port: PortPrototypeRef | None = None,
                 require_port: PortPrototypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.provide_port: PortPrototypeRef | None = None  # .PROVIDED-OUTER-PORT-REF
        self.require_port: PortPrototypeRef | None = None  # .REQUIRED-OUTER-PORT-REF
        # .SERVICE-INTERFACE-ELEMENT-MAPPING-REFS not yet supported
        self._assign_optional_strict("provide_port", provide_port, PortPrototypeRef)
        self._assign_optional_strict("require_port", require_port, PortPrototypeRef)


class CompositionSwComponentType(SwComponentType, Searchable):
    """
    Complex type AR:COMPOSITION-SW-COMPONENT-TYPE
    Tag variants: 'COMPOSITION-SW-COMPONENT-TYPE'
    """

    def __init__(self,
                 name: str,
                 components: SwComponentPrototype | list[SwComponentPrototype] | None = None,
                 connectors: SwConnectorElement | list[SwConnectorElement] = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.components: list[SwComponentPrototype] = []  # .COMPONENTS
        self.connectors: list[SwConnectorElement] = []  # .CONNECTORS
        # .CONSTANT-VALUE-MAPPING-REFS not yet supported
        # .DATA-TYPE-MAPPING-REFS not yet supported
        # .INSTANTIATION-RTE-EVENT-PROPSS not yet supported
        if components is not None:
            if isinstance(components, SwComponentPrototype):
                self.append_component(components)
            elif isinstance(components, list):
                for component in components:
                    self.append_component(component)
            else:
                raise TypeError(f"components: Invalid type '{str(type(components))}'")
        if connectors is not None:
            if isinstance(connectors, (AssemblySwConnector, DelegationSwConnector, PassThroughSwConnector)):
                self.append_connector(connectors)
            elif isinstance(connectors, list):
                for connector in connectors:
                    self.append_connector(connector)
            else:
                raise TypeError(f"components: Invalid type '{str(type(connectors))}'")

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.COMPOSITION_SW_COMPONENT_TYPE)

    def append_component(self, component: SwComponentPrototype) -> None:
        """
        Appends components prototype to internal list
        """
        if isinstance(component, SwComponentPrototype):
            component.parent = self
            self.components.append(component)
        else:
            raise TypeError(f"component: Invalid type {(str(type(component)))}")

    def append_connector(self, connector: SwConnectorElement) -> None:
        """
        Appends components prototype to internal list
        """
        if isinstance(connector, (AssemblySwConnector, DelegationSwConnector, PassThroughSwConnector)):
            connector.parent = self
            self.connectors.append(connector)
        else:
            raise TypeError(f"connector: Invalid type {(str(type(connector)))}")

    def find(self, ref: str) -> Identifiable | None:
        """
        Searches components and connectors for a match in ref
        """
        parts = ref.partition('/')
        for elem in self.components:
            if elem.name == parts[0]:
                return elem
        for elem in self.connectors:
            if elem.name == parts[0]:
                return elem
        return super().find(ref)

    @convenience_function
    def create_component_prototype(self,
                                   component_type: SwComponentType,
                                   name: str = None,
                                   **kwargs) -> SwComponentPrototype:
        """

        Creates a new SwComponentPrototype object from the source SwComponentType and adds it
        to the internal list of components.
        By default the created SwComponentPrototype will have the same name as the source
        SwComponentType. The optional name argument can be used to give it a different name.
        """
        if name is None:
            name = component_type.name
        component_prototype = SwComponentPrototype(name, component_type.ref(), **kwargs)
        self.append_component(component_prototype)
        return component_prototype

    @convenience_function
    def create_connector(self,
                         port_ref1: str,
                         port_ref2: str,
                         workspace: Searchable) -> None:
        """

        Creates a connector between two ports in the composition
        port_ref1 and port_ref2 can be of any of these formats:
        * 'component_name/port_name' - references a port of an inner component
        * 'port_name' - references a port in the composition itself

        Depending on the combination of ports this function automatically determines
        the type of connector to create which can be one of:
        * AssemblySwConnector
        * DelegationSwConnector
        * PassThroughSwConnector
        """
        assert workspace is not None
        port1, component1 = self._analyze_port_ref(workspace, port_ref1)
        port2, component2 = self._analyze_port_ref(workspace, port_ref2)

        if component1 is None and component2 is None:
            return self._create_pass_through_connector(port1, port2)
        elif component1 is None:
            return self._create_delegation_connector(component2, port2, port1)
        elif component2 is None:
            return self._create_delegation_connector(component1, port1, port2)
        else:
            requester_component: SwComponentPrototype = None
            provider_component: SwComponentPrototype = None
            provide_port: PortPrototype = None
            require_port: PortPrototype = None
            if isinstance(port1, RequirePortPrototype) and isinstance(port2, ProvidePortPrototype):
                requester_component, provider_component = component1, component2
                require_port, provide_port = port1, port2
            elif isinstance(port1, ProvidePortPrototype) and isinstance(port2, RequirePortPrototype):
                requester_component, provider_component = component2, component1
                require_port, provide_port = port2, port1
            elif isinstance(port1, RequirePortPrototype) and isinstance(port2, RequirePortPrototype):
                raise ValueError('cannot create assembly connector between two require-ports')
            else:
                raise ValueError('cannot create assembly connector between two provide-ports')
            return self._create_assembly_connector(provider_component, provide_port,
                                                   requester_component, require_port)

    def _analyze_port_ref(self,
                          workspace: Searchable,
                          port_ref: str) -> tuple[PortPrototype, Union[SwComponentPrototype, None]]:
        """
        Analyze port reference string and attempts to determine what component
        and port are referenced.
        """
        port: PortPrototype | None = None
        port_name: str | None = None
        parts = split_ref(port_ref)
        if len(parts) > 1:
            if len(parts) == 2:  # Format is 'component_name/port_name'?
                port_name = parts[1]
                for elem in self.components:
                    if elem.name == parts[0]:
                        component = workspace.find(str(elem.type_ref))
                        if component is None:
                            raise ValueError(f"Invalid reference: {elem.type_ref}")
                        if not isinstance(component, SwComponentType):
                            msg = f"Reference is not a valid SwComponentType: {elem.type_ref}"
                            raise ValueError(msg)
                        port = component.find(port_name)
                        if (port is None) or (not isinstance(port, PortPrototype)):
                            msg = f"Component '{component.name}' does not seem to have a port with name '{port_name}'"
                            raise ValueError(msg)
                        return port, elem
            else:
                raise ValueError(f"Invalid format: '{port_ref}'")
        else:  # Format is 'port_name'
            # Leaving component as None here is a reminder to the caller to create a delegation or a
            # pass-through connector
            port_name = parts[0]
            port = self.find(port_name)
            if (port is None) or (not isinstance(port, PortPrototype)):
                msg = f"Component '{self.name}' does not seem to have a port with name '{port_name}'"
                raise ValueError(msg)
        return port, None

    def _create_assembly_connector(self,
                                   provider_component: SwComponentPrototype,
                                   provide_port: PortPrototype,
                                   requester_component: SwComponentPrototype,
                                   require_port: PortPrototype) -> AssemblySwConnector:
        """
        Internal helper function for creating assembly connector
        """
        connector_name = '_'.join([provider_component.name,
                                   provide_port.name,
                                   requester_component.name,
                                   require_port.name])
        provider_iref = PortInCompositionTypeInstanceRef(provider_component.ref(), provide_port.ref())
        requester_iref = PortInCompositionTypeInstanceRef(requester_component.ref(), require_port.ref())
        connector = AssemblySwConnector(connector_name, provider_iref, requester_iref)
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.append_connector(connector)
        return connector

    def _create_delegation_connector(self,
                                     inner_component: SwComponentPrototype,
                                     inner_port: PortPrototype,
                                     outer_port: PortPrototype) -> DelegationSwConnector:
        if isinstance(outer_port, ProvidePortPrototype):
            connector_name = '_'.join([inner_component.name, inner_port.name, outer_port.name])
        else:
            connector_name = '_'.join([outer_port.name, inner_component.name, inner_port.name])
        inner_port_iref = PortInCompositionTypeInstanceRef(inner_component.ref(), inner_port.ref())
        connector = DelegationSwConnector(connector_name, inner_port_iref, outer_port.ref())
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.connectors.append(connector)
        return connector

    def _create_pass_through_connector(self,
                                       provide_port: ProvidePortPrototype,
                                       require_port: RequirePortPrototype) -> PassThroughSwConnector:
        connector_name = '_'.join([provide_port.name, require_port.name])
        connector = PassThroughSwConnector(connector_name, provide_port.ref(), require_port.ref())
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.connectors.append(connector)
        return connector


class ModeGroupInAtomicSwcInstanceRef(ARObject):
    """
    Group AR:MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
    Abstract base class
    """


class POperationInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:P-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'OPERATION-IREF'
    """

    def __init__(self,
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_provided_operation: ClientServerOperationRef | str | None = None,
                 ) -> None:
        # .CONTEXT-P-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractProvidedPortPrototypeRef | None = None
        # .TARGET-PROVIDED-OPERATION-REF
        self.target_provided_operation: ClientServerOperationRef | None = None
        self._assign_optional("context_port", context_port, AbstractProvidedPortPrototypeRef)
        self._assign_optional("target_provided_operation", target_provided_operation, ClientServerOperationRef)


class PModeGroupInAtomicSwcInstanceRef(ModeGroupInAtomicSwcInstanceRef):
    """
    Complex type AR:P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'MODE-GROUP-IREF' | 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF' |
                  'SWC-MODE-GROUP-IREF'
    """

    def __init__(self,
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_mode_group: ModeDeclarationGroupPrototypeRef | str | None = None,
                 ) -> None:
        # .CONTEXT-P-PORT-REF
        self.context_port: AbstractProvidedPortPrototypeRef | None = None
        # .TARGET-MODE-GROUP-REF
        self.target_mode_group: ModeDeclarationGroupPrototypeRef | None = None

        self._assign_optional("context_port", context_port, AbstractProvidedPortPrototypeRef)
        self._assign_optional("target_mode_group",
                              target_mode_group,
                              ModeDeclarationGroupPrototypeRef)


class PTriggerInAtomicSwcTypeInstanceRef(ARObject):
    """
    Complex type AR:P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF' | 'SWC-TRIGGER-IREF' |
                  'TRIGGER-IREF'
    """

    def __init__(self,
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_trigger: TriggerRef | str | None = None,
                 ) -> None:
        # .CONTEXT-P-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractProvidedPortPrototypeRef | None = None
        # .TARGET-TRIGGER-REF
        self.target_trigger: TriggerRef | None = None

        self._assign_optional("context_port", context_port, AbstractProvidedPortPrototypeRef)
        self._assign_optional("target_trigger", target_trigger, TriggerRef)


class ROperationInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'OPERATION-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_required_operation: ClientServerOperationRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-REQUIRED-OPERATION-REF
        self.target_required_operation: ClientServerOperationRef | None = None
        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_required_operation", target_required_operation, ClientServerOperationRef)


class RModeInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-MODE-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'DISABLED-MODE-IREF' | 'MODE-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | None = None,
                 target_mode_declaration: ModeDeclarationRef | None = None,
                 ) -> None:
        # .CONTEXT-PORT-REF
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | None = None
        # .TARGET-MODE-DECLARATION-REF
        self.target_mode_declaration: ModeDeclarationRef | None = None
        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("context_mode_declaration_group_prototype",
                              context_mode_declaration_group_prototype,
                              ModeDeclarationGroupPrototypeRef)
        self._assign_optional("target_mode_declaration", target_mode_declaration, ModeDeclarationRef)


class RModeGroupInAtomicSwcInstanceRef(ModeGroupInAtomicSwcInstanceRef):
    """
    Complex type AR:R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_mode_group: ModeDeclarationGroupPrototypeRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-MODE-GROUP-REF
        self.target_mode_group: ModeDeclarationGroupPrototypeRef | None = None

        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_mode_group", target_mode_group, ModeDeclarationGroupPrototypeRef)


class RVariableInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-VARIABLE-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'DATA-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_data_element: VariableDataPrototypeRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-DATA-ELEMENT-REF
        self.target_data_element: VariableDataPrototypeRef | None = None

        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_data_element", target_data_element, VariableDataPrototypeRef)


class RTriggerInAtomicSwcInstanceRef(ARObject):
    """
    Complex type AR:R-TRIGGER-IN-ATOMIC-SWC-INSTANCE-REF
    Tag variants: 'REQUIRED-TRIGGER-IREF' | 'TRIGGER-IREF'
    """

    def __init__(self,
                 context_port: AbstractRequiredPortPrototypeRef | None = None,
                 target_trigger: TriggerRef | str | None = None,
                 ) -> None:
        # .CONTEXT-R-PORT-REF (Keep name consistent in similar classes)
        self.context_port: AbstractRequiredPortPrototypeRef | None = None
        # .TARGET-TRIGGER-REF
        self.target_trigger: TriggerRef | None = None

        self._assign_optional("context_port", context_port, AbstractRequiredPortPrototypeRef)
        self._assign_optional("target_trigger", target_trigger, TriggerRef)


__all__ = [
    "PortPrototypeElement",
    "SwConnectorElement",
    "EndToEndTransformationComSpecPropsArgTypes",
    "ModeSwitchedAckRequest",
    "TransmissionAcknowledgementRequest",
    "TransmissionComSpecProps",
    "ProvidePortComSpec",
    "SenderComSpec",
    "ModeSwitchSenderComSpec",
    "QueuedSenderComSpec",
    "NonqueuedSenderComSpec",
    "NvProvideComSpec",
    "ParameterProvideComSpec",
    "ServerComSpec",
    "ReceptionComSpecProps",
    "RequirePortComSpec",
    "ReceiverComSpec",
    "QueuedReceiverComSpec",
    "NonqueuedReceiverComSpec",
    "NvRequireComSpec",
    "ParameterRequireComSpec",
    "ModeSwitchReceiverComSpec",
    "ClientComSpec",
    "PortPrototype",
    "ProvidePortPrototype",
    "RequirePortPrototype",
    "PRPortPrototype",
    "SwComponentType",
    "AtomicSoftwareComponentType",
    "ApplicationSoftwareComponentType",
    "ComplexDeviceDriverSwComponentType",
    "EcuAbstractionSwComponentType",
    "NvBlockSwComponentType",
    "SensorActuatorSwComponentType",
    "ServiceSwComponentType",
    "ServiceProxySwComponentType",
    "SwComponentPrototype",
    "PortInCompositionTypeInstanceRef",
    "SwConnector",
    "AssemblySwConnector",
    "DelegationSwConnector",
    "PassThroughSwConnector",
    "CompositionSwComponentType",
    "ModeGroupInAtomicSwcInstanceRef",
    "POperationInAtomicSwcInstanceRef",
    "PModeGroupInAtomicSwcInstanceRef",
    "PTriggerInAtomicSwcTypeInstanceRef",
    "ROperationInAtomicSwcInstanceRef",
    "RModeInAtomicSwcInstanceRef",
    "RModeGroupInAtomicSwcInstanceRef",
    "RVariableInAtomicSwcInstanceRef",
    "RTriggerInAtomicSwcInstanceRef",
]
