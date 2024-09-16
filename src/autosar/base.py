"""Shared declarations"""
from typing import Any
import abc

DEFAULT_SCHEMA_VERSION = 51


def split_ref(ref: str) -> list[str] | None:
    """Splits a string separated with slashes and automatially removes leading slash"""
    sep = "/"
    if isinstance(ref, str):
        return ref[1:].split(sep) if ref[0] == sep else ref.split(sep)
    return None


def split_ref_strict(ref: str) -> list[str] | None:
    """Splits a strings separated with slashes but throws an error if the string starts with a slash"""
    sep = "/"
    if not isinstance(ref, str):
        raise TypeError("ref: Must be a string")
    if ref[0] == sep:
        raise ValueError("ref: String cannot start with '/'")
    return ref.split(sep)


class Searchable(abc.ABC):
    """
    Searchable interface
    """

    @abc.abstractmethod
    def find(self, ref: str) -> Any:
        """
        Finds an Identifiable object based on its name
        """
