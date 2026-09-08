"""Calibration data elements."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

from autosar.xml.base import ARObject
from autosar.xml.elements._base import NumericalValue
from autosar.xml.elements.documentation import (
    LanguageLongName,
    MultilanguageLongName,
    SingleLanguageUnitNames,
)
from autosar.xml.elements.data_type import ValueList
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import UnitRef

if TYPE_CHECKING:
    from autosar.xml.elements.constant import NumericalOrText


def _get_numerical_or_text_class():
    from autosar.xml.elements.constant import NumericalOrText
    return NumericalOrText


SwValueElement = Union[int, float, str, NumericalValue, "ValueGroup", "NumericalOrText"]  # Type alias


class SwValues(ARObject):
    """
    Complex type AR:SW-VALUES
    Tag variants: 'SW-VALUES-PHYS'
    """

    def __init__(self,
                 values: list[SwValueElement] | SwValueElement | None = None) -> None:
        self.values = []
        if values is not None:
            NumericalOrText = _get_numerical_or_text_class()
            if isinstance(values, (int, float, str, NumericalValue, ValueGroup, NumericalOrText)):
                self.append(values)
            elif isinstance(values, list):
                for value in values:
                    self.append(value)

    def append(self, value: SwValueElement) -> None:
        """
        Appends value to list of values
        """
        NumericalOrText = _get_numerical_or_text_class()
        if isinstance(value, (int, float, str, NumericalValue, ValueGroup, NumericalOrText)):
            self.values.append(value)
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")


class ValueGroup(SwValues):
    """
    Complex type AR:VALUE-GROUP
    Tag variants: 'VG'
    """

    def __init__(self,
                 label: str | MultilanguageLongName | tuple[ar_enum.Language, str] | LanguageLongName | None = None,
                 values: SwValues | None = None) -> None:
        self.label: MultilanguageLongName | None = None
        super().__init__(values)
        if label is not None:
            if isinstance(label, MultilanguageLongName):
                self.label = label
            elif isinstance(label, (tuple, LanguageLongName)):
                self.label = MultilanguageLongName(label)
            else:
                raise TypeError(f"Invalid type for 'label': {str(type(label))}")


class SwAxisCont(ARObject):
    """
    Complex type AR:SW-AXIS-CONT
    Tag variants: 'SW-AXIS-CONT'
    """

    def __init__(self,
                 category: ar_enum.CalibrationAxisCategory | None = None,
                 unit_ref: UnitRef | None = None,
                 unit_display_name: SingleLanguageUnitNames | None = None,
                 sw_axis_index: int | str | None = None,
                 sw_array_size: ValueList | None = None,
                 sw_values_phys: SwValues | None = None) -> None:
        self.category: ar_enum.CalibrationAxisCategory = None  # .CATEGORY
        self.unit_ref: UnitRef = None  # .UNIT-REF
        self.unit_display_name: SingleLanguageUnitNames = None  # .UNIT-DISPLAY_NAME
        self.sw_axis_index: int | str = None  # .SW-AXIS-INDEX
        self.sw_array_size: ValueList = None  # .SW-ARRAYSIZE
        self.sw_values_phys: SwValues = None  # .SW-VALUES-PHYS
        self._assign_optional('category', category, ar_enum.CalibrationAxisCategory)
        self._assign_optional_strict('unit_ref', unit_ref, UnitRef)
        self._assign_optional_strict('unit_display_name', unit_display_name, SingleLanguageUnitNames)
        if sw_axis_index is not None:
            if isinstance(sw_axis_index, (int, str)):
                self.sw_axis_index = sw_axis_index
            else:
                error_msg = "Invalid type for parameter 'sw_axis_index'. Expected 'int' or 'str', "
                raise TypeError(error_msg + f"got '{str(type(sw_axis_index))}'")
        self._assign_optional_strict('sw_array_size', sw_array_size, ValueList)
        self._assign_optional_strict('sw_values_phys', sw_values_phys, SwValues)


class SwValueCont(ARObject):
    """
    Complex type AR:SW-VALUE-CONT
    Tag variants: 'SW-VALUE-CONT'
    """

    def __init__(self,
                 unit_ref: UnitRef | None = None,
                 unit_display_name: SingleLanguageUnitNames | None = None,
                 sw_array_size: ValueList | None = None,
                 sw_values_phys: SwValues | None = None) -> None:
        self.unit_ref: UnitRef = None  # .UNIT-REF
        self.unit_display_name: SingleLanguageUnitNames = None  # .UNIT-DISPLAY_NAME
        self.sw_array_size: ValueList = None  # .SW-ARRAYSIZE
        self.sw_values_phys: SwValues = None  # .SW-VALUES-PHYS
        self._assign_optional_strict('unit_ref', unit_ref, UnitRef)
        self._assign_optional_strict('unit_display_name', unit_display_name, SingleLanguageUnitNames)
        self._assign_optional_strict('sw_array_size', sw_array_size, ValueList)
        self._assign_optional_strict('sw_values_phys', sw_values_phys, SwValues)


__all__ = [
    "SwValueElement",
    "SwValues",
    "ValueGroup",
    "SwAxisCont",
    "SwValueCont",
]
