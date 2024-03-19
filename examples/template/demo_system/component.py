"""
Component type templates
"""
# flake8: noqa
# pylint: disable=C0103, C0301


import autosar.xml.element as ar_element
import autosar.xml.workspace as ar_workspace
from . import factory, portinterface, constants

NAMESPACE = "Default"


def create_ReceiverComponent(_0: str,
                             workspace: ar_workspace.Workspace,
                             deps: dict[str, ar_element.ARElement] | None,
                             **_1) -> ar_element.ApplicationSoftwareComponentType:
    """
    Create Receiver component type
    """

    timer_interface = deps[portinterface.FreeRunningTimer_I.ref(workspace)]
    vehicle_speed_interface = deps[portinterface.EngineSpeed_I.ref(workspace)]
    engine_speed_interface = deps[portinterface.VehicleSpeed_I.ref(workspace)]
    engine_speed_init = deps[constants.EngineSpeed_IV.ref(workspace)]
    vehicle_speed_init = deps[constants.VehicleSpeed_IV.ref(workspace)]
    swc = ar_element.ApplicationSoftwareComponentType("ReceiverComponent")
    swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "alive_timeout": 0,
                                                                             "enable_update": False,
                                                                             "uses_end_to_end_protection": False,
                                                                             "handle_never_received": False
                                                                             })
    swc.create_require_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
                                                                               "alive_timeout": 0,
                                                                               "enable_update": False,
                                                                               "uses_end_to_end_protection": False,
                                                                               "handle_never_received": False
                                                                               })
    swc.create_require_port("FreeRunningTimer", timer_interface)
    swc.create_internal_behavior()
    return swc


ReceiverComponent = factory.GenericComponentTypeTemplate("ReceiverComponent",
                                                        NAMESPACE,
                                                        create_ReceiverComponent,
                                                        depends=[portinterface.EngineSpeed_I,
                                                                 portinterface.VehicleSpeed_I,
                                                                 portinterface.FreeRunningTimer_I,
                                                                 constants.EngineSpeed_IV,
                                                                 constants.VehicleSpeed_IV,])
ReceiverComponent_Implementation = factory.SwcImplementationTemplate("ReceiverComponent_Implementation",
                                                                     NAMESPACE,
                                                                     component_type=ReceiverComponent)
