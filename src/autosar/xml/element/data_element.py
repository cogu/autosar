"""References to AUTOSAR variables and parameters."""

from __future__ import annotations

from typing import Union

from autosar.xml.base import ARObject
from autosar.xml.reference import (
    AbstractImplementationDataTypeElementRef,
    ApplicationCompositeElementDataPrototypeRef,
    DataPrototypeRef,
    ParameterDataPrototypeRef,
    PortPrototypeRef,
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
                 target_data_prototype_ref: DataPrototypeRef | VariableDataPrototypeRef | None = None,
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


class ParameterInAtomicSwcTypeInstanceRef(ARObject):
    """
    Complex type AR:PARAMETER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'AUTOSAR-PARAMETER-IREF'
    """

    def __init__(self,
                 port_prototype: PortPrototypeRef | None = None,
                 root_parameter_data_prototype: DataPrototypeRef | None = None,
                 context_data_prototype: ApplicationCompositeElementDataPrototypeRef | None = None,
                 target_data_prototype: DataPrototypeRef | ParameterDataPrototypeRef | None = None
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


__all__ = [
    "ArVariableInImplementationDataInstanceRef",
    "VariableInAtomicSWCTypeInstanceRef",
    "AutosarVariableRef",
    "ParameterInAtomicSwcTypeInstanceRef",
    "AutosarParameterRef",
]
