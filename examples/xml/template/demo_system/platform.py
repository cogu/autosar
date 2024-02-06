"""
Platform types
"""

from . import factory

NAMESPACE = "AUTOSAR_Platform"


class BaseTypes:
    """
    Base types
    """

    boolean = factory.SwBaseTypeTemplate("boolean", NAMESPACE, 8, "BOOLEAN", "boolean")
    uint8 = factory.SwBaseTypeTemplate("uint8", NAMESPACE, 8, "uint8")
    uint16 = factory.SwBaseTypeTemplate("uint16", NAMESPACE, 16, "uint16")
    uint32 = factory.SwBaseTypeTemplate("uint32", NAMESPACE, 32, "uint32")
    uint64 = factory.SwBaseTypeTemplate("uint64", NAMESPACE, 64, "uint64")
    sint8 = factory.SwBaseTypeTemplate("sint8", NAMESPACE, 8, "2C", "sint8")
    sint16 = factory.SwBaseTypeTemplate("sint16", NAMESPACE, 16, "2C", "sint16")
    sint32 = factory.SwBaseTypeTemplate("sint32", NAMESPACE, 32, "2C", "sint32")
    sint64 = factory.SwBaseTypeTemplate("sint64", NAMESPACE, 64, "2C", "sint64")


class ImplementationTypes:
    """
    Implementation data types
    """

    _boolean_constraint = factory.DataConstraintInternalTemplate("boolean_DataConstr", NAMESPACE, 0, 1)
    _uint8_constraint = factory.DataConstraintInternalTemplate("uint8_DataConstr", NAMESPACE, 0, 255)
    _uint16_constraint = factory.DataConstraintInternalTemplate("uint16_DataConstr", NAMESPACE, 0, 65535)
    _uint32_constraint = factory.DataConstraintInternalTemplate("uint32_DataConstr", NAMESPACE, 0, 4294967295)
    _uint64_constraint = factory.DataConstraintInternalTemplate("uint64_DataConstr", NAMESPACE,
                                                                0, 18446744073709551615)
    _boolean_compumethod = factory.CompuMethodEnumTemplate("boolean_CompuMethod", NAMESPACE, ["FALSE", "TRUE"])

    boolean = factory.ImplementationValueTypeTemplate("boolean", NAMESPACE, BaseTypes.boolean, _boolean_constraint,
                                                      _boolean_compumethod, type_emitter="Platform_Type")
    uint8 = factory.ImplementationValueTypeTemplate("uint8", NAMESPACE, BaseTypes.uint8, _uint8_constraint,
                                                    type_emitter="Platform_Type")
    uint16 = factory.ImplementationValueTypeTemplate("uint16", NAMESPACE, BaseTypes.uint16, _uint16_constraint,
                                                     type_emitter="Platform_Type")
    uint32 = factory.ImplementationValueTypeTemplate("uint32", NAMESPACE, BaseTypes.uint32, _uint32_constraint,
                                                     type_emitter="Platform_Type")
    uint64 = factory.ImplementationValueTypeTemplate("uint64", NAMESPACE, BaseTypes.uint64, _uint64_constraint,
                                                     type_emitter="Platform_Type")
