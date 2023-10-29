"""
Enum Definitions
"""
# pylint: disable=R0801
from enum import Enum


class ArrayImplPolicy(Enum):
    """
    AR:ARRAY-IMPL-POLICY-ENUM--SIMPLE
    """

    PAYLOAD_AS_ARRAY = 0
    PAYLOAD_AS_POINTER_TO_ARRAY = 1


class ArraySizeHandling(Enum):
    """
    AR:ARRAY-SIZE-HANDLING-ENUM--SIMPLE
    """

    ALL_INDICES_DIFFERENT_ARRAY_SIZE = 0
    ALL_INDICES_SAME_ARRAY_SIZE = 1
    INHERITED_FROM_ARRAY_ELEMENT_TYPE_SIZE = 2


class ArraySizeSemantics(Enum):
    """
    AR:ARRAY-SIZE-SEMANTICS-ENUM--SIMPLE
    """

    FIXED_SIZE = 0
    VARIABLE_SIZE = 1
