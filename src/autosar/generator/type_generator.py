"""
RTE type generator
Requires cfile v0.3.2
"""
import os
from typing import Iterator
import cfile
import cfile.core
import autosar.model.element as rte_element
from autosar.model.implementation import ImplementationModel, Node

C = cfile.CFactory()


class TypeGenerator:
    """
    RTE type generator class
    """

    def __init__(self, implementation: ImplementationModel):
        self.implementation = implementation
        self.style = cfile.StyleOptions(break_before_braces=cfile.BreakBeforeBraces.ATTACH,
                                        pointer_alignment=cfile.Alignment.RIGHT)
        self.writer = cfile.Writer(self.style)

    def write_type_header_str(self) -> str:
        """
        Returns content of Rte_Type.h as a string
        """
        code = self._create_code_sequence()
        writer = cfile.Writer(cfile.StyleOptions())
        return writer.write_str(code)

    def write_type_header(self, dest_dir: str = '.') -> None:
        """
        Generates Rte_Type.h in destination directory
        """
        file_path = os.path.join(dest_dir, "Rte_Type.h")
        writer = cfile.Writer(cfile.StyleOptions())
        code = self._create_code_sequence()
        writer.write_file(code, file_path)

    def _create_code_sequence(self) -> cfile.core.Sequence:

        include_guard = "RTE_TYPE_H_"

        code = C.sequence()
        code.append(C.ifndef(include_guard))
        code.append(C.define(include_guard))
        code.append(C.blank())
        code.append(C.ifdef("__cplusplus"))
        code.append(C.line(C.extern("C")))
        code.append(C.line("{"))
        code.append(C.endif())
        code.append(C.blank())
        code.append(C.block_comment("*             INCLUDES             *", width=35))
        code.append(C.include("Rte.h"))
        code.append(C.blank())
        code.append(C.block_comment("*     CONSTANTS AND DATA TYPES     *", width=35))
        code.append(C.blank())
        code.extend(self._gen_type_defs(self.gen_data_type_creation_order()))
        code.append(C.blank())
        code.append(C.ifdef("__cplusplus"))
        code.append(C.line("}"))
        code.append([C.endif(), C.line_comment(" __cplusplus")])
        code.append([C.endif(), C.line_comment(" " + include_guard)])
        return code

    def gen_data_type_creation_order(self) -> list:
        """
        Resolves type definition order
        """
        instance_refs = set()
        result = []
        for root_node in self.implementation.gen_type_dependency_trees():
            node: Node
            for node in self.implementation.get_type_creation_order(root_node):
                data_type = node.data
                if data_type.ref not in instance_refs:
                    instance_refs.add(data_type.ref)
                    # Ignore BaseTypes without native declaration
                    if isinstance(data_type, rte_element.BaseType) and not data_type.native_declaration:
                        continue
                    # Ignore ImplementationTypes with non-RTE type emitter
                    if isinstance(data_type, rte_element.ImplementationType) and (
                            data_type.type_emitter is not None and data_type.type_emitter.upper() != "RTE"):
                        continue
                    result.append(data_type)
        return result

    def write_type_defs_str(self) -> str:
        """
        Returns typedefs section as a string.
        Used primarily for unit test validation
        """
        code = self._gen_type_defs(self.gen_data_type_creation_order())
        writer = cfile.Writer(cfile.StyleOptions())
        return writer.write_str(code)

    def _gen_type_defs(self, data_types: Iterator[rte_element.Element]) -> cfile.core.Sequence:
        """
        Generates typedefs section
        """
        code = C.sequence()
        for data_type in data_types:
            if isinstance(data_type, rte_element.BaseType):
                code.append(C.statement(C.declaration(C.typedef(data_type.name, data_type.native_declaration))))
            elif isinstance(data_type, rte_element.ScalarType):
                code.append(C.statement(C.declaration(C.typedef(data_type.name, data_type.base_type.name))))
            elif isinstance(data_type, rte_element.RefType):
                code.append(C.statement(C.declaration(C.typedef(data_type.name, data_type.impl_type.name))))
            elif isinstance(data_type, rte_element.ArrayType):
                code.append(self._gen_array_type_def(data_type))
            elif isinstance(data_type, rte_element.RecordType):
                code.extend(self._gen_record_type_def(data_type))
            else:
                raise NotImplementedError(str(type(data_type)))
        return code

    def _gen_array_type_def(self, data_type: rte_element.ArrayType) -> cfile.core.Statement:
        last_element = data_type.sub_elements[-1]
        if isinstance(last_element.data_type, rte_element.ScalarType):
            scalar_type: rte_element.ScalarType = last_element.data_type
            if scalar_type.base_type.native_declaration:
                target_type = C.type(scalar_type.base_type.native_declaration)
            else:
                target_type = C.type(scalar_type.base_type.name)
        elif isinstance(last_element.data_type, rte_element.RefType):
            target_type = C.type(last_element.data_type.impl_type.name)
        else:
            raise NotImplementedError(str(type(last_element.data_type)))
        return C.statement(C.declaration(C.typedef(data_type.name, target_type, array=last_element.array_size)))

    def _gen_record_type_def(self, data_type: rte_element.RecordType) -> cfile.core.Statement:
        members = []
        for element in data_type.sub_elements:
            if isinstance(element.data_type, rte_element.ScalarType):
                scalar_type: rte_element.ScalarType = element.data_type
                if scalar_type.base_type.native_declaration:
                    target_type = C.type(scalar_type.base_type.native_declaration)
                else:
                    target_type = C.type(scalar_type.base_type.name)
            elif isinstance(element.data_type, rte_element.RefType):
                target_type = C.type(element.data_type.impl_type.name)
            else:
                raise NotImplementedError(str(type(element.data_type)))
            members.append(C.struct_member(element.name, target_type))
        struct_name = "Rte_struct_" + data_type.name
        code = C.sequence()
        struct = C.struct(struct_name, members)
        code.append(C.statement(C.declaration(struct)))
        code.append(C.statement(C.declaration(C.typedef(data_type.name, struct))))
        return code
