"""Constant elements."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Union

from autosar.xml.base import ARObject, convenience_function
from autosar.xml.elements._base import ARElement, NumericalValue
from autosar.xml.elements.data_type import ValueList
from autosar.xml.elements.calibration_data import SwAxisCont, SwValueCont
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except
from autosar.xml.reference import (
    ConstantRef,
    ConstantSpecificationMappingSetRef,
    DataPrototypeRef,
    UnitRef,
)

ValueSpecificationElement = Union[
    "TextValueSpecification",
    "NumericalValueSpecification",
    "NotAvailableValueSpecification",
    "ArrayValueSpecification",
    "RecordValueSpecification",
    "ApplicationValueSpecification",
    "ConstantReference",
    "ReferenceValueSpecification",
    "NumericalRuleBasedValueSpecification",
    "ApplicationRuleBasedValueSpecification",
    "CompositeRuleBasedValueSpecification",
]

InitValueArgType = Union[
    int,
    float,
    str,
    list,
    tuple,
    ValueSpecificationElement,
    ConstantRef,
    DataPrototypeRef,
]


class ValueSpecification(ARObject):
    """
    Group AR:VALUE-SPECIFICATION
    Base class for value specifications
    """

    def __init__(self, label: str | None = None) -> None:
        self.label = label  # .SHORT-LABEL
        # .VARIATION-POINT not supported

    @convenience_function
    @classmethod
    def make_value_with_check(cls,
                              value: InitValueArgType | None = None,
                              ) -> ValueSpecificationElement | None:
        """

        Wrapper for checking and creating init values based on different value types

        The main differences compared to make_value are:
        * Returns None if input value is None.
        * Can create ConstantReference objects if given ConstantRef input.
        """
        if value is not None:
            if isinstance(value, ValueSpecification):
                return value  # Already a proper init-value
            elif isinstance(value, ConstantRef):
                return ConstantReference(value)  # Wrap inside constant reference
            elif isinstance(value, DataPrototypeRef):
                return ReferenceValueSpecification(value)
            elif isinstance(value, RuleBasedValueSpecification):
                return NumericalRuleBasedValueSpecification(rule_based_values=value)
            elif isinstance(value, (int, float, str, list, tuple)):
                return cls.make_value(value)  # Attempt to create a new value based on raw python data
            else:
                raise TypeError(f"Unsupported type: {str(type(value))}")
        return None

    @convenience_function
    @classmethod
    def make_value(cls, data: Any) -> ValueSpecificationElement:
        """

        Builds value specification based on Python data
        Format 1 - data is not a tuple:
          value = data
        Format 2 - data is 2-tuple:
          label = data[0]
          value = data[1]
        Format 3 - data is a 3-tuple:
          label = data[0]
          value = None
          default_pattern = data[2]
          This format is used only when creating NotAvailableValueSpecification

        The type of 'value' can be one of:

        1. scalar value (int, float, str)
        2. list: (used for array and record values)
           When using list, the first list-element must contain a string which acts as a
           marker indicating what kind of element you want to create.
           - "A" or "ARRAY": Will use remaining list elements to create an ArrayValueSpecification
           - "R" or "RECORD": Will use remaining list elements to create an RecordValueSpecification
        3. None: used for creating NotAvailableValueSpecification
        """
        label = None
        default_pattern = None
        if isinstance(data, tuple):
            if not isinstance(data[0], str):
                raise TypeError("First tuple element must be a string")
            if len(data) == 2:
                label, value = data
            elif len(data) == 3:
                label, value, default_pattern = data
            else:
                raise ValueError(f"Too many elements in tuple: {repr(data)}")
        else:
            value = data
        return ValueSpecification._make_from_args(label, value, default_pattern)

    @classmethod
    def _make_from_args(cls, label: str | None,
                        value: Any,
                        default_pattern: int | None = None) -> ValueSpecificationElement:
        if isinstance(value, (int, float)):
            return NumericalValueSpecification(label, value)
        elif isinstance(value, str):
            return TextValueSpecification(label, value)
        elif value is None:
            return NotAvailableValueSpecification(label, default_pattern)
        elif isinstance(value, list):
            if not isinstance(value[0], str):
                raise TypeError("First element of a list must be a string")
            if value[0].upper() in ("A", "ARRAY"):
                return ValueSpecification._make_array_value_specification(label, value[1:])
            elif value[0].upper() in ("R", "RECORD"):
                return ValueSpecification._make_record_value_specification(label, value[1:])
            else:
                raise ValueError(f"Invalid element type: {str(type(value[0]))}")
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")

    @classmethod
    def _make_array_value_specification(cls, label: str | None, values: list) -> "ArrayValueSpecification":
        elements = []
        for value in values:
            elements.append(ValueSpecification.make_value(value))
        return ArrayValueSpecification(label, elements)

    @classmethod
    def _make_record_value_specification(cls, label: str | None, values: list) -> "RecordValueSpecification":
        fields = []
        for value in values:
            fields.append(ValueSpecification.make_value(value))
        return RecordValueSpecification(label, fields)


class TextValueSpecification(ValueSpecification):
    """
    Complex type AR:TEXT-VALUE-SPECIFICATION
    Tag variants: 'META-DATA-ITEM-TYPE' | 'TEXT-VALUE-SPECIFICATION'
    """

    def __init__(self, label: str | None = None, value: str | None = None) -> None:
        super().__init__(label)
        self.value = None if value is None else str(value)


class NumericalValueSpecification(ValueSpecification):
    """
    Complex type AR:NUMERICAL-VALUE-SPECIFICATION
    Tag variants: 'NUMERICAL-VALUE-SPECIFICATION'
    """

    def __init__(self, label: str | None = None, value: int | float | None = None) -> None:
        super().__init__(label)
        self.value = value


class NotAvailableValueSpecification(ValueSpecification):
    """
    Complex type AR:NOT-AVAILABLE-VALUE-SPECIFICATION
    Tag variants: 'NOT-AVAILABLE-VALUE-SPECIFICATION'
    Status: Draft (AUTOSAR R20-11 / schema 50)
    """

    def __init__(self,
                 label: str | None = None,
                 default_pattern: int | None = None,
                 default_pattern_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        super().__init__(label)
        if isinstance(default_pattern, int) and default_pattern < 0:
            raise ValueError("default_pattern must be a positive integer")
        self.default_pattern = default_pattern
        self.default_pattern_format = default_pattern_format  # Currently not used


class ReferenceValueSpecification(ValueSpecification):
    """
    Complex type AR:REFERENCE-VALUE-SPECIFICATION
    Tag variants: 'REFERENCE-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 reference_value: DataPrototypeRef | None = None,
                 label: str | None = None) -> None:
        super().__init__(label)
        # .REFERENCE-VALUE-REF
        self.reference_value: DataPrototypeRef | None = None
        self._assign_optional_strict("reference_value", reference_value, DataPrototypeRef)


class ArrayValueSpecification(ValueSpecification):
    """
    Complex type AR:ARRAY-VALUE-SPECIFICATION
    Tag variants: 'ARRAY-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 label: str | None = None,
                 elements: list[ValueSpecificationElement] | None = None
                 ) -> None:
        super().__init__(label)
        self.elements: list[ValueSpecificationElement] = []
        if elements is not None:
            if isinstance(elements, ValueSpecification):
                self.append(elements)
            elif isinstance(elements, list):
                for element in elements:
                    self.append(element)

    def append(self, element: ValueSpecificationElement):
        """
        Appends element to array specification
        """
        if not isinstance(element, ValueSpecification):
            raise TypeError(f"Invalid type for 'element': {str(type(element))}")
        self.elements.append(element)


class RecordValueSpecification(ValueSpecification):
    """
    Complex type AR:RECORD-VALUE-SPECIFICATION
    Tag variants: 'RECORD-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 label: str | None = None,
                 fields: list[ValueSpecificationElement] | None = None
                 ) -> None:
        super().__init__(label)
        self.fields: list[ValueSpecificationElement] = []
        if fields is not None:
            if isinstance(fields, ValueSpecification):
                self.append(fields)
            elif isinstance(fields, list):
                for field in fields:
                    self.append(field)

    def append(self, field: ValueSpecificationElement):
        """
        Appends field to record specification
        """
        if not isinstance(field, ValueSpecification):
            raise TypeError(f"Invalid type for 'field': {str(type(field))}")
        self.fields.append(field)


class ApplicationValueSpecification(ValueSpecification):
    """
    Complex type AR:APPLICATION-VALUE-SPECIFICATION
    Tag variants: 'APPLICATION-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 label: str | None = None,
                 category: str | None = None,
                 sw_axis_conts: SwAxisCont | list[SwAxisCont] | None = None,
                 sw_value_cont: SwValueCont | None = None
                 ) -> None:
        super().__init__(label)
        self.category: str = None
        self.sw_axis_conts: list[SwAxisCont] = []
        self.sw_value_cont: SwValueCont = None
        self._assign_optional_strict("category", category, str)
        self._assign_optional_strict("sw_value_cont", sw_value_cont, SwValueCont)
        if sw_axis_conts is not None:
            if isinstance(sw_axis_conts, SwAxisCont):
                self.sw_axis_conts.append(sw_axis_conts)
            elif isinstance(sw_axis_conts, list):
                for elem in sw_axis_conts:
                    if isinstance(elem, SwAxisCont):
                        self.sw_axis_conts.append(elem)
                    else:
                        error_msg = "sw_axis_conts: Elements in list must of type SwAxisCont."
                        raise TypeError(error_msg + f" Got {str(type(elem))}")
            else:
                error_msg = "sw_axis_conts: argument must be either SwAxisCont or list[SwAxisCont]."
                raise TypeError(error_msg + f" Got {str(type(sw_axis_conts))}")


class ConstantSpecification(ARElement):
    """
    Complex type AR:CONSTANT-SPECIFICATION
    Tag variants: 'CONSTANT-SPECIFICATION'
    """

    def __init__(self, name: str, value: ValueSpecificationElement | None = None, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.value: ValueSpecificationElement = None  # .VALUE-SPEC
        if value is not None:
            if isinstance(value, ValueSpecification):
                self.value = value
            else:
                error_msg = "Invalid type for parameter 'value'. Expected a subclass of ValueSpecification,"
                raise TypeError(error_msg + f" got {str(type(value))}")

    def ref(self) -> ConstantRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ConstantRef(ref_str)

    @convenience_function
    @classmethod
    def make_constant(cls,
                      name: str,
                      value: tuple[str, Any] | Any,
                      **kwargs) -> "ConstantSpecification":
        """
        Creates a new constant object and populates it from Python data.
        """
        value = ValueSpecification.make_value(value)
        return cls(name, value, **kwargs)


class ConstantReference(ValueSpecification):
    """
    Complex type AR:CONSTANT-REFERENCE
    Tag variants: 'CONSTANT-REFERENCE'

    It's easy to confuse this with the ConstantRef class.
    This class is just a wrapper around an instance of ConstantRef.
    """

    def __init__(self,
                 constant_ref: ConstantRef | str | None = None,
                 label: str | None = None) -> None:
        self.constant_ref: ConstantRef = None
        super().__init__(label)
        if constant_ref is not None:
            if isinstance(constant_ref, str):
                self.constant_ref = ConstantRef(constant_ref)
            elif isinstance(constant_ref, ConstantRef):
                self.constant_ref = constant_ref
            else:
                raise ar_except.AssignmentTypeError("constant_ref", ("ConstantRef", "str"), constant_ref)


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
        self._assign_optional_strict("vf", vf, (int, float, NumericalValue))
        self._assign_optional_strict("vt", vt, str)


RuleArgumentElement = Union[int, float, str, NumericalValue, "NumericalOrText"]


class RuleArguments(ARObject):
    """
    Complex type AR:RULE-ARGUMENTS
    Tag variants: 'RULE-ARGUMENTS'
    """

    def __init__(self,
                 values: list[RuleArgumentElement] | RuleArgumentElement | None = None) -> None:
        self.values: list[RuleArgumentElement] = []
        if values is not None:
            if isinstance(values, list):
                for value in values:
                    self.append(value)
            else:
                self.append(values)

    def append(self, value: RuleArgumentElement) -> None:
        """
        Appends value to list of values
        """
        if isinstance(value, (int, float, str, NumericalValue, NumericalOrText)):
            self.values.append(value)
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")


class RuleBasedValueSpecification(ARObject):
    """
    Complex type AR:RULE-BASED-VALUE-SPECIFICATION
    Tag variants: 'RULE-BASED-VALUE-SPECIFICATION' | 'RULE-BASED-VALUES'
    """

    def __init__(self,
                 rule: str | None = None,
                 arguments: list[RuleArguments] | RuleArguments | None = None,
                 max_size_to_fill: int | None = None) -> None:
        # .RULE
        self.rule: str | None = None
        # .ARGUMENTS (XML: ARGUMENTSS/RULE-ARGUMENTS)
        self.arguments: list[RuleArguments] = []
        # .MAX-SIZE-TO-FILL
        self.max_size_to_fill: int | None = None
        self._assign_optional_strict("rule", rule, str)
        if arguments is not None:
            if isinstance(arguments, RuleArguments):
                self.append(arguments)
            elif isinstance(arguments, list):
                for argument in arguments:
                    self.append(argument)
            else:
                raise TypeError(f"Invalid type for 'arguments': {str(type(arguments))}")
        self._assign_optional_strict("max_size_to_fill", max_size_to_fill, int)

    def append(self, argument: RuleArguments) -> None:
        """
        Appends a RuleArguments object to the arguments list
        """
        if isinstance(argument, RuleArguments):
            self.arguments.append(argument)
        else:
            raise TypeError(f"Invalid type for 'argument': {str(type(argument))}")


class RuleBasedAxisCont(ARObject):
    """
    Complex type AR:RULE-BASED-AXIS-CONT
    Tag variants: 'RULE-BASED-AXIS-CONT'
    """

    def __init__(self,
                 category: ar_enum.CalibrationAxisCategory | None = None,
                 unit_ref: UnitRef | None = None,
                 sw_axis_index: int | str | None = None,
                 sw_array_size: ValueList | None = None,
                 rule_based_values: RuleBasedValueSpecification | None = None) -> None:
        # .CATEGORY
        self.category: ar_enum.CalibrationAxisCategory | None = None
        # .UNIT-REF
        self.unit_ref: UnitRef | None = None
        # .SW-AXIS-INDEX
        self.sw_axis_index: int | str | None = None
        # .SW-ARRAYSIZE
        self.sw_array_size: ValueList | None = None
        # .RULE-BASED-VALUES
        self.rule_based_values: RuleBasedValueSpecification | None = None
        self._assign_optional("category", category, ar_enum.CalibrationAxisCategory)
        self._assign_optional_strict("unit_ref", unit_ref, UnitRef)
        if sw_axis_index is not None:
            if isinstance(sw_axis_index, (int, str)):
                self.sw_axis_index = sw_axis_index
            else:
                error_msg = "Invalid type for parameter 'sw_axis_index'. Expected 'int' or 'str', "
                raise TypeError(error_msg + f"got '{str(type(sw_axis_index))}'")
        self._assign_optional_strict("sw_array_size", sw_array_size, ValueList)
        self._assign_optional_strict("rule_based_values", rule_based_values, RuleBasedValueSpecification)


class RuleBasedValueCont(ARObject):
    """
    Complex type AR:RULE-BASED-VALUE-CONT
    Tag variants: 'RULE-BASED-VALUE-CONT'
    """

    def __init__(self,
                 unit_ref: UnitRef | None = None,
                 sw_array_size: ValueList | None = None,
                 rule_based_values: RuleBasedValueSpecification | None = None) -> None:
        # .UNIT-REF
        self.unit_ref: UnitRef | None = None
        # .SW-ARRAYSIZE
        self.sw_array_size: ValueList | None = None
        # .RULE-BASED-VALUES
        self.rule_based_values: RuleBasedValueSpecification | None = None
        self._assign_optional_strict("unit_ref", unit_ref, UnitRef)
        self._assign_optional_strict("sw_array_size", sw_array_size, ValueList)
        self._assign_optional_strict("rule_based_values", rule_based_values, RuleBasedValueSpecification)


class NumericalRuleBasedValueSpecification(ValueSpecification):
    """
    Complex type AR:NUMERICAL-RULE-BASED-VALUE-SPECIFICATION
    Tag variants: 'NUMERICAL-RULE-BASED-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 rule_based_values: RuleBasedValueSpecification | None = None,
                 label: str | None = None) -> None:
        super().__init__(label)
        # .RULE-BASED-VALUES
        self.rule_based_values: RuleBasedValueSpecification | None = None
        self._assign_optional_strict("rule_based_values", rule_based_values, RuleBasedValueSpecification)


class ApplicationRuleBasedValueSpecification(ValueSpecification):
    """
    Complex type AR:APPLICATION-RULE-BASED-VALUE-SPECIFICATION
    Tag variants: 'APPLICATION-RULE-BASED-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 category: str | None = None,
                 sw_axis_conts: RuleBasedAxisCont | list[RuleBasedAxisCont] | None = None,
                 sw_value_cont: RuleBasedValueCont | None = None,
                 label: str | None = None) -> None:
        super().__init__(label)
        # .CATEGORY
        self.category: str | None = None
        # .SW-AXIS-CONTS
        self.sw_axis_conts: list[RuleBasedAxisCont] = []
        # .SW-VALUE-CONT
        self.sw_value_cont: RuleBasedValueCont | None = None
        self._assign_optional_strict("category", category, str)
        self._assign_optional_strict("sw_value_cont", sw_value_cont, RuleBasedValueCont)
        if sw_axis_conts is not None:
            if isinstance(sw_axis_conts, RuleBasedAxisCont):
                self.sw_axis_conts.append(sw_axis_conts)
            elif isinstance(sw_axis_conts, list):
                for elem in sw_axis_conts:
                    if isinstance(elem, RuleBasedAxisCont):
                        self.sw_axis_conts.append(elem)
                    else:
                        raise TypeError(f"Expected RuleBasedAxisCont, got {str(type(elem))}")
            else:
                raise TypeError(f"Invalid type for 'sw_axis_conts': {str(type(sw_axis_conts))}")

    def append(self, item: RuleBasedAxisCont) -> None:
        """
        Appends RuleBasedAxisCont to sw_axis_conts list
        """
        if isinstance(item, RuleBasedAxisCont):
            self.sw_axis_conts.append(item)
        else:
            raise TypeError(f"Invalid type for 'item': {str(type(item))}")


CompoundPrimitiveArgType = Union["ApplicationRuleBasedValueSpecification", "ApplicationValueSpecification"]


class CompositeRuleBasedValueSpecification(ValueSpecification):
    """
    Complex type AR:COMPOSITE-RULE-BASED-VALUE-SPECIFICATION
    Tag variants: 'COMPOSITE-RULE-BASED-VALUE-SPECIFICATION'
    """

    def __init__(self,
                 rule: str | None = None,
                 arguments: list[ValueSpecificationElement] | ValueSpecificationElement | None = None,
                 compound_primitive_arguments: list[CompoundPrimitiveArgType] | CompoundPrimitiveArgType | None = None,
                 max_size_to_fill: int | None = None,
                 label: str | None = None) -> None:
        super().__init__(label)
        # .RULE
        self.rule: str | None = None
        # .ARGUMENTS (XML: ARGUMENTS/...)
        self.arguments: list[ValueSpecificationElement] = []
        # .COMPOUND-PRIMITIVE-ARGUMENTS (XML: COMPOUND-PRIMITIVE-ARGUMENTS/...)
        self.compound_primitive_arguments: list[CompoundPrimitiveArgType] = []
        # .MAX-SIZE-TO-FILL
        self.max_size_to_fill: int | None = None
        self._assign_optional_strict("rule", rule, str)
        if arguments is not None:
            if isinstance(arguments, ValueSpecification):
                self.append_argument(arguments)
            elif isinstance(arguments, list):
                for arg in arguments:
                    self.append_argument(arg)
            else:
                raise TypeError(f"Invalid type for 'arguments': {str(type(arguments))}")
        if compound_primitive_arguments is not None:
            if isinstance(compound_primitive_arguments,
                          (ApplicationRuleBasedValueSpecification, ApplicationValueSpecification)):
                self.append_compound_primitive_argument(compound_primitive_arguments)
            elif isinstance(compound_primitive_arguments, list):
                for arg in compound_primitive_arguments:
                    self.append_compound_primitive_argument(arg)
            else:
                raise TypeError(
                    f"Invalid type for 'compound_primitive_arguments': {str(type(compound_primitive_arguments))}")
        self._assign_optional_strict("max_size_to_fill", max_size_to_fill, int)

    def append_argument(self, argument: ValueSpecificationElement) -> None:
        """
        Appends ValueSpecification to arguments list
        """
        if isinstance(argument, ValueSpecification):
            self.arguments.append(argument)
        else:
            raise TypeError(f"Invalid type for 'argument': {str(type(argument))}")

    def append_compound_primitive_argument(self, argument: CompoundPrimitiveArgType) -> None:
        """
        Appends compound primitive argument
        """
        if isinstance(argument, (ApplicationRuleBasedValueSpecification, ApplicationValueSpecification)):
            self.compound_primitive_arguments.append(argument)
        else:
            raise TypeError(f"Invalid type for 'argument': {str(type(argument))}")


class ConstantSpecificationMapping(ARObject):
    """
    Complex type AR:CONSTANT-SPECIFICATION-MAPPING
    Tag variants: 'CONSTANT-SPECIFICATION-MAPPING'
    """

    def __init__(self,
                 appl_constant_ref: ConstantRef | str | None = None,
                 impl_constant_ref: ConstantRef | str | None = None,
                 ) -> None:
        # .APPL-CONSTANT-REF
        self.appl_constant_ref: ConstantRef | None = None
        # .IMPL-CONSTANT-REF
        self.impl_constant_ref: ConstantRef | None = None
        self._assign_optional('appl_constant_ref', appl_constant_ref, ConstantRef)
        self._assign_optional('impl_constant_ref', impl_constant_ref, ConstantRef)


class ConstantSpecificationMappingSet(ARElement):
    """
    Complex type AR:CONSTANT-SPECIFICATION-MAPPING-SET
    Tag variants: 'CONSTANT-SPECIFICATION-MAPPING-SET'
    """

    def __init__(self,
                 name: str,
                 mappings: ConstantSpecificationMapping | list[ConstantSpecificationMapping] | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        # .MAPPINGS
        self.mappings: list[ConstantSpecificationMapping] = []

        if mappings is not None:
            if isinstance(mappings, ConstantSpecificationMapping):
                self.append(mappings)
            elif isinstance(mappings, Iterable):
                for mapping in mappings:
                    self.append(mapping)
            else:
                raise TypeError(f'mappings: Invalid type "{str(type(mappings))}"')

    def append(self, mapping: ConstantSpecificationMapping) -> None:
        """
        Appends ConstantSpecificationMapping to mappings list
        """
        if isinstance(mapping, ConstantSpecificationMapping):
            self.mappings.append(mapping)
        else:
            raise TypeError(f'mapping: Expected type "ConstantSpecificationMapping", got "{str(type(mapping))}"')

    def ref(self) -> ConstantSpecificationMappingSetRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ConstantSpecificationMappingSetRef(ref_str)


__all__ = [
    "ValueSpecificationElement",
    "InitValueArgType",
    "RuleArgumentElement",
    "CompoundPrimitiveArgType",
    "ValueSpecification",
    "TextValueSpecification",
    "NumericalValueSpecification",
    "NotAvailableValueSpecification",
    "ReferenceValueSpecification",
    "ArrayValueSpecification",
    "RecordValueSpecification",
    "ApplicationValueSpecification",
    "ConstantSpecification",
    "ConstantReference",
    "NumericalOrText",
    "RuleArguments",
    "RuleBasedValueSpecification",
    "RuleBasedAxisCont",
    "RuleBasedValueCont",
    "NumericalRuleBasedValueSpecification",
    "ApplicationRuleBasedValueSpecification",
    "CompositeRuleBasedValueSpecification",
    "ConstantSpecificationMapping",
    "ConstantSpecificationMappingSet",
]
