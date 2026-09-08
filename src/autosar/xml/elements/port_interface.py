"""Port interface elements."""

from __future__ import annotations

from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import ARElement, Identifiable
from autosar.xml.elements.common import Trigger
from autosar.xml.elements.constant import ValueSpecificationElement
from autosar.xml.elements.data_type import (
    ArgumentDataPrototype,
    ParameterDataPrototype,
    VariableDataPrototype,
)
from autosar.xml.elements.mode_declaration import ModeDeclarationGroupPrototype
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import (
    ApplicationErrorRef,
    ClientServerOperationRef,
    ModeDeclarationGroupRef,
    PortInterfaceRef,
    VariableDataPrototypeRef,
)


class PortInterface(ARElement):
    """
    Group AR:PORT-INTERFACE
    """

    def __init__(self,
                 name: str,
                 is_service: bool | None = None,
                 service_kind: ar_enum.ServiceKind | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.is_service: bool | None = None  # .IS-SERVICE
        # .NAMESPACES not supported
        self.service_kind: ar_enum.ServiceKind | None = None  # .SERVICE-KIND
        self._assign_optional_strict("is_service", is_service, bool)
        self._assign_optional_strict("service_kind", service_kind, ar_enum.ServiceKind)


class DataInterface(PortInterface):
    """
    Group AR:DATA-INTERFACE

    Base class for data-based interfaces (as opposed to operations-based)
    """


class InvalidationPolicy(ARObject):
    """
    Complex type AR:INVALIDATION-POLICY
    Tag variants: 'INVALIDATION-POLICY'
    """

    def __init__(self,
                 data_element_ref: VariableDataPrototypeRef | None = None,
                 handle_invalid: ar_enum.HandleInvalid | None = None) -> None:
        self.data_element_ref: VariableDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        self.handle_invalid: ar_enum.HandleInvalid | None = None  # .HANDLE-INVALID
        self._assign_optional("data_element_ref", data_element_ref, VariableDataPrototypeRef)
        self._assign_optional("handle_invalid", handle_invalid, ar_enum.HandleInvalid)


class SenderReceiverInterface(DataInterface):
    """
    Complex type AR:SENDER-RECEIVER-INTERFACE
    Tag variants: 'SENDER-RECEIVER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 data_elements: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 invalidation_policies: InvalidationPolicy | list[InvalidationPolicy] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.data_elements: list[VariableDataPrototype] = []  # .DATA-ELEMENTS
        self.invalidation_policies: list[InvalidationPolicy] = []  # .INVALIDATION-POLICYS
        # .META-DATA-ITEM-SETS not supported
        if data_elements is not None:
            if isinstance(data_elements, VariableDataPrototype):
                self.append_data_element(data_elements)
            elif isinstance(data_elements, list):
                for data_element in data_elements:
                    self.append_data_element(data_element)
            else:
                msg = f"data_elements: Invalid type '{str(type(data_element))}'"
                raise TypeError(msg + ". Expected 'VariableDataPrototype' or list[VariableDataPrototype]")
        if invalidation_policies is not None:
            if isinstance(invalidation_policies, InvalidationPolicy):
                self.append_invalidation_policy(invalidation_policies)
            elif isinstance(invalidation_policies, list):
                for invalidation_policy in invalidation_policies:
                    self.append_invalidation_policy(invalidation_policy)
            else:
                msg = f"data_elements: Invalid type '{str(type(invalidation_policies))}'"
                raise TypeError(msg + ". Expected 'InvalidationPolicy' or list[InvalidationPolicy]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)

    def append_data_element(self, data_element: VariableDataPrototype):
        """
        Appends data element to internal list of elements
        """
        if isinstance(data_element, VariableDataPrototype):
            self.data_elements.append(data_element)
            data_element.parent = self
        else:
            msg = f"data_element: Invalid type '{str(type(data_element))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototype'")

    def append_invalidation_policy(self, invalidation_policy: InvalidationPolicy):
        """
        Appends invalidation policy to internal list of policies
        """
        if isinstance(invalidation_policy, InvalidationPolicy):
            self.invalidation_policies.append(invalidation_policy)
        else:
            msg = f"invalidation_policy: Invalid type '{str(type(invalidation_policy))}'"
            raise TypeError(msg + ". Expected 'InvalidationPolicy'")

    @convenience_function
    def create_data_element(self,
                            name: str,
                            init_value: ValueSpecificationElement | None = None,
                            **kwargs) -> VariableDataPrototype:
        """

        Adds a new data element to this port interface
        """
        data_element = VariableDataPrototype(name, init_value, **kwargs)
        self.append_data_element(data_element)
        return data_element

    @convenience_function
    def create_invalidation_policy(self,
                                   data_element_ref: VariableDataPrototypeRef | str,
                                   handle_invalid: ar_enum.HandleInvalid) -> InvalidationPolicy:
        """

        Adds a new invalidation policy to this port interface
        """
        if isinstance(data_element_ref, str):
            data_element_ref = VariableDataPrototypeRef(data_element_ref)
        elif not isinstance(data_element_ref, VariableDataPrototypeRef):
            msg = f"data_element_ref: Invalid type '{str(type(data_element_ref))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototypeRef' or 'str'")
        if not isinstance(handle_invalid, ar_enum.HandleInvalid):
            msg = f"handle_invalid: Invalid type '{str(type(data_element_ref))}'"
            raise TypeError(msg + ". Expected 'HandleInvalid'")
        invalidation_policy = InvalidationPolicy(data_element_ref, handle_invalid)
        self.append_invalidation_policy(invalidation_policy)
        return invalidation_policy


class NvDataInterface(DataInterface):
    """
    Complex type AR:NV-DATA-INTERFACE
    Tag variants: 'NV-DATA-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 data_elements: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.data_elements: list[VariableDataPrototype] = []  # .NV-DATAS
        if data_elements is not None:
            if isinstance(data_elements, VariableDataPrototype):
                self.append_data_element(data_elements)
            elif isinstance(data_elements, list):
                for data_element in data_elements:
                    self.append_data_element(data_element)
            else:
                msg = f"nv_datas: Invalid type '{str(type(data_elements))}'"
                raise TypeError(msg + ". Expected 'VariableDataPrototype' or list[VariableDataPrototype]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE)

    def append_data_element(self, nv_data: VariableDataPrototype):
        """
        Appends data element to internal list of data elements
        """
        if isinstance(nv_data, VariableDataPrototype):
            self.data_elements.append(nv_data)
            nv_data.parent = self
        else:
            msg = f"nv_data: Invalid type '{str(type(nv_data))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototype'")

    @convenience_function
    def create_data_element(self,
                            name: str,
                            init_value: ValueSpecificationElement | None = None,
                            **kwargs) -> VariableDataPrototype:
        """

        Adds a new data element to this port interface
        """
        data_element = VariableDataPrototype(name, init_value, **kwargs)
        self.append_data_element(data_element)
        return data_element


class ParameterInterface(DataInterface):
    """
    Complex type AR:PARAMETER-INTERFACE
    Tag variants: 'PARAMETER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 parameters: ParameterDataPrototype | list[ParameterDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.parameters: list[ParameterDataPrototype] = []  # .PARAMETERS
        if parameters is not None:
            if isinstance(parameters, ParameterDataPrototype):
                self.append_parameter(parameters)
            elif isinstance(parameters, list):
                for parameter in parameters:
                    self.append_parameter(parameter)
            else:
                msg = f"parameters: Invalid type '{str(type(parameters))}'"
                raise TypeError(msg + ". Expected 'ParameterDataPrototype' or list[ParameterDataPrototype]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE)

    def append_parameter(self, parameter: ParameterDataPrototype):
        """
        Appends parameter to internal list of parameters
        """
        if isinstance(parameter, ParameterDataPrototype):
            self.parameters.append(parameter)
            parameter.parent = self
        else:
            msg = f"parameter: Invalid type '{str(type(parameter))}'"
            raise TypeError(msg + ". Expected 'ParameterDataPrototype'")

    @convenience_function
    def create_parameter(self,
                         name: str,
                         init_value: ValueSpecificationElement | None = None,
                         **kwargs) -> ParameterDataPrototype:
        """

        Adds a new parameter to this port interface
        """
        data_element = ParameterDataPrototype(name, init_value, **kwargs)
        self.append_parameter(data_element)
        return data_element


class ApplicationError(Identifiable):
    """
    Complex type AR:APPLICATION-ERROR
    Tag variants: 'APPLICATION-ERROR'
    """

    def __init__(self,
                 name: str,
                 error_code: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.error_code: int | None = None
        self._assign_optional_strict("error_code", error_code, int)

    def ref(self) -> ApplicationErrorRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationErrorRef(ref_str)


PossibleErrorRefsTypes = ApplicationErrorRef | list[ApplicationErrorRef] | str | list[str]


class ClientServerOperation(Identifiable):
    """
    Complex type AR:CLIENT-SERVER-OPERATION
    Tag variants: 'CLIENT-SERVER-OPERATION'
    """

    def __init__(self,
                 name: str,
                 arguments: ArgumentDataPrototype | list[ArgumentDataPrototype] | None = None,
                 diag_arg_integrity: bool | None = None,
                 possible_error_refs: PossibleErrorRefsTypes | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ARGUMENTS
        self.arguments: list[ArgumentDataPrototype] = []
        # .DIAG-ARG-INTEGRITY
        self.diag_arg_integrity: bool | None = None
        # .FIRE-AND-FORGET --- NOT SUPPORTED (AP)
        # .POSSIBLE-AP-ERROR-REFS --- NOT SUPPORTED (AP)
        # .POSSIBLE-AP-ERROR-SET-REFS --- NOT SUPPORTED (AP)
        # .POSSIBLE-ERROR-REFS
        self.possible_error_refs: list[ApplicationErrorRef] = []
        # .VARIATION-POINT --- NOT SUPPORTED (VARIANT)

        self._assign_optional_strict("diag_arg_integrity", diag_arg_integrity, bool)
        if arguments is not None:
            if isinstance(arguments, ArgumentDataPrototype):
                self.append_argument(arguments)
            elif isinstance(arguments, list):
                for argument in arguments:
                    self.append_argument(argument)
            else:
                msg = f"parameters: Invalid type '{str(type(arguments))}'"
                raise TypeError(msg + ". Expected 'ArgumentDataPrototype' or list[ArgumentDataPrototype]")

        if possible_error_refs is not None:
            if isinstance(possible_error_refs, ApplicationErrorRef):
                self.append_possible_error_ref(possible_error_refs)
            elif isinstance(possible_error_refs, str):
                self.append_possible_error_ref(ApplicationErrorRef(possible_error_refs))
            elif isinstance(possible_error_refs, list):
                for possible_error_ref in possible_error_refs:
                    self.append_possible_error_ref(possible_error_ref)
            else:
                msg = f"possible_error_refs: Invalid type '{str(type(possible_error_refs))}'"
                raise TypeError(msg + ". Expected 'ApplicationErrorRef' or list[ApplicationErrorRef]")

    def ref(self) -> ClientServerOperationRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ClientServerOperationRef(ref_str)

    def append_argument(self, argument: ArgumentDataPrototype) -> None:
        """
        Appends argument to internal list of arguments
        """
        if isinstance(argument, ArgumentDataPrototype):
            self.arguments.append(argument)
        else:
            msg = f"argument: Invalid type '{str(type(argument))}'"
            raise TypeError(msg + ". Expected 'ArgumentDataPrototype'")

    @convenience_function
    def create_argument(self,
                        name: str,
                        direction: ar_enum.ArgumentDirection | None = None,
                        server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                        **kwargs) -> ArgumentDataPrototype:
        """

        Adds a new argument to this operation
        """
        argument = ArgumentDataPrototype(name, direction, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    @convenience_function
    def create_in_argument(self,
                           name: str,
                           server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                           **kwargs) -> ArgumentDataPrototype:
        """

        Adds a new in-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.IN, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    @convenience_function
    def create_inout_argument(self,
                              name: str,
                              server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                              **kwargs) -> ArgumentDataPrototype:
        """

        Adds a new inout-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.INOUT, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    @convenience_function
    def create_out_argument(self,
                            name: str,
                            server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                            **kwargs) -> ArgumentDataPrototype:
        """

        Adds a new out-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.OUT, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def append_possible_error_ref(self, possible_error_ref: ApplicationErrorRef) -> None:
        """
        Appends error reference to internal list of possible errors for this operation
        """
        if isinstance(possible_error_ref, ApplicationErrorRef):
            self.possible_error_refs.append(possible_error_ref)
        else:
            msg = f"argument: Invalid type '{str(type(possible_error_ref))}'"
            raise TypeError(msg + ". Expected 'ApplicationErrorRef'")

    @convenience_function
    def create_possible_error_ref(self, value: str) -> ApplicationErrorRef:
        """

        Adds a new possible error reference to this operation
        """
        possible_error_ref = ApplicationErrorRef(value)
        self.append_possible_error_ref(possible_error_ref)
        return possible_error_ref


class ClientServerInterface(PortInterface):
    """
    Complex type AR:CLIENT-SERVER-INTERFACE
    Tag variants: 'CLIENT-SERVER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 operations: ClientServerOperation | list[ClientServerOperation] | None = None,
                 possible_errors: ApplicationError | list[ApplicationError] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.operations: list[ClientServerOperation] = []
        self.possible_errors: list[ApplicationError] = []

        if operations is not None:
            if isinstance(operations, ClientServerOperation):
                self.append_operation(operations)
            elif isinstance(operations, list):
                for operation in operations:
                    self.append_operation(operation)
            else:
                msg = f"operations: Invalid type '{str(type(operations))}'"
                raise TypeError(msg + ". Expected 'ClientServerOperation' or list[ClientServerOperation]")

        if possible_errors is not None:
            if isinstance(possible_errors, ApplicationError):
                self.append_operation(possible_errors)
            elif isinstance(possible_errors, list):
                for possible_error in possible_errors:
                    self.append_possible_errors(possible_error)
            else:
                msg = f"possible_errors: Invalid type '{str(type(possible_errors))}'"
                raise TypeError(msg + ". Expected 'ApplicationError' or list[ApplicationError]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE)

    def append_operation(self, operation: ClientServerOperation) -> None:
        """
        Appends operation to internal list of operations
        """
        if isinstance(operation, ClientServerOperation):
            self.operations.append(operation)
            operation.parent = self
        else:
            msg = f"operation: Invalid type '{str(type(operation))}'"
            raise TypeError(msg + ". Expected 'ClientServerOperation'")

    def append_possible_errors(self, possible_error: ApplicationError) -> None:
        """
        Appends possible error to internal list of possible errors
        """
        if isinstance(possible_error, ApplicationError):
            possible_error.parent = self
            self.possible_errors.append(possible_error)
        else:
            msg = f"operation: Invalid type '{str(type(possible_error))}'"
            raise TypeError(msg + ". Expected 'ApplicationError'")

    @convenience_function
    def create_operation(self,
                         name: str,
                         arguments: ArgumentDataPrototype | list[ArgumentDataPrototype] | None = None,
                         diag_arg_integrity: bool | None = None,
                         possible_error_refs: ApplicationErrorRef | list[ApplicationErrorRef] | None = None,
                         **kwargs) -> ClientServerOperation:
        """

        Adds a new operation to this port interface
        """
        operation = ClientServerOperation(name, arguments, diag_arg_integrity, possible_error_refs,
                                          **kwargs)
        self.append_operation(operation)
        return operation

    @convenience_function
    def create_possible_error(self,
                              name: str,
                              error_code: int | None = None,
                              **kwargs) -> ApplicationError:
        """

        Adds a new possible error in this port interface
        """
        possible_error = ApplicationError(name, error_code, **kwargs)
        self.append_possible_errors(possible_error)
        return possible_error


class ModeSwitchInterface(PortInterface):
    """
    Complex type AR:MODE-SWITCH-INTERFACE
    Tag variants: 'MODE-SWITCH-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 mode_group: ModeDeclarationGroupPrototype | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MODE-GROUP
        self.mode_group: ModeDeclarationGroupPrototype | None = None

        self._assign_optional_strict("mode_group", mode_group, ModeDeclarationGroupPrototype)

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE)

    @convenience_function
    def create_mode_group(self,
                          name: str,
                          type_ref: ModeDeclarationGroupRef | None = None,
                          calibration_access: ar_enum.SwCalibrationAccess | None = None,
                          **kwargs) -> ModeDeclarationGroupPrototype:
        """

        Adds a new mode declaration group to this port interface

        Note that this class only supports up to one mode group. Calling this method a second time
        will overwrite the previous value.
        """
        self.mode_group = ModeDeclarationGroupPrototype(name, type_ref, calibration_access, **kwargs)
        self.mode_group.parent = self
        return self.mode_group


class TriggerInterface(PortInterface):
    """
    Complex type AR:TRIGGER-INTERFACE
    Tag variants: 'TRIGGER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 triggers: Trigger | list[Trigger] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .TRIGGERS
        self.triggers: list[Trigger] = []
        if triggers is not None:
            if isinstance(triggers, list):
                for trigger in triggers:
                    self.append_trigger(trigger)
            else:
                self.append_trigger(triggers)

    def append_trigger(self, trigger: Trigger) -> None:
        """Appends trigger to internal list of triggers"""
        if isinstance(trigger, Trigger):
            self.triggers.append(trigger)
            trigger.parent = self
        else:
            msg = f"trigger: Invalid type '{str(type(trigger))}'"
            raise TypeError(msg)

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.TRIGGER_INTERFACE)


__all__ = [
    "PossibleErrorRefsTypes",
    "PortInterface",
    "DataInterface",
    "InvalidationPolicy",
    "SenderReceiverInterface",
    "NvDataInterface",
    "ParameterInterface",
    "ApplicationError",
    "ClientServerOperation",
    "ClientServerInterface",
    "ModeSwitchInterface",
    "TriggerInterface",
]
