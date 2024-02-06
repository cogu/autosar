"""
Port interface templates
"""
# flake8: noqa
# pylint: disable=C0103, C0301


from . import factory, mode

NAMESPACE = "Default"

EcuM_CurrentMode = factory.ModeSwitchInterfaceTemplate("EcuM_CurrentMode", NAMESPACE, mode.EcuM_Mode, "currentMode", is_service=True)
