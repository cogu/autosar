"""
Classes related to AUTOSAR Elements

"""

import re
from collections.abc import Iterable, Iterator
from typing import Any, Union
from enum import Enum
import abc
from autosar.base import split_ref, Searchable
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except


alignment_type_re = re.compile(
    r"[1-9][0-9]*|0[xX][0-9a-fA-F]*|0[bB][0-1]+|0[0-7]*|UNSPECIFIED|UNKNOWN|BOOLEAN|PTR")

display_format_str_re = re.compile(
    r"%[ \-+#]?[0-9]*(\.[0-9]+)?[diouxXfeEgGcs]")

# Type aliases

ValueSpecificationElement = Union["TextValueSpecification",
                                  "NumericalValueSpecification",
                                  "NotAvailableValueSpecification",
                                  "ArrayValueSpecification",
                                  "RecordValueSpecification",
                                  "ApplicationValueSpecification",
                                  "ConstantReference"]

PortPrototypeElement = Union["ProvidePortPrototype",
                             "RequirePortPrototype",
                             "PRPortPrototype"]

SwConnectorElement = Union["AssemblySwConnector",
                           "DelegationSwConnector",
                           "PassThroughSwConnector"]

InitValueArgType = Union["int",
                         "float",
                         "str",
                         "list",
                         "tuple",
                         "ValueSpecificationElement",
                         "ConstantRef"]

# Decorators


def convenience_method(func):
    """
    Tags the function as a convenience method
    """
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# Helper classes


class NumericalValue:
    """
    Wrapper for numerical value
    """

    def __init__(self,
                 value: int | float | str,
                 value_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        self._value = self._validate_value(value)
        if isinstance(value, str):
            if value.startswith("0x"):
                value_format = ar_enum.ValueFormat.HEXADECIMAL
            elif value.startswith("0b"):
                value_format = ar_enum.ValueFormat.BINARY
        self.value_format = value_format

    @property
    def value(self):
        """Value property"""
        return self._value

    @value.setter
    def value(self, value):
        self._value = self._validate_value(value)

    def _validate_value(self, value: Any) -> int | float | str:
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            try:
                return int(value, 0)
            except ValueError:
                return float(value)
        else:
            raise TypeError(f"Unexpected type for value {str(type(value))}")


class PositiveIntegerValue:
    """
    Wrapper for positive value
    """

    def __init__(self,
                 value: int,
                 value_format: ar_enum.ValueFormat = ar_enum.ValueFormat.DEFAULT
                 ) -> None:
        self._value = self._validate_value(value)
        self.value_format = value_format

    @property
    def value(self):
        """Value property"""
        return self._value

    @value.setter
    def value(self, value):
        self._value = self._validate_value(value)

    def _validate_value(self, value: int | str) -> int:
        if isinstance(value, str):
            try:
                value = int(value, 0)
            except ValueError as err:
                raise TypeError("Unable to convert to integer") from err
        if isinstance(value, int):
            if value < 0:
                raise ValueError("Value must be a positive integer")
            return value
        else:
            raise TypeError(f"Unexpected type for value {str(type(value))}")

# Base classes


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
            self._set_attr_from_str_or_direct(attr_name, value, type_name)
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

    def _set_attr_from_str_or_direct(self, attr_name: str, value: Any, type_name: type):
        """
        Can create new objects from str if necessary
        """
        if isinstance(value, str):
            new_value = type_name(value)
        elif isinstance(value, type_name):
            new_value = value
        else:
            raise TypeError(f"Invalid type  for '{attr_name}'"
                            f". Expected one of (str, {type_name}), got '{str(type(value))}'")
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


class Referrable(ARObject):
    """
    Group AR:REFERRABLE
    Type: Abstract
    """

    def __init__(self, name: str) -> None:
        self.name: str = name  # .SHORT-NAME
        self.parent: 'CollectableElement' = None

    @property
    def short_name(self) -> str:
        """
        Alias for .name
        """
        return self.name


class MultiLanguageReferrable(Referrable):
    """
    Group AR:MULTILANGUAGE-REFERRABLE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 long_name: Union["MultilanguageLongName", None] = None) -> None:
        super().__init__(name)
        self.long_name: MultilanguageLongName | None = None
        if long_name is not None:
            if isinstance(long_name, MultilanguageLongName):
                self.long_name = long_name
            else:
                raise TypeError(
                    f'long_name: Expected type "MultilanguageLongName", got "{str(type(long_name))}"')


class Identifiable(MultiLanguageReferrable):
    """
    Complex type AR:IDENTIFIABLE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 desc: Union["MultiLanguageOverviewParagraph", tuple[ar_enum.Language, str], str, None] = None,
                 category: str | None = None,
                 uuid: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.desc: MultiLanguageOverviewParagraph | None = None
        self.category = None
        self.admin_data = None
        self.introduction = None
        self.annotations = None
        self.uuid = None
        if desc is not None:
            if isinstance(desc, MultiLanguageOverviewParagraph):
                self.desc = desc
            elif isinstance(desc, str):
                self.desc = MultiLanguageOverviewParagraph.make(ar_enum.Language.FOR_ALL, desc)
            elif isinstance(desc, tuple) and len(desc) == 2:
                self.desc = MultiLanguageOverviewParagraph.make(*desc)
            else:
                raise TypeError(f"Invalid type for argument 'desc': {str(type(desc))}")
        self._assign_optional('category', category, str)
        self._assign_optional('uuid', uuid, str)

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used for generating reference strings
        """
        ref_parts.append(self.name)
        self.parent.update_ref_parts(ref_parts)

    def _calc_ref_string(self) -> str | None:
        """
        Calculates reference string based on parent
        """
        if self.parent is None:
            return None
        ref_parts: list[str] = [self.name]
        self.parent.update_ref_parts(ref_parts)
        return '/'.join(reversed(ref_parts))


class CollectableElement(Identifiable):
    """
    AR:COLLECTABLE-ELEMENT

    Meta-class that identify either an
    AR:PACKAGE or AR-ELEMENT.
    Both types can be places inside another
    package.

    Type Abstract
    """


class ARElement(CollectableElement):
    """
    AR:AR-ELEMENT

    Base class for all package-elements

    Type: Abstract
    """

# Common structure elements


class AdminData(ARObject):
    """
    Complex type AR:ADMIN-DATA
    Type: Concrete
    Tag variants: 'ADMIN-DATA'
    """

    def __init__(self, data: dict | None = None) -> None:
        self.data = data


class DataFilter(ARObject):
    """
    Complex type AR:DATA-FILTER
    Tag variants: 'FILTER' | 'DATA-FILTER'
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
    Tag variants: 'AUTOSAR-ENGINEERING-OBJECT' | 'ARTIFACT-DESCRIPTOR'

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

# --- Reference elements


class BaseRef(ARObject, abc.ABC):
    """
    Base type for all reference classes
    Complex type AR:REF
    Type: Abstract
    """

    def __init__(self,
                 value: str,
                 dest: ar_enum.IdentifiableSubTypes) -> None:
        self.value = value
        self.dest: ar_enum.IdentifiableSubTypes = None
        if dest in self._accepted_subtypes():
            self.dest = dest
        else:
            raise ValueError(f"{str(dest)} is not a valid sub-type for {str(type(self))}")

    @abc.abstractmethod
    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """
        Subset of ar_enum.IdentifiableSubTypes defining
        which enum values are acceptable for dest
        """

    def __str__(self) -> str:
        """Returns reference as string"""
        return self.value


class CompuMethodRef(BaseRef):
    """
    CompuMethod reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.COMPU_METHOD) -> None:
        super().__init__(value, dest)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.COMPU_METHOD}


class FunctionPtrSignatureRef(BaseRef):
    """
    Function pointer signature reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.BSW_MODULE_ENTRY)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.BSW_MODULE_ENTRY}


class ImplementationDataTypeRef(BaseRef):
    """
    ImplementationDataType reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE}


class SwAddrMethodRef(BaseRef):
    """
    SwAddrMethod reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD}


class SwBaseTypeRef(BaseRef):
    """
    SwBaseType reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.SW_BASE_TYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SW_BASE_TYPE}


class DataConstraintRef(BaseRef):
    """
    DataConstraint reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.DATA_CONSTR)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.DATA_CONSTR}


class PhysicalDimensionRef(BaseRef):
    """
    PhysicalDimension reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.PHYSICAL_DIMENSION)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.PHYSICAL_DIMENSION}


class UnitRef(BaseRef):
    """
    DataConstraint reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.UNIT)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.UNIT}


class IndexDataTypeRef(BaseRef):
    """
    IndexDataType reference
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE}


class ApplicationDataTypeRef(BaseRef):
    """
    Application data type reference
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE}


class ApplicationCompositeElementDataPrototypeRef(BaseRef):
    """
    References to APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_ELEMENT,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_ELEMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT,
                }


class AutosarDataTypeRef(BaseRef):
    """
    References to AR:AUTOSAR-DATA-TYPE--SUBTYPES-ENUM
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_IMPLEMENTATION_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.AUTOSAR_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE}


class ConstantRef(BaseRef):
    """
    Reference to ConstantSpecification
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.CONSTANT_SPECIFICATION)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.CONSTANT_SPECIFICATION}


class VariableDataPrototypeRef(BaseRef):
    """
    Reference to VariableDataPrototype
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE}


class ParameterDataPrototypeRef(BaseRef):
    """
    Reference to ParameterDataPrototype
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE}


class ApplicationErrorRef(BaseRef):
    """
    Reference to ApplicationError
    tag variants: 'POSSIBLE-ERROR-REF'
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.APPLICATION_ERROR)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ERROR}


class ModeDeclarationRef(BaseRef):
    """
    Reference to ModeDeclaration
    tag variants: 'TARGET-MODE-DECLARATION-REF' | 'INITIAL-MODE-REF' |
                  'FIRST-MODE-REF' | 'SECOND-MODE-REF' | 'MODE-DECLARATION-REF' |
                  'DEFAULT-MODE-REF' | 'TARGET-MODE-REF' | 'ENTERED-MODE-REF' |
                  'EXITED-MODE-REF' | 'ENTRY-MODE-DECLARATION-REF' | 'EXIT-MODE-DECLARATION-REF'

    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.MODE_DECLARATION)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_DECLARATION}


class ModeDeclarationGroupRef(BaseRef):
    """
    Reference to ModeDeclarationGroup
    Tag variants: 'MODE-DECLARATION-GROUP-REF' | 'TYPE-TREF' | 'MODE-GROUP-REF'
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP}


class ModeDeclarationGroupPrototypeRef(BaseRef):
    """
    Reference to ModeDeclarationGroupPrototype
    Tag variants: 'MODE-GROUP-REF' | 'REQUIRED-MODE-GROUP-REF' | 'FIRST-MODE-GROUP-REF' |
                  'SECOND-MODE-GROUP-REF' | 'MODE-DECLARATION-GROUP-PROTOTYPE-REF'
                  (and more)
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP_PROTOTYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP_PROTOTYPE}


class AutosarDataPrototypeRef(BaseRef):
    """
    Reference to elements that derives from AutosarDataPrototype
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ARGUMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE}


class E2EProfileCompatibilityPropsRef(BaseRef):
    """
    Reference to E2EProfileCompatibilityProps
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.E2E_PROFILE_COMPATIBILITY_PROPS)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.E2E_PROFILE_COMPATIBILITY_PROPS}


class ClientServerOperationRef(BaseRef):
    """
    Reference to ClientServerOperation
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.CLIENT_SERVER_OPERATION)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.CLIENT_SERVER_OPERATION}


class PortPrototypeRef(BaseRef):
    """
    Reference to port prototype elements
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_PROVIDED_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.ABSTRACT_REQUIRED_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE,
                }

    @property
    def is_provide_port_ref(self) -> bool:
        """
        True if destination of port reference is a P-PORT
        """
        p_port_values = {ar_enum.IdentifiableSubTypes.ABSTRACT_PROVIDED_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE}
        return self.dest in p_port_values

    @property
    def is_require_port_ref(self) -> bool:
        """
        True if destination of port reference is an R-PORT
        """
        r_port_values = {ar_enum.IdentifiableSubTypes.ABSTRACT_REQUIRED_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE}
        return self.dest in r_port_values


class AbstractImplementationDataTypeElementRef(BaseRef):
    """
    Reference to abstract or specific data-type elements
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_IMPLEMENTATION_DATA_TYPE_ELEMENT,
                ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE_ELEMENT}


class DataPrototypeRef(BaseRef):
    """
    References to DATA-PROTOTYPE--SUBTYPES-ENUM
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_ELEMENT,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_ELEMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT,
                ar_enum.IdentifiableSubTypes.ARGUMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.AUTOSAR_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE,
                }


class PortInterfaceRef(BaseRef):
    """
    References to PORT-INTERFACE--SUBTYPES-ENUM

    Only a small piece of the enum is currently implemented
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE,
                ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE,
                ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE,
                ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE,
                ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE,
                }


class SwComponentTypeRef(BaseRef):
    """
    References to SW-COMPONENT-TYPE--SUBTYPES-ENUM

    Only a small piece of the enum is currently implemented
    """

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE,
                ar_enum.IdentifiableSubTypes.COMPOSITION_SW_COMPONENT_TYPE,
                }


class SwComponentPrototypeRef(BaseRef):
    """
    Reference to SW-COMPONENT-PROTOTYPE--SUBTYPES-ENUM
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.SW_COMPONENT_PROTOTYPE)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SW_COMPONENT_PROTOTYPE}


class SwcInternalBehaviorRef(BaseRef):
    """
    Reference to AR:SWC-INTERNAL-BEHAVIOR--SUBTYPES-ENUM
    """

    def __init__(self, value: str) -> None:
        super().__init__(value, ar_enum.IdentifiableSubTypes.SWC_INTERNAL_BEHAVIOR)

    def _accepted_subtypes(self) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SWC_INTERNAL_BEHAVIOR}


# --- Documentation Elements


class Break(ARObject):
    """
    Complex type AR:BR
    Type: Concrete
    Tag variants: BR

    Same function as the html element.

    """


class EmphasisText(ARObject):
    """
    Complex type AR:EMPHASIS-TEXT
    Type: Concrete
    Tag variants: E

    Emphasized text

    Limitations: No support for child-elements. Type for argument elements must be string.

    """

    def __init__(self,
                 elements: None | list | str = None,
                 color: str = None,
                 font: ar_enum.EmphasisFont = None,
                 type: ar_enum.EmphasisType = None) -> None:  # pylint: disable=redefined-builtin
        self.elements = []
        self.color = color  # Attribute @COLOR
        self.font = font  # Attribute @FONT
        self.type = type  # Attribute @TYPE
        if elements is not None:
            if isinstance(elements, str):
                self.elements.append(elements)
            else:
                raise NotImplementedError("List of elements not yet supported")


class IndexEntry(ARObject):
    """
    Complex type AR:INDEX-ENTRY
    Type: Concrete
    Tag variants: IE

    Index Entry

    Limitations: Doesn't support sub-elements as seen in XML schema.
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Text content


class TechnicalTerm(ARObject):
    """
    Complex type AR:TT
    Type: Concrete
    Tag variants: TT

    Technical Term

    """

    def __init__(self,
                 text: str,
                 tex_render: str = None,
                 type: str = None) -> None:  # pylint: disable=redefined-builtin
        self.tex_render = tex_render  # attribute @TEX-RENDER
        self.type = type  # attribute @TYPE
        self.text = text  # Text content


class Subscript(ARObject):
    """
    Complex type AR:SUPSCRIPT
    Type: Concrete
    Tag variants: SUB

    Subscript is based on the same Complex type

    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content


class Superscript(ARObject):
    """
    Complex type AR:SUPSCRIPT
    Type: Concrete
    Tag variants: SUP

    Superscript
    """

    def __init__(self, text: str) -> None:
        self.text = text  # Simple content

    def __str__(self) -> str:
        """
        Convert to basic string
        """
        return "^" + self.text


class LanguageSpecific(ARObject):
    """
    Complex type AR:LANGUAGE-SPECIFIC
    Type: Abstract
    """

    def __init__(self, language: ar_enum.Language) -> None:
        assert isinstance(language, ar_enum.Language)
        self.language = language  # Attribute @L


class MixedContentForLongName(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-LONG-NAME
    Type: Abstract
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | TT | E | SUP | SUB | IE

    def append(self, part: str | TechnicalTerm | EmphasisText | Subscript | Subscript):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, TechnicalTerm, EmphasisText, Subscript, Subscript, IndexEntry)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class MixedContentForOverviewParagraph(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-OVERVIEW-PARAGRAPH
    Type: Abstract
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | TT | E | SUP | SUB | IE
        # Unsupported elements:
        # FT : AR:SL-OVERVIEW-PARAGRAPH
        # TRACE-REF: Complex type
        # XREF: AR:-XREF-TARGET

    def append(self, part: str | TechnicalTerm | EmphasisText | Subscript | Subscript):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, TechnicalTerm, EmphasisText, Subscript, Subscript, IndexEntry)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class LanguageLongName(MixedContentForLongName):
    """
    Complex type AR:L-LONG-NAME
    Type: Concrete
    Tag: L-4

    Longname for a specific language.

    The parts parameter can be a single string or a list of mixed types.

    Accepted mixed types:
    * strings
    * TechnicalTerm
    * EmphasisText
    * Subscript
    * Subscript
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultilanguageLongName(ARObject):
    """
    Complex type AR:MULTILANGUAGE-LONG-NAME
    Type: Concrete
    Tag variants: 'LABEL' | 'LONG-NAME'
    """

    def __init__(self,
                 long_name: None | tuple[ar_enum.Language,
                                         str] | LanguageLongName = None) -> None:
        self.elements: list[LanguageLongName] = []
        if long_name is not None:
            if isinstance(long_name, LanguageLongName):
                self.append(long_name)
            elif isinstance(long_name, tuple):
                self.append(LanguageLongName(long_name[0], long_name[1]))
            else:
                raise TypeError('Invalid type for long_name. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageLongName,'
                                f' got "{str(type(long_name))}"')

    def append(self, long_name: LanguageLongName) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(long_name, LanguageLongName)
        self.elements.append(long_name)


class LanguageOverviewParagraph(MixedContentForOverviewParagraph):
    """
    Complex type AR:L-OVERVIEW-PARAGRAPH
    Type: Concrete
    Tag variants: 'L-2'

    Overview paragraph for specific language

    The parts parameter can be a single string or a list of mixed types.

    Accepted mixed types:
    * strings
    * TechnicalTerm
    * EmphasisText
    * Subscript
    * Subscript
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultiLanguageOverviewParagraph(ARObject):
    """
    Complex type AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
    Type: Concrete
    Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
    """

    def __init__(self,
                 paragraph: None | tuple[ar_enum.Language,
                                         str] | LanguageOverviewParagraph = None) -> None:
        self.elements: list[LanguageOverviewParagraph] = []
        if paragraph is not None:
            if isinstance(paragraph, LanguageOverviewParagraph):
                self.append(paragraph)
            elif isinstance(paragraph, tuple) and len(paragraph) == 2:
                self.append(LanguageOverviewParagraph(*paragraph))
            else:
                raise TypeError('Invalid type for paragraph. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageOverviewParagraph,'
                                f' got "{str(type(paragraph))}"')

    def append(self, paragraph: LanguageOverviewParagraph) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(paragraph, LanguageOverviewParagraph)
        self.elements.append(paragraph)

    @classmethod
    def make(cls, language: ar_enum.Language, paragraph: str):
        """
        Convenience method for creating instances from text string
        """
        return cls(LanguageOverviewParagraph(language, paragraph))


class DocumentViewSelectable(ARObject):
    """
    Group AR:DOCUMENT-VIEW-SELECTABLE
    Type: Abstract
    """

    def __init__(self,
                 semantic_information: None | str = None,
                 view: None | str = None) -> None:
        self.semantic_information = semantic_information  # Attribute 'SI'
        self.view = view  # Attribute 'VIEW'
        if semantic_information is not None and (not isinstance(semantic_information, str)):
            raise TypeError(
                f"semantic_information: Expected type 'str', got '{str(type(semantic_information))}'")
        if view is not None and (not isinstance(view, str)):
            raise TypeError(
                f"view: Expected type 'str', got '{str(type(view))}'")


class Paginateable(DocumentViewSelectable):
    """
    Group AR:PAGINATEABLE
    Type: Abstract

    Experiment with named attributes for this class while keeping
    Unknown parent attributes hidden in kwargs
    """

    def __init__(self,
                 page_break: None | ar_enum.PageBreak = None,
                 keep_with_previous: None | ar_enum.KeepWithPrevious = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.page_break = page_break  # Attribute 'BREAK'
        self.keep_with_previous = keep_with_previous  # Attribute 'KEEP-WITH-PREVIOUS'
        if (page_break is not None) and (not isinstance(page_break, ar_enum.PageBreak)):
            raise TypeError(
                f"page_break: Expected type 'PageBreak', got '{str(type(page_break))}'")
        if (keep_with_previous is not None) and (not isinstance(keep_with_previous, ar_enum.KeepWithPrevious)):
            raise TypeError(
                f"page_break: Expected type 'PageBreak', got '{str(type(keep_with_previous))}'")


class MixedContentForParagraph(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-PARAGRAPH
    Type: Abstract
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | BR | E | IE | SUB | SUP | TT
        # Unsupported elements:
        # FT : AR:SL-OVERVIEW-PARAGRAPH
        # STD: AR:STD
        # TRACE-REF : Specialization of AR:REF
        # XDOC: AR:XDOC
        # XFILE: AR:XFILE
        # XREF: AR:XREF
        # XREF-TARGET: AR:-XREF-TARGET

    def append(self,
               part: str | Break | EmphasisText | IndexEntry | Subscript | Subscript | TechnicalTerm):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, Break, EmphasisText, IndexEntry, Subscript, Subscript, TechnicalTerm)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class LanguageParagraph(MixedContentForParagraph):
    """
    Complex type AR:L-PARAGRAPH
    Type: Concrete
    Tag variants: 'L-1'

    Paragraph for specific language

    The parts parameter can be a single string or a list of mixed types.

    Accepted mixed types:
    * strings
    * Break
    * EmphasisText
    * TechnicalTerm
    * Subscript
    * Subscript
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultiLanguageParagraph(Paginateable):
    """
    Complex type AR:MULTI-LANGUAGE-PARAGRAPH
    Type: Concrete
    Tag variants: 'P'
    """

    def __init__(self,
                 paragraph: None | tuple[ar_enum.Language,
                                         str] | LanguageParagraph = None,
                 help_entry: None | str = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.help_entry = help_entry  # Attribute 'HELP-ENTRY'
        self.elements: list[LanguageParagraph] = []
        if paragraph is not None:
            if isinstance(paragraph, LanguageParagraph):
                self.append(paragraph)
            elif isinstance(paragraph, tuple):
                self.append(LanguageParagraph(paragraph[0], paragraph[1]))
            else:
                raise TypeError('Invalid type for paragraph. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageParagraph,'
                                f' got "{str(type(paragraph))}"')

    def append(self, paragraph: LanguageParagraph) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(paragraph, LanguageParagraph)
        self.elements.append(paragraph)


class MixedContentForVerbatim(LanguageSpecific):
    """
    Group AR:MIXED-CONTENT-FOR-VERBATIM
    Type: Abstract

    This includes AR:WHITESPACE-CONTROLLED as it
    does not have any attributes or elements of its
    own.
    """

    def __init__(self, language: ar_enum.Language) -> None:
        super().__init__(language)
        self.parts = []  # Unbounded list of str | BR | E | TT
        # Unsupported elements:
        # XREF: AR:XREF

    def append(self,
               part: str | Break | EmphasisText | TechnicalTerm):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, Break, EmphasisText, TechnicalTerm)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class LanguageVerbatim(MixedContentForVerbatim):
    """
    Complex type AR:L-VERBATIM
    Type: Concrete
    Tag variants: 'L-5'
    """

    def __init__(self, language: ar_enum.Language, parts: None | str | list[Any] = None) -> None:
        super().__init__(language)
        if parts is not None:
            if isinstance(parts, str):
                self.append(parts)
            else:
                for part in parts:
                    self.append(part)


class MultiLanguageVerbatim(Paginateable):
    """
    Complex type AR:MULTI-LANGUAGE-VERBATIM
    Type: Concrete
    Tag variants: 'VERBATIM'
    """

    def __init__(self,
                 element: None | tuple[ar_enum.Language,
                                       str] | LanguageVerbatim = None,
                 allow_break: None | str = None,
                 float: None | ar_enum.Float = None,  # pylint: disable=redefined-builtin
                 page_wide: None | ar_enum.PageWide = None,
                 help_entry: None | str = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.allow_break = allow_break  # Attribute 'ALLOW-BREAK'
        self.float = float  # Attribte 'FLOAT'
        self.page_wide = page_wide  # Attribute 'PGWIDE'
        self.help_entry = help_entry  # Attribute 'HELP-ENTRY'
        self.elements: list[LanguageVerbatim] = []
        if element is not None:
            if isinstance(element, LanguageVerbatim):
                self.append(element)
            elif isinstance(element, tuple):
                self.append(LanguageVerbatim(element[0], element[1]))
            else:
                raise TypeError('Invalid type for element. '
                                f'Expected tuple[ar_enum.Language,str] or LanguageVerbatim,'
                                f' got "{str(type(element))}"')

    def append(self, paragraph: LanguageVerbatim) -> None:
        """
        Adds long_name to its inner list with type-check
        """
        assert isinstance(paragraph, LanguageVerbatim)
        self.elements.append(paragraph)


class MixedContentForUnitNames(ARObject):
    """
    Group MIXED-CONTENT-FOR-UNIT-NAMES
    Type: Abstract
    """

    def __init__(self) -> None:
        self.parts = []  # Unbounded list of str | SUB | SUP

    def append(self,
               part: str | Break | EmphasisText | TechnicalTerm):
        """
        Checks type validity before adding element to elements
        """
        if isinstance(part, (str, Subscript, Superscript)):
            self.parts.append(part)
        else:
            raise TypeError('Unsupported element type: ' + str(type(part)))


class SingleLanguageUnitNames(MixedContentForUnitNames):
    """
    Complex type AR:SINGLE-LANGUAGE-UNIT-NAMES
    Type: Concrete
    Tag variants: 'PRM-UNIT' | 'UNIT-DISPLAY-NAME' | 'UNIT-DISPLAY-NAME' | 'DISPLAY-NAME'
    """

    def __init__(self, parts: str | list | None = None) -> None:
        super().__init__()
        if parts is not None:
            if isinstance(parts, Iterable):
                for part in parts:
                    self.append(part)
            else:
                self.append(parts)

    def __str__(self) -> str:
        """
        Convert to string if the unit name has simple
        type (at most one part of type str).
        """
        result = []
        for part in self.parts:
            if isinstance(part, str):
                result.append(part)
            elif isinstance(part, Superscript):
                result.append(str(part))
            else:
                raise ValueError("Unable to convert to string from multiple parts")
        return "".join(result)


class DocumentationBlock(ARObject):
    """
    Complex type AR:DOCUMENTATION-BLOCK
    Type: Concrete
    Tag Variants: 'INTRODUCTION', 'DEF', 'VALUE', 'ANNOTATION-TEXT', 'REMARK'
                  'COND', 'DESCRICPTION', 'RATIONALE', 'DEPENDENCIES', 'USE-CASE',
                  'CONFLICTS', 'SUPPORTING-MATERIAL', 'SW-GENERIC-AXIS-DESC'
    """

    def __init__(self,
                 element: MultiLanguageParagraph | MultiLanguageVerbatim | list[Any] | None = None) -> None:
        self.elements: list[MultiLanguageParagraph | MultiLanguageVerbatim] = []
        if element is not None:
            if isinstance(element, Iterable):
                for elem in element:
                    self.append(elem)
            else:
                self.append(element)

    def append(self, element: MultiLanguageParagraph | MultiLanguageVerbatim) -> None:
        """
        Appends new element with type check
        """
        assert isinstance(element,
                          (MultiLanguageParagraph,
                           MultiLanguageVerbatim))
        self.elements.append(element)


class GeneralAnnotation(ARObject):
    """
    Group AR:GENERAL-ANNOTATION
    Type: Abstract
    """

    def __init__(self,
                 label: MultilanguageLongName | None = None,
                 origin: str | None = None,
                 text: DocumentationBlock | None = None) -> None:
        super().__init__()
        self.label = label  # .LABEL
        self.origin = origin  # .ANNOTATION-ORIGIN
        self.text = text  # .ANNOTATION-TEXT


class Annotation(GeneralAnnotation):
    """
    Complex type AR:ANNOTATION
    Type: Concrete
    """

    def __init__(self,  # pylint: disable=useless-parent-delegation
                 label: MultilanguageLongName | None = None,
                 origin: str | None = None,
                 text: DocumentationBlock | None = None) -> None:
        super().__init__(label, origin, text)


class Describable(ARObject):
    """
    Group AR:DESCRIBABLE
    """

    def __init__(self,
                 desc: Union["MultiLanguageOverviewParagraph", tuple[ar_enum.Language, str], str, None] = None,
                 category: str | None = None,
                 introduction: DocumentationBlock | None = None,
                 admin_data: AdminData | None = None
                 ) -> None:
        super().__init__()
        self.desc: MultiLanguageOverviewParagraph | None = None  # .DESC
        self.category: str | None = None  # .CATEGORY
        self.introduction: DocumentationBlock | None = None  # .INTRODUCTION
        self.admin_data: AdminData | None = None  # .ADMIN-DATA
        if desc is not None:
            if isinstance(desc, MultiLanguageOverviewParagraph):
                self.desc = desc
            elif isinstance(desc, str):
                self.desc = MultiLanguageOverviewParagraph.make(ar_enum.Language.FOR_ALL, desc)
            elif isinstance(desc, tuple) and len(desc) == 2:
                self.desc = MultiLanguageOverviewParagraph.make(*desc)
            else:
                raise TypeError(f"Invalid type for argument 'desc': {str(type(desc))}")
        self._assign_optional('category', category, str)
        self._assign_optional_strict('introduction', introduction, DocumentationBlock)
        self._assign_optional_strict('admin_data', admin_data, AdminData)


# --- Computation method elements


class CompuRational(ARObject):
    """
    AR:COMPU-RATIONAL-COEFFS
    Type: Concrete
    Tag variants: 'COMPU-RATIONAL-COEFFS'
    """

    def __init__(self,
                 numerator: tuple[int | float] | list[int | float] | None,
                 denominator: tuple[int | float] | list[int | float] | None = None) -> None:
        if numerator is not None:
            if not isinstance(numerator, (tuple, list)):
                raise TypeError("Parameter for 'numerator' must be either a list or a tuple")
            self.numerator = tuple(numerator)
        else:
            self.numerator = None
        if denominator is not None:
            if not isinstance(denominator, (tuple, list)):
                raise TypeError("Parameter for 'denominator' must be either a list or a tuple")
            self.denominator = tuple(denominator)
        else:
            self.denominator = None


class CompuConst(ARObject):
    """
    AR:COMPU-CONST
    Type: Concrete

    Handles AR:COMPU-CONST-NUMERIC-CONTENT
    and AR:COMPU-CONST-TEXT-CONTENT dynamically
    """

    def __init__(self, value: int | float | str):
        self.value = value


class CompuScale(ARObject):
    """
    AR:COMPU-SCALE
    Type: Concrete
    Tag variants: 'COMPU-SCALE'
    """

    def __init__(self,
                 content: CompuConst | CompuRational | None = None,
                 lower_limit: int | float | str | None = None,
                 upper_limit: int | float | str | None = None,
                 label: str | None = None,
                 symbol: str | None = None,
                 desc: MultiLanguageOverviewParagraph | None = None,
                 mask: int | None = None,
                 inverse_value: CompuConst | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        self.content = content                      # CHOICE(COMPU-SCALE-CONSTANT-CONTENTS, COMPU-SCALE-RATIONAL-FORMULA) # noqa E501 pylint: disable=C0301
        self.lower_limit = lower_limit              # .LOWER-LIMIT
        self.upper_limit = upper_limit              # .UPPER-LIMIT
        self.label = label                          # .SHORT-LABEL
        self.symbol = symbol                        # .SYMBOL
        self.desc = desc                            # .DESC
        self.mask = mask                            # .MASK
        self.inverse_value: CompuConst | None = None  # .COMPU-INVERSE-VALUE
        if inverse_value is not None:
            if isinstance(inverse_value, CompuConst):
                self.inverse_value = inverse_value
            elif isinstance(inverse_value, (int, float, str)):
                self.inverse_value = CompuConst(inverse_value)
            else:
                raise TypeError(f"Invalid type for 'inverse_value': {str(type(inverse_value))}")
        self.lower_limit_type = lower_limit_type    # .LOWER-LIMIT@INTERVAL-TYPE
        self.upper_limit_type = upper_limit_type    # .UPPER-LIMIT@INTERVAL-TYPE
        # .VARIATION-POINT not supported

    @property
    def content_type(self) -> ar_enum.CompuScaleContent:
        """
        What kind of content does this CompuScale have?
        """
        if isinstance(self.content, CompuConst):
            return ar_enum.CompuScaleContent.CONSTANT
        elif isinstance(self.content, CompuRational):
            return ar_enum.CompuScaleContent.RATIONAL
        else:
            return ar_enum.CompuScaleContent.NONE


class Computation(ARObject):
    """
    AR:COMPU
    Type: Concrete
    Tag variants: 'COMPU-INTERNAL-TO-PHYS' | 'COMPU-PHYS-TO-INTERNAL'
    """

    def __init__(self,
                 compu_scales: list[CompuScale] | None = None,
                 default_value: CompuConst | int | float | str | None = None) -> None:

        self.compu_scales = compu_scales
        self.default_value: CompuConst | int | float | str | None = None  # .COMPU-DEFAULT-VALUE
        if isinstance(default_value, CompuConst):
            self.default_value = default_value
        elif isinstance(default_value, (int, float, str)):
            self.default_value = CompuConst(default_value)

    @classmethod
    def make_value_table(cls: "Computation",
                         elements: list[Any],
                         default_value: CompuConst | int | float | str | None = None,
                         auto_label: bool = True):
        """
        Creates new const-based computation from values in list

        When elements is a list of strings:
            Creates one CompuScale per list item and automatically calculates lower and upper limits

        When elements is a list of tuples:
            If 2-tuple: First element is both lower_limit and upper_limit, second element is text value.
            If 3-tuple: First element is lower_limit, second element is upper_limit, third element is text value.

        auto_label: automatically creates a <SHORT-LABEL> based on the text value.

        """
        compu_scales = []
        for i, elem in enumerate(elements):
            label = None
            if isinstance(elem, str):
                lower_limit, upper_limit, value = i, i, elem
            elif isinstance(elem, tuple):
                if len(elem) == 2:
                    lower_limit, upper_limit, value = (elem[0], elem[0], elem[1])
                elif len(elem) == 3:
                    lower_limit, upper_limit, value = elem
                else:
                    raise ValueError(f"Invalid length of tuple: {len(elem)}")
            else:
                raise TypeError(f"Invalid type of element: {str(type(elem))}")
            if auto_label and isinstance(value, str):
                label = value
            compu_scales.append(CompuScale(CompuConst(value), lower_limit, upper_limit, label))
        return cls(compu_scales, default_value)

    @classmethod
    def make_rational(cls: "Computation",
                      scaling_factor: int | float = 1,
                      offset: int | float = 0,
                      lower_limit: int | float | str | None = None,
                      upper_limit: int | float | str | None = None,
                      default_value: CompuConst | int | float | str | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:
        """
        Creates a new Computation instance with one COMPU-SCALE containing numerator
        and denominator.

        """
        numerator = [offset, float(scaling_factor)]
        denominator = [1]
        compu_scales = [CompuScale(CompuRational(numerator, denominator),
                                   lower_limit,
                                   upper_limit,
                                   lower_limit_type=lower_limit_type,
                                   upper_limit_type=upper_limit_type)]
        return cls(compu_scales, default_value)


class CompuMethod(ARElement):
    """
    AR:COMPU-METHOD
    Type: Concrete
    Tag Variants: 'COMPU-METHOD'
    """

    def __init__(self, name: str,
                 int_to_phys: Computation | None = None,
                 phys_to_int: Computation | None = None,
                 unit_ref: UnitRef | None = None,
                 display_format: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.int_to_phys = int_to_phys        # .COMPU-INTERNAL-TO-PHYS
        self.phys_to_int = phys_to_int        # .COMPU-PHYS-TO-INTERNAL
        self.unit_ref = unit_ref              # .UNIT-REF
        self.display_format = display_format  # .DISPLAY-FORMAT

    def ref(self) -> CompuMethodRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else CompuMethodRef(ref_str)


# Constraint elements


class LimitObject(ARObject):
    """
    Base class for elements that has
    upper and lower limits
    Type: Abstract
    """

    def __init__(self,
                 lower_limit: int | float | None = None,
                 upper_limit: int | float | None = None,
                 lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                 upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED) -> None:

        self.lower_limit = lower_limit              # .LOWER-LIMIT
        self.upper_limit = upper_limit              # .UPPER-LIMIT
        self.lower_limit_type = lower_limit_type    # .LOWER-LIMIT@INTERVAL-TYPE
        self.upper_limit_type = upper_limit_type    # .UPPER-LIMIT@INTERVAL-TYPE

    @property
    def is_empty(self) -> bool:
        """Overrides is_empty from base class"""
        return self.is_empty_with_ignore({"lower_limit_type", "upper_limit_type"})

    def check_value(self, value: int | float) -> bool:
        """
        Checks if given value is inside the constraint limits
        """
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
    """
    AR:SCALE-CONSTR
    Type: Concrete
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
    """
    Base class data constraint rules
    Type: Abstract
    """

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
    """
    AR:INTERNAL-CONSTRS
    Type: Concrete
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
    """
    AR:PHYS-CONSTRS
    Type: Concrete
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
    """
    AR:DATA-CONSTR-RULE
    Type: Concrete
    Tag variants: 'DATA-CONSTR-RULE'
    """

    def __init__(self,
                 internal: InternalConstraint | None = None,
                 physical: PhysicalConstraint | None = None,
                 level: int | None = None) -> None:
        self.internal = internal   # .INTERNAL-CONSTRS
        self.physical = physical   # .PHYS-CONSTRS
        self.level = level         # .CONSTR-LEVEL


class DataConstraint(ARElement):
    """
    AR:DATA-CONSTR
    Type: Concrete
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
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else DataConstraintRef(ref_str)

    @classmethod
    def make_physical(cls: "DataConstraint",
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
                      **kwargs) -> "DataConstraint":
        """
        Convenience method for creating a DataConstraint
        that contains a single physical constraint.
        """
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

    @classmethod
    def make_internal(cls: "DataConstraint",
                      name: str,
                      lower_limit: int | float | None = None,
                      upper_limit: int | float | None = None,
                      scale_constr: list[ScaleConstraint] | None = None,
                      max_gradient: int | float | None = None,
                      max_diff: int | float | None = None,
                      monotony: ar_enum.Monotony | None = None,
                      lower_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      upper_limit_type: ar_enum.IntervalType = ar_enum.IntervalType.CLOSED,
                      **kwargs) -> "DataConstraint":
        """
        Convenience method for creating a DataConstraint
        that contains a single internal constraint.
        """
        rule = DataConstraintRule(internal=InternalConstraint(lower_limit,
                                                              upper_limit,
                                                              scale_constr,
                                                              max_gradient,
                                                              max_diff,
                                                              monotony,
                                                              lower_limit_type,
                                                              upper_limit_type))
        return cls(name, [rule], **kwargs)

# Unit elements


class Unit(ARElement):
    """
    Complex type AR:UNIT
    Type: Concrete
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
                self.physical_dimension_ref = PhysicalDimensionRef(display_name)
            elif isinstance(physical_dimension_ref, PhysicalDimensionRef):
                self.physical_dimension_ref = physical_dimension_ref
            else:
                raise TypeError(f"physical_dimension_ref: Invalid type '{str(type(physical_dimension_ref))}'")
        self._assign_optional('factor', factor, float)
        self._assign_optional('offset', offset, float)

    def ref(self) -> UnitRef:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else UnitRef(ref_str)


# DataDictionary and DataType elements


class BaseType(ARElement):
    """
    Merge of Complex types AR:BASE-TYPE, AR:BASE-TYPE-DEFINITION,
    AR:BASE-TYPE-DIRECT-DEFINITION
    Type: Abstract
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.size: int | None = None  # .BASE-TYPE-SIZE
        self.max_size: int | None = None  # .MAX-BASE-TYPE-SIZE
        self.encoding: str | None = None  # .BASE-TYPE-ENCODING
        self.alignment: int | None = None  # .MEM-ALIGNMENT
        self.byte_order: ar_enum.ByteOrder | None = None  # .BYTE-ORDER
        self.native_declaration: str | None = None  # .NATIVE-DECLARATION


class SwBaseType(BaseType):
    """
    Complex type AR:SW-BASE-TYPE
    Type: Concrete
    Tag variants: SW-BASE-TYPE
    """

    def __init__(self,
                 name: str,
                 size: int | None = None,
                 max_size: int | None = None,
                 encoding: str | None = None,
                 alignment: int | None = None,
                 byte_order: ar_enum.ByteOrder | None = None,
                 native_declaration: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.size = size
        self.max_size = max_size
        self.encoding = encoding
        self.alignment = alignment
        self.byte_order = byte_order
        self.native_declaration = native_declaration

    def ref(self) -> SwBaseTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwBaseTypeRef(ref_str)


class SwBitRepresentation(ARObject):
    """
    SW-BIT-REPRESENTATION
    Type: Concrete
    """

    def __init__(self,
                 position: int | None = None,
                 num_bits: int | None = None) -> None:
        super().__init__()
        self.position: int | None = None
        self.num_bits: int | None = None
        self._assign_optional('position', position, int)
        self._assign_optional('num_bits', num_bits, int)


class SwTextProps(ARObject):
    """
    Complex type AR:SW-TEXT-PROPS
    Type: Concrete
    Tag Variants: 'SW-TEXT-PROPS'
    """

    def __init__(self,
                 array_size_semantics: ar_enum.ArraySizeSemantics | None = None,
                 max_text_size: int | None = None,
                 base_type_ref: SwBaseTypeRef | str | None = None,
                 fill_char: int | None = None,
                 ):
        self.array_size_semantics: ar_enum.ArraySizeSemantics | None = None   # .ARRAY-SIZE-SEMANTICS
        self.max_text_size: int | None = None                                 # .SW-MAX-TEXT-SIZE
        self.base_type_ref: SwBaseTypeRef | str | None = None                 # .BASE-TYPE-REF
        self.fill_char: int | None = None                                     # .FILL-CHAR
        self._assign_optional('array_size_semantics', array_size_semantics, ar_enum.ArraySizeSemantics)
        self._assign_optional('max_text_size', max_text_size, int)
        self._assign_optional('base_type_ref', base_type_ref, SwBaseTypeRef)
        self._assign_optional('fill_char', fill_char, int)


class SwPointerTargetProps(ARObject):
    """
    Complex type AR:SW-POINTER-TARGET-PROPS
    Type: Concrete
    Tag Variants: 'SW-POINTER-TARGET-PROPS'
    """

    def __init__(self,
                 target_category: str | None = None,
                 sw_data_def_props: Union["SwDataDefProps", "SwDataDefPropsConditional", None] = None,
                 function_ptr_signature_ref: FunctionPtrSignatureRef | None = None
                 ) -> None:
        self.target_category: str | None = None  # .TARGET-CATEGORY
        self.sw_data_def_props: Union["SwDataDefProps", None] = None  # .SW-DATA-DEF-PROPS
        self.function_ptr_signature_ref: FunctionPtrSignatureRef | None = None  # .FUNCTION-POINTER-SIGNATURE-REF
        self._assign_optional("target_category", target_category, str)
        self._assign_optional("function_ptr_signature_ref", function_ptr_signature_ref, FunctionPtrSignatureRef)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class SwDataDefPropsConditional(ARObject):
    """
    Merge of Complex types AR:SW-DATA-DEF-PROPS-CONDITIONAL and
    AR:SW-DATA-DEF-PROPS-CONTENT
    Type: Concrete
    Tag Variants: SW-DATA-DEF-PROPS-CONDITIONAL
    """

    def __init__(self,
                 display_presentation: ar_enum.DisplayPresentation | None = None,
                 step_size: float | None = None,
                 annotations: Annotation | list[Annotation] | None = None,
                 sw_addr_method_ref: str | SwAddrMethodRef | None = None,
                 base_type_ref: SwBaseTypeRef | None = None,
                 compu_method_ref: str | CompuMethodRef | None = None,
                 data_constraint_ref: str | DataConstraintRef | None = None,
                 impl_data_type_ref: str | ImplementationDataTypeRef | None = None,
                 unit_ref: str | UnitRef | None = None,
                 alignment: int | float | None = None,
                 bit_representation: SwBitRepresentation | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 text_props: SwTextProps | None = None,
                 display_format: str | None = None,
                 impl_policy: ar_enum.SwImplPolicy | None = None,
                 additional_native_type_qualifier: str | None = None,
                 intended_resolution: int | float | None = None,
                 interpolation_method: str | None = None,
                 is_virtual: bool | None = None,
                 ptr_target_props: SwPointerTargetProps | None = None
                 ) -> None:
        # .DISPLAY-PRESENTATION
        self.display_presentation: ar_enum.DisplayPresentation | None = None
        self.step_size: float | None = None  # .STEP-SIZE : AR:FLOAT
        # .SW-VALUE-BLOCK-SIZE-MULTS not supported.
        self.annotations: list[Annotation] = []  # .ANNOTATIONS
        self.sw_addr_method_ref: SwAddrMethodRef | None = None  # .SW-ADDR-METHOD-REF
        self.alignment: int | str | None = None  # .SW-ALIGNMENT
        self.base_type_ref: SwBaseTypeRef | None = None  # .BASE-TYPE-REF
        self.bit_representation: SwBitRepresentation | None = None  # .SW-BIT-REPRESENTATION
        self.calibration_access: ar_enum.SwCalibrationAccess | None = None  # .SW-CALIBRATION-ACCESS
        # .SW-VALUE-BLOCK-SIZE not supported.
        # .SW-CALPRM-AXIS-SET not yet supported. Low on priority list.
        self.text_props: SwTextProps | None = None  # .SW-TEXT-PROPS
        # .SW-COMPARISON-VARIABLES not yet supported. Low on priority list.
        self.compu_method_ref: CompuMethodRef | None = None
        self.data_constraint_ref: DataConstraintRef | None = None
        # .SW-DATA-DEPENDENCY not yet supported. Low on priority list.
        self.display_format: str | None = None  # .DISPLAY-FORMAT
        self.impl_data_type_ref: ImplementationDataTypeRef | None = None  # .IMPLEMENTATION-DATA-TYPE-REF
        # .SW-HOST-VARIABLE not yet supported. Low on priority list.
        self.impl_policy: ar_enum.SwImplPolicy | None = None  # .SW-IMPL-POLICY
        self.additional_native_type_qualifier: str | None = None  # .ADDITIONAL-NATIVE-TYPE-QUALIFIER
        self.intended_resolution: int | float | None = None  # .SW-INTENDED-RESOLUTION
        self.interpolation_method: str | None = None  # .SW-INTERPOLATION-METHOD
        # .INVALID-VALUE not yet supported.
        # .MC-FUNCTION not yet supported. Low on priority list.
        self.is_virtual: bool | None = None  # .IS-VIRTUAL
        self.ptr_target_props: SwPointerTargetProps | None = None  # .SW-POINTER-TARGET-PROPS
        # .SW-RECORD-LAYOUT-REF not yet supported. Low on priority list.
        # .SW-REFRESH-TIMING not yet supported. Low on priority list.
        self.unit_ref = None  # .UNIT-REF
        # .VALUE-AXIS-DATA-TYPE-REF not yet supported. Low on priority list.

        self._assign_optional('display_presentation', display_presentation, ar_enum.DisplayPresentation)
        self._assign_optional('step_size', step_size, float)
        if annotations is not None:
            if isinstance(annotations, Annotation):
                self.annotations.append(annotations)
            elif isinstance(annotations, Iterable):
                for annotation in annotations:
                    if not isinstance(annotation, Annotation):
                        raise TypeError(
                            f"Param annotations: Expected type 'Annotation', got '{str(type(annotation))}'")
                    self.annotations.append(annotation)
            else:
                raise TypeError(
                    "Param annotations: "
                    f"Expected type 'Annotation' or list[Annotation], got '{str(type(annotations))}'")
        self._assign_optional('sw_addr_method_ref', sw_addr_method_ref, SwAddrMethodRef)
        self._assign_int_or_str_pattern_optional('alignment', alignment, alignment_type_re)
        self._assign_optional('base_type_ref', base_type_ref, SwBaseTypeRef)
        if bit_representation is not None:
            if not isinstance(bit_representation, SwBitRepresentation):
                raise TypeError(f"bit_representation: Invalid type '{str(type(bit_representation))}'."
                                " Expected 'SwBitRepresentation'")
            self.bit_representation = bit_representation
        self._assign_optional('calibration_access', calibration_access, ar_enum.SwCalibrationAccess)
        if text_props is not None:
            if not isinstance(text_props, SwTextProps):
                raise TypeError(f"text_props: Invalid type '{str(type(text_props))}'."
                                " Expected 'SwTextProps'")
            self.text_props = text_props
        self._assign_optional('compu_method_ref', compu_method_ref, CompuMethodRef)
        self._assign_optional('data_constraint_ref', data_constraint_ref, DataConstraintRef)
        self._assign_optional('impl_data_type_ref', impl_data_type_ref, ImplementationDataTypeRef)
        self._assign_optional('unit_ref', unit_ref, UnitRef)
        self._assign_int_or_str_pattern_optional('display_format', display_format, display_format_str_re)
        self._assign_optional('impl_policy', impl_policy, ar_enum.SwImplPolicy)
        self._assign_optional('additional_native_type_qualifier',
                              additional_native_type_qualifier, str)
        if intended_resolution is not None:
            if isinstance(intended_resolution, (int, float)):
                self.intended_resolution = intended_resolution
            else:
                raise TypeError(f"Invalid type '{str(type(intended_resolution))}' for paramater 'intended_resolution'")
        self._assign_optional('interpolation_method', interpolation_method, str)
        self._assign_optional('is_virtual', is_virtual, bool)
        if ptr_target_props is not None:
            self._set_attr_with_strict_type('ptr_target_props', ptr_target_props, SwPointerTargetProps)

    @property
    def is_queued(self) -> bool:
        """
        Returns True if impl_policy is set to QUEUED
        """
        if self.impl_policy is not None and self.impl_policy == ar_enum.SwImplPolicy.QUEUED:
            return True
        return False


class SwDataDefProps(ARObject):
    """
    Complex type AR:SW-DATA-DEF-PROPS
    Tag variants: 'SW-DATA-DEF-PROPS' | 'NETWORK-REPRESENTATION' |
                  'NETWORK-REPRESENTATION-PROPS' | 'PHYSICAL-PROPS'
    """

    def __init__(self, variants: SwDataDefPropsConditional | list[SwDataDefPropsConditional] | None = None) -> None:
        super().__init__()
        self.variants: list[SwDataDefPropsConditional] = []  # .SW-DATA-DEF-PROPS-VARIANTS
        if variants is not None:
            if isinstance(variants, list):
                for variant in variants:
                    self.append(variant)
            elif isinstance(variants, SwDataDefPropsConditional):
                self.append(variants)
            else:
                raise TypeError("variant must be one of (SwDataDefPropsConditional, list[SwDataDefPropsConditional])")

    def __getitem__(self, index: int) -> SwDataDefPropsConditional:
        """
        Accessor of variants list
        """
        return self.variants[index]

    def __len__(self) -> int:
        """
        Length of variants list
        """
        return len(self.variants)

    def __iter__(self):
        """
        Iterator of variants list
        """
        return iter(self.variants)

    def append(self, variant: SwDataDefPropsConditional):
        """
        Appends SW-DATA-DEF-PROPS-CONDITIONAL to variants list
        """
        if isinstance(variant, SwDataDefPropsConditional):
            self.variants.append(variant)
        else:
            raise TypeError("variant must be of type SwDataDefPropsConditional")


class AutosarDataType(ARElement):
    """
    Element AUTOSAR-DATA-TYPE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.sw_data_def_props: SwDataDefProps | None = None
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class ImplementationProps(Referrable):
    """
    Complex type AR:IMPLEMENTATION-PROPS
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 symbol: str | None = None) -> None:
        super().__init__(name)
        self.symbol: str | None = None
        self._assign_optional('symbol', symbol, str)


class SymbolProps(ImplementationProps):
    """
    Complex type AR:SYMBOL-PROPS
    Type: Concrete
    Tag Variants: 'SYMBOL-PROPS', 'EVENT-SYMBOL-PROPS'
    """


class ImplementationDataTypeElement(Identifiable):
    """
    Complex type AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
    Type: Concrete
    Tag variants: 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
    """

    def __init__(self,
                 name: str,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 array_size: int | None = None,
                 array_impl_policy: ar_enum.ArrayImplPolicy | None = None,
                 array_size_handling: ar_enum.ArraySizeHandling | None = None,
                 array_size_semantics: ar_enum.ArraySizeSemantics | None = None,
                 sub_elements: list["ImplementationDataTypeElement"] | None = None,
                 is_optional: bool | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.array_size: int | None = None                                      # .ARRAY-SIZE
        self.array_impl_policy: ar_enum.ArrayImplPolicy | None = None           # .ARRAY-IMPL-POLICY
        self.array_size_handling: ar_enum.ArraySizeHandling | None = None       # .ARRAY-SIZE-HANDLING
        self.array_size_semantics: ar_enum.ArraySizeSemantics | None = None     # .ARRAY-SIZE-SEMANTICS
        self.is_optional: bool | None = None                                    # .IS-OPTIONAL
        self.sub_elements: list["ImplementationDataTypeElement"] | None = []    # .SUB-ELEMENTS
        self.sw_data_def_props: SwDataDefProps | None = None                    # .SW-DATA-DEF-PROPS
        self._assign_optional_positive_int("array_size", array_size)
        self._assign_optional("array_impl_policy", array_impl_policy, ar_enum.ArrayImplPolicy)
        self._assign_optional("array_size_handling", array_size_handling, ar_enum.ArraySizeHandling)
        self._assign_optional("array_size_semantics", array_size_semantics, ar_enum.ArraySizeSemantics)
        self._assign_optional("is_optional", is_optional, bool)
        if sub_elements is not None:
            for elem in sub_elements:
                self.append(elem)
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")

    def append(self, elem: "ImplementationDataTypeElement") -> None:
        """
        Appends elem to sub_element list
        """
        if isinstance(elem, ImplementationDataTypeElement):
            self.sub_elements.append(elem)
        else:
            raise TypeError("'elem' must be of type ImplementationDataTypeElement")


class ImplementationDataType(AutosarDataType):
    """
    AR: IMPLEMENTATION-DATA-TYPE
    Type: Concrete
    Tag Variants: 'IMPLEMENTATION-DATA-TYPE'
    """

    def __init__(self,
                 name: str,
                 dynamic_array_size_profile: str | None = None,
                 is_struct_with_optional_element: bool | None = None,
                 sub_elements: list[ImplementationDataTypeElement] | None = None,
                 symbol_props: SymbolProps | None = None,
                 type_emitter: str | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.dynamic_array_size_profile: str | None = None                  # .DYNAMIC-ARRAY-SIZE-PROFILE
        self.is_struct_with_optional_element: bool | None = None            # .IS-STRUCT-WITH-OPTIONAL-ELEMENT
        self.sub_elements: list[ImplementationDataTypeElement] = []         # .SUB-ELEMENTS
        self.symbol_props: SymbolProps | None = None                        # .SYMBOL-PROPS
        self.type_emitter: str | None = None                                # .TYPE-EMITTER
        self._assign_optional('dynamic_array_size_profile', dynamic_array_size_profile, str)
        self._assign_optional('is_struct_with_optional_element', is_struct_with_optional_element, bool)
        self._assign_optional('type_emitter', type_emitter, str)
        if sub_elements is not None:
            for elem in sub_elements:
                self.append(elem)
        if symbol_props is not None:
            if isinstance(symbol_props, SymbolProps):
                self.symbol_props = symbol_props
            else:
                raise TypeError("'symbol_props' must be of type SymbolProps")

    def append(self, elem: ImplementationDataTypeElement) -> None:
        """
        Appends elem to sub_element list
        """
        if isinstance(elem, ImplementationDataTypeElement):
            self.sub_elements.append(elem)
        else:
            raise TypeError("'elem' must be of type ImplementationDataTypeElement")

    def ref(self) -> ImplementationDataTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ImplementationDataTypeRef(ref_str)

    def find(self, ref: str) -> Any:
        """
        Finds item by reference
        """
        assert "/" not in ref
        return self._find_by_name(self.sub_elements, ref)


class DataPrototype(Identifiable):
    """
    Group AR:DATA-PROTOTYPE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 sw_data_def_props: SwDataDefProps | SwDataDefPropsConditional | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.sw_data_def_props: SwDataDefProps | None = None  # .SW-DATA-DEF-PROPS
        if sw_data_def_props is not None:
            if isinstance(sw_data_def_props, SwDataDefProps):
                self.sw_data_def_props = sw_data_def_props
            elif isinstance(sw_data_def_props, SwDataDefPropsConditional):
                self.sw_data_def_props = SwDataDefProps(sw_data_def_props)
            else:
                raise TypeError("'sw_data_def_props' must be one of (SwDataDefProps, SwDataDefPropsConditional)")


class AutosarDataPrototype(DataPrototype):
    """
    Group AR:AUTOSAR-DATA-PROTOTYPE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 type_ref: AutosarDataTypeRef | ImplementationDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: AutosarDataTypeRef | None = None  # .TYPE-TREF
        if type_ref is not None:
            if isinstance(type_ref, AutosarDataTypeRef):
                pass
            elif isinstance(type_ref, ImplementationDataTypeRef):
                type_ref = AutosarDataTypeRef(type_ref.value, ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE)
            else:
                msg = f"type_ref: Invalid type '{str(type(type_ref))}'."
                raise TypeError(msg + " Expected type 'AutosarDataTypeRef' or 'ImplementationDataTypeRef'")
            self._set_attr_with_strict_type("type_ref", type_ref, AutosarDataTypeRef)


class VariableDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:VARIABLE-DATA-PROTOTYPE
    Type: Concrete
    Tag variants: 'VARIABLE-DATA-PROTOTYPE' | 'BULK-NV-BLOCK' | 'RAM-BLOCK'
    """

    def __init__(self,
                 name: str,
                 init_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        # .VARIATION-POINT not supported
        self._assign_optional_strict("init_value", init_value, ValueSpecification)

    def ref(self) -> VariableDataPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else VariableDataPrototypeRef(ref_str)

    @property
    def is_queued(self) -> bool:
        """
        Returns True if internal sw_data_def_props has its impl_policy is set to QUEUED
        """
        if self.sw_data_def_props is not None and len(self.sw_data_def_props.variants) > 0:
            return self.sw_data_def_props.variants[0].is_queued
        return False


class ParameterDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:PARAMETER-DATA-PROTOTYPE
    Type: Concrete
    Tag variants: 'PARAMETER-DATA-PROTOTYPE' | 'ROM-BLOCK'
    """

    def __init__(self,
                 name: str,
                 init_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        # .VARIATION-POINT not supported
        self._assign_optional_strict("init_value", init_value, ValueSpecification)

    def ref(self) -> ParameterDataPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ParameterDataPrototypeRef(ref_str)


class ArgumentDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:ARGUMENT-DATA-PROTOTYPE
    Type: Concrete
    Tag variants: 'ARGUMENT-DATA-PROTOTYPE'
    """

    def __init__(self,
                 name: str,
                 direction: ar_enum.ArgumentDirection | None = None,
                 server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.direction: ar_enum.ArgumentDirection | None = None  # .DIRECTION
        self.server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None  # .SERVER-ARGUMENT-IMPL-POLICY
        # .TYPE-BLUEPRINTS not supported
        # .VARIATION-POINT not supported
        self._assign_optional("direction", direction, ar_enum.ArgumentDirection)
        self._assign_optional("server_arg_impl_policy", server_arg_impl_policy, ar_enum.ServerArgImplPolicy)


class ApplicationDataType(AutosarDataType):
    """
    Group AR:APPLICATION-DATA-TYPE
    Type: Abstract
    """


class ApplicationCompositeDataType(ApplicationDataType):
    """
    Group AR:APPLICATION-COMPOSITE-DATA-TYPE
    Type: Abstract
    """

    @property
    def is_composite(self):
        """Is this a composite data type?"""
        return True


class ApplicationPrimitiveDataType(ApplicationDataType):
    """
    Complex type AR:APPLICATION-PRIMITIVE-DATA-TYPE
    Type: Concrete
    Tag variants: 'APPLICATION-PRIMITIVE-DATA-TYPE'
    """

    @property
    def is_composite(self):
        """Is this a composite data type?"""
        return False

    def ref(self) -> ApplicationDataTypeRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationDataTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE)


class ApplicationCompositeElementDataPrototype(DataPrototype):
    """
    Group AR:APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 type_ref: ApplicationDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: ApplicationDataTypeRef | None = None  # .TYPE-TREF
        self._assign_optional_strict('type_ref', type_ref, ApplicationDataTypeRef)


class ApplicationArrayElement(ApplicationCompositeElementDataPrototype):
    """
    Complex type AR:APPLICATION-ARRAY-ELEMENT
    Type: Concrete
    Tag variants: 'ELEMENT'
    """

    def __init__(self,
                 name: str,
                 max_number_of_elements: int | None = None,
                 array_size_handling: ar_enum.ArraySizeHandling | None = None,
                 array_size_semantics: ar_enum.ArraySizeSemantics | None = None,
                 index_data_type_ref: IndexDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.array_size_handling: ar_enum.ArraySizeHandling | None = None     # .ARRAY-SIZE-HANDLING
        self.array_size_semantics: ar_enum.ArraySizeSemantics | None = None   # .ARRAY-SIZE-SEMANTICS
        self.max_number_of_elements: int | None = None                        # ."MAX-NUMBER-OF-ELEMENTS
        self.index_data_type_ref: IndexDataTypeRef | None = None              # .INDEX-DATA-TYPE-REF
        self._assign_optional("array_size_handling", array_size_handling, ar_enum.ArraySizeHandling)
        self._assign_optional("array_size_semantics", array_size_semantics, ar_enum.ArraySizeSemantics)
        self._assign_optional_positive_int("max_number_of_elements", max_number_of_elements)
        self._assign_optional("index_data_type_ref", index_data_type_ref, IndexDataTypeRef)


class ApplicationArrayDataType(ApplicationCompositeDataType):
    """
    Complex type AR:APPLICATION-ARRAY-DATA-TYPE
    Type: Concrete
    Tag variants: 'APPLICATION-ARRAY-DATA-TYPE'
    """

    def __init__(self,
                 name: str,
                 dynamic_array_size_profile: str | None = None,
                 element: ApplicationArrayElement | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.dynamic_array_size_profile: str | None = None                  # .DYNAMIC-ARRAY-SIZE-PROFILE
        self.element: ApplicationArrayElement | None = None                 # .ELEMENT
        self._assign_optional('dynamic_array_size_profile', dynamic_array_size_profile, str)
        self._assign_optional_strict('element', element, ApplicationArrayElement)

    def ref(self) -> ApplicationDataTypeRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationDataTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE)


class ApplicationRecordElement(ApplicationCompositeElementDataPrototype):
    """
    Complex type AR:APPLICATION-RECORD-ELEMENT
    Type: Concrete
    Tag variants: 'APPLICATION-RECORD-ELEMENT'
    """

    def __init__(self,
                 name: str,
                 is_optional: bool | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.is_optional: bool | None = None  # .IS-OPTIONAL
        self._assign_optional('is_optional', is_optional, bool)


class ApplicationRecordDataType(ApplicationCompositeDataType):
    """
    Complex type AR:APPLICATION-RECORD-DATA-TYPE
    Type: Concrete
    Tag variants: 'APPLICATION-RECORD-DATA-TYPE'
    """

    def __init__(self,
                 name: str,
                 elements: ApplicationRecordElement | list[ApplicationRecordElement] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.elements: list[ApplicationRecordElement] = []
        if elements is not None:
            if isinstance(elements, ApplicationRecordElement):
                self.append(elements)
            elif isinstance(elements, list):
                self.extend(elements)

    def append(self, element: ApplicationRecordElement) -> None:
        """
        Appends element to elements list
        """
        if isinstance(element, ApplicationRecordElement):
            self.elements.append(element)
        else:
            raise TypeError("'element' must be of type ApplicationRecordElement")

    def extend(self, elements: list[ApplicationRecordElement]) -> None:
        """
        Extends elements to elements list
        """
        for element in elements:  # We want to type-check each element before adding to internal list
            self.append(element)

    def ref(self) -> ApplicationDataTypeRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationDataTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE)


class DataTypeMap(ARObject):
    """
    Complex type AR:DATA-TYPE-MAP
    Type: Concrete
    Tag variants: 'DATA-TYPE-MAP'
    """

    def __init__(self,
                 appl_data_type_ref: ApplicationDataTypeRef | None = None,
                 impl_data_type_ref: ImplementationDataTypeRef | None = None,
                 ) -> None:
        self.appl_data_type_ref = appl_data_type_ref   # .APPLICATION-DATA-TYPE-REF
        self.impl_data_type_ref = impl_data_type_ref   # .IMPLEMENTATION-DATA-TYPE-REF


class DataTypeMappingSet(ARElement):
    """
    Complex type AR:DATA-TYPE-MAPPING-SET
    Type: Concrete
    Tag variants: 'DATA-TYPE-MAPPING-SET'
    """

    def __init__(self,
                 name: str,
                 data_type_maps: DataTypeMap | list[DataTypeMap] | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.data_type_maps: list[DataTypeMap] = []  # .DATA-TYPE-MAPS
        self.mode_request_type_maps = []  # .MODE-REQUEST-TYPE-MAPS (Not yet implemented)
        if data_type_maps is not None:
            if isinstance(data_type_maps, DataTypeMap):
                self.append(data_type_maps)
            elif isinstance(data_type_maps, list):
                for data_type_map in data_type_maps:
                    self.append(data_type_map)
            else:
                raise TypeError(f'data_type_maps: Invalid type "{str(type(data_type_maps))}"')

    def append(self, element: DataTypeMap) -> None:
        """
        Appends element to one of the inner lists based on parameter type
        Currently, appending to mode_request_type_maps isn't
        implemented.
        """
        if isinstance(element, DataTypeMap):
            self.data_type_maps.append(element)
        else:
            raise TypeError(f'Unexpected type: "{str(type(element))}"')


class ValueList(ARObject):
    """
    Complex type AR:VALUE-LIST
    Type: Concrete
    Tag variants: 'SW-ARRAYSIZE'
    """

    def __init__(self, values: list[int | float | NumericalValue] | None = None) -> None:
        self.values = []
        if values is not None:
            if isinstance(values, (int, float)):
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


# Software address method (partly implemented)


class SwAddrMethod(ARElement):
    """
    Complex type AR:SW-ADDR-METHOD
    Type: Concrete
    Tag Variants: 'SW-ADDR-METHOD'
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.memory_allocation_keyword_policy = None  # .MEMORY-ALLOCATION-KEYWORD-POLICY
        self.options = []  # .OPTIONS
        self.section_initialization_policy = None  # .SECTION-INITIALIZATION-POLICY
        self.section_type = None  # .SECTION-TYPE

    def ref(self) -> SwAddrMethodRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwAddrMethodRef(ref_str)

# --- Calibration data elements


SwValueElement = Union[int, float, str, NumericalValue, "ValueGroup"]  # Type alias


class SwValues(ARObject):
    """
    Complex type AR:SW-VALUES
    Type: Concrete
    Tag variants: SW-VALUES-PHYS
    """

    def __init__(self,
                 values: list[SwValueElement] | None = None) -> None:
        self.values = []
        if values is not None:
            if isinstance(values, (int, float, str, NumericalValue, ValueGroup)):
                self.append(values)
            elif isinstance(values, list):
                for value in values:
                    self.append(value)

    def append(self, value: SwValueElement) -> None:
        """
        Appends value to list of values
        XML elements not supported:

        - VTF
        - VF
        """
        if isinstance(value, (int, float, str, NumericalValue, ValueGroup)):
            self.values.append(value)
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")


class ValueGroup(SwValues):
    """
    Complex type AR:VALUE-GROUP
    Type: Concrete
    Tag variants: VG
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
    Type: Concrete
    Tag variants: SW-AXIS-CONT
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
    Type: Concrete
    Tag variants: SW-VALUE-CONT
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


# --- Constant and value specifications


class ValueSpecification(ARObject):
    """
    Group AR:VALUE-SPECIFCATION
    Type: Abstract
    Base class for value specifications
    """

    def __init__(self, label: str | None = None) -> None:
        self.label = label  # .SHORT-LABEL
        # .VARIATION-POINT not supported

    @classmethod
    def make_value_with_check(cls,
                              value: InitValueArgType | None = None,
                              ) -> ValueSpecificationElement:
        """
        Wrapper for checking and creating init values based on different value types
        """
        if value is not None:
            if isinstance(value, ValueSpecification):
                return value  # Already a proper init-value
            elif isinstance(value, ConstantRef):
                return ConstantReference(value)  # Wrap inside constant reference
            elif isinstance(value, (int, float, str, list, tuple)):
                return cls.make_value(value)  # Attempt to create a new value based on raw python data
            else:
                raise TypeError(f"Unsupported type: {str(type(value))}")
        return None

    @classmethod
    def make_value(cls, data: Any) -> ValueSpecificationElement:
        """
        Builds value specification based on Python data
        Format 1 - data is not a tuple:
          value = data
        Format 2 - data is 2-tuple:
          label = data[0]
          value = data[1]
        Format 3- data is a 3-tuple:
          label = data[0]
          value = None
          default_pattern = data[2]
          This format is used only when creating NotAvailableValueSpecification

        The type of 'value' can be one of:

        1. scalar value (int, float, str)
        2. list: (used for array and record values)
           When using list, the first list-element must contain a string containing a
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
                return ValueSpecification._make_array_value_spefication(label, value[1:])
            elif value[0].upper() in ("R", "RECORD"):
                return ValueSpecification._make_record_value_spefication(label, value[1:])
            else:
                raise ValueError(f"Invalid element type: {str(type(value[0]))}")
        else:
            raise TypeError(f"Invalid value type: {str(type(value))}")

    @classmethod
    def _make_array_value_spefication(cls, label: str | None, values: list) -> "ArrayValueSpecification":
        elements = []
        for value in values:
            elements.append(ValueSpecification.make_value(value))
        return ArrayValueSpecification(label, elements)

    @classmethod
    def _make_record_value_spefication(cls, label: str | None, values: list) -> "RecordValueSpecification":
        fields = []
        for value in values:
            fields.append(ValueSpecification.make_value(value))
        return RecordValueSpecification(label, fields)


class TextValueSpecification(ValueSpecification):
    """
    Complex type AR:TEXT-VALUE-SPECIFICATION
    Type: Concrete
    Tag variants: 'TEXT-VALUE-SPECIFICATION'
    """

    def __init__(self, label: str | None = None, value: str | None = None) -> None:
        super().__init__(label)
        self.value = None if value is None else str(value)


class NumericalValueSpecification(ValueSpecification):
    """
    Complex type AR:NUMERICAL-VALUE-SPECIFICATION
    Type: Concrete
    Tag variants: 'NUMERICAL-VALUE-SPECIFICATION'
    """

    def __init__(self, label: str | None = None, value: int | float | None = None) -> None:
        super().__init__(label)
        self.value = value


class NotAvailableValueSpecification(ValueSpecification):
    """
    Complex type AR:NOT-AVAILABLE-VALUE-SPECIFICATION
    Type: Concrete
    Tag variants: 'NOT-AVAILABLE-VALUE-SPECIFICATION'
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


class ArrayValueSpecification(ValueSpecification):
    """
    Complex type AR:ARRAY-VALUE-SPECIFICATION
    Type: Concrete
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
    Type: Concrete
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
    Type: Concrete
    Tag variants: APPLICATION-VALUE-SPECIFICATION
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
    Type: Concrete
    Tag Variants: 'CONSTANT-SPECIFICATION'
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
    Type: Concrete
    Tag variants 'CONSTANT-REFERENCE'

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


# --- Package (Partly implemented)


class Package(CollectableElement):
    """
    AR:PACKAGE
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.elements: list[ARElement] = []
        self.packages: list[Package] = []
        self._collection_map = {}

    def append(self, item: CollectableElement):
        """
        Append element or sub-package
        """
        if isinstance(item, Package):
            package: Package = item
            if package.name in self._collection_map:
                raise ValueError(
                    f"Package with SHORT-NAME '{package.name}' already exists in package '{self.name}")
            package.parent = self
            self.packages.append(package)
            self._collection_map[package.name] = package
        elif isinstance(item, ARElement):
            elem: ARElement = item
            if elem.name in self._collection_map:
                raise ValueError(
                    f"Element with SHORT-NAME '{elem.name}' already exists in package '{self.name}'")
            elem.parent = self
            self.elements.append(elem)
            self._collection_map[elem.name] = elem
        else:
            raise TypeError(f"Invalid type {str(type(item))}")

    def make_packages(self, ref: str) -> "Package":
        """
        Recursively creates sub-packages
        """
        if ref.startswith('/'):
            raise ValueError("Reference string can't start with '/'")
        parts = ref.partition('/')
        package = self._collection_map.get(parts[0], None)
        if package is None:
            package = self.create_package(parts[0])
        elif not isinstance(package, Package):
            raise KeyError(f"Item with name '{parts[0]}' already exists but isn't a package")
        if len(parts[2]) > 0:
            return package.make_packages(parts[2])
        else:
            return package

    def create_package(self, name: str, **kwargs) -> "Package":
        """
        Creates new sub-package
        """
        if name in self._collection_map:
            return ValueError(f"Package with name '{name}' already exists")
        package = Package(name, **kwargs)
        self._collection_map[name] = package
        self.packages.append(package)
        package.parent = self
        return package

    def find(self, ref: str) -> Any:
        """
        Finds item by reference
        """
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        item = self._collection_map.get(parts[0], None)
        if item is not None:
            if len(parts[2]) > 0:
                return item.find(parts[2])
        return item

    def filter(self, *names: str) -> Iterator[ARElement]:
        """
        Yields all elements whose short-name matches any of the names in
        argument list
        """
        for elem in self.elements:
            if elem.name in names:
                yield elem

    def filter_regex(self, pattern: str | re.Pattern) -> Iterator[ARElement]:
        """
        Yields all elements whose short-name matches the given regex pattern
        """
        regex: re.Pattern = None
        if isinstance(pattern, str):
            regex = re.compile(pattern)
        elif isinstance(pattern, re.Pattern):
            regex = pattern
        else:
            raise TypeError(f"pattern: Invalid type '{str(type(pattern))}'")
        for elem in self.elements:
            if regex.match(elem.name):
                yield elem

# --- ModeDeclaration elements


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
    tag variants: 'MODE-TRANSITION'
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


MODE_DECLARATION_TYPES = ModeDeclaration | list[ModeDeclaration] | list[str] | list[tuple[str, int]]


class ModeDeclarationGroup(ARElement):
    """
    Complex type AR:MODE-DECLARATION-GROUP
    Tag variants: 'MODE-DECLARATION-GROUP'
    """

    def __init__(self,
                 name: str,
                 mode_declarations: MODE_DECLARATION_TYPES | None = None,
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
                self.append_mode_declaratation(mode_declarations)
            elif isinstance(mode_declarations, list):
                for mode_declaration in mode_declarations:
                    if isinstance(mode_declaration, ModeDeclaration):
                        self.append_mode_declaratation(mode_declaration)
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

    def append_mode_declaratation(self, mode_declaration: ModeDeclaration) -> None:
        """
        Appends mode declaratopm to internal list of mode declarations
        """
        if isinstance(mode_declaration, ModeDeclaration):
            mode_declaration.parent = self
            self.mode_declarations.append(mode_declaration)
        else:
            msg = f"mode_declaration: Invalid type '{str(type(mode_declaration))}'"
            raise TypeError(msg + ". Expected 'ModeDeclaration'")

    def create_mode_declaration(self,
                                name: str,
                                value: int | None = None,
                                **kwargs) -> ModeDeclaration:
        """
        Convenience method for creating a new mode declaration within this group
        """
        mode_declaration = ModeDeclaration(name, value, **kwargs)
        self.append_mode_declaratation(mode_declaration)
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
                  | 'PROCESS-STATE-MACHINE' | 'STATE-MACHINE'
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

# --- Port Interface elements


class PortInterface(ARElement):
    """
    Group AR:PORT-INTERFACE
    Type: Abstract
    """

    def __init__(self,
                 name: str,
                 is_service: bool | None = None,
                 service_kind: ar_enum.ServiceKind | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.is_service: bool | None = None  # .IS-SERVICE
        # .NAMESPACES not supported
        self.service_kind: ar_enum.ServiceKind | None = None  # .SERVICE-KIND
        self._assign_optional_strict("is_service", is_service, bool)
        self._assign_optional_strict("service_kind", service_kind, ar_enum.ServiceKind)


class DataInterface(PortInterface):
    """
    Group AR-DATA-INTERFACE
    Type: Abstract

    Base class for data-concerned interfaces (as opposed to operations-based)
    """


class InvalidationPolicy(ARObject):
    """
    Complex type AR:INVALIDATION-POLICY
    Type: Concrete
    Tag variants: 'INVALIDATION-POLICY'
    """

    def __init__(self,
                 data_element_ref: VariableDataPrototypeRef | None = None,
                 handle_invalid: ar_enum.HandleInvalid | None = None) -> None:
        self.data_element_ref: VariableDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        self.handle_invalid: ar_enum.HandleInvalid | None = None  # .HANDLE-INVALID
        self._assign_optional("data_element_ref", data_element_ref, VariableDataPrototypeRef)
        self._assign_optional("handle_invalid", handle_invalid, ar_enum.HandleInvalid)


class SenderReceiverInterface(DataInterface):
    """
    Complex type AR:SENDER-RECEIVER-INTERFACE
    Type: Concrete
    Tag variants: 'SENDER-RECEIVER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 data_elements: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 invalidation_policies: InvalidationPolicy | list[InvalidationPolicy] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.data_elements: list[VariableDataPrototype] = []  # .DATA-ELEMENTS
        self.invalidation_policies: list[InvalidationPolicy] = []  # .INVALIDATION-POLICYS
        # .META-DATA-ITEM-SETS not supported
        if data_elements is not None:
            if isinstance(data_elements, VariableDataPrototype):
                self.append_data_element(data_elements)
            elif isinstance(data_elements, list):
                for data_element in data_elements:
                    self.append_data_element(data_element)
            else:
                msg = f"data_elements: Invalid type '{str(type(data_element))}'"
                raise TypeError(msg + ". Expected 'VariableDataPrototype' or list[VariableDataPrototype]")
        if invalidation_policies is not None:
            if isinstance(invalidation_policies, InvalidationPolicy):
                self.append_invalidation_policy(invalidation_policies)
            elif isinstance(invalidation_policies, list):
                for invalidation_policy in invalidation_policies:
                    self.append_invalidation_policy(invalidation_policy)
            else:
                msg = f"data_elements: Invalid type '{str(type(invalidation_policies))}'"
                raise TypeError(msg + ". Expected 'InvalidationPolicy' or list[InvalidationPolicy]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE)

    def append_data_element(self, data_element: VariableDataPrototype):
        """
        Appends data element to internal list of elements
        """
        if isinstance(data_element, VariableDataPrototype):
            data_element.parent = self
            self.data_elements.append(data_element)
        else:
            msg = f"data_element: Invalid type '{str(type(data_element))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototype'")

    def append_invalidation_policy(self, invalidation_policy: InvalidationPolicy):
        """
        Appends invalidation policy to internal list of policies
        """
        if isinstance(invalidation_policy, InvalidationPolicy):
            self.invalidation_policies.append(invalidation_policy)
        else:
            msg = f"invalidation_policy: Invalid type '{str(type(invalidation_policy))}'"
            raise TypeError(msg + ". Expected 'InvalidationPolicy'")

    def create_data_element(self,
                            name: str,
                            init_value: ValueSpecificationElement | None = None,
                            **kwargs) -> VariableDataPrototype:
        """
        Convenience method for adding a new data element to this port interface
        """
        data_element = VariableDataPrototype(name, init_value, **kwargs)
        self.append_data_element(data_element)
        return data_element

    def create_invalidation_policy(self,
                                   data_element_ref: VariableDataPrototypeRef | str,
                                   handle_invalid: ar_enum.HandleInvalid) -> InvalidationPolicy:
        """
        Convenience method for adding a new invalidation policy to this port interface
        """
        if isinstance(data_element_ref, str):
            data_element_ref = VariableDataPrototypeRef(data_element_ref)
        elif not isinstance(data_element_ref, VariableDataPrototypeRef):
            msg = f"data_element_ref: Invalid type '{str(type(data_element_ref))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototypeRef' or 'str'")
        if not isinstance(handle_invalid, ar_enum.HandleInvalid):
            msg = f"handle_invalid: Invalid type '{str(type(data_element_ref))}'"
            raise TypeError(msg + ". Expected 'HandleInvalid'")
        invalidation_policy = InvalidationPolicy(data_element_ref, handle_invalid)
        self.append_invalidation_policy(invalidation_policy)
        return invalidation_policy


class NvDataInterface(DataInterface):
    """
    Complex type AR:NV-DATA-INTERFACE
    Type: Concrete
    Tag variants: 'NV-DATA-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 data_elements: VariableDataPrototype | list[VariableDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.data_elements: list[VariableDataPrototype] = []  # .NV-DATAS
        if data_elements is not None:
            if isinstance(data_elements, VariableDataPrototype):
                self.append_data_element(data_elements)
            elif isinstance(data_elements, list):
                for data_element in data_elements:
                    self.append_data_element(data_element)
            else:
                msg = f"nv_datas: Invalid type '{str(type(data_elements))}'"
                raise TypeError(msg + ". Expected 'VariableDataPrototype' or list[VariableDataPrototype]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE)

    def append_data_element(self, nv_data: VariableDataPrototype):
        """
        Appends data element to internal list of data elements
        """
        if isinstance(nv_data, VariableDataPrototype):
            self.data_elements.append(nv_data)
        else:
            msg = f"nv_data: Invalid type '{str(type(nv_data))}'"
            raise TypeError(msg + ". Expected 'VariableDataPrototype'")

    def create_data_element(self,
                            name: str,
                            init_value: ValueSpecificationElement | None = None,
                            **kwargs) -> VariableDataPrototype:
        """
        Convenience method for adding a new data element to this port interface
        """
        data_element = VariableDataPrototype(name, init_value, **kwargs)
        self.append_data_element(data_element)
        return data_element


class ParameterInterface(DataInterface):
    """
    Complex type AR:PARAMETER-INTERFACE
    Type: Concrete
    Tag variants: 'PARAMETER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 parameters: ParameterDataPrototype | list[ParameterDataPrototype] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.parameters: list[ParameterDataPrototype] = []  # .PARAMETERS
        if parameters is not None:
            if isinstance(parameters, ParameterDataPrototype):
                self.append_parameter(parameters)
            elif isinstance(parameters, list):
                for parameter in parameters:
                    self.append_parameter(parameter)
            else:
                msg = f"parameters: Invalid type '{str(type(parameters))}'"
                raise TypeError(msg + ". Expected 'ParameterDataPrototype' or list[ParameterDataPrototype]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE)

    def append_parameter(self, parameter: ParameterDataPrototype):
        """
        Appends parameter to internal list of parameters
        """
        if isinstance(parameter, ParameterDataPrototype):
            self.parameters.append(parameter)
        else:
            msg = f"parameter: Invalid type '{str(type(parameter))}'"
            raise TypeError(msg + ". Expected 'ParameterDataPrototype'")

    def create_parameter(self,
                         name: str,
                         init_value: ValueSpecificationElement | None = None,
                         **kwargs) -> ParameterDataPrototype:
        """
        Convenience method for adding a new parameter to this port interface
        """
        data_element = ParameterDataPrototype(name, init_value, **kwargs)
        self.append_parameter(data_element)
        return data_element


class ApplicationError(Identifiable):
    """
    Complex type AR:APPLICATION-ERROR
    Tag variants: 'APPLICATION-ERROR'
    """

    def __init__(self,
                 name: str,
                 error_code: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.error_code: int | None = None
        self._assign_optional_strict("error_code", error_code, int)

    def ref(self) -> ApplicationErrorRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationErrorRef(ref_str)


PossibleErrorRefsTypes = ApplicationErrorRef | list[ApplicationErrorRef] | str | list[str]


class ClientServerOperation(Identifiable):
    """
    Complex type AR:CLIENT-SERVER-OPERATION
    Tag variants: 'CLIENT-SERVER-OPERATION'
    """

    def __init__(self,
                 name: str,
                 arguments: ArgumentDataPrototype | list[ArgumentDataPrototype] | None = None,
                 diag_arg_integrity: bool | None = None,
                 fire_and_forget: bool | None = None,
                 possible_error_refs: PossibleErrorRefsTypes | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.arguments: list[ArgumentDataPrototype] = []  # .ARGUMENTS
        self.diag_arg_integrity: bool | None = None  # .DIAG-ARG-INTEGRITY
        self.fire_and_forget: bool | None = None  # .FIRE-AND-FORGET
        # .POSSIBLE-AP-ERROR-REFS not supported
        # .POSSIBLE-AP-ERROR-SET-REFS not supported
        self.possible_error_refs: list[ApplicationErrorRef] = []  # .POSSIBLE-ERROR-REFS
        # .VARIATION-POINT not supported

        self._assign_optional_strict("diag_arg_integrity", diag_arg_integrity, bool)
        self._assign_optional_strict("fire_and_forget", fire_and_forget, bool)
        if arguments is not None:
            if isinstance(arguments, ArgumentDataPrototype):
                self.append_argument(arguments)
            elif isinstance(arguments, list):
                for argument in arguments:
                    self.append_argument(argument)
            else:
                msg = f"parameters: Invalid type '{str(type(arguments))}'"
                raise TypeError(msg + ". Expected 'ArgumentDataPrototype' or list[ArgumentDataPrototype]")

        if possible_error_refs is not None:
            if isinstance(possible_error_refs, ApplicationErrorRef):
                self.append_possible_error_ref(possible_error_refs)
            elif isinstance(possible_error_refs, str):
                self.append_possible_error_ref(ApplicationErrorRef(possible_error_refs))
            elif isinstance(possible_error_refs, list):
                for possible_error_ref in possible_error_refs:
                    self.append_possible_error_ref(possible_error_ref)
            else:
                msg = f"possible_error_refs: Invalid type '{str(type(possible_error_refs))}'"
                raise TypeError(msg + ". Expected 'ApplicationErrorRef' or list[ApplicationErrorRef]")

    def ref(self) -> ClientServerOperationRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ClientServerOperationRef(ref_str)

    def append_argument(self, argument: ArgumentDataPrototype) -> None:
        """
        Appends argument to internal list of arguments
        """
        if isinstance(argument, ArgumentDataPrototype):
            self.arguments.append(argument)
        else:
            msg = f"argument: Invalid type '{str(type(argument))}'"
            raise TypeError(msg + ". Expected 'ArgumentDataPrototype'")

    def create_argument(self,
                        name: str,
                        direction: ar_enum.ArgumentDirection | None = None,
                        server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                        **kwargs) -> ArgumentDataPrototype:
        """
        Convenience method for adding a new argument to this operation
        """
        argument = ArgumentDataPrototype(name, direction, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def create_in_argument(self,
                           name: str,
                           server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                           **kwargs) -> ArgumentDataPrototype:
        """
        Convenience method for adding a new in-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.IN, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def create_inout_argument(self,
                              name: str,
                              server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                              **kwargs) -> ArgumentDataPrototype:
        """
        Convenience method for adding a new inout-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.INOUT, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def create_out_argument(self,
                            name: str,
                            server_arg_impl_policy: ar_enum.ServerArgImplPolicy | None = None,
                            **kwargs) -> ArgumentDataPrototype:
        """
        Convenience method for adding a new out-argument to this operation
        """
        argument = ArgumentDataPrototype(name, ar_enum.ArgumentDirection.OUT, server_arg_impl_policy, **kwargs)
        self.append_argument(argument)
        return argument

    def append_possible_error_ref(self, possible_error_ref: ApplicationErrorRef) -> None:
        """
        Appends error reference to internal list of possible errors for this operation
        """
        if isinstance(possible_error_ref, ApplicationErrorRef):
            self.possible_error_refs.append(possible_error_ref)
        else:
            msg = f"argument: Invalid type '{str(type(possible_error_ref))}'"
            raise TypeError(msg + ". Expected 'ApplicationErrorRef'")

    def create_possible_error_ref(self, value: str) -> ApplicationErrorRef:
        """
        Convenience method for creating and adding a new possible error reference to this operation
        """
        possible_error_ref = ApplicationErrorRef(value)
        self.append_possible_error_ref(possible_error_ref)
        return possible_error_ref


class ClientServerInterface(PortInterface):
    """
    Complex type AR:CLIENT-SERVER-INTERFACE
    Tag variants: 'CLIENT-SERVER-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 operations: ClientServerOperation | list[ClientServerOperation] | None = None,
                 possible_errors: ApplicationError | list[ApplicationError] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.operations: list[ClientServerOperation] = []
        self.possible_errors: list[ApplicationError] = []

        if operations is not None:
            if isinstance(operations, ClientServerOperation):
                self.append_operation(operations)
            elif isinstance(operations, list):
                for operation in operations:
                    self.append_operation(operation)
            else:
                msg = f"operations: Invalid type '{str(type(operations))}'"
                raise TypeError(msg + ". Expected 'ClientServerOperation' or list[ClientServerOperation]")

        if possible_errors is not None:
            if isinstance(possible_errors, ApplicationError):
                self.append_operation(possible_errors)
            elif isinstance(possible_errors, list):
                for possible_error in possible_errors:
                    self.append_possible_errors(possible_error)
            else:
                msg = f"possible_errors: Invalid type '{str(type(possible_errors))}'"
                raise TypeError(msg + ". Expected 'ApplicationError' or list[ApplicationError]")

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE)

    def append_operation(self, operation: ClientServerOperation) -> None:
        """
        Appends operation to internal list of operations
        """
        if isinstance(operation, ClientServerOperation):
            operation.parent = self
            self.operations.append(operation)
        else:
            msg = f"operation: Invalid type '{str(type(operation))}'"
            raise TypeError(msg + ". Expected 'ClientServerOperation'")

    def append_possible_errors(self, possible_error: ApplicationError) -> None:
        """
        Appends possible error to internal list of possible errors
        """
        if isinstance(possible_error, ApplicationError):
            possible_error.parent = self
            self.possible_errors.append(possible_error)
        else:
            msg = f"operation: Invalid type '{str(type(possible_error))}'"
            raise TypeError(msg + ". Expected 'ApplicationError'")

    def create_operation(self,
                         name: str,
                         arguments: ArgumentDataPrototype | list[ArgumentDataPrototype] | None = None,
                         diag_arg_integrity: bool | None = None,
                         fire_and_forget: bool | None = None,
                         possible_error_refs: ApplicationErrorRef | list[ApplicationErrorRef] | None = None,
                         **kwargs) -> ClientServerOperation:
        """
        Convenience method for creating a new operation in this port interface
        """
        operation = ClientServerOperation(name, arguments, diag_arg_integrity, fire_and_forget, possible_error_refs,
                                          **kwargs)
        self.append_operation(operation)
        return operation

    def create_possible_error(self,
                              name: str,
                              error_code: int | None = None,
                              **kwargs) -> ApplicationError:
        """
        Convenience-method for creating a new possible error in this port interface
        """
        possible_error = ApplicationError(name, error_code, **kwargs)
        self.append_possible_errors(possible_error)
        return possible_error


class ModeSwitchInterface(PortInterface):
    """
    Complex type AR:MODE-SWITCH-INTERFACE
    Tag variants: 'MODE-SWITCH-INTERFACE'
    """

    def __init__(self,
                 name: str,
                 mode_group: ModeDeclarationGroupPrototype | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.mode_group: ModeDeclarationGroupPrototype | None = None
        self._assign_optional_strict("mode_group", mode_group, ModeDeclarationGroupPrototype)

    def ref(self) -> PortInterfaceRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortInterfaceRef(ref_str, ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE)

    def create_mode_group(self,
                          name: str,
                          type_ref: ModeDeclarationGroupRef | None = None,
                          calibration_access: ar_enum.SwCalibrationAccess | None = None,
                          **kwargs) -> ModeDeclarationGroupPrototype:
        """
        Convenience method for both creating and setting the mode_group property
        """
        self.mode_group = ModeDeclarationGroupPrototype(name, type_ref, calibration_access, **kwargs)
        return self.mode_group

# --- System Template Elements


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

    def __init__(self,
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
                 window_size: int | None = None,
                 window_size_init: int | None = None,
                 window_size_invalid: int | None = None,
                 window_size_valid: int | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.clear_from_valid_to_invalid: bool | None = None  # .CLEAR-FROM-VALID-TO-INVALID
        self.disable_e2e_check: bool | None = None  # .DISABLE-END-TO-END-CHECK
        self.disable_e2e_state_machine: bool | None = None  # .DISABLE-END-TO-END-STATE-MACHINE
        # .E-2-E-PROFILE-COMPATIBILITY-PROPS-REF
        self.e2e_profile_compatibility_props_ref: E2EProfileCompatibilityPropsRef | None = None
        self.max_delta_counter: int | None = None  # .MAX-DELTA-COUNTER
        self.max_error_state_init: int | None = None  # .MAX-ERROR-STATE-INIT
        self.max_error_state_invalid: int | None = None   # .MAX-ERROR-STATE-INVALID
        self.max_error_state_valid: int | None = None   # .MAX-ERROR-STATE-VALID
        self.max_no_new_repeated_data: int | None = None   # .MAX-NO-NEW-OR-REPEATED-DATA
        self.min_ok_state_init: int | None = None   # .MIN-OK-STATE-INIT
        self.min_ok_state_invalid: int | None = None   # .MIN-OK-STATE-INVALID
        self.min_ok_state_valid: int | None = None   # .MIN-OK-STATE-VALID
        self.sync_counter_init: int | None = None   # .SYNC-COUNTER-INIT
        self.window_size: int | None = None   # .WINDOW-SIZE
        self.window_size_init: int | None = None   # .WINDOW-SIZE-INIT
        self.window_size_invalid: int | None = None   # .WINDOW-SIZE-INVALID
        self.window_size_valid: int | None = None   # .WINDOW-SIZE-VALID
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
        self._assign_optional_positive_int("window_size", window_size)
        self._assign_optional_positive_int("window_size_init", window_size_init)
        self._assign_optional_positive_int("window_size_invalid", window_size_invalid)
        self._assign_optional_positive_int("window_size_valid", window_size_valid)


# --- SoftwareComponent elements


class ModeSwitchedAckRequest(ARObject):
    """
    Complex type AR:MODE-SWITCHED-ACK-REQUEST
    Tag variants: 'MODE-SWITCHED-ACK'
    """

    def __init__(self, timeout: float | None = None) -> None:
        super().__init__()
        self.timeout: float | None = None
        self._assign_optional("timeout", timeout, float)


class TransmissionAcknowledgementRequest(ARObject):
    """
    Complex type AR:TRANSMISSION-ACKNOWLEDGEMENT-REQUEST
    Tag variants: 'TRANSMISSION-ACKNOWLEDGE'
    """

    def __init__(self,
                 timeout: float | int | None = None) -> None:
        super().__init__()
        self.timeout: float | None = None  # .TIMEOUT
        self._assign_optional("timeout", timeout, float)


class TransmissionComSpecProps(ARObject):
    """
    Complex type AR:TRANSMISSION-COM-SPEC-PROPS
    Tag variants: 'TRANSMISSION-PROPS'

    This only exists in AUTOSAR 4.6 or newer (schema version >= 49)
    """

    def __init__(self,
                 data_update_period: float | int | None = None,
                 minimum_send_interval: float | int | None = None,
                 transmission_mode: ar_enum.TransmissionMode | None = None
                 ) -> None:
        super().__init__()
        self.data_update_period: float | int | None = None  # .DATA-UPDATE-PERIOD
        self.minimum_send_interval: float | int | None = None  # .MINIMUM-SEND-INTERVAL
        self.transmission_mode: ar_enum.TransmissionMode | None = None  # .TRANSMISSION-MODE
        self._assign_optional("data_update_period", data_update_period, float)
        self._assign_optional("minimum_send_interval", minimum_send_interval, float)
        self._assign_optional("transmission_mode", transmission_mode, ar_enum.TransmissionMode)


class ProvidePortComSpec(ARObject):
    """
    Group AR:P-PORT-COM-SPEC
    """

    @classmethod
    def make_from_port_interface(cls, port_interface: PortInterface, **kwargs) -> "ProvidePortComSpec":
        """
        Convenience method for creating P-PORT com-specs

        For SenderReceiverInterface:
        If interface has a single element: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple elements: kwargs is a dict of dict where
                                            outer dict keys are element names and each value
                                            is another dict containing key-value pairs for one com-spec

        For ClientServerInterface:
        If interface has a single operation: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple operations: kwargs is a dict of dict where
                                              outer dict keys are operation names and each value
                                              is another dict containing key-value pairs for one com-spec
        """
        if isinstance(port_interface, SenderReceiverInterface):
            if len(port_interface.data_elements) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one element")
            if len(port_interface.data_elements) == 1:
                data_element: VariableDataPrototype = port_interface.data_elements[0]
                if data_element.is_queued:
                    return QueuedSenderComSpec(data_element_ref=data_element.ref(), **kwargs)
                else:
                    return cls.make_non_queued_sender_com_spec(data_element_ref=data_element.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for element_name, value in kwargs.items():
                    unprocessed.add(element_name)
                    if not isinstance(value, dict):
                        msg = f"{port_interface.name}.{element_name}: Expected dict type, got {str(type(value))}"
                        raise TypeError(msg)
                for data_element in port_interface.data_elements:
                    if data_element.name in unprocessed:
                        unprocessed.remove(data_element.name)
                        com_spec_args = kwargs[data_element.name]
                        if data_element.is_queued:
                            com_spec = QueuedSenderComSpec(data_element_ref=data_element.ref(),
                                                           **com_spec_args)
                        else:
                            com_spec = cls.make_non_queued_sender_com_spec(data_element_ref=data_element.ref(),
                                                                           **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    operations = ', '.join(list[unprocessed])
                    raise ValueError(f"{port_interface.name}: Operation(s) not found in port interface: '{operations}'")
                return com_spec_list
        if isinstance(port_interface, ClientServerInterface):
            if len(port_interface.operations) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one operation")
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
                return ServerComSpec(operation_ref=operation.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for operation_name in kwargs:
                    unprocessed.add(operation_name)
                for operation in port_interface.operations:
                    if operation.name in unprocessed:
                        unprocessed.remove(operation.name)
                        com_spec_args = kwargs[operation.name]
                        com_spec = ServerComSpec(operation_ref=operation.ref(), **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    element_names = ', '.join(list[unprocessed])
                    msg = f"{port_interface.name}: Data element(s) not found in port interface: '{element_names}'"
                    raise ValueError(msg)
                return com_spec_list
        else:
            raise NotImplementedError(str(type(port_interface)))

    @classmethod
    def make_non_queued_sender_com_spec(cls,
                                        init_value: InitValueArgType | None = None,
                                        **kwargs
                                        ) -> "NonqueuedSenderComSpec":
        """
        Convenience method for creating NonqueuedSenderComSpec
        """
        init_value = ValueSpecification.make_value_with_check(init_value)
        return NonqueuedSenderComSpec(init_value=init_value, **kwargs)


class SenderComSpec(ProvidePortComSpec):
    """
    Group AR:SENDER-COM-SPEC
    """

    def __init__(self,
                 data_element_ref: AutosarDataPrototypeRef | VariableDataPrototypeRef | None = None,
                 handle_out_of_range: ar_enum.HandleOutOfRange | None = None,
                 network_representation: SwDataDefProps | None = None,
                 transmission_acknowledge: TransmissionAcknowledgementRequest | float | None = None,
                 tranmsission_props: TransmissionComSpecProps | None = None,
                 uses_end_to_end_protection: bool | None = None
                 ) -> None:
        super().__init__()
        # .COMPOSITE-NETWORK-REPRESENTATIONS not supported
        self.data_element_ref: AutosarDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        # .DATA-UPDATE-PERIOD not supported (Status Removed)
        self.handle_out_of_range: ar_enum.HandleOutOfRange | None = None  # .HANDLE-OUT-OF-RANGE
        self.network_representation: SwDataDefProps | None = None  # .NETWORK-REPRESENTATION
        # .SENDER-INTENT not supported (Adaptive Platform)
        self.transmission_acknowledge: TransmissionAcknowledgementRequest | None = None  # .TRANSMISSION-ACKNOWLEDGE
        self.tranmsission_props: TransmissionComSpecProps | None = None  # .TRANSMISSION-PROPS
        self.uses_end_to_end_protection: bool | None = None  # .USES-END-TO-END-PROTECTION
        if data_element_ref is not None:
            if isinstance(data_element_ref, AutosarDataPrototypeRef):
                self.data_element_ref = data_element_ref
            elif isinstance(data_element_ref, VariableDataPrototypeRef):
                self.data_element_ref = AutosarDataPrototypeRef(data_element_ref.value,
                                                                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
            else:
                raise ar_except.AssignmentTypeError("data_element_ref",
                                                    ("AutosarDataPrototypeRef", "VariableDataPrototypeRef"),
                                                    data_element_ref)
        self._assign_optional("handle_out_of_range", handle_out_of_range, ar_enum.HandleOutOfRange)
        self._assign_optional_strict("network_representation", network_representation, SwDataDefProps)
        self._assign_optional_strict("tranmsission_props", tranmsission_props, TransmissionComSpecProps)
        self._assign_optional("uses_end_to_end_protection", uses_end_to_end_protection, bool)
        if transmission_acknowledge is not None:
            if isinstance(transmission_acknowledge, (int, float)):
                self.transmission_acknowledge = TransmissionAcknowledgementRequest(transmission_acknowledge)
            elif isinstance(transmission_acknowledge, TransmissionAcknowledgementRequest):
                self.transmission_acknowledge = transmission_acknowledge
            else:
                msg_part1 = f"Invalid type '{str(type(transmission_acknowledge))}'"
                msg_part2 = "Expected (TransmissionAcknowledgementRequest, float)"
                raise TypeError(f"transmission_acknowledge: {msg_part1}. {msg_part2}.")


class ModeSwitchSenderComSpec(ProvidePortComSpec):
    """
    Complex type AR:MODE-SWITCH-SENDER-COM-SPEC
    Tag variants: 'MODE-SWITCH-SENDER-COM-SPEC'
    """

    def __init__(self,
                 mode_group_ref: str | ModeDeclarationGroupPrototypeRef | None = None,
                 enhanced_mode_api: bool | None = None,
                 mode_switched_ack: ModeSwitchedAckRequest | float | None = None,
                 queue_length: int | None = None
                 ) -> None:
        super().__init__()
        self.mode_group_ref: ModeDeclarationGroupPrototypeRef | None = None  # .ENHANCED-MODE-API
        self.enhanced_mode_api: bool | None = None  # .MODE-GROUP-REF
        self.mode_switched_ack: ModeSwitchedAckRequest | None = None  # .MODE-SWITCHED-ACK
        self.queue_length = None  # .QUEUE-LENGTH
        self._assign_optional("mode_group_ref", mode_group_ref, ModeDeclarationGroupPrototypeRef)
        self._assign_optional("enhanced_mode_api", enhanced_mode_api, bool)
        if mode_switched_ack is not None:
            if isinstance(mode_switched_ack, (int, float)):
                self.mode_switched_ack = ModeSwitchedAckRequest(mode_switched_ack)
            elif isinstance(mode_switched_ack, ModeSwitchedAckRequest):
                self.mode_switched_ack = mode_switched_ack
            else:
                msg = f"Invalid type. Expected (ModeSwitchedAckRequest, str), got '{str(type(mode_switched_ack))}'"
                raise TypeError("mode_switched_ack: " + msg)
        self._assign_optional_positive_int("queue_length", queue_length)


class QueuedSenderComSpec(SenderComSpec):
    """
    Complex type AR:QUEUED-SENDER-COM-SPEC
    Tag variants: 'QUEUED-SENDER-COM-SPEC'

    Doesn't need its own constuctor, we can use the one defined by base class
    """


class NonqueuedSenderComSpec(SenderComSpec):
    """
    Complex type AR:NONQUEUED-SENDER-COM-SPEC
    Tag variants: 'NONQUEUED-SENDER-COM-SPEC'
    """

    def __init__(self,
                 init_value: ValueSpecificationElement | None = None,
                 data_filter: DataFilter | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.data_filter: DataFilter | None = None  # .DATA-FILTER
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self._assign_optional_strict("data_filter", data_filter, DataFilter)
        self._assign_optional_strict("init_value", init_value, ValueSpecification)


class NvProvideComSpec(ProvidePortComSpec):
    """
    Complex type AR:NV-PROVIDE-COM-SPEC
    Tag variants: 'NV-PROVIDE-COM-SPEC'
    """

    def __init__(self,
                 variable_ref: VariableDataPrototypeRef | None = None,
                 ram_block_init_value: ValueSpecificationElement | None = None,
                 rom_block_init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.ram_block_init_value: ValueSpecificationElement | None = None  # .RAM-BLOCK-INIT-VALUE
        self.rom_block_init_value: ValueSpecificationElement | None = None  # .RAM-BLOCK-INIT-VALUE
        self.variable_ref: VariableDataPrototypeRef | None = None         # .VARIABLE-REF
        self._assign_optional_strict("ram_block_init_value", ram_block_init_value, ValueSpecification)
        self._assign_optional_strict("rom_block_init_value", rom_block_init_value, ValueSpecification)
        self._assign_optional("variable_ref", variable_ref, VariableDataPrototypeRef)


class ParameterProvideComSpec(ProvidePortComSpec):
    """
    Complex type AR:PARAMETER-PROVIDE-COM-SPEC
    Tag variants: 'PARAMETER-PROVIDE-COM-SPEC'
    """

    def __init__(self,
                 parameter_ref: ParameterDataPrototypeRef | str | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.parameter_ref: VariableDataPrototypeRef | None = None  # .PARAMETER-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("parameter_ref", parameter_ref, ParameterDataPrototypeRef)


EndToEndTransformationComSpecPropsArgTypes = Union[EndToEndTransformationComSpecProps,
                                                   list[EndToEndTransformationComSpecProps]]


class ServerComSpec(ProvidePortComSpec):
    """
    Complex type AR:SERVER-COM-SPEC
    Tag variants: 'SERVER-COM-SPEC'
    """

    def __init__(self,
                 operation_ref: ClientServerOperationRef | None = None,
                 queue_length: int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None
                 ) -> None:
        super().__init__()
        # .GETTER-REF not supported (Adaptive Platform)
        self.operation_ref: ClientServerOperationRef | None = None  # .OPERATION-REF
        self.queue_length: int | None = None  # .QUEUE-LENGTH
        # .SETTER-REF not supported (Adaptive Platform)
        # .TRANSFORMATION-COM-SPEC-PROPSS
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        # USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet supported under transformation_com_spec_props
        self._assign_optional("operation_ref", operation_ref, ClientServerOperationRef)
        self._assign_optional_positive_int("queue_length", queue_length)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(props)
        else:
            raise TypeError("props must be of type EndToEndTransformationComSpecProps")


class ReceptionComSpecProps(ARObject):
    """
    Complex type AR:RECEPTION-COM-SPEC-PROPS
    Tag variants: 'RECEPTION-PROPS'
    """

    def __init__(self,
                 data_update_period: float | None = None,
                 timeout: float | None = None,
                 ) -> None:
        super().__init__()
        self.data_update_period: float | None = None  # .DATA-UPDATE-PERIOD
        self.timeout: float | None = None  # .TIMEOUT
        self._assign_optional("data_update_period", data_update_period, float)
        self._assign_optional("timeout", timeout, float)


class RequirePortComSpec(ARObject):
    """
    Group AR:R-PORT-COM-SPEC
    """

    @classmethod
    def make_from_port_interface(cls, port_interface: PortInterface, **kwargs) -> "RequirePortComSpec":
        """
        Convenience method for creating R-PORT com-specs

        For SenderReceiverInterface:
        If interface has a single element: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple elements: kwargs is a dict of dict where
                                            outer dict keys are element names and each value
                                            is another dict containing key-value pairs for one com-spec

        For ClientServerInterface:
        If interface has a single operation: kwargs is a dict with key-value pairs for one com-spec
        If interface has multiple operations: kwargs is a dict of dict where
                                              outer dict keys are operation names and each value
                                              is another dict containing key-value pairs for one com-spec
        """
        if isinstance(port_interface, SenderReceiverInterface):
            if len(port_interface.data_elements) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one element")
            if len(port_interface.data_elements) == 1:
                data_element: VariableDataPrototype = port_interface.data_elements[0]
                if data_element.is_queued:
                    return QueuedReceiverComSpec(data_element_ref=data_element.ref(), **kwargs)
                else:
                    return cls.make_non_queued_receiver_com_spec(data_element_ref=data_element.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for element_name, value in kwargs.items():
                    unprocessed.add(element_name)
                    if not isinstance(value, dict):
                        msg = f"{port_interface.name}.{element_name}: Expected dict type, got {str(type(value))}"
                        raise TypeError(msg)
                for data_element in port_interface.data_elements:
                    if data_element.name in unprocessed:
                        unprocessed.remove(data_element.name)
                        com_spec_args = kwargs[data_element.name]
                        if data_element.is_queued:
                            com_spec = QueuedSenderComSpec(data_element_ref=data_element.ref(),
                                                           **com_spec_args)
                        else:
                            com_spec = cls.make_non_queued_receiver_com_spec(data_element_ref=data_element.ref(),
                                                                             **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    element_names = ', '.join(list[unprocessed])
                    msg = f"{port_interface.name}: Data element(s) not found in port interface: '{element_names}'"
                    raise ValueError(msg)
                return com_spec_list
        if isinstance(port_interface, ClientServerInterface):
            if len(port_interface.operations) == 0:
                raise ValueError(f"{port_interface.name}: Port interface must have at least one operation")
            if len(port_interface.operations) == 1:
                operation = port_interface.operations[0]
                return ClientComSpec(operation_ref=operation.ref(), **kwargs)
            else:
                com_spec_list = []
                unprocessed = set()
                for operation_name in kwargs:
                    unprocessed.add(operation_name)
                for operation in port_interface.operations:
                    if operation.name in unprocessed:
                        unprocessed.remove(operation.name)
                        com_spec_args = kwargs[operation.name]
                        com_spec = ClientComSpec(operation_ref=operation.ref(), **com_spec_args)
                        com_spec_list.append(com_spec)
                if len(unprocessed) > 0:
                    operations = ', '.join(list[unprocessed])
                    raise ValueError(f"{port_interface.name}: Operation(s) not found in port interface: '{operations}'")
                return com_spec_list
        else:
            raise NotImplementedError(str(type(port_interface)))

    @classmethod
    def make_non_queued_receiver_com_spec(cls,
                                          init_value: InitValueArgType | None = None,
                                          **kwargs
                                          ) -> "NonqueuedReceiverComSpec":
        """
        Convenience method for creating NonqueuedReceiverComSpec
        """
        init_value = ValueSpecification.make_value_with_check(init_value)
        return NonqueuedReceiverComSpec(init_value=init_value, **kwargs)


class ReceiverComSpec(RequirePortComSpec):
    """
    Group AR:RECEIVER-COM-SPEC
    """

    def __init__(self,
                 data_element_ref: AutosarDataPrototypeRef | VariableDataPrototypeRef | None = None,
                 handle_out_of_range: ar_enum.HandleOutOfRange | None = None,
                 handle_out_of_range_status: ar_enum.HandleOutOfRangeStatus | None = None,
                 max_delta_counter_init: int | None = None,
                 max_no_new_repeated_data: int | None = None,
                 network_representation: SwDataDefProps | None = None,
                 reception_props: ReceptionComSpecProps | None = None,
                 replace_with: Union["VariableAccess", None] = None,
                 sync_counter_init: int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None,
                 uses_end_to_end_protection: bool | None = None
                 ) -> None:
        super().__init__()
        # .COMPOSITE-NETWORK-REPRESENTATIONS not supported
        self.data_element_ref: AutosarDataPrototypeRef | None = None  # .DATA-ELEMENT-REF
        # .DATA-UPDATE-PERIOD not supported (Status Removed)
        # .EXTERNAL-REPLACEMENT-REF not supported (Status Removed)
        self.handle_out_of_range: ar_enum.HandleOutOfRange | None = None  # .HANDLE-OUT-OF-RANGE
        self.handle_out_of_range_status: ar_enum.HandleOutOfRangeStatus | None = None  # .HANDLE-OUT-OF-RANGE-STATUS
        self.max_delta_counter_init: int | None = None   # .MAX-DELTA-COUNTER-INIT
        self.max_no_new_repeated_data: int | None = None   # .MAX-NO-NEW-OR-REPEATED-DATA
        self.network_representation: SwDataDefProps | None = None  # .NETWORK-REPRESENTATION
        # .RECEIVER-INTENT not supported (adaptive platform)
        self.reception_props: ReceptionComSpecProps | None = None  # .RECEPTION-PROPS
        self.replace_with: VariableAccess | None = None  # .REPLACE-WITH
        self.sync_counter_init: int | None = None   # .SYNC-COUNTER-INIT
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        self.uses_end_to_end_protection: bool | None = None  # .USES-END-TO-END-PROTECTION
        if data_element_ref is not None:
            if isinstance(data_element_ref, AutosarDataPrototypeRef):
                self.data_element_ref = data_element_ref
            elif isinstance(data_element_ref, VariableDataPrototypeRef):
                self.data_element_ref = AutosarDataPrototypeRef(data_element_ref.value,
                                                                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE)
            else:
                raise ar_except.AssignmentTypeError("data_element_ref",
                                                    ("AutosarDataPrototypeRef", "VariableDataPrototypeRef"),
                                                    data_element_ref)

        self._assign_optional("handle_out_of_range", handle_out_of_range, ar_enum.HandleOutOfRange)
        self._assign_optional("handle_out_of_range_status", handle_out_of_range_status, ar_enum.HandleOutOfRangeStatus)
        self._assign_optional_positive_int("max_delta_counter_init", max_delta_counter_init)
        self._assign_optional_positive_int("max_no_new_repeated_data", max_no_new_repeated_data)
        self._assign_optional_strict("network_representation", network_representation, SwDataDefProps)
        self._assign_optional_strict("reception_props", reception_props, ReceptionComSpecProps)
        self._assign_optional_strict("replace_with", replace_with, VariableAccess)
        self._assign_optional_positive_int("sync_counter_init", sync_counter_init)
        self._assign_optional("uses_end_to_end_protection", uses_end_to_end_protection, bool)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, com_spec_props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(com_spec_props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(com_spec_props)
        else:
            raise TypeError("com_spec_props must be of type EndToEndTransformationComSpecProps")


class QueuedReceiverComSpec(ReceiverComSpec):
    """
    Complex type AR:QUEUED-RECEIVER-COM-SPEC
    Tag variants: 'QUEUED-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 queue_length: int | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.queue_length: int | None = None  # .QUEUE-LENGTH
        self._assign_optional_positive_int("queue_length", queue_length)


class NonqueuedReceiverComSpec(ReceiverComSpec):
    """
    Complex type AR:NONQUEUED-RECEIVER-COM-SPEC
    Tag variants: 'NONQUEUED-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 alive_timeout: int | float | None = None,
                 enable_update: bool | None = None,
                 data_filter: DataFilter | None = None,
                 handle_data_status: bool | None = None,
                 handle_never_received: bool | None = None,
                 handle_timeout_type: ar_enum.HandleTimeout | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 timeout_substitution_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.alive_timeout: int | float | None = None  # .ALIVE-TIMEOUT
        self.enable_update: bool | None = None  # .ENABLE-UPDATE
        self.data_filter: DataFilter | None = None  # .FILTER
        self.handle_data_status: bool | None = None  # .HANDLE-DATA-STATUS
        self.handle_never_received: bool | None = None  # .HANDLE-NEVER-RECEIVED
        self.handle_timeout_type: ar_enum.HandleTimeout | None = None  # .HANDLE-TIMEOUT-TYPE
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.timeout_substitution_value: ValueSpecificationElement | None = None  # .TIMEOUT-SUBSTITUTION-VALUE
        self._assign_optional("alive_timeout", alive_timeout, float)
        self._assign_optional("enable_update", enable_update, bool)
        self._assign_optional_strict("data_filter", data_filter, DataFilter)
        self._assign_optional("handle_data_status", handle_data_status, bool)
        self._assign_optional("handle_never_received", handle_never_received, bool)
        self._assign_optional("handle_timeout_type", handle_timeout_type, ar_enum.HandleTimeout)
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional_strict("timeout_substitution_value", timeout_substitution_value, ValueSpecification)


class NvRequireComSpec(RequirePortComSpec):
    """
    Complex type AR:NV-REQUIRE-COM-SPEC
    Tag variants: 'NV-REQUIRE-COM-SPEC'
    """

    def __init__(self,
                 variable_ref: VariableDataPrototypeRef | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.variable_ref: VariableDataPrototypeRef | None = None  # .VARIABLE-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("variable_ref", variable_ref, VariableDataPrototypeRef)


class ParameterRequireComSpec(RequirePortComSpec):
    """
    Complex type AR:PARAMETER-REQUIRE-COM-SPEC
    Tag variants: 'PARAMETER-REQUIRE-COM-SPEC'
    """

    def __init__(self,
                 parameter_ref: ParameterDataPrototypeRef | str | None = None,
                 init_value: ValueSpecificationElement | None = None,
                 ) -> None:
        super().__init__()
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        self.parameter_ref: VariableDataPrototypeRef | None = None  # .PARAMETER-REF
        self._assign_optional_strict("init_value", init_value, ValueSpecification)
        self._assign_optional("parameter_ref", parameter_ref, ParameterDataPrototypeRef)


class ModeSwitchReceiverComSpec(RequirePortComSpec):
    """
    Complex type AR:MODE-SWITCH-RECEIVER-COM-SPEC
    Tag variants: 'MODE-SWITCH-RECEIVER-COM-SPEC'
    """

    def __init__(self,
                 mode_group_ref: str | ModeDeclarationGroupPrototypeRef | None = None,
                 enhanced_mode_api: bool | None = None,
                 supports_async: bool | None = None,
                 ) -> None:
        super().__init__()
        self.mode_group_ref: ModeDeclarationGroupPrototypeRef | None = None  # .ENHANCED-MODE-API
        self.enhanced_mode_api: bool | None = None  # .MODE-GROUP-REF
        self.supports_async: bool | None = None  # .SUPPORTS-ASYNCHRONOUS-MODE-SWITCH
        self._assign_optional("mode_group_ref", mode_group_ref, ModeDeclarationGroupPrototypeRef)
        self._assign_optional("enhanced_mode_api", enhanced_mode_api, bool)
        self._assign_optional("supports_async", supports_async, bool)


class ClientComSpec(RequirePortComSpec):
    """
    Complex type AR:CLIENT-COM-SPEC
    Tag variants: 'CLIENT-COM-SPEC'
    """

    def __init__(self,
                 operation_ref: ClientServerOperationRef | None = None,
                 e2e_call_respone_timeout: float | int | None = None,
                 transformation_com_spec_props: EndToEndTransformationComSpecPropsArgTypes | None = None
                 ) -> None:
        super().__init__()
        # .CLIENT-INTENT not supported (Adaptive Platform)
        # .GETTER-REF not supported (Adaptive Platform)
        self.operation_ref: ClientServerOperationRef | None = None  # .OPERATION-REF
        self.e2e_call_respone_timeout: float | None = None  # .END-TO-END-CALL-RESPONSE-TIMEOUT
        # .SETTER-REF not supported (Adaptive Platform)
        # .TRANSFORMATION-COM-SPEC-PROPSS
        self.transformation_com_spec_props: list[EndToEndTransformationComSpecProps] = []
        # USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet supported under transformation_com_spec_props
        self._assign_optional("operation_ref", operation_ref, ClientServerOperationRef)
        self._assign_optional("e2e_call_respone_timeout", e2e_call_respone_timeout, float)
        if transformation_com_spec_props is not None:
            if isinstance(transformation_com_spec_props, EndToEndTransformationComSpecProps):
                self.append_transformation_com_spec_props(transformation_com_spec_props)
            elif isinstance(transformation_com_spec_props, list):
                for props in transformation_com_spec_props:
                    self.append_transformation_com_spec_props(props)
            else:
                raise ar_except.AssignmentTypeError("transformation_com_spec_props",
                                                    ("EndToEndTransformationComSpecProps",
                                                     "list[EndToEndTransformationComSpecProps]"),
                                                    transformation_com_spec_props)

    def append_transformation_com_spec_props(self, props: EndToEndTransformationComSpecProps) -> None:
        """
        Appends EndToEndTransformationComSpecProps to internal list of transformations

        Elements of type AR:USER-DEFINED-TRANSFORMATION-COM-SPEC-PROPS not yet implemented
        """
        if isinstance(props, EndToEndTransformationComSpecProps):
            self.transformation_com_spec_props.append(props)
        else:
            raise TypeError("props must be of type EndToEndTransformationComSpecProps")


class PortPrototype(Identifiable):
    """
    Group AR:PORT-PROTOTYPE
    """
    # .CLIENT-SERVER-ANNOTATIONS not supported
    # .DELEGATED-PORT-ANNOTATION not supported
    # .IO-HW-ABSTRACTION-SERVER-ANNOTATIONS not supported
    # .MODE-PORT-ANNOTATIONS not supported
    # .NV-DATA-PORT-ANNOTATIONS not supported
    # .PARAMETER-PORT-ANNOTATIONS not supported
    # .PORT-PROTOTYPE-PROPS not supported
    # .SENDER-RECEIVER-ANNOTATIONS not supported
    # .TRIGGER-PORT-ANNOTATIONS not supported
    # .VARIATION-POINT not supported


class ProvidePortPrototype(PortPrototype):
    """
    Complex type AR:P-PORT-PROTOTYPE
    Tag variants: 'P-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.com_spec: list[ProvidePortComSpec] = []  # .PROVIDED-COM-SPECS
        self.port_interface_ref: PortInterfaceRef | None = None  # .PROVIDED-INTERFACE-TREF
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        if com_spec is not None:
            if isinstance(com_spec, ProvidePortComSpec):
                self.append_com_spec(com_spec)
            elif isinstance(com_spec, (list, tuple)):
                for com_spec_elem in com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("com_spec must be of a type derived from ProvidePortComSpec")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: ProvidePortComSpec) -> None:
        """
        Adds comspec to internal list of com-specs
        """
        if isinstance(com_spec, ProvidePortComSpec):
            self.com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of a type derived from ProvidePortComSpec")


class RequirePortPrototype(PortPrototype):
    """
    Complex type AR:R-PORT-PROTOTYPE
    Tag variants: 'R-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                 allow_unconnected: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.com_spec: list[RequirePortComSpec] = []  # .REQUIRED-COM-SPECS
        self.allow_unconnected: bool | None = None  # .MAY-BE-UNCONNECTED
        self.port_interface_ref: PortInterfaceRef | None = None  # .REQUIRED-INTERFACE-TREF
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        self._assign_optional("allow_unconnected", allow_unconnected, bool)
        if com_spec is not None:
            if isinstance(com_spec, RequirePortComSpec):
                self.append_com_spec(com_spec)
            elif isinstance(com_spec, (list, tuple)):
                for com_spec_elem in com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                msg = "com_spec: Needs be of a type derived from RequirePortComSpec."
                raise TypeError(msg + f" Got {str(type(com_spec))}")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: RequirePortComSpec) -> None:
        """
        Adds comspec to internal list of com-specs
        """
        if isinstance(com_spec, RequirePortComSpec):
            self.com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of type RequirePortComSpec")


class PRPortPrototype(PortPrototype):
    """
    Complex type AR:PR-PORT-PROTOTYPE
    Tag variants: 'PR-PORT-PROTOTYPE'

    Includes AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE and AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE
    """

    def __init__(self,
                 name: str,
                 port_interface_ref: PortInterfaceRef | None = None,
                 provided_com_spec: ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                 required_com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.port_interface_ref: PortInterfaceRef | None = None
        self.provided_com_spec: list[ProvidePortComSpec] = []
        self.required_com_spec: list[RequirePortComSpec] = []
        self._assign_optional_strict("port_interface_ref", port_interface_ref, PortInterfaceRef)
        if provided_com_spec is not None:
            if isinstance(provided_com_spec, ProvidePortComSpec):
                self.append_com_spec(provided_com_spec)
            elif isinstance(required_com_spec, (list, tuple)):
                for com_spec_elem in provided_com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("provided_com_spec must be of a type derived from ProvidePortComSpec")
        if required_com_spec is not None:
            if isinstance(required_com_spec, RequirePortComSpec):
                self.append_com_spec(required_com_spec)
            elif isinstance(required_com_spec, (list, tuple)):
                for com_spec_elem in required_com_spec:
                    self.append_com_spec(com_spec_elem)
            else:
                raise TypeError("required_com_spec must be of a type derived from RequirePortComSpec")

    def ref(self) -> PortPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return PortPrototypeRef(ref_str, ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE)

    def append_com_spec(self, com_spec: ProvidePortComSpec | RequirePortComSpec) -> None:
        """
        Append com-spec to internal list(s) of com-specs
        """
        if isinstance(com_spec, ProvidePortComSpec):
            self.provided_com_spec.append(com_spec)
        elif isinstance(com_spec, RequirePortComSpec):
            self.required_com_spec.append(com_spec)
        else:
            raise TypeError("com_spec must be of either type ProvidePortComSpec, RequirePortComSpec")


class SwComponentType(ARElement, Searchable):
    """
    Group AR:SW-COMPONENT-TYPE
    """

    def __init__(self,
                 name: str,
                 ports: PortPrototypeElement | list[PortPrototypeElement] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .SW-COMPONENT-DOCUMENTATIONS not supported
        # .CONSISTENCY-NEEDSS not supported
        self.ports: list[PortPrototypeElement] = []  # .PORTS
        # .PORT_GROUPS not yet supported
        # .SWC-MAPPING-CONSTRAINT-REFS not yet supported
        # .UNIT-GROUP-REFS not yet supported
        if ports is not None:
            if isinstance(ports, PortPrototype):
                self.append_port(ports)
            elif isinstance(ports, list):
                for port in ports:
                    self.append_port(port)
            else:
                msg_part_1 = "ports: Type must be ProvidePortPrototype, RequirePortPrototype, PRPortPrototype"
                msg_part_2 = " or a list of those types."
                raise TypeError(msg_part_1 + msg_part_2 + f" Got {str(type(ports))}")

    def append_port(self, port: PortPrototypeElement):
        """
        Adds port to internal list of ports
        """
        if isinstance(port, PortPrototype):
            port.parent = self
            self.ports.append(port)
        else:
            msg = "port type must be one of: ProvidePortPrototype, RequirePortPrototype, PRPortPrototype."
            raise TypeError(msg + f" Got {str(type(port))}")

    @property
    def provide_ports(self) -> Iterator[ProvidePortPrototype]:
        """
        P-PORTS
        """
        for port in self.ports:
            if isinstance(port, ProvidePortPrototype):
                yield port

    @property
    def require_ports(self) -> Iterator[RequirePortPrototype]:
        """
        R-PORTS
        """
        for port in self.ports:
            if isinstance(port, RequirePortPrototype):
                yield port

    @property
    def pr_ports(self) -> Iterator[PRPortPrototype]:
        """
        PR-PORTS
        """
        for port in self.ports:
            if isinstance(port, PRPortPrototype):
                yield port

    def find(self, ref: str) -> Identifiable | None:
        """
        Searches port names for a match in ref
        """
        parts = ref.partition('/')
        for elem in self.ports:
            if elem.name == parts[0]:
                return elem
        return None

    @convenience_method
    def create_provide_port(self,
                            name: str,
                            port_interface: PortInterface | None = None,
                            com_spec: dict | list[dict] | ProvidePortComSpec | list[ProvidePortComSpec] | None = None,
                            **kwargs) -> ProvidePortPrototype:
        """
        Creates a new provide port and adds it to the internal list of ports
        """
        if com_spec is not None:
            if isinstance(com_spec, dict):
                com_spec = ProvidePortComSpec.make_from_port_interface(port_interface, **com_spec)
                assert com_spec is not None
        port = ProvidePortPrototype(name, port_interface.ref(), com_spec, **kwargs)
        self.append_port(port)
        return port

    @convenience_method
    def create_require_port(self,
                            name: str,
                            port_interface: PortInterface,
                            com_spec: dict | list[dict] | RequirePortComSpec | list[RequirePortComSpec] | None = None,
                            allow_unconnected: bool | None = None,
                            **kwargs) -> RequirePortPrototype:
        """
        Creates a new require port and adds it to the internal list of ports
        """
        if com_spec is not None:
            if isinstance(com_spec, dict):
                com_spec = RequirePortComSpec.make_from_port_interface(port_interface, **com_spec)
                assert com_spec is not None
        port = RequirePortPrototype(name, port_interface.ref(), com_spec, allow_unconnected, **kwargs)
        self.append_port(port)
        return port

    @convenience_method
    def create_pr_port(self,
                       name: str,
                       port_interface_ref: PortInterfaceRef | None = None,
                       com_spec: RequirePortComSpec | list[RequirePortComSpec] | None = None,
                       **kwargs) -> PRPortPrototype:
        """
        Creates a new pr-port and adds it to the internal list of ports
        """
        port = PRPortPrototype(name, port_interface_ref, com_spec, **kwargs)
        self.append_port(port)
        return port


class AtomicSoftwareComponentType(SwComponentType):
    """
    Group AR:ATOMIC-SW-COMPONENT-TYPE
    """

    def __init__(self,
                 name: str,
                 internal_behavior: Union["SwcInternalBehavior", None] = None,
                 symbol_props: SymbolProps | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.internal_behavior: SwcInternalBehavior | None = None
        self.symbol_props = None  # AR:SYMBOL-PROPS
        self._assign_optional_strict("internal_behavior", internal_behavior, SwcInternalBehavior)
        self._assign_optional_strict("symbol_props", symbol_props, SymbolProps)


class ApplicationSoftwareComponentType(AtomicSoftwareComponentType):
    """
    Complex type AR:APPLICATION-SW-COMPONENT-TYPE
    Tag variants: 'APPLICATION-SW-COMPONENT-TYPE'

    Same constructor as parent class
    """

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE)


class SwComponentPrototype(Identifiable):
    """
    Complex type AR:SW-COMPONENT-PROTOTYPE
    Tag variants: 'SW-COMPONENT-PROTOTYPE'
    """

    def __init__(self,
                 name: str,
                 type_ref: SwComponentTypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: SwComponentTypeRef | None = None
        self._assign_optional_strict("type_ref", type_ref, SwComponentTypeRef)

    def ref(self) -> SwComponentPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else SwComponentPrototypeRef(ref_str)


class PortInCompositionTypeInstanceRef(ARObject):
    """
    Merge of complex types AR:P-PORT-IN-COMPOSITION-INSTANCE-REF
    and R-PORT-IN-COMPOSITION-INSTANCE-REF
    Tag variants: 'PROVIDER-IREF' | 'P-PORT-IN-COMPOSITION-INSTANCE-REF' |
                  'REQUESTER-IREF'| 'R-PORT-IN-COMPOSITION-INSTANCE-REF'
    """

    def __init__(self,
                 component_ref: SwComponentPrototypeRef | None = None,
                 port_ref: PortPrototypeRef | None = None,
                 ) -> None:
        super().__init__()
        self.component_ref: SwComponentPrototypeRef | None = None  # .CONTEXT-COMPONENT-REF
        self.port_ref: PortPrototypeRef | None = None  # .TARGET-P-PORT-REF or .TARGET-R-PORT-REF
        self._assign_optional_strict("component_ref", component_ref, SwComponentPrototypeRef)
        self._assign_optional_strict("port_ref", port_ref, PortPrototypeRef)


class SwConnector(Identifiable):
    """
    Group AR:SW-CONNECTOR
    """

    def __init__(self,
                 name: str,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MAPPING-REF not yet supported
        # .VARIATION-POINT not supported


class AssemblySwConnector(SwConnector):
    """
    Complex type AR:ASSEMBLY-SW-CONNECTOR
    Tag variants: 'ASSEMBLY-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 provide_port: PortInCompositionTypeInstanceRef | None = None,
                 require_port: PortInCompositionTypeInstanceRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.provide_port: PortInCompositionTypeInstanceRef | None = None  # .PROVIDER-IREF
        self.require_port: PortInCompositionTypeInstanceRef | None = None  # .REQUESTER-IREF
        self._assign_optional_strict("provide_port", provide_port, PortInCompositionTypeInstanceRef)
        self._assign_optional_strict("require_port", require_port, PortInCompositionTypeInstanceRef)


class DelegationSwConnector(SwConnector):
    """
    Complex type AR:DELEGATION-SW-CONNECTOR
    Tag variants: 'DELEGATION-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 inner_port: PortInCompositionTypeInstanceRef | None = None,
                 outer_port: PortPrototypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.inner_port: PortInCompositionTypeInstanceRef | None = None  # .INNER-PORT-IREF
        self.outer_port: PortPrototypeRef | None = None  # .OUTER-PORT-REF"
        self._assign_optional_strict("inner_port", inner_port, PortInCompositionTypeInstanceRef)
        self._assign_optional_strict("outer_port", outer_port, PortPrototypeRef)

    @property
    def xml_tag(self) -> str | None:
        """
        Returns a suitable XML-tag for inner_port_ref based on port reference type.
        Raises exception is port reference isn't set or if port-reference contains invalid value
        """
        if self.inner_port.port_ref is not None:
            if self.inner_port.port_ref.is_provide_port_ref:
                return "P-PORT-IN-COMPOSITION-INSTANCE-REF"
            if self.inner_port.port_ref.is_require_port_ref:
                return "R-PORT-IN-COMPOSITION-INSTANCE-REF"
        return None


class PassThroughSwConnector(SwConnector):
    """
    Complex type AR:PASS-THROUGH-SW-CONNECTOR
    Tag variants: 'PASS-THROUGH-SW-CONNECTOR'
    """

    def __init__(self,
                 name: str,
                 provide_port: PortPrototypeRef | None = None,
                 require_port: PortPrototypeRef | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.provide_port: PortPrototypeRef | None = None  # .PROVIDED-OUTER-PORT-REF
        self.require_port: PortPrototypeRef | None = None  # .REQUIRED-OUTER-PORT-REF
        # .SERVICE-INTERFACE-ELEMENT-MAPPING-REFS not yet supported
        self._assign_optional_strict("provide_port", provide_port, PortPrototypeRef)
        self._assign_optional_strict("require_port", require_port, PortPrototypeRef)


class CompositionSwComponentType(SwComponentType, Searchable):
    """
    Complex type AR:COMPOSITION-SW-COMPONENT-TYPE
    Tag variants: 'COMPOSITION-SW-COMPONENT-TYPE'
    """

    def __init__(self,
                 name: str,
                 components: SwComponentPrototype | list[SwComponentPrototype] | None = None,
                 connectors: SwConnectorElement | list[SwConnectorElement] = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.components: list[SwComponentPrototype] = []  # .COMPONENTS
        self.connectors: list[SwConnectorElement] = []  # .CONNECTORS
        # .CONSTANT-VALUE-MAPPING-REFS not yet supported
        # .DATA-TYPE-MAPPING-REFS not yet supported
        # .INSTANTIATION-RTE-EVENT-PROPSS not yet supported
        if components is not None:
            if isinstance(components, SwComponentPrototype):
                self.append_component(components)
            elif isinstance(components, list):
                for component in components:
                    self.append_component(component)
            else:
                raise TypeError(f"components: Invalid type '{str(type(components))}'")
        if connectors is not None:
            if isinstance(connectors, (AssemblySwConnector, DelegationSwConnector, PassThroughSwConnector)):
                self.append_connector(connectors)
            elif isinstance(connectors, list):
                for connector in connectors:
                    self.append_connector(connector)
            else:
                raise TypeError(f"components: Invalid type '{str(type(connectors))}'")

    def ref(self) -> SwComponentTypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return SwComponentTypeRef(ref_str, ar_enum.IdentifiableSubTypes.COMPOSITION_SW_COMPONENT_TYPE)

    def append_component(self, component: SwComponentPrototype) -> None:
        """
        Appends components prototype to internal list
        """
        if isinstance(component, SwComponentPrototype):
            component.parent = self
            self.components.append(component)
        else:
            raise TypeError(f"component: Invalid type {(str(type(component)))}")

    def append_connector(self, connector: SwConnectorElement) -> None:
        """
        Appends components prototype to internal list
        """
        if isinstance(connector, (AssemblySwConnector, DelegationSwConnector, PassThroughSwConnector)):
            connector.parent = self
            self.connectors.append(connector)
        else:
            raise TypeError(f"connector: Invalid type {(str(type(connector)))}")

    def find(self, ref: str) -> Identifiable | None:
        """
        Searches components and connectors for a match in ref
        """
        parts = ref.partition('/')
        for elem in self.components:
            if elem.name == parts[0]:
                return elem
        for elem in self.connectors:
            if elem.name == parts[0]:
                return elem
        return super().find(ref)

    @convenience_method
    def create_component_prototype(self,
                                   component_type: SwComponentType,
                                   name: str = None,
                                   **kwargs) -> SwComponentPrototype:
        """
        Creates a new SwComponentPrototype object from the source SwComponentType and adds it
        to the internal list of components.
        By default the created SwComponentPrototype will have the same name as the source
        SwComponentType. The optional name argument can be used to give it a different name.
        """
        if name is None:
            name = component_type.name
        component_prototype = SwComponentPrototype(name, component_type.ref(), **kwargs)
        self.append_component(component_prototype)
        return component_prototype

    @convenience_method
    def create_connector(self,
                         port_ref1: str,
                         port_ref2: str,
                         workspace: Searchable) -> None:
        """
        Creates a connector between two ports in the composition
        port_ref1 and port_ref2 can be of any of these formats:
        * 'component_name/port_name' - references a port of an inner component
        * 'port_name' - references a port in the composition itself

        Depending on the combination of ports this function automatically determines
        the type of connector to create which can be one of:
        * AssemblySwConnector
        * DelegationSwConnector
        * PassThroughSwConnector
        """
        assert workspace is not None
        port1, component1 = self._analyze_port_ref(workspace, port_ref1)
        port2, component2 = self._analyze_port_ref(workspace, port_ref2)

        if component1 is None and component2 is None:
            return self._create_pass_through_connector(port1, port2)
        elif component1 is None:
            return self._create_delegation_connector(component2, port2, port1)
        elif component2 is None:
            return self._create_delegation_connector(component1, port1, port2)
        else:
            requester_component: SwComponentPrototype = None
            provider_component: SwComponentPrototype = None
            provide_port: PortPrototype = None
            require_port: PortPrototype = None
            if isinstance(port1, RequirePortPrototype) and isinstance(port2, ProvidePortPrototype):
                requester_component, provider_component = component1, component2
                require_port, provide_port = port1, port2
            elif isinstance(port1, ProvidePortPrototype) and isinstance(port2, RequirePortPrototype):
                requester_component, provider_component = component2, component1
                require_port, provide_port = port2, port1
            elif isinstance(port1, RequirePortPrototype) and isinstance(port2, RequirePortPrototype):
                raise ValueError('cannot create assembly connector between two require-ports')
            else:
                raise ValueError('cannot create assembly connector between two provide-ports')
            return self._create_assembly_connector(provider_component, provide_port,
                                                   requester_component, require_port)

    def _analyze_port_ref(self,
                          workspace: Searchable,
                          port_ref: str) -> tuple[PortPrototype, Union[SwComponentPrototype, None]]:
        """
        Analyze port reference string and attempts to determine what component
        and port are referenced.
        """
        port: PortPrototype | None = None
        port_name: str | None = None
        parts = split_ref(port_ref)
        if len(parts) > 1:
            if len(parts) == 2:  # Format is 'component_name/port_name'?
                port_name = parts[1]
                for elem in self.components:
                    if elem.name == parts[0]:
                        component = workspace.find(str(elem.type_ref))
                        if component is None:
                            raise ValueError(f"Invalid reference: {elem.type_ref}")
                        if not isinstance(component, SwComponentType):
                            msg = f"Reference is not a valid SwComponentType: {elem.type_ref}"
                            raise ValueError(msg)
                        port = component.find(port_name)
                        if (port is None) or (not isinstance(port, PortPrototype)):
                            msg = f"Component '{component.name}' does not seem to have a port with name '{port_name}'"
                            raise ValueError(msg)
                        return port, elem
            else:
                raise ValueError(f"Invalid format: '{port_ref}'")
        else:  # Format is 'port_name'
            # Leaving component as None here is a reminder to the caller to create a delegation or a
            # pass-through connector
            port_name = parts[0]
            port = self.find(port_name)
            if (port is None) or (not isinstance(port, PortPrototype)):
                msg = f"Component '{self.name}' does not seem to have a port with name '{port_name}'"
                raise ValueError(msg)
        return port, None

    def _create_assembly_connector(self,
                                   provider_component: SwComponentPrototype,
                                   provide_port: PortPrototype,
                                   requester_component: SwComponentPrototype,
                                   require_port: PortPrototype) -> AssemblySwConnector:
        """
        Internal helper function for creating assembly connector
        """
        connector_name = '_'.join([provider_component.name,
                                   provide_port.name,
                                   requester_component.name,
                                   require_port.name])
        provider_iref = PortInCompositionTypeInstanceRef(provider_component.ref(), provide_port.ref())
        requester_iref = PortInCompositionTypeInstanceRef(requester_component.ref(), require_port.ref())
        connector = AssemblySwConnector(connector_name, provider_iref, requester_iref)
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.append_connector(connector)
        return connector

    def _create_delegation_connector(self,
                                     inner_component: SwComponentPrototype,
                                     inner_port: PortPrototype,
                                     outer_port: PortPrototype) -> DelegationSwConnector:
        if isinstance(outer_port, ProvidePortPrototype):
            connector_name = '_'.join([inner_component.name, inner_port.name, outer_port.name])
        else:
            connector_name = '_'.join([outer_port.name, inner_component.name, inner_port.name])
        inner_port_iref = PortInCompositionTypeInstanceRef(inner_component.ref(), inner_port.ref())
        connector = DelegationSwConnector(connector_name, inner_port_iref, outer_port.ref())
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.connectors.append(connector)
        return connector

    def _create_pass_through_connector(self,
                                       provide_port: ProvidePortPrototype,
                                       require_port: RequirePortPrototype) -> PassThroughSwConnector:
        connector_name = '_'.join([provide_port.name, require_port.name])
        connector = PassThroughSwConnector(connector_name, provide_port.ref(), require_port.ref())
        if self.find(connector_name) is not None:
            raise ValueError(f"{self.name}: Connector with name '{connector_name}' already exists")
        self.connectors.append(connector)
        return connector

# --- SWC internal behavior elements


class ArVariableInImplementationDataInstanceRef(ARObject):
    """
    Complex type AR:AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
    Tag variants: 'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE' | 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
    """

    ContextDataPrototypeArgType = Union[AbstractImplementationDataTypeElementRef,
                                        list[AbstractImplementationDataTypeElementRef]]

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | None = None,
                 root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None,
                 context_data_prototype_refs: ContextDataPrototypeArgType | None = None,
                 target_data_prototype_ref: AbstractImplementationDataTypeElementRef | None = None
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROOT-VARIABLE-DATA-PROTOTYPE-REF
        self.root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REFS
        self.context_data_prototype_refs: list[AbstractImplementationDataTypeElementRef] = []
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype_ref: AbstractImplementationDataTypeElementRef | None = None

        self._assign_optional_strict("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional_strict("root_variable_data_prototype_ref",
                                     root_variable_data_prototype_ref,
                                     VariableDataPrototypeRef)
        self._assign_optional_strict("target_data_prototype_ref",
                                     target_data_prototype_ref,
                                     AbstractImplementationDataTypeElementRef)
        if context_data_prototype_refs is not None:
            if isinstance(context_data_prototype_refs, AbstractImplementationDataTypeElementRef):
                self.append_context_data_protype_ref(context_data_prototype_refs)
            elif isinstance(context_data_prototype_refs, list):
                for context_data_prototype_ref in context_data_prototype_refs:
                    self.append_context_data_protype_ref(context_data_prototype_ref)

    def append_context_data_protype_ref(self, context_data_prototype_ref: AbstractImplementationDataTypeElementRef):
        """
        Appends datatype reference to internal list of context data type references
        """
        if isinstance(context_data_prototype_ref, AbstractImplementationDataTypeElementRef):
            self.context_data_prototype_refs.append(context_data_prototype_ref)
        else:
            raise TypeError("context_data_prototype_ref must be of type AbstractImplementationDataTypeElementRef")


class VariableInAtomicSWCTypeInstanceRef(ARObject):
    """
    Complex type AR:VARIABLE-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
    Tag variants: 'AUTOSAR-VARIABLE-IREF'
    """

    ContextDataPrototypeArgType = Union[ApplicationCompositeElementDataPrototypeRef,
                                        list[ApplicationCompositeElementDataPrototypeRef]]

    def __init__(self,
                 port_prototype_ref: PortPrototypeRef | None = None,
                 root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None,
                 context_data_prototype_refs: ContextDataPrototypeArgType | None = None,
                 target_data_prototype_ref: DataPrototypeRef | None = None,
                 ) -> None:
        super().__init__()
        # .PORT-PROTOTYPE-REF
        self.port_prototype_ref: PortPrototypeRef | None = None
        # .ROOT-VARIABLE-DATA-PROTOTYPE-REF
        self.root_variable_data_prototype_ref: VariableDataPrototypeRef | None = None
        # .CONTEXT-DATA-PROTOTYPE-REF
        self.context_data_prototype_refs: list[ApplicationCompositeElementDataPrototypeRef] = []
        # .TARGET-DATA-PROTOTYPE-REF
        self.target_data_prototype_ref: DataPrototypeRef | None = None
        self._assign_optional_strict("port_prototype_ref", port_prototype_ref, PortPrototypeRef)
        self._assign_optional_strict("root_variable_data_prototype_ref",
                                     root_variable_data_prototype_ref, VariableDataPrototypeRef)
        self._assign_optional_strict("target_data_prototype_ref", target_data_prototype_ref, DataPrototypeRef)
        if context_data_prototype_refs is not None:
            if isinstance(context_data_prototype_refs, ApplicationCompositeElementDataPrototypeRef):
                self.append_context_data_protype_ref(context_data_prototype_refs)
            elif isinstance(context_data_prototype_refs, list):
                for context_data_prototype_ref in context_data_prototype_refs:
                    self.append_context_data_protype_ref(context_data_prototype_ref)

    def append_context_data_protype_ref(self, context_data_prototype_ref: ApplicationCompositeElementDataPrototypeRef):
        """
        Appends datatype reference to internal list of context data type references
        """
        if isinstance(context_data_prototype_ref, ApplicationCompositeElementDataPrototypeRef):
            self.context_data_prototype_refs.append(context_data_prototype_ref)
        else:
            raise TypeError("context_data_prototype_ref must be of type AbstractImplementationDataTypeElementRef")


class AutosarVariableRef(ARObject):
    """
    Complex type AR:AUTOSAR-VARIABLE-REF
    Tag variants: 'VARIABLE-INSTANCE' | 'NV-RAM-BLOCK-ELEMENT' | 'READ-NV-DATA' |
                  'WRITTEN-NV-DATA' | 'WRITTEN-READ-NV-DATA' | 'USED-DATA-ELEMENT' |
                  'AUTOSAR-VARIABLE' | 'ACCESSED-VARIABLE'
    """

    def __init__(self,
                 ar_variable_in_impl_datatype: ArVariableInImplementationDataInstanceRef | None = None,
                 ar_variable_iref: VariableInAtomicSWCTypeInstanceRef | None = None,
                 local_variable_ref: VariableDataPrototypeRef | None = None
                 ) -> None:
        super().__init__()
        # .AUTOSAR-VARIABLE-IN-IMPL-DATATYPE
        self.ar_variable_in_impl_datatype: ArVariableInImplementationDataInstanceRef | None = None
        # .AUTOSAR-VARIABLE-IREF
        self.ar_variable_iref: VariableInAtomicSWCTypeInstanceRef | None = None
        # .LOCAL-VARIABLE-REF
        self.local_variable_ref: VariableDataPrototypeRef | None = None
        self._assign_optional_strict("ar_variable_in_impl_datatype",
                                     ar_variable_in_impl_datatype,
                                     ArVariableInImplementationDataInstanceRef)
        self._assign_optional_strict("ar_variable_iref",
                                     ar_variable_iref,
                                     VariableInAtomicSWCTypeInstanceRef)
        self._assign_optional_strict("local_variable_ref",
                                     local_variable_ref,
                                     VariableDataPrototypeRef)


class VariableAccess(Identifiable):
    """
    Complex type AR:VARIABLE-ACCESS
    Tag variants: 'REPLACE-WITH' | 'VARIABLE-ACCESS'
    """

    def __init__(self,
                 name: str,
                 accessed_variable: AutosarVariableRef | None = None,
                 scope: ar_enum.VariableAccessScope | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.accessed_variable: AutosarVariableRef | None = None  # .ACCESSED-VARIABLE
        self.scope: ar_enum.VariableAccessScope | None = None  # .SCOPE
        # .VARIATION-POINT not supported
        self._assign_optional_strict("accessed_variable", accessed_variable, AutosarVariableRef)
        self._assign_optional("scope", scope, ar_enum.VariableAccessScope)


class SwcInternalBehavior(Identifiable):
    """
    Complex type AR:SWC-INTERNAL-BEHAVIOR
    Tag variants: 'SWC-INTERNAL-BEHAVIOR'

    This is just a placeholder. Will be implemented later.
    """

    def __init__(self,
                 name: str,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)


class SwcImplementation(Implementation):
    """
    Complex type AR:SWC-IMPLEMENTATION
    Tag variants: 'SWC-IMPLEMENTATION'
    """

    def __init__(self,
                 name: str,
                 behavior_ref: SwcInternalBehaviorRef | None = None,
                 code_descriptors: Code | list[Code] | None = None,
                 required_rte_vendor: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, code_descriptors, **kwargs)
        self.behavior_ref: SwcInternalBehaviorRef | None = None
        # .PER-INSTANCE-MEMORY-SIZES not yet supported
        self.required_rte_vendor: str | None = None
        self._assign_optional("behavior_ref", behavior_ref, SwcInternalBehaviorRef)
        self._assign_optional_strict("required_rte_vendor", required_rte_vendor, str)
