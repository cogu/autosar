"""
AUTOSAR XML Workspace
"""
import posixpath
from typing import Any
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
import autosar.xml.template as ar_template


class Namespace:
    """
    Namespace
    """

    def __init__(self, name: str, package_map: dict[str, str], base_ref: str = None) -> None:
        self.name = name
        self.base_ref = "/" + name if base_ref is None else base_ref
        self.package_map: dict[ar_enum.PackageRole | str, str] = {}

        for role_name, rel_path in package_map.items():
            if role_name.startswith("!"):
                package_role = role_name[1:]
            else:
                package_role = ar_enum.str_to_package_role(role_name)
            abs_path = posixpath.join(self.base_ref, rel_path)
            self.package_map[package_role] = abs_path


class Workspace:
    """
    Workspace
    """

    def __init__(self, config_file_path: str = None) -> None:
        self.namespaces: dict[str, Namespace] = {}
        self.packages: list[ar_element.Package] = []
        self._package_map: dict[str, ar_element.Package] = {}

    def create_namespace(self, name: str, package_map: dict[str, str], base_ref: str = None) -> None:
        """
        Creates new namespace
        """
        self.namespaces[name] = Namespace(name, package_map, base_ref)

    def get_namespace(self, name: str) -> Namespace:
        """
        Selects previously created namespace
        """
        if name in self.namespaces:
            return self.namespaces[name]
        else:
            raise KeyError(f"No such namespace: {name}")

    def get_package_ref_by_role(self, namespace_name: str, role: ar_enum.PackageRole | str):
        """
        Returns package reference based on role in
        currently selected namespace
        """
        if not isinstance(role, (ar_enum.PackageRole, str)):
            raise TypeError(f"role must be of type PackageRole or str. Got {str(type(role))}")
        namespace = self.get_namespace(namespace_name)
        base_ref = namespace.base_ref
        try:
            rel_path = namespace.package_map[role]
        except KeyError as ex:
            raise ValueError(f"Role '{str(role)}'not in namespace map") from ex
        return posixpath.normpath(posixpath.join(base_ref, rel_path))

    def make_packages(self, ref: str) -> ar_element.Package:
        """
        Recursively creates packages from reference
        """
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        package = self._package_map.get(parts[0], None)
        if package is None:
            package = self.create_package(parts[0])
        if len(parts[2]) > 0:
            return package.make_packages(parts[2])
        return package

    def create_package(self, name: str, **kwargs) -> ar_element.Package:
        """
        Creates new package in workspace
        """
        if name in self._package_map:
            return ValueError(f"Package with name '{name}' already exists")
        package = ar_element.Package(name, **kwargs)
        self._package_map[name] = package
        self.packages.append(package)
        package.parent = self
        return package

    def find(self, ref: str) -> Any:
        """
        Finds item by reference
        """
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        package = self._package_map.get(parts[0], None)
        if (package is not None) and (len(parts[2]) > 0):
            return package.find(parts[2])
        return package

    def update_ref_parts(self, ref_parts: list[str]):
        """
        Utility method used generating XML references
        """
        ref_parts.append('')

    def apply(self, template: Any, **kwargs) -> Any:
        """
        Applies template oject in this workspace
        """
        if isinstance(template, ar_template.ElementTemplate):
            return self._apply_element_template(template, kwargs)
        elif isinstance(template, ar_template.GenericTemplate):
            return template.apply(self, **kwargs)
        else:
            raise NotImplementedError(f"Unknown template type: {str(type(template))}")

    def _apply_element_template(self, template: ar_template.ElementTemplate, kwargs: dict):
        """
        Wrapper for element templates.

        Before apply method is called:
        * Make sure dependencies have been created
        * Make sure the necessary package has been created
        * Make sure the element doesn't already exists in the package

        After apply method returns:
         * Adds the newly created element to the package
        """
        dependencies = None
        if template.depends is not None:
            dependencies = self._create_dependencies(template.depends)
        package_ref = self.get_package_ref_by_role(template.namespace_name, template.package_role)
        package = self.make_packages(package_ref)
        elem = package.find(template.element_name)
        if elem is None:
            elem = template.apply(self, depends=dependencies, **kwargs)
            package.append(elem)
        return elem

    def _create_dependencies(self, dependencies: list[ar_template.TemplateBase]) -> list[Any]:
        items = []
        for dependency in dependencies:
            items.append(self.apply(dependency))
        return items
