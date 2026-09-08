"""Common structure elements."""

from __future__ import annotations

from autosar.xml.base import ARObject
from autosar.xml.elements._base import ARElement, Identifiable
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import TriggerRef


class DataFilter(ARObject):
    """
    Complex type AR:DATA-FILTER
    Tag variants: 'DATA-FILTER' | 'FILTER'
    """

    def __init__(self,
                 data_filter_type: ar_enum.DataFilterType | None = None,
                 min_val: int | None = None,
                 max_val: int | None = None,
                 mask: int | None = None,
                 offset: int | None = None,
                 period: int | None = None,
                 x: int | None = None,                # pylint: disable=C0103
                 ) -> None:
        super().__init__()
        self.data_filter_type: ar_enum.DataFilterType | None = None
        self.min_val: int | None = None
        self.max_val: int | None = None
        self.mask: int | None = None
        self.offset: int | None = None
        self.period: int | None = None
        self.x: int | None = None                     # pylint: disable=C0103
        self._assign_optional("data_filter_type", data_filter_type, ar_enum.DataFilterType)  # .DATA-FILTER-TYPE
        self._assign_optional("mask", mask, int)  # .MASK
        self._assign_optional("max_val", max_val, int)  # .MAX
        self._assign_optional("min_val", min_val, int)  # .MIN
        self._assign_optional("offset", offset, int)  # .OFFSET
        self._assign_optional("period", period, int)  # .PERIOD
        self._assign_optional("x", x, int)  # .X


class EngineeringObject(ARObject):
    """
    Group AR:ENGINEERING-OBJECT
    """

    def __init__(self,
                 label: str | None = None,
                 category: str | None = None) -> None:
        super().__init__()
        self.label: str | None = None  # .SHORT-LABEL
        self.category: str | None = None  # .CATEGORY
        self._assign_optional_strict("label", label, str)
        self._assign_optional_strict("category", category, str)


class AutosarEngineeringObject(EngineeringObject):
    """
    Complex type AR:AUTOSAR-ENGINEERING-OBJECT
    Tag variants: 'ARTIFACT-DESCRIPTOR' | 'AUTOSAR-ENGINEERING-OBJECT'

    Same constructor as parent class
    """


class Code(Identifiable):
    """
    Complex type AR:CODE
    Tag variants: 'CODE'
    """

    def __init__(self,
                 name: str,
                 artifact_descriptors: AutosarEngineeringObject | list[AutosarEngineeringObject] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.artifact_descriptors: list[AutosarEngineeringObject] = []  # .
        # .CALLBACK-HEADER-REFS not yet supported
        if artifact_descriptors is not None:
            if isinstance(artifact_descriptors, AutosarEngineeringObject):
                self.append_artifact_descriptor(artifact_descriptors)
            else:
                for artifact_descriptor in artifact_descriptors:
                    self.append_artifact_descriptor(artifact_descriptor)

    def append_artifact_descriptor(self, artifact_descriptor: AutosarEngineeringObject) -> None:
        """
        Appends artifact_descriptor to internal list of descriptors
        """
        if isinstance(artifact_descriptor, AutosarEngineeringObject):
            self.artifact_descriptors.append(artifact_descriptor)
        else:
            raise TypeError("artifact_descriptor must be of type AutosarEngineeringObject")


class Implementation(ARElement):
    """
    Group AR:IMPLEMENTATION
    """

    def __init__(self,
                 name: str,
                 code_descriptors: Code | list[Code] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .BUILD-ACTION-MANIFEST-REF-CONDITIONAL not yet supported
        self.code_descriptors: list[Code] = []  # .CODE-DESCRIPTORS
        # .COMPILERS not yet supported
        # .GENERATED-ARTIFACTS not yet supported
        # .HW-ELEMENT-REFS not yet supported
        # .LINKERS not yet supported
        # .MC-SUPPORT not yet supported
        # .PROGRAMMING-LANGUAGE not yet supported
        # .REQUIRED-ARTIFACTS not yet supported
        # .REQUIRED-GENERATOR-TOOLS not yet supported
        # .RESOURCE-CONSUMPTION not yet supported
        # .SW-VERSION not yet supported
        # .SWC-BSW-MAPPING-REF not yet supported
        # .USED-CODE-GENERATOR not yet supported
        # .VENDOR-ID not yet supported
        if code_descriptors is not None:
            if isinstance(code_descriptors, Code):
                self.append_code_descriptor(code_descriptors)
            else:
                for code_descriptor in code_descriptors:
                    self.append_code_descriptor(code_descriptor)

    def append_code_descriptor(self, code_descriptors: Code) -> None:
        """
        Appends code descriptor to internal list of descriptors
        """
        if isinstance(code_descriptors, Code):
            self.code_descriptors.append(code_descriptors)
        else:
            raise TypeError("code_descriptors must be of type Code")


class MultidimensionalTime(ARObject):
    """
    Complex type AR:MULTIDIMENSIONAL-TIME
    Tag variants: 'ACCURACY' | 'ACCURACY-EXT' | 'ACCURACY-INT' | 'AGE' |
                  'BEST-CASE-EXECUTION-TIME' | 'ESTIMATED-EXECUTION-TIME' | 'JITTER' |
                  'LOWER-BOUND' | 'MAXIMUM' | 'MAXIMUM-EXECUTION-TIME' |
                  'MAXIMUM-INTER-ARRIVAL-TIME' | 'MINIMUM' | 'MINIMUM-EXECUTION-TIME' |
                  'MINIMUM-INTER-ARRIVAL-TIME' | 'NOMINAL' | 'NOMINAL-EXECUTION-TIME' |
                  'PATTERN-JITTER' | 'PATTERN-LENGTH' | 'PATTERN-PERIOD' | 'PERIOD' |
                  'SIGNAL-AGE' | 'SW-REFRESH-TIMING' | 'TIME-VALUE' | 'TOLERANCE' |
                  'TRIGGER-PERIOD' | 'UPPER-BOUND' | 'WORST-CASE-EXECUTION-TIME'

    """

    def __init__(self, time_base: int | None = None, scaling_factor: int | None = None) -> None:
        # .CSE-CODE
        self.time_base: int | None = None
        # .CSE-CODE-FACTOR
        self.scaling_factor: int | None = None

        self._assign_optional("time_base", time_base, int)
        self._assign_optional("scaling_factor", scaling_factor, int)


class Trigger(Identifiable):
    """
    Complex type AR:TRIGGER
    Tag variants: 'TRIGGER'
    """

    def __init__(self,
                 name: str,
                 sw_impl_policy: ar_enum.SwImplPolicy | None = None,
                 trigger_period: MultidimensionalTime | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .SW-IMPL-POLICY
        self.sw_impl_policy: ar_enum.SwImplPolicy | None = None
        # .TRIGGER-PERIOD
        self.trigger_period: MultidimensionalTime | None = None

        self._assign_optional("sw_impl_policy", sw_impl_policy, ar_enum.SwImplPolicy)
        self._assign_optional_strict("trigger_period", trigger_period, MultidimensionalTime)

    def ref(self) -> TriggerRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else TriggerRef(ref_str)


__all__ = [
    "DataFilter",
    "EngineeringObject",
    "AutosarEngineeringObject",
    "Code",
    "Implementation",
    "MultidimensionalTime",
    "Trigger",
]
