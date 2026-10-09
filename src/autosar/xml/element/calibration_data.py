"""Calibration data elements."""

from __future__ import annotations

from typing import Union

from autosar.xml.base import ARObject
from autosar.xml.element._base import NumericalValue
from autosar.xml.element.documentation import (
    LanguageLongName,
    MultilanguageLongName,
    SingleLanguageUnitNames,
)
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import UnitRef


class ValueList(ARObject):
    """
    Complex type AR:VALUE-LIST
    Tag variants: 'SW-ARRAYSIZE'
    """

    def __init__(self,
                 values: list[int | float | NumericalValue] | int | float | NumericalValue | None = None
                 ) -> None:
        self.values = []
        if values is not None:
            if isinstance(values, (int, float, NumericalValue)):
                self.append(values)
            else:
                for value in values:
                    self.append(value)

    def append(self, value: int | float | NumericalValue) -> None:
        """
        Adds value to list of values
        """
        if isinstance(value, (int, float, NumericalValue)):
            self.values.append(value)
        else:
            raise TypeError(f"Invalid type for value: {str(type(value))}")


class NumericalOrText(ARObject):
    """
    Complex type AR:NUMERICAL-OR-TEXT
    Tag variants: 'VTF'
    """

    def __init__(self,
                 vf: int | float | NumericalValue | None = None,
                 vt: str | None = None
                 ) -> None:
        # .VF
        self.vf: int | float | NumericalValue | None = None
        # .VT
        self.vt: str | None = None
        # .VARIATION-POINT not supported
        self._assign_optional_strict("vf", vf, (int, float, NumericalValue))  # pyright: ignore[reportArgumentType]
        self._assign_optional_strict("vt", vt, str)


SwValueElement = Union[int, float, str, NumericalValue, "ValueGroup", NumericalOrText]  # Type alias


class SwValues(ARObject):
    """
    Complex type AR:SW-VALUES
    Tag variants: 'SW-VALUES-PHYS'
    """

    def __init__(self,
                 values: list[SwValueElement] | SwValueElement | None = None) -> None:
        self.values = []
        if values is not None:
            if isinstance(values, (int, float, str, NumericalValue, ValueGroup, NumericalOrText)):
                self.append(values)
            elif isinstance(values, list):
                for value in values:
                    self.append(value)

    def append(self, value: SwValueElement) -> None:
        """
        Appends value to list of values
        """
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
                 values: list[SwValueElement] | SwValueElement | None = None) -> None:
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
        self.category: ar_enum.CalibrationAxisCategory | None = None  # .CATEGORY
        self.unit_ref: UnitRef | None = None  # .UNIT-REF
        self.unit_display_name: SingleLanguageUnitNames | None = None  # .UNIT-DISPLAY_NAME
        self.sw_axis_index: int | str | None = None  # .SW-AXIS-INDEX
        self.sw_array_size: ValueList | None = None  # .SW-ARRAYSIZE
        self.sw_values_phys: SwValues | None = None  # .SW-VALUES-PHYS
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
        self.unit_ref: UnitRef | None = None  # .UNIT-REF
        self.unit_display_name: SingleLanguageUnitNames | None = None  # .UNIT-DISPLAY_NAME
        self.sw_array_size: ValueList | None = None  # .SW-ARRAYSIZE
        self.sw_values_phys: SwValues | None = None  # .SW-VALUES-PHYS
        self._assign_optional_strict('unit_ref', unit_ref, UnitRef)
        self._assign_optional_strict('unit_display_name', unit_display_name, SingleLanguageUnitNames)
        self._assign_optional_strict('sw_array_size', sw_array_size, ValueList)
        self._assign_optional_strict('sw_values_phys', sw_values_phys, SwValues)


__all__ = [
    "ValueList",
    "NumericalOrText",
    "SwValueElement",
    "SwValues",
    "ValueGroup",
    "SwAxisCont",
    "SwValueCont",
]
