"""Unit tests for programmatically building components and save them as XML"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
from typing import Any
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element # noqa E402
import autosar.xml.enumeration as ar_enum # noqa E402
import autosar # noqa E402


def create_packages(workspace: autosar.xml.workspace.Workspace) -> dict[str, ar_element.Package]:
    """
    Creates the packages needed for unit tests
    """
    packages = dict(zip(["PlatformBaseTypes",
                         "PlatformImplementationDataTypes",
                         "PlatformDataConstraints",
                         "PlatformCompuMethods",
                         "Constants",
                         "PortInterfaces",
                         "ModeDeclarations",
                         "ComponentTypes"],
                    workspace.make_packages("AUTOSAR_Platform/BaseTypes",
                                            "AUTOSAR_Platform/ImplementationDataTypes",
                                            "AUTOSAR_Platform/DataConstraints",
                                            "AUTOSAR_Platform/CompuMethods",
                                            "Constants",
                                            "PortInterfaces",
                                            "ModeDeclarations",
                                            "ComponentTypes")))
    return packages


def create_platform_types(packages: dict[str, ar_element.Package]):
    """
    Creates necessary platform types
    """
    boolean_base_type = ar_element.SwBaseType('boolean', size=8, encoding="BOOLEAN")
    packages["PlatformBaseTypes"].append(boolean_base_type)
    uint8_base_type = ar_element.SwBaseType('uint8', size=8)
    packages["PlatformBaseTypes"].append(uint8_base_type)
    uint16_base_type = ar_element.SwBaseType('uint16', size=16)
    packages["PlatformBaseTypes"].append(uint16_base_type)
    uint32_base_type = ar_element.SwBaseType('uint32', size=32)
    packages["PlatformBaseTypes"].append(uint32_base_type)
    boolean_data_constr = ar_element.DataConstraint.make_internal("boolean_DataConstr", 0, 1)
    packages["PlatformDataConstraints"].append(boolean_data_constr)
    computation = ar_element.Computation.make_value_table(["FALSE", "TRUE"])
    boolean_compu_method = ar_element.CompuMethod(name="boolean_CompuMethod",
                                                  category="TEXTTABLE",
                                                  int_to_phys=computation)
    packages["PlatformCompuMethods"].append(boolean_compu_method)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref(),
                                                             data_constraint_ref=boolean_data_constr.ref(),
                                                             compu_method_ref=boolean_compu_method.ref())
    boolean_impl_type = ar_element.ImplementationDataType("boolean",
                                                          category="VALUE",
                                                          sw_data_def_props=sw_data_def_props)
    packages["PlatformImplementationDataTypes"].append(boolean_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
    uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                        category="VALUE",
                                                        sw_data_def_props=sw_data_def_props)
    packages["PlatformImplementationDataTypes"].append(uint8_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint16_base_type.ref())
    uint16_impl_type = ar_element.ImplementationDataType("uint16",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    packages["PlatformImplementationDataTypes"].append(uint16_impl_type)
    sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint32_base_type.ref())
    uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
    packages["PlatformImplementationDataTypes"].append(uint32_impl_type)


def create_mode_declaration_groups(packages: dict[str, ar_element.Package]):
    """
    Creates mode declarations
    """
    vehicle_mode = ar_element.ModeDeclarationGroup("VehicleMode", ["OFF",
                                                                   "PARKING",
                                                                   "ACCESSORY",
                                                                   "CRANKING",
                                                                   "RUNNING"])
    packages["ModeDeclarations"].append(vehicle_mode)
    vehicle_mode.initial_mode_ref = vehicle_mode.find("OFF").ref()

    application_mode = ar_element.ModeDeclarationGroup("ApplicationMode", ["INACTIVE",
                                                                           "ACTIVE"])
    packages["ModeDeclarations"].append(application_mode)
    application_mode.initial_mode_ref = application_mode.find("INACTIVE").ref()


def create_vehicle_speed_interface(packages: dict[str, ar_element.Package]) -> ar_element.SenderReceiverInterface:
    """
    Create sender-receiver port interface for vehicle speed
    """
    uint16_impl_t = packages["PlatformImplementationDataTypes"].find("uint16")
    port_interface = ar_element.SenderReceiverInterface("VehicleSpeed_I")
    port_interface.create_data_element("VehicleSpeed", type_ref=uint16_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_engine_speed_interface(packages: dict[str, ar_element.Package]) -> ar_element.SenderReceiverInterface:
    """
    Create sender-receiver port interface for engine speed
    """
    uint16_impl_t = packages["PlatformImplementationDataTypes"].find("uint16")
    port_interface = ar_element.SenderReceiverInterface("EngineSpeed_I")
    port_interface.create_data_element("EngineSpeed", type_ref=uint16_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_safe_state_interface(packages: dict[str, ar_element.Package]) -> ar_element.SenderReceiverInterface:
    """
    Create sender-receiver port interface for safe state
    """
    boolean_impl_t = packages["PlatformImplementationDataTypes"].find("boolean")
    port_interface = ar_element.SenderReceiverInterface("SafeState_I")
    port_interface.create_data_element("SafeState", type_ref=boolean_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_vehicle_mode_interface(packages: dict[str, ar_element.Package]) -> ar_element.ModeSwitchInterface:
    """
    Create mode switch interface
    """
    mode_declaration_group = packages["ModeDeclarations"].find("VehicleMode")
    portinterface = ar_element.ModeSwitchInterface("VehicleMode_I")
    portinterface.create_mode_group("mode", mode_declaration_group.ref())
    packages["PortInterfaces"].append(portinterface)
    return portinterface


def create_application_mode_interface(packages: dict[str, ar_element.Package]) -> ar_element.ModeSwitchInterface:
    """
    Create mode switch interface
    """
    mode_declaration_group = packages["ModeDeclarations"].find("ApplicationMode")
    portinterface = ar_element.ModeSwitchInterface("ApplicationMode_I")
    portinterface.create_mode_group("mode", mode_declaration_group.ref())
    packages["PortInterfaces"].append(portinterface)
    return portinterface


def create_timer_interface(packages: dict[str, ar_element.Package]) -> ar_element.ClientServerInterface:
    """
    Create mode switch interface
    """
    uint32_impl_t = packages["PlatformImplementationDataTypes"].find("uint32")
    portinterface = ar_element.ClientServerInterface("Timer_I", is_service=False)
    packages["PortInterfaces"].append(portinterface)
    operation = portinterface.create_operation("GetTime")
    operation.create_out_argument("value",
                                  server_arg_impl_policy=ar_enum.ServerArgImplPolicy.USE_ARGUMENT_TYPE,
                                  type_ref=uint32_impl_t.ref())
    return portinterface


def create_init_value(packages, name: str, value: Any) -> ar_element.ConstantSpecification:
    """
    Creates VehicleSpeed init value
    """
    constant = ar_element.ConstantSpecification.make_constant(name, value)
    packages["Constants"].append(constant)
    return constant


def create_application_swc(packages):
    """
    Creates application SW component
    """
    swc = ar_element.ApplicationSoftwareComponentType("MyApplication")
    packages["ComponentTypes"].append(swc)
    swc.create_internal_behavior("MyApplication_InternalBehavior")
    return swc


class TestSenderPort(unittest.TestCase):

    def test_init_value_ref(self):
        workspace = autosar.xml.Workspace()
        packages = create_packages(workspace)
        create_platform_types(packages)
        port_interface = create_vehicle_speed_interface(packages)
        init_value = create_init_value(packages, "VehicleSpeed_IV", 65535)
        swc = create_application_swc(packages)
        port = swc.create_provide_port("VehicleSpeed", port_interface, com_spec={'init_value': init_value.ref()})
        self.assertIsInstance(port, ar_element.ProvidePortPrototype)
        com_spec: ar_element.NonqueuedSenderComSpec = port.com_spec[0]
        self.assertIsInstance(com_spec, ar_element.NonqueuedSenderComSpec)
        self.assertIsInstance(com_spec.init_value, ar_element.ConstantReference)
        self.assertEqual(str(com_spec.init_value.constant_ref), "/Constants/VehicleSpeed_IV")

    def test_numerical_init_value(self):
        workspace = autosar.xml.Workspace()
        packages = create_packages(workspace)
        create_platform_types(packages)
        port_interface = create_vehicle_speed_interface(packages)
        swc = create_application_swc(packages)
        port = swc.create_provide_port("VehicleSpeed", port_interface, com_spec={'init_value': 65535})
        self.assertIsInstance(port, ar_element.ProvidePortPrototype)
        com_spec: ar_element.NonqueuedSenderComSpec = port.com_spec[0]
        self.assertIsInstance(com_spec, ar_element.NonqueuedSenderComSpec)
        self.assertIsInstance(com_spec.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(com_spec.init_value.value, 65535)


class TestReceiverPort(unittest.TestCase):

    def test_init_value_ref(self):
        workspace = autosar.xml.Workspace()
        packages = create_packages(workspace)
        create_platform_types(packages)
        port_interface = create_vehicle_speed_interface(packages)
        init_value = create_init_value(packages, "VehicleSpeed_IV", 65535)
        swc = create_application_swc(packages)
        port = swc.create_require_port("VehicleSpeed", port_interface, com_spec={'init_value': init_value.ref()})
        self.assertIsInstance(port, ar_element.RequirePortPrototype)
        com_spec: ar_element.NonqueuedReceiverComSpec = port.com_spec[0]
        self.assertIsInstance(com_spec, ar_element.NonqueuedReceiverComSpec)
        self.assertIsInstance(com_spec.init_value, ar_element.ConstantReference)
        self.assertEqual(str(com_spec.init_value.constant_ref), "/Constants/VehicleSpeed_IV")

    def test_numerical_init_value(self):
        workspace = autosar.xml.Workspace()
        packages = create_packages(workspace)
        create_platform_types(packages)
        port_interface = create_vehicle_speed_interface(packages)
        swc = create_application_swc(packages)
        port = swc.create_require_port("VehicleSpeed", port_interface, com_spec={'init_value': 65535})
        self.assertIsInstance(port, ar_element.RequirePortPrototype)
        com_spec: ar_element.NonqueuedReceiverComSpec = port.com_spec[0]
        self.assertIsInstance(com_spec, ar_element.NonqueuedReceiverComSpec)
        self.assertIsInstance(com_spec.init_value, ar_element.NumericalValueSpecification)
        self.assertEqual(com_spec.init_value.value, 65535)


class TestSwcPortFinderAPI(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        vehicle_speed_interface = create_vehicle_speed_interface(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        safe_state_interface = create_safe_state_interface(packages)
        swc = create_application_swc(packages)
        swc.create_provide_port("VehicleSpeed", vehicle_speed_interface, com_spec={'init_value': 65535})
        swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={'init_value': 65535})
        swc.create_pr_port("SafeState", safe_state_interface, provided_com_spec={'init_value': False})
        return swc

    def test_find_r_port(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        self.assertIsInstance(swc, ar_element.ApplicationSoftwareComponentType)
        port = swc.find_r_port("EngineSpeed")
        self.assertIsInstance(port, ar_element.RequirePortPrototype)
        self.assertEqual(port.name, "EngineSpeed")
        port = swc.find_r_port("SafeState")
        self.assertIsInstance(port, ar_element.PRPortPrototype)
        self.assertEqual(port.name, "SafeState")
        self.assertIsNone(swc.find_r_port("VehicleSpeed"))

    def test_find_p_port(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        self.assertIsInstance(swc, ar_element.ApplicationSoftwareComponentType)
        port = swc.find_p_port("VehicleSpeed")
        self.assertIsInstance(port, ar_element.ProvidePortPrototype)
        self.assertEqual(port.name, "VehicleSpeed")
        port = swc.find_p_port("SafeState")
        self.assertIsInstance(port, ar_element.PRPortPrototype)
        self.assertEqual(port.name, "SafeState")
        self.assertIsNone(swc.find_p_port("EngineSpeed"))


class TestRootCollectionAPI(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        swc = create_application_swc(packages)
        swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={'init_value': 65535})
        return swc

    def test_find_root_from_package(self):
        workspace = autosar.xml.Workspace()
        packages = create_packages(workspace)
        package = packages["PortInterfaces"]
        root = package.root_collection()
        self.assertIs(root, workspace)

    def test_find_root_from_swc(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        root = swc.root_collection()
        self.assertIs(root, workspace)

    def test_find_root_from_port(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        port = swc.find_r_port("EngineSpeed")
        root = port.root_collection()
        self.assertIs(root, workspace)


class TestWorkspaceFinder(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        swc = create_application_swc(packages)
        swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={'init_value': 65535})
        return swc

    def test_find_port_by_reference(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        port1 = swc.find_r_port("EngineSpeed")
        self.assertEqual(str(port1.ref()), "/ComponentTypes/MyApplication/EngineSpeed")
        port2 = workspace.find(port1.ref())
        self.assertIs(port1, port2)

    def test_find_port_interface_by_reference(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        port: ar_element.RequirePortPrototype = swc.find_r_port("EngineSpeed")
        self.assertEqual(str(port.port_interface_ref), "/PortInterfaces/EngineSpeed_I")
        port_interface = workspace.find(port.port_interface_ref)
        self.assertIsInstance(port_interface, ar_element.SenderReceiverInterface)
        self.assertEqual(port_interface.name, "EngineSpeed_I")


class TestPortInterfaceSubElementsGetterAPI(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        vehicle_speed_interface = create_vehicle_speed_interface(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        swc = create_application_swc(packages)
        swc.create_provide_port("VehicleSpeed", vehicle_speed_interface, com_spec={'init_value': 65535})
        swc.create_require_port("EngineSpeed", engine_speed_interface, com_spec={'init_value': 65535})
        return swc

    def test_find_data_element_on_p_port_with_sender_receiver_interface(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        port: ar_element.RequirePortPrototype = swc.find_p_port("VehicleSpeed")
        # With data element name
        data_element1 = swc.get_data_element_in_port(port, "VehicleSpeed")
        self.assertIsInstance(data_element1, ar_element.VariableDataPrototype)
        self.assertEqual(str(data_element1.ref()), "/PortInterfaces/VehicleSpeed_I/VehicleSpeed")
        # Without data element name
        data_element2 = swc.get_data_element_in_port(port)
        self.assertIs(data_element1, data_element2)


class TestEventCreaterAPI(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.expected_behavior_ref = "/ComponentTypes/MyApplication/MyApplication_InternalBehavior"

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        create_mode_declaration_groups(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        vehicle_mode_interface = create_vehicle_mode_interface(packages)
        application_mode_interface = create_application_mode_interface(packages)
        timer_interface = create_timer_interface(packages)
        swc = create_application_swc(packages)
        swc.create_r_port("EngineSpeed", engine_speed_interface, com_spec={'init_value': 65535})
        swc.create_r_port("VehicleMode", vehicle_mode_interface, com_spec={'supports_async': False})
        swc.create_p_port("ApplicationMode", application_mode_interface)
        swc.create_p_port("Timer", timer_interface)
        return swc

    def test_create_background_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("background_event_prefix", "BT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Background")
        event = behavior.create_background_event("MyApplication_Background")
        self.assertIsInstance(event, ar_element.BackgroundEvent)
        self.assertEqual(event.name, "BT_MyApplication_Background")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Background")

    def test_create_data_receive_error_event_using_port_name_only(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_error_event_prefix", "DRET_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("EngineSpeed_Updated")
        event = behavior.create_data_receive_error_event("EngineSpeed_Updated", "EngineSpeed")
        self.assertIsInstance(event, ar_element.DataReceiveErrorEvent)
        self.assertEqual(event.name, "DRET_EngineSpeed_Updated_EngineSpeed_EngineSpeed")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/EngineSpeed_Updated")
        self.assertEqual(str(event.data.context_port), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(event.data.target_data_element), "/PortInterfaces/EngineSpeed_I/EngineSpeed")

    def test_create_data_receive_error_event_using_port_and_data_element(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_error_event_prefix", "DRET_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("EngineSpeed_Updated")
        event = behavior.create_data_receive_error_event("EngineSpeed_Updated", "EngineSpeed/EngineSpeed")
        self.assertIsInstance(event, ar_element.DataReceiveErrorEvent)
        self.assertEqual(event.name, "DRET_EngineSpeed_Updated_EngineSpeed_EngineSpeed")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/EngineSpeed_Updated")
        self.assertEqual(str(event.data.context_port), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(event.data.target_data_element), "/PortInterfaces/EngineSpeed_I/EngineSpeed")

    def test_create_data_received_event_using_port_name_only(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_event_prefix", "DRT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("EngineSpeed_Updated")
        event = behavior.create_data_received_event("EngineSpeed_Updated", "EngineSpeed")
        self.assertIsInstance(event, ar_element.DataReceivedEvent)
        self.assertEqual(event.name, "DRT_EngineSpeed_Updated_EngineSpeed_EngineSpeed")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/EngineSpeed_Updated")
        self.assertEqual(str(event.data.context_port), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(event.data.target_data_element), "/PortInterfaces/EngineSpeed_I/EngineSpeed")

    def test_create_data_received_event_using_port_and_data_element(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_event_prefix", "DRT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("EngineSpeed_Updated")
        event = behavior.create_data_received_event("EngineSpeed_Updated", "EngineSpeed/EngineSpeed")
        self.assertIsInstance(event, ar_element.DataReceivedEvent)
        self.assertEqual(event.name, "DRT_EngineSpeed_Updated_EngineSpeed_EngineSpeed")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/EngineSpeed_Updated")
        self.assertEqual(str(event.data.context_port), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(event.data.target_data_element), "/PortInterfaces/EngineSpeed_I/EngineSpeed")

    def test_create_init_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("init_event_prefix", "IT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Init")
        event = behavior.create_init_event("MyApplication_Init")
        self.assertIsInstance(event, ar_element.InitEvent)
        self.assertEqual(event.name, "IT_MyApplication_Init")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Init")

    def test_create_operation_invoked_event_port_name_only(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("operation_invoked_event_prefix", "OIT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_GetTime")
        event = behavior.create_operation_invoked_event("MyApplication_GetTime", "Timer")
        self.assertIsInstance(event, ar_element.OperationInvokedEvent)
        self.assertEqual(event.name, "OIT_MyApplication_GetTime_Timer_GetTime")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_GetTime")
        self.assertEqual(str(event.operation.context_port), "/ComponentTypes/MyApplication/Timer")
        self.assertEqual(str(event.operation.target_provided_operation), "/PortInterfaces/Timer_I/GetTime")

    def test_create_operation_invoked_event_with_operation_name(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("operation_invoked_event_prefix", "OIT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_GetTime")
        event = behavior.create_operation_invoked_event("MyApplication_GetTime", "Timer/GetTime")
        self.assertIsInstance(event, ar_element.OperationInvokedEvent)
        self.assertEqual(event.name, "OIT_MyApplication_GetTime_Timer_GetTime")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_GetTime")
        self.assertEqual(str(event.operation.context_port), "/ComponentTypes/MyApplication/Timer")
        self.assertEqual(str(event.operation.target_provided_operation), "/PortInterfaces/Timer_I/GetTime")

    def test_create_swc_mode_manager_error_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("swc_mode_manager_error_event_prefix", "MMET_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_ApplicationModeError")
        event = behavior.create_swc_mode_manager_error_event("MyApplication_ApplicationModeError", "ApplicationMode")
        self.assertIsInstance(event, ar_element.SwcModeManagerErrorEvent)
        self.assertEqual(event.name, "MMET_MyApplication_ApplicationModeError_ApplicationMode_mode",)
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_ApplicationModeError")
        self.assertEqual(str(event.mode_group.context_port), "/ComponentTypes/MyApplication/ApplicationMode")
        self.assertEqual(str(event.mode_group.context_mode_declaration_group_prototype),
                         "/PortInterfaces/ApplicationMode_I/mode")

    def test_create_swc_mode_switch_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("swc_mode_switch_event_prefix", "MST_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Init")
        event = behavior.create_swc_mode_mode_switch_event("MyApplication_Init",
                                                           "VehicleMode/ACCESSORY")
        self.assertIsInstance(event, ar_element.SwcModeSwitchEvent)
        self.assertEqual(event.name, "MST_MyApplication_Init",)
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Init")
        self.assertEqual(str(event.mode.context_port), "/ComponentTypes/MyApplication/VehicleMode")
        self.assertEqual(str(event.mode.context_mode_declaration_group_prototype), "/PortInterfaces/VehicleMode_I/mode")
        self.assertEqual(str(event.mode.target_mode_declaration), "/ModeDeclarations/VehicleMode/ACCESSORY")

    def test_create_swc_mode_switch_event_with_transition(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("swc_mode_switch_event_prefix", "MST_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Init")
        event = behavior.create_swc_mode_mode_switch_event("MyApplication_Init",
                                                           ["VehicleMode/PARKING", "VehicleMode/ACCESSORY"])
        self.assertIsInstance(event, ar_element.SwcModeSwitchEvent)
        self.assertEqual(event.name, "MST_MyApplication_Init",)
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Init")
        self.assertEqual(str(event.mode[0].context_port), "/ComponentTypes/MyApplication/VehicleMode")
        self.assertEqual(str(event.mode[0].context_mode_declaration_group_prototype),
                         "/PortInterfaces/VehicleMode_I/mode")
        self.assertEqual(str(event.mode[0].target_mode_declaration), "/ModeDeclarations/VehicleMode/PARKING")
        self.assertEqual(str(event.mode[1].context_port), "/ComponentTypes/MyApplication/VehicleMode")
        self.assertEqual(str(event.mode[1].context_mode_declaration_group_prototype),
                         "/PortInterfaces/VehicleMode_I/mode")
        self.assertEqual(str(event.mode[1].target_mode_declaration), "/ModeDeclarations/VehicleMode/ACCESSORY")

    def test_create_timing_event_without_offset(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("timing_event_prefix", "TMT_")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Run")
        event = behavior.create_timing_event("MyApplication_Run", 0.02)
        self.assertIsInstance(event, ar_element.TimingEvent)
        self.assertEqual(event.name, "TMT_MyApplication_Run")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Run")
        self.assertAlmostEqual(event.period, 0.02)
        self.assertIsNone(event.offset)


if __name__ == '__main__':
    unittest.main()
