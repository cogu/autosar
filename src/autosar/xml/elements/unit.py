"""Unit elements."""

from __future__ import annotations

from autosar.xml.elements._base import ARElement
from autosar.xml.elements.documentation import SingleLanguageUnitNames
from autosar.xml.reference import PhysicalDimensionRef, UnitRef


class Unit(ARElement):
    """Complex type AR:UNIT.

    Tag variants: 'UNIT'
    """

    def __init__(self, name: str,
                 display_name: str | SingleLanguageUnitNames | None = None,
                 factor: float | None = None,
                 offset: float | None = None,
                 physical_dimension_ref: str | PhysicalDimensionRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.display_name: SingleLanguageUnitNames | None = None  # .DISPLAY-NAME
        self.physical_dimension_ref: PhysicalDimensionRef | None = None  # .PHYSICAL-DIMENSION-REF
        self.factor: float | None = None  # .FACTOR-SI-TO-UNIT
        self.offset: float | None = None  # .OFFSET-SI-TO-UNIT
        if display_name is not None:
            if isinstance(display_name, str):
                self.display_name = SingleLanguageUnitNames(display_name)
            elif isinstance(display_name, SingleLanguageUnitNames):
                self.display_name = display_name
            else:
                raise TypeError(f"display_name: Invalid type '{str(type(display_name))}'")
        if physical_dimension_ref is not None:
            if isinstance(physical_dimension_ref, str):
                self.physical_dimension_ref = PhysicalDimensionRef(physical_dimension_ref)
            elif isinstance(physical_dimension_ref, PhysicalDimensionRef):
                self.physical_dimension_ref = physical_dimension_ref
            else:
                raise TypeError(f"physical_dimension_ref: Invalid type '{str(type(physical_dimension_ref))}'")
        self._assign_optional('factor', factor, float)
        self._assign_optional('offset', offset, float)

    def ref(self) -> UnitRef:
        """Return reference to this element or None if not yet part of a package."""
        ref_str = self._calc_ref_string()
        return None if ref_str is None else UnitRef(ref_str)


__all__ = [
    "Unit",
]
