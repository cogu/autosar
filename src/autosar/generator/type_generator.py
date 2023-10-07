"""
RTE type generator
Requires cfile v0.3.0
"""
import os
from typing import Iterator
import cfile
import autosar.model.element as rte_element
from autosar.model import application

C = cfile.CFactory()


class TypeGenerator:
    """
    RTE type generator class
    """

    def __init__(self, app: application.Application):
        self.application = app
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
        code.append(C.ifndef("__cplusplus", adjust=1))
        code.append(C.line(C.extern("C")))
        code.append(C.line("{"))
        code.append(C.endif(adjust=1))
        code.append(C.blank())
        code.append(C.block_comment("*             INCLUDES             *", width=35))
        code.append(C.include("Rte.h"))
        code.append(C.blank())
        code.append(C.block_comment("*     CONSTANTS AND DATA TYPES     *", width=35))
        code.append(C.blank())
        code.extend(self._gen_type_defs(self.gen_data_type_creation_order()))
        code.append(C.blank())
        code.append(C.ifndef("__cplusplus", adjust=1))
        code.append(C.line(C.extern("C")))
        code.append(C.line("}"))
        code.append(C.endif(adjust=1))
        code.append([C.endif(), C.line_comment(" " + include_guard)])
        return code

    def gen_data_type_creation_order(self) -> list:
        """
        Resolves type definition order
        """
        instance_refs = set()
        result = []
        for root_node in self.application.gen_type_dependency_trees():
            node: application.Node
            for node in self.application.get_type_creation_order(root_node):
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

    def _gen_type_defs(self, data_types: Iterator[rte_element.DataType]) -> cfile.core.Sequence:
        """
        Generates typedefs section
        """
        code = C.sequence()
        for data_type in data_types:
            if isinstance(data_type, rte_element.BaseType):
                code.append(C.statement(C.typedef(data_type.name, data_type.native_declaration)))
            elif isinstance(data_type, rte_element.ScalarType):
                code.append(C.statement(C.typedef(data_type.name, data_type.base_type.name)))
            elif isinstance(data_type, rte_element.RefType):
                code.append(C.statement(C.typedef(data_type.name, data_type.impl_type.name)))
            else:
                raise NotImplementedError(str(type(data_type)))
        return code

    def write_type_defs_str(self) -> str:
        """
        Returns typedefs section as a string.
        Used primarily for unit test validation
        """
        code = self._gen_type_defs(self.gen_data_type_creation_order())
        writer = cfile.Writer(cfile.StyleOptions())
        return writer.write_str(code)
