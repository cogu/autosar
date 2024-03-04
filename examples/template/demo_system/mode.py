"""
Modes
"""
# flake8: noqa
# pylint: disable=C0103, C0301

from . import factory

NAMESPACE = "Default"

EcuM_Mode = factory.ModeDeclarationGroupTemplate("EcuM_Mode", "Default", ["STARTUP", "RUN", "POST_RUN", "SLEEP", "WAKEUP", "SHUTDOWN"], "STARTUP")
