"""
AUTOSAR XML Workspace
"""
import posixpath
import os
from typing import Any
import autosar.base as ar_base
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
import autosar.xml.template as ar_template
import autosar.xml.document as ar_document
from autosar.xml.writer import Writer
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class DocumentConfig:
    """
    Internal class used during document creation
    """

    def __init__(self, file_path: str, package_refs: list[str] | str | None = None) -> None:
        self.document = ar_document.Document()
        self.file_path = file_path
        self.package_refs: list[str] = []
        if isinstance(package_refs, str):
            self.package_refs.append(package_refs)
        else:
            for package_ref in package_refs:
                assert isinstance(package_ref, str)
                self.package_refs.append(package_ref)


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

    def __init__(self, config_file_path: str | None = None, document_root: str | None = None) -> None:
        self.namespaces: dict[str, Namespace] = {}
        self.packages: list[ar_element.Package] = []
        self._package_dict: dict[str, ar_element.Package] = {}  # Each key is the name of an actual package
        self.documents: list[DocumentConfig] = []
        self.document_root = document_root
        self.package_map: dict[str, ar_element.Package] = {}  # Each key is user-defined
        if config_file_path is not None:
            self.load_config(config_file_path)

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

    def create_package(self, name: str, **kwargs) -> ar_element.Package:
        """
        Creates new package in workspace
        """
        if name in self._package_dict:
            return ValueError(f"Package with name '{name}' already exists")
        package = ar_element.Package(name, **kwargs)
        self.append(package)
        return package

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
            package = self._package_dict.get(parts[0], None)
            if package is None:
                package = self.create_package(parts[0])
            if len(parts[2]) > 0:
                package = package.make_packages(parts[2])
            result.append(package)
        return result[0] if len(result) == 1 else result

    def init_package_map(self, mapping: dict[str, str]) -> None:
        """
        Initializes an internally stored package map using key-value pairs.
        The key can be any (unique) name while each value must be a package reference.
        This function internally creates packages from dict-values calling the method
        make_packages.

        Use in conjunction with the add_element and find_element methods.

        Avoid manually calling make_packages if using this method.
        """
        self.package_map.clear()
        for package_key, package_ref in mapping.items():
            self.package_map[package_key] = self.make_packages(package_ref)

    def add_element(self, package_key: str, element: ar_element.ARObject):
        """
        Adds element to package specified by package_key

        Only use after calling init_package_map.
        """
        if len(self.package_map) == 0:
            raise RuntimeError("Internal package map not initialized")
        self.package_map[package_key].append(element)

    def find_element(self, package_key: str, element_name: str) -> ar_element.ARElement | None:
        """
        Finds an element in the package referenced by package_key.

        Only use after calling init_package_map.
        """
        if len(self.package_map) == 0:
            raise RuntimeError("Internal package map not initialized")
        return self.package_map[package_key].find(element_name)

    def get_package(self, package_key: str) -> ar_element.Package:
        """
        Returns the package referenced by package_key.

        Only use after calling init_package_map.
        """
        if len(self.package_map) == 0:
            raise RuntimeError("Internal package map not initialized")
        return self.package_map[package_key]

    def append(self, package: ar_element.Package):
        """
        Appends package to this worksapace
        """
        assert isinstance(package, ar_element.Package)
        self._package_dict[package.name] = package
        self.packages.append(package)
        package.parent = self

    def find(self, ref: str) -> ar_element.Identifiable | None:
        """
        Finds item by reference
        """
        if ref.startswith('/'):
            ref = ref[1:]
        parts = ref.partition('/')
        package = self._package_dict.get(parts[0], None)
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

    def create_document(self, file_path: str, packages: str | list[str] | None = None) -> None:
        """
        Creates a new document object and appends one or more packages to it.
        Use the write_documents method to write documents to file system
        """
        self.documents.append(DocumentConfig(file_path, packages))

    def set_document_root(self, directory: str) -> None:
        """
        Sets root directory where documents are written
        """
        self.document_root = directory

    def write_documents(self, scehema_version=ar_base.DEFAULT_SCHEMA_VERSION) -> None:
        """
        Writes all documents to file system
        """
        writer = Writer()
        for document_config in self.documents:
            document = document_config.document
            file_path = document_config.file_path
            package_refs = document_config.package_refs
            document.schema_version = scehema_version
            for package_ref in package_refs:
                package = self.find(package_ref)
                if package is not None:
                    if not isinstance(package, ar_element.Package):
                        raise ValueError(f"'{package_ref}' does not reference a package element")
                document.append(package)
            if self.document_root is not None:
                file_path = os.path.join(self.document_root, file_path)
            writer.write_file(document, file_path)

    def load_config(self, file_path: str) -> None:
        """
        Loads (.toml) config file into workspace
        """
        with open(file_path, "rb") as fp:  # pylint: disable=C0103
            config = tomllib.load(fp)
            namespace = config.get("namespace", None)
            if namespace is not None:
                for name, ns_config in namespace.items():
                    self._create_namespace_from_config(name, ns_config)
            document = config.get("document", None)
            if document is not None:
                for name, doc_config in document.items():
                    self._create_document_from_config(name, doc_config)

    def _create_namespace_from_config(self, name: str, config: dict):
        base_ref = None
        package_map = {}
        for key, value in config.items():
            if key == "base_ref":
                base_ref = value
            else:
                package_map[key] = value
        self.create_namespace(name, package_map, base_ref)

    def _create_document_from_config(self, name: str, config: str | list[str]):
        file_name = f"{name}.arxml"
        self.create_document(file_name, config.get("packages", None))

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
            depends_map = self._create_dependencies(template.depends)
        else:
            depends_map = None
        package_ref = self.get_package_ref_by_role(template.namespace_name, template.package_role)
        package: ar_element.Package = self.make_packages(package_ref)
        if isinstance(package, ar_element.Package):
            elem = package.find(template.element_name)
            if elem is None:
                element_ref = package_ref + "/" + template.element_name
                elem = template.create(element_ref, self, depends_map, **kwargs)
                assert isinstance(elem, ar_element.ARElement)
                package.append(elem)
            return elem
        raise TypeError(f"Expected Package, got {str(type(package))}")

    def _create_dependencies(self, dependencies: list[ar_template.TemplateBase]
                             ) -> dict[str, ar_element.ARElement]:
        item_map = {}
        for dependency in dependencies:
            elem = self.apply(dependency)
            assert isinstance(elem, ar_element.ARElement)
            assert hasattr(elem, "ref")
            item_map[str(elem.ref())] = elem
        return item_map
