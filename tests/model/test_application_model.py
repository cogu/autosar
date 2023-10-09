"""Unit tests for RTE model data types"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from autosar.xml import Workspace  # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.model.element as rte_element  # noqa E402
from autosar.model import Application # noqa E402


class TestBaseType(unittest.TestCase):

    def test_create_from_uint8_platform_base_type(self):
        # Setup
        workspace = Workspace()
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
        workspace = Workspace()
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
        workspace = Workspace()
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
        workspace = Workspace()
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
        workspace = Workspace()
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
        workspace = Workspace()
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
        workspace = Workspace()
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
        workspace = Workspace()
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


class TestArrayDataType(unittest.TestCase):

    def test_create_array_from_scalar_type(self):
        # Setup
        workspace = Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        uint8_base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(uint8_base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement("Element",
                                                               category="VALUE",
                                                               array_size=4,
                                                               sw_data_def_props=sw_data_def_props)
        impl_type = ar_element.ImplementationDataType("U8Array4_T",
                                                      category="ARRAY",
                                                      sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(impl_type)

        # Test
        application = Application(workspace)
        elem: rte_element.ArrayType = application.create_from_element(impl_type)
        self.assertIsInstance(elem, rte_element.ArrayType)
        self.assertEqual(elem.name, "U8Array4_T")
        self.assertEqual(len(elem.sub_elements), 1)
        sub_element = elem.sub_elements[0]
        self.assertIsInstance(sub_element, rte_element.ArrayTypeElement)
        self.assertEqual(sub_element.array_size, 4)
        data_type: rte_element.ScalarType = sub_element.data_type
        self.assertIsInstance(data_type, rte_element.ScalarType)
        self.assertEqual(data_type.base_type.ref, "/DataTypes/BaseTypes/uint8")

    def test_create_array_from_ref_type(self):
        # Setup
        workspace = Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        uint8_base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(uint8_base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        value_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(value_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=value_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement("Element",
                                                               category="TYPE_REFERENCE",
                                                               array_size=2,
                                                               sw_data_def_props=sw_data_def_props)
        ref_type = ar_element.ImplementationDataType("U8Array4_T",
                                                     category="ARRAY",
                                                     sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(ref_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=value_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement("Element",
                                                               category="TYPE_REFERENCE",
                                                               array_size=2,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType("InactiveActiveArray2_T",
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        application = Application(workspace)
        elem: rte_element.ArrayType = application.create_from_element(array_type)
        self.assertIsInstance(elem, rte_element.ArrayType)
        self.assertEqual(elem.name, "InactiveActiveArray2_T")
        self.assertEqual(len(elem.sub_elements), 1)
        sub_element = elem.sub_elements[0]
        self.assertIsInstance(sub_element, rte_element.ArrayTypeElement)
        self.assertEqual(sub_element.array_size, 2)
        data_type: rte_element.RefType = sub_element.data_type
        self.assertIsInstance(data_type, rte_element.RefType)
        impl_type = data_type.impl_type
        self.assertIsInstance(impl_type, rte_element.ScalarType)
        self.assertEqual(impl_type.name, "InactiveActive_T")
        self.assertIsInstance(impl_type.base_type, rte_element.BaseType)
        self.assertEqual(impl_type.base_type.name, "uint8")


class TestStructDataType(unittest.TestCase):

    def test_create_struct_from_scalar_types(self):
        # Setup
        workspace = Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        uint8_base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(uint8_base_type)

        uint32_base_type = ar_element.SwBaseType("uint32")
        packages["BaseTypes"].append(uint32_base_type)

        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        elem1 = ar_element.ImplementationDataTypeElement("Elem1",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint32_base_type.ref())
        elem2 = ar_element.ImplementationDataTypeElement("Elem2",
                                                         category="VALUE",
                                                         sw_data_def_props=sw_data_def_props)
        struct_type = ar_element.ImplementationDataType("StructType_T",
                                                        category="STRUCTURE",
                                                        sub_elements=[elem1, elem2])
        packages["ImplementationDataTypes"].append(struct_type)

        # Test
        model = Application(workspace)
        elem: rte_element.StructType = model.create_from_element(struct_type)
        self.assertIsInstance(elem, rte_element.StructType)
        self.assertEqual(elem.name, "StructType_T")
        self.assertEqual(len(elem.sub_elements), 2)
        sub_element = elem.sub_elements[0]
        self.assertEqual(sub_element.name, "Elem1")
        self.assertIsInstance(sub_element, rte_element.StructTypeElement)
        data_type: rte_element.ScalarType = sub_element.data_type
        self.assertIsInstance(data_type, rte_element.ScalarType)
        self.assertEqual(data_type.base_type.ref, "/DataTypes/BaseTypes/uint8")
        sub_element = elem.sub_elements[1]
        self.assertEqual(sub_element.name, "Elem2")
        self.assertIsInstance(sub_element, rte_element.StructTypeElement)
        data_type: rte_element.ScalarType = sub_element.data_type
        self.assertIsInstance(data_type, rte_element.ScalarType)
        self.assertEqual(data_type.base_type.ref, "/DataTypes/BaseTypes/uint32")

    def test_create_struct_from_ref_types(self):
        # Setup
        workspace = Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        uint8_base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(uint8_base_type)
        uint32_base_type = ar_element.SwBaseType("uint32")
        packages["BaseTypes"].append(uint32_base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                            category="VALUE",
                                                            sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(uint8_impl_type)
        uint32_impl_type = ar_element.ImplementationDataType("uint32",
                                                             category="VALUE",
                                                             sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(uint32_impl_type)

        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint8_impl_type.ref())
        elem1 = ar_element.ImplementationDataTypeElement("Elem1",
                                                         category="TYPE_REFERENCE",
                                                         sw_data_def_props=sw_data_def_props)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint32_impl_type.ref())
        elem2 = ar_element.ImplementationDataTypeElement("Elem2",
                                                         category="TYPE_REFERENCE",
                                                         sw_data_def_props=sw_data_def_props)
        struct_type = ar_element.ImplementationDataType("StructType_T",
                                                        category="STRUCTURE",
                                                        sub_elements=[elem1, elem2])
        packages["ImplementationDataTypes"].append(struct_type)

        # Test
        model = Application(workspace)
        elem: rte_element.StructType = model.create_from_element(struct_type)
        self.assertIsInstance(elem, rte_element.StructType)
        self.assertEqual(elem.name, "StructType_T")
        self.assertEqual(len(elem.sub_elements), 2)
        sub_element = elem.sub_elements[0]
        self.assertEqual(sub_element.name, "Elem1")
        self.assertIsInstance(sub_element, rte_element.StructTypeElement)
        data_type: rte_element.RefType = sub_element.data_type
        self.assertIsInstance(data_type, rte_element.RefType)
        self.assertEqual(data_type.impl_type.ref, "/DataTypes/ImplementationDataTypes/uint8")
        sub_element = elem.sub_elements[1]
        self.assertEqual(sub_element.name, "Elem2")
        self.assertIsInstance(sub_element, rte_element.StructTypeElement)
        data_type: rte_element.RefType = sub_element.data_type
        self.assertIsInstance(data_type, rte_element.RefType)
        self.assertEqual(data_type.impl_type.ref, "/DataTypes/ImplementationDataTypes/uint32")


if __name__ == '__main__':
    unittest.main()
