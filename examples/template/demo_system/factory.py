"""
Example template classes
"""
from typing import Any, Callable
import autosar.xml.template as ar_template
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
from autosar.xml.template import TemplateBase
import autosar.xml.workspace as ar_workspace


class SwBaseTypeTemplate(ar_template.ElementTemplate):
    """
    SwBaseType template
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

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.SwBaseType:
        """
        Factory method for SwBaseType
        """
        elem = ar_element.SwBaseType(name=self.element_name,
                                     category=self.category,
                                     size=self.bit_size,
                                     encoding=self.encoding,
                                     native_declaration=self.native_declaration)

        return elem


class DataConstraintInternalTemplate(ar_template.ElementTemplate):
    """
    Template class for internal DataConstraint
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 lower_limit: int | float,
                 upper_limit: int | float) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.DATA_CONSTRAINT)
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.DataConstraint:
        """
        Factory method
        """
        elem = ar_element.DataConstraint.make_internal(self.element_name, self.lower_limit, self.upper_limit)
        return elem


class CompuMethodEnumTemplate(ar_template.ElementTemplate):
    """
    Template class for Compumethods based on enumeration
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 value_table: list[str] | list[tuple],
                 auto_label: bool = True,
                 desc: str | None = None,) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.COMPU_METHOD)
        self.category = "TEXTTABLE"
        self.value_table = value_table
        self.auto_label = auto_label
        self.desc = desc

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.CompuMethod:
        """
        Factory method
        """
        computation = ar_element.Computation.make_value_table(self.value_table)
        elem = ar_element.CompuMethod(name=self.element_name,
                                      desc=self.desc,
                                      category=self.category,
                                      int_to_phys=computation)
        return elem


class ImplementationValueTypeTemplate(ar_template.ElementTemplate):
    """
    Template class for value-based implementation data type
    that references a base type
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 base_type: ar_template.ElementTemplate,
                 data_constraint: ar_template.ElementTemplate = None,
                 compu_method: ar_template.ElementTemplate = None,
                 desc: str | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 type_emitter: str | None = None
                 ) -> None:
        dependencies = [base_type]
        if data_constraint is not None:
            dependencies.append(data_constraint)
        if compu_method is not None:
            dependencies.append(compu_method)
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.IMPLEMENTATION_DATA_TYPE, dependencies)
        self.category = "VALUE"
        self.desc = desc
        self.base_type = base_type
        self.data_constraint = data_constraint
        self.compu_method = compu_method
        self.calibration_access = calibration_access
        self.type_emitter = type_emitter

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.ImplementationDataType:
        """
        Factory method
        """
        base_type_ref = self.base_type.ref(workspace)
        compu_method_ref = None if self.compu_method is None else self.compu_method.ref(workspace)
        data_constraint_ref = None if self.data_constraint is None else self.data_constraint.ref(workspace)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type_ref,
                                                                 compu_method_ref=compu_method_ref,
                                                                 data_constraint_ref=data_constraint_ref,
                                                                 calibration_access=self.calibration_access,
                                                                 )
        elem = ar_element.ImplementationDataType(name=self.element_name,
                                                 desc=self.desc,
                                                 category=self.category,
                                                 sw_data_def_props=sw_data_def_props,
                                                 type_emitter=self.type_emitter)
        return elem


class ImplementationEnumDataTypeTemplate(ar_template.ElementTemplate):
    """
    Template class for implementation types based on
    an enumeration table
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 base_type: ar_template.ElementTemplate,
                 value_table: list[str],
                 desc: str | None = None,
                 calibration_access: ar_enum.SwCalibrationAccess | None = None,
                 data_constraint_suffix="_DataConstr",
                 compu_method_suffix="",
                 ) -> None:

        data_constraint = self._create_data_constraint(element_name,
                                                       namespace_name,
                                                       data_constraint_suffix,
                                                       value_table)
        compu_method = self._create_compu_method(element_name,
                                                 namespace_name,
                                                 compu_method_suffix,
                                                 value_table)
        dependencies = [base_type, data_constraint, compu_method]
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.IMPLEMENTATION_DATA_TYPE, dependencies)
        self.category = "VALUE"
        self.desc = desc
        self.base_type = base_type
        self.data_constraint = data_constraint
        self.compu_method = compu_method
        self.calibration_access = calibration_access

    def _create_data_constraint(self,
                                element_name: str,
                                namespace_name: str,
                                suffix: str,
                                value_table: list[str]) -> ar_template.ElementTemplate:
        return DataConstraintInternalTemplate(element_name + suffix, namespace_name, 0, len(value_table) - 1)

    def _create_compu_method(self,
                             element_name: str,
                             namespace_name: str,
                             suffix: str,
                             value_table: list[str]) -> ar_template.ElementTemplate:
        return CompuMethodEnumTemplate(element_name + suffix, namespace_name, value_table, auto_label=False)

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.ImplementationDataType:
        """
        Factory method
        """
        base_type_ref = self.base_type.ref(workspace)
        compu_method_ref = None if self.compu_method is None else self.compu_method.ref(workspace)
        data_constraint_ref = None if self.data_constraint is None else self.data_constraint.ref(workspace)
        sw_data_def_props = ar_element.SwDataDefPropsConditional(base_type_ref=base_type_ref,
                                                                 compu_method_ref=compu_method_ref,
                                                                 data_constraint_ref=data_constraint_ref,
                                                                 calibration_access=self.calibration_access,
                                                                 )
        elem = ar_element.ImplementationDataType(name=self.element_name,
                                                 desc=self.desc,
                                                 category=self.category,
                                                 sw_data_def_props=sw_data_def_props)
        return elem


class ModeDeclarationGroupTemplate(ar_template.ElementTemplate):
    """
    ModeDeclarationGroup template
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 mode_declarations: list[str],
                 initial_mode_name: str | None = None) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.MODE_DECLARATION)
        self.mode_declarations = list(mode_declarations)
        self.initial_mode_name = initial_mode_name

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.ModeDeclarationGroup:
        """
        Factory method for SwBaseType
        """
        initial_mode_ref = None
        if self.initial_mode_name is not None:
            initial_mode_ref = '/'.join([str(package.ref()), self.element_name, self.initial_mode_name])
        elem = ar_element.ModeDeclarationGroup(name=self.element_name,
                                               mode_declarations=self.mode_declarations,
                                               initial_mode_ref=initial_mode_ref)
        return elem


class ModeSwitchInterfaceTemplate(ar_template.ElementTemplate):
    """
    ModeDeclarationGroup template
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 mode_declaration_group: ModeDeclarationGroupTemplate,
                 mode_group_name: str,
                 is_service: bool = False) -> None:
        dependencies = [mode_declaration_group]
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.PORT_INTERFACE, dependencies)
        self.mode_group_name = mode_group_name
        self.mode_declaration_group = mode_declaration_group
        self.is_service = is_service

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.ModeSwitchInterface:
        """
        Element creation method
        """
        elem = ar_element.ModeSwitchInterface(self.element_name, is_service=self.is_service)
        elem.create_mode_group(self.mode_group_name, self.mode_declaration_group.ref(workspace))
        return elem


CreateFuncType = Callable[[ar_element.Package, ar_workspace.Workspace, dict[str, ar_element.ARElement] | None],
                          ar_element.ARElement]


class GenericPortInterfaceTemplate(ar_template.ElementTemplate):
    """
    Generic port interface element template
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 create_func: CreateFuncType,
                 depends: list[TemplateBase] | None = None) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.PORT_INTERFACE, depends)
        self.create_func = create_func

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.PortInterface:
        """
        Create method
        """
        elem = self.create_func(package, workspace, dependencies, **kwargs)
        return elem


class SenderReceiverInterfaceTemplate(ar_template.ElementTemplate):
    """
    Sender receiver port interface template restricted to a single data element
    It is assumed that the element name ends with "_I"
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 data_element_template: ar_template.ElementTemplate,
                 data_element_name: str | None = None) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.PORT_INTERFACE, [data_element_template])
        self.data_element_template = data_element_template
        self.data_element_name = data_element_name

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.SenderReceiverInterface:
        """
        Create method
        """
        elem_type = dependencies[self.data_element_template.ref(workspace)]
        port_interface = ar_element.SenderReceiverInterface(self.element_name)
        elem_name = self.data_element_name
        if elem_name is None:
            if self.element_name.endswith("_I"):
                elem_name = self.element_name[:-2]
            else:
                elem_name = self.element_name
        port_interface.create_data_element(elem_name, type_ref=elem_type.ref())
        return port_interface


class GenericComponentTypeTemplate(ar_template.ElementTemplate):
    """
    Generic component type element template
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 create_func: CreateFuncType,
                 depends: list[TemplateBase] | None = None,
                 append_to_package: bool = True) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.COMPONENT_TYPE, depends, append_to_package)
        self.create_func = create_func

    def create(self,
               package: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.PortInterface:
        """
        Create method
        """
        elem = self.create_func(package, workspace, dependencies, **kwargs)
        return elem


class SwcImplementationTemplate(ar_template.ElementTemplate):
    """
    SwcImplementation template
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 component_type: ar_template.ElementTemplate) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.COMPONENT_TYPE, [component_type])
        self.component_type = component_type

    def create(self,
               _0: ar_element.Package,
               workspace: ar_workspace.Workspace,
               dependencies: dict[str, ar_element.ARElement] | None,
               **kwargs) -> ar_element.SwBaseType:
        """
        Factory method for creating a new SwcImplementation
        """
        swc_type = dependencies[self.component_type.ref(workspace)]
        elem = ar_element.SwcImplementation(self.element_name,
                                            behavior_ref=swc_type.internal_behavior.ref())

        return elem


class ConstantTemplate(ar_template.ElementTemplate):
    """
    Constant template
    """

    def __init__(self,
                 element_name: str,
                 namespace_name: str,
                 value: Any) -> None:
        super().__init__(element_name, namespace_name, ar_enum.PackageRole.CONSTANT)
        self.value = value

    def create(self,
               _0: ar_element.Package,
               _1: ar_workspace.Workspace,
               _2: dict[str, ar_element.ARElement] | None,
               **_3) -> ar_element.SwBaseType:
        """
        Factory method for creating a new SwcImplementation
        """
        return ar_element.ConstantSpecification.make_constant(self.element_name, self.value)
