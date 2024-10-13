"""
Component type templates
"""
# pylint: disable=C0103, C0301


import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
import autosar.xml.workspace as ar_workspace
from . import factory, portinterface, constants

NAMESPACE = "Default"


def create_ReceiverComponent(package: ar_element.Package,
                             workspace: ar_workspace.Workspace,
                             deps: dict[str, ar_element.ARElement] | None,
                             **_1) -> ar_element.ApplicationSoftwareComponentType:
    """
    Receiver ports:
    - EngineSpeed
    - VehicleSpeed
    Client ports:
    - FreeRunningTimer
    """
    timer_interface = deps[portinterface.FreeRunningTimer_I.ref(workspace)]
    vehicle_speed_interface = deps[portinterface.VehicleSpeed_I.ref(workspace)]
    engine_speed_interface = deps[portinterface.EngineSpeed_I.ref(workspace)]
    ecu_mode_interface = deps[portinterface.EcuM_CurrentMode_I.ref(workspace)]
    engine_speed_init = deps[constants.EngineSpeed_IV.ref(workspace)]
    vehicle_speed_init = deps[constants.VehicleSpeed_IV.ref(workspace)]
    swc_name = "ReceiverComponent"
    swc = ar_element.ApplicationSoftwareComponentType(swc_name)
    package.append(swc)
    swc.create_require_port("EcuM_CurrentMode", ecu_mode_interface, com_spec={"enhanced_mode_api": False,
                                                                              "supports_async": False})
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
    init_runnable_name = swc_name + '_Init'
    periodic_runnable_name = swc_name + '_Run'
    behavior = swc.create_internal_behavior()
    behavior.create_runnable(init_runnable_name)
    behavior.create_runnable(periodic_runnable_name)
    behavior.create_swc_mode_mode_switch_event(init_runnable_name,
                                               "EcuM_CurrentMode/RUN",
                                               ar_enum.ModeActivationKind.ON_ENTRY)
    behavior.create_timing_event(periodic_runnable_name, 20.0 / 1000)
    return swc


def create_TimerComponent(package: ar_element.Package,
                          workspace: ar_workspace.Workspace,
                          deps: dict[str, ar_element.ARElement] | None,
                          **_0) -> ar_element.ApplicationSoftwareComponentType:
    """
    Create TimerComponent component type
    """
    timer_interface = deps[portinterface.FreeRunningTimer_I.ref(workspace)]
    swc = ar_element.ApplicationSoftwareComponentType("TimerComponent")
    package.append(swc)
    swc.create_provide_port("FreeRunningTimer", timer_interface, com_spec={"GetTime": {"queue_length": 1},
                                                                           "IsTimerElapsed": {"queue_length": 1}
                                                                           })
    behavior = swc.create_internal_behavior()
    init_runnable_name = swc.name + "_Init"
    get_time_runnable_name = swc.name + "_GetTime"
    timer_elapsed_runnable_name = swc.name + "_IsTimerElapsed"
    behavior.create_runnable(init_runnable_name)
    behavior.create_runnable(get_time_runnable_name, reentrancy_level=ar_enum.ReentrancyLevel.NON_REENTRANT)
    behavior.create_runnable(timer_elapsed_runnable_name, reentrancy_level=ar_enum.ReentrancyLevel.NON_REENTRANT)
    behavior.create_init_event(init_runnable_name)
    behavior.create_operation_invoked_event(get_time_runnable_name, "FreeRunningTimer/GetTime")
    behavior.create_operation_invoked_event(timer_elapsed_runnable_name, "FreeRunningTimer/IsTimerElapsed")
    return swc


def create_composition_component(package: ar_element.Package,
                                 workspace: ar_workspace.Workspace,
                                 deps: dict[str, ar_element.ARElement] | None,
                                 **_0) -> ar_element.ApplicationSoftwareComponentType:
    """
    Creates a composition component
    The created swc must be manually added to the package, otherwise the
    swc.create_connector will not work properly.
    To disable automatic adding of the SWC by the workspace, set append_to_package to False
    in the template constructor.
    """
    engine_speed_interface = deps[portinterface.EngineSpeed_I.ref(workspace)]
    vehicle_speed_interface = deps[portinterface.VehicleSpeed_I.ref(workspace)]
    engine_speed_init = deps[constants.EngineSpeed_IV.ref(workspace)]
    vehicle_speed_init = deps[constants.VehicleSpeed_IV.ref(workspace)]
    receiver_component = workspace.find(ReceiverComponent.ref(workspace))
    timer_component = workspace.find(TimerComponent.ref(workspace))
    assert isinstance(receiver_component, ar_element.ApplicationSoftwareComponentType)
    assert isinstance(timer_component, ar_element.ApplicationSoftwareComponentType)
    swc = ar_element.CompositionSwComponentType("CompositionComponent")
    package.append(swc)
    swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": engine_speed_init.ref(),
                                                                             "uses_end_to_end_protection": False})
    swc.create_require_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": vehicle_speed_init.ref(),
                                                                               "uses_end_to_end_protection": False})

    swc.create_component_prototype(receiver_component)
    swc.create_component_prototype(timer_component)
    swc.create_connector("TimerComponent/FreeRunningTimer", "ReceiverComponent/FreeRunningTimer", workspace)
    swc.create_connector("VehicleSpeed", "ReceiverComponent/VehicleSpeed", workspace)
    swc.create_connector("EngineSpeed", "ReceiverComponent/EngineSpeed", workspace)
    return swc


ReceiverComponent = factory.GenericComponentTypeTemplate("ReceiverComponent",
                                                         NAMESPACE,
                                                         create_ReceiverComponent,
                                                         depends=[portinterface.EcuM_CurrentMode_I,
                                                                  portinterface.EngineSpeed_I,
                                                                  portinterface.VehicleSpeed_I,
                                                                  portinterface.FreeRunningTimer_I,
                                                                  constants.EngineSpeed_IV,
                                                                  constants.VehicleSpeed_IV])
ReceiverComponent_Implementation = factory.SwcImplementationTemplate("ReceiverComponent_Implementation",
                                                                     NAMESPACE,
                                                                     component_type=ReceiverComponent)
TimerComponent = factory.GenericComponentTypeTemplate("TimerComponent",
                                                      NAMESPACE,
                                                      create_TimerComponent,
                                                      depends=[portinterface.FreeRunningTimer_I])
TimerComponent_Implementation = factory.SwcImplementationTemplate("TimerComponent_Implementation",
                                                                  NAMESPACE,
                                                                  component_type=TimerComponent)
CompositionComponent = factory.GenericComponentTypeTemplate("CompositionComponent",
                                                            NAMESPACE,
                                                            create_composition_component,
                                                            depends=[portinterface.EngineSpeed_I,
                                                                     portinterface.VehicleSpeed_I,
                                                                     constants.EngineSpeed_IV,
                                                                     constants.VehicleSpeed_IV,
                                                                     ReceiverComponent_Implementation,
                                                                     TimerComponent_Implementation])
