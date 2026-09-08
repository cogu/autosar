"""Mode declaration elements."""

from __future__ import annotations

from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import ARElement, Identifiable
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import (
    ImplementationDataTypeRef,
    ModeDeclarationGroupPrototypeRef,
    ModeDeclarationGroupRef,
    ModeDeclarationRef,
)


class ModeDeclaration(Identifiable):
    """
    Complex type AR:MODE-DECLARATION
    Tag variants: 'MODE-DECLARATION'
    """

    def __init__(self,
                 name: str,
                 value: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.value: int | None = None  # .VALUE
        # .VARIATION-POINT not supported
        self._assign_optional_positive_int("value", value)

    def ref(self) -> ModeDeclarationRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeDeclarationRef(ref_str)


class ModeErrorBehavior(ARObject):
    """
    Complex type AR:MODE-ERROR-BEHAVIOR
    Tag variants: 'MODE-MANAGER-ERROR-BEHAVIOR' | 'MODE-USER-ERROR-BEHAVIOR'
    """

    def __init__(self,
                 default_mode_ref: ModeDeclarationRef | None = None,
                 error_reaction_policy: ar_enum.ModeErrorReactionPolicy | None = None
                 ) -> None:
        self.default_mode_ref: ModeDeclarationRef | None = None
        self.error_reaction_policy: ar_enum.ModeErrorReactionPolicy | None = None
        self._assign_optional("default_mode_ref", default_mode_ref, ModeDeclarationRef)
        self._assign_optional("error_reaction_policy", error_reaction_policy, ar_enum.ModeErrorReactionPolicy)


class ModeTransition(Identifiable):
    """
    Complex type AR:MODE-TRANSITION
    Tag variants: 'MODE-TRANSITION'
    """

    def __init__(self,
                 name: str,
                 entered_mode_ref: ModeDeclarationRef | None = None,
                 exited_mode_ref: ModeDeclarationRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.entered_mode_ref: ModeDeclarationRef | None = None
        self.exited_mode_ref: ModeDeclarationRef | None = None
        self._assign_optional("entered_mode_ref", entered_mode_ref, ModeDeclarationRef)
        self._assign_optional("exited_mode_ref", exited_mode_ref, ModeDeclarationRef)


ModeDeclarationType = ModeDeclaration | list[ModeDeclaration] | list[str] | list[tuple[str, int]]


class ModeDeclarationGroup(ARElement):
    """
    Complex type AR:MODE-DECLARATION-GROUP
    Tag variants: 'MODE-DECLARATION-GROUP'
    """

    def __init__(self,
                 name: str,
                 mode_declarations: ModeDeclarationType | None = None,
                 initial_mode_ref: ModeDeclarationRef | None = None,
                 mode_manager_error_behavior: ModeErrorBehavior | None = None,
                 mode_transitions: ModeTransition | list[ModeTransition] | None = None,
                 mode_user_error_behavior: ModeErrorBehavior | None = None,
                 on_transition_value: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.initial_mode_ref: ModeDeclarationRef | None = None  # .INITIAL-MODE-REF
        self.mode_declarations: list[ModeDeclaration] = []  # .MODE-DECLARATIONS
        self.mode_manager_error_behavior: ModeErrorBehavior | None = None  # .MODE-MANAGER-ERROR-BEHAVIOR
        self.mode_transitions: list[ModeTransition] = []  # .MODE-TRANSITIONS
        self.mode_user_error_behavior: ModeErrorBehavior | None = None  # .MODE-USER-ERROR-BEHAVIOR
        self.on_transition_value: int | None = None  # .ON-TRANSITION-VALUE
        self._assign_optional("initial_mode_ref", initial_mode_ref, ModeDeclarationRef)
        self._assign_optional_strict("mode_manager_error_behavior", mode_manager_error_behavior, ModeErrorBehavior)
        self._assign_optional_strict("mode_user_error_behavior", mode_user_error_behavior, ModeErrorBehavior)
        self._assign_optional_positive_int("on_transition_value", on_transition_value)

        expected_types = "Expected 'ModeDeclaration', list[ModeDeclaration], list[str], list[tuple[str,int]]"
        if mode_declarations is not None:
            if isinstance(mode_declarations, ModeDeclaration):
                self.append_mode_declaration(mode_declarations)
            elif isinstance(mode_declarations, list):
                for mode_declaration in mode_declarations:
                    if isinstance(mode_declaration, ModeDeclaration):
                        self.append_mode_declaration(mode_declaration)
                    elif isinstance(mode_declaration, str):
                        self.create_mode_declaration(mode_declaration)
                    elif isinstance(mode_declaration, tuple):
                        self.create_mode_declaration(*mode_declaration)
                    else:
                        err_msg = f"Invalid type '{str(type(mode_declaration))}'"
                        raise TypeError(err_msg + ". " + expected_types)
            else:
                err_msg = f"mode_declarations: Invalid type '{str(type(mode_declarations))}'"
                raise TypeError(err_msg + ". " + expected_types)

        if mode_transitions is not None:
            if isinstance(mode_transitions, ModeTransition):
                self.append_mode_transition(mode_transitions)
            elif isinstance(mode_transitions, list):
                for mode_transition in mode_transitions:
                    self.append_mode_transition(mode_transition)
            else:
                msg = f"operations: Invalid type '{str(type(mode_transitions))}'"
                raise TypeError(msg + ". Expected 'ModeTransition' or list[ModeTransition]")

    def find(self, name: str) -> ModeDeclaration | ModeTransition | None:
        """
        Finds and returns sub-item based on short name
        """
        for mode_declaration in self.mode_declarations:
            if mode_declaration.name == name:
                return mode_declaration
        for mode_transition in self.mode_transitions:
            if mode_transition.name == name:
                return mode_transition
        return None

    def append_mode_declaration(self, mode_declaration: ModeDeclaration) -> None:
        """
        Appends mode declaratopm to internal list of mode declarations
        """
        if isinstance(mode_declaration, ModeDeclaration):
            mode_declaration.parent = self
            self.mode_declarations.append(mode_declaration)
        else:
            msg = f"mode_declaration: Invalid type '{str(type(mode_declaration))}'"
            raise TypeError(msg + ". Expected 'ModeDeclaration'")

    @convenience_function
    def create_mode_declaration(self,
                                name: str,
                                value: int | None = None,
                                **kwargs) -> ModeDeclaration:
        """

        Adds a new mode declaration to this group
        """
        mode_declaration = ModeDeclaration(name, value, **kwargs)
        self.append_mode_declaration(mode_declaration)
        return mode_declaration

    def append_mode_transition(self, mode_transition: ModeTransition) -> None:
        """
        Appends mode transition to internal list of transitions
        """
        if isinstance(mode_transition, ModeTransition):
            mode_transition.parent = mode_transition
            self.mode_transitions.append(mode_transition)
        else:
            msg = f"mode_transition: Invalid type '{str(type(mode_transition))}'"
            raise TypeError(msg + ". Expected 'ModeTransition'")

    def ref(self) -> ModeDeclarationGroupRef | None:
        """
        Returns a reference to this element or None if the element is
        not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeDeclarationGroupRef(ref_str)


class ModeDeclarationGroupPrototype(Identifiable):
    """
    Complex type AR:MODE-DECLARATION-GROUP-PROTOTYPE
    Tag variants: 'MODE-DECLARATION-GROUP-PROTOTYPE' | 'MODE-GROUP'
    """

    def __init__(self,
                 name: str,
                 type_ref: ModeDeclarationGroupRef | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.calibration_access: ar_enum.SwCalibrationAccess | None = None  # .SW-CALIBRATION-ACCESS
        self.type_ref: ModeDeclarationGroupRef | None = None  # .TYPE-TREF
        self._assign_optional('calibration_access', calibration_access, ar_enum.SwCalibrationAccess)
        self._assign_optional('type_ref', type_ref, ModeDeclarationGroupRef)

    def ref(self) -> ModeDeclarationGroupPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ModeDeclarationGroupPrototypeRef(ref_str)


class ModeRequestTypeMap(ARObject):
    """
    Complex type AR:MODE-REQUEST-TYPE-MAP
    Tag variants: 'MODE-REQUEST-TYPE-MAP'
    """

    def __init__(self,
                 implementation_data_type: ImplementationDataTypeRef | None = None,
                 mode_group: ModeDeclarationGroupRef | None = None) -> None:
        # .IMPLEMENTATION-DATA-TYPE-REF
        self.implementation_data_type: ImplementationDataTypeRef | None = None
        # .MODE-GROUP-REF
        self.mode_group: ModeDeclarationGroupRef | None = None
        self._assign_optional('implementation_data_type', implementation_data_type, ImplementationDataTypeRef)
        self._assign_optional('mode_group', mode_group, ModeDeclarationGroupRef)


__all__ = [
    "ModeDeclarationType",
    "ModeDeclaration",
    "ModeErrorBehavior",
    "ModeTransition",
    "ModeDeclarationGroup",
    "ModeDeclarationGroupPrototype",
    "ModeRequestTypeMap",
]
