"""Internal behavior elements."""

from __future__ import annotations

import builtins
from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Union

from autosar.base import split_ref_strict
from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import (
    Identifiable,
    Referrable,
    make_unique_name_in_list,
)
from autosar.xml.elements.common import Code, Implementation, Trigger
from autosar.xml.elements.constant import ValueSpecification, ValueSpecificationElement
from autosar.xml.elements.data_type import (
    ImplementationProps,
    ParameterDataPrototype,
    SwDataDefProps,
    SwDataDefPropsConditional,
    VariableDataPrototype,
)
from autosar.xml.elements.mode_declaration import (
    ModeDeclaration,
    ModeDeclarationGroup,
    ModeDeclarationGroupPrototype,
)
from autosar.xml.elements.package import BehaviorSettings, PackageCollection
from autosar.xml.elements.port_interface import (
    ClientServerInterface,
    ModeSwitchInterface,
    NvDataInterface,
    ParameterInterface,
    PortInterface,
    SenderReceiverInterface,
    TriggerInterface,
)
from autosar.xml.elements.service_dependency import (
    RoleBasedDataAssignment,
    RoleBasedPortAssignment,
    SwcServiceDependency,
)
from autosar.xml.elements.service_needs import ServiceNeeds
from autosar.xml.elements.software_component import (
    AtomicSoftwareComponentType,
    ModeGroupInAtomicSwcInstanceRef,
    PModeGroupInAtomicSwcInstanceRef,
    POperationInAtomicSwcInstanceRef,
    PRPortPrototype,
    PTriggerInAtomicSwcTypeInstanceRef,
    PortPrototype,
    PortPrototypeElement,
    ProvidePortPrototype,
    RModeGroupInAtomicSwcInstanceRef,
    RModeInAtomicSwcInstanceRef,
    ROperationInAtomicSwcInstanceRef,
    RTriggerInAtomicSwcInstanceRef,
    RVariableInAtomicSwcInstanceRef,
    RequirePortPrototype,
    SwComponentType,
)
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except
from autosar.xml.reference import (
    AbstractImplementationDataTypeElementRef,
    AbstractProvidedPortPrototypeRef,
    AbstractRequiredPortPrototypeRef,
    ApplicationCompositeElementDataPrototypeRef,
    AsynchronousServerCallPointRef,
    AsynchronousServerCallResultPointRef,
    AutosarDataTypeRef,
    ClientServerOperationRef,
    ConstantSpecificationMappingSetRef,
    DataPrototypeRef,
    DataTypeMappingSetRef,
    ExclusiveAreaNestingOrderRef,
    ExclusiveAreaRef,
    ImplementationDataTypeRef,
    InternalTriggeringPointRef,
    ModeDeclarationGroupPrototypeRef,
    ModeDeclarationGroupRef,
    ModeDeclarationRef,
    ModeSwitchPointRef,
    PerInstanceMemoryRef,
    PortGroupRef,
    PortPrototypeRef,
    RteEventRef,
    RunnableEntityRef,
    SwAddrMethodRef,
    SwcImplementationRef,
    SwcInternalBehaviorRef,
    TriggerRef,
    VariableAccessRef,
    VariableDataPrototypeRef,
)


class ArVariableInImplementationDataInstanceRef(ARObject):
    """
    Complex type AR:AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
    Tag variants: 'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE' | 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
    """

    ContextDataPrototypeArgType = Union[AbstractImplementationDataTypeElementRef,
                                        list[AbstractImplementationDataTypeElementRef]]

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | None = None,
                 root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None,
                 context_data_prototype_refs: ContextDataPrototypeArgType | None = None,
                 target_data_prototype_ref: AbstractImplementationDataTypeElementRef | None = None
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROOT-VARIABLE-DATA-PROTOTYPE-REF
        self.root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REFS
        self.context_data_prototype_refs: list[AbstractImplementationDataTypeElementRef] = []
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype_ref: AbstractImplementationDataTypeElementRef | None = None

        self._assign_optional_strict("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional_strict("root_variable_data_prototype_ref",
                                     root_variable_data_prototype_ref,
                                     VariableDataPrototypeRef)
        self._assign_optional_strict("target_data_prototype_ref",
                                     target_data_prototype_ref,
                                     AbstractImplementationDataTypeElementRef)
        if context_data_prototype_refs is not None:
            if isinstance(context_data_prototype_refs, AbstractImplementationDataTypeElementRef):
                self.append_context_data_protype_ref(context_data_prototype_refs)
            elif isinstance(context_data_prototype_refs, list):
                for context_data_prototype_ref in context_data_prototype_refs:
                    self.append_context_data_protype_ref(context_data_prototype_ref)

    def append_context_data_protype_ref(self, context_data_prototype_ref: AbstractImplementationDataTypeElementRef):
        """
        Appends datatype reference to internal list of context data type references
        """
        if isinstance(context_data_prototype_ref, AbstractImplementationDataTypeElementRef):
            self.context_data_prototype_refs.append(context_data_prototype_ref)
        else:
            raise TypeError("context_data_prototype_ref must be of type AbstractImplementationDataTypeElementRef")


class VariableInAtomicSWCTypeInstanceRef(ARObject):
    """
    Complex type AR:VARIABLE-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'AUTOSAR-VARIABLE-IREF'
    """

    ContextDataPrototypeArgType = Union[ApplicationCompositeElementDataPrototypeRef,
                                        list[ApplicationCompositeElementDataPrototypeRef]]

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | None = None,
                 root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None,
                 context_data_prototype_refs: ContextDataPrototypeArgType | None = None,
                 target_data_prototype_ref: DataPrototypeRef | None = None,
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROOT-VARIABLE-DATA-PROTOTYPE-REF
        self.root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REF
        self.context_data_prototype_refs: list[ApplicationCompositeElementDataPrototypeRef] = []
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype_ref: DataPrototypeRef | None = None

        self._assign_optional("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional("root_variable_data_prototype_ref",
                              root_variable_data_prototype_ref, VariableDataPrototypeRef)
        self._assign_optional("target_data_prototype_ref", target_data_prototype_ref, DataPrototypeRef)
        if context_data_prototype_refs is not None:
            if isinstance(context_data_prototype_refs, ApplicationCompositeElementDataPrototypeRef):
                self.append_context_data_protype_ref(context_data_prototype_refs)
            elif isinstance(context_data_prototype_refs, list):
                for context_data_prototype_ref in context_data_prototype_refs:
                    self.append_context_data_protype_ref(context_data_prototype_ref)

    def append_context_data_protype_ref(self, context_data_prototype_ref: ApplicationCompositeElementDataPrototypeRef):
        """
        Appends datatype reference to internal list of context data type references
        """
        if isinstance(context_data_prototype_ref, ApplicationCompositeElementDataPrototypeRef):
            self.context_data_prototype_refs.append(context_data_prototype_ref)
        else:
            raise TypeError("context_data_prototype_ref must be of type AbstractImplementationDataTypeElementRef")


class AutosarVariableRef(ARObject):
    """
    Complex type AR:AUTOSAR-VARIABLE-REF
    Tag variants: 'ACCESSED-VARIABLE' | 'AUTOSAR-VARIABLE' | 'NV-RAM-BLOCK-ELEMENT' |
                  'READ-NV-DATA' | 'USED-DATA-ELEMENT' | 'VARIABLE-INSTANCE' |
                  'WRITTEN-NV-DATA' | 'WRITTEN-READ-NV-DATA'
    """

    def __init__(self,
                 ar_variable_in_impl_datatype: ArVariableInImplementationDataInstanceRef | None = None,
                 ar_variable_iref: VariableInAtomicSWCTypeInstanceRef | None = None,
                 local_variable_ref: VariableDataPrototypeRef | None = None
                 ) -> None:
        super().__init__()
        # .AUTOSAR-VARIABLE-IN-IMPL-DATATYPE
        self.ar_variable_in_impl_datatype: ArVariableInImplementationDataInstanceRef | None = None
        # .AUTOSAR-VARIABLE-IREF
        self.ar_variable_iref: VariableInAtomicSWCTypeInstanceRef | None = None
        # .LOCAL-VARIABLE-REF
        self.local_variable_ref: VariableDataPrototypeRef | None = None
        self._assign_optional_strict("ar_variable_in_impl_datatype",
                                     ar_variable_in_impl_datatype,
                                     ArVariableInImplementationDataInstanceRef)
        self._assign_optional_strict("ar_variable_iref",
                                     ar_variable_iref,
                                     VariableInAtomicSWCTypeInstanceRef)
        self._assign_optional_strict("local_variable_ref",
                                     local_variable_ref,
                                     VariableDataPrototypeRef)


class VariableAccess(Identifiable):
    """
    Complex type AR:VARIABLE-ACCESS
    Tag variants: 'REPLACE-WITH' | 'VARIABLE-ACCESS'
    """

    def __init__(self,
                 name: str,
                 accessed_variable: AutosarVariableRef | None = None,
                 scope: ar_enum.VariableAccessScope | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ACCESSED-VARIABLE
        self.accessed_variable: AutosarVariableRef | None = None
        # .SCOPE
        self.scope: ar_enum.VariableAccessScope | None = None

        # .VARIATION-POINT not supported
        self._assign_optional_strict("accessed_variable", accessed_variable, AutosarVariableRef)
        self._assign_optional("scope", scope, ar_enum.VariableAccessScope)

    @convenience_function
    @classmethod
    def make_from_port(cls,
                       name: str,
                       port_prototype_ref: PortPrototypeRef,
                       target_data_prototype_ref: DataPrototypeRef,
                       **kwargs) -> "VariableAccess":
        """

        Simplified creation method for use with VariableInAtomicSWCTypeInstanceRef
        """
        variable_iref = VariableInAtomicSWCTypeInstanceRef(port_prototype_ref=port_prototype_ref,
                                                           target_data_prototype_ref=target_data_prototype_ref)
        autosar_variable_ref = AutosarVariableRef(ar_variable_iref=variable_iref)
        return cls(name, autosar_variable_ref, **kwargs)

    @convenience_function
    @classmethod
    def make_from_port_with_args(cls,
                                 name: str,
                                 port_prototype_ref: PortPrototypeRef,
                                 target_data_prototype_ref: DataPrototypeRef,
                                 args: dict[str, Any] | None) -> "VariableAccess":
        """

        Same as make_from_port but allows extra arguments to be given as an optional dictionary
        """
        if args is not None:
            return cls.make_from_port(name, port_prototype_ref, target_data_prototype_ref, **args)
        else:
            return cls.make_from_port(name, port_prototype_ref, target_data_prototype_ref)

    def ref(self) -> VariableAccessRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return VariableAccessRef(ref_str)


class SwcImplementation(Implementation):
    """
    Complex type AR:SWC-IMPLEMENTATION
    Tag variants: 'SWC-IMPLEMENTATION'
    """

    def __init__(self,
                 name: str,
                 behavior_ref: SwcInternalBehaviorRef | None = None,
                 code_descriptors: Code | list[Code] | None = None,
                 required_rte_vendor: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, code_descriptors, **kwargs)
        self.behavior_ref: SwcInternalBehaviorRef | None = None
        # .PER-INSTANCE-MEMORY-SIZES not yet supported
        self.required_rte_vendor: str | None = None
        self._assign_optional("behavior_ref", behavior_ref, SwcInternalBehaviorRef)
        self._assign_optional_strict("required_rte_vendor", required_rte_vendor, str)

    def ref(self) -> SwcImplementationRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwcImplementationRef(ref_str)


class ExecutableEntityActivationReason(ImplementationProps):
    """
    Complex type AR:EXECUTABLE-ENTITY-ACTIVATION-REASON
    Tag variants: 'EXECUTABLE-ENTITY-ACTIVATION-REASON'
    """

    def __init__(self,
                 name: str,
                 bit_position: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.bit_position: int | None = None
        self._assign_optional_positive_int("bit_position", bit_position)


class ExclusiveAreaRefConditional(ARObject):
    """
    Complex type AR:EXCLUSIVE-AREA-REF-CONDITIONAL
    Tag variants: 'EXCLUSIVE-AREA-REF-CONDITIONAL'
    """

    def __init__(self,
                 exclusive_area: ExclusiveAreaRef | str | None = None) -> None:
        self.exclusive_area: ExclusiveAreaRef | None = None  # .EXCLUSIVE-AREA-REF
        self._assign_optional("exclusive_area", exclusive_area, ExclusiveAreaRef)


ActivationReasonArgumentType = ExecutableEntityActivationReason | list[ExecutableEntityActivationReason] | None
CanEnterLeaveArgumentType = Union[ExclusiveAreaRefConditional,
                                  list[ExclusiveAreaRefConditional],
                                  ExclusiveAreaRef,
                                  list[ExclusiveAreaRef],
                                  str,
                                  list[str],
                                  None]

ExclusiveAreaNestingOrderArgumentType = ExclusiveAreaNestingOrderRef | list[ExclusiveAreaNestingOrderRef] | None
RunsInsidesArgumentType = Union[ExclusiveAreaRefConditional,
                                list[ExclusiveAreaRefConditional],
                                ExclusiveAreaRef,
                                list[ExclusiveAreaRef],
                                str,
                                None]

ExclusiveAreaElementArgumentType = ExclusiveAreaRefConditional | ExclusiveAreaRef | str


class ExecutableEntity(Identifiable):
    """
    Group AR:EXECUTABLE-ENTITY
    """

    def __init__(self,
                 name: str,
                 activation_reasons: ActivationReasonArgumentType = None,
                 can_enter_leave: CanEnterLeaveArgumentType = None,
                 exclusive_area_nesting_order: ExclusiveAreaNestingOrderArgumentType = None,
                 minimum_start_interval: int | float | None = None,
                 reentrancy_level: ar_enum.ReentrancyLevel | None = None,
                 runs_insides: RunsInsidesArgumentType = None,
                 sw_addr_method: str | SwAddrMethodRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.activation_reasons: list[ExecutableEntityActivationReason] = []  # .ACTIVATION-REASONS
        # .CAN-ENTERS or CAN-ENTER-EXCLUSIVE-AREA-REFS depending on schema version
        self.can_enter_leave: list[ExclusiveAreaRefConditional] = []
        self.exclusive_area_nesting_order: list[ExclusiveAreaNestingOrderRef] = []  # .EXCLUSIVE-AREA-NESTING-ORDER-REFS
        self.minimum_start_interval: float | None = None  # .MINIMUM-START-INTERVAL
        self.reentrancy_level: ar_enum.ReentrancyLevel | None = None  # .REENTRANCY-LEVEL
        # .RUNS-INSIDES or .RUNS-INSIDE-EXCLUSIVE-AREA-REFS depending on schema version
        self.runs_insides: list[ExclusiveAreaRefConditional] = []
        self.sw_addr_method: str | SwAddrMethodRef | None = None  # .SW-ADDR-METHOD-REF

        if activation_reasons is not None:
            if isinstance(activation_reasons, list):
                for activation_reason in activation_reasons:
                    self.append_activation_reason(activation_reason)
            else:
                self.append_activation_reason(activation_reasons)
        if can_enter_leave is not None:
            if isinstance(can_enter_leave, list):
                for elem in can_enter_leave:
                    self.append_can_enter_leave(elem)
            else:
                self.append_can_enter_leave(can_enter_leave)
        if exclusive_area_nesting_order is not None:
            if isinstance(exclusive_area_nesting_order, ExclusiveAreaNestingOrderRef):
                self.append_exclusive_area_nesting_order(exclusive_area_nesting_order)
            elif isinstance(exclusive_area_nesting_order, list):
                for elem in exclusive_area_nesting_order:
                    self.append_exclusive_area_nesting_order(elem)
        self._assign_optional("minimum_start_interval", minimum_start_interval, float)
        self._assign_optional("reentrancy_level", reentrancy_level, ar_enum.ReentrancyLevel)
        if runs_insides is not None:
            if isinstance(runs_insides, list):
                for elem in runs_insides:
                    self.append_runs_insides(elem)
            else:
                self.append_runs_insides(runs_insides)
        self._assign_optional('sw_addr_method', sw_addr_method, SwAddrMethodRef)

    def append_activation_reason(self, activation_reason: ExecutableEntityActivationReason) -> None:
        """
        Appends activation_reason to internal list of activation reasons
        """
        if isinstance(activation_reason, ExecutableEntityActivationReason):
            self.activation_reasons.append(activation_reason)
        else:
            raise TypeError("activation_reason must be of type ExecutableEntityActivationReason")

    def append_can_enter_leave(self, value: ExclusiveAreaElementArgumentType) -> None:
        """
        The executable entity can enter/leave the referenced exclusive area through explicit API calls
        """
        if isinstance(value, ExclusiveAreaRefConditional):
            self.can_enter_leave.append(value)
        elif isinstance(value, (ExclusiveAreaRef, str)):
            self.can_enter_leave.append(ExclusiveAreaRefConditional(value))
        else:
            raise TypeError("value: Invalid type. Expected one of ExclusiveAreaRefConditional, ExclusiveAreaRef, str.")

    def append_exclusive_area_nesting_order(self, exclusive_area_nesting_order: ExclusiveAreaNestingOrderRef) -> None:
        """
        Appends exclusive area reference to internal list of nesting orders
        """
        if isinstance(exclusive_area_nesting_order, ExclusiveAreaNestingOrderRef):
            self.exclusive_area_nesting_order.append(exclusive_area_nesting_order)
        else:
            raise TypeError("exclusive_area_nesting_order must be of type ExclusiveAreaRefConditional")

    def append_runs_insides(self, value: ExclusiveAreaElementArgumentType) -> None:
        """
        The executable entity runs completely inside the referenced exclusive area
        """
        if isinstance(value, ExclusiveAreaRefConditional):
            self.runs_insides.append(value)
        elif isinstance(value, (ExclusiveAreaRef, str)):
            self.runs_insides.append(ExclusiveAreaRefConditional(value))
        else:
            raise TypeError("value: Invalid type. Expected one of ExclusiveAreaRefConditional, ExclusiveAreaRef, str.")


class RunnableEntityArgument(ARObject):
    """
    Complex type AR:RUNNABLE-ENTITY-ARGUMENT
    Tag variants: 'RUNNABLE-ENTITY-ARGUMENT'
    """

    def __init__(self, symbol: str | None = None) -> None:
        super().__init__()
        # .SYMBOL
        self.symbol: str | None = None
        self._assign_optional_strict("symbol", symbol, str)


class AbstractAccessPoint(Identifiable):
    """
    Group AR:ABSTRACT-ACCESS-POINT
    """

    def __init__(self,
                 name: str,
                 return_value_provision: ar_enum.RteApiReturnValueProvision | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .RETURN-VALUE-PROVISION
        self.return_value_provision: ar_enum.RteApiReturnValueProvision | None = None

        self._assign_optional("return_value_provision", return_value_provision, ar_enum.RteApiReturnValueProvision)


class ServerCallPoint(AbstractAccessPoint):
    """
    Group AR:SERVER-CALL-POINT
    """

    def __init__(self,
                 name: str,
                 operation: ROperationInAtomicSwcInstanceRef | None = None,
                 timeout: int | float | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .OPERATION-IREF
        self.operation: ROperationInAtomicSwcInstanceRef | None = None
        # .TIMEOUT
        self.timeout: float | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("operation", operation, ROperationInAtomicSwcInstanceRef)
        self._assign_optional('timeout', timeout, float)


class AsynchronousServerCallPoint(ServerCallPoint):
    """
    Complex type AR:ASYNCHRONOUS-SERVER-CALL-POINT
    Tag variants: 'ASYNCHRONOUS-SERVER-CALL-POINT'
    Use constructor from base class
    """

    def ref(self) -> AsynchronousServerCallPointRef:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else AsynchronousServerCallPointRef(ref_str)


class AsynchronousServerCallResultPoint(AbstractAccessPoint):
    """
    Complex type AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT
    Tag variants: 'ASYNCHRONOUS-SERVER-CALL-RESULT-POINT'
    """

    def __init__(self,
                 name: str,
                 async_server_call_point: AsynchronousServerCallPointRef | str | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .ASYNCHRONOUS-SERVER-CALL-POINT-REF
        self.async_server_call_point: AsynchronousServerCallPointRef | None = None

        self._assign_optional("async_server_call_point", async_server_call_point, AsynchronousServerCallPointRef)

    def ref(self) -> AsynchronousServerCallResultPointRef:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else AsynchronousServerCallResultPointRef(ref_str)


class SynchronousServerCallPoint(ServerCallPoint):
    """
    Complex type AR:SYNCHRONOUS-SERVER-CALL-POINT
    Tag variants: 'SYNCHRONOUS-SERVER-CALL-POINT'
    """

    def __init__(self,
                 name: str,
                 called_from_within_exclusive_area: ExclusiveAreaNestingOrderRef | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .CALLED-FROM-WITHIN-EXCLUSIVE-AREA-REF
        self.called_from_within_exclusive_area: ExclusiveAreaNestingOrderRef | None = None

        self._assign_optional("called_from_within_exclusive_area",
                              called_from_within_exclusive_area,
                              ExclusiveAreaNestingOrderRef)


class ExternalTriggeringPointIdent(AbstractAccessPoint):
    """
    Complex type AR:EXTERNAL-TRIGGERING-POINT-IDENT
    Tag variants: 'IDENT'
    Use constructor from base class
    """

    @convenience_function
    @classmethod
    def make_with_args(cls, name: str, args: dict[str, Any] | None) -> "ExternalTriggeringPointIdent":
        """

        Enables creation of ExternalTriggeringPointIdent by giving extra arguments as an optional dictionary
        """
        return cls(name, **args) if args is not None else cls(name)


class ExternalTriggeringPoint(ARObject):
    """
    Complex type AR:EXTERNAL-TRIGGERING-POINT
    Tag variants: 'EXTERNAL-TRIGGERING-POINT'
    """

    def __init__(self,
                 ident: ExternalTriggeringPointIdent | None = None,
                 trigger: PTriggerInAtomicSwcTypeInstanceRef | None = None
                 ) -> None:
        super().__init__()
        # .IDENT
        self.ident: ExternalTriggeringPointIdent | None = None
        # .TRIGGER-IREF
        self.trigger: PTriggerInAtomicSwcTypeInstanceRef | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("ident", ident, ExternalTriggeringPointIdent)
        self._assign_optional_strict("trigger", trigger, PTriggerInAtomicSwcTypeInstanceRef)


class InternalTriggeringPoint(AbstractAccessPoint):
    """
    Complex type AR:INTERNAL-TRIGGERING-POINT
    Tag variants: 'INTERNAL-TRIGGERING-POINT'
    """

    def __init__(self, name: str, sw_impl_policy: ar_enum.SwImplPolicy | None = None, **kwargs):
        super().__init__(name, **kwargs)

        # .SW-IMPL-POLICY
        self.sw_impl_policy: ar_enum.SwImplPolicy | None = None
        # .VARIATION-POINT

        self._assign_optional("sw_impl_policy", sw_impl_policy, ar_enum.SwImplPolicy)

    def ref(self) -> InternalTriggeringPointRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else InternalTriggeringPointRef(ref_str)


class ModeAccessPointIdent(AbstractAccessPoint):
    """
    Complex type AR:MODE-ACCESS-POINT-IDENT
    Tag variants: 'IDENT'
    Use constructor from base class
    """

    @convenience_function
    @classmethod
    def make_with_args(cls, name: str, args: dict[str, Any] | None) -> "ModeAccessPointIdent":
        """

        Enables creation of ModeAccessPointIdent by giving extra arguments as an optional dictionary
        """
        return cls(name, **args) if args is not None else cls(name)


class ModeAccessPoint(ARObject):
    """
    Complex type AR:MODE-ACCESS-POINT
    Tag variants: 'MODE-ACCESS-POINT'
    """

    def __init__(self,
                 ident: ModeAccessPointIdent | None = None,
                 mode_group: PModeGroupInAtomicSwcInstanceRef | RModeGroupInAtomicSwcInstanceRef | None = None
                 ) -> None:
        super().__init__()
        # .IDENT
        self.ident: ModeAccessPointIdent | None = None
        # .MODE-GROUP-IREF
        self.mode_group: PModeGroupInAtomicSwcInstanceRef | RModeGroupInAtomicSwcInstanceRef | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("ident", ident, ModeAccessPointIdent)
        if mode_group is not None:
            if isinstance(mode_group, ModeGroupInAtomicSwcInstanceRef):
                self.mode_group = mode_group
            else:
                msg_part_1 = "Invalid type for parameter 'mode_group'. "
                msg_part_2 = "Expected types PModeGroupInAtomicSwcInstanceRef or RModeGroupInAtomicSwcInstanceRef, "
                msg_part_3 = f"got {str(type(mode_group))}"
                raise TypeError(msg_part_1 + msg_part_2 + msg_part_3)


class ModeSwitchPoint(AbstractAccessPoint):
    """
    Complex type AR:MODE-SWITCH-POINT
    Tag variants: 'MODE-SWITCH-POINT'
    """

    def __init__(self,
                 name: str,
                 mode_group: PModeGroupInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MODE-GROUP-IREF
        self.mode_group: PModeGroupInAtomicSwcInstanceRef | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("mode_group", mode_group, PModeGroupInAtomicSwcInstanceRef)

    def ref(self) -> ModeSwitchPointRef:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeSwitchPointRef(ref_str)


class ParameterInAtomicSwcTypeInstanceRef(ARObject):
    """
    Complex type AR:PARAMETER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'AUTOSAR-PARAMETER-IREF'
    """

    def __init__(self,
                 port_prototype: PortPrototypeRef | None = None,
                 root_parameter_data_prototype: DataPrototypeRef | None = None,
                 context_data_prototype: ApplicationCompositeElementDataPrototypeRef | None = None,
                 target_data_prototype: DataPrototypeRef | None = None
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype: PortPrototypeRef | None = None
        # .ROOT-PARAMETER-DATA-PROTOTYPE-REF
        self.root_parameter_data_prototype: DataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REF
        self.context_data_prototype: ApplicationCompositeElementDataPrototypeRef | None = None
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype: DataPrototypeRef | None = None

        self._assign_optional("port_prototype", port_prototype, PortPrototypeRef)
        self._assign_optional("root_parameter_data_prototype", root_parameter_data_prototype, DataPrototypeRef)
        self._assign_optional("context_data_prototype",
                              context_data_prototype, ApplicationCompositeElementDataPrototypeRef)
        self._assign_optional("target_data_prototype", target_data_prototype, DataPrototypeRef)


class AutosarParameterRef(ARObject):
    """
    Complex type AR:AUTOSAR-PARAMETER-REF
    Tag variants: 'ACCESSED-PARAMETER' | 'AR-PARAMETER' | 'PARAMETER-INSTANCE' |
                  'USED-PARAMETER-ELEMENT'
    """

    def __init__(self,
                 autosar_parameter: ParameterInAtomicSwcTypeInstanceRef | None = None,
                 local_parameter: DataPrototypeRef | None = None) -> None:
        super().__init__()
        # .AUTOSAR-PARAMETER-IREF
        self.autosar_parameter: ParameterInAtomicSwcTypeInstanceRef | None = None
        # .LOCAL-PARAMETER-REF
        self.local_parameter: DataPrototypeRef | None = None

        self._assign_optional_strict("autosar_parameter", autosar_parameter, ParameterInAtomicSwcTypeInstanceRef)
        self._assign_optional("local_parameter", local_parameter, DataPrototypeRef)


class ParameterAccess(AbstractAccessPoint):
    """
    Complex type AR:PARAMETER-ACCESS
    Tag variants: 'PARAMETER-ACCESS'
    """

    def __init__(self,
                 name: str,
                 accessed_parameter: AutosarParameterRef | None = None,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)

        # .ACCESSED-PARAMETER
        self.accessed_parameter: AutosarParameterRef | None = None
        # .SW-DATA-DEF-PROPS
        self.sw_data_def_props: SwDataDefProps | None = None
        # .VARIATION-POINT not supported

        self._assign_optional_strict("accessed_parameter", accessed_parameter, AutosarParameterRef)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("sw_data_def_props: Type must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class WaitPoint(Identifiable):
    """
    Complex type AR:WAIT-POINT
    Tag variants: 'WAIT-POINT'
    """

    def __init__(self,
                 name: str,
                 trigger: RteEventRef | None = None,
                 timeout: int | float | None = None,
                 **kwargs):
        super().__init__(name, **kwargs)
        # .TIMEOUT
        self.timeout: float | None = None
        # .TRIGGER-REF
        self.trigger: RteEventRef | None = None

        self._assign_optional("trigger", trigger, RteEventRef)
        self._assign_optional("timeout", timeout, float)


AsyncServerCallResultPointArgumentType = AsynchronousServerCallResultPoint | list[AsynchronousServerCallResultPoint]
ServerCallPointArgumentType = Union[AsynchronousServerCallPoint,
                                    SynchronousServerCallPoint,
                                    list[AsynchronousServerCallPoint | SynchronousServerCallPoint]]


@dataclass
class PortAccessOptions:
    """
    Internal class used for creating port access
    """

    access: ar_enum.PortAccess = ar_enum.PortAccess.EXPLICIT
    result: ar_enum.ReadResult = ar_enum.ReadResult.BY_ARGUMENT
    mode: ar_enum.ModeAccess | None = None
    call: ar_enum.CallPoint = ar_enum.CallPoint.SYNC
    trigger: ar_enum.TriggerPoint = ar_enum.TriggerPoint.EXTERNAL


class RunnableEntity(ExecutableEntity):
    """
    Complex type AR:RUNNABLE-ENTITY
    Tag variants: 'RUNNABLE-ENTITY'
    """

    def __init__(self,
                 name: str,
                 argument: RunnableEntityArgument | list[RunnableEntityArgument] | None = None,
                 async_server_call_result_point: AsyncServerCallResultPointArgumentType | None = None,
                 can_be_invoked_concurrently: bool | None = None,
                 data_read_access: VariableAccess | list[VariableAccess] | None = None,
                 data_receive_point_by_argument: VariableAccess | list[VariableAccess] | None = None,
                 data_receive_point_by_value: VariableAccess | list[VariableAccess] | None = None,
                 data_send_point: VariableAccess | list[VariableAccess] | None = None,
                 data_write_access: VariableAccess | list[VariableAccess] | None = None,
                 external_triggering_point: ExternalTriggeringPoint | list[ExternalTriggeringPoint] | None = None,
                 internal_triggering_point: InternalTriggeringPoint | list[InternalTriggeringPoint] | None = None,
                 mode_access_point: ModeAccessPoint | list[ModeAccessPoint] | None = None,
                 mode_switch_point: ModeSwitchPoint | list[ModeSwitchPoint] | None = None,
                 parameter_access: ParameterAccess | list[ParameterAccess] | None = None,
                 read_local_variable: VariableAccess | list[VariableAccess] | None = None,
                 write_local_variable: VariableAccess | list[VariableAccess] | None = None,
                 server_call_point: ServerCallPointArgumentType | None = None,
                 wait_point: WaitPoint | list[WaitPoint] | None = None,
                 symbol: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ARGUMENTS
        self.argument: list[RunnableEntityArgument] = []
        # .ASYNCHRONOUS-SERVER-CALL-RESULT-POINTS
        self.async_server_call_result_point: list[AsynchronousServerCallResultPoint] = []
        # .CAN-BE-INVOKED-CONCURRENTLY
        self.can_be_invoked_concurrently: bool | None = None
        # .DATA-READ-ACCESSS
        self.data_read_access: list[VariableAccess] = []
        # .DATA-RECEIVE-POINT-BY-ARGUMENTS
        self.data_receive_point_by_argument: list[VariableAccess] = []
        # .DATA-RECEIVE-POINT-BY-VALUES
        self.data_receive_point_by_value: list[VariableAccess] = []
        # .DATA-SEND-POINTS
        self.data_send_point: list[VariableAccess] = []
        # .DATA-WRITE-ACCESSS
        self.data_write_access: list[VariableAccess] = []
        # .EXTERNAL-TRIGGERING-POINTS
        self.external_triggering_point: list[ExternalTriggeringPoint] = []
        # .INTERNAL-TRIGGERING-POINTS
        self.internal_triggering_point: list[InternalTriggeringPoint] = []
        # .MODE-ACCESS-POINTS
        self.mode_access_point: list[ModeAccessPoint] = []
        # .MODE-SWITCH-POINTS
        self.mode_switch_point: list[ModeSwitchPoint] = []
        # .PARAMETER-ACCESSS
        self.parameter_access: list[ParameterAccess] = []
        # .READ-LOCAL-VARIABLES
        self.read_local_variable: list[VariableAccess] = []
        # .SERVER-CALL-POINTS
        self.server_call_point: list[AsynchronousServerCallPoint | SynchronousServerCallPoint] = []
        # .SYMBOL
        self.symbol: str | None = None
        # .WAIT-POINTS
        self.wait_point: list[WaitPoint] = []
        # .WRITTEN-LOCAL-VARIABLES (We use a different name in our variable)
        self.write_local_variable: list[VariableAccess] = []

        # Simple arguments
        self._assign_optional("can_be_invoked_concurrently", can_be_invoked_concurrently, bool)
        self._assign_optional_strict("symbol", symbol, str)

        # Complex arguments
        if argument is not None:
            if isinstance(argument, Iterable):
                for elem in argument:
                    self.append_argument(elem)
            else:
                self.append_argument(argument)

        if async_server_call_result_point is not None:
            if isinstance(async_server_call_result_point, Iterable):
                for elem in async_server_call_result_point:
                    self.append_async_server_call_result_point(elem)
            else:
                self.append_async_server_call_result_point(async_server_call_result_point)

        if data_read_access is not None:
            if isinstance(data_read_access, Iterable):
                for elem in data_read_access:
                    self.append_data_read_access(elem)
            else:
                self.append_data_read_access(data_read_access)

        if data_receive_point_by_argument is not None:
            if isinstance(data_receive_point_by_argument, Iterable):
                for elem in data_receive_point_by_argument:
                    self.append_data_receive_point_by_argument(elem)
            else:
                self.append_data_receive_point_by_argument(data_receive_point_by_argument)

        if data_receive_point_by_value is not None:
            if isinstance(data_receive_point_by_value, Iterable):
                for elem in data_receive_point_by_value:
                    self.append_data_receive_point_by_value(elem)
            else:
                self.append_data_receive_point_by_value(data_receive_point_by_value)

        if data_send_point is not None:
            if isinstance(data_send_point, Iterable):
                for elem in data_send_point:
                    self.append_data_send_point(elem)
            else:
                self.append_data_send_point(data_send_point)

        if data_write_access is not None:
            if isinstance(data_write_access, Iterable):
                for elem in data_write_access:
                    self.append_data_write_access(elem)
            else:
                self.append_data_write_access(data_write_access)

        if external_triggering_point is not None:
            if isinstance(external_triggering_point, Iterable):
                for elem in external_triggering_point:
                    self.append_external_triggering_point(elem)
            else:
                self.append_external_triggering_point(external_triggering_point)

        if internal_triggering_point is not None:
            if isinstance(internal_triggering_point, Iterable):
                for elem in internal_triggering_point:
                    self.append_internal_triggering_point(elem)
            else:
                self.append_internal_triggering_point(internal_triggering_point)

        if mode_access_point is not None:
            if isinstance(mode_access_point, Iterable):
                for elem in mode_access_point:
                    self.append_mode_access_point(elem)
            else:
                self.append_mode_access_point(mode_access_point)

        if mode_switch_point is not None:
            if isinstance(mode_switch_point, Iterable):
                for elem in mode_switch_point:
                    self.append_mode_switch_point(elem)
            else:
                self.append_mode_switch_point(mode_switch_point)

        if parameter_access is not None:
            if isinstance(parameter_access, Iterable):
                for elem in parameter_access:
                    self.append_parameter_access(elem)
            else:
                self.append_parameter_access(parameter_access)

        if read_local_variable is not None:
            if isinstance(read_local_variable, Iterable):
                for elem in read_local_variable:
                    self.append_read_local_variable(elem)
            else:
                self.append_read_local_variable(read_local_variable)

        if write_local_variable is not None:
            if isinstance(write_local_variable, Iterable):
                for elem in write_local_variable:
                    self.append_write_local_variable(elem)
            else:
                self.append_write_local_variable(write_local_variable)

        if server_call_point is not None:
            if isinstance(server_call_point, Iterable):
                for elem in server_call_point:
                    self.append_server_call_point(elem)
            else:
                self.append_server_call_point(server_call_point)

        if wait_point is not None:
            if isinstance(wait_point, Iterable):
                for elem in wait_point:
                    self.append_wait_point(elem)
            else:
                self.append_wait_point(wait_point)

    def ref(self) -> RunnableEntityRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else RunnableEntityRef(ref_str)

    @convenience_function
    def create_port_access(self,
                           elements: str | list[str] | tuple[str, dict] | list[tuple[str, dict]]
                           ) -> None:
        """

        Attempts to automatically create new port access points based on SWC port names.
        Before this function can be used you must first setup the necessary name prefixes in the
        BehaviorSeettings object (see unit tests for examples).

        Arguments:
        elements: list of strings (See below).
                  Optionally each element can be of type tuple[str, dict] where the the dict is used
                  as additional arguments for during the access point creation.

        SenderReceiver and NvData Interfaces:
            String formats:
                1. "<prefix>:<port-name>/<element-name>"
                2. "<prefix>:<port-name>
                3. "<port-name>/<element-name>"
                4. "<port-name>"
            Accepted Prefixes:
                * "ARGUMENT" | "ARG" (default for r-port): Explicit read. Value is returned by argument.
                * "VALUE" | "VAL" : Explicit read. Value is returned by function return.
                * "READ" : Implicit read.
                * "WRITE" : Implicit write.
                * "SEND" (defalt for p-port) : Explicit write.

        ClientServer Interface:
            String formats:
                1. "<prefix>:<port-name>/<operation-name>"
                2. "<port-name>/<operation-name>"
            Accepted Prefixes:
                * "ASYNC" : Asynchronous call point
                * "SYNC" (default) : Synchronous call point

        ModeSwitch Interface:
            String formats:
                1. "<prefix>:<port-name>"
                2. "<port-name>"
            Accepcted prefixes:
                * "ACCESS" (default) : ModeAccessPoint
                * "SWITCH" :  ModeSwitchpoint

        Trigger Interface:
            String formats:
                1. "<prefix>:<port-name>/<trigger-name>"
                2. "<prefix>:<trigger-name>
                3. "<port-name>/<trigger-name>"
                4. "<port-name>"

            Accepted Prefixes:
                * "EXTERNAL" | "EXTERN" | "EXT" (default) : ExternalTriggeringPoint
        """
        behavior = self.get_valid_parent()
        swc = behavior.get_valid_parent()
        workspace: PackageCollection = swc.root_collection()
        if workspace is None:
            raise ValueError("Runnable doesn't seem to belong to a root collection")
        settings = workspace.get_valid_behavior_settings()
        if isinstance(elements, (str, tuple)):
            elements = [elements]
        for elem in elements:
            if isinstance(elem, tuple):
                text, access_point_args = elem
            else:
                text, access_point_args = elem, None
            options = PortAccessOptions()
            parts = text.partition(":")
            if parts[1] == ":":
                self._parse_port_access_prefix(parts[0].upper(), options)
                port_arg = parts[2].lstrip()
            else:
                port_arg = parts[0]
            ref = port_arg.partition("/")
            port_name = ref[0]
            port: PortPrototypeElement = swc.find(port_name)
            if port is None:
                raise ValueError(f"Invalid port name: {port_name}")
            port_interface = workspace.get_port_interface(port.port_interface_ref)
            self._create_port_access_internal(port, port_interface, ref[2], settings, options, access_point_args)

    @convenience_function
    def create_internal_triggering_point(self,
                                         trigger_name: str,
                                         sw_impl_policy: ar_enum.SwImplPolicy | None = None,
                                         **kwargs) -> None:
        """
        Create a new internal triggering point for this runnable entity
        """
        triggering_point = InternalTriggeringPoint(trigger_name, sw_impl_policy, **kwargs)
        self.append_internal_triggering_point(triggering_point)

    def _parse_port_access_prefix(self, text: str, options: PortAccessOptions) -> None:
        """
        Parses port access prefix
        """
        if text == 'ASYNC':
            options.call = ar_enum.CallPoint.ASYNC
        elif text == "SYNC":
            options.call = ar_enum.CallPoint.SYNC
        elif text in ["READ", "WRITE"]:
            options.access = ar_enum.PortAccess.IMPLICIT
        elif text in ["ARGUMENT", "ARG"]:
            options.access = ar_enum.PortAccess.EXPLICIT
            options.result = ar_enum.ReadResult.BY_ARGUMENT
        elif text in ["VALUE", "VAL"]:
            options.access = ar_enum.PortAccess.EXPLICIT
            options.result = ar_enum.ReadResult.BY_VALUE
        elif text == "SEND":
            options.access = ar_enum.PortAccess.EXPLICIT
        elif text == "ACCESS":
            options.mode = ar_enum.ModeAccess.ACCESS
        elif text == "SWITCH":
            options.mode = ar_enum.ModeAccess.SWITCH
        elif text in ["EXTERNAL", "EXTERN", "EXT"]:
            options.trigger = ar_enum.TriggerPoint.EXTERNAL
        else:
            raise ValueError(f"Unrecognized access option: '{text}'")

    def _create_port_access_internal(self,
                                     port: PortPrototypeElement,
                                     port_interface: PortInterface,
                                     element_name: str,
                                     settings: BehaviorSettings,
                                     options: PortAccessOptions,
                                     access_point_args: dict[str, Any] | None) -> None:
        """
        Helper function for creating port access
        """
        if isinstance(port_interface, (SenderReceiverInterface, NvDataInterface)):
            self._create_data_based_port_access(port, port_interface, element_name,
                                                settings, options.access, options.result, access_point_args)
        elif isinstance(port_interface, ModeSwitchInterface):
            self._create_mode_based_port_access(port, port_interface, element_name,
                                                settings, options.mode, access_point_args)
        elif isinstance(port_interface, ParameterInterface):
            self._create_parameter_port_access(port, port_interface, element_name, settings, access_point_args)
        elif isinstance(port_interface, ClientServerInterface):
            self._create_client_server_port_access(port, port_interface, element_name,
                                                   settings, options.call, access_point_args)
        elif isinstance(port_interface, TriggerInterface):
            self._create_trigger_port_access(port, port_interface, element_name,
                                             settings, options.trigger, access_point_args)
        else:
            raise NotImplementedError(str(type(port_interface)))

    def _create_data_based_port_access(self,
                                       port: PortPrototypeElement,
                                       port_interface: SenderReceiverInterface | NvDataInterface,
                                       element_name: str,
                                       settings: BehaviorSettings,
                                       access_type: ar_enum.PortAccess,
                                       result_type: ar_enum.ReadResult,
                                       access_point_args: dict[str, Any] | None) -> None:
        """
        Automatically create port access for SenderReceiverInterface or NvDataInterface
        """
        data_element = None
        if len(element_name) == 0:
            if len(port_interface.data_elements) == 1:
                data_element = port_interface.data_elements[0]
        else:
            for element in port_interface.data_elements:
                if element.name == element_name:
                    data_element = element
        if data_element is None:
            raise builtins.RuntimeError(f"Unable to find a matching data element '{element_name}' "
                                        f"in port interface '{port_interface.name}'")
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if isinstance(port, RequirePortPrototype):
            if access_type == ar_enum.PortAccess.IMPLICIT:
                if name is None:
                    name = "_".join([settings.get_value("data_read_access_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                self.append_data_read_access(variable_access)
            else:
                if name is None:
                    name = "_".join([settings.get_value("data_receive_point_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                if result_type == ar_enum.ReadResult.BY_VALUE:
                    self.append_data_receive_point_by_value(variable_access)
                else:
                    self.append_data_receive_point_by_argument(variable_access)
        elif isinstance(port, ProvidePortPrototype):
            if access_type == ar_enum.PortAccess.IMPLICIT:
                if name is None:
                    name = "_".join([settings.get_value("data_write_access_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                self.append_data_write_access(variable_access)
            else:
                if name is None:
                    name = "_".join([settings.get_value("data_send_point_prefix"), port.name, data_element.name])
                variable_access = VariableAccess.make_from_port_with_args(name, port.ref(), data_element.ref(),
                                                                          access_point_args)
                self.append_data_send_point(variable_access)
        else:
            raise TypeError(f"Type not supported: {str(type(port))}")

    def _create_mode_based_port_access(self,
                                       port: PortPrototypeElement,
                                       port_interface: ModeSwitchInterface,
                                       mode_group_name: str,
                                       settings: BehaviorSettings,
                                       access_type: ar_enum.ModeAccess | None,
                                       access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for mode-based interfaces.

        access_point_args:
            For ModeAccess it's used as additional arguments for the internal ModeAccessPointIdent object.
            For ModeSwitchPoint it's used as additional arguments for the ModeSwitchPoint object.
        """
        mode_group = None
        if len(mode_group_name) != 0:
            if mode_group_name == port_interface.mode_group.name:
                mode_group = port_interface.mode_group
        else:
            mode_group = port_interface.mode_group
        if mode_group is None:
            raise builtins.RuntimeError(f"Unable to find a ModeDeclarationGroupPrototype named '{mode_group_name}' "
                                        f"in port interface '{port_interface.name}'")
        name: str | None = None
        access_point = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if isinstance(port, RequirePortPrototype):
            mode_group_iref = RModeGroupInAtomicSwcInstanceRef(port.ref(), mode_group.ref())
            if access_type is None:
                access_point = ModeAccessPoint(mode_group=mode_group_iref)
            elif access_type == ar_enum.ModeAccess.ACCESS:
                if name is None:
                    name = "_".join([settings.get_value("mode_access_point_prefix"), port.name, mode_group.name])
                ident = ModeAccessPointIdent.make_with_args(name, access_point_args)
                access_point = ModeAccessPoint(ident=ident, mode_group=mode_group_iref)
        elif isinstance(port, ProvidePortPrototype):
            mode_group_iref = PModeGroupInAtomicSwcInstanceRef(port.ref(), mode_group.ref())
            if access_type is None:
                access_point = ModeAccessPoint(mode_group=mode_group_iref)
            elif access_type == ar_enum.ModeAccess.ACCESS:
                if name is None:
                    name = "_".join([settings.get_value("mode_access_point_prefix"), port.name, mode_group.name])
                ident = ModeAccessPointIdent.make_with_args(name, access_point_args)
                access_point = ModeAccessPoint(ident=ident, mode_group=mode_group_iref)
            else:
                if name is None:
                    name = "_".join([settings.get_value("mode_switch_point_prefix"), port.name, mode_group.name])
                if access_point_args is not None:
                    switch_point = ModeSwitchPoint(name, mode_group_iref, **access_point_args)
                else:
                    switch_point = ModeSwitchPoint(name, mode_group_iref)
                self.append_mode_switch_point(switch_point)
        if access_point:
            self.append_mode_access_point(access_point)

    def _create_parameter_port_access(self,
                                      port: PortPrototypeElement,
                                      port_interface: ParameterInterface,
                                      parameter_name: str,
                                      settings: BehaviorSettings,
                                      access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for parameter interface
        """
        target_data = None
        if len(parameter_name) == 0:
            if len(port_interface.parameters) == 1:
                target_data = port_interface.parameter[0]
        else:
            for element in port_interface.parameters:
                if element.name == parameter_name:
                    target_data = element
        if target_data is None:
            raise builtins.RuntimeError(f"Unable to find a matching parameter element '{parameter_name}' "
                                        f"in port interface '{port_interface.name}'")
        parameter_iref = ParameterInAtomicSwcTypeInstanceRef(port_prototype=port.ref(),
                                                             target_data_prototype=target_data.ref())
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if name is None:
            name = "_".join([settings.get_value("parameter_access_prefix"),
                            port.name,
                            target_data.name])
        if access_point_args is not None:
            parameter_access = ParameterAccess(name,
                                               AutosarParameterRef(autosar_parameter=parameter_iref),
                                               **access_point_args)
        else:
            parameter_access = ParameterAccess(name, AutosarParameterRef(autosar_parameter=parameter_iref))
        self.append_parameter_access(parameter_access)

    def _create_client_server_port_access(self,
                                          port: PortPrototypeElement,
                                          port_interface: ClientServerInterface,
                                          operation_name: str,
                                          settings: BehaviorSettings,
                                          call_type: ar_enum.CallPoint,
                                          access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for client-server interfaces
        """
        operation = None
        if len(operation_name) == 0:
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
        else:
            for element in port_interface.operations:
                if element.name == operation_name:
                    operation = element
        if operation is None:
            raise builtins.RuntimeError(f"Unable to find a matching operation '{operation_name}' "
                                        f"in port interface '{port_interface.name}'")
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if isinstance(port, (RequirePortPrototype, PRPortPrototype)):
            access_point = None
            if name is None:
                name = "_".join([settings.get_value("server_call_point_prefix"), port.name, operation.name])
            operation_iref = ROperationInAtomicSwcInstanceRef(port.ref(), operation.ref())
            if access_point_args is not None:
                if call_type == ar_enum.CallPoint.ASYNC:
                    access_point = AsynchronousServerCallPoint(name, operation_iref, **access_point_args)
                else:
                    access_point_args["operation"] = operation_iref
                    access_point = SynchronousServerCallPoint(name, **access_point_args)
            else:
                if call_type == ar_enum.CallPoint.ASYNC:
                    access_point = AsynchronousServerCallPoint(name, operation_iref)
                else:
                    access_point = SynchronousServerCallPoint(name, operation=operation_iref)
            if access_point:
                self.append_server_call_point(access_point)

    def _create_trigger_port_access(self,
                                    port: PortPrototypeElement,
                                    port_interface: TriggerInterface,
                                    trigger_name: str,
                                    settings: BehaviorSettings,
                                    trigger_point_type: ar_enum.TriggerPoint,
                                    access_point_args: dict[str, Any] | None) -> None:
        """
        Creates port access for trigger interfaces
        """
        trigger = None
        if len(trigger_name) == 0:
            if len(port_interface.triggers) == 1:
                trigger = port_interface.triggers[0]
        else:
            for element in port_interface.triggers:
                if element.name == trigger_name:
                    trigger = element
        if trigger is None:
            raise builtins.RuntimeError(f"Unable to find a matching trigger '{trigger_name}' "
                                        f"in port interface '{port_interface.name}'")
        if isinstance(port, (ProvidePortPrototype, PRPortPrototype)):
            triggering_point = None
            if trigger_point_type == ar_enum.TriggerPoint.EXTERNAL:
                triggering_point = self._create_external_triggering_point(port, trigger, settings, access_point_args)
            else:
                triggering_point = self._create_internal_triggering_point(port, trigger, settings, access_point_args)
            self.append_external_triggering_point(triggering_point)

    def _create_external_triggering_point(self,
                                          port: PortPrototypeElement,
                                          trigger: Trigger,
                                          settings: BehaviorSettings,
                                          access_point_args: dict[str, Any] | None) -> ExternalTriggeringPoint:
        """
        Creates an ExternalTriggeringPoint object
                 context_port: AbstractProvidedPortPrototypeRef | None = None,
                 target_trigger: TriggerRef | str | None = None,
        """
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if name is None:
            name = "_".join([settings.get_value("external_triggering_point_prefix"), port.name, trigger.name])
        ident = ExternalTriggeringPointIdent.make_with_args(name, access_point_args)
        instance_trigger = PTriggerInAtomicSwcTypeInstanceRef(port.ref(), trigger.ref())
        return ExternalTriggeringPoint(ident=ident, trigger=instance_trigger)

    def _create_internal_triggering_point(self,
                                          port: PortPrototypeElement,
                                          trigger: Trigger,
                                          settings: BehaviorSettings,
                                          access_point_args: dict[str, Any] | None) -> InternalTriggeringPoint:
        """
        Creates an InternalTriggeringPoint object
        """
        name: str | None = None
        if access_point_args is not None and "name" in access_point_args:
            name = access_point_args["name"]
            del access_point_args["name"]
        if name is None:
            name = "_".join([settings.get_value("internal_triggering_point_prefix"), port.name, trigger.name])
        if access_point_args is not None:
            return InternalTriggeringPoint(name, **access_point_args)
        else:
            return InternalTriggeringPoint(name)

    def append_argument(self, argument: RunnableEntityArgument) -> None:
        """
        Adds additional argument to the RunnableEntity
        """
        if isinstance(argument, RunnableEntityArgument):
            self.argument.append(argument)
        else:
            raise TypeError(f"argument: Expected type RunnableEntityArgument, got '{str(type(argument))}'")

    def append_async_server_call_result_point(self,
                                              result_point: AsynchronousServerCallResultPoint
                                              ) -> None:
        """
        A server call result point allows a runnable to fetch the result of an asynchronous server call.
        """
        if isinstance(result_point, AsynchronousServerCallResultPoint):
            make_unique_name_in_list(self.async_server_call_result_point, result_point.name)
            self.async_server_call_result_point.append(result_point)
            result_point.parent = self
        else:
            raise TypeError("result_point: Expected type AsynchronousServerCallResultPoint, "
                            f"got '{str(type(result_point))}'")

    def append_data_read_access(self, element: VariableAccess) -> None:
        """
        Implicit read access to data element of a sender-receiver port or nv-data port.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_read_access, element.name)
            self.data_read_access.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_receive_point_by_argument(self, element: VariableAccess) -> None:
        """
        Explicit read access to data element of a sender-receiver port or nv-data port.
        The result is passed back to the application by means of an argument in the function signature.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_receive_point_by_argument, element.name)
            self.data_receive_point_by_argument.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_receive_point_by_value(self, element: VariableAccess) -> None:
        """
        Explicit read access to data element of a sender-receiver port or nv-data port.
        The result is passed back to the application by means of the return value.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_receive_point_by_value, element.name)
            self.data_receive_point_by_value.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_send_point(self, element: VariableAccess) -> None:
        """
        Explicit write access to data element of a sender-receiver port or nv-data.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_send_point, element.name)
            self.data_send_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_data_write_access(self, element: VariableAccess) -> None:
        """
        Implicit write access to data element of a sender-receiver port or nv-data port.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.data_write_access, element.name)
            self.data_write_access.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_external_triggering_point(self, element: ExternalTriggeringPoint) -> None:
        """
        External triggering point
        """
        if isinstance(element, ExternalTriggeringPoint):
            self.external_triggering_point.append(element)
            if element.ident is not None:
                element.ident.parent = self
        else:
            raise TypeError(f"element: Expected type ExternalTriggeringPoint, got '{str(type(element))}'")

    def append_internal_triggering_point(self, element: InternalTriggeringPoint) -> None:
        """
        Internal triggering point
        """
        if isinstance(element, InternalTriggeringPoint):
            make_unique_name_in_list(self.internal_triggering_point, element.name)
            self.internal_triggering_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type InternalTriggeringPoint, got '{str(type(element))}'")

    def append_mode_access_point(self, element: ModeAccessPoint) -> None:
        """
        Mode access point
        """
        if isinstance(element, ModeAccessPoint):
            self.mode_access_point.append(element)
            if element.ident is not None:
                element.ident.parent = self
        else:
            raise TypeError(f"element: Expected type ModeAccessPoint, got '{str(type(element))}'")

    def append_mode_switch_point(self, element: ModeSwitchPoint) -> None:
        """
        Mode switch point
        """
        if isinstance(element, ModeSwitchPoint):
            make_unique_name_in_list(self.mode_switch_point, element.name)
            self.mode_switch_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type ModeSwitchPoint, got '{str(type(element))}'")

    def append_parameter_access(self, element: ParameterAccess) -> None:
        """
        Read access to parameter which may either be local or within a PortPrototype.
        """
        if isinstance(element, ParameterAccess):
            make_unique_name_in_list(self.parameter_access, element.name)
            self.parameter_access.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type ParameterAccess, got '{str(type(element))}'")

    def append_read_local_variable(self, element: VariableAccess) -> None:
        """
        Read access to a local variable in the role of ImplicitInterRunnableVariable or ExplicitInterRunnableVariable.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.read_local_variable, element.name)
            self.read_local_variable.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_write_local_variable(self, element: VariableAccess) -> None:
        """
        Write access to a local varaible in the role of ImplicitInterRunnableVariable or ExplicitInterRunnableVariable.
        """
        if isinstance(element, VariableAccess):
            make_unique_name_in_list(self.write_local_variable, element.name)
            self.write_local_variable.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type VariableAccess, got '{str(type(element))}'")

    def append_server_call_point(self, element: AsynchronousServerCallPoint | SynchronousServerCallPoint) -> None:
        """
        Access to call a server operation of a client-server port.
        """
        if isinstance(element, ServerCallPoint):
            make_unique_name_in_list(self.server_call_point, element.name)
            self.server_call_point.append(element)
            element.parent = self
        else:
            raise TypeError("element: Expected type AsynchronousServerCallPoint or SynchronousServerCallPoint, "
                            f"got '{str(type(element))}'")

    def append_wait_point(self, element: WaitPoint) -> None:
        """
        Append a WaitPoint associated with the RunnableEntity.
        """
        if isinstance(element, WaitPoint):
            make_unique_name_in_list(self.wait_point, element.name)
            self.wait_point.append(element)
            element.parent = self
        else:
            raise TypeError(f"element: Expected type WaitPoint, got '{str(type(element))}'")

    def get_valid_parent(self) -> "SwcInternalBehavior":
        """
        Verifies that this object has valid SwcInternalBehavior as parent before returning it
        """
        if self.parent is None or not isinstance(self.parent, SwcInternalBehavior):
            raise builtins.RuntimeError("Runnable object doesn't have a valid parent")
        return self.parent


class RteEvent(Identifiable):
    """
    Group AR:RTE-EVENT
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | None = None,
                 disabled_modes: RModeInAtomicSwcInstanceRef | list[RModeInAtomicSwcInstanceRef] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DISABLED-MODE-IREFS
        self.disabled_modes: list[RModeInAtomicSwcInstanceRef] = []
        # .START-ON-EVENT-REF
        self.start_on_event: RunnableEntityRef | None = None

        if disabled_modes is not None:
            if isinstance(disabled_modes, RModeInAtomicSwcInstanceRef):
                self.append_disabled_mode(disabled_modes)
            elif isinstance(disabled_modes, list):
                for disabled_mode in disabled_modes:
                    self.append_disabled_mode(disabled_mode)
        self._assign_optional("start_on_event", start_on_event, RunnableEntityRef)

    def append_disabled_mode(self, disabled_mode: RModeInAtomicSwcInstanceRef) -> None:
        """
        Adds reference to the modes that disable the event
        """
        if isinstance(disabled_mode, RModeInAtomicSwcInstanceRef):
            self.disabled_modes.append(disabled_mode)
        else:
            raise TypeError("disabled_mode must be of type RModeInAtomicSwcInstanceRef")


class AsynchronousServerCallReturnsEvent(RteEvent):
    """
    Complex type AR:ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT
    Tag variants: 'ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: AsynchronousServerCallResultPointRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: AsynchronousServerCallResultPointRef | None = None
        self._assign_optional("event_source", event_source, AsynchronousServerCallResultPointRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_RETURNS_EVENT)


class BackgroundEvent(RteEvent):
    """
    Complex type AR:BACKGROUND-EVENT
    Tag variants: 'BACKGROUND-EVENT'
    Inherits constructor from base-class
    """

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.BACKGROUND_EVENT)


class DataReceiveErrorEvent(RteEvent):
    """
    Complex type AR:DATA-RECEIVE-ERROR-EVENT
    Tag variants: 'DATA-RECEIVE-ERROR-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 data: RVariableInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .DATA-IREF
        self.data: RVariableInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("data", data, RVariableInAtomicSwcInstanceRef)

    @convenience_function
    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             target_data_element: VariableDataPrototypeRef | str | None = None,
             **kwargs) -> "DataReceiveErrorEvent":
        """

        Simplified creation method that automatically creates
        and uses the necessary RVariableInAtomicSwcInstanceRef object
        """
        data = RVariableInAtomicSwcInstanceRef(context_port, target_data_element)
        return cls(name, start_on_event, data, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_RECEIVE_ERROR_EVENT)


class DataReceivedEvent(RteEvent):
    """
    Complex type AR:DATA-RECEIVED-EVENT
    Tag variants: 'DATA-RECEIVED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 data: RVariableInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .DATA-IREF
        self.data: RVariableInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("data", data, RVariableInAtomicSwcInstanceRef)

    @convenience_function
    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             target_data_element: VariableDataPrototypeRef | str | None = None,
             **kwargs) -> "DataReceivedEvent":
        """

        Simplified creation method that automatically creates
        and uses the necessary RVariableInAtomicSwcInstanceRef object
        """
        data = RVariableInAtomicSwcInstanceRef(context_port, target_data_element)
        return cls(name, start_on_event, data, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_RECEIVED_EVENT)


class DataSendCompletedEvent(RteEvent):
    """
    Complex type AR:DATA-SEND-COMPLETED-EVENT
    Tag variants: 'DATA-SEND-COMPLETED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: VariableAccessRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: VariableAccessRef | None = None
        self._assign_optional("event_source", event_source, VariableAccessRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_SEND_COMPLETED_EVENT)


class DataWriteCompletedEvent(RteEvent):
    """
    Complex type AR:DATA-WRITE-COMPLETED-EVENT
    Tag variants: 'DATA-WRITE-COMPLETED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: VariableAccessRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: VariableAccessRef | None = None
        self._assign_optional("event_source", event_source, VariableAccessRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.DATA_WRITE_COMPLETED_EVENT)


class ExternalTriggerOccurredEvent(RteEvent):
    """
    Complex type AR:EXTERNAL-TRIGGER-OCCURRED-EVENT
    Tag variants: 'EXTERNAL-TRIGGER-OCCURRED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 trigger: RTriggerInAtomicSwcInstanceRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .TRIGGER-IREF
        self.trigger: RTriggerInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("trigger", trigger, RTriggerInAtomicSwcInstanceRef)

    @convenience_function
    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             target_trigger: TriggerRef | str | None = None,
             **kwargs) -> "ExternalTriggerOccurredEvent":
        """
        Simplified creation method that automatically creates
        and uses the necessary RTriggerInAtomicSwcInstanceRef object
        """
        trigger = RTriggerInAtomicSwcInstanceRef(context_port, target_trigger)
        return cls(name, start_on_event, trigger, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.EXTERNAL_TRIGGER_OCCURRED_EVENT)


class InitEvent(RteEvent):
    """
    Complex type AR:INIT-EVENT
    Tag variants: 'INIT-EVENT'
    Inherits constructor from base-class
    """

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.INIT_EVENT)


class InternalTriggerOccurredEvent(RteEvent):
    """
    Complex type AR:INTERNAL-TRIGGER-OCCURRED-EVENT
    Tag variants: 'INTERNAL-TRIGGER-OCCURRED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: InternalTriggeringPointRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: InternalTriggeringPointRef | None = None
        self._assign_optional("event_source", event_source, InternalTriggeringPointRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.INTERNAL_TRIGGER_OCCURRED_EVENT)


class ModeSwitchedAckEvent(RteEvent):
    """
    Complex type AR:MODE-SWITCHED-ACK-EVENT
    Tag variants: 'MODE-SWITCHED-ACK-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 event_source: ModeSwitchPointRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .EVENT-SOURCE-REF
        self.event_source: ModeSwitchPointRef | None = None
        self._assign_optional("event_source", event_source, ModeSwitchPointRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.MODE_SWITCHED_ACK_EVENT)


class OperationInvokedEvent(RteEvent):
    """
    Complex type AR:OPERATION-INVOKED-EVENT
    Tag variants: 'OPERATION-INVOKED-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 operation: POperationInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .OPERATION-IREF
        self.operation: POperationInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("operation", operation, POperationInAtomicSwcInstanceRef)

    @convenience_function
    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractProvidedPortPrototypeRef | None = None,
             target_provided_operation: ClientServerOperationRef | str | None = None,
             **kwargs) -> "OperationInvokedEvent":
        """

        Simplified creation method that automatically creates
        and uses the necessary POperationInAtomicSwcInstanceRef object
        """
        operation = POperationInAtomicSwcInstanceRef(context_port, target_provided_operation)
        return cls(name, start_on_event, operation, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.OPERATION_INVOKED_EVENT)


class OsTaskExecutionEvent(RteEvent):
    """
    Complex type AR:OS-TASK-EXECUTION-EVENT
    Tag variants: 'OS-TASK-EXECUTION-EVENT'

    Inherits constructor from base class
    """

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.OS_TASK_EXECUTION_EVENT)


SwcModeSwitchEventModeType = Union[RModeInAtomicSwcInstanceRef,
                                   tuple[RModeInAtomicSwcInstanceRef, RModeInAtomicSwcInstanceRef],
                                   None]


class SwcModeManagerErrorEvent(RteEvent):
    """
    Complex type AR:SWC-MODE-MANAGER-ERROR-EVENT
    Tag variants: 'SWC-MODE-MANAGER-ERROR-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 mode_group: PModeGroupInAtomicSwcInstanceRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .MODE-GROUP-IREF
        self.mode_group: PModeGroupInAtomicSwcInstanceRef | None = None
        self._assign_optional_strict("mode_group", mode_group, PModeGroupInAtomicSwcInstanceRef)

    @convenience_function
    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             context_port: AbstractProvidedPortPrototypeRef | None = None,
             context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | str | None = None,
             **kwargs) -> "SwcModeManagerErrorEvent":
        """
        Simplified creation method that automatically creates
        and uses the necessary PModeGroupInAtomicSwcInstanceRef object
        """
        mode_group = PModeGroupInAtomicSwcInstanceRef(context_port, context_mode_declaration_group_prototype)
        return cls(name, start_on_event, mode_group, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.SWC_MODE_MANAGER_ERROR_EVENT)


class SwcModeSwitchEvent(RteEvent):
    """
    Complex type AR:SWC-MODE-SWITCH-EVENT
    Tag variants: 'SWC-MODE-SWITCH-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 activation: ar_enum.ModeActivationKind | None = None,
                 mode: SwcModeSwitchEventModeType = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .ACTIVATION
        self.activation: ar_enum.ModeActivationKind | None = None
        # .MODE-IREFS
        self.mode: SwcModeSwitchEventModeType = None

        self._assign_optional("activation", activation, ar_enum.ModeActivationKind)
        if mode is not None:
            if isinstance(mode, RModeInAtomicSwcInstanceRef):
                self.mode = mode
            elif isinstance(mode, tuple):
                if (isinstance(mode[0], RModeInAtomicSwcInstanceRef) and  # noqa W504
                        isinstance(mode[1], RModeInAtomicSwcInstanceRef)):
                    self.mode = mode
                else:
                    raise TypeError("Both values of mode tuple must be of type RModeInAtomicSwcInstanceRef")
            else:
                msg_part1 = "Invalid type for parameter 'mode'. "
                msg_part2 = "Expected types are RModeInAtomicSwcInstanceRef or tuple of same type."
                msg_part3 = f"Got {str(type(mode))}"
                raise TypeError(msg_part1 + msg_part2 + msg_part3)

    @convenience_function
    @classmethod
    def make(cls,
             name: str,
             start_on_event: RunnableEntityRef | str | None = None,
             activation: ar_enum.ModeActivationKind | None = None,
             context_port: AbstractRequiredPortPrototypeRef | None = None,
             context_mode_declaration_group_prototype: ModeDeclarationGroupPrototypeRef | None = None,
             target_mode_declaration: ModeDeclarationRef | None = None,
             **kwargs) -> "SwcModeSwitchEvent":
        """

        Only suitable for ON-ENTRY and ON-EXIT activation types.
        For ON-TRANSITION activation, use the class constructor instead.

        """
        mode = RModeInAtomicSwcInstanceRef(context_port,
                                           context_mode_declaration_group_prototype,
                                           target_mode_declaration)
        return cls(name, start_on_event, activation, mode, **kwargs)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.SWC_MODE_SWITCH_EVENT)


class TimingEvent(RteEvent):
    """
    Complex type AR:TIMING-EVENT
    Tag variants: 'TIMING-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 period: int | float | None = None,
                 offset: int | float | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .OFFSET
        self.offset: int | float | None = None
        # .PERIOD
        self.period: int | float | None = None

        self._assign_optional("offset", offset, float)
        self._assign_optional("period", period, float)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.TIMING_EVENT)


class TransformerHardErrorEvent(RteEvent):
    """
    Complex type AR:TRANSFORMER-HARD-ERROR-EVENT
    Tag variants: 'TRANSFORMER-HARD-ERROR-EVENT'
    """

    def __init__(self,
                 name: str,
                 start_on_event: RunnableEntityRef | str | None = None,
                 operation: POperationInAtomicSwcInstanceRef | None = None,
                 required_trigger: RTriggerInAtomicSwcInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, start_on_event, **kwargs)
        # .OPERATION-IREF
        self.operation: POperationInAtomicSwcInstanceRef | None = None
        # .REQUIRED-TRIGGER-IREF
        self.required_trigger: RTriggerInAtomicSwcInstanceRef | None = None
        # .TRIGGER-IREF --- REMOVED

        self._assign_optional_strict("operation", operation, POperationInAtomicSwcInstanceRef)
        self._assign_optional_strict("required_trigger", required_trigger, RTriggerInAtomicSwcInstanceRef)

    def ref(self) -> RteEventRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return RteEventRef(ref_str, ar_enum.IdentifiableSubTypes.TRANSFORMER_HARD_ERROR_EVENT)


class PortDefinedArgumentValue(ARObject):
    """
    Complex type AR:PORT-DEFINED-ARGUMENT-VALUE
    Tag variants: 'PORT-DEFINED-ARGUMENT-VALUE'
    """

    def __init__(self,
                 value: ValueSpecificationElement | None = None,
                 value_type: ImplementationDataTypeRef | str | None = None) -> None:
        super().__init__()
        # .VALUE
        self.value: ValueSpecificationElement | None = None
        # .VALUE-TYPE-TREF
        self.value_type: ImplementationDataTypeRef | None = None

        self._assign_optional_strict("value", value, ValueSpecification)
        self._assign_optional("value_type", value_type, ImplementationDataTypeRef)


class SwcSupportedFeature(ARObject):
    """
    Base class for supported features
    """


class CommunicationBufferLocking(SwcSupportedFeature):
    """
    Complex type AR:COMMUNICATION-BUFFER-LOCKING
    Tag variants: 'COMMUNICATION-BUFFER-LOCKING'
    """

    def __init__(self,
                 support_buffer_locking: ar_enum.SupportBufferLocking | None = None) -> None:
        super().__init__()
        # .SUPPORT-BUFFER-LOCKING
        self.support_buffer_locking: ar_enum.SupportBufferLocking = None

        self._assign_optional("support_buffer_locking", support_buffer_locking, ar_enum.SupportBufferLocking)


PortDefinedArgumentValueArgType = PortDefinedArgumentValue | list[PortDefinedArgumentValue] | None
SwcSupportedFeatureArgType = SwcSupportedFeature | list[SwcSupportedFeature] | None


class PortApiOption(ARObject):
    """
    Complex type AR:PORT-API-OPTION
    Tag variants: 'PORT-API-OPTION'
    """

    def __init__(self,
                 port: PortPrototypeRef | None = None,
                 enable_take_address: bool | None = None,
                 indirect_api: bool | None = None,
                 error_handling: ar_enum.DataTransformationErrorHandling | None = None,
                 port_arg_values: PortDefinedArgumentValueArgType = None,
                 supported_features: SwcSupportedFeatureArgType = None,
                 transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None
                 ) -> None:
        super().__init__()
        # .ENABLE-TAKE-ADDRESS
        self.enable_take_address: bool | None = None
        # .ERROR-HANDLING
        self.error_handling: ar_enum.DataTransformationErrorHandling | None = None
        # .INDIRECT-API
        self.indirect_api: bool | None = None
        # .PORT-ARG-VALUES
        self.port_arg_values: list[PortDefinedArgumentValue] = []
        # .PORT-REF
        self.port: PortPrototypeRef | None = port
        # .SUPPORTED-FEATURES
        self.supported_features: list[SwcSupportedFeature] = []
        # .TRANSFORMER-STATUS-FORWARDING
        self.transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None
        # .VARIATION-POINT not supported

        self._assign_optional("enable_take_address", enable_take_address, bool)
        self._assign_optional("error_handling", error_handling, ar_enum.DataTransformationErrorHandling)
        self._assign_optional("indirect_api", indirect_api, bool)
        self._assign_optional("port", port, PortPrototypeRef)
        self._assign_optional("transformer_status_forwarding",
                              transformer_status_forwarding,
                              ar_enum.DataTransformationStatusForwarding)
        if port_arg_values is not None:
            if isinstance(port_arg_values, list):
                for port_arg_value in port_arg_values:
                    self.append_port_arg_value(port_arg_value)
            else:
                self.append_port_arg_value(port_arg_values)
        if supported_features is not None:
            if isinstance(supported_features, list):
                for supported_feature in supported_features:
                    self.append_supported_feature(supported_feature)
            else:
                self.append_supported_feature(supported_features)

    def append_port_arg_value(self, port_arg_value: PortDefinedArgumentValue) -> None:
        """
        Adds PortDefinedArgumentValue to internal list
        """
        if isinstance(port_arg_value, PortDefinedArgumentValue):
            self.port_arg_values.append(port_arg_value)
        else:
            raise TypeError("port_arg_value must be of type PortDefinedArgumentValue")

    def append_supported_feature(self, supported_feature: SwcSupportedFeature) -> None:
        """
        Adds PortDefinedArgumentValue to internal list
        """
        if isinstance(supported_feature, (CommunicationBufferLocking,)):
            self.supported_features.append(supported_feature)
        else:
            raise TypeError("supported_feature must be of type CommunicationBufferLocking")


class ExclusiveArea(Identifiable):
    """
    Complex type AR:EXCLUSIVE-AREA
    Tag variants: 'EXCLUSIVE-AREA'
    Inherits constructor from parent class
    """

    def ref(self) -> ExclusiveAreaRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ExclusiveAreaRef(ref_str)


class ExclusiveAreaNestingOrder(Referrable):
    """
    Complex type AR:EXCLUSIVE-AREA-NESTING-ORDER
    Tag variants: 'EXCLUSIVE-AREA-NESTING-ORDER'
    """

    def __init__(self,
                 name: str,
                 exclusive_area: (ExclusiveAreaRef | list[ExclusiveAreaRef] |
                                  str | list[str] | None) = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        # .EXCLUSIVE-AREA-REFS
        self.exclusive_area: list[ExclusiveAreaRef] = []

        if exclusive_area is not None:
            if isinstance(exclusive_area, (ExclusiveAreaRef, str)):
                self.append(exclusive_area)
            elif isinstance(exclusive_area, Iterable):
                for item in exclusive_area:
                    self.append(item)
            else:
                raise TypeError(f"exclusive_area: Invalid type {str(type(exclusive_area))}")

    def append(self, exclusive_area: ExclusiveAreaRef | str) -> None:
        """
        Adds ExclusiveAreaRef to internal list
        """
        if isinstance(exclusive_area, str):
            self.exclusive_area.append(ExclusiveAreaRef(exclusive_area))
        elif isinstance(exclusive_area, ExclusiveAreaRef):
            self.exclusive_area.append(exclusive_area)
        else:
            raise ar_except.ElementTypeError("exclusive_area", ("ExclusiveAreaRef", "str"), exclusive_area)

    def ref(self) -> ExclusiveAreaNestingOrderRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ExclusiveAreaNestingOrderRef(ref_str)


class SwcExclusiveAreaPolicy(ARObject):
    """
    Complex type AR:SWC-EXCLUSIVE-AREA-POLICY
    Tag variants: 'SWC-EXCLUSIVE-AREA-POLICY'
    """

    def __init__(self,
                 exclusive_area: ExclusiveAreaRef | str | None = None,
                 api_principle: ar_enum.ApiPrinciple | str | None = None) -> None:
        # .EXCLUSIVE-AREA-REF
        self.exclusive_area: ExclusiveAreaRef | None = None
        # .API-PRINCIPLE
        self.api_principle: ar_enum.ApiPrinciple | None = None
        self._assign_optional("exclusive_area", exclusive_area, ExclusiveAreaRef)
        self._assign_optional("api_principle", api_principle, ar_enum.ApiPrinciple)


class IncludedDataTypeSet(ARObject):
    """
    Complex type AR:INCLUDED-DATA-TYPE-SET
    Tag variants: 'INCLUDED-DATA-TYPE-SET'
    """

    def __init__(self,
                 data_type: (AutosarDataTypeRef | list[AutosarDataTypeRef] |
                             str | list[str] | None) = None,
                 literal_prefix: str | None = None) -> None:
        super().__init__()
        # .DATA-TYPE-REFS
        self.data_type: list[AutosarDataTypeRef] = []
        # .LITERAL-PREFIX
        self.literal_prefix: str | None = None

        self._assign_optional_strict("literal_prefix", literal_prefix, str)

        if data_type is not None:
            if isinstance(data_type, (AutosarDataTypeRef, str)):
                self.append(data_type)
            elif isinstance(data_type, Iterable):
                for item in data_type:
                    self.append(item)
            else:
                raise TypeError(f"data_type: Invalid type {str(type(data_type))}")

    def append(self, data_type: AutosarDataTypeRef | str) -> None:
        """
        Adds AutosarDataTypeRef to internal list
        """
        if isinstance(data_type, str):
            self.data_type.append(AutosarDataTypeRef(data_type, ar_enum.IdentifiableSubTypes.AUTOSAR_DATA_TYPE))
        elif isinstance(data_type, AutosarDataTypeRef):
            self.data_type.append(data_type)
        else:
            raise ar_except.ElementTypeError("data_type", ("AutosarDataTypeRef", "str"), data_type)


class IncludedModeDeclarationGroupSet(ARObject):
    """
    Complex type AR:INCLUDED-MODE-DECLARATION-GROUP-SET
    Tag variants: 'INCLUDED-MODE-DECLARATION-GROUP-SET'
    """

    def __init__(self,
                 mode_declaration_group: (ModeDeclarationGroupRef | list[ModeDeclarationGroupRef] |
                                          str | list[str] | None) = None,
                 prefix: str | None = None) -> None:
        super().__init__()
        # .MODE-DECLARATION-GROUP-REFS
        self.mode_declaration_group: list[ModeDeclarationGroupRef] = []
        # .PREFIX
        self.prefix: str | None = None

        self._assign_optional_strict("prefix", prefix, str)

        if mode_declaration_group is not None:
            if isinstance(mode_declaration_group, (ModeDeclarationGroupRef, str)):
                self.append(mode_declaration_group)
            elif isinstance(mode_declaration_group, Iterable):
                for item in mode_declaration_group:
                    self.append(item)
            else:
                raise TypeError(f"mode_declaration_group: Invalid type {str(type(mode_declaration_group))}")

    def append(self, mode_declaration_group: ModeDeclarationGroupRef | str) -> None:
        """
        Adds ModeDeclarationGroupRef to internal list
        """
        if isinstance(mode_declaration_group, str):
            self.mode_declaration_group.append(ModeDeclarationGroupRef(mode_declaration_group))
        elif isinstance(mode_declaration_group, ModeDeclarationGroupRef):
            self.mode_declaration_group.append(mode_declaration_group)
        else:
            raise ar_except.ElementTypeError("mode_declaration_group",
                                             ("ModeDeclarationGroupRef", "str"),
                                             mode_declaration_group)


class InstantiationDataDefProps(ARObject):
    """
    Complex type AR:INSTANTIATION-DATA-DEF-PROPS
    Tag variants: 'INSTANTIATION-DATA-DEF-PROPS'
    """

    def __init__(self,
                 parameter_instance: AutosarParameterRef | None = None,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 variable_instance: AutosarVariableRef | None = None) -> None:
        super().__init__()
        # .PARAMETER-INSTANCE
        self.parameter_instance: AutosarParameterRef | None = None
        # .SW-DATA-DEF-PROPS
        self.sw_data_def_props: SwDataDefProps | None = None
        # .VARIABLE-INSTANCE
        self.variable_instance: AutosarVariableRef | None = None
        # .VARIATION-POINT --- NOT SUPPORTED (VARIANT)

        self._assign_optional_strict("parameter_instance",
                                     parameter_instance,
                                     AutosarParameterRef)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")
        self._assign_optional_strict("variable_instance",
                                     variable_instance,
                                     AutosarVariableRef)


class PerInstanceMemory(Identifiable):
    """
    Complex type AR:PER-INSTANCE-MEMORY
    Tag variants: 'PER-INSTANCE-MEMORY'
    """

    def __init__(self,
                 name: str,
                 init_value: str | None = None,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 type: str | None = None,  # pylint: disable=redefined-builtin
                 type_definition: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .INIT-VALUE
        self.init_value: str | None = None
        # .SW-DATA-DEF-PROPS
        self.sw_data_def_props: SwDataDefProps | None = None
        # .TYPE
        self.type: str | None = None
        # .TYPE-DEFINITION
        self.type_definition: str | None = None
        # .VARIATION-POINT --- NOT SUPPORTED (VARIANT)

        self._assign_optional_strict("init_value", init_value, str)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")
        self._assign_optional_strict("type", type, str)
        self._assign_optional_strict("type_definition", type_definition, str)

    def ref(self) -> PerInstanceMemoryRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else PerInstanceMemoryRef(ref_str)


class InternalBehavior(Identifiable):
    """
    Group AR:INTERNAL-BEHAVIOR
    """

    def __init__(self,
                 name: str,
                 constant_memory: ParameterDataPrototype | list[ParameterDataPrototype] | None = None,
                 constant_value_mapping: (str | ConstantSpecificationMappingSetRef |
                                          list[ConstantSpecificationMappingSetRef] | None) = None,
                 data_type_mapping: str | DataTypeMappingSetRef | list[DataTypeMappingSetRef] | None = None,
                 exclusive_area: ExclusiveArea | list[ExclusiveArea] | None = None,
                 exclusive_area_nesting_order: (ExclusiveAreaNestingOrder |
                                                list[ExclusiveAreaNestingOrder] | None) = None,
                 static_memory: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CONSTANT-MEMORYS
        self.constant_memory: list[ParameterDataPrototype] = []
        # .CONSTANT-VALUE-MAPPING-REFS
        self.constant_value_mapping: list[ConstantSpecificationMappingSetRef] = []
        # .DATA-TYPE-MAPPING-REFS
        self.data_type_mapping: list[DataTypeMappingSetRef] = []
        # .EXCLUSIVE-AREAS
        self.exclusive_area: list[ExclusiveArea] = []
        # .EXCLUSIVE-AREA-NESTING-ORDERS
        self.exclusive_area_nesting_order: list[ExclusiveAreaNestingOrder] = []
        # .STATIC-MEMORYS
        self.static_memory: list[VariableDataPrototype] = []

        if constant_memory is not None:
            if isinstance(constant_memory, Iterable):
                for item in constant_memory:
                    self.append_constant_memory(item)
            else:
                self.append_constant_memory(constant_memory)
        if constant_value_mapping is not None:
            if isinstance(constant_value_mapping, str):
                constant_value_mapping = ConstantSpecificationMappingSetRef(constant_value_mapping)
            if isinstance(constant_value_mapping, Iterable):
                for mapping_set in constant_value_mapping:
                    self.append_constant_value_mapping(mapping_set)
            else:
                self.append_constant_value_mapping(constant_value_mapping)
        if data_type_mapping is not None:
            if isinstance(data_type_mapping, str):
                data_type_mapping = DataTypeMappingSetRef(data_type_mapping)
            if isinstance(data_type_mapping, Iterable):
                for mapping_set in data_type_mapping:
                    self.append_data_type_mapping(mapping_set)
            else:
                self.append_data_type_mapping(data_type_mapping)
        if exclusive_area is not None:
            if isinstance(exclusive_area, Iterable):
                for item in exclusive_area:
                    self.append_exclusive_area(item)
            else:
                self.append_exclusive_area(exclusive_area)
        if exclusive_area_nesting_order is not None:
            if isinstance(exclusive_area_nesting_order, Iterable):
                for order in exclusive_area_nesting_order:
                    self.append_exclusive_area_nesting_order(order)
            else:
                self.append_exclusive_area_nesting_order(exclusive_area_nesting_order)
        if static_memory is not None:
            if isinstance(static_memory, Iterable):
                for item in static_memory:
                    self.append_static_memory(item)
            else:
                self.append_static_memory(static_memory)

    @convenience_function
    def create_constant_memory(self,
                               name: str,
                               init_value: ValueSpecificationElement | None = None,
                               **kwargs) -> ParameterDataPrototype:
        """
        Adds a new ParameterDataPrototype to constant_memory
        """
        item = ParameterDataPrototype(name, init_value, **kwargs)
        self.append_constant_memory(item)
        return item

    @convenience_function
    def create_static_memory(self,
                             name: str,
                             init_value: ValueSpecificationElement | None = None,
                             **kwargs) -> VariableDataPrototype:
        """
        Adds a new VariableDataPrototype to static_memory
        """
        item = VariableDataPrototype(name, init_value, **kwargs)
        self.append_static_memory(item)
        return item

    @convenience_function
    def create_exclusive_area(self, name: str, **kwargs) -> ExclusiveArea:
        """
        Adds a new ExclusiveArea to this object
        """
        exclusive_area = ExclusiveArea(name, **kwargs)
        self.append_exclusive_area(exclusive_area)
        return exclusive_area

    @convenience_function
    def create_exclusive_area_nesting_order(self,
                                            name: str,
                                            exclusive_area: (ExclusiveAreaRef | list[ExclusiveAreaRef] |
                                                             str | list[str] | None) = None,
                                            **kwargs) -> ExclusiveAreaNestingOrder:
        """
        Adds a new ExclusiveAreaNestingOrder to this object
        """
        order = ExclusiveAreaNestingOrder(name, exclusive_area, **kwargs)
        self.append_exclusive_area_nesting_order(order)
        return order

    def append_constant_memory(self, item: ParameterDataPrototype) -> None:
        """
        Appends ParameterDataPrototype to constant_memory
        """
        if isinstance(item, ParameterDataPrototype):
            self.constant_memory.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", ParameterDataPrototype, item)

    def append_static_memory(self, item: VariableDataPrototype) -> None:
        """
        Appends VariableDataPrototype to static_memory
        """
        if isinstance(item, VariableDataPrototype):
            self.static_memory.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", VariableDataPrototype, item)

    def append_constant_value_mapping(self, mapping_set: ConstantSpecificationMappingSetRef) -> None:
        """
        Appends ConstantSpecificationMappingSetRef to constant_value_mapping
        """
        if isinstance(mapping_set, ConstantSpecificationMappingSetRef):
            self.constant_value_mapping.append(mapping_set)
        else:
            raise ar_except.ElementTypeError("mapping_set", ConstantSpecificationMappingSetRef, mapping_set)

    def append_data_type_mapping(self, mapping_set: DataTypeMappingSetRef) -> None:
        """
        Appends DataTypeMappingSetRef to data_type_mapping
        """
        if isinstance(mapping_set, DataTypeMappingSetRef):
            self.data_type_mapping.append(mapping_set)
        else:
            raise ar_except.ElementTypeError("mapping_set", DataTypeMappingSetRef, mapping_set)

    def append_exclusive_area(self, exclusive_area: ExclusiveArea) -> None:
        """
        Appends ExclusiveArea to exclusive_area
        """
        if isinstance(exclusive_area, ExclusiveArea):
            self.exclusive_area.append(exclusive_area)
            exclusive_area.parent = self
        else:
            raise ar_except.ElementTypeError("exclusive_area", ExclusiveArea, exclusive_area)

    def append_exclusive_area_nesting_order(self, item: ExclusiveAreaNestingOrder) -> None:
        """
        Appends ExclusiveAreaNestingOrder to exclusive_area_nesting_order
        """
        if isinstance(item, ExclusiveAreaNestingOrder):
            self.exclusive_area_nesting_order.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", ExclusiveAreaNestingOrder, item)


ModeSwitchEventArgsReturnType = tuple[RequirePortPrototype, ModeDeclarationGroupPrototype, ModeDeclaration]


# pylint: disable=too-many-public-methods
class SwcInternalBehavior(InternalBehavior):
    """
    Complex type AR:SWC-INTERNAL-BEHAVIOR
    Tag variants: 'SWC-INTERNAL-BEHAVIOR'
    """

    def __init__(self,
                 name: str,
                 ar_typed_per_instance_memory: (VariableDataPrototype |
                                                list[VariableDataPrototype] | None) = None,
                 event: RteEvent | list[RteEvent] | None = None,
                 exclusive_area_policy: (SwcExclusiveAreaPolicy |
                                         list[SwcExclusiveAreaPolicy] | None) = None,
                 explicit_inter_runnable_variable: (VariableDataPrototype |
                                                    list[VariableDataPrototype] | None) = None,
                 handle_termination_and_restart: ar_enum.HandleTerminationAndRestart | None = None,
                 implicit_inter_runnable_variable: (VariableDataPrototype |
                                                    list[VariableDataPrototype] | None) = None,
                 included_data_type_set: (IncludedDataTypeSet |
                                          list[IncludedDataTypeSet] | None) = None,
                 included_mode_declaration_group_set: (IncludedModeDeclarationGroupSet |
                                                       list[IncludedModeDeclarationGroupSet] | None) = None,
                 instantiation_data_def_props: (InstantiationDataDefProps |
                                                list[InstantiationDataDefProps] | None) = None,
                 per_instance_memory: (PerInstanceMemory |
                                       list[PerInstanceMemory] | None) = None,
                 per_instance_parameter: (ParameterDataPrototype |
                                          list[ParameterDataPrototype] | None) = None,
                 port_api_option: PortApiOption | list[PortApiOption] | None = None,
                 runnable: RunnableEntity | list[RunnableEntity] | None = None,
                 service_dependency: (SwcServiceDependency |
                                      list[SwcServiceDependency] | None) = None,
                 shared_parameter: (ParameterDataPrototype |
                                    list[ParameterDataPrototype] | None) = None,
                 supports_multiple_instantiation: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .AR-TYPED-PER-INSTANCE-MEMORYS
        self.ar_typed_per_instance_memory: list[VariableDataPrototype] = []
        # .EVENTS
        self.event: list[RteEvent] = []
        # .EXCLUSIVE-AREA-POLICYS
        self.exclusive_area_policy: list[SwcExclusiveAreaPolicy] = []
        # .EXPLICIT-INTER-RUNNABLE-VARIABLES
        self.explicit_inter_runnable_variable: list[VariableDataPrototype] = []
        # .HANDLE-TERMINATION-AND-RESTART
        self.handle_termination_and_restart: ar_enum.HandleTerminationAndRestart | None = None
        # .IMPLICIT-INTER-RUNNABLE-VARIABLES
        self.implicit_inter_runnable_variable: list[VariableDataPrototype] = []
        # .INCLUDED-DATA-TYPE-SETS
        self.included_data_type_set: list[IncludedDataTypeSet] = []
        # .INCLUDED-MODE-DECLARATION-GROUP-SETS
        self.included_mode_declaration_group_set: list[IncludedModeDeclarationGroupSet] = []
        # .INSTANTIATION-DATA-DEF-PROPSS
        self.instantiation_data_def_props: list[InstantiationDataDefProps] = []
        # .PER-INSTANCE-MEMORYS
        self.per_instance_memory: list[PerInstanceMemory] = []
        # .PER-INSTANCE-PARAMETERS
        self.per_instance_parameter: list[ParameterDataPrototype] = []
        # .PORT-API-OPTIONS
        self.port_api_option: OrderedDict[PortApiOption] = OrderedDict()
        # .RUNNABLES
        self.runnable: list[RunnableEntity] = []
        # .SERVICE-DEPENDENCYS
        self.service_dependency: list[SwcServiceDependency] = []
        # .SHARED-PARAMETERS
        self.shared_parameter: list[ParameterDataPrototype] = []
        # .SUPPORTS-MULTIPLE-INSTANTIATION
        self.supports_multiple_instantiation: bool | None = None
        # .VARIATION-POINT-PROXYS --- NOT SUPPORTED (VARIANT)
        # .VARIATION-POINT --- NOT SUPPORTED (VARIANT)

        self._assign_optional("handle_termination_and_restart",
                              handle_termination_and_restart,
                              ar_enum.HandleTerminationAndRestart)
        self._assign_optional("supports_multiple_instantiation",
                              supports_multiple_instantiation,
                              bool)

        if ar_typed_per_instance_memory is not None:
            if isinstance(ar_typed_per_instance_memory, Iterable):
                for item in ar_typed_per_instance_memory:
                    self.append_ar_typed_per_instance_memory(item)
            else:
                self.append_ar_typed_per_instance_memory(ar_typed_per_instance_memory)

        if event is not None:
            if isinstance(event, Iterable):
                for item in event:
                    self.append_event(item)
            else:
                self.append_event(event)

        if exclusive_area_policy is not None:
            if isinstance(exclusive_area_policy, Iterable):
                for item in exclusive_area_policy:
                    self.append_exclusive_area_policy(item)
            else:
                self.append_exclusive_area_policy(exclusive_area_policy)

        if explicit_inter_runnable_variable is not None:
            if isinstance(explicit_inter_runnable_variable, Iterable):
                for item in explicit_inter_runnable_variable:
                    self.append_explicit_inter_runnable_variable(item)
            else:
                self.append_explicit_inter_runnable_variable(explicit_inter_runnable_variable)

        if implicit_inter_runnable_variable is not None:
            if isinstance(implicit_inter_runnable_variable, Iterable):
                for item in implicit_inter_runnable_variable:
                    self.append_implicit_inter_runnable_variable(item)
            else:
                self.append_implicit_inter_runnable_variable(implicit_inter_runnable_variable)

        if included_data_type_set is not None:
            if isinstance(included_data_type_set, Iterable):
                for item in included_data_type_set:
                    self.append_included_data_type_set(item)
            else:
                self.append_included_data_type_set(included_data_type_set)

        if included_mode_declaration_group_set is not None:
            if isinstance(included_mode_declaration_group_set, Iterable):
                for item in included_mode_declaration_group_set:
                    self.append_included_mode_declaration_group_set(item)
            else:
                self.append_included_mode_declaration_group_set(included_mode_declaration_group_set)

        if instantiation_data_def_props is not None:
            if isinstance(instantiation_data_def_props, Iterable):
                for item in instantiation_data_def_props:
                    self.append_instantiation_data_def_props(item)
            else:
                self.append_instantiation_data_def_props(instantiation_data_def_props)

        if port_api_option is not None:
            if isinstance(port_api_option, Iterable):
                for item in port_api_option:
                    self.append_port_api_option(item)
            else:
                self.append_port_api_option(port_api_option)

        if runnable is not None:
            if isinstance(runnable, Iterable):
                for item in runnable:
                    self.append_runnable(item)
            else:
                self.append_runnable(runnable)

        if service_dependency is not None:
            if isinstance(service_dependency, Iterable):
                for item in service_dependency:
                    self.append_service_dependency(item)
            else:
                self.append_service_dependency(service_dependency)

        if per_instance_memory is not None:
            if isinstance(per_instance_memory, Iterable):
                for item in per_instance_memory:
                    self.append_per_instance_memory(item)
            else:
                self.append_per_instance_memory(per_instance_memory)

        if per_instance_parameter is not None:
            if isinstance(per_instance_parameter, Iterable):
                for item in per_instance_parameter:
                    self.append_per_instance_parameter(item)
            else:
                self.append_per_instance_parameter(per_instance_parameter)

        if shared_parameter is not None:
            if isinstance(shared_parameter, Iterable):
                for item in shared_parameter:
                    self.append_shared_parameter(item)
            else:
                self.append_shared_parameter(shared_parameter)

    def get_valid_parent(self) -> SwComponentType:
        """
        Verifies that this object has valid SoftwareComponent as parent before returning it
        """
        if self.parent is None or not isinstance(self.parent, SwComponentType):
            raise builtins.RuntimeError("Behavior object doesn't have a valid parent")
        return self.parent

    def get_valid_behavior_settings(self) -> BehaviorSettings:
        """
        Verifies that the root collection has a valid behavior_settings object and returns it
        """
        swc = self.get_valid_parent()
        workspace = swc.root_collection()
        if workspace is None:
            raise builtins.RuntimeError("Workspace object not found")
        if workspace.behavior_settings is None:
            raise builtins.RuntimeError("behavior_settings object not found in workspace")
        return workspace.behavior_settings

    def ref(self) -> SwcInternalBehaviorRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwcInternalBehaviorRef(ref_str)

    @convenience_function
    def create_ar_typed_per_instance_memory(self,
                                            name: str,
                                            init_value: ValueSpecificationElement | None = None,
                                            **kwargs) -> VariableDataPrototype:
        """
        Adds a new VariableDataPrototype to ar_typed_per_instance_memory
        """
        item = VariableDataPrototype(name, init_value, **kwargs)
        self.append_ar_typed_per_instance_memory(item)
        return item

    def append_ar_typed_per_instance_memory(self, item: VariableDataPrototype) -> None:
        """
        Appends VariableDataPrototype to ar_typed_per_instance_memory
        """
        if isinstance(item, VariableDataPrototype):
            self.ar_typed_per_instance_memory.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", VariableDataPrototype, item)

    @convenience_function
    def create_explicit_inter_runnable_variable(self,
                                                name: str,
                                                init_value: ValueSpecificationElement | None = None,
                                                **kwargs) -> VariableDataPrototype:
        """
        Adds a new VariableDataPrototype to explicit_inter_runnable_variable
        """
        item = VariableDataPrototype(name, init_value, **kwargs)
        self.append_explicit_inter_runnable_variable(item)
        return item

    def append_explicit_inter_runnable_variable(self, item: VariableDataPrototype) -> None:
        """
        Appends VariableDataPrototype to explicit_inter_runnable_variable
        """
        if isinstance(item, VariableDataPrototype):
            self.explicit_inter_runnable_variable.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", VariableDataPrototype, item)

    @convenience_function
    def create_implicit_inter_runnable_variable(self,
                                                name: str,
                                                init_value: ValueSpecificationElement | None = None,
                                                **kwargs) -> VariableDataPrototype:
        """
        Adds a new VariableDataPrototype to implicit_inter_runnable_variable
        """
        item = VariableDataPrototype(name, init_value, **kwargs)
        self.append_implicit_inter_runnable_variable(item)
        return item

    def append_implicit_inter_runnable_variable(self, item: VariableDataPrototype) -> None:
        """
        Appends VariableDataPrototype to implicit_inter_runnable_variable
        """
        if isinstance(item, VariableDataPrototype):
            self.implicit_inter_runnable_variable.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", VariableDataPrototype, item)

    @convenience_function
    def create_exclusive_area_policy(self,
                                     exclusive_area: ExclusiveAreaRef | str | None = None,
                                     api_principle: ar_enum.ApiPrinciple | str | None = None
                                     ) -> SwcExclusiveAreaPolicy:
        """
        Adds a new SwcExclusiveAreaPolicy to exclusive_area_policy
        """
        policy = SwcExclusiveAreaPolicy(exclusive_area, api_principle)
        self.append_exclusive_area_policy(policy)
        return policy

    def append_exclusive_area_policy(self, item: SwcExclusiveAreaPolicy) -> None:
        """
        Appends SwcExclusiveAreaPolicy to exclusive_area_policy
        """
        if isinstance(item, SwcExclusiveAreaPolicy):
            self.exclusive_area_policy.append(item)
        else:
            raise ar_except.ElementTypeError("item", SwcExclusiveAreaPolicy, item)

    @convenience_function
    def create_included_data_type_set(self,
                                      data_type: (AutosarDataTypeRef | list[AutosarDataTypeRef] |
                                                  str | list[str] | None) = None,
                                      literal_prefix: str | None = None
                                      ) -> IncludedDataTypeSet:
        """
        Adds a new IncludedDataTypeSet to included_data_type_set
        """
        item = IncludedDataTypeSet(data_type=data_type, literal_prefix=literal_prefix)
        self.append_included_data_type_set(item)
        return item

    def append_included_data_type_set(self, item: IncludedDataTypeSet) -> None:
        """
        Appends IncludedDataTypeSet to included_data_type_set
        """
        if isinstance(item, IncludedDataTypeSet):
            self.included_data_type_set.append(item)
        else:
            raise ar_except.ElementTypeError("item", IncludedDataTypeSet, item)

    @convenience_function
    def create_included_mode_declaration_group_set(self,
                                                   mode_declaration_group: (ModeDeclarationGroupRef |
                                                                            list[ModeDeclarationGroupRef] |
                                                                            str | list[str] | None) = None,
                                                   prefix: str | None = None
                                                   ) -> IncludedModeDeclarationGroupSet:
        """
        Adds a new IncludedModeDeclarationGroupSet to included_mode_declaration_group_set
        """
        item = IncludedModeDeclarationGroupSet(mode_declaration_group=mode_declaration_group, prefix=prefix)
        self.append_included_mode_declaration_group_set(item)
        return item

    def append_included_mode_declaration_group_set(self, item: IncludedModeDeclarationGroupSet) -> None:
        """
        Appends IncludedModeDeclarationGroupSet to included_mode_declaration_group_set
        """
        if isinstance(item, IncludedModeDeclarationGroupSet):
            self.included_mode_declaration_group_set.append(item)
        else:
            raise ar_except.ElementTypeError("item", IncludedModeDeclarationGroupSet, item)

    @convenience_function
    def create_instantiation_data_def_props(self,
                                            parameter_instance: AutosarParameterRef | None = None,
                                            sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                                            variable_instance: AutosarVariableRef | None = None
                                            ) -> InstantiationDataDefProps:
        """
        Adds a new InstantiationDataDefProps to instantiation_data_def_props
        """
        item = InstantiationDataDefProps(parameter_instance=parameter_instance,
                                         sw_data_def_props=sw_data_def_props,
                                         variable_instance=variable_instance)
        self.append_instantiation_data_def_props(item)
        return item

    def append_instantiation_data_def_props(self, item: InstantiationDataDefProps) -> None:
        """
        Appends InstantiationDataDefProps to instantiation_data_def_props
        """
        if isinstance(item, InstantiationDataDefProps):
            self.instantiation_data_def_props.append(item)
        else:
            raise ar_except.ElementTypeError("item", InstantiationDataDefProps, item)

    @convenience_function
    def create_per_instance_memory(self,
                                   name: str,
                                   init_value: str | None = None,
                                   sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                                   type: str | None = None,  # pylint: disable=redefined-builtin
                                   type_definition: str | None = None,
                                   **kwargs) -> PerInstanceMemory:
        """
        Adds a new PerInstanceMemory to per_instance_memory
        """
        item = PerInstanceMemory(name,
                                 init_value=init_value,
                                 sw_data_def_props=sw_data_def_props,
                                 type=type,
                                 type_definition=type_definition,
                                 **kwargs)
        self.append_per_instance_memory(item)
        return item

    def append_per_instance_memory(self, item: PerInstanceMemory) -> None:
        """
        Appends PerInstanceMemory to per_instance_memory
        """
        if isinstance(item, PerInstanceMemory):
            self.per_instance_memory.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", PerInstanceMemory, item)

    @convenience_function
    def create_per_instance_parameter(self,
                                      name: str,
                                      init_value: ValueSpecificationElement | None = None,
                                      **kwargs) -> ParameterDataPrototype:
        """
        Adds a new ParameterDataPrototype to per_instance_parameter
        """
        item = ParameterDataPrototype(name, init_value, **kwargs)
        self.append_per_instance_parameter(item)
        return item

    def append_per_instance_parameter(self, item: ParameterDataPrototype) -> None:
        """
        Appends ParameterDataPrototype to per_instance_parameter
        """
        if isinstance(item, ParameterDataPrototype):
            self.per_instance_parameter.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", ParameterDataPrototype, item)

    @convenience_function
    def create_shared_parameter(self,
                                name: str,
                                init_value: ValueSpecificationElement | None = None,
                                **kwargs) -> ParameterDataPrototype:
        """
        Adds a new ParameterDataPrototype to shared_parameter
        """
        item = ParameterDataPrototype(name, init_value, **kwargs)
        self.append_shared_parameter(item)
        return item

    def append_shared_parameter(self, item: ParameterDataPrototype) -> None:
        """
        Appends ParameterDataPrototype to shared_parameter
        """
        if isinstance(item, ParameterDataPrototype):
            self.shared_parameter.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", ParameterDataPrototype, item)

    def append_runnable(self, runnable: RunnableEntity) -> None:
        """
        Adds runnable to internal list of runnables
        """
        if isinstance(runnable, RunnableEntity):
            runnable.parent = self
            self.runnable.append(runnable)
        else:
            raise TypeError(f"runnable must be of type RunnableEntity. Got {str(type(runnable))}")

    @convenience_function
    def create_service_dependency(self,
                                  name: str,
                                  assigned_datas: (RoleBasedDataAssignment |
                                                   list[RoleBasedDataAssignment] |
                                                   None) = None,
                                  assigned_ports: (RoleBasedPortAssignment |
                                                   list[RoleBasedPortAssignment] |
                                                   None) = None,
                                  represented_port_group_ref: PortGroupRef | str | None = None,
                                  service_needs: ServiceNeeds | None = None,
                                  **kwargs) -> SwcServiceDependency:
        """
        Adds a new SwcServiceDependency to service_dependency
        """
        item = SwcServiceDependency(name,
                                    assigned_datas=assigned_datas,
                                    assigned_ports=assigned_ports,
                                    represented_port_group_ref=represented_port_group_ref,
                                    service_needs=service_needs,
                                    **kwargs)
        self.append_service_dependency(item)
        return item

    def append_service_dependency(self, item: SwcServiceDependency) -> None:
        """
        Appends SwcServiceDependency to service_dependency
        """
        if isinstance(item, SwcServiceDependency):
            self.service_dependency.append(item)
            item.parent = self
        else:
            raise ar_except.ElementTypeError("item", SwcServiceDependency, item)

    def append_event(self, event: RteEvent) -> None:
        """
        Adds event to internal list of events
        """
        if isinstance(event, RteEvent):
            event.parent = self
            self.event.append(event)
        else:
            raise TypeError(f"event must derive from RteEvent. Got {str(type(event))}")

    def append_port_api_option(self, element: PortApiOption) -> None:
        """
        Generation options for port-related calls in the RTE.
        """
        if isinstance(element, PortApiOption):
            if element.port is not None:
                parts = str(element.port).split("/")
                self.port_api_option[parts[-1]] = element
        else:
            raise TypeError(f"element: Expected type PortApiOption, got '{str(type(element))}'")

    @convenience_function
    def create_runnable(self,
                        name: str,
                        can_be_invoked_concurrently: bool | None = None,
                        minimum_start_interval: int | float | None = None,
                        symbol: str | None = "",
                        activation_reasons: ActivationReasonArgumentType = None,
                        can_enter_leave: CanEnterLeaveArgumentType = None,
                        exclusive_area_nesting_order: ExclusiveAreaNestingOrderArgumentType = None,
                        reentrancy_level: ar_enum.ReentrancyLevel | None = None,
                        runs_insides: RunsInsidesArgumentType = None,
                        sw_addr_method: str | SwAddrMethodRef | None = None,
                        **kwargs) -> RunnableEntity:
        """
        Adds a new RunnableEntity to this behavior object

        symbol: If the symbol argument is an empty string (default value), it will generate a symbol
                identcal to the the name argument.
                If you don't want a symbol at all, explicitly pass the value None as argument for symbol.

        can_enter_leave: If argument type is str or list[str] then it expects each string to be the
                         short-name of an existing exclusive area.
        """
        if isinstance(symbol, str) and len(symbol) == 0:
            symbol = name
        if can_enter_leave is not None:
            names: dict[str, bool] = {}
            if isinstance(can_enter_leave, str):
                names[can_enter_leave] = False
            elif isinstance(can_enter_leave, Iterable):
                for elem in can_enter_leave:
                    if isinstance(elem, str):
                        names[elem] = False
            if names:
                exclusive_area_refs: ExclusiveAreaRef = []
                for area in self.exclusive_area:
                    if area.name in names:
                        names[area.name] = True  # Marks it as handled
                        exclusive_area_refs.append(area.ref())
                for key, value in names.items():
                    if not value:
                        raise ValueError(f"can_enter_leave: '{key}' does not name an exclusive area in "
                                         "this SwcInternalBehavior object")
                can_enter_leave = exclusive_area_refs

        data = {"can_be_invoked_concurrently": can_be_invoked_concurrently,
                "minimum_start_interval": minimum_start_interval,
                "symbol": symbol,
                "activation_reasons": activation_reasons,
                "can_enter_leave": can_enter_leave,
                "exclusive_area_nesting_order": exclusive_area_nesting_order,
                "reentrancy_level": reentrancy_level,
                "runs_insides": runs_insides,
                "sw_addr_method": sw_addr_method
                }
        data.update(kwargs)
        runnable = RunnableEntity(name, **data)
        self.append_runnable(runnable)
        runnable.parent = self
        return runnable

    def find_runnable(self, name: str) -> RunnableEntity | None:
        """
        Find runnable by name. Returns None if no runnable is found.
        """
        for runnable in self.runnable:
            if runnable.name == name:
                return runnable
        return None

    def _make_unique_event_name(self, event_name: str) -> str:
        """
        Checks if event_name is unique in internal event list.
        If not, then it automatically starts to add an integer-based name suffix ("_0", "_1" etc.).
        Calling this function could potentially invalidate existing event references.
        Note: Not yet implemented
        """
        return make_unique_name_in_list(self.event, event_name)

    @convenience_function
    def create_background_event(self,
                                runnable_name: str,
                                event_name: str | None = None,
                                **kwargs
                                ) -> BackgroundEvent:
        """
        Adds a new BackgroundEvent to this SwcInternalBehavior object.
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.background_event_prefix:
                event_name = behavior_settings.background_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " background_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = BackgroundEvent(unique_event_name, runnable.ref(), **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_data_receive_error_event(self,
                                        runnable_name: str,
                                        port_data_element: str,
                                        event_name: str | None = None,
                                        **kwargs
                                        ) -> DataReceiveErrorEvent:
        """
        Adds a new DataReceiveErrorEvent to this SwcInternalBehavior object
        port_data_element is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(port_data_element)
        if len(name_parts) == 1:
            port_name, data_element_name = name_parts[0], None
        else:
            port_name, data_element_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"port_data_element: '{port_data_element}' does not name an existing R-PORT or PR-PORT")
        target_data_element = swc.get_data_element_in_port(context_port, data_element_name)
        if target_data_element is None:
            msg = f"port_data_element: '{port_data_element}' does not name an existing data element in port interface"
            raise ValueError(msg)
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.data_receive_error_event_prefix:
                event_name = "_".join([behavior_settings.data_receive_error_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       target_data_element.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " data_receive_error_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = DataReceiveErrorEvent.make(unique_event_name,
                                           runnable.ref(),
                                           context_port.ref(),
                                           target_data_element.ref(),
                                           **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_data_received_event(self,
                                   runnable_name: str,
                                   data_element_ref: str,
                                   event_name: str | None = None,
                                   **kwargs
                                   ) -> DataReceivedEvent:
        """
        Adds a new DataReceivedEvent to this SwcInternalBehavior object
        data_element_ref is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(data_element_ref)
        if len(name_parts) == 1:
            port_name, data_element_name = name_parts[0], None
        else:
            port_name, data_element_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"data_element_ref: '{data_element_ref}' does not name an existing R-PORT or PR-PORT")
        target_data_element = swc.get_data_element_in_port(context_port, data_element_name)
        if target_data_element is None:
            msg = f"data_element_ref: '{data_element_ref}' does not name an existing data element in port interface"
            raise ValueError(msg)
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.data_receive_event_prefix:
                event_name = "_".join([behavior_settings.data_receive_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       target_data_element.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " data_receive_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = DataReceivedEvent.make(unique_event_name,
                                       runnable.ref(),
                                       context_port.ref(),
                                       target_data_element.ref(),
                                       **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_data_send_completed_event(self,
                                         runnable_name: str,
                                         data_element_ref: str,
                                         event_name: str | None = None,
                                         **kwargs
                                         ) -> DataSendCompletedEvent:
        """
        Adds a new DataSendCompletedEvent to this SwcInternalBehavior object
        data_element_ref is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.
        The given runnable must have a data send point referencing the port and data element.
        Note: Unable to complete implementation. Requires support for port-access in runnables.
        """
        raise NotImplementedError("References to data send points are not yet supported")

    @convenience_function
    def create_data_write_completed_event(self,
                                          runnable_name: str,
                                          data_element_ref: str,
                                          event_name: str | None = None,
                                          **kwargs
                                          ) -> DataWriteCompletedEvent:
        """
        Adds a new DataWriteCompletedEvent to this SwcInternalBehavior object
        data_element_ref is a string with format '<PortName>/<DataElementName>' or
        just '<PortName>' which can be used in the special situation when the port interface
        only has a single data element.
        The given runnable must have a data send point referencing the port and data element.
        Note: Not implemented due to lack of support for data write access
        """
        raise NotImplementedError("References to data write access are not yet supported")

    @convenience_function
    def create_init_event(self,
                          runnable_name: str,
                          event_name: str | None = None,
                          **kwargs
                          ) -> InitEvent:
        """
        Adds a new InitEvent to this SwcInternalBehavior object
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.init_event_prefix:
                event_name = behavior_settings.init_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " init_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = InitEvent(unique_event_name, runnable.ref(), **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_operation_invoked_event(self,
                                       runnable_name: str,
                                       operation_ref: str,
                                       event_name: str | None = None,
                                       **kwargs
                                       ) -> OperationInvokedEvent:
        """
        Adds a new OperationInvokedEvent to this object
        operation_ref is a string with format <PortName>/<OperationName>
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(operation_ref)
        if len(name_parts) == 1:
            port_name, operation_name = name_parts[0], None
        else:
            port_name, operation_name = name_parts[0], name_parts[1]
        context_port = swc.find_p_port(port_name)
        if context_port is None:
            raise ValueError(f"port_name: '{port_name}' does not name an existing P-PORT or PR-PORT")
        target_provided_operation = swc.get_operation_in_port(context_port, operation_name)
        if target_provided_operation is None:
            raise ValueError(f"operation_ref: '{operation_ref}' does not name a valid operation in port interface")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.operation_invoked_event_prefix:
                event_name = "_".join([behavior_settings.operation_invoked_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       target_provided_operation.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " operation_invoked_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = OperationInvokedEvent.make(unique_event_name,
                                           runnable.ref(),
                                           context_port.ref(),
                                           target_provided_operation.ref(),
                                           **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_os_task_execution_event(self,
                                       runnable_name: str,
                                       event_name: str | None = None,
                                       **kwargs
                                       ) -> OsTaskExecutionEvent:
        """
        Adds a new OsTaskExecutionEvent to this SwcInternalBehavior object
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.os_task_execution_event_prefix:
                event_name = behavior_settings.os_task_execution_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " os_task_execution_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = OsTaskExecutionEvent(unique_event_name, runnable.ref(), **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_swc_mode_manager_error_event(self,
                                            runnable_name: str,
                                            port_name: str,
                                            event_name: str | None = None,
                                            **kwargs
                                            ) -> SwcModeManagerErrorEvent:
        """
        Adds a new SwcModeManagerErrorEvent to this object
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        context_port = swc.find_p_port(port_name)
        if context_port is None:
            raise ValueError(f"port_name: '{port_name}' does not name an existing P-PORT or PR-PORT")
        context_mode_declaration_group = swc.get_mode_declaration_group_in_port(context_port)
        if context_mode_declaration_group is None:
            msg = f"port_name: '{port_name}' does not name a valid ModeDeclarationGroupPrototype in port interface"
            raise ValueError(msg)
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.swc_mode_manager_error_event_prefix:
                event_name = "_".join([behavior_settings.swc_mode_manager_error_event_prefix,
                                       runnable_name,
                                       context_port.name,
                                       context_mode_declaration_group.name])
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " swc_mode_manager_error_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = SwcModeManagerErrorEvent.make(unique_event_name,
                                              runnable.ref(),
                                              context_port.ref(),
                                              context_mode_declaration_group.ref(),
                                              **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_swc_mode_mode_switch_event(self,
                                          runnable_name: str,
                                          mode_ref: str | list[str] | tuple[str, str],
                                          activation: ar_enum.ModeActivationKind | None = None,
                                          event_name: str | None = None,
                                          **kwargs
                                          ) -> SwcModeSwitchEvent:
        """
        Adds a new SwcModeSwitchEvent to this SwcInternalBehavior object.
        mode_ref is a string with format '<PortName>/<ModeDeclarationName>'.
        mode_ref can also be a 2-element list or a 2-tuple containing strings with same format as above.
        The second version is used for creating events for specific mode transitions.
        """
        swc = self.get_valid_parent()
        workspace = swc.root_collection()
        assert workspace is not None
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.swc_mode_switch_event_prefix:
                event_name = behavior_settings.swc_mode_switch_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " swc_mode_switch_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        expected_formats = "Expected formats: '<PortName>', '<PortName>/<ModeDeclarationName>', tuple[str, str]"
        if isinstance(mode_ref, str):
            if len(mode_ref) == 0:
                raise ValueError("mode_ref: Invalid argument. " + expected_formats)
            context_port, context_mode_declaration_group, target_mode_declaration = (
                self._get_swc_mode_switch_event_args(workspace, swc, mode_ref))
            event = SwcModeSwitchEvent.make(unique_event_name,
                                            runnable.ref(),
                                            activation,
                                            context_port.ref(),
                                            context_mode_declaration_group.ref(),
                                            target_mode_declaration.ref(),
                                            **kwargs)
        elif isinstance(mode_ref, (list, tuple)):
            if len(mode_ref) != 2:
                raise ValueError("mode_ref: Must be exactly two elements in tuple or list")
            instance_refs = []
            for ref in mode_ref:
                if isinstance(ref, str):
                    if len(ref) == 0:
                        raise ValueError("mode_ref: Invalid argument. " + expected_formats)
                    context_port, context_mode_declaration_group, target_mode_declaration = (
                        self._get_swc_mode_switch_event_args(workspace, swc, ref))
                    instance_refs.append(RModeInAtomicSwcInstanceRef(context_port.ref(),
                                                                     context_mode_declaration_group.ref(),
                                                                     target_mode_declaration.ref()))
                else:
                    raise TypeError(f"mode_ref: Invalid type '{str(type(ref))}'. " + expected_formats)
            event = SwcModeSwitchEvent(unique_event_name,
                                       runnable.ref(),
                                       activation,
                                       (instance_refs[0], instance_refs[1]),
                                       **kwargs)
        else:
            raise TypeError(f"mode_ref: Unsupported type '{str(type(mode_ref))}'")
        self.append_event(event)
        return event

    @convenience_function
    def create_timing_event(self,
                            runnable_name: str,
                            period: int | float | None = None,
                            offset: int | float | None = None,
                            event_name: str | None = None,
                            **kwargs) -> TimingEvent:
        """
        Adds a new TimingEvent to this object
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.timing_event_prefix:
                event_name = behavior_settings.timing_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " timing_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event = TimingEvent(unique_event_name, runnable.ref(), period, offset, **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_external_trigger_event(self,
                                      runnable_name: str,
                                      trigger_ref: str,
                                      event_name: str | None = None,
                                      **kwargs
                                      ) -> ExternalTriggerOccurredEvent:
        """
        Adds a new ExternalTriggerOccurredEvent to this SwcInternalBehavior object
        """
        swc = self.get_valid_parent()
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        name_parts = split_ref_strict(trigger_ref)
        if len(name_parts) == 1:
            port_name, trigger_name = name_parts[0], None
        else:
            port_name, trigger_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"port_name: '{port_name}' does not name an existing P-PORT or PR-PORT")
        target_trigger = swc.get_trigger_in_port(context_port, trigger_name)
        if target_trigger is None:
            raise ValueError(f"trigger_ref: '{trigger_ref}' does not name a valid trigger in port interface")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.external_trigger_event_prefix:
                event_name = behavior_settings.external_trigger_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " external_trigger_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        instance_ref = RTriggerInAtomicSwcInstanceRef(context_port.ref(), target_trigger.ref())
        event = ExternalTriggerOccurredEvent(unique_event_name, runnable.ref(), instance_ref, **kwargs)
        self.append_event(event)
        return event

    @convenience_function
    def create_internal_trigger_event(self,
                                      runnable_name: str,
                                      source_name: str,
                                      event_name: str | None = None,
                                      **kwargs
                                      ) -> InternalTriggerOccurredEvent:
        """
        Adds a new InternalTriggerOccurredEvent to this SwcInternalBehavior object
        """
        runnable = self.find_runnable(runnable_name)
        if runnable is None:
            raise KeyError(f"Found no runnable with name '{runnable_name}'")
        if event_name is None:
            behavior_settings = self.get_valid_behavior_settings()
            if behavior_settings.internal_trigger_event_prefix:
                event_name = behavior_settings.internal_trigger_event_prefix + "_" + runnable_name
            else:
                msg = "event_name: Unable to dynamically create event name,"\
                      " internal_trigger_event_prefix is not set in behavior settings"
                raise builtins.RuntimeError(msg)
        assert isinstance(event_name, str)
        unique_event_name = self._make_unique_event_name(event_name)
        event_source_ref = self._find_internal_trigger_point(source_name)
        if event_source_ref is None:
            msg = f"source_name: '{source_name}' does not name a valid internal trigger point in this object"
            raise ValueError(msg)
        event = InternalTriggerOccurredEvent(unique_event_name, runnable.ref(), event_source_ref, **kwargs)
        self.append_event(event)
        return event

    def _get_swc_mode_switch_event_args(self,
                                        workspace: PackageCollection,
                                        swc: AtomicSoftwareComponentType,
                                        mode_ref: str
                                        ) -> ModeSwitchEventArgsReturnType:
        """
        Helper function for create_swc_mode_switch_event
        """
        name_parts = split_ref_strict(mode_ref)
        if len(name_parts) != 2:
            raise ValueError("mode_ref: Formatting error, expected <PortName>/<ModeDeclarationName>")
        port_name, mode_declaration_name = name_parts[0], name_parts[1]
        context_port = swc.find_r_port(port_name)
        if context_port is None:
            raise ValueError(f"mode_ref: '{mode_ref}' does not name an existing R-PORT or PR-PORT")
        context_mode_declaration_group = swc.get_mode_declaration_group_in_port(context_port)
        if context_mode_declaration_group is None:
            msg = f"mode_ref: '{mode_ref}' does not name a valid ModeDeclarationGroupPrototype in port interface"
            raise ValueError(msg)
        target_mode_declaration_group: ModeDeclarationGroup | None
        target_mode_declaration_group = workspace.find(context_mode_declaration_group.type_ref)
        if target_mode_declaration_group is None:
            raise ar_except.InvalidReferenceError(str(context_mode_declaration_group.type_ref))
        target_mode_declaration: ModeDeclaration | None = target_mode_declaration_group.find(mode_declaration_name)
        if target_mode_declaration is None:
            raise ValueError(f"mode_ref: '{mode_ref}' does not name a valid mode declaration in ModeDeclarationGroup")
        return context_port, context_mode_declaration_group, target_mode_declaration

    def _find_internal_trigger_point(self, trigger_point_name: str) -> InternalTriggeringPointRef | None:
        """
        Helper function for create_internal_trigger_event
        """
        for runnable in self.runnable:
            for trigger_point in runnable.internal_triggering_point:
                if trigger_point.name == trigger_point_name:
                    return trigger_point.ref()
        return None

    @convenience_function
    def create_port_api_options(self,
                                port_name: str | list[str],
                                enable_take_address: bool | None = None,
                                indirect_api: bool | None = None,
                                error_handling: ar_enum.DataTransformationErrorHandling | None = None,
                                port_arg_values: PortDefinedArgumentValueArgType = None,
                                supported_features: SwcSupportedFeatureArgType = None,
                                transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None
                                ) -> None:
        """
        Creates and adds new PortApiOptions to this SwcInternalBehavior object

        port_name: Name of the port to create options for. It can also be a list of names in case you want to use
                   identical options for multiple ports.
                   Special value is "*" which creates one options object per port found in parent SWC.
        """
        swc = self.get_valid_parent()
        # names of ports to process.
        # The bool is used to check if it has been handled or not
        ports_to_process: dict[str, bool] = {}
        if isinstance(port_name, str):
            if port_name == "*":
                for port in swc.ports:
                    ports_to_process[port.name] = False
            else:
                ports_to_process[port_name] = False
        elif isinstance(port_name, Iterable):
            for name in port_name:
                ports_to_process[name] = False
        else:
            raise TypeError(f"port_name: Expected type string or list of string. Got {str(type(port_name))}")
        if len(ports_to_process):
            for port in sorted(swc.ports, key=lambda x: x.name.lower()):
                if port.name in ports_to_process:
                    ports_to_process[port.name] = True
                    option = self._create_port_api_option_internal(port,
                                                                   enable_take_address,
                                                                   indirect_api,
                                                                   error_handling,
                                                                   port_arg_values,
                                                                   supported_features,
                                                                   transformer_status_forwarding)
                    self.append_port_api_option(option)
            for key, value in ports_to_process.items():
                if not value:
                    raise ValueError(f"port_name: '{key}' is not a valid port name in SWC '{swc.name}'")

    def _create_port_api_option_internal(self,
                                         port: PortPrototypeElement,
                                         enable_take_address: bool | None = None,
                                         indirect_api: bool | None = None,
                                         error_handling: ar_enum.DataTransformationErrorHandling | None = None,
                                         port_arg_values: PortDefinedArgumentValueArgType = None,
                                         supported_features: SwcSupportedFeatureArgType = None,
                                         transformer_status_forwarding: ar_enum.DataTransformationStatusForwarding | None = None # noqa E501 pylint: disable=C0301
                                         ) -> PortApiOption:
        """
        Creates a single PortApiOption object. The port argument must be a valid port in parent SWC.
        """
        if not isinstance(port, PortPrototype):
            raise TypeError("port: argument must be a valid port")
        if port.ref() is None:
            msg = f"port {port.name} must have a valid reference. Make sure the parent SWC is part of a package"
            raise ValueError(msg)
        return PortApiOption(port.ref(),
                             enable_take_address,
                             indirect_api,
                             error_handling,
                             port_arg_values,
                             supported_features,
                             transformer_status_forwarding)


__all__ = [
    "ActivationReasonArgumentType",
    "CanEnterLeaveArgumentType",
    "ExclusiveAreaNestingOrderArgumentType",
    "RunsInsidesArgumentType",
    "ExclusiveAreaElementArgumentType",
    "AsyncServerCallResultPointArgumentType",
    "ServerCallPointArgumentType",
    "SwcModeSwitchEventModeType",
    "PortDefinedArgumentValueArgType",
    "SwcSupportedFeatureArgType",
    "ModeSwitchEventArgsReturnType",
    "ArVariableInImplementationDataInstanceRef",
    "VariableInAtomicSWCTypeInstanceRef",
    "AutosarVariableRef",
    "VariableAccess",
    "SwcImplementation",
    "ExecutableEntityActivationReason",
    "ExclusiveAreaRefConditional",
    "ExecutableEntity",
    "RunnableEntityArgument",
    "AbstractAccessPoint",
    "ServerCallPoint",
    "AsynchronousServerCallPoint",
    "AsynchronousServerCallResultPoint",
    "SynchronousServerCallPoint",
    "ExternalTriggeringPointIdent",
    "ExternalTriggeringPoint",
    "InternalTriggeringPoint",
    "ModeAccessPointIdent",
    "ModeAccessPoint",
    "ModeSwitchPoint",
    "ParameterInAtomicSwcTypeInstanceRef",
    "AutosarParameterRef",
    "ParameterAccess",
    "WaitPoint",
    "PortAccessOptions",
    "RunnableEntity",
    "RteEvent",
    "AsynchronousServerCallReturnsEvent",
    "BackgroundEvent",
    "DataReceiveErrorEvent",
    "DataReceivedEvent",
    "DataSendCompletedEvent",
    "DataWriteCompletedEvent",
    "ExternalTriggerOccurredEvent",
    "InitEvent",
    "InternalTriggerOccurredEvent",
    "ModeSwitchedAckEvent",
    "OperationInvokedEvent",
    "OsTaskExecutionEvent",
    "SwcModeManagerErrorEvent",
    "SwcModeSwitchEvent",
    "TimingEvent",
    "TransformerHardErrorEvent",
    "PortDefinedArgumentValue",
    "SwcSupportedFeature",
    "CommunicationBufferLocking",
    "PortApiOption",
    "ExclusiveArea",
    "ExclusiveAreaNestingOrder",
    "SwcExclusiveAreaPolicy",
    "IncludedDataTypeSet",
    "IncludedModeDeclarationGroupSet",
    "InstantiationDataDefProps",
    "PerInstanceMemory",
    "InternalBehavior",
    "SwcInternalBehavior",
]
