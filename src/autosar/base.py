"""Shared declarations"""
from typing import Any
import abc

DEFAULT_SCHEMA_VERSION = 51


def split_ref(ref: str) -> list[str] | None:
    """Splits an autosar reference string into a list of strings"""
    if isinstance(ref, str):
        return ref[1:].split('/') if ref[0] == '/' else ref.split('/')
    return None


class Searchable(abc.ABC):
    """
    Searchable interface
    """

    @abc.abstractmethod
    def find(self, ref: str) -> Any:
        """
        Finds an Identifiable object based on its name
        """
