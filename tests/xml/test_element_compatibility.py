"""Unit tests for autosar.xml.element compatibility facade."""

# pylint: disable=missing-class-docstring, missing-function-docstring
import importlib
import os
import pickle
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
import autosar  # noqa E402
import autosar.xml.element as ar_element  # noqa E402
import autosar.xml.enumeration as ar_enum  # noqa E402


class TestElementImports(unittest.TestCase):
    """Test public imports through the facade."""

    def test_import_facade(self):
        """Verify representative classes are accessible via the facade module."""
        representative_classes = [
            "AdminData",
            "SpecialDataGroup",
            "SpecialDataElement",
            "SpecialDataValue",
            "DocRevision",
            "Modification",
            "Referrable",
            "MultiLanguageReferrable",
            "Identifiable",
            "CollectableElement",
            "ARElement",
            "NumericalValue",
            "PositiveIntegerValue",
            "Unit",
            "Computation",
            "CompuMethod",
            "DataConstraint",
            "ImplementationDataType",
            "ApplicationPrimitiveDataType",
            "SwBaseType",
            "SenderReceiverInterface",
            "ClientServerInterface",
            "ModeSwitchInterface",
            "ApplicationSoftwareComponentType",
            "CompositionSwComponentType",
            "SwcInternalBehavior",
            "Package",
        ]
        for name in representative_classes:
            self.assertTrue(hasattr(ar_element, name), f"ar_element missing {name}")

    def test_direct_imports(self):
        """Verify direct import from autosar.xml.element."""
        from autosar.xml.element import (
            AdminData,
            ARElement,
            ApplicationPrimitiveDataType,
            Computation,
            DataConstraint,
            ImplementationDataType,
            Package,
            SenderReceiverInterface,
            SpecialDataGroup,
            SwcInternalBehavior,
            Unit,
        )

        self.assertIs(AdminData, ar_element.AdminData)
        self.assertIs(ARElement, ar_element.ARElement)
        self.assertIs(ApplicationPrimitiveDataType, ar_element.ApplicationPrimitiveDataType)
        self.assertIs(Computation, ar_element.Computation)
        self.assertIs(DataConstraint, ar_element.DataConstraint)
        self.assertIs(ImplementationDataType, ar_element.ImplementationDataType)
        self.assertIs(Package, ar_element.Package)
        self.assertIs(SenderReceiverInterface, ar_element.SenderReceiverInterface)
        self.assertIs(SpecialDataGroup, ar_element.SpecialDataGroup)
        self.assertIs(SwcInternalBehavior, ar_element.SwcInternalBehavior)
        self.assertIs(Unit, ar_element.Unit)

    def test_reexported_identity_with_internal_modules(self):
        """If autosar.xml.elements submodules exist, verify facade re-exports the exact class objects."""
        # Check _base if it has been created
        try:
            elements_base = importlib.import_module("autosar.xml.elements._base")
        except ModuleNotFoundError:
            elements_base = None

        if elements_base is not None:
            for cls_name in ["Referrable", "Identifiable", "ARElement", "AdminData", "SpecialDataGroup"]:
                if hasattr(elements_base, cls_name):
                    base_cls = getattr(elements_base, cls_name)
                    facade_cls = getattr(ar_element, cls_name)
                    self.assertIs(
                        facade_cls,
                        base_cls,
                        f"Facade {cls_name} is not identical to elements._base.{cls_name}",
                    )

        try:
            elements_unit = importlib.import_module("autosar.xml.elements.unit")
        except ModuleNotFoundError:
            elements_unit = None

        if elements_unit is not None:
            self.assertIs(ar_element.Unit, elements_unit.Unit)

        try:
            elements_constraint = importlib.import_module("autosar.xml.elements.constraint")
        except ModuleNotFoundError:
            elements_constraint = None

        if elements_constraint is not None:
            for cls_name in ["DataConstraint", "DataConstraintRule", "InternalConstraint", "PhysicalConstraint"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_constraint, cls_name))

        try:
            elements_comp = importlib.import_module("autosar.xml.elements.computation_method")
        except ModuleNotFoundError:
            elements_comp = None

        if elements_comp is not None:
            for cls_name in ["CompuRational", "CompuConst", "CompuScale", "Computation", "CompuMethod"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_comp, cls_name))

        try:
            elements_aux = importlib.import_module("autosar.xml.elements.auxiliary")
        except ModuleNotFoundError:
            elements_aux = None

        if elements_aux is not None:
            self.assertIs(ar_element.SwAddrMethod, elements_aux.SwAddrMethod)

        try:
            elements_sn = importlib.import_module("autosar.xml.elements.service_needs")
        except ModuleNotFoundError:
            elements_sn = None

        if elements_sn is not None:
            for cls_name in ["ServiceNeeds", "BswMgrNeeds", "DiagnosticEventNeeds", "NvBlockNeeds"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_sn, cls_name))

        try:
            elements_doc = importlib.import_module("autosar.xml.elements.documentation")
        except ModuleNotFoundError:
            elements_doc = None

        if elements_doc is not None:
            for cls_name in ["Date", "RevisionLabelString", "Annotation", "DocumentationBlock",
                             "MultiLanguageOverviewParagraph", "MultilanguageLongName"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_doc, cls_name))
            self.assertIs(ar_element.date_re, elements_doc.date_re)
            self.assertIs(ar_element.revision_label_string_re, elements_doc.revision_label_string_re)

        try:
            elements_com = importlib.import_module("autosar.xml.elements.common")
        except ModuleNotFoundError:
            elements_com = None

        if elements_com is not None:
            for cls_name in ["DataFilter", "EngineeringObject", "AutosarEngineeringObject",
                             "Code", "Implementation", "MultidimensionalTime", "Trigger"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_com, cls_name))

        try:
            elements_dt = importlib.import_module("autosar.xml.elements.data_type")
        except ModuleNotFoundError:
            elements_dt = None

        if elements_dt is not None:
            for cls_name in ["BaseType", "SwBaseType", "ImplementationDataType",
                             "ApplicationPrimitiveDataType", "DataTypeMappingSet", "ValueList"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_dt, cls_name))
            self.assertIs(ar_element.alignment_type_re, elements_dt.alignment_type_re)
            self.assertIs(ar_element.display_format_str_re, elements_dt.display_format_str_re)

        try:
            elements_cd = importlib.import_module("autosar.xml.elements.calibration_data")
        except ModuleNotFoundError:
            elements_cd = None

        if elements_cd is not None:
            for cls_name in ["SwValues", "ValueGroup", "SwAxisCont", "SwValueCont"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_cd, cls_name))

        try:
            elements_const = importlib.import_module("autosar.xml.elements.constant")
        except ModuleNotFoundError:
            elements_const = None

        if elements_const is not None:
            for cls_name in ["ValueSpecification", "NumericalValueSpecification", "ConstantSpecification",
                             "ConstantReference", "NumericalOrText", "ConstantSpecificationMapping"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_const, cls_name))

        try:
            elements_pkg = importlib.import_module("autosar.xml.elements.package")
        except ModuleNotFoundError:
            elements_pkg = None

        if elements_pkg is not None:
            for cls_name in ["Package", "BehaviorSettings", "PackageCollection"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_pkg, cls_name))

        try:
            elements_md = importlib.import_module("autosar.xml.elements.mode_declaration")
        except ModuleNotFoundError:
            elements_md = None

        if elements_md is not None:
            for cls_name in ["ModeDeclaration", "ModeDeclarationGroup", "ModeRequestTypeMap"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_md, cls_name))

        try:
            elements_pi = importlib.import_module("autosar.xml.elements.port_interface")
        except ModuleNotFoundError:
            elements_pi = None

        if elements_pi is not None:
            for cls_name in ["PortInterface", "SenderReceiverInterface", "ClientServerInterface",
                             "ModeSwitchInterface", "ApplicationError", "ClientServerOperation"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_pi, cls_name))

        try:
            elements_st = importlib.import_module("autosar.xml.elements.system_template")
        except ModuleNotFoundError:
            elements_st = None

        if elements_st is not None:
            for cls_name in ["E2EProfileCompatibilityProps", "EndToEndTransformationComSpecProps"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_st, cls_name))

        try:
            elements_swc = importlib.import_module("autosar.xml.elements.software_component")
        except ModuleNotFoundError:
            elements_swc = None

        if elements_swc is not None:
            for cls_name in ["ApplicationSoftwareComponentType", "CompositionSwComponentType",
                             "ProvidePortPrototype", "RequirePortPrototype", "AssemblySwConnector"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_swc, cls_name))

        try:
            elements_sd = importlib.import_module("autosar.xml.elements.service_dependency")
        except ModuleNotFoundError:
            elements_sd = None

        if elements_sd is not None:
            for cls_name in ["RoleBasedDataAssignment", "RoleBasedDataTypeAssignment", "RoleBasedPortAssignment",
                             "SymbolicNameProps", "ServiceDependency", "SwcServiceDependency"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_sd, cls_name))

        try:
            elements_ib = importlib.import_module("autosar.xml.elements.internal_behavior")
        except ModuleNotFoundError:
            elements_ib = None

        if elements_ib is not None:
            for cls_name in ["InternalBehavior", "SwcInternalBehavior", "RunnableEntity",
                             "RteEvent", "TimingEvent", "DataReceivedEvent", "VariableAccess",
                             "ServerCallPoint", "PortApiOption", "ExclusiveArea"]:
                self.assertIs(getattr(ar_element, cls_name), getattr(elements_ib, cls_name))


class TestIsInstanceBehavior(unittest.TestCase):
    """Test inheritance hierarchy and isinstance behavior."""

    def test_admin_data_hierarchy(self):
        sdg = ar_element.SpecialDataGroup(gid="GID1", content="Hello")
        admin_data = ar_element.AdminData(sdg)
        self.assertIsInstance(sdg, ar_element.SpecialDataGroup)
        self.assertIsInstance(admin_data, ar_element.AdminData)
        self.assertIsInstance(sdg, autosar.xml.base.ARObject)
        self.assertIsInstance(admin_data, autosar.xml.base.ARObject)

    def test_identifiable_hierarchy(self):
        data_type = ar_element.ApplicationPrimitiveDataType("MyType")
        self.assertIsInstance(data_type, ar_element.ApplicationPrimitiveDataType)
        self.assertIsInstance(data_type, ar_element.ARElement)
        self.assertIsInstance(data_type, ar_element.CollectableElement)
        self.assertIsInstance(data_type, ar_element.Identifiable)
        self.assertIsInstance(data_type, ar_element.MultiLanguageReferrable)
        self.assertIsInstance(data_type, ar_element.Referrable)
        self.assertIsInstance(data_type, autosar.xml.base.ARObject)

    def test_software_component_hierarchy(self):
        swc = ar_element.ApplicationSoftwareComponentType("MySwc")
        self.assertIsInstance(swc, ar_element.ApplicationSoftwareComponentType)
        self.assertIsInstance(swc, ar_element.AtomicSoftwareComponentType)
        self.assertIsInstance(swc, ar_element.SwComponentType)
        self.assertIsInstance(swc, ar_element.ARElement)

    def test_port_interface_hierarchy(self):
        sr_if = ar_element.SenderReceiverInterface("MyInterface")
        self.assertIsInstance(sr_if, ar_element.SenderReceiverInterface)
        self.assertIsInstance(sr_if, ar_element.PortInterface)
        self.assertIsInstance(sr_if, ar_element.ARElement)

    def test_internal_behavior_hierarchy(self):
        behavior = ar_element.SwcInternalBehavior("MyBehavior")
        self.assertIsInstance(behavior, ar_element.SwcInternalBehavior)
        self.assertIsInstance(behavior, ar_element.InternalBehavior)
        self.assertIsInstance(behavior, ar_element.Identifiable)
        runnable = ar_element.RunnableEntity("MyRunnable")
        self.assertIsInstance(runnable, ar_element.RunnableEntity)
        self.assertIsInstance(runnable, ar_element.ExecutableEntity)
        self.assertIsInstance(runnable, ar_element.Identifiable)

    def test_service_dependency_hierarchy(self):
        dep = ar_element.SwcServiceDependency("MyServiceDep")
        self.assertIsInstance(dep, ar_element.SwcServiceDependency)
        self.assertIsInstance(dep, ar_element.ServiceDependency)
        self.assertIsInstance(dep, ar_element.Identifiable)


class TestRoundTripARXML(unittest.TestCase):
    """Test ARXML writing and reading round-trip with reader/writer."""

    def test_round_trip_basic(self):
        writer = autosar.xml.Writer()
        reader = autosar.xml.Reader()

        # AdminData round trip
        sdg = ar_element.SpecialDataGroup(gid="ConfigGID", content="TestContent")
        admin_data = ar_element.AdminData(sdgs=sdg)
        xml_str = writer.write_str_elem(admin_data)
        read_admin_data = reader.read_str_elem(xml_str)
        self.assertIsInstance(read_admin_data, ar_element.AdminData)
        self.assertEqual(len(read_admin_data.sdgs), 1)
        self.assertEqual(read_admin_data.sdgs[0].gid, "ConfigGID")

        # DataConstraint round trip
        data_constr = ar_element.DataConstraint.make_internal("uint8_DataConstr", 0, 255)
        xml_constr = writer.write_str_elem(data_constr)
        read_constr = reader.read_str_elem(xml_constr)
        self.assertIsInstance(read_constr, ar_element.DataConstraint)
        self.assertEqual(read_constr.name, "uint8_DataConstr")


class TestPickleCompatibility(unittest.TestCase):
    """Test serialization / deserialization using pickle."""

    def test_pickle_special_data(self):
        elem = ar_element.SpecialDataElement("val", gid="G")
        pickled = pickle.dumps(elem)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, ar_element.SpecialDataElement)
        self.assertEqual(unpickled.text, "val")
        self.assertEqual(unpickled.gid, "G")

    def test_pickle_numerical_value(self):
        num = ar_element.NumericalValue(42, ar_enum.ValueFormat.HEXADECIMAL)
        pickled = pickle.dumps(num)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, ar_element.NumericalValue)
        self.assertEqual(unpickled.value, 42)
        self.assertEqual(unpickled.value_format, ar_enum.ValueFormat.HEXADECIMAL)

    def test_pickle_admin_data(self):
        sdg = ar_element.SpecialDataGroup(gid="PickleGID", caption="Caption")
        sdg.append_content("Item1")
        admin_data = ar_element.AdminData(sdgs=sdg)
        pickled = pickle.dumps(admin_data)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, ar_element.AdminData)
        self.assertEqual(len(unpickled.sdgs), 1)
        self.assertEqual(unpickled.sdgs[0].gid, "PickleGID")
        self.assertEqual(unpickled.sdgs[0].caption, "Caption")

    def test_pickle_data_constraint(self):
        data_constr = ar_element.DataConstraint.make_internal("TestConstr", 0, 100)
        pickled = pickle.dumps(data_constr)
        unpickled = pickle.loads(pickled)
        self.assertIsInstance(unpickled, ar_element.DataConstraint)
        self.assertEqual(unpickled.name, "TestConstr")


if __name__ == "__main__":
    unittest.main()
