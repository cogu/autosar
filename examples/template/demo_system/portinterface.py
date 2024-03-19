"""
Port interface templates
"""
# flake8: noqa
# pylint: disable=C0103, C0301


import autosar.xml.element as ar_element
import autosar.xml.workspace as ar_workspace
from . import factory, mode, platform

NAMESPACE = "Default"


def create_NvMService_interface(element_ref: str,
                                _1: ar_workspace.Workspace,
                                _2: dict[str, ar_element.ARElement] | None,
                                **_3) -> ar_element.ClientServerInterface:
    """
    Create NvmService interface
    """

    port_interface = ar_element.ClientServerInterface("NvMService_I", is_service=True)
    e_not_ok = port_interface.create_possible_error("E_NOT_OK", 1)
    port_interface.create_operation("EraseBlock", possible_error_refs=element_ref + "/" + e_not_ok.name)
    return port_interface


def create_free_running_timer_interface(_0: str,
                                        workspace: ar_workspace.Workspace,
                                        deps: dict[str, ar_element.ARElement] | None,
                                        **_1) -> ar_element.ClientServerInterface:
    """
    Creates client server interface FreeRunningTimer_I
    """
    uint32_impl_type = deps[platform.ImplementationTypes.uint32.ref(workspace)]
    boolean_impl_type = deps[platform.ImplementationTypes.boolean.ref(workspace)]
    port_interface = ar_element.ClientServerInterface("FreeRunningTimer_I")
    operation = port_interface.create_operation("GetTime")
    operation.create_out_argument("value", type_ref=uint32_impl_type.ref())
    operation = port_interface.create_operation("IsTimerElapsed")
    operation.create_in_argument("startTime", type_ref=uint32_impl_type.ref())
    operation.create_in_argument("duration", type_ref=uint32_impl_type.ref())
    operation.create_out_argument("result", type_ref=boolean_impl_type.ref())
    return port_interface

EcuM_CurrentMode = factory.ModeSwitchInterfaceTemplate("EcuM_CurrentMode", NAMESPACE, mode.EcuM_Mode, "currentMode", is_service=True)
NvMService_I = factory.GenericPortInterfaceTemplate("NvMService_I", NAMESPACE, create_NvMService_interface)
FreeRunningTimer_I = factory.GenericPortInterfaceTemplate("FreeRunningTimer_I",
                                                          NAMESPACE,
                                                          create_free_running_timer_interface,
                                                          depends=[platform.ImplementationTypes.uint32,
                                                                   platform.ImplementationTypes.boolean])
VehicleSpeed_I = factory.SenderReceiverInterfaceTemplate("VehicleSpeed_I", NAMESPACE, platform.ImplementationTypes.uint16)
EngineSpeed_I = factory.SenderReceiverInterfaceTemplate("EngineSpeed_I", NAMESPACE, platform.ImplementationTypes.uint16)
