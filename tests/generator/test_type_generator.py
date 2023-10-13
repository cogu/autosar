"""Unit tests for type generator"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.model.element as rte_element  # noqa E402
from autosar.model import ImplementationModel # noqa E402
import autosar.generator # noqa E402


class TestDataTypeDependencyTrees(unittest.TestCase):

    def test_custom_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        package.append(base_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(base_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 1)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "MyUInt8Base")
        self.assertIsInstance(data_type, rte_element.BaseType)

    def test_base_type_without_native_declaration(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType("uint8")
        package.append(base_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(base_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 0)

    def test_scalar_type_of_custom_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        impl_type = ar_element.ImplementationDataType("MyUInt8",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(impl_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(impl_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 2)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "MyUInt8Base")
        self.assertIsInstance(data_type, rte_element.BaseType)
        data_type = data_types[1]
        self.assertEqual(data_type.name, "MyUInt8")
        self.assertIsInstance(data_type, rte_element.ScalarType)

    def test_type_reference(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))

        uint8_base_type = ar_element.SwBaseType('uint8')
        packages["BaseTypes"].append(uint8_base_type)
        package = workspace.find("DataTypes/ImplementationDataTypes")
        workspace.append(package)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                            category="VALUE",
                                                            sw_data_def_props=sw_data_def_props,
                                                            type_emitter="Platform")
        packages["ImplementationDataTypes"].append(uint8_impl_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint8_impl_type.ref())
        inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                              category="TYPE_REFERENCE",
                                                              sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(inactive_active_t)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(inactive_active_t)

        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 1)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "InactiveActive_T")
        self.assertIsInstance(data_type, rte_element.RefType)

    def test_array_of_platform_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                               category="VALUE",
                                                               array_size=8,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType('Array_T',
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(array_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 1)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "Array_T")
        self.assertIsInstance(data_type, rte_element.ArrayType)

    def test_array_of_custom_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                               category="VALUE",
                                                               array_size=8,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType('Array_T',
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(array_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 1)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "Array_T")
        self.assertIsInstance(data_type, rte_element.ArrayType)

    def test_array_of_type_reference(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))

        uint8_base_type = ar_element.SwBaseType('uint8')
        packages["BaseTypes"].append(uint8_base_type)
        package = workspace.find("DataTypes/ImplementationDataTypes")
        workspace.append(package)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        value_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(value_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=value_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                               category="TYPE_REFERENCE",
                                                               array_size=3,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType('Array_T',
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(array_type)

        type_generator = autosar.generator.TypeGenerator(implementation)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 2)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "InactiveActive_T")
        self.assertIsInstance(data_type, rte_element.ScalarType)
        data_type = data_types[1]
        self.assertEqual(data_type.name, "Array_T")
        self.assertIsInstance(data_type, rte_element.ArrayType)


class TestTypeGenerator(unittest.TestCase):

    def test_custom_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        package.append(base_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(base_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = '''typedef unsigned char MyUInt8Base;
'''
        self.assertEqual(type_generator.write_type_defs_str(), expected)

    def test_base_type_without_native_declaration(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType("uint8")
        package.append(base_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(base_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        self.assertEqual(type_generator.write_type_defs_str(), "")

    def test_scalar_type_of_custom_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        impl_type = ar_element.ImplementationDataType("MyUInt8",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(impl_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(impl_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = '''typedef unsigned char MyUInt8Base;
typedef MyUInt8Base MyUInt8;
'''
        self.assertEqual(type_generator.write_type_defs_str(), expected)

    def test_scalar_type_of_platform_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        impl_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(impl_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(impl_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = 'typedef uint8 InactiveActive_T;\n'
        self.assertEqual(type_generator.write_type_defs_str(), expected)

    def test_type_reference(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))

        uint8_base_type = ar_element.SwBaseType('uint8')
        packages["BaseTypes"].append(uint8_base_type)
        package = workspace.find("DataTypes/ImplementationDataTypes")
        workspace.append(package)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                            category="VALUE",
                                                            sw_data_def_props=sw_data_def_props,
                                                            type_emitter="Platform")
        packages["ImplementationDataTypes"].append(uint8_impl_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint8_impl_type.ref())
        inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                              category="TYPE_REFERENCE",
                                                              sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(inactive_active_t)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(inactive_active_t)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = 'typedef uint8 InactiveActive_T;\n'
        self.assertEqual(type_generator.write_type_defs_str(), expected)

    def test_array_of_platform_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType("uint8")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                               category="VALUE",
                                                               array_size=8,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType('Array_T',
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(array_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = 'typedef uint8 Array_T[8];\n'
        self.assertEqual(type_generator.write_type_defs_str(), expected)

    def test_array_of_custom_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        packages["BaseTypes"].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                               category="VALUE",
                                                               array_size=8,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType('Array_T',
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(array_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = 'typedef unsigned char Array_T[8];\n'
        self.assertEqual(type_generator.write_type_defs_str(), expected)

    def test_array_of_type_reference(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = dict(zip(["BaseTypes", "ImplementationDataTypes"],
                            workspace.make_packages("DataTypes/BaseTypes",
                                                    "DataTypes/ImplementationDataTypes")))

        uint8_base_type = ar_element.SwBaseType('uint8')
        packages["BaseTypes"].append(uint8_base_type)
        package = workspace.find("DataTypes/ImplementationDataTypes")
        workspace.append(package)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        value_type = ar_element.ImplementationDataType("InactiveActive_T",
                                                       category="VALUE",
                                                       sw_data_def_props=sw_data_def_props)
        packages["ImplementationDataTypes"].append(value_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=value_type.ref())
        sub_element = ar_element.ImplementationDataTypeElement('Element',
                                                               category="TYPE_REFERENCE",
                                                               array_size=3,
                                                               sw_data_def_props=sw_data_def_props)
        array_type = ar_element.ImplementationDataType('Array_T',
                                                       category="ARRAY",
                                                       sub_elements=[sub_element])
        packages["ImplementationDataTypes"].append(array_type)

        # Test
        implementation = ImplementationModel(workspace)
        implementation.create_from_element(array_type)
        type_generator = autosar.generator.TypeGenerator(implementation)
        expected = '''typedef uint8 InactiveActive_T;
typedef InactiveActive_T Array_T[3];
'''
        self.assertEqual(type_generator.write_type_defs_str(), expected)


if __name__ == '__main__':
    unittest.main()
