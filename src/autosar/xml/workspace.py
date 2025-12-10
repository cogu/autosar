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
    Used to store settings about a document creation action
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


class PackageToDocumentMapping:
    """
    Used to store settings for a package-to-document-mapping action.
    This is used to split a package into multiple documents based on element types
    """

    def __init__(self,
                 package_ref: str,
                 element_types: type | tuple[type],
                 suffix_filters: str | list[str]):
        self.package_ref: str = package_ref
        self.element_types: type | tuple[type] = element_types
        self.suffix_filters: list[str] = []
        if isinstance(suffix_filters, str):
            self.element_types.append(suffix_filters)
        else:
            for suffix_filter in suffix_filters:
                assert isinstance(suffix_filter, str)
                self.suffix_filters.append(suffix_filter)


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


class Workspace(ar_element.PackageCollection):
    """
    Workspace
    """

    def __init__(self, config_file_path: str | None = None, document_root: str | None = None) -> None:
        super().__init__(behavior_settings=ar_element.BehaviorSettings())
        self.namespaces: dict[str, Namespace] = {}
        self.documents: list[DocumentConfig] = []
        self.document_mappings: list[PackageToDocumentMapping] = []
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
        Returns previously created namespace
        """
        if name in self.namespaces:
            return self.namespaces[name]
        else:
            raise KeyError(f"No such namespace: {name}")

    def get_package_ref_by_role(self, namespace_name: str, role: ar_enum.PackageRole | str):
        """
        Returns package reference based on role in given namespace
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

    def create_package_map(self, mapping: dict[str, str]) -> None:
        """
        Creates a basic package map without a namespace.

        Use in conjunction with the add_element and find_element methods.

        """
        self.package_map.clear()
        for package_key, package_ref in mapping.items():
            self.package_map[package_key] = self.make_packages(package_ref)

    def update_package_map(self, mapping: dict[str, str]) -> None:
        """
        Update basic package map without clearing it.

        Use in conjunction with the add_element and find_element methods.
        """
        for package_key, package_ref in mapping.items():
            self.package_map[package_key] = self.make_packages(package_ref)

    def add_element(self, package_key: str, element: ar_element.ARObject):
        """
        Adds element to package specified by package_key

        Only use after calling create_package_map.
        """
        if len(self.package_map) == 0:
            raise RuntimeError("Internal package map not initialized")
        self.package_map[package_key].append(element)

    def find_element(self, package_key: str, element_name: str) -> ar_element.ARElement | None:
        """
        Finds an element in the package referenced by package_key.

        Only use after calling create_package_map.
        """
        if len(self.package_map) == 0:
            raise RuntimeError("Internal package map not initialized")
        return self.package_map[package_key].find(element_name)

    def get_package(self, package_key: str) -> ar_element.Package:
        """
        Returns the package referenced by package_key.

        Only use after calling create_package_map.
        """
        if len(self.package_map) == 0:
            raise RuntimeError("Internal package map not initialized")
        return self.package_map[package_key]

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

    def create_document_mapping(self,
                                package_ref: str,
                                element_types: type | tuple[type],
                                suffix_filters: str | list[str]):
        """
        Splits a package into multiple documents. The document name(s) equal the short-name of the found element(s)
        """
        self.document_mappings.append(PackageToDocumentMapping(package_ref, element_types, suffix_filters))

    def set_document_root(self, directory: str) -> None:
        """
        Sets root directory where documents are written
        """
        self.document_root = directory

    def write_documents(self, schema_version=ar_base.DEFAULT_SCHEMA_VERSION) -> None:
        """
        Writes all documents to file system
        """
        writer = Writer()
        for document_config in self.documents:
            self._write_document_from_config(writer, schema_version, document_config)
        for package_document_mapping in self.document_mappings:
            self._gen_package_to_document_mapping(writer, schema_version, package_document_mapping)

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
            document_mapping = config.get("document_mapping", None)
            if document_mapping is not None:
                for mapping in document_mapping.values():
                    self._create_document_mapping_from_config(mapping)
            behavior_settings = config.get("behavior", None)
            if behavior_settings is not None:
                self.behavior_settings.update(behavior_settings)

    def _write_document_from_config(self,
                                    writer: Writer,
                                    schema_version: int,
                                    document_config: DocumentConfig) -> None:
        document = document_config.document
        file_path = document_config.file_path
        package_refs = document_config.package_refs
        document.schema_version = schema_version
        for package_ref in package_refs:
            package = self.find(package_ref)
            if package is not None:
                if not isinstance(package, ar_element.Package):
                    raise ValueError(f"'{package_ref}' does not reference a package element")
            document.append(package)
        if self.document_root is not None:
            file_path = os.path.join(self.document_root, file_path)
        writer.write_file(document, file_path)

    def _gen_package_to_document_mapping(self,
                                         writer: Writer,
                                         schema_version: int,
                                         mapping: PackageToDocumentMapping) -> None:
        package = self.find(mapping.package_ref)
        if package is not None:
            if not isinstance(package, ar_element.Package):
                raise ValueError(f"'{mapping.package_ref}' does not reference a package element")
            element_map = {}
            type_matched_elements = {}
            for element in package.elements:
                element_map[element.name] = element
                if isinstance(element, mapping.element_types):
                    type_matched_elements[element.name] = element
            for matched_element in type_matched_elements.values():
                document_name = matched_element.name + ".arxml"
                element_list = [matched_element]
                if mapping.suffix_filters:
                    for suffix in mapping.suffix_filters:
                        if len(suffix) > 0:
                            name = matched_element.name + suffix
                            extra_element = element_map.get(name, None)
                            if extra_element is not None:
                                element_list.append(extra_element)
                document = ar_document.Document(schema_version=schema_version)
                new_package = document.make_packages(str(package.ref()))
                for element in sorted(element_list, key=lambda x: x.name):
                    new_package.append(element)
                if self.document_root is not None:
                    file_path = os.path.join(self.document_root, document_name)
                else:
                    file_path = document_name
                writer.write_file(document, file_path)

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

    def _create_document_mapping_from_config(self, mapping: dict):
        """
        Creates a document object mapping object from config object
        """
        package_ref: str = mapping.get("package_ref", None)
        element_types: list[type] = []
        suffix_filters: list[str] = []
        elem_names: list[str] = []
        if package_ref is None:
            raise KeyError("A document mapping must define 'package_ref'")
        value = mapping.get("element_types")
        if value is None:
            raise KeyError("A document mapping must define 'element_types'")
        if isinstance(value, str):
            elem_names.append(value)
        elif isinstance(value, list):
            for item in value:
                assert isinstance(item, str)
                elem_names.append(item)
        else:
            raise ValueError(f"element_types: Invalid type '{str(type(value))}'")
        for elem_name in elem_names:
            try:
                element_types.append(getattr(ar_element, elem_name))
            except AttributeError as exc:
                raise ValueError(f"element_types: '{elem_name}' is not a valid element name") from exc
        if len(element_types) == 0:
            raise ValueError("element_types: At least one element type must be given")
        value = mapping.get("suffix_filters")
        if value is not None:
            if isinstance(value, str):
                suffix_filters.append(value)
            elif isinstance(value, list):
                for item in value:
                    assert isinstance(item, str)
                    suffix_filters.append(item)
            else:
                raise ValueError(f"suffix_filters: Invalid type '{str(type(value))}'")
        self.create_document_mapping(package_ref, tuple(element_types), suffix_filters)

    def _apply_element_template(self, template: ar_template.ElementTemplate, kwargs: dict) -> ar_element.ARElement:
        """
        Wrapper for element templates.

        Before create-method is called:
        * Make sure dependencies have been created
        * Make sure the necessary package has been created
        * Make sure the element doesn't already exists in the package

        After create-method is called:
          if template.append_to_package is True (default):
            Adds the created element to the given package
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
                elem = template.create(package, self, depends_map, **kwargs)
                if elem is None:
                    raise TypeError(f"{template.element_name}: Create-method did not return an element")
                if not isinstance(elem, ar_element.ARElement):
                    raise TypeError(f"{str(type(elem))}: Class is not an ARElement")
                if template.append_to_package:
                    package.append(elem)
            return elem
        else:
            raise TypeError(f"Expected Package, got {str(type(package))}")

    def _create_dependencies(self, dependencies: list[ar_template.TemplateBase]
                             ) -> dict[str, ar_element.ARElement]:
        item_map = {}
        for dependency in dependencies:
            elem = self.apply(dependency)
            if not isinstance(elem, ar_element.ARElement):
                raise TypeError(f"{str(type(elem))}: Class is not an ARElement")
            if not hasattr(elem, "ref"):
                raise NotImplementedError(f"{str(type(elem))}: Class is missing its ref method")
            item_map[str(elem.ref())] = elem
        return item_map
