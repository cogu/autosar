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
    port_interface = ar_element.ModeSwitchInterface("VehicleMode_I")
    port_interface.create_mode_group("mode", mode_declaration_group.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_application_mode_interface(packages: dict[str, ar_element.Package]) -> ar_element.ModeSwitchInterface:
    """
    Create mode switch interface
    """
    mode_declaration_group = packages["ModeDeclarations"].find("ApplicationMode")
    port_interface = ar_element.ModeSwitchInterface("ApplicationMode_I")
    port_interface.create_mode_group("mode", mode_declaration_group.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_check_point_interface(packages: dict[str, ar_element.Package]) -> ar_element.ClientServerInterface:
    """
    Creates a simple client-server interface
    """
    uint32_impl_t = packages["PlatformImplementationDataTypes"].find("uint32")
    port_interface = ar_element.ClientServerInterface("AliveSupervision_I")
    packages["PortInterfaces"].append(port_interface)
    operation = port_interface.create_operation("CheckPointReached")
    operation.create_in_argument("id", type_ref=uint32_impl_t.ref())
    return port_interface


def create_timer_interface(packages: dict[str, ar_element.Package]) -> ar_element.ClientServerInterface:
    """
    Creates client server interface FreeRunningTimer_I
    """
    uint32_impl_t = packages["PlatformImplementationDataTypes"].find("uint32")
    boolean_impl_t = packages["PlatformImplementationDataTypes"].find("boolean")
    port_interface = ar_element.ClientServerInterface("FreeRunningTimer_I")
    packages["PortInterfaces"].append(port_interface)
    operation = port_interface.create_operation("GetTime")
    operation.create_out_argument("value",
                                  server_arg_impl_policy=ar_enum.ServerArgImplPolicy.USE_ARGUMENT_TYPE,
                                  type_ref=uint32_impl_t.ref())
    operation = port_interface.create_operation("IsTimerElapsed")
    operation.create_in_argument("startTime", type_ref=uint32_impl_t.ref())
    operation.create_in_argument("duration", type_ref=uint32_impl_t.ref())
    operation.create_out_argument("result", type_ref=boolean_impl_t.ref())
    return port_interface


def create_stored_data_interface(packages: dict[str, ar_element.Package]) -> ar_element.NvDataInterface:
    """
    Create non-volatile data interface
    """
    uint8_impl_t = packages["PlatformImplementationDataTypes"].find("uint8")
    port_interface = ar_element.NvDataInterface("StoredData_I")
    port_interface.create_data_element("Value", type_ref=uint8_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_parameter_interface(packages: dict[str, ar_element.Package]) -> ar_element.ParameterInterface:
    """
    Create non-volatile data interface
    """
    uint8_impl_t = packages["PlatformImplementationDataTypes"].find("uint8")
    port_interface = ar_element.ParameterInterface("Calibration_I")
    port_interface.create_parameter("p1", type_ref=uint8_impl_t.ref())
    port_interface.create_parameter("p2", type_ref=uint8_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_actuator_interface(packages: dict[str, ar_element.Package]) -> ar_element.SenderReceiverInterface:
    """
    Create sender-receiver port interface containing two generic data elements.
    The interface is just nonsense. The purpose is to test multi-element ports.
    """
    uint16_impl_t = packages["PlatformImplementationDataTypes"].find("uint16")
    uint8_impl_t = packages["PlatformImplementationDataTypes"].find("uint8")
    port_interface = ar_element.SenderReceiverInterface("Actuator_I")
    port_interface.create_data_element("Primary", type_ref=uint16_impl_t.ref())
    port_interface.create_data_element("Secondary", type_ref=uint8_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


def create_sensor_interface(packages: dict[str, ar_element.Package]) -> ar_element.SenderReceiverInterface:
    """
    Create sender-receiver port interface containing sensor-related data elements.
    The interface is just nonsense. The purpose is to test multi-element ports.
    """
    uint32_impl_t = packages["PlatformImplementationDataTypes"].find("uint32")
    uint16_impl_t = packages["PlatformImplementationDataTypes"].find("uint16")
    port_interface = ar_element.SenderReceiverInterface("Sensor_I")
    port_interface.create_data_element("Sensor1", type_ref=uint32_impl_t.ref())
    port_interface.create_data_element("Sensor2", type_ref=uint16_impl_t.ref())
    packages["PortInterfaces"].append(port_interface)
    return port_interface


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


class TestEventCreationAPI(unittest.TestCase):

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
        alive_supervision_interface = create_check_point_interface(packages)
        swc = create_application_swc(packages)
        swc.create_r_port("EngineSpeed", engine_speed_interface, com_spec={'init_value': 65535})
        swc.create_r_port("VehicleMode", vehicle_mode_interface, com_spec={'supports_async': False})
        swc.create_p_port("ApplicationMode", application_mode_interface)
        swc.create_p_port("AliveSupervision", alive_supervision_interface)
        return swc

    def test_create_background_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("background_event_prefix", "BT")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Background")
        event = behavior.create_background_event("MyApplication_Background")
        self.assertIsInstance(event, ar_element.BackgroundEvent)
        self.assertEqual(event.name, "BT_MyApplication_Background")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Background")

    def test_create_data_receive_error_event_using_port_name_only(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_error_event_prefix", "DRET")
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
        workspace.behavior_settings.set_value("data_receive_error_event_prefix", "DRET")
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
        workspace.behavior_settings.set_value("data_receive_event_prefix", "DRT")
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
        workspace.behavior_settings.set_value("data_receive_event_prefix", "DRT")
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
        workspace.behavior_settings.set_value("init_event_prefix", "IT")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Init")
        event = behavior.create_init_event("MyApplication_Init")
        self.assertIsInstance(event, ar_element.InitEvent)
        self.assertEqual(event.name, "IT_MyApplication_Init")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Init")

    def test_create_operation_invoked_event_port_name_only(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("operation_invoked_event_prefix", "OIT")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_CheckPointReached")
        event = behavior.create_operation_invoked_event("MyApplication_CheckPointReached", "AliveSupervision")
        self.assertIsInstance(event, ar_element.OperationInvokedEvent)
        self.assertEqual(event.name, "OIT_MyApplication_CheckPointReached_AliveSupervision_CheckPointReached")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_CheckPointReached")
        self.assertEqual(str(event.operation.context_port), "/ComponentTypes/MyApplication/AliveSupervision")
        self.assertEqual(str(event.operation.target_provided_operation),
                         "/PortInterfaces/AliveSupervision_I/CheckPointReached")

    def test_create_operation_invoked_event_with_operation_name(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("operation_invoked_event_prefix", "OIT")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_CheckPointReached")
        event = behavior.create_operation_invoked_event("MyApplication_CheckPointReached",
                                                        "AliveSupervision/CheckPointReached")
        self.assertIsInstance(event, ar_element.OperationInvokedEvent)
        self.assertEqual(event.name, "OIT_MyApplication_CheckPointReached_AliveSupervision_CheckPointReached")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_CheckPointReached")
        self.assertEqual(str(event.operation.context_port), "/ComponentTypes/MyApplication/AliveSupervision")
        self.assertEqual(str(event.operation.target_provided_operation),
                         "/PortInterfaces/AliveSupervision_I/CheckPointReached")

    def test_create_swc_mode_manager_error_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("swc_mode_manager_error_event_prefix", "MMET")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_ApplicationModeError")
        event = behavior.create_swc_mode_manager_error_event("MyApplication_ApplicationModeError", "ApplicationMode")
        self.assertIsInstance(event, ar_element.SwcModeManagerErrorEvent)
        self.assertEqual(event.name, "MMET_MyApplication_ApplicationModeError_ApplicationMode_mode",)
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_ApplicationModeError")
        self.assertEqual(str(event.mode_group.context_port), "/ComponentTypes/MyApplication/ApplicationMode")
        self.assertEqual(str(event.mode_group.target_mode_group),
                         "/PortInterfaces/ApplicationMode_I/mode")

    def test_create_swc_mode_switch_event(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("swc_mode_switch_event_prefix", "MST")
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
        workspace.behavior_settings.set_value("swc_mode_switch_event_prefix", "MST")
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

    def test_create_multiple_swc_mode_switch_events_with_same_base_name(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("swc_mode_switch_event_prefix", "MST")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Init")
        event1 = behavior.create_swc_mode_mode_switch_event("MyApplication_Init",
                                                            "VehicleMode/ACCESSORY",
                                                            ar_enum.ModeActivationKind.ON_ENTRY)
        event2 = behavior.create_swc_mode_mode_switch_event("MyApplication_Init",
                                                            "VehicleMode/PARKING",
                                                            ar_enum.ModeActivationKind.ON_ENTRY)
        event3 = behavior.create_swc_mode_mode_switch_event("MyApplication_Init",
                                                            "VehicleMode/RUNNING",
                                                            ar_enum.ModeActivationKind.ON_ENTRY)

        self.assertIsInstance(event1, ar_element.SwcModeSwitchEvent)
        self.assertIsInstance(event2, ar_element.SwcModeSwitchEvent)
        self.assertIsInstance(event3, ar_element.SwcModeSwitchEvent)
        self.assertEqual(event1.name, "MST_MyApplication_Init_0",)
        self.assertEqual(event2.name, "MST_MyApplication_Init_1",)
        self.assertEqual(event3.name, "MST_MyApplication_Init_2",)
        self.assertEqual(str(event1.mode.target_mode_declaration), "/ModeDeclarations/VehicleMode/ACCESSORY")
        self.assertEqual(str(event2.mode.target_mode_declaration), "/ModeDeclarations/VehicleMode/PARKING")
        self.assertEqual(str(event3.mode.target_mode_declaration), "/ModeDeclarations/VehicleMode/RUNNING")

    def test_create_timing_event_without_offset(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("timing_event_prefix", "TMT")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_runnable("MyApplication_Run")
        event = behavior.create_timing_event("MyApplication_Run", 0.02)
        self.assertIsInstance(event, ar_element.TimingEvent)
        self.assertEqual(event.name, "TMT_MyApplication_Run")
        self.assertEqual(str(event.start_on_event), self.expected_behavior_ref + "/MyApplication_Run")
        self.assertAlmostEqual(event.period, 0.02)
        self.assertIsNone(event.offset)


class TestRunnableEntityAPI(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        create_mode_declaration_groups(packages)
        vehicle_speed_interface = create_vehicle_speed_interface(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        safe_state_interface = create_safe_state_interface(packages)
        data_interface = create_stored_data_interface(packages)
        parameter_interface = create_parameter_interface(packages)
        actuator_interface = create_actuator_interface(packages)
        sensor_interface = create_sensor_interface(packages)
        vehicle_mode_interface = create_vehicle_mode_interface(packages)
        application_mode_interface = create_application_mode_interface(packages)
        timer_interface = create_timer_interface(packages)

        swc = create_application_swc(packages)
        swc.create_p_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": 65535})
        swc.create_r_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": 65535})
        swc.create_r_port("StoredData", data_interface)
        swc.create_r_port("CalibrationData", parameter_interface)
        swc.create_r_port("Timer", timer_interface)
        swc.create_p_port("Actuator", actuator_interface, com_spec=[("Primary", {"init_value": 65535}),
                                                                    ("Secondary", {"init_value": 255})])
        swc.create_r_port("Sensor", sensor_interface, com_spec=[("Sensor1", {"init_value": (2 ** 32) - 1}),
                                                                ("Sensor2", {"init_value": 65535})])
        swc.create_pr_port("SafeState", safe_state_interface, provided_com_spec={"init_value": False})
        swc.create_r_port("VehicleMode", vehicle_mode_interface, com_spec={'supports_async': False})
        swc.create_p_port("ApplicationMode", application_mode_interface)

        return swc

    def test_create_data_read_access(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_read_access_prefix", "READ")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["READ: EngineSpeed",
                                     "READ: Sensor/Sensor2"])

        self.assertEqual(len(runnable.data_read_access), 2)
        child: ar_element.VariableAccess = runnable.data_read_access[0]
        self.assertEqual(child.name, "READ_EngineSpeed_EngineSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/EngineSpeed_I/EngineSpeed")
        child = runnable.data_read_access[1]
        self.assertEqual(child.name, "READ_Sensor_Sensor2")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/Sensor")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/Sensor_I/Sensor2")

    def test_create_default_data_receive_point_sender_receiver(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_point_prefix", "REC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["EngineSpeed", "Sensor/Sensor1"])

        self.assertEqual(len(runnable.data_receive_point_by_argument), 2)
        child: ar_element.VariableAccess = runnable.data_receive_point_by_argument[0]
        self.assertEqual(child.name, "REC_EngineSpeed_EngineSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/EngineSpeed_I/EngineSpeed")
        child = runnable.data_receive_point_by_argument[1]
        self.assertEqual(child.name, "REC_Sensor_Sensor1")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/Sensor")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/Sensor_I/Sensor1")

    def test_create_data_receive_point_by_argument_sender_receiver(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_point_prefix", "REC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["ARG:EngineSpeed", "ARGUMENT:Sensor/Sensor1"])

        self.assertEqual(len(runnable.data_receive_point_by_argument), 2)
        child: ar_element.VariableAccess = runnable.data_receive_point_by_argument[0]
        self.assertEqual(child.name, "REC_EngineSpeed_EngineSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/EngineSpeed_I/EngineSpeed")
        child = runnable.data_receive_point_by_argument[1]
        self.assertEqual(child.name, "REC_Sensor_Sensor1")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/Sensor")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/Sensor_I/Sensor1")

    def test_create_data_receive_point_by_value_sender_receiver(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_point_prefix", "REC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["VAL: EngineSpeed",
                                     "VALUE: Sensor/Sensor1"])

        self.assertEqual(len(runnable.data_receive_point_by_value), 2)
        child: ar_element.VariableAccess = runnable.data_receive_point_by_value[0]
        self.assertEqual(child.name, "REC_EngineSpeed_EngineSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/EngineSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/EngineSpeed_I/EngineSpeed")
        child = runnable.data_receive_point_by_value[1]
        self.assertEqual(child.name, "REC_Sensor_Sensor1")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/Sensor")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/Sensor_I/Sensor1")

    def test_create_data_receive_point_with_ambiguous_element_name(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_point_prefix", "REC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        with self.assertRaises(RuntimeError):
            # Ambiguous name, the port interface has multiple data elements and giving just the port name shall
            # raise an exception
            runnable.create_port_access("ARG:Sensor")
            runnable.create_port_access("READ:Sensor")

    def test_create_data_receive_point_by_argument_from_nv_data(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_point_prefix", "REC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access("StoredData/Value")

        self.assertEqual(len(runnable.data_receive_point_by_argument), 1)
        child: ar_element.VariableAccess = runnable.data_receive_point_by_argument[0]
        self.assertEqual(child.name, "REC_StoredData_Value")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/StoredData")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/StoredData_I/Value")

    def test_create_data_receive_point_by_argument_from_nv_data_with_extra_args(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_receive_point_prefix", "REC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(("StoredData/Value", {"desc": "MyDescription"}))

        self.assertEqual(len(runnable.data_receive_point_by_argument), 1)
        child: ar_element.VariableAccess = runnable.data_receive_point_by_argument[0]
        self.assertEqual(child.name, "REC_StoredData_Value")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/StoredData")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/StoredData_I/Value")
        self.assertEqual(child.desc.elements[0].parts[0], "MyDescription")

    def test_create_data_send_from_sender_receiver(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_send_point_prefix", "SEND")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["VehicleSpeed", "Actuator/Primary"])

        self.assertEqual(len(runnable.data_send_point), 2)
        child: ar_element.VariableAccess = runnable.data_send_point[0]
        self.assertEqual(child.name, "SEND_VehicleSpeed_VehicleSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/VehicleSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/VehicleSpeed_I/VehicleSpeed")
        child = runnable.data_send_point[1]
        self.assertEqual(child.name, "SEND_Actuator_Primary")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/Actuator")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/Actuator_I/Primary")

    def test_create_data_send_from_sender_receiver_with_extra_args(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_send_point_prefix", "SEND")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        access_args = {"scope": ar_enum.VariableAccessScope.COMMUNICATION_INTRA_PARTITION}
        runnable.create_port_access(("VehicleSpeed", access_args))

        self.assertEqual(len(runnable.data_send_point), 1)
        child: ar_element.VariableAccess = runnable.data_send_point[0]
        self.assertEqual(child.name, "SEND_VehicleSpeed_VehicleSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/VehicleSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/VehicleSpeed_I/VehicleSpeed")
        self.assertEqual(child.scope, ar_enum.VariableAccessScope.COMMUNICATION_INTRA_PARTITION)

    def test_create_data_write_access_from_sender_receiver(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("data_write_access_prefix", "WRITE")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["WRITE:VehicleSpeed", "WRITE:Actuator/Primary"])

        self.assertEqual(len(runnable.data_write_access), 2)
        child: ar_element.VariableAccess = runnable.data_write_access[0]
        self.assertEqual(child.name, "WRITE_VehicleSpeed_VehicleSpeed")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/VehicleSpeed")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/VehicleSpeed_I/VehicleSpeed")
        child = runnable.data_write_access[1]
        self.assertEqual(child.name, "WRITE_Actuator_Primary")
        variable = child.accessed_variable.ar_variable_iref
        self.assertEqual(str(variable.port_prototype_ref), "/ComponentTypes/MyApplication/Actuator")
        self.assertEqual(str(variable.target_data_prototype_ref), "/PortInterfaces/Actuator_I/Primary")

    # # TODO: implement unit test for external_triggering_point and internal_triggering_point

    def test_create_default_mode_access_point(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["VehicleMode", "ApplicationMode"])
        self.assertEqual(len(runnable.mode_access_point), 2)
        child: ar_element.ModeAccessPoint = runnable.mode_access_point[0]
        self.assertIsNone(child.ident)
        r_mode_group: ar_element.RModeGroupInAtomicSwcInstanceRef = child.mode_group
        self.assertIsInstance(r_mode_group, ar_element.RModeGroupInAtomicSwcInstanceRef)
        self.assertEqual(str(r_mode_group.context_port), "/ComponentTypes/MyApplication/VehicleMode")
        self.assertEqual(str(r_mode_group.target_mode_group), "/PortInterfaces/VehicleMode_I/mode")
        child: ar_element.ModeAccessPoint = runnable.mode_access_point[1]
        self.assertIsNone(child.ident)
        p_mode_group: ar_element.PModeGroupInAtomicSwcInstanceRef = child.mode_group
        self.assertIsInstance(p_mode_group, ar_element.PModeGroupInAtomicSwcInstanceRef)
        self.assertEqual(str(p_mode_group.context_port), "/ComponentTypes/MyApplication/ApplicationMode")
        self.assertEqual(str(p_mode_group.target_mode_group), "/PortInterfaces/ApplicationMode_I/mode")

    def test_create_named_mode_access_point(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("mode_access_point_prefix", "ACCESS")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["ACCESS:VehicleMode", "ACCESS:ApplicationMode"])
        self.assertEqual(len(runnable.mode_access_point), 2)
        child: ar_element.ModeAccessPoint = runnable.mode_access_point[0]
        self.assertEqual(child.ident.name, "ACCESS_VehicleMode_mode")
        r_mode_group: ar_element.RModeGroupInAtomicSwcInstanceRef = child.mode_group
        self.assertIsInstance(r_mode_group, ar_element.RModeGroupInAtomicSwcInstanceRef)
        self.assertEqual(str(r_mode_group.context_port), "/ComponentTypes/MyApplication/VehicleMode")
        self.assertEqual(str(r_mode_group.target_mode_group), "/PortInterfaces/VehicleMode_I/mode")
        child: ar_element.ModeAccessPoint = runnable.mode_access_point[1]
        self.assertEqual(child.ident.name, "ACCESS_ApplicationMode_mode")
        p_mode_group: ar_element.PModeGroupInAtomicSwcInstanceRef = child.mode_group
        self.assertIsInstance(p_mode_group, ar_element.PModeGroupInAtomicSwcInstanceRef)
        self.assertEqual(str(p_mode_group.context_port), "/ComponentTypes/MyApplication/ApplicationMode")
        self.assertEqual(str(p_mode_group.target_mode_group), "/PortInterfaces/ApplicationMode_I/mode")

    def test_create_mode_switch_point(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("mode_switch_point_prefix", "SWITCH")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access("SWITCH:ApplicationMode")
        self.assertEqual(len(runnable.mode_switch_point), 1)
        child: ar_element.ModeSwitchPoint = runnable.mode_switch_point[0]
        self.assertEqual(child.name, "SWITCH_ApplicationMode_mode")
        mode_group: ar_element.PModeGroupInAtomicSwcInstanceRef = child.mode_group
        self.assertIsInstance(mode_group, ar_element.PModeGroupInAtomicSwcInstanceRef)
        self.assertEqual(str(mode_group.context_port), "/ComponentTypes/MyApplication/ApplicationMode")
        self.assertEqual(str(mode_group.target_mode_group), "/PortInterfaces/ApplicationMode_I/mode")

    def test_create_mode_switch_point_extra_args(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("mode_switch_point_prefix", "SWITCH")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        access_point_args = {"return_value_provision": ar_enum.RteApiReturnValueProvision.RETURN_VALUE_PROVIDED}
        runnable.create_port_access(("SWITCH:ApplicationMode", access_point_args))
        self.assertEqual(len(runnable.mode_switch_point), 1)
        child: ar_element.ModeSwitchPoint = runnable.mode_switch_point[0]
        self.assertEqual(child.name, "SWITCH_ApplicationMode_mode")
        mode_group: ar_element.PModeGroupInAtomicSwcInstanceRef = child.mode_group
        self.assertIsInstance(mode_group, ar_element.PModeGroupInAtomicSwcInstanceRef)
        self.assertEqual(str(mode_group.context_port), "/ComponentTypes/MyApplication/ApplicationMode")
        self.assertEqual(str(mode_group.target_mode_group), "/PortInterfaces/ApplicationMode_I/mode")
        self.assertEqual(child.return_value_provision, ar_enum.RteApiReturnValueProvision.RETURN_VALUE_PROVIDED)

    def test_parameter_access(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("parameter_access_prefix", "PRM")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        runnable.create_port_access(["CalibrationData/p1", "CalibrationData/p2"])
        self.assertEqual(len(runnable.parameter_access), 2)
        child: ar_element.ParameterAccess = runnable.parameter_access[0]
        self.assertEqual(child.name, "PRM_CalibrationData_p1")
        parameter = child.accessed_parameter.autosar_parameter
        self.assertEqual(str(parameter.port_prototype), "/ComponentTypes/MyApplication/CalibrationData")
        self.assertEqual(str(parameter.target_data_prototype), "/PortInterfaces/Calibration_I/p1")
        child = runnable.parameter_access[1]
        self.assertEqual(child.name, "PRM_CalibrationData_p2")
        parameter = child.accessed_parameter.autosar_parameter
        self.assertEqual(str(parameter.port_prototype), "/ComponentTypes/MyApplication/CalibrationData")
        self.assertEqual(str(parameter.target_data_prototype), "/PortInterfaces/Calibration_I/p2")

    def test_parameter_access_with_extra_args(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("parameter_access_prefix", "PRM")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        sw_data_def_props = ar_element.SwDataDefPropsConditional(sw_addr_method_ref="/SWADDR/Protected")
        runnable.create_port_access(("CalibrationData/p1", {"sw_data_def_props": sw_data_def_props}))
        self.assertEqual(len(runnable.parameter_access), 1)
        child: ar_element.ParameterAccess = runnable.parameter_access[0]
        self.assertEqual(child.name, "PRM_CalibrationData_p1")
        parameter = child.accessed_parameter.autosar_parameter
        self.assertEqual(str(parameter.port_prototype), "/ComponentTypes/MyApplication/CalibrationData")
        self.assertEqual(str(parameter.target_data_prototype), "/PortInterfaces/Calibration_I/p1")
        self.assertEqual(str(child.sw_data_def_props.variants[0].sw_addr_method_ref), "/SWADDR/Protected")

    def test_server_call_point(self):
        """
        This also tests adding additional arguments using tuples
        """
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("server_call_point_prefix", "SC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run")
        exclusive_are_ref = ar_element.ExclusiveAreaNestingOrderRef("/ComponentTypes/MyApplication/MyExclusiveArea")
        runnable.create_port_access([("SYNC:Timer/GetTime",
                                      {"timeout": 0.0, "called_from_within_exclusive_area": exclusive_are_ref}),
                                     ("ASYNC:Timer/IsTimerElapsed", {"timeout": 1.0})])

        self.assertEqual(len(runnable.server_call_point), 2)
        child: ar_element.SynchronousServerCallPoint = runnable.server_call_point[0]
        self.assertIsInstance(child, ar_element.SynchronousServerCallPoint)
        self.assertEqual(child.name, "SC_Timer_GetTime")
        operation = child.operation
        self.assertEqual(str(operation.context_port), "/ComponentTypes/MyApplication/Timer")
        self.assertEqual(str(operation.target_required_operation), "/PortInterfaces/FreeRunningTimer_I/GetTime")
        self.assertEqual(child.timeout, 0)
        self.assertEqual(str(child.called_from_within_exclusive_area), str(exclusive_are_ref))
        child = runnable.server_call_point[1]
        self.assertIsInstance(child, ar_element.AsynchronousServerCallPoint)
        self.assertEqual(child.name, "SC_Timer_IsTimerElapsed")
        operation = child.operation
        self.assertEqual(str(operation.context_port), "/ComponentTypes/MyApplication/Timer")
        self.assertEqual(str(operation.target_required_operation), "/PortInterfaces/FreeRunningTimer_I/IsTimerElapsed")
        self.assertAlmostEqual(child.timeout, 1.0)

    def test_custom_symbol(self):
        workspace = autosar.xml.Workspace()
        workspace.behavior_settings.set_value("server_call_point_prefix", "SC")
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        runnable = behavior.create_runnable("MyApplication_Run", symbol="Run")
        self.assertEqual(runnable.symbol, "Run")


class TestPortAPIOptionAPI(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        create_mode_declaration_groups(packages)
        vehicle_speed_interface = create_vehicle_speed_interface(packages)
        engine_speed_interface = create_engine_speed_interface(packages)
        safe_state_interface = create_safe_state_interface(packages)
        data_interface = create_stored_data_interface(packages)
        parameter_interface = create_parameter_interface(packages)
        actuator_interface = create_actuator_interface(packages)
        sensor_interface = create_sensor_interface(packages)
        vehicle_mode_interface = create_vehicle_mode_interface(packages)
        application_mode_interface = create_application_mode_interface(packages)
        timer_interface = create_timer_interface(packages)

        swc = create_application_swc(packages)
        swc.create_p_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": 65535})
        swc.create_r_port("EngineSpeed", engine_speed_interface, com_spec={"init_value": 65535})
        swc.create_r_port("StoredData", data_interface)
        swc.create_r_port("CalibrationData", parameter_interface)
        swc.create_r_port("Timer", timer_interface)
        swc.create_p_port("Actuator", actuator_interface, com_spec=[("Primary", {"init_value": 65535}),
                                                                    ("Secondary", {"init_value": 255})])
        swc.create_r_port("Sensor", sensor_interface, com_spec=[("Sensor1", {"init_value": (2 ** 32) - 1}),
                                                                ("Sensor2", {"init_value": 65535})])
        swc.create_pr_port("SafeState", safe_state_interface, provided_com_spec={"init_value": False})
        swc.create_r_port("VehicleMode", vehicle_mode_interface, com_spec={'supports_async': False})
        swc.create_p_port("ApplicationMode", application_mode_interface)

        return swc

    def test_create_options_for_all(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_port_api_options("*", enable_take_address=True, indirect_api=True)
        self.assertEqual(len(behavior.port_api_options), 10)
        options: ar_element.PortApiOption
        for options in behavior.port_api_options.values():
            self.assertTrue(options.enable_take_address)
            self.assertTrue(options.indirect_api)

    def test_create_options_for_single_port(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_port_api_options("VehicleSpeed", enable_take_address=True, indirect_api=True)
        self.assertEqual(len(behavior.port_api_options), 1)
        options = behavior.port_api_options["VehicleSpeed"]
        self.assertIsInstance(options, ar_element.PortApiOption)
        self.assertTrue(options.enable_take_address)
        self.assertTrue(options.indirect_api)

    def test_create_options_for_invalid_port_name(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        with self.assertRaises(ValueError):
            behavior.create_port_api_options("VehicleSpeeds", enable_take_address=True, indirect_api=True)

    def test_create_default_options_then_modify_existing(self):
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        behavior.create_port_api_options("*", enable_take_address=False)
        behavior.port_api_options["VehicleSpeed"].enable_take_address = True
        options: ar_element.PortApiOption
        for key, options in behavior.port_api_options.items():
            self.assertIsInstance(options.enable_take_address, bool)
            if key == "VehicleSpeed":
                self.assertTrue(options.enable_take_address)
            else:
                self.assertFalse(options.enable_take_address)


class TestExclusiveAreaAPI(unittest.TestCase):

    def create_swc(self, workspace: autosar.xml.Workspace) -> ar_element.ApplicationSoftwareComponentType:
        packages = create_packages(workspace)
        create_platform_types(packages)
        vehicle_speed_interface = create_vehicle_speed_interface(packages)

        swc = create_application_swc(packages)
        swc.create_p_port("VehicleSpeed", vehicle_speed_interface, com_spec={"init_value": 65535})
        return swc

    def test_create_exclusive_area(self):
        ref_str = "/ComponentTypes/MyApplication/MyApplication_InternalBehavior/MyExclusiveArea"
        workspace = autosar.xml.Workspace()
        swc = self.create_swc(workspace)
        behavior = swc.internal_behavior
        exclusive_area = behavior.create_exclusive_area("MyExclusiveArea")
        runnable = behavior.create_runnable("MyRunnable", can_enter_leave=exclusive_area.ref())
        self.assertEqual(len(runnable.can_enter_leave), 1)
        elem: ar_element.ExclusiveAreaRefConditional = runnable.can_enter_leave[0]
        self.assertIsInstance(elem, ar_element.ExclusiveAreaRefConditional)
        self.assertEqual(str(elem.exclusive_area), ref_str)


if __name__ == '__main__':
    unittest.main()
