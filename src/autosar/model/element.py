"""
AUTOSAR Model elements

This is the meta-model used by RTE and BSW. For XML model see the autosar.xml modules.
"""


class BaseType:
    """
    A data type created from a SwBaseType
    """

    def __init__(self, name: str, native_declaration: str | None = None) -> None:
        self.name = name
        self.native_declaration = native_declaration


class DataType:
    """
    Implementation data type
    """

    def __init__(self,
                 name: str,
                 symbol_name: str | None = None,
                 const: bool = False
                 ) -> None:
        self.name = name
        self.const = const
        if symbol_name is None:
            self.symbol_name = name
        else:
            self.symbol_name = symbol_name


class ScalarType(DataType):
    """
    A data type that can represent a single value.
    Created from ar_elements where the category is set to VALUE.
    It directly refers by its SwDataDefProps to a SwBaseType.
    For more information, see: https://computersciencewiki.org/index.php/Scalar_type
    """

    def __init__(self,
                 name: str,
                 base_type: BaseType,
                 symbol_name: str | None = None,
                 const: bool = False) -> None:
        super().__init__(name, symbol_name, const)
        self.base_type = base_type


class ArrayType(DataType):
    """
    A data type that can represent an array.
    Created from ar_elements where the category is set to ARRAY.
    Sub-elements are used to define each dimension of the array.
    The array_size specifies the number of array elements of the dimension.
    """


class RefType(DataType):
    """
    A data type that references another ImplementationDataType (typedef).
    Created from ar_elements where the category is set to TYPE_REFERENCE.
    """


class PointerType(DataType):
    """
    A pointer to another ImplementationDataType.
    Created from ar_elements where the category is set to DATA_REFERENCE.
    """


class StructType(DataType):
    """
    A data type that can represent a structure.
    Created from ar_elements where the category is set to STRUCTURE.
    """


class UnionType(DataType):
    """
    A data type that can represent a union.
    Created from ar_elements where the category is set to UNION.
    """
