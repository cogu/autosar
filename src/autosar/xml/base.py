"""
AUTOSAR XML base classes
"""

import abc
import re
from typing import Any, Type
from enum import Enum
import autosar.xml.enumeration as ar_enum


class ARObject:
    """
    Base class for all AUTOSAR objects
    """

    @property
    def is_empty(self) -> bool:
        """
        True if no value has been set (everything is None)
        """
        for value in vars(self).values():
            if isinstance(value, list):
                if len(value) > 0:
                    return False
            else:
                if value is not None:
                    return False
        return True

    def is_empty_with_ignore(self, ignore_set: set) -> bool:
        """
        Same as is_empty but the caller can give
        a list of property names to ignore during
        check
        """
        for key in vars(self).keys():
            if key not in ignore_set:
                value = getattr(self, key)
                if isinstance(value, list):
                    if len(value) > 0:
                        return False
                else:
                    if value is not None:
                        return False
        return True

    def _assign_optional(self, attr_name: str, value: Any, type_name: type) -> None:
        """
        Same as _assign but with a None-check
        """
        if value is not None:
            self._assign(attr_name, value, type_name)

    def _assign(self, attr_name: str, value: Any, type_name: type) -> None:
        """
        Assign single value to attribute with type check.
        """
        if issubclass(type_name, Enum):
            self._set_attr_with_strict_type(attr_name, value, type_name)
        elif issubclass(type_name, BaseRef):
            self._check_and_set_reference(attr_name, value, type_name)
        else:
            self._set_attr_with_type_cast(attr_name, value, type_name)

    def _assign_int_or_str_pattern_optional(self, attr_name: str, value: int | str | None, pattern: re.Pattern) -> None:
        """
        Same as _assign_int_or_str_pattern but with a None-check
        """
        if value is not None:
            self._assign_int_or_str_pattern(attr_name, value, pattern)

    def _assign_int_or_str_pattern(self, attr_name: str, value: int | str, pattern: re.Pattern) -> None:
        """
        Special assignment-function for values that can be either int or conforms
        to a specific regular expression
        """
        if isinstance(value, int):
            pass
        elif isinstance(value, str):
            match = pattern.match(value)
            if match is None:
                raise ValueError(f"Invalid parameter '{value}' for '{attr_name}'")
        else:
            raise TypeError(f"{attr_name}: Invalid type. Expected (int, str), got '{str(type(value))}'")
        setattr(self, attr_name, value)

    def _assign_optional_strict(self, attr_name: str, value: Any, type_name: type) -> None:
        """
        Sets object attribute with strict type check
        """
        if value is not None:
            self._set_attr_with_strict_type(attr_name, value, type_name)

    def _assign_optional_positive_int(self, attr_name, value: int) -> None:
        """
        Checks that the optional value is a positive integer before assignment
        """
        if value is not None:
            self._set_attr_positive_int(attr_name, value)

    def _set_attr_with_strict_type(self, attr_name: str, value: Any, type_class: type) -> None:
        """
        Sets object attribute only if the value is matches given type-class
        """
        if isinstance(value, type_class):
            setattr(self, attr_name, value)
        else:
            raise TypeError(
                f"Invalid type for parameter '{attr_name}'. Expected type {str(type_class)}, got {str(type(value))}")

    def _check_and_set_reference(self, attr_name: str, value: Any, ref_type: Type["BaseRef"]):
        """
        Checks reference type compatibility and on success updates the value
        """
        accepted_sub_types: set = ref_type.accepted_sub_types()
        if (len(accepted_sub_types) == 0) or not isinstance(accepted_sub_types, set):
            msg = f"Error in reference type '{str(type(ref_type))}', it doesn't seem to have a valid set of sub-types."
            raise RuntimeError(msg)
        if isinstance(value, str):
            if len(accepted_sub_types) == 1:
                new_value = ref_type(value, list(accepted_sub_types)[0])
            else:
                raise TypeError("Ambigious value for DEST. Unable to create reference directly from string")
        elif isinstance(value, BaseRef):
            if type(value) is ref_type or value.dest in accepted_sub_types:  # pylint: disable=C0123
                new_value = ref_type(value.value, value.dest)
            else:
                raise TypeError(f"'{attr_name}': Reference type {str(type(value))}"
                                f"isn't combatible with {str(ref_type)}")
        else:
            raise TypeError(f"'{attr_name}': Invalid type. "
                            f"Expected one of (str, {str(ref_type)}), got '{str(type(value))}'")
        setattr(self, attr_name, new_value)

    def _set_attr_with_type_cast(self, attr_name: str, value: Any, type_class: type) -> None:
        """
        Sets object attribute only if it can be converted to given type.
        """
        if type_class in {bool, int, str, float}:
            new_value = type_class(value)
        else:
            raise NotImplementedError(type_class)
        setattr(self, attr_name, new_value)

    def _set_attr_positive_int(self, attr_name: str, value: int) -> None:
        """
        Checks that value is non-negative before updating attribute
        """
        if not isinstance(value, int):
            raise TypeError(f"Invalid type for '{attr_name}'. Expected int, got '{str(type(value))}'")
        if value < 0:
            raise ValueError(f"Positive integer expected: {value}")
        setattr(self, attr_name, value)

    def _find_by_name(self, elements: list, name: str):
        """
        Iterates through list of elements and return the first whose
        name matches the name argument
        """
        for elem in elements:
            if elem.name == name:
                return elem
        return None


class BaseRef(ARObject, abc.ABC):
    """
    Base type for all reference classes
    """

    def __init__(self,
                 value: str,
                 dest: ar_enum.IdentifiableSubTypes = None) -> None:
        self.value = value
        self.dest: ar_enum.IdentifiableSubTypes = None
        if dest is None:
            if len(self.accepted_sub_types()) == 1:
                dest = list(self.accepted_sub_types())[0]
            else:
                msg_part1 = "Value of dest cannot be None. Accepted values are: "
                msg_part2 = ",".join([str(x) for x in sorted(list(self.accepted_sub_types()))])
                raise ValueError(msg_part1 + msg_part2)
        if dest in self.accepted_sub_types():
            self.dest = dest
        else:
            raise ValueError(f"{str(dest)} is not a valid sub-type for {str(type(self))}")

    @classmethod
    @abc.abstractmethod
    def accepted_sub_types(cls) -> list[ar_enum.IdentifiableSubTypes]:
        """
        Subset of ar_enum.IdentifiableSubTypes defining
        which enum values are acceptable for dest
        """

    def __str__(self) -> str:
        """Returns reference as string"""
        return self.value
