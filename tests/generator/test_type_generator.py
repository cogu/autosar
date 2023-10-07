"""Unit tests for type generator"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.model.element as rte_element  # noqa E402
from autosar.model import Application # noqa E402
import autosar.generator # noqa E402


class TestTypeGenerator(unittest.TestCase):

    def test_type_creation_order_from_base_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        package.append(base_type)
        application = Application(workspace)
        application.create_from_element(base_type)

        # Test
        type_generator = autosar.generator.TypeGenerator(application)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 1)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "MyUInt8Base")
        self.assertIsInstance(data_type, rte_element.BaseType)

    def test_type_creation_order_from_scalar_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        packages = workspace.make_packages("DataTypes/BaseTypes",
                                           "DataTypes/ImplementationDataTypes")
        base_type = ar_element.SwBaseType('MyUInt8Base', native_declaration="unsigned char")
        packages[0].append(base_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        impl_type = ar_element.ImplementationDataType("MyUInt8",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
        packages[1].append(impl_type)
        application = Application(workspace)
        application.create_from_element(impl_type)

        # Test
        type_generator = autosar.generator.TypeGenerator(application)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 2)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "MyUInt8Base")
        self.assertIsInstance(data_type, rte_element.BaseType)
        data_type = data_types[1]
        self.assertEqual(data_type.name, "MyUInt8")
        self.assertIsInstance(data_type, rte_element.ScalarType)

    def test_type_creation_order_from_ref_type(self):
        # Setup
        workspace = autosar.xml.Workspace()
        workspace.make_packages("DataTypes/BaseTypes",
                                "DataTypes/ImplementationDataTypes")
        package = workspace.find("DataTypes/BaseTypes")
        uint8_base_type = ar_element.SwBaseType('uint8')
        package.append(uint8_base_type)
        package = workspace.find("DataTypes/ImplementationDataTypes")
        workspace.append(package)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=uint8_base_type.ref())
        uint8_impl_type = ar_element.ImplementationDataType("uint8",
                                                            category="VALUE",
                                                            sw_data_def_props=sw_data_def_props,
                                                            type_emitter="Platform")
        package.append(uint8_impl_type)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(impl_data_type_ref=uint8_impl_type.ref())
        inactive_active_t = ar_element.ImplementationDataType("InactiveActive_T",
                                                              category="TYPE_REFERENCE",
                                                              sw_data_def_props=sw_data_def_props)
        package.append(inactive_active_t)

        application = Application(workspace)
        application.create_from_element(inactive_active_t)

        # Test
        type_generator = autosar.generator.TypeGenerator(application)
        data_types = type_generator.gen_data_type_creation_order()
        self.assertEqual(len(data_types), 1)
        data_type = data_types[0]
        self.assertEqual(data_type.name, "InactiveActive_T")
        self.assertIsInstance(data_type, rte_element.RefType)


if __name__ == '__main__':
    unittest.main()
