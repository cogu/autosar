"""System template elements."""

from __future__ import annotations

from autosar.xml.elements._base import ARElement
from autosar.xml.elements.documentation import Describable
from autosar.xml.reference import E2EProfileCompatibilityPropsRef


class E2EProfileCompatibilityProps(ARElement):
    """
    Complex type AR:E-2-E-PROFILE-COMPATIBILITY-PROPS
    Tag variants: 'E-2-E-PROFILE-COMPATIBILITY-PROPS'
    """

    def __init__(self,
                 name: str,
                 transit_to_invalid_extended: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.transit_to_invalid_extended: bool | None = None  # .TRANSIT-TO-INVALID-EXTENDED
        self._assign_optional_strict("transit_to_invalid_extended", transit_to_invalid_extended, bool)

    def ref(self) -> E2EProfileCompatibilityPropsRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return E2EProfileCompatibilityPropsRef(ref_str)


class EndToEndTransformationComSpecProps(Describable):
    """
    Complex type AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
    Tag variants: 'END-TO-END-TRANSFORMATION-COM-SPEC-PROPS'
    """

    def __init__(self,  # pylint: disable=R0917
                 clear_from_valid_to_invalid: bool | None = None,
                 disable_e2e_check: bool | None = None,
                 disable_e2e_state_machine: bool | None = None,
                 e2e_profile_compatibility_props_ref: E2EProfileCompatibilityPropsRef | None = None,
                 max_delta_counter: int | None = None,
                 max_error_state_init: int | None = None,
                 max_error_state_invalid: int | None = None,
                 max_error_state_valid: int | None = None,
                 max_no_new_repeated_data: int | None = None,
                 min_ok_state_init: int | None = None,
                 min_ok_state_invalid: int | None = None,
                 min_ok_state_valid: int | None = None,
                 sync_counter_init: int | None = None,
                 window_size_init: int | None = None,
                 window_size_invalid: int | None = None,
                 window_size_valid: int | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        # .CLEAR-FROM-VALID-TO-INVALID
        self.clear_from_valid_to_invalid: bool | None = None
        # .DISABLE-END-TO-END-CHECK
        self.disable_e2e_check: bool | None = None
        # .DISABLE-END-TO-END-STATE-MACHINE
        self.disable_e2e_state_machine: bool | None = None
        # .E-2-E-PROFILE-COMPATIBILITY-PROPS-REF
        self.e2e_profile_compatibility_props_ref: E2EProfileCompatibilityPropsRef | None = None
        # .MAX-DELTA-COUNTER
        self.max_delta_counter: int | None = None
        # .MAX-ERROR-STATE-INIT
        self.max_error_state_init: int | None = None
        # .MAX-ERROR-STATE-INVALID
        self.max_error_state_invalid: int | None = None
        # .MAX-ERROR-STATE-VALID
        self.max_error_state_valid: int | None = None
        # .MAX-NO-NEW-OR-REPEATED-DATA
        self.max_no_new_repeated_data: int | None = None
        # .MIN-OK-STATE-INIT
        self.min_ok_state_init: int | None = None
        # .MIN-OK-STATE-INVALID
        self.min_ok_state_invalid: int | None = None
        # .MIN-OK-STATE-VALID
        self.min_ok_state_valid: int | None = None
        # .SYNC-COUNTER-INIT
        self.sync_counter_init: int | None = None
        # .WINDOW-SIZE --- REMOVED
        # .WINDOW-SIZE-INIT
        self.window_size_init: int | None = None
        # .WINDOW-SIZE-INVALID
        self.window_size_invalid: int | None = None
        # .WINDOW-SIZE-VALID
        self.window_size_valid: int | None = None
        self._assign_optional_strict("clear_from_valid_to_invalid", clear_from_valid_to_invalid, bool)
        self._assign_optional_strict("disable_e2e_check", disable_e2e_check, bool)
        self._assign_optional_strict("disable_e2e_state_machine", disable_e2e_state_machine, bool)
        self._assign_optional("e2e_profile_compatibility_props_ref",
                              e2e_profile_compatibility_props_ref, E2EProfileCompatibilityPropsRef)
        self._assign_optional_positive_int("max_delta_counter", max_delta_counter)
        self._assign_optional_positive_int("max_error_state_init", max_error_state_init)
        self._assign_optional_positive_int("max_error_state_invalid", max_error_state_invalid)
        self._assign_optional_positive_int("max_error_state_valid", max_error_state_valid)
        self._assign_optional_positive_int("max_no_new_repeated_data", max_no_new_repeated_data)
        self._assign_optional_positive_int("min_ok_state_init", min_ok_state_init)
        self._assign_optional_positive_int("min_ok_state_invalid", min_ok_state_invalid)
        self._assign_optional_positive_int("min_ok_state_valid", min_ok_state_valid)
        self._assign_optional_positive_int("sync_counter_init", sync_counter_init)
        self._assign_optional_positive_int("window_size_init", window_size_init)
        self._assign_optional_positive_int("window_size_invalid", window_size_invalid)
        self._assign_optional_positive_int("window_size_valid", window_size_valid)


__all__ = [
    "E2EProfileCompatibilityProps",
    "EndToEndTransformationComSpecProps",
]
