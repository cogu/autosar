"""
Application model
"""
from typing import Any, Iterator
from collections import deque
import autosar.xml
import autosar.xml.element as ar_element
import autosar.model.element as rte_element


class Node:
    """
    Node used for type dependency trees
    """

    def __init__(self, data: rte_element.DataType) -> None:
        self.data = data
        self.children = []

    def add_child(self, child: "Node"):
        """
        Adds node to our list of childredn
        """
        self.children.append(child)


class Application:
    """
    Application model
    Needs an assigned XML workspace to pull elements from as needed
    """

    def __init__(self, workspace: autosar.xml.Workspace) -> None:
        self.workspace = workspace
        self.data_types = {}
        self.source_type_refs = set()

    def create_from_ref(self, ref: ar_element.BaseRef, is_source: bool = True) -> Any:
        """
        Creates new application element from reference
        """
        element = self.workspace.find(str(ref))
        if element is None:
            raise KeyError(f"Invalid reference: {str(ref)}")
        return self.create_from_element(element, is_source)

    def create_from_element(self, element: ar_element.ARElement, is_source: bool = True) -> Any:
        """
        Creates new application element from xml-based element
        """
        elem_ref = element.ref()

        if str(elem_ref) not in self.data_types:
            if is_source:
                self.source_type_refs.add(str(elem_ref))
            if isinstance(element, ar_element.SwBaseType):
                return self._create_base_type(element)
            elif isinstance(element, ar_element.ImplementationDataType):
                assert isinstance(element.category, str)
                if element.category == "VALUE":
                    return self._create_scalar_type_from_element(element)
                if element.category == "TYPE_REFERENCE":
                    return self._create_ref_type_from_element(element)
                else:
                    raise NotImplementedError("ImplementationDataType::" + str(element.category))
            else:
                raise NotImplementedError(str(type(element)))

    def gen_type_dependency_trees(self) -> list[Node]:
        """
        Returns a list of root nodes (tree structures) which shows how data types depend on each other
        """
        dependency_trees = []
        for type_ref in sorted(self.source_type_refs):
            data_type = self.data_types[type_ref]
            dependency_trees.append(self._create_tree_node(data_type))
        return dependency_trees

    def get_type_creation_order(self, root: Node) -> Iterator[Node]:
        """
        Given a type dependency tree, returns the creation order as an iterator.

        Apply the reverse level order algorithm to solve the problem
        """
        que = deque()
        que.append(root)
        result = []
        while que:
            node: Node = que.popleft()
            result.append(node)
            for child in reversed(node.children):
                que.append(child)
        return reversed(result)

    def _create_base_type(self, element: ar_element.SwBaseType) -> rte_element.BaseType:
        """
        Creates new Base type and adds it to internal model using the given key.
        The expected key is the reference in underlying XML workspace.
        """
        elem_ref = element.ref()
        element = rte_element.BaseType(str(elem_ref), element.name, element.native_declaration)
        self.data_types[str(elem_ref)] = element
        return element

    def _create_scalar_type_from_element(self, element: ar_element.ImplementationDataType) -> rte_element.ScalarType:
        """
        Creates new scalar data type based on properties in the given XML element
        """
        elem_ref = element.ref()
        sw_data_def_props = element.sw_data_def_props
        base_type = self.create_from_ref(sw_data_def_props[0].base_type_ref, False)
        symbol = None
        if element.symbol_props is not None:
            symbol = element.symbol_props.symbol
        scalar_type = rte_element.ScalarType(str(elem_ref), element.name, base_type, symbol, type_emitter=element.type_emitter)
        self.data_types[str(elem_ref)] = scalar_type
        return scalar_type

    def _create_ref_type_from_element(self, element: ar_element.ImplementationDataType) -> rte_element.ScalarType:
        """
        Creates new reference data type based on properties in the given XML element
        """
        elem_ref = element.ref()
        sw_data_def_props = element.sw_data_def_props
        impl_type = self.create_from_ref(sw_data_def_props[0].impl_data_type_ref, False)
        symbol = None
        if element.symbol_props is not None:
            symbol = element.symbol_props.symbol
        ref_type = rte_element.RefType(str(elem_ref), element.name, impl_type, symbol)
        self.data_types[str(elem_ref)] = ref_type
        return ref_type

    def _create_tree_node(self, data_type: rte_element.DataType) -> Node:
        node = Node(data_type)
        if isinstance(data_type, rte_element.BaseType):
            pass
        elif isinstance(data_type, rte_element.ScalarType):
            node.add_child(self._create_tree_node(data_type.base_type))
        elif isinstance(data_type, rte_element.RefType):
            node.add_child(self._create_tree_node(data_type.impl_type))
        else:
            raise NotImplementedError(str(type(data_type)))
        return node
