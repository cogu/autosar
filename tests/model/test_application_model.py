"""Unit tests for RTE model data types"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.model.element as rte_element  # noqa E402
from autosar.model import Application # noqa E402


class TestBaseType(unittest.TestCase):

    def test_create_from_uint8_platform_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('uint8')
        package.append(base_type)

        # Test
        application = Application(workspace)
        elem: rte_element.BaseType = application.create_from_element(base_type)
        self.assertEqual(elem.name, "uint8")
        self.assertIsNone(elem.native_declaration)

    def test_create_from_custom_uint8_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('MyUint8Base', native_declaration="unsigned char")
        package.append(base_type)

        # Test
        application = Application(workspace)
        elem: rte_element.BaseType = application.create_from_element(base_type)
        self.assertEqual(elem.name, base_type.name)
        self.assertEqual(elem.native_declaration, base_type.native_declaration)


class TestScalarType(unittest.TestCase):

    def test_create_from_custom_uint8_impl_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")

        base_type = ar_element.SwBaseType('MyUint8Base', native_declaration="unsigned char")
        packages[0].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        impl_type = ar_element.ImplementationDataType("MyUint8",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type)

        # Test
        application = Application(workspace)
        elem: rte_element.ScalarType = application.create_from_element(impl_type)
        self.assertIsInstance(elem, rte_element.ScalarType)
        self.assertEqual(elem.name, "MyUint8")
        self.assertIsInstance(elem.base_type, rte_element.BaseType)
        self.assertEqual(elem.base_type.name, "MyUint8Base")
        self.assertEqual(elem.base_type.native_declaration, "unsigned char")


class TestRefType(unittest.TestCase):

    def test_create_from_uint8_impl_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")
        uint8_base_type = ar_element.SwBaseType('uint8', 8)
        packages[0].append(uint8_base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                            category="VALUE",
                                                            sw_data_def_props=sw_data_def_props,
                                                            type_emitter="Platform")
        packages[1].append(uint8_impl_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint8_impl_type.ref())
        impl_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="TYPE_REFERENCE",
                                                      sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type)

        # Test
        application = Application(workspace)
        elem: rte_element.RefType = application.create_from_element(impl_type)
        self.assertIsInstance(elem, rte_element.RefType)
        self.assertEqual(elem.name, "InactiveActive_T")
        self.assertIsInstance(elem.impl_type, rte_element.ScalarType)
        self.assertEqual(elem.impl_type.name, "uint8")
        self.assertEqual(elem.impl_type.type_emitter, "Platform")
        self.assertIsInstance(elem.impl_type.base_type, rte_element.BaseType)
        self.assertEqual(elem.impl_type.base_type.name, "uint8")
        self.assertIsNone(elem.impl_type.base_type.native_declaration)

    def test_gen_type_dependency_tree(self):

        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")
        base_type = ar_element.SwBaseType('uint8', 8)
        packages[0].append(base_type)

        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationDataTypes/InactiveActive_T")
        impl_type1 = ar_element.ImplementationDataType("PowerSwitch_T",
                                                       category="TYPE_REFERENCE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type1)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="DataTypes/BaseTypes/uint8")
        impl_type2 = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type2)

        application = Application(workspace)
        application.create_from_element(impl_type1)

        # Test
        depency_trees = application.gen_type_dependency_trees()
        self.assertEqual(len(depency_trees), 1)
        root = depency_trees[0]
        self.assertEqual(root.data.ref, "/DataTypes/ImplementationDataTypes/PowerSwitch_T")
        self.assertEqual(len(root.children), 1)
        child = root.children[0]
        self.assertEqual(child.data.ref, "/DataTypes/ImplementationDataTypes/InactiveActive_T")
        self.assertEqual(len(child.children), 1)
        grand_child = child.children[0]
        self.assertEqual(grand_child.data.ref, "/DataTypes/BaseTypes/uint8")

    def test_gen_type_dependency_tree_with_more_depth(self):

        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")
        base_type = ar_element.SwBaseType('uint8', 8)
        packages[0].append(base_type)

        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationDataTypes/InactiveActive_T")
        impl_type1 = ar_element.ImplementationDataType("PowerSwitch_T",
                                                       category="TYPE_REFERENCE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type1)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationDataTypes/uint8")
        impl_type2 = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="TYPE_REFERENCE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type2)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="DataTypes/BaseTypes/uint8")
        impl_type3 = ar_element.ImplementationDataType("uint8",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props,
                                                       type_emitter="Platform")
        packages[1].append(impl_type3)

        application = Application(workspace)
        application.create_from_element(impl_type1)

        # Test
        depency_trees = application.gen_type_dependency_trees()
        self.assertEqual(len(depency_trees), 1)
        root = depency_trees[0]
        self.assertEqual(root.data.ref, "/DataTypes/ImplementationDataTypes/PowerSwitch_T")
        self.assertEqual(len(root.children), 1)
        child = root.children[0]
        self.assertEqual(child.data.ref, "/DataTypes/ImplementationDataTypes/InactiveActive_T")
        self.assertEqual(len(child.children), 1)
        grand_child = child.children[0]
        self.assertEqual(grand_child.data.ref, "/DataTypes/ImplementationDataTypes/uint8")
        self.assertEqual(len(grand_child.children), 1)
        ancestor = grand_child.children[0]
        self.assertEqual(ancestor.data.ref, "/DataTypes/BaseTypes/uint8")
        self.assertEqual(len(ancestor.children), 0)

    def test_get_type_creation_order(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")
        base_type = ar_element.SwBaseType('uint8', 8)
        packages[0].append(base_type)

        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationDataTypes/InactiveActive_T")
        impl_type1 = ar_element.ImplementationDataType("PowerSwitch_T",
                                                       category="TYPE_REFERENCE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type1)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="DataTypes/BaseTypes/uint8")
        impl_type2 = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type2)

        application = Application(workspace)
        application.create_from_element(impl_type1)
        # Test
        depency_trees = application.gen_type_dependency_trees()
        creation_order = list(application.get_type_creation_order(depency_trees[0]))
        self.assertEqual(len(creation_order), 3)
        self.assertEqual(creation_order[0].data.name, "uint8")
        self.assertEqual(creation_order[1].data.name, "InactiveActive_T")
        self.assertEqual(creation_order[2].data.name, "PowerSwitch_T")

    def test_get_type_creation_order_with_more_depth(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")
        base_type = ar_element.SwBaseType('uint8', 8)
        packages[0].append(base_type)

        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationDataTypes/InactiveActive_T")
        impl_type1 = ar_element.ImplementationDataType("PowerSwitch_T",
                                                       category="TYPE_REFERENCE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type1)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(
            impl_data_type_ref="/DataTypes/ImplementationDataTypes/uint8")
        impl_type2 = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="TYPE_REFERENCE",
                                                       sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type2)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref="DataTypes/BaseTypes/uint8")
        impl_type3 = ar_element.ImplementationDataType("uint8",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props,
                                                       type_emitter="Platform")
        packages[1].append(impl_type3)

        application = Application(workspace)
        application.create_from_element(impl_type1)

        # Test
        depency_trees = application.gen_type_dependency_trees()
        creation_order = list(application.get_type_creation_order(depency_trees[0]))
        self.assertEqual(len(creation_order), 4)
        self.assertEqual(creation_order[0].data.name, "uint8")
        self.assertIsInstance(creation_order[0].data, rte_element.BaseType)
        self.assertEqual(creation_order[1].data.name, "uint8")
        self.assertIsInstance(creation_order[1].data, rte_element.ScalarType)
        self.assertEqual(creation_order[2].data.name, "InactiveActive_T")
        self.assertIsInstance(creation_order[2].data, rte_element.RefType)
        self.assertEqual(creation_order[3].data.name, "PowerSwitch_T")
        self.assertIsInstance(creation_order[3].data, rte_element.RefType)


if __name__ == '__main__':
    unittest.main()
