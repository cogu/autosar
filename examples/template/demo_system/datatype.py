"""
data types
"""
# flake8: noqa
# pylint: disable=C0103, C0301

from . import factory, platform

NAMESPACE = "Default"

InactiveActive_T = factory.ImplementationEnumDataTypeTemplate("InactiveActive_T", "Default", platform.BaseTypes.uint8, ["InactiveActive_Inactive", "InactiveActive_Active"])
