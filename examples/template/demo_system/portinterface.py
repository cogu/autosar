"""
Port interface templates
"""
# flake8: noqa
# pylint: disable=C0103, C0301


import autosar.xml.element as ar_element
import autosar.xml.workspace as ar_workspace
from . import factory, mode

NAMESPACE = "Default"

EcuM_CurrentMode = factory.ModeSwitchInterfaceTemplate("EcuM_CurrentMode", NAMESPACE, mode.EcuM_Mode, "currentMode", is_service=True)


def create_NvMService_interface(element_ref: str,
                                _1: ar_workspace.Workspace,
                                _2: dict[str, ar_element.ARElement] | None,
                                **_3) -> ar_element.ClientServerInterface:
    """
    Create NvmService interface
    """

    interface = ar_element.ClientServerInterface("NvMService_I", is_service=True)
    e_not_ok = interface.create_possible_error("E_NOT_OK", 1)
    interface.create_operation("EraseBlock", possible_error_refs=element_ref + "/" + e_not_ok.name)
    return interface


NvMService_I = factory.GenericPortInterfaceTemplate("NvMService_I", NAMESPACE, create_NvMService_interface)
