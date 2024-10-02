"""Unit tests for workspace"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.workspace as ar_workspace # noqa E402
import autosar.xml.enumeration as ar_enum  # noqa E402
import autosar.xml.element as ar_element  # noqa E402


class NamespaceTests(unittest.TestCase):

    def test_create_without_base_ref(self):
        namespace = ar_workspace.Namespace("AUTOSAR_Platform", package_map={
            "BaseType": "BaseTypes",
            "ImplementationDataType": "ImplementationDataTypes",
            "CompuMethod": "CompuMethods",
            "DataConstraint": "DataConstrs"})
        self.assertEqual(namespace.package_map[ar_enum.PackageRole.BASE_TYPE],
                         "/AUTOSAR_Platform/BaseTypes")
        self.assertEqual(namespace.package_map[ar_enum.PackageRole.IMPLEMENTATION_DATA_TYPE],
                         "/AUTOSAR_Platform/ImplementationDataTypes")
        self.assertEqual(namespace.package_map[ar_enum.PackageRole.COMPU_METHOD],
                         "/AUTOSAR_Platform/CompuMethods")
        self.assertEqual(namespace.package_map[ar_enum.PackageRole.DATA_CONSTRAINT],
                         "/AUTOSAR_Platform/DataConstrs")

    def test_create_with_custom_role(self):
        namespace = ar_workspace.Namespace("Custom", package_map={
            "!DataType": "DataTypes",
            "CompuMethod": "/DataTypes/CompuMethods",
            "DataConstraint": "/DataTypes/DataConstrs"}, base_ref="/")
        self.assertEqual(namespace.package_map["DataType"],
                         "/DataTypes")


class WorkspaceTests(unittest.TestCase):

    def create_autosar_namespace(self, workspace: ar_workspace.Workspace):
        workspace.create_namespace("AUTOSAR_Platform", package_map={
            "BaseType": "BaseTypes",
            "ImplementationDataType": "ImplementationDataTypes",
            "CompuMethod": "CompuMethods",
            "DataConstraint": "DataConstrs"})

    def create_autosar_namespace_with_rel_path(self, workspace: ar_workspace.Workspace):
        workspace.create_namespace("AUTOSAR_Platform", package_map={
            "BaseType": "./BaseTypes",
            "ImplementationDataType": "./ImplementationDataTypes",
            "CompuMethod": "./CompuMethods",
            "DataConstraint": "./DataConstrs"})

    def create_namespace_with_custom_role(self, workspace: ar_workspace.Workspace):
        workspace.create_namespace("Custom", package_map={
            "!DataType": "DataTypes",
            "CompuMethod": "/DataTypes/CompuMethods",
            "DataConstraint": "/DataTypes/DataConstrs"}, base_ref="/")

    def test_make_packages_depth1(self):
        workspace = ar_workspace.Workspace()
        package = workspace.make_packages("/AUTOSAR_Platform")
        self.assertIsInstance(package, ar_element.Package)
        self.assertIs(workspace.packages[0], package)
        self.assertEqual(package.name, "AUTOSAR_Platform")

    def test_make_packages_depth2(self):
        workspace = ar_workspace.Workspace()
        package = workspace.make_packages("/AUTOSAR_Platform/BaseTypes")
        self.assertIsInstance(package, ar_element.Package)
        self.assertEqual(package.name, "BaseTypes")

    def test_make_packages_multiple(self):
        workspace = ar_workspace.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes", "DataTypes/ImplementationDataTypes")
        self.assertEqual(len(packages), 2)
        self.assertIsInstance(packages[0], ar_element.Package)
        self.assertEqual(packages[0].name, "BaseTypes")
        self.assertEqual(packages[0].parent.name, "DataTypes")
        self.assertIsInstance(packages[1], ar_element.Package)
        self.assertEqual(packages[1].name, "ImplementationDataTypes")
        self.assertEqual(packages[1].parent.name, "DataTypes")

    def test_find_package_depth1(self):
        workspace = ar_workspace.Workspace()
        workspace.make_packages("/AUTOSAR_Platform/BaseTypes")
        package = workspace.find("/AUTOSAR_Platform")
        self.assertIsInstance(package, ar_element.Package)
        self.assertEqual(package.name, "AUTOSAR_Platform")

    def test_find_package_depth2(self):
        workspace = ar_workspace.Workspace()
        workspace.make_packages("/AUTOSAR_Platform/BaseTypes")
        package = workspace.find("/AUTOSAR_Platform/BaseTypes")
        self.assertIsInstance(package, ar_element.Package)
        self.assertEqual(package.name, "BaseTypes")

    def test_create_namespace(self):
        workspace = ar_workspace.Workspace()
        self.create_autosar_namespace(workspace)
        self.assertIsInstance(workspace.namespaces["AUTOSAR_Platform"], ar_workspace.Namespace)

    def test_create_namespace_with_custom_roles(self):
        workspace = ar_workspace.Workspace()
        self.create_namespace_with_custom_role(workspace)
        self.assertIsInstance(workspace.namespaces["Custom"], ar_workspace.Namespace)

    def test_get_package_ref_by_role(self):
        workspace = ar_workspace.Workspace()
        self.create_autosar_namespace(workspace)
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.BASE_TYPE),
            "/AUTOSAR_Platform/BaseTypes")
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.IMPLEMENTATION_DATA_TYPE),
            "/AUTOSAR_Platform/ImplementationDataTypes")
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.COMPU_METHOD),
            "/AUTOSAR_Platform/CompuMethods")
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.DATA_CONSTRAINT),
            "/AUTOSAR_Platform/DataConstrs")

    def test_get_package_ref_by_role_from_rel_paths(self):
        workspace = ar_workspace.Workspace()
        self.create_autosar_namespace_with_rel_path(workspace)
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.BASE_TYPE),
            "/AUTOSAR_Platform/BaseTypes")
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.IMPLEMENTATION_DATA_TYPE),
            "/AUTOSAR_Platform/ImplementationDataTypes")
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.COMPU_METHOD),
            "/AUTOSAR_Platform/CompuMethods")
        self.assertEqual(
            workspace.get_package_ref_by_role("AUTOSAR_Platform", ar_enum.PackageRole.DATA_CONSTRAINT),
            "/AUTOSAR_Platform/DataConstrs")

    def test_get_package_ref_by_role_with_custom_role(self):
        workspace = ar_workspace.Workspace()
        self.create_namespace_with_custom_role(workspace)
        self.assertEqual(
            workspace.get_package_ref_by_role("Custom", "DataType"),
            "/DataTypes")


class BehaviorSettingsTests(unittest.TestCase):

    def test_background_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("background_event_prefix", "BT_")
        self.assertEqual(workspace.behavior_settings.background_event_prefix, "BT_")

    def test_data_receive_error_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("data_receive_error_event_prefix", "DRET_")
        self.assertEqual(workspace.behavior_settings.data_receive_error_event_prefix, "DRET_")

    def test_data_receive_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("data_receive_event_prefix", "DRT_")
        self.assertEqual(workspace.behavior_settings.data_receive_event_prefix, "DRT_")

    def test_init_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("init_event_prefix", "IT_")
        self.assertEqual(workspace.behavior_settings.init_event_prefix, "IT_")

    def test_operation_invoked_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("operation_invoked_event_prefix", "OIT_")
        self.assertEqual(workspace.behavior_settings.operation_invoked_event_prefix, "OIT_")

    def test_swc_mode_manager_error_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("swc_mode_manager_error_event_prefix", "MMET_")
        self.assertEqual(workspace.behavior_settings.swc_mode_manager_error_event_prefix, "MMET_")

    def test_swc_mode_switch_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("swc_mode_switch_event_prefix", "MST_")
        self.assertEqual(workspace.behavior_settings.swc_mode_switch_event_prefix, "MST_")

    def test_timing_event_prefix(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.set_value("timing_event_prefix", "TMT_")
        self.assertEqual(workspace.behavior_settings.timing_event_prefix, "TMT_")

    def test_set_multiple(self):
        workspace = ar_workspace.Workspace()
        workspace.behavior_settings.update({"init_event_prefix": "IT_",
                                            "operation_invoked_event_prefix": "OIT_",
                                            "swc_mode_switch_event_prefix": "MST_",
                                            "timing_event_prefix": "TMT_"})
        self.assertEqual(workspace.behavior_settings.init_event_prefix, "IT_")
        self.assertEqual(workspace.behavior_settings.operation_invoked_event_prefix, "OIT_")
        self.assertEqual(workspace.behavior_settings.swc_mode_switch_event_prefix, "MST_")
        self.assertEqual(workspace.behavior_settings.timing_event_prefix, "TMT_")


if __name__ == '__main__':
    unittest.main()
