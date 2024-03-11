"""Unit tests for programmatically building components and save them as XML"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
from typing import Any
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.element as ar_element # noqa E402
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
                         "ComponentTypes"],
                    workspace.make_packages("AUTOSAR_Platform/BaseTypes",
                                            "AUTOSAR_Platform/ImplementationDataTypes",
                                            "AUTOSAR_Platform/DataConstraints",
                                            "AUTOSAR_Platform/CompuMethods",
                                            "Constants",
                                            "PortInterfaces",
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


def create_vehicle_speed_interface(packages: dict[str, ar_element.Package]) -> ar_element.SenderReceiverInterface:
    """
    Create sender-receiver port interfaces used in example
    """
    uint16_impl_t = packages["PlatformImplementationDataTypes"].find("uint16")
    port_interface = ar_element.SenderReceiverInterface("VehicleSpeed_I")
    port_interface.create_data_element("VehicleSpeed", type_ref=uint16_impl_t.ref())
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


if __name__ == '__main__':
    unittest.main()
