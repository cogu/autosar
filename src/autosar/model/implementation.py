"""
Application model
"""
from typing import Any, Iterator
from collections import deque
from autosar.xml import Workspace
import autosar.xml.element as ar_element
import autosar.model.element as rte_element
import autosar.model.enumeration as rte_enumeration


class Node:
    """
    Node used for type dependency trees
    """

    def __init__(self, data: rte_element.Element) -> None:
        self.data = data
        self.children = []

    def add_child(self, child: "Node"):
        """
        Adds node to our list of childredn
        """
        self.children.append(child)


class ImplementationModel:
    """
    Implementation model
    Needs an assigned XML workspace to pull elements from as needed
    """

    def __init__(self, workspace: Workspace) -> None:
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
                if element.category == "ARRAY":
                    return self._create_array_type_from_element(element)
                if element.category == "STRUCTURE":
                    return self._create_struct_type_from_element(element)
                if element.category == "DATA_REFERENCE":
                    return self._create_ptr_type_from_element(element)
                raise NotImplementedError("ImplementationDataType::" + str(element.category))
            else:
                raise NotImplementedError(str(type(element)))
        return self.data_types[str(elem_ref)]

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
        scalar_type = rte_element.ScalarType(str(elem_ref),
                                             element.name,
                                             base_type,
                                             symbol,
                                             type_emitter=element.type_emitter)
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

    def _create_array_type_from_element(self, element: ar_element.ImplementationDataType) -> rte_element.ArrayType:
        elem_ref = str(element.ref())
        symbol = None
        if element.symbol_props is not None:
            symbol = element.symbol_props.symbol
        data_type = rte_element.ArrayType(elem_ref, element.name, symbol_name=symbol, type_emitter=element.type_emitter)
        last_element = element.sub_elements[-1]
        if last_element.category == "VALUE":
            sub_element = self._create_array_type_element_from_scalar_type(elem_ref, last_element)
        elif last_element.category == "TYPE_REFERENCE":
            sub_element = self._create_array_type_element_from_ref_type(elem_ref, last_element)
        else:
            raise NotImplementedError(last_element.category)
        if last_element.array_impl_policy is not None:
            sub_element.impl_policy = rte_enumeration.ArrayImplPolicy(last_element.array_impl_policy)
        if last_element.array_size_handling is not None:
            sub_element.size_handling = rte_enumeration.ArraySizeHandling(last_element.array_size_handling)
        if last_element.array_size_semantics is not None:
            sub_element.size_semantics = rte_enumeration.ArraySizeSemantics(last_element.array_size_semantics)
        data_type.sub_elements.append(sub_element)
        for ar_sub_elem in reversed(element.sub_elements[:-1]):
            xml_ref = elem_ref + "/" + ar_sub_elem.name
            assert isinstance(xml_ref.array_size, int)
            rte_sub_element = rte_element.ArrayTypeElement(xml_ref, ar_sub_elem.name, ar_sub_elem.array_size)
            data_type.sub_elements.insert(0, rte_sub_element)
        self.data_types[str(elem_ref)] = data_type
        return data_type

    def _create_array_type_element_from_scalar_type(self,
                                                    parent_ref: str,
                                                    element: ar_element.ImplementationDataTypeElement
                                                    ) -> rte_element.ArrayTypeElement:
        element_ref = parent_ref + "/" + element.name
        sw_data_def_props = element.sw_data_def_props
        base_type = self.create_from_ref(sw_data_def_props[0].base_type_ref, False)
        scalar_type = rte_element.ScalarType(element_ref,
                                             element.name,
                                             base_type)
        assert isinstance(element.array_size, int)
        return rte_element.ArrayTypeElement(element_ref,
                                            element.name,
                                            element.array_size,
                                            scalar_type)

    def _create_array_type_element_from_ref_type(self,
                                                 parent_ref: str,
                                                 element: ar_element.ImplementationDataTypeElement
                                                 ) -> rte_element.ArrayTypeElement:
        element_ref = parent_ref + "/" + element.name
        sw_data_def_props = element.sw_data_def_props
        impl_type = self.create_from_ref(sw_data_def_props[0].impl_data_type_ref, False)
        ref_type = rte_element.RefType(element_ref, element.name, impl_type)
        assert isinstance(element.array_size, int)
        return rte_element.ArrayTypeElement(element_ref,
                                            element.name,
                                            element.array_size,
                                            ref_type)

    def _create_struct_type_from_element(self, element: ar_element.ImplementationDataType) -> rte_element.RecordType:
        elem_ref = str(element.ref())
        symbol = None
        if element.symbol_props is not None:
            symbol = element.symbol_props.symbol
        data_type = rte_element.RecordType(elem_ref,
                                           element.name,
                                           symbol_name=symbol,
                                           type_emitter=element.type_emitter)
        for ar_sub_elem in element.sub_elements:
            if ar_sub_elem.category == "VALUE":
                sub_element = self._create_struct_type_element_from_scalar_type(elem_ref, ar_sub_elem)
            elif ar_sub_elem.category == "TYPE_REFERENCE":
                sub_element = self._create_struct_type_element_from_ref_type(elem_ref, ar_sub_elem)
            else:
                raise NotImplementedError(ar_sub_elem.category)
            data_type.sub_elements.append(sub_element)
        self.data_types[str(elem_ref)] = data_type
        return data_type

    def _create_struct_type_element_from_scalar_type(self,
                                                     parent_ref: str,
                                                     element: ar_element.ImplementationDataTypeElement
                                                     ) -> rte_element.ArrayTypeElement:
        element_ref = parent_ref + "/" + element.name
        sw_data_def_props = element.sw_data_def_props
        base_type = self.create_from_ref(sw_data_def_props[0].base_type_ref, False)
        scalar_type = rte_element.ScalarType(element_ref,
                                             element.name,
                                             base_type)
        return rte_element.RecordTypeElement(element_ref,
                                             element.name,
                                             scalar_type)

    def _create_struct_type_element_from_ref_type(self,
                                                  parent_ref: str,
                                                  element: ar_element.ImplementationDataTypeElement
                                                  ) -> rte_element.ArrayTypeElement:
        element_ref = parent_ref + "/" + element.name
        sw_data_def_props = element.sw_data_def_props
        impl_type = self.create_from_ref(sw_data_def_props[0].impl_data_type_ref, False)
        ref_type = rte_element.RefType(element_ref, element.name, impl_type)
        return rte_element.RecordTypeElement(element_ref,
                                             element.name,
                                             ref_type)

    def _create_ptr_type_from_element(self, element: ar_element.ImplementationDataType) -> rte_element.PointerType:
        elem_ref = str(element.ref())
        symbol = None
        if element.symbol_props is not None:
            symbol = element.symbol_props.symbol
        ptr_target_props: ar_element.SwPointerTargetProps = element.sw_data_def_props[0].ptr_target_props
        if ptr_target_props.target_category == "VALUE":
            target_type = self.create_from_ref(ptr_target_props.sw_data_def_props[0].base_type_ref, False)
        elif ptr_target_props.target_category == "TYPE_REFERENCE":
            target_type = self.create_from_ref(ptr_target_props.sw_data_def_props[0].impl_data_type_ref, False)
        else:
            raise NotImplementedError
        data_type = rte_element.PointerType(elem_ref,
                                            element.name,
                                            target_type,
                                            symbol_name=symbol,
                                            type_emitter=element.type_emitter)
        self.data_types[str(elem_ref)] = data_type
        return data_type

    def _create_tree_node(self, data_type: rte_element.Element) -> Node:
        node = Node(data_type)
        if isinstance(data_type, rte_element.BaseType):
            pass
        elif isinstance(data_type, rte_element.ScalarType):
            node.add_child(self._create_tree_node(data_type.base_type))
        elif isinstance(data_type, rte_element.RefType):
            node.add_child(self._create_tree_node(data_type.impl_type))
        elif isinstance(data_type, rte_element.ArrayType):
            last_element: rte_element.ArrayTypeElement = data_type.sub_elements[-1]
            self._process_array_or_record_element_tree_node(node, last_element.data_type)
        elif isinstance(data_type, rte_element.RecordType):
            for element in data_type.sub_elements:
                self._process_array_or_record_element_tree_node(node, element.data_type)
        else:
            raise NotImplementedError(str(type(data_type)))
        return node

    def _process_array_or_record_element_tree_node(self, node: Node, element: rte_element.Element) -> None:
        if isinstance(element, rte_element.ScalarType):
            pass  # Arrays and records/structs use the native declaration directly instead of the base type name
        elif isinstance(element, rte_element.RefType):
            node.add_child(self._create_tree_node(element.impl_type))
        else:
            raise NotImplementedError(str(type(element)))
