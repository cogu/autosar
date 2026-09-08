"""Constraint elements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import ARElement
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import DataConstraintRef, UnitRef

if TYPE_CHECKING:
    from autosar.xml.elements.documentation import MultiLanguageOverviewParagraph


class LimitObject(ARObject):
    """Base class for elements that has upper and lower limits."""

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__()
        self.lower_limit = lower_limit              # .LOWER-LIMIT
        self.upper_limit = upper_limit              # .UPPER-LIMIT
        self.lower_limit_type = lower_limit_type    # .LOWER-LIMIT@INTERVAL-TYPE
        self.upper_limit_type = upper_limit_type    # .UPPER-LIMIT@INTERVAL-TYPE

    @property
    def is_empty(self) -> bool:
        """Override is_empty from base class."""
        return self.is_empty_with_ignore({"lower_limit_type", "upper_limit_type"})

    def check_value(self, value: int | float) -> bool:
        """Check if given value is inside the constraint limits."""
        if self.lower_limit_type == ar_enum.IntervalType.CLOSED:
            if value < self.lower_limit:
                return False
        elif value <= self.lower_limit:
            return False
        if self.upper_limit_type == ar_enum.IntervalType.CLOSED:
            if value > self.upper_limit:
                return False
        elif value >= self.upper_limit:
            return False
        return True


class ScaleConstraint(LimitObject):
    """Complex type AR:SCALE-CONSTR.

    Tag variants: 'SCALE-CONSTR'
    """

    def __init__(self,
                 label: str | None = None,
                 desc: MultiLanguageOverviewParagraph | None = None,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 validity: ar_enum.ScaleConstraintValidity | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit, upper_limit, lower_limit_type, upper_limit_type)
        self.label = label
        self.desc = desc
        self.validity = validity


class ConstraintBase(LimitObject):
    """Base class for data constraint rules."""

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 scale_constrs: list[ScaleConstraint] | None = None,
                 max_gradient: int | float | None = None,
                 max_diff: int | float | None = None,
                 monotony: ar_enum.Monotony | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit, upper_limit, lower_limit_type, upper_limit_type)
        self.scale_constrs = list(scale_constrs) if scale_constrs else []
        self.max_gradient = max_gradient
        self.max_diff = max_diff
        self.monotony = monotony


class InternalConstraint(ConstraintBase):
    """Complex type AR:INTERNAL-CONSTRS.

    Tag variants: 'INTERNAL-CONSTRS'
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 scale_constr: list[ScaleConstraint] | None = None,
                 max_gradient: int | float | None = None,
                 max_diff: int | float | None = None,
                 monotony: ar_enum.Monotony | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit,
                         upper_limit,
                         scale_constr,
                         max_gradient,
                         max_diff,
                         monotony,
                         lower_limit_type,
                         upper_limit_type)


class PhysicalConstraint(ConstraintBase):
    """Complex type AR:PHYS-CONSTRS.

    Tag variants: 'PHYS-CONSTRS'
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 scale_constr: list[ScaleConstraint] | None = None,
                 max_gradient: int | float | None = None,
                 max_diff: int | float | None = None,
                 monotony: ar_enum.Monotony | None = None,
                 unit_ref: UnitRef | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        super().__init__(lower_limit,
                         upper_limit,
                         scale_constr,
                         max_gradient,
                         max_diff,
                         monotony,
                         lower_limit_type,
                         upper_limit_type)
        self.unit_ref = unit_ref


class DataConstraintRule(ARObject):
    """Complex type AR:DATA-CONSTR-RULE.

    Tag variants: 'DATA-CONSTR-RULE'
    """

    def __init__(self,
                 internal: InternalConstraint | None = None,
                 physical: PhysicalConstraint | None = None,
                 level: int | None = None) -> None:
        super().__init__()
        self.internal = internal   # .INTERNAL-CONSTRS
        self.physical = physical   # .PHYS-CONSTRS
        self.level = level         # .CONSTR-LEVEL


class DataConstraint(ARElement):
    """Complex type AR:DATA-CONSTR.

    Tag variants: 'DATA-CONSTR'
    """

    def __init__(self, name: str,
                 rules: list[DataConstraintRule] | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.rules = []
        if rules is not None:
            for rule in rules:
                assert isinstance(rule, DataConstraintRule)
            self.rules.extend(rules)

    def ref(self) -> DataConstraintRef:
        """Return reference to this element or None if not yet part of a package."""
        ref_str = self._calc_ref_string()
        return None if ref_str is None else DataConstraintRef(ref_str)

    @convenience_function
    @classmethod
    def make_physical(cls: type[DataConstraint],
                      name: str,
                      lower_limit: int | float | None = None,
                      upper_limit: int | float | None = None,
                      scale_constr: list[ScaleConstraint] | None = None,
                      max_gradient: int | float | None = None,
                      max_diff: int | float | None = None,
                      monotony: ar_enum.Monotony | None = None,
                      unit_ref: UnitRef | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      **kwargs) -> DataConstraint:
        """Create a DataConstraint which contains a single physical constraint."""
        rule = DataConstraintRule(physical=PhysicalConstraint(lower_limit,
                                                              upper_limit,
                                                              scale_constr,
                                                              max_gradient,
                                                              max_diff,
                                                              monotony,
                                                              unit_ref,
                                                              lower_limit_type,
                                                              upper_limit_type))
        return cls(name, [rule], **kwargs)

    @convenience_function
    @classmethod
    def make_internal(cls: type[DataConstraint],
                      name: str,
                      lower_limit: int | float | None = None,
                      upper_limit: int | float | None = None,
                      scale_constr: list[ScaleConstraint] | None = None,
                      max_gradient: int | float | None = None,
                      max_diff: int | float | None = None,
                      monotony: ar_enum.Monotony | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      **kwargs) -> DataConstraint:
        """Create a DataConstraint that contains a single internal constraint."""
        rule = DataConstraintRule(internal=InternalConstraint(lower_limit,
                                                              upper_limit,
                                                              scale_constr,
                                                              max_gradient,
                                                              max_diff,
                                                              monotony,
                                                              lower_limit_type,
                                                              upper_limit_type))
        return cls(name, [rule], **kwargs)


__all__ = [
    "LimitObject",
    "ScaleConstraint",
    "ConstraintBase",
    "InternalConstraint",
    "PhysicalConstraint",
    "DataConstraintRule",
    "DataConstraint",
]
