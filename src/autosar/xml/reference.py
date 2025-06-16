"""
AUTOSAR XML Reference classes
"""

from autosar.xml.base import BaseRef
import autosar.xml.enumeration as ar_enum


class SwBaseTypeRef(BaseRef):
    """
    SwBaseType reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.SW_BASE_TYPE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SW_BASE_TYPE}


class PackageRef(BaseRef):
    """
    References to AR-PACKAGE--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.AR_PACKAGE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.AR_PACKAGE}


class CompuMethodRef(BaseRef):
    """
    CompuMethod reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.COMPU_METHOD
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.COMPU_METHOD}


class FunctionPtrSignatureRef(BaseRef):
    """
    Function pointer signature reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.BSW_MODULE_ENTRY
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.BSW_MODULE_ENTRY}


class ImplementationDataTypeRef(BaseRef):
    """
    ImplementationDataType reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE}


class SwAddrMethodRef(BaseRef):
    """
    SwAddrMethod reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SW_ADDR_METHOD}


class DataConstraintRef(BaseRef):
    """
    DataConstraint reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.DATA_CONSTR
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.DATA_CONSTR}


class PhysicalDimensionRef(BaseRef):
    """
    PhysicalDimension reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.PHYSICAL_DIMENSION
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.PHYSICAL_DIMENSION}


class UnitRef(BaseRef):
    """
    DataConstraint reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.UNIT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.UNIT}


class IndexDataTypeRef(BaseRef):
    """
    IndexDataType reference
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE}


class ApplicationDataTypeRef(BaseRef):
    """
    Application data type reference
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE}


class ApplicationCompositeElementDataPrototypeRef(BaseRef):
    """
    References to AR:APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_ELEMENT,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_ELEMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT,
                }


class AutosarDataTypeRef(BaseRef):
    """
    References to AR:AUTOSAR-DATA-TYPE--SUBTYPES-ENUM
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_IMPLEMENTATION_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_DEFERRED_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_PRIMITIVE_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.AUTOSAR_DATA_TYPE,
                ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE}


class ConstantRef(BaseRef):
    """
    Reference to ConstantSpecification
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.CONSTANT_SPECIFICATION
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.CONSTANT_SPECIFICATION}


class VariableDataPrototypeRef(BaseRef):
    """
    Reference to VariableDataPrototype
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE}


class ParameterDataPrototypeRef(BaseRef):
    """
    Reference to ParameterDataPrototype
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE}


class ApplicationErrorRef(BaseRef):
    """
    Reference to ApplicationError
    tag variants: 'POSSIBLE-ERROR-REF'
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.APPLICATION_ERROR) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ERROR}


class ModeDeclarationRef(BaseRef):
    """
    Reference to ModeDeclaration
    tag variants: 'TARGET-MODE-DECLARATION-REF' | 'INITIAL-MODE-REF' |
                  'FIRST-MODE-REF' | 'SECOND-MODE-REF' | 'MODE-DECLARATION-REF' |
                  'DEFAULT-MODE-REF' | 'TARGET-MODE-REF' | 'ENTERED-MODE-REF' |
                  'EXITED-MODE-REF' | 'ENTRY-MODE-DECLARATION-REF' | 'EXIT-MODE-DECLARATION-REF'

    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.MODE_DECLARATION) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_DECLARATION}


class ModeDeclarationGroupRef(BaseRef):
    """
    Reference to ModeDeclarationGroup
    Tag variants: 'MODE-DECLARATION-GROUP-REF' | 'TYPE-TREF' | 'MODE-GROUP-REF'
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP}


class ModeDeclarationGroupPrototypeRef(BaseRef):
    """
    Reference to ModeDeclarationGroupPrototype
    Tag variants: 'MODE-GROUP-REF' | 'REQUIRED-MODE-GROUP-REF' | 'FIRST-MODE-GROUP-REF' |
                  'SECOND-MODE-GROUP-REF' | 'MODE-DECLARATION-GROUP-PROTOTYPE-REF'
                  (and more)
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP_PROTOTYPE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_DECLARATION_GROUP_PROTOTYPE}


class AutosarDataPrototypeRef(BaseRef):
    """
    Reference to elements that derives from AutosarDataPrototype
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ARGUMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE}


class E2EProfileCompatibilityPropsRef(BaseRef):
    """
    Reference to E2EProfileCompatibilityProps
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.E2E_PROFILE_COMPATIBILITY_PROPS
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.E2E_PROFILE_COMPATIBILITY_PROPS}


class ClientServerOperationRef(BaseRef):
    """
    Reference to ClientServerOperation
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.CLIENT_SERVER_OPERATION
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.CLIENT_SERVER_OPERATION}


class PortPrototypeRef(BaseRef):
    """
    Reference to port prototype elements
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_PROVIDED_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.ABSTRACT_REQUIRED_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE,
                }

    @property
    def is_provide_port_ref(self) -> bool:
        """
        True if destination of port reference is a P-PORT
        """
        p_port_values = {ar_enum.IdentifiableSubTypes.ABSTRACT_PROVIDED_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE}
        return self.dest in p_port_values

    @property
    def is_require_port_ref(self) -> bool:
        """
        True if destination of port reference is an R-PORT
        """
        r_port_values = {ar_enum.IdentifiableSubTypes.ABSTRACT_REQUIRED_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE,
                         ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE}
        return self.dest in r_port_values


class AbstractImplementationDataTypeElementRef(BaseRef):
    """
    Reference to abstract or specific data-type elements
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_IMPLEMENTATION_DATA_TYPE_ELEMENT,
                ar_enum.IdentifiableSubTypes.IMPLEMENTATION_DATA_TYPE_ELEMENT}


class DataPrototypeRef(BaseRef):
    """
    References to DATA-PROTOTYPE--SUBTYPES-ENUM
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_ELEMENT,
                ar_enum.IdentifiableSubTypes.APPLICATION_COMPOSITE_ELEMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT,
                ar_enum.IdentifiableSubTypes.ARGUMENT_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.AUTOSAR_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PARAMETER_DATA_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.VARIABLE_DATA_PROTOTYPE,
                }


class PortInterfaceRef(BaseRef):
    """
    References to PORT-INTERFACE--SUBTYPES-ENUM

    Only a small piece of the enum is currently implemented
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.CLIENT_SERVER_INTERFACE,
                ar_enum.IdentifiableSubTypes.MODE_SWITCH_INTERFACE,
                ar_enum.IdentifiableSubTypes.NV_DATA_INTERFACE,
                ar_enum.IdentifiableSubTypes.PARAMETER_INTERFACE,
                ar_enum.IdentifiableSubTypes.SENDER_RECEIVER_INTERFACE,
                }


class SwComponentTypeRef(BaseRef):
    """
    References to SW-COMPONENT-TYPE--SUBTYPES-ENUM

    Only a small piece of the enum is currently implemented
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_SW_COMPONENT_TYPE,
                ar_enum.IdentifiableSubTypes.COMPOSITION_SW_COMPONENT_TYPE,
                }


class SwComponentPrototypeRef(BaseRef):
    """
    Reference to SW-COMPONENT-PROTOTYPE--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.SW_COMPONENT_PROTOTYPE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SW_COMPONENT_PROTOTYPE}


class SwcInternalBehaviorRef(BaseRef):
    """
    Reference to AR:SWC-INTERNAL-BEHAVIOR--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.SWC_INTERNAL_BEHAVIOR
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SWC_INTERNAL_BEHAVIOR}


class SwcImplementationRef(BaseRef):
    """
    AR:SWC-IMPLEMENTATION--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.SWC_IMPLEMENTATION
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.SWC_IMPLEMENTATION}


class ExclusiveAreaRef(BaseRef):
    """
    AR:EXCLUSIVE-AREA--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.EXCLUSIVE_AREA
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.EXCLUSIVE_AREA}


class ExclusiveAreaNestingOrderRef(BaseRef):
    """
    AR:EXCLUSIVE-AREA-NESTING-ORDER--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.EXCLUSIVE_AREA_NESTING_ORDER
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.EXCLUSIVE_AREA_NESTING_ORDER}


class AbstractRequiredPortPrototypeRef(BaseRef):
    """
    AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE--SUBTYPES-ENUM
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_REQUIRED_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.R_PORT_PROTOTYPE}


class AbstractProvidedPortPrototypeRef(BaseRef):
    """
    AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE--SUBTYPES-ENUM
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ABSTRACT_PROVIDED_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.P_PORT_PROTOTYPE,
                ar_enum.IdentifiableSubTypes.PR_PORT_PROTOTYPE}


class RunnableEntityRef(BaseRef):
    """
    AR:RUNNABLE-ENTITY--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.RUNNABLE_ENTITY
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.RUNNABLE_ENTITY}


class VariableAccessRef(BaseRef):
    """
    VARIABLE-ACCESS--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.VARIABLE_ACCESS
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.VARIABLE_ACCESS}


class ModeSwitchPointRef(BaseRef):
    """
    AR:MODE-SWITCH-POINT--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.MODE_SWITCH_POINT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.MODE_SWITCH_POINT}


class AsynchronousServerCallPointRef(BaseRef):
    """
    AR:ASYNCHRONOUS-SERVER-CALL-POINT--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_POINT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_POINT}


class AsynchronousServerCallResultPointRef(BaseRef):
    """
    AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_RESULT_POINT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_RESULT_POINT}


class TriggerRef(BaseRef):
    """
    AR:TRIGGER--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.TRIGGER
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.TRIGGER}


class InternalTriggeringPointRef(BaseRef):
    """
    AR:INTERNAL-TRIGGERING-POINT--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.INTERNAL_TRIGGERING_POINT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.INTERNAL_TRIGGERING_POINT}


class RteEventRef(BaseRef):
    """
    AR:RTE-EVENT--SUBTYPES-ENUM
    """

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ASYNCHRONOUS_SERVER_CALL_RETURNS_EVENT,
                ar_enum.IdentifiableSubTypes.BACKGROUND_EVENT,
                ar_enum.IdentifiableSubTypes.DATA_RECEIVE_ERROR_EVENT,
                ar_enum.IdentifiableSubTypes.DATA_RECEIVED_EVENT,
                ar_enum.IdentifiableSubTypes.DATA_SEND_COMPLETED_EVENT,
                ar_enum.IdentifiableSubTypes.DATA_WRITE_COMPLETED_EVENT,
                ar_enum.IdentifiableSubTypes.EXTERNAL_TRIGGER_OCCURRED_EVENT,
                ar_enum.IdentifiableSubTypes.INIT_EVENT,
                ar_enum.IdentifiableSubTypes.INTERNAL_TRIGGER_OCCURRED_EVENT,
                ar_enum.IdentifiableSubTypes.MODE_SWITCHED_ACK_EVENT,
                ar_enum.IdentifiableSubTypes.OPERATION_INVOKED_EVENT,
                ar_enum.IdentifiableSubTypes.SWC_MODE_MANAGER_ERROR_EVENT,
                ar_enum.IdentifiableSubTypes.SWC_MODE_SWITCH_EVENT,
                ar_enum.IdentifiableSubTypes.TIMING_EVENT,
                ar_enum.IdentifiableSubTypes.TRANSFORMER_HARD_ERROR_EVENT,
                }


class DataTypeMappingSetRef(BaseRef):
    """
    AR:DATA-TYPE-MAPPING-SET--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.DATA_TYPE_MAPPING_SET
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.DATA_TYPE_MAPPING_SET}


class ArgumentDataPrototypeRef(BaseRef):
    """
    AR:ARGUMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.ARGUMENT_DATA_PROTOTYPE
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.ARGUMENT_DATA_PROTOTYPE}


class ApplicationArrayElementRef(BaseRef):
    """
    AR:APPLICATION-ARRAY-ELEMENT--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_ELEMENT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_ARRAY_ELEMENT}


class ApplicationRecordElementRef(BaseRef):
    """
    AR:APPLICATION-RECORD-ELEMENT--SUBTYPES-ENUM
    """

    def __init__(self, value: str,
                 dest: ar_enum.IdentifiableSubTypes = ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT
                 ) -> None:
        super().__init__(value, dest)

    @classmethod
    def accepted_sub_types(cls) -> set[ar_enum.IdentifiableSubTypes]:
        """Acceptable values for dest"""
        return {ar_enum.IdentifiableSubTypes.APPLICATION_RECORD_ELEMENT}
