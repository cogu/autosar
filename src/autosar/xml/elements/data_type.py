"""Data type elements."""

from __future__ import annotations

from collections.abc import Iterable
import re
from typing import TYPE_CHECKING, Any, Union

from autosar.xml.base import ARObject
from autosar.xml.elements._base import (
    ARElement,
    Identifiable,
    NumericalValue,
    Referrable,
)
from autosar.xml.elements.documentation import Annotation
import autosar.xml.enumeration as ar_enum
from autosar.xml.reference import (
    AbstractImplementationDataTypeElementRef,
    ApplicationArrayElementRef,
    ApplicationDataTypeRef,
    ApplicationRecordElementRef,
    ArgumentDataPrototypeRef,
    AutosarDataTypeRef,
    CompuMethodRef,
    DataConstraintRef,
    DataTypeMappingSetRef,
    FunctionPtrSignatureRef,
    ImplementationDataTypeRef,
    IndexDataTypeRef,
    ParameterDataPrototypeRef,
    SwAddrMethodRef,
    SwBaseTypeRef,
    UnitRef,
    VariableDataPrototypeRef,
)

if TYPE_CHECKING:
    from autosar.xml.elements.mode_declaration import ModeRequestTypeMap

ValueSpecificationElement = Any


def _get_value_specification_class():
    from autosar.xml.elements.constant import ValueSpecification
    return ValueSpecification


def _get_mode_request_type_map_class():
    from autosar.xml.elements.mode_declaration import ModeRequestTypeMap
    return ModeRequestTypeMap


alignment_type_re = re.compile(
    r"[1-9][0-9]*|0[xX][0-9a-fA-F]*|0[bB][0-1]+|0[0-7]*|UNSPECIFIED|UNKNOWN|BOOLEAN|PTR")

display_format_str_re = re.compile(
    r"%[ \-+#]?[0-9]*(\.[0-9]+)?[diouxXfeEgGcs]")


class BaseType(ARElement):
    """
    Group AR:BASE-TYPE
    Merge of Groups AR:BASE-TYPE, AR:BASE-TYPE-DEFINITION, and AR:BASE-TYPE-DIRECT-DEFINITION
    """

    def __init__(self, name: str, **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        # .BASE-TYPE-SIZE
        self.size: int | None = None
        # .MAX-BASE-TYPE-SIZE --- REMOVED
        # .BASE-TYPE-ENCODING
        self.encoding: str | None = None
        # .MEM-ALIGNMENT
        self.alignment: int | None = None
        # .BYTE-ORDER
        self.byte_order: ar_enum.ByteOrder | None = None
        # .NATIVE-DECLARATION
        self.native_declaration: str | None = None


class SwBaseType(BaseType):
    """
    Complex type AR:SW-BASE-TYPE
    Tag variants: 'SW-BASE-TYPE'
    """

    def __init__(self,
                 name: str,
                 size: int | None = None,
                 encoding: str | None = None,
                 alignment: int | None = None,
                 byte_order: ar_enum.ByteOrder | None = None,
                 native_declaration: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.size = size
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
    Complex type AR:SW-BIT-REPRESENTATION
    Tag variants: 'SW-BIT-REPRESENTATION'
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
    Tag variants: 'SW-TEXT-PROPS'
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
    Tag variants: 'SW-POINTER-TARGET-PROPS'
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
    Complex type AR:SW-DATA-DEF-PROPS-CONDITIONAL
    Merge of Complex type AR:SW-DATA-DEF-PROPS-CONDITIONAL and group AR:SW-DATA-DEF-PROPS-CONTENT
    Tag variants: 'SW-DATA-DEF-PROPS-CONDITIONAL'
    """

    def __init__(self,  # pylint: disable=R0917
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
    Tag variants: 'NETWORK-REPRESENTATION' | 'NETWORK-REPRESENTATION-PROPS' | 'PHYSICAL-PROPS' |
                  'RESULTING-PROPERTIES' | 'SW-DATA-DEF-PROPS'
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
    Group AR:AUTOSAR-DATA-TYPE
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
    Group AR:IMPLEMENTATION-PROPS
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
    Tag variants: 'EVENT-SYMBOL-NAME' | 'SYMBOL-PROPS'

    Base class already supports everything we need
    """


class ImplementationDataTypeElement(Identifiable):
    """
    Complex type AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
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

    def ref(self) -> AbstractImplementationDataTypeElementRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return AbstractImplementationDataTypeElementRef(ref_str,
                                                        ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE_ELEMENT)


class ImplementationDataType(AutosarDataType):
    """
    Complex type AR:IMPLEMENTATION-DATA-TYPE
    Tag variants: 'IMPLEMENTATION-DATA-TYPE'

    Skip parent class AbstractImplementationDataType since it doesn't have any properties
    of its own.
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
    """

    def __init__(self,
                 name: str,
                 type_ref: AutosarDataTypeRef | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.type_ref: AutosarDataTypeRef | None = None  # .TYPE-TREF
        if type_ref is not None:
            self._assign_optional("type_ref", type_ref, AutosarDataTypeRef)


class VariableDataPrototype(AutosarDataPrototype):
    """
    Complex type AR:VARIABLE-DATA-PROTOTYPE
    Tag variants: 'BULK-NV-BLOCK' | 'RAM-BLOCK' | 'VARIABLE-DATA-PROTOTYPE'
    """

    def __init__(self,
                 name: str,
                 init_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        # .VARIATION-POINT not supported
        if init_value is not None:
            self._assign_optional_strict("init_value", init_value, _get_value_specification_class())

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
    Tag variants: 'PARAMETER-DATA-PROTOTYPE' | 'ROM-BLOCK'
    """

    def __init__(self,
                 name: str,
                 init_value: ValueSpecificationElement | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.init_value: ValueSpecificationElement | None = None  # .INIT-VALUE
        # .VARIATION-POINT not supported
        if init_value is not None:
            self._assign_optional_strict("init_value", init_value, _get_value_specification_class())

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

    def ref(self) -> ArgumentDataPrototypeRef | None:
        """
        Returns a reference to this element or None if the element
        is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        return None if ref_str is None else ArgumentDataPrototypeRef(ref_str)


class ApplicationDataType(AutosarDataType):
    """
    Group AR:APPLICATION-DATA-TYPE
    """


class ApplicationCompositeDataType(ApplicationDataType):
    """
    Group AR:APPLICATION-COMPOSITE-DATA-TYPE
    """

    @property
    def is_composite(self):
        """Returns true if this is a composite data type"""
        return True


class ApplicationPrimitiveDataType(ApplicationDataType):
    """
    Complex type AR:APPLICATION-PRIMITIVE-DATA-TYPE
    Tag variants: 'APPLICATION-PRIMITIVE-DATA-TYPE'
    """

    @property
    def is_composite(self):
        """Returns true if this is a composite data type"""
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

    def ref(self) -> ApplicationArrayElementRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationArrayElementRef(ref_str)


class ApplicationArrayDataType(ApplicationCompositeDataType):
    """
    Complex type AR:APPLICATION-ARRAY-DATA-TYPE
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
    Tag variants: 'APPLICATION-RECORD-ELEMENT'
    """

    def __init__(self,
                 name: str,
                 is_optional: bool | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        self.is_optional: bool | None = None  # .IS-OPTIONAL
        self._assign_optional('is_optional', is_optional, bool)

    def ref(self) -> ApplicationRecordElementRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return ApplicationRecordElementRef(ref_str)


class ApplicationRecordDataType(ApplicationCompositeDataType):
    """
    Complex type AR:APPLICATION-RECORD-DATA-TYPE
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
    Tag variants: 'DATA-TYPE-MAPPING-SET'
    """

    def __init__(self,
                 name: str,
                 data_type_maps: DataTypeMap | list[DataTypeMap] | None = None,
                 mode_request_type_maps: ModeRequestTypeMap | list[ModeRequestTypeMap] | None = None,
                 **kwargs: dict) -> None:
        super().__init__(name, **kwargs)
        # .DATA-TYPE-MAPS
        self.data_type_maps: list[DataTypeMap] = []
        # .MODE-REQUEST-TYPE-MAPS
        self.mode_request_type_maps = []

        if data_type_maps is not None:
            if isinstance(data_type_maps, DataTypeMap):
                self.append(data_type_maps)
            elif isinstance(data_type_maps, Iterable):
                for data_type_map in data_type_maps:
                    self.append(data_type_map)
            else:
                raise TypeError(f'data_type_maps: Invalid type "{str(type(data_type_maps))}"')

        if mode_request_type_maps is not None:
            mode_req_cls = _get_mode_request_type_map_class()
            if isinstance(mode_request_type_maps, mode_req_cls):
                self.append(mode_request_type_maps)
            elif isinstance(mode_request_type_maps, Iterable):
                for mode_request_type_map in mode_request_type_maps:
                    self.append(mode_request_type_map)
            else:
                raise TypeError(f'mode_request_type_maps: Invalid type "{str(type(mode_request_type_maps))}"')

    def append(self, element: DataTypeMap | ModeRequestTypeMap) -> None:
        """
        Appends element to one of the inner lists based on parameter type
        Currently, appending to mode_request_type_maps isn't
        implemented.
        """
        if isinstance(element, DataTypeMap):
            self.data_type_maps.append(element)
        else:
            mode_req_cls = _get_mode_request_type_map_class()
            if isinstance(element, mode_req_cls):
                self.mode_request_type_maps.append(element)
            else:
                raise TypeError(f'Unexpected type: "{str(type(element))}"')

    def ref(self) -> DataTypeMappingSetRef | None:
        """
        Returns a reference to this element or
        None if the element is not yet part of a package
        """
        ref_str = self._calc_ref_string()
        if ref_str is None:
            return None
        return DataTypeMappingSetRef(ref_str)


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


__all__ = [
    "alignment_type_re",
    "display_format_str_re",
    "BaseType",
    "SwBaseType",
    "SwBitRepresentation",
    "SwTextProps",
    "SwPointerTargetProps",
    "SwDataDefPropsConditional",
    "SwDataDefProps",
    "AutosarDataType",
    "ImplementationProps",
    "SymbolProps",
    "ImplementationDataTypeElement",
    "ImplementationDataType",
    "DataPrototype",
    "AutosarDataPrototype",
    "VariableDataPrototype",
    "ParameterDataPrototype",
    "ArgumentDataPrototype",
    "ApplicationDataType",
    "ApplicationCompositeDataType",
    "ApplicationPrimitiveDataType",
    "ApplicationCompositeElementDataPrototype",
    "ApplicationArrayElement",
    "ApplicationArrayDataType",
    "ApplicationRecordElement",
    "ApplicationRecordDataType",
    "DataTypeMap",
    "DataTypeMappingSet",
    "ValueList",
]
