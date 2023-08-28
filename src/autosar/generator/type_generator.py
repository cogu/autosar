"""
RTE type generator
Requires cfile v0.3.0 (unreleased)
"""
import os
import cfile
import autosar.model.element as rte_element

C = cfile.CFactory()


class TypeGenerator:
    """
    RTE type generator class
    """

    def __init__(self, application):
        self.application = application
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
        code.extend(self._gen_type_defs())
        code.append(C.blank())
        code.append(C.ifndef("__cplusplus", adjust=1))
        code.append(C.line(C.extern("C")))
        code.append(C.line("}"))
        code.append(C.endif(adjust=1))
        code.append([C.endif(), C.line_comment(" " + include_guard)])
        return code

    def _gen_type_defs(self) -> cfile.core.Sequence:
        """
        Generates typedefs section
        """
        code = C.sequence()
        for data_type in self.application.base_types.values():
            if data_type.native_declaration:
                code.append(C.statement(C.typedef(data_type.name, data_type.native_declaration)))
        primitive_types = []
        array_types = []
        struct_types = []
        union_types = []

        for data_type in self.application.implementation_types.values():
            if isinstance(data_type, (rte_element.ScalarType, rte_element.RefType, rte_element.PointerType)):
                primitive_types.append(data_type)
            elif isinstance(data_type, rte_element.ArrayType):
                array_types.append(data_type)
            elif isinstance(data_type, rte_element.StructType):
                struct_types.append(data_type)
            elif isinstance(data_type, rte_element.UnionType):
                union_types.append(data_type)
            else:
                raise NotImplementedError(str(type(data_type)))
        for data_type in primitive_types:
            if isinstance(data_type, rte_element.ScalarType):
                code.append(C.statement(C.typedef(data_type.name, data_type.base_type.name)))
            else:
                raise NotImplementedError(str(type(data_type)))
        return code

    def write_type_defs_str(self) -> str:
        """
        Returns typedefs section as a string.
        Used primarily for unit test validation
        """
        code = self._gen_type_defs()
        writer = cfile.Writer(cfile.StyleOptions())
        return writer.write_str(code)
