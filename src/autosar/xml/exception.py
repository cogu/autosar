"""
Collection of user-defined exceptions
"""

from typing import Any


class ParseError(RuntimeError):
    """
    Raised by ARXML parser
    """


class DuplicateElement(ValueError):
    """
    Element with this name already in exist in current context
    """


class VersionError(ValueError):
    """
    Invalid/Unsupported XML version
    """


class AssignmentTypeError(TypeError):
    """
    Assignment of invalid type
    """

    def __init__(self, name: str, expected_types: str | list[str] | tuple[str], value: Any) -> None:
        if isinstance(expected_types, str):
            expected = expected_types
        else:
            expected = ", ".join(expected_types)
        msg = f"{name}: Invalid type. Expected one of ({expected}), got '{str(type(value))}'"
        super().__init__(msg)
