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

    def __init__(self,
                 name: str,
                 expected_types: str | type | list[str | type] | tuple[str | type, ...] | set[str | type],
                 value: Any) -> None:
        if isinstance(expected_types, str):
            expected = expected_types
        elif isinstance(expected_types, type):
            expected = expected_types.__name__
        elif isinstance(expected_types, (list, tuple, set)):
            expected = ", ".join(t.__name__ if isinstance(t, type) else str(t) for t in expected_types)
        else:
            expected = str(expected_types)
        msg = f"{name}: Invalid type. Expected one of ({expected}), got '{str(type(value))}'"
        super().__init__(msg)


class InvalidReferenceError(ValueError):
    """
    Reference is invalid
    """
