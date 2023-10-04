"""
AUTOSAR Model elements

This is the meta-model used by RTE and BSW. For XML model see the autosar.xml modules.
"""
#from typing import Any


class DataType:
    """
    Base class for both BaseType and ImplementationType
    """
    def __init__(self, ref: str) -> None:
        self.ref = ref


class BaseType(DataType):
    """
    A data type created from a SwBaseType
    """

    def __init__(self, xml_ref: str, name: str, native_declaration: str | None = None) -> None:
        super().__init__(xml_ref)
        self.name = name
        self.native_declaration = native_declaration


class ImplementationType(DataType):
    """
    Implementation data type
    """

    def __init__(self,
                 xml_ref: str,
                 name: str,
                 symbol_name: str | None = None,
                 const: bool = False,
                 type_emitter: str | None = None,
                 ) -> None:
        super().__init__(xml_ref)
        self.name = name
        self.const = const
        self.type_emitter = type_emitter
        if symbol_name is None:
            self.symbol_name = name
        else:
            self.symbol_name = symbol_name


class ScalarType(ImplementationType):
    """
    A data type that can represent a single value.
    Created from ar_elements where the category is set to VALUE.
    It directly refers by its SwDataDefProps to a SwBaseType.
    For more information, see: https://computersciencewiki.org/index.php/Scalar_type
    """

    def __init__(self,
                 xml_ref: str,
                 name: str,
                 base_type: BaseType,
                 symbol_name: str | None = None,
                 const: bool = False,
                 type_emitter: str | None = None) -> None:
        super().__init__(xml_ref, name, symbol_name, const, type_emitter)
        self.base_type = base_type


class ArrayType(ImplementationType):
    """
    A data type that can represent an array.
    Created from ar_elements where the category is set to ARRAY.
    Sub-elements are used to define each dimension of the array.
    The array_size specifies the number of array elements of the dimension.
    """


class RefType(ImplementationType):
    """
    A data type that references another ImplementationDataType (typedef).
    Created from ar_elements where the category is set to TYPE_REFERENCE.
    """

    def __init__(self,
                 xml_ref: str,
                 name: str,
                 impl_type: ScalarType,
                 symbol_name: str | None = None,
                 const: bool = False) -> None:
        super().__init__(xml_ref, name, symbol_name, const)
        self.impl_type = impl_type


class PointerType(ImplementationType):
    """
    A pointer to another ImplementationDataType.
    Created from ar_elements where the category is set to DATA_REFERENCE.
    """


class StructType(ImplementationType):
    """
    A data type that can represent a structure.
    Created from ar_elements where the category is set to STRUCTURE.
    """


class UnionType(ImplementationType):
    """
    A data type that can represent a union.
    Created from ar_elements where the category is set to UNION.
    """
