"""
Collection of user-defined exceptions
"""


class ParseError(RuntimeError):
    """
    Raised by ARXML parser
    """


class VersionError(ValueError):
    """
    Invalid/Unsupported XML version
    """
