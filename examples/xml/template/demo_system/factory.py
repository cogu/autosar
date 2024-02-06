"""
Example template classes
"""
import autosar.xml.template as ar_template
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
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

    def apply(self, package: ar_element.Package, workspace: ar_workspace.Workspace, **kwargs) -> ar_element.SwBaseType:
        """
        Factory method for SwBaseType
        """
        elem = ar_element.SwBaseType(name=self.element_name,
                                     category=self.category,
                                     size=self.bit_size,
                                     encoding=self.encoding,
                                     native_declaration=self.native_declaration)
        package.append(elem)
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

    def apply(self,
              package: ar_element.Package,
              workspace: ar_workspace.Workspace,
              **kwargs) -> ar_element.DataConstraint:
        """
        Factory method
        """
        elem = ar_element.DataConstraint.make_internal(self.element_name, self.lower_limit, self.upper_limit)
        package.append(elem)
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

    def apply(self,
              package: ar_element.Package,
              workspace: ar_workspace.Workspace,
              **kwargs) -> ar_element.CompuMethod:
        """
        Factory method
        """
        computation = ar_element.Computation.make_value_table(self.value_table)
        elem = ar_element.CompuMethod(name=self.element_name,
                                      desc=self.desc,
                                      category=self.category,
                                      int_to_phys=computation)
        package.append(elem)
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

    def apply(self, package: ar_element.Package, workspace: ar_workspace.Workspace, **kwargs) -> ar_element.SwBaseType:
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
        package.append(elem)
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

    def apply(self, package: ar_element.Package,
              workspace: ar_workspace.Workspace, **kwargs) -> ar_element.ImplementationDataType:
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
        package.append(elem)
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

    def apply(self, package: ar_element.Package, workspace: ar_workspace.Workspace, **kwargs) -> ar_element.SwBaseType:
        """
        Factory method for SwBaseType
        """
        elem = ar_element.ModeDeclarationGroup(name=self.element_name,
                                               mode_declarations=self.mode_declarations)
        package.append(elem)
        if self.initial_mode_name is not None:
            elem.initial_mode_ref = elem.find(self.initial_mode_name).ref()
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

    def apply(self, package: ar_element.Package, workspace: ar_workspace.Workspace, **kwargs) -> ar_element.SwBaseType:
        """
        Element creation method
        """
        elem = ar_element.ModeSwitchInterface(self.element_name, is_service=self.is_service)
        elem.create_mode_group(self.mode_group_name, self.mode_declaration_group.ref(workspace))
        package.append(elem)
        return elem
