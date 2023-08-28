"""
Model enum Definitions
"""

from enum import Enum


class ByteOrder(Enum):
    """
    Byte order
    """

    BIG_ENDIAN = 0
    LITTLE_ENDIAN = 1
    OPAQUE = 2
