"""
AUTOSAR XML Workspace
"""
import posixpath
from typing import Any
import autosar.base as ar_base
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
import autosar.xml.template as ar_template
import autosar.xml.document as ar_document
from autosar.xml.writer import Writer


class Namespace:
    """
    Namespace
    """

    def __init__(self, name: str, package_map: dict[str, str], base_ref: str | None = None) -> None:
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

    def __init__(self, config_file_path: str | None = None) -> None:
        self.namespaces: dict[str, Namespace] = {}
        self.packages: list[ar_element.Package] = []
        self._package_map: dict[str, ar_element.Package] = {}
        self.documents: list[tuple(ar_document.Document, str)] = []

    def create_namespace(self, name: str, package_map: dict[str, str], base_ref: str | None = None) -> None:
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

    def make_packages(self, *refs: list[str]) -> ar_element.Package | list[ar_element.Package]:
        """
        Recursively creates packages from reference(s)
        Returns a list of created packages.
        If only one argument is given it will return that package (not a list).
        """
        result = []
        for ref in refs:
            if ref.startswith('/'):
                ref = ref[1:]
            parts = ref.partition('/')
            package = self._package_map.get(parts[0], None)
            if package is None:
                package = self.create_package(parts[0])
            if len(parts[2]) > 0:
                package = package.make_packages(parts[2])
            result.append(package)
        return result[0] if len(result) == 1 else result

    def create_package(self, name: str, **kwargs) -> ar_element.Package:
        """
        Creates new package in workspace
        """
        if name in self._package_map:
            return ValueError(f"Package with name '{name}' already exists")
        package = ar_element.Package(name, **kwargs)
        self.append(package)
        return package

    def append(self, package: ar_element.Package):
        """
        Appends package to this worksapace
        """
        assert isinstance(package, ar_element.Package)
        self._package_map[package.name] = package
        self.packages.append(package)
        package.parent = self

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

    def create_document(self, file_path: str, packages: str | list[str]) -> ar_document.Document:
        """
        Creates a new document object and appends one or more packages to it.
        Use the write_documents method to write documents to file system
        """
        document = ar_document.Document()
        if isinstance(packages, str):
            package = self.find(packages)
            if package is None:
                raise ValueError(f"Invalid package reference: '{packages}'")
            document.append(package)
        else:
            for package_ref in packages:
                package = self.find(package_ref)
                if package is None:
                    raise ValueError(f"Invalid package reference: '{package_ref}'")
                document.append(package)
        self.documents.append((document, file_path))
        return document

    def write_documents(self, scehema_version=ar_base.DEFAULT_SCHEMA_VERSION) -> None:
        """
        Writes all documents to file system
        """
        writer = Writer()
        for (document, file_path) in self.documents:
            document.schema_version = scehema_version
            writer.write_file(document, file_path)

    def _apply_element_template(self, template: ar_template.ElementTemplate, kwargs: dict) -> ar_element.ARElement:
        """
        Wrapper for element templates.

        Before apply method is called:
        * Make sure dependencies have been created
        * Make sure the necessary package has been created
        * Make sure the element doesn't already exists in the package

        It's up to the implementer of the apply-method to call package.append to add the newly
        created element
        """
        if template.depends is not None:
            self._create_dependencies(template.depends)
        package_ref = self.get_package_ref_by_role(template.namespace_name, template.package_role)
        package: ar_element.Package = self.make_packages(package_ref)
        if isinstance(package, ar_element.Package):
            elem = package.find(template.element_name)
            if elem is None:
                elem = template.apply(package, self, **kwargs)
            return elem
        raise TypeError(f"Expected Package, got {str(type(package))}")

    def _create_dependencies(self, dependencies: list[ar_template.TemplateBase]) -> list[Any]:
        items = []
        for dependency in dependencies:
            items.append(self.apply(dependency))
        return items
