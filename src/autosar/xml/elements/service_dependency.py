"""Service dependency elements."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from autosar.xml.base import ARObject
from autosar.xml.elements._base import Identifiable, Referrable
from autosar.xml.elements.service_needs import ServiceNeeds
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except
from autosar.xml.reference import (
    ImplementationDataTypeRef,
    PerInstanceMemoryRef,
    PortGroupRef,
    PortPrototypeRef,
)

if TYPE_CHECKING:
    from autosar.xml.elements.internal_behavior import (
        AutosarParameterRef,
        AutosarVariableRef,
    )


def _get_autosar_variable_ref_class():
    from autosar.xml.elements.internal_behavior import AutosarVariableRef
    return AutosarVariableRef


def _get_autosar_parameter_ref_class():
    from autosar.xml.elements.internal_behavior import AutosarParameterRef
    return AutosarParameterRef


class RoleBasedDataAssignment(ARObject):
    """
    Complex type AR:ROLE-BASED-DATA-ASSIGNMENT
    Tag variants: 'ROLE-BASED-DATA-ASSIGNMENT'
    """

    def __init__(self,
                 role: str | None = None,
                 used_data_element: AutosarVariableRef | None = None,
                 used_parameter_element: AutosarParameterRef | None = None,
                 used_pim_ref: PerInstanceMemoryRef | str | None = None) -> None:
        super().__init__()
        # .ROLE
        self.role: str | None = None
        # .USED-DATA-ELEMENT
        self.used_data_element: AutosarVariableRef | None = None
        # .USED-PARAMETER-ELEMENT
        self.used_parameter_element: AutosarParameterRef | None = None
        # .USED-PIM-REF
        self.used_pim_ref: PerInstanceMemoryRef | None = None

        self._assign_optional_strict("role", role, str)
        if used_data_element is not None:
            self._assign_optional_strict("used_data_element",
                                         used_data_element,
                                         _get_autosar_variable_ref_class())
        if used_parameter_element is not None:
            self._assign_optional_strict("used_parameter_element",
                                         used_parameter_element,
                                         _get_autosar_parameter_ref_class())
        self._assign_optional("used_pim_ref", used_pim_ref, PerInstanceMemoryRef)


class RoleBasedDataTypeAssignment(ARObject):
    """
    Complex type AR:ROLE-BASED-DATA-TYPE-ASSIGNMENT
    Tag variants: 'ROLE-BASED-DATA-TYPE-ASSIGNMENT'
    """

    def __init__(self,
                 role: str | None = None,
                 used_implementation_data_type_ref: ImplementationDataTypeRef | str | None = None) -> None:
        super().__init__()
        # .ROLE
        self.role: str | None = None
        # .USED-IMPLEMENTATION-DATA-TYPE-REF
        self.used_implementation_data_type_ref: ImplementationDataTypeRef | None = None

        self._assign_optional_strict("role", role, str)
        self._assign_optional("used_implementation_data_type_ref",
                              used_implementation_data_type_ref,
                              ImplementationDataTypeRef)


class RoleBasedPortAssignment(ARObject):
    """
    Complex type AR:ROLE-BASED-PORT-ASSIGNMENT
    Tag variants: 'ROLE-BASED-PORT-ASSIGNMENT'
    """

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | str | None = None,
                 role: str | None = None) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROLE
        self.role: str | None = None

        self._assign_optional("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional_strict("role", role, str)


class SymbolicNameProps(Referrable):
    """
    Complex type AR:SYMBOLIC-NAME-PROPS
    Tag variants: 'SYMBOLIC-NAME-PROPS'
    """

    def __init__(self,
                 name: str,
                 symbol: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .SYMBOL
        self.symbol: str | None = None
        self._assign_optional_strict("symbol", symbol, str)


class ServiceDependency(Identifiable):
    """
    Group AR:SERVICE-DEPENDENCY
    """

    def __init__(self,
                 name: str,
                 assigned_data_types: (RoleBasedDataTypeAssignment |
                                       list[RoleBasedDataTypeAssignment] |
                                       None) = None,
                 diagnostic_relevance: ar_enum.ServiceDiagnosticRelevance | str | None = None,
                 symbolic_name_props: SymbolicNameProps | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ASSIGNED-DATA-TYPES
        self.assigned_data_types: list[RoleBasedDataTypeAssignment] = []
        # .DIAGNOSTIC-RELEVANCE
        self.diagnostic_relevance: ar_enum.ServiceDiagnosticRelevance | None = None
        # .SYMBOLIC-NAME-PROPS
        self.symbolic_name_props: SymbolicNameProps | None = None

        if assigned_data_types is not None:
            if isinstance(assigned_data_types, RoleBasedDataTypeAssignment):
                self.assigned_data_types.append(assigned_data_types)
            elif isinstance(assigned_data_types, Iterable):
                for item in assigned_data_types:
                    self.append_assigned_data_type(item)
            else:
                raise TypeError(f"assigned_data_types: Invalid type {str(type(assigned_data_types))}")

        self._assign_optional("diagnostic_relevance",
                              diagnostic_relevance,
                              ar_enum.ServiceDiagnosticRelevance)
        self._assign_optional_strict("symbolic_name_props",
                                     symbolic_name_props,
                                     SymbolicNameProps)

    def append_assigned_data_type(self, item: RoleBasedDataTypeAssignment) -> None:
        """
        Appends RoleBasedDataTypeAssignment to assigned_data_types
        """
        if isinstance(item, RoleBasedDataTypeAssignment):
            self.assigned_data_types.append(item)
        else:
            raise ar_except.ElementTypeError("item", RoleBasedDataTypeAssignment, item)


class SwcServiceDependency(ServiceDependency):
    """
    Complex type AR:SWC-SERVICE-DEPENDENCY
    Tag variants: 'SWC-SERVICE-DEPENDENCY'
    """

    def __init__(self,
                 name: str,
                 assigned_datas: (RoleBasedDataAssignment |
                                  list[RoleBasedDataAssignment] |
                                  None) = None,
                 assigned_ports: (RoleBasedPortAssignment |
                                  list[RoleBasedPortAssignment] |
                                  None) = None,
                 represented_port_group_ref: PortGroupRef | str | None = None,
                 service_needs: ServiceNeeds | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ASSIGNED-DATAS
        self.assigned_datas: list[RoleBasedDataAssignment] = []
        # .ASSIGNED-PORTS
        self.assigned_ports: list[RoleBasedPortAssignment] = []
        # .REPRESENTED-PORT-GROUP-REF
        self.represented_port_group_ref: PortGroupRef | None = None
        # .SERVICE-NEEDS
        self.service_needs: ServiceNeeds | None = None

        if assigned_datas is not None:
            if isinstance(assigned_datas, RoleBasedDataAssignment):
                self.assigned_datas.append(assigned_datas)
            elif isinstance(assigned_datas, Iterable):
                for item in assigned_datas:
                    self.append_assigned_data(item)
            else:
                raise TypeError(f"assigned_datas: Invalid type {str(type(assigned_datas))}")

        if assigned_ports is not None:
            if isinstance(assigned_ports, RoleBasedPortAssignment):
                self.assigned_ports.append(assigned_ports)
            elif isinstance(assigned_ports, Iterable):
                for item in assigned_ports:
                    self.append_assigned_port(item)
            else:
                raise TypeError(f"assigned_ports: Invalid type {str(type(assigned_ports))}")

        self._assign_optional("represented_port_group_ref",
                              represented_port_group_ref,
                              PortGroupRef)
        self._assign_optional_strict("service_needs",
                                     service_needs,
                                     ServiceNeeds)

    def append_assigned_data(self, item: RoleBasedDataAssignment) -> None:
        """
        Appends RoleBasedDataAssignment to assigned_datas
        """
        if isinstance(item, RoleBasedDataAssignment):
            self.assigned_datas.append(item)
        else:
            raise ar_except.ElementTypeError("item", RoleBasedDataAssignment, item)

    def append_assigned_port(self, item: RoleBasedPortAssignment) -> None:
        """
        Appends RoleBasedPortAssignment to assigned_ports
        """
        if isinstance(item, RoleBasedPortAssignment):
            self.assigned_ports.append(item)
        else:
            raise ar_except.ElementTypeError("item", RoleBasedPortAssignment, item)


__all__ = [
    "RoleBasedDataAssignment",
    "RoleBasedDataTypeAssignment",
    "RoleBasedPortAssignment",
    "SymbolicNameProps",
    "ServiceDependency",
    "SwcServiceDependency",
]
