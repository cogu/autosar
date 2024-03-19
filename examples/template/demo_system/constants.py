"""
Constants templates
"""
# flake8: noqa
# pylint: disable=C0103, C0301

from . import factory

NAMESPACE = "Default"

EngineSpeed_IV = factory.ConstantTemplate("EngineSpeed_IV", NAMESPACE, 65535)
VehicleSpeed_IV = factory.ConstantTemplate("VehicleSpeed_IV", NAMESPACE, 65535)
