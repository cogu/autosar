"""
Application model
"""
from typing import Any
import autosar.xml
import autosar.xml.element as ar_element
import autosar.model.element as rte_element


class Application:
    """
    Application model
    Needs an assigned XML workspace to pull elements from as needed
    """

    def __init__(self, workspace: autosar.xml.Workspace) -> None:
        self.workspace = workspace
        self.base_types = {}
        self.implementation_types = {}

    def create_from_ref(self, ref: ar_element.BaseRef) -> Any:
        """
        Creates new application element from reference
        """
        element = self.workspace.find(str(ref))
        if element is None:
            raise KeyError(f"Invalid reference: {str(ref)}")
        return self.create_from_element(element)

    def create_from_element(self, element: ar_element.ARElement) -> Any:
        """
        Creates new application element from xml-based element
        """
        if isinstance(element, ar_element.SwBaseType):
            return self._create_base_type(element.name, str(element.ref()), element.native_declaration)
        elif isinstance(element, ar_element.ImplementationDataType):
            assert isinstance(element.category, str)
            if element.category == "VALUE":
                return self._create_scalar_type_from_element(element)
            else:
                raise NotImplementedError("ImplementationDataType::" + str(element.category))
        else:
            raise NotImplementedError(str(type(element)))

    def _create_base_type(self,
                          name: str,
                          key: str,
                          native_declaration: str | None = None) -> rte_element.BaseType:
        """
        Creates new Base type and adds it to internal model using the given key.
        The expected key is the reference in underlying XML workspace.
        """
        if name in self.base_types:
            # TODO: Check for compatibility here instead of throwing exception
            raise KeyError("BaseType with name already exist")
        element = rte_element.BaseType(name, native_declaration)
        self.base_types[key] = element
        return element

    def _create_scalar_type_from_element(self, element: ar_element.ImplementationDataType) -> rte_element.ScalarType:
        """
        Creates new DataType based on properties in the given XML element
        """
        elem_ref = element.ref()
        sw_data_def_props = element.sw_data_def_props
        base_type = self.create_from_ref(sw_data_def_props[0].base_type_ref)
        symbol = None
        if element.symbol_props is not None:
            symbol = element.symbol_props.symbol
        scalar_type = rte_element.ScalarType(element.name, base_type, symbol)
        self.implementation_types[str(elem_ref)] = scalar_type
        return scalar_type
