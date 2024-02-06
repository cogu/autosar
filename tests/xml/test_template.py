"""Unit tests for template classes"""

# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import autosar.xml.workspace as ar_workspace # noqa E402
import autosar.xml.enumeration as ar_enum  # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.xml.template as ar_template # noqa E402


class MyBaseTypeTemplate(ar_template.ElementTemplate):
    """
    Template class for SwBaseType (for unit tests)
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 bit_size: int = None,
                 encoding: str = None,
                 native_declaration: str = None) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.BASE_TYPE)
        self.category = "FIXED_LENGTH"
        self.bit_size = bit_size
        self.encoding = encoding
        self.native_declaration = native_declaration

    def apply(self, package: ar_element.Package, _: ar_workspace.Workspace, **kwargs) -> ar_element.SwBaseType:
        """
        Template method
        """
        elem = ar_element.SwBaseType(name=self.element_name,
                                     category=self.category,
                                     size=self.bit_size,
                                     encoding=self.encoding,
                                     native_declaration=self.native_declaration)
        package.append(elem)
        return elem


class MyInternalDataConstraintTemplate(ar_template.ElementTemplate):
    """
    Template class for SwBaseType (for unit tests)
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 lower_limit: int | float,
                 upper_limit: int | float) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.DATA_CONSTRAINT)
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def apply(self, package: ar_element.Package, _: ar_workspace.Workspace, **kwargs) -> ar_element.DataConstraint:
        """
        Create new internal data constraint
        """
        elem = ar_element.DataConstraint.make_internal(self.element_name, self.lower_limit, self.upper_limit)
        package.append(elem)
        return elem


class MyImplementationValueDataTypeTemplate(ar_template.ElementTemplate):
    """
    Template class for value-based implementation data types (for unit tests)
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 base_type: ar_template.ElementTemplate,
                 data_constraint: ar_template.ElementTemplate = None,
                 desc: str | None = None,
                 calibration_access: str = ar_enum.SwCalibrationAccess.NOT_ACCESSIBLE,
                 ) -> None:
        depends = [base_type, data_constraint]
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.IMPLEMENTATION_DATA_TYPE, depends)
        self.category = "VALUE"
        self.desc = desc
        self.base_type = base_type
        self.data_constraint = data_constraint
        self.calibration_access = calibration_access

    def apply(self, package: ar_element.Package, workspace: ar_workspace.Workspace, **kwargs) -> ar_element.SwBaseType:
        """
        Template method
        """
        base_type_ref = self.base_type.ref(workspace)
        data_constraint_ref = self.data_constraint.ref(workspace)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type_ref,
                                                                 calibration_access=self.calibration_access,
                                                                 data_constraint_ref=data_constraint_ref)

        elem = ar_element.ImplementationDataType(name=self.element_name,
                                                 desc=self.desc,
                                                 category=self.category,
                                                 sw_data_def_props=sw_data_def_props)
        package.append(elem)
        return elem


class BaseTypeTemplateTests(unittest.TestCase):

    def create_autosar_namespace(self, workspace: ar_workspace.Workspace):
        workspace.create_namespace("AUTOSAR_Platform", package_map={
            "BaseType": "BaseTypes",
            "ImplementationDataType": "ImplementationDataTypes",
            "CompuMethod": "CompuMethods",
            "DataConstraint": "DataConstrs"})

    def test_create_uint8_base_type(self):

        uint8_template = MyBaseTypeTemplate("uint8", "AUTOSAR_Platform", 8, native_declaration="uint8")
        workspace = ar_workspace.Workspace()
        self.create_autosar_namespace(workspace)
        self.assertIsNone(workspace.find("/AUTOSAR_Platform/BaseTypes"))
        workspace.apply(uint8_template)
        self.assertIsNotNone(workspace.find("/AUTOSAR_Platform/BaseTypes"))
        base_type: ar_element.SwBaseType = workspace.find("/AUTOSAR_Platform/BaseTypes/uint8")
        self.assertIsInstance(base_type, ar_element.SwBaseType)
        self.assertEqual(base_type.name, "uint8")
        self.assertEqual(base_type.category, "FIXED_LENGTH")
        self.assertEqual(base_type.size, 8)
        self.assertEqual(base_type.native_declaration, "uint8")

    def test_create_sint8_base_type(self):

        sint8_template = MyBaseTypeTemplate("sint8", "AUTOSAR_Platform", 8, "2C", "sint8")
        workspace = ar_workspace.Workspace()
        self.create_autosar_namespace(workspace)
        workspace.apply(sint8_template)
        base_type: ar_element.SwBaseType = workspace.find("/AUTOSAR_Platform/BaseTypes/sint8")
        self.assertIsInstance(base_type, ar_element.SwBaseType)
        self.assertEqual(base_type.name, "sint8")
        self.assertEqual(base_type.category, "FIXED_LENGTH")
        self.assertEqual(base_type.size, 8)
        self.assertEqual(base_type.encoding, "2C")
        self.assertEqual(base_type.native_declaration, "sint8")


class ImplementationDataTypeTemplateTests(unittest.TestCase):

    def create_autosar_namespace(self, workspace: ar_workspace.Workspace):
        workspace.create_namespace("AUTOSAR_Platform", package_map={
            "BaseType": "BaseTypes",
            "ImplementationDataType": "ImplementationDataTypes",
            "CompuMethod": "CompuMethods",
            "DataConstraint": "DataConstrs"})

    def test_create_uint8_impl_type(self):
        uint8_base_type = MyBaseTypeTemplate("uint8", "AUTOSAR_Platform", 8, native_declaration="uint8")
        uint8_constraint = MyInternalDataConstraintTemplate("uint8_DataConstr", "AUTOSAR_Platform", 0, 255)
        uint8_impl_template = MyImplementationValueDataTypeTemplate("uint8",
                                                                    "AUTOSAR_Platform",
                                                                    uint8_base_type,
                                                                    uint8_constraint)
        workspace = ar_workspace.Workspace()
        self.create_autosar_namespace(workspace)
        workspace.apply(uint8_impl_template)
        impl_type: ar_element.ImplementationDataType = workspace.find("/AUTOSAR_Platform/ImplementationDataTypes/uint8")
        self.assertIsInstance(impl_type, ar_element.ImplementationDataType)
        self.assertEqual(impl_type.name, "uint8")
        self.assertEqual(impl_type.category, "VALUE")
        data_constraint: ar_element.DataConstraint = workspace.find("/AUTOSAR_Platform/DataConstrs/uint8_DataConstr")
        self.assertIsInstance(data_constraint, ar_element.DataConstraint)
        rule: ar_element.DataConstraintRule = data_constraint.rules[0]
        self.assertEqual(rule.internal.lower_limit, 0)
        self.assertEqual(rule.internal.upper_limit, 255)


if __name__ == '__main__':
    unittest.main()
