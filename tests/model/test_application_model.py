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


class ApplicationModelTests(unittest.TestCase):

    def test_create_uint8_base_type(self):
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('uint8')
        package.append(base_type)
        application = Application(workspace)
        elem: rte_element.BaseType = application.create_from_element(base_type)
        self.assertEqual(elem.name, base_type.name)
        self.assertEqual(elem.native_declaration, base_type.native_declaration)

    def test_create_custom_uint8_base_type(self):
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('MyUint8Base', native_declaration="unsigned char")
        package.append(base_type)
        application = Application(workspace)
        elem: rte_element.BaseType = application.create_from_element(base_type)
        self.assertEqual(elem.name, base_type.name)
        self.assertEqual(elem.native_declaration, base_type.native_declaration)

    def test_create_custom_uint8_scalar_type(self):
        workspace = autosar.xml.Workspace()
        package = workspace.make_packages("DataTypes/BaseTypes")
        base_type = ar_element.SwBaseType('MyUint8Base', native_declaration="unsigned char")
        package.append(base_type)
        package = workspace.make_packages("DataTypes/ImplementationDataTypes")
        workspace.append(package)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type.ref())
        impl_type = ar_element.ImplementationDataType("MyUint8",
                                                      category="VALUE",
                                                      sw_data_def_props=sw_data_def_props)
        package.append(impl_type)
        application = Application(workspace)
        elem: rte_element.ScalarType = application.create_from_element(impl_type)
        self.assertIsInstance(elem, rte_element.ScalarType)
        self.assertEqual(elem.name, impl_type.name)
        self.assertEqual(elem.base_type.name, "MyUint8Base")


if __name__ == '__main__':
    unittest.main()
