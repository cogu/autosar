"""Auxiliary object elements."""

from __future__ import annotations

from autosar.xml.elements._base import ARElement
from autosar.xml.reference import SwAddrMethodRef


class SwAddrMethod(ARElement):
    """Complex type AR:SW-ADDR-METHOD.

    Tag variants: 'SW-ADDR-METHOD'
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.memory_allocation_keyword_policy = None  # .MEMORY-ALLOCATION-KEYWORD-POLICY
        self.options = []  # .OPTIONS
        self.section_initialization_policy = None  # .SECTION-INITIALIZATION-POLICY
        self.section_type = None  # .SECTION-TYPE

    def ref(self) -> SwAddrMethodRef | None:
        """Return reference to this element or None if not yet part of a package."""
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwAddrMethodRef(ref_str)


__all__ = [
    "SwAddrMethod",
]
