"""Service needs elements."""

from __future__ import annotations

from autosar.xml.base import ARObject
from autosar.xml.elements._base import Identifiable
import autosar.xml.enumeration as ar_enum
import autosar.xml.exception as ar_except
from autosar.xml.reference import (
    ApplicationDataTypeRef,
    DiagnosticEventNeedsRef,
    DiagnosticValueNeedsRef,
    FunctionInhibitionNeedsRef,
    SupervisedEntityCheckpointNeedsRef,
)


class ServiceNeeds(Identifiable):
    """
    Group AR:SERVICE-NEEDS
    """

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)


class BswMgrNeeds(ServiceNeeds):
    """
    Complex type AR:BSW-MGR-NEEDS
    Tag variants: 'BSW-MGR-NEEDS'

    Same constructor as parent class
    """


class ComMgrUserNeeds(ServiceNeeds):
    """
    Complex type AR:COM-MGR-USER-NEEDS
    Tag variants: 'COM-MGR-USER-NEEDS'
    """

    def __init__(self,
                 name: str,
                 max_comm_mode: ar_enum.MaxCommMode | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .MAX-COMM-MODE
        self.max_comm_mode: ar_enum.MaxCommMode | None = None

        self._assign_optional("max_comm_mode", max_comm_mode, ar_enum.MaxCommMode)


class CryptoCertificateKeySlotNeeds(ServiceNeeds):
    """
    Complex type AR:CRYPTO-CERTIFICATE-KEY-SLOT-NEEDS
    Tag variants: 'CRYPTO-CERTIFICATE-KEY-SLOT-NEEDS'

    Same constructor as parent class
    """


class CryptoKeyManagementNeeds(ServiceNeeds):
    """
    Complex type AR:CRYPTO-KEY-MANAGEMENT-NEEDS
    Tag variants: 'CRYPTO-KEY-MANAGEMENT-NEEDS'

    Same constructor as parent class
    """


class CryptoServiceJobNeeds(ServiceNeeds):
    """
    Complex type AR:CRYPTO-SERVICE-JOB-NEEDS
    Tag variants: 'CRYPTO-SERVICE-JOB-NEEDS'

    Same constructor as parent class
    """


class CryptoServiceNeeds(ServiceNeeds):
    """
    Complex type AR:CRYPTO-SERVICE-NEEDS
    Tag variants: 'CRYPTO-SERVICE-NEEDS'
    """

    def __init__(self,
                 name: str,
                 algorithm_family: str | None = None,
                 algorithm_mode: str | None = None,
                 crypto_key_description: str | None = None,
                 maximum_key_length: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ALGORITHM-FAMILY
        self.algorithm_family: str | None = None
        # .ALGORITHM-MODE
        self.algorithm_mode: str | None = None
        # .CRYPTO-KEY-DESCRIPTION
        self.crypto_key_description: str | None = None
        # .MAXIMUM-KEY-LENGTH
        self.maximum_key_length: int | None = None

        self._assign_optional_strict("algorithm_family", algorithm_family, str)
        self._assign_optional_strict("algorithm_mode", algorithm_mode, str)
        self._assign_optional_strict("crypto_key_description", crypto_key_description, str)
        self._assign_optional_positive_int("maximum_key_length", maximum_key_length)


class DiagEventDebounceAlgorithm(Identifiable):
    """
    Group AR:DIAG-EVENT-DEBOUNCE-ALGORITHM
    """


class DiagEventDebounceCounterBased(DiagEventDebounceAlgorithm):
    """
    Complex type AR:DIAG-EVENT-DEBOUNCE-COUNTER-BASED
    Tag variants: 'DIAG-EVENT-DEBOUNCE-COUNTER-BASED'
    """

    def __init__(self,
                 name: str,
                 counter_based_fdc_threshold_storage_value: int | None = None,
                 counter_decrement_step_size: int | None = None,
                 counter_failed_threshold: int | None = None,
                 counter_increment_step_size: int | None = None,
                 counter_jump_down: bool | None = None,
                 counter_jump_down_value: int | None = None,
                 counter_jump_up: bool | None = None,
                 counter_jump_up_value: int | None = None,
                 counter_passed_threshold: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .COUNTER-BASED-FDC-THRESHOLD-STORAGE-VALUE
        self.counter_based_fdc_threshold_storage_value: int | None = None
        # .COUNTER-DECREMENT-STEP-SIZE
        self.counter_decrement_step_size: int | None = None
        # .COUNTER-FAILED-THRESHOLD
        self.counter_failed_threshold: int | None = None
        # .COUNTER-INCREMENT-STEP-SIZE
        self.counter_increment_step_size: int | None = None
        # .COUNTER-JUMP-DOWN
        self.counter_jump_down: bool | None = None
        # .COUNTER-JUMP-DOWN-VALUE
        self.counter_jump_down_value: int | None = None
        # .COUNTER-JUMP-UP
        self.counter_jump_up: bool | None = None
        # .COUNTER-JUMP-UP-VALUE
        self.counter_jump_up_value: int | None = None
        # .COUNTER-PASSED-THRESHOLD
        self.counter_passed_threshold: int | None = None

        self._assign_optional("counter_based_fdc_threshold_storage_value",
                              counter_based_fdc_threshold_storage_value, int)
        self._assign_optional("counter_decrement_step_size", counter_decrement_step_size, int)
        self._assign_optional("counter_failed_threshold", counter_failed_threshold, int)
        self._assign_optional("counter_increment_step_size", counter_increment_step_size, int)
        self._assign_optional("counter_jump_down", counter_jump_down, bool)
        self._assign_optional("counter_jump_down_value", counter_jump_down_value, int)
        self._assign_optional("counter_jump_up", counter_jump_up, bool)
        self._assign_optional("counter_jump_up_value", counter_jump_up_value, int)
        self._assign_optional("counter_passed_threshold", counter_passed_threshold, int)


class DiagEventDebounceMonitorInternal(DiagEventDebounceAlgorithm):
    """
    Complex type AR:DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL
    Tag variants: 'DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL'

    Same constructor as parent class
    """


class DiagEventDebounceTimeBased(DiagEventDebounceAlgorithm):
    """
    Complex type AR:DIAG-EVENT-DEBOUNCE-TIME-BASED
    Tag variants: 'DIAG-EVENT-DEBOUNCE-TIME-BASED'
    """

    def __init__(self,
                 name: str,
                 time_based_fdc_threshold_storage_value: float | int | None = None,
                 time_failed_threshold: float | int | None = None,
                 time_passed_threshold: float | int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .TIME-BASED-FDC-THRESHOLD-STORAGE-VALUE
        self.time_based_fdc_threshold_storage_value: float | int | None = None
        # .TIME-FAILED-THRESHOLD
        self.time_failed_threshold: float | int | None = None
        # .TIME-PASSED-THRESHOLD
        self.time_passed_threshold: float | int | None = None

        self._assign_optional("time_based_fdc_threshold_storage_value",
                              time_based_fdc_threshold_storage_value, float)
        self._assign_optional("time_failed_threshold", time_failed_threshold, float)
        self._assign_optional("time_passed_threshold", time_passed_threshold, float)


class DiagnosticCapabilityElement(ServiceNeeds):
    """
    Group AR:DIAGNOSTIC-CAPABILITY-ELEMENT
    """

    def __init__(self,
                 name: str,
                 audience: ar_enum.DiagnosticAudience | str | list[ar_enum.DiagnosticAudience | str] | None = None,
                 diag_requirement: str | None = None,
                 security_access_level: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .AUDIENCES
        self.audience: list[ar_enum.DiagnosticAudience] = []
        # .DIAG-REQUIREMENT
        self.diag_requirement: str | None = None
        # .SECURITY-ACCESS-LEVEL
        self.security_access_level: int | None = None

        if audience is not None:
            if isinstance(audience, (ar_enum.DiagnosticAudience, str)):
                self._append_audience(audience)
            elif isinstance(audience, list):
                for item in audience:
                    self._append_audience(item)
            else:
                raise ar_except.ElementTypeError("audience", [ar_enum.DiagnosticAudience, str], audience)
        self._assign_optional_strict("diag_requirement", diag_requirement, str)
        self._assign_optional_positive_int("security_access_level", security_access_level)

    def _append_audience(self, item: ar_enum.DiagnosticAudience | str) -> None:
        if isinstance(item, str):
            try:
                item = ar_enum.xml_to_enum("DiagnosticAudience", item)
            except KeyError as exc:
                raise ar_except.ConversionError("audience", ar_enum.DiagnosticAudience, item) from exc
        if isinstance(item, ar_enum.DiagnosticAudience):
            self.audience.append(item)
        else:
            raise ar_except.ElementTypeError("audience", ar_enum.DiagnosticAudience, item)


class DiagnosticClearConditionNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-CLEAR-CONDITION-NEEDS
    Tag variants: 'DIAGNOSTIC-CLEAR-CONDITION-NEEDS'

    Same constructor as parent class
    """


class DiagnosticCommunicationManagerNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS
    Tag variants: 'DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS'
    """

    def __init__(self,
                 name: str,
                 service_request_callback_type: (ar_enum.DiagnosticServiceRequestCallbackType
                                                 | str
                                                 | None) = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .SERVICE-REQUEST-CALLBACK-TYPE
        self.service_request_callback_type: ar_enum.DiagnosticServiceRequestCallbackType | None = None

        self._assign_optional("service_request_callback_type",
                              service_request_callback_type,
                              ar_enum.DiagnosticServiceRequestCallbackType)


class DiagnosticComponentNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-COMPONENT-NEEDS
    Tag variants: 'DIAGNOSTIC-COMPONENT-NEEDS'

    Same constructor as parent class
    """


class DiagnosticControlNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-CONTROL-NEEDS
    Tag variants: 'DIAGNOSTIC-CONTROL-NEEDS'

    Same constructor as parent class
    """


class DiagnosticEnableConditionNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-ENABLE-CONDITION-NEEDS
    Tag variants: 'DIAGNOSTIC-ENABLE-CONDITION-NEEDS'
    """

    def __init__(self,
                 name: str,
                 initial_status: ar_enum.EventAcceptanceStatus | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .INITIAL-STATUS
        self.initial_status: ar_enum.EventAcceptanceStatus | None = None

        self._assign_optional("initial_status", initial_status, ar_enum.EventAcceptanceStatus)


DiagEventDebounceAlgorithmType = (DiagEventDebounceCounterBased |
                                  DiagEventDebounceMonitorInternal |
                                  DiagEventDebounceTimeBased)
InhibitingSecondaryFidRefType = FunctionInhibitionNeedsRef | str


class DiagnosticEventNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-EVENT-NEEDS
    Tag variants: 'DIAGNOSTIC-EVENT-NEEDS'
    """

    def __init__(self,
                 name: str,
                 consider_pto_status: bool | None = None,
                 diag_event_debounce_algorithm: DiagEventDebounceAlgorithmType | None = None,
                 dtc_kind: ar_enum.DtcKind | str | None = None,
                 dtc_number: int | None = None,
                 inhibiting_fid_ref: FunctionInhibitionNeedsRef | str | None = None,
                 inhibiting_secondary_fid_refs: (InhibitingSecondaryFidRefType |
                                                 list[InhibitingSecondaryFidRefType] |
                                                 None) = None,
                 obd_dtc_number: int | None = None,
                 prestored_freezeframe_stored_in_nvm: bool | None = None,
                 report_behavior: ar_enum.ReportBehavior | str | None = None,
                 uds_dtc_number: int | None = None,
                 uses_monitor_data: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CONSIDER-PTO-STATUS
        self.consider_pto_status: bool | None = None
        # .DIAG-EVENT-DEBOUNCE-ALGORITHM
        self.diag_event_debounce_algorithm: DiagEventDebounceAlgorithmType | None = None
        # .DTC-KIND
        self.dtc_kind: ar_enum.DtcKind | None = None
        # .DTC-NUMBER
        self.dtc_number: int | None = None
        # .INHIBITING-FID-REF
        self.inhibiting_fid_ref: FunctionInhibitionNeedsRef | None = None
        # .INHIBITING-SECONDARY-FID-REFS
        self.inhibiting_secondary_fid_refs: list[FunctionInhibitionNeedsRef] = []
        # .OBD-DTC-NUMBER
        self.obd_dtc_number: int | None = None
        # .PRESTORED-FREEZEFRAME-STORED-IN-NVM
        self.prestored_freezeframe_stored_in_nvm: bool | None = None
        # .REPORT-BEHAVIOR
        self.report_behavior: ar_enum.ReportBehavior | None = None
        # .UDS-DTC-NUMBER
        self.uds_dtc_number: int | None = None
        # .USES-MONITOR-DATA
        self.uses_monitor_data: bool | None = None

        self._assign_optional("consider_pto_status", consider_pto_status, bool)
        self._assign_optional_strict("diag_event_debounce_algorithm",
                                     diag_event_debounce_algorithm,
                                     (DiagEventDebounceCounterBased,
                                      DiagEventDebounceMonitorInternal,
                                      DiagEventDebounceTimeBased))
        self._assign_optional("dtc_kind", dtc_kind, ar_enum.DtcKind)
        self._assign_optional_positive_int("dtc_number", dtc_number)
        self._assign_optional("inhibiting_fid_ref", inhibiting_fid_ref, FunctionInhibitionNeedsRef)
        if inhibiting_secondary_fid_refs is not None:
            if isinstance(inhibiting_secondary_fid_refs, list):
                for ref in inhibiting_secondary_fid_refs:
                    self.append_inhibiting_secondary_fid_ref(ref)
            else:
                self.append_inhibiting_secondary_fid_ref(inhibiting_secondary_fid_refs)
        self._assign_optional_positive_int("obd_dtc_number", obd_dtc_number)
        self._assign_optional("prestored_freezeframe_stored_in_nvm", prestored_freezeframe_stored_in_nvm, bool)
        self._assign_optional("report_behavior", report_behavior, ar_enum.ReportBehavior)
        self._assign_optional_positive_int("uds_dtc_number", uds_dtc_number)
        self._assign_optional("uses_monitor_data", uses_monitor_data, bool)

    def append_inhibiting_secondary_fid_ref(self, ref: InhibitingSecondaryFidRefType) -> None:
        """
        Appends inhibiting secondary FID reference to internal list
        """
        if isinstance(ref, FunctionInhibitionNeedsRef):
            self.inhibiting_secondary_fid_refs.append(ref)
        elif isinstance(ref, str):
            self.inhibiting_secondary_fid_refs.append(FunctionInhibitionNeedsRef(ref))
        else:
            raise TypeError("ref: Expected type FunctionInhibitionNeedsRef or str")

    append = append_inhibiting_secondary_fid_ref


class DiagnosticEventInfoNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-EVENT-INFO-NEEDS
    Tag variants: 'DIAGNOSTIC-EVENT-INFO-NEEDS'
    """

    def __init__(self,
                 name: str,
                 obd_dtc_number: int | None = None,
                 uds_dtc_number: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .OBD-DTC-NUMBER
        self.obd_dtc_number: int | None = None
        # .UDS-DTC-NUMBER
        self.uds_dtc_number: int | None = None

        self._assign_optional("obd_dtc_number", obd_dtc_number, int)
        self._assign_optional("uds_dtc_number", uds_dtc_number, int)


class DiagnosticEventManagerNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-EVENT-MANAGER-NEEDS
    Tag variants: 'DIAGNOSTIC-EVENT-MANAGER-NEEDS'

    Same constructor as parent class
    """


class DiagnosticGenericUdsNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-GENERIC-UDS-NEEDS
    Tag variants: 'DIAGNOSTIC-GENERIC-UDS-NEEDS'

    Same constructor as parent class
    """


class DiagnosticIndicatorNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-INDICATOR-NEEDS
    Tag variants: 'DIAGNOSTIC-INDICATOR-NEEDS'

    Same constructor as parent class
    """


class DiagnosticIoControlNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-IO-CONTROL-NEEDS
    Tag variants: 'DIAGNOSTIC-IO-CONTROL-NEEDS'
    """

    def __init__(self,
                 name: str,
                 current_value_ref: DiagnosticValueNeedsRef | None = None,
                 freeze_current_state_supported: bool | None = None,
                 reset_to_default_supported: bool | None = None,
                 short_term_adjustment_supported: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CURRENT-VALUE-REF
        self.current_value_ref: DiagnosticValueNeedsRef | None = None
        # .FREEZE-CURRENT-STATE-SUPPORTED
        self.freeze_current_state_supported: bool | None = None
        # .RESET-TO-DEFAULT-SUPPORTED
        self.reset_to_default_supported: bool | None = None
        # .SHORT-TERM-ADJUSTMENT-SUPPORTED
        self.short_term_adjustment_supported: bool | None = None

        self._assign_optional("current_value_ref", current_value_ref, DiagnosticValueNeedsRef)
        self._assign_optional("freeze_current_state_supported", freeze_current_state_supported, bool)
        self._assign_optional("reset_to_default_supported", reset_to_default_supported, bool)
        self._assign_optional("short_term_adjustment_supported", short_term_adjustment_supported, bool)


class DiagnosticOperationCycleNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-OPERATION-CYCLE-NEEDS
    Tag variants: 'DIAGNOSTIC-OPERATION-CYCLE-NEEDS'
    """

    def __init__(self,
                 name: str,
                 operation_cycle: ar_enum.OperationCycleType | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .OPERATION-CYCLE
        self.operation_cycle: ar_enum.OperationCycleType | None = None

        self._assign_optional("operation_cycle", operation_cycle, ar_enum.OperationCycleType)


class DiagnosticRequestFileTransferNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS
    Tag variants: 'DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS'

    Same constructor as parent class
    """


class DiagnosticResponseOnEventNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-RESPONSE-ON-EVENT-NEEDS
    Tag variants: 'DIAGNOSTIC-RESPONSE-ON-EVENT-NEEDS'

    Same constructor as parent class
    """


class DiagnosticRoutineNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-ROUTINE-NEEDS
    Tag variants: 'DIAGNOSTIC-ROUTINE-NEEDS'
    """

    def __init__(self,
                 name: str,
                 diag_routine_type: ar_enum.DiagnosticRoutineType | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DIAG-ROUTINE-TYPE
        self.diag_routine_type: ar_enum.DiagnosticRoutineType | None = None

        self._assign_optional("diag_routine_type", diag_routine_type, ar_enum.DiagnosticRoutineType)


class DiagnosticStorageConditionNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-STORAGE-CONDITION-NEEDS
    Tag variants: 'DIAGNOSTIC-STORAGE-CONDITION-NEEDS'
    """

    def __init__(self,
                 name: str,
                 initial_status: ar_enum.StorageConditionStatus | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .INITIAL-STATUS
        self.initial_status: ar_enum.StorageConditionStatus | None = None

        self._assign_optional("initial_status", initial_status, ar_enum.StorageConditionStatus)


class DiagnosticUploadDownloadNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS
    Tag variants: 'DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS'

    Same constructor as parent class
    """


class DiagnosticValueNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTIC-VALUE-NEEDS
    Tag variants: 'DIAGNOSTIC-VALUE-NEEDS'
    """

    def __init__(self,
                 name: str,
                 data_length: int | None = None,
                 diagnostic_value_access: ar_enum.DiagnosticValueAccess | str | None = None,
                 fixed_length: bool | None = None,
                 processing_style: ar_enum.DiagnosticProcessingStyle | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DATA-LENGTH
        self.data_length: int | None = None
        # .DIAGNOSTIC-VALUE-ACCESS
        self.diagnostic_value_access: ar_enum.DiagnosticValueAccess | None = None
        # .FIXED-LENGTH
        self.fixed_length: bool | None = None
        # .PROCESSING-STYLE
        self.processing_style: ar_enum.DiagnosticProcessingStyle | None = None

        self._assign_optional("data_length", data_length, int)
        self._assign_optional("diagnostic_value_access", diagnostic_value_access, ar_enum.DiagnosticValueAccess)
        self._assign_optional("fixed_length", fixed_length, bool)
        self._assign_optional("processing_style", processing_style, ar_enum.DiagnosticProcessingStyle)


class DiagnosticsCommunicationSecurityNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS
    Tag variants: 'DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS'

    Same constructor as parent class
    """


class DltUserNeeds(ServiceNeeds):
    """
    Complex type AR:DLT-USER-NEEDS
    Tag variants: 'DLT-USER-NEEDS'

    Same constructor as parent class
    """


class DoIpServiceNeeds(ServiceNeeds):
    """
    Group AR:DO-IP-SERVICE-NEEDS
    """


class DoIpActivationLineNeeds(DoIpServiceNeeds):
    """
    Complex type AR:DO-IP-ACTIVATION-LINE-NEEDS
    Tag variants: 'DO-IP-ACTIVATION-LINE-NEEDS'

    Same constructor as parent class
    """


class DoIpGidNeeds(DoIpServiceNeeds):
    """
    Complex type AR:DO-IP-GID-NEEDS
    Tag variants: 'DO-IP-GID-NEEDS'

    Same constructor as parent class
    """


class DoIpGidSynchronizationNeeds(DoIpServiceNeeds):
    """
    Complex type AR:DO-IP-GID-SYNCHRONIZATION-NEEDS
    Tag variants: 'DO-IP-GID-SYNCHRONIZATION-NEEDS'

    Same constructor as parent class
    """


class DoIpPowerModeStatusNeeds(DoIpServiceNeeds):
    """
    Complex type AR:DO-IP-POWER-MODE-STATUS-NEEDS
    Tag variants: 'DO-IP-POWER-MODE-STATUS-NEEDS'

    Same constructor as parent class
    """


class DoIpRoutingActivationAuthenticationNeeds(DoIpServiceNeeds):
    """
    Complex type AR:DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS
    Tag variants: 'DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS'
    """

    def __init__(self,
                 name: str,
                 data_length_request: int | None = None,
                 data_length_response: int | None = None,
                 routing_activation_type: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DATA-LENGTH-REQUEST
        self.data_length_request: int | None = None
        # .DATA-LENGTH-RESPONSE
        self.data_length_response: int | None = None
        # .ROUTING-ACTIVATION-TYPE
        self.routing_activation_type: str | None = None

        self._assign_optional_positive_int("data_length_request", data_length_request)
        self._assign_optional_positive_int("data_length_response", data_length_response)
        self._assign_optional_strict("routing_activation_type", routing_activation_type, str)


class DoIpRoutingActivationConfirmationNeeds(DoIpServiceNeeds):
    """
    Complex type AR:DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS
    Tag variants: 'DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS'
    """

    def __init__(self,
                 name: str,
                 data_length_request: int | None = None,
                 data_length_response: int | None = None,
                 routing_activation_type: str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DATA-LENGTH-REQUEST
        self.data_length_request: int | None = None
        # .DATA-LENGTH-RESPONSE
        self.data_length_response: int | None = None
        # .ROUTING-ACTIVATION-TYPE
        self.routing_activation_type: str | None = None

        self._assign_optional_positive_int("data_length_request", data_length_request)
        self._assign_optional_positive_int("data_length_response", data_length_response)
        self._assign_optional_strict("routing_activation_type", routing_activation_type, str)


class DtcStatusChangeNotificationNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:DTC-STATUS-CHANGE-NOTIFICATION-NEEDS
    Tag variants: 'DTC-STATUS-CHANGE-NOTIFICATION-NEEDS'
    """

    def __init__(self,
                 name: str,
                 notification_time: ar_enum.DiagnosticClearDtcNotification | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .NOTIFICATION-TIME
        self.notification_time: ar_enum.DiagnosticClearDtcNotification | None = None

        self._assign_optional("notification_time",
                              notification_time,
                              ar_enum.DiagnosticClearDtcNotification)


class EcuStateMgrUserNeeds(ServiceNeeds):
    """
    Complex type AR:ECU-STATE-MGR-USER-NEEDS
    Tag variants: 'ECU-STATE-MGR-USER-NEEDS'

    Same constructor as parent class
    """


class TracedFailure(Identifiable):
    """
    Group AR:TRACED-FAILURE
    """

    def __init__(self,
                 name: str,
                 id: int | None = None,  # pylint: disable=redefined-builtin
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ID
        self.id: int | None = None

        self._assign_optional_positive_int("id", id)


class DevelopmentError(TracedFailure):
    """
    Complex type AR:DEVELOPMENT-ERROR
    Tag variants: 'DEVELOPMENT-ERROR'

    Same constructor as parent class
    """


class RuntimeError(TracedFailure):  # pylint: disable=redefined-builtin
    """
    Complex type AR:RUNTIME-ERROR
    Tag variants: 'RUNTIME-ERROR'

    Same constructor as parent class
    """


class PossibleErrorReaction(Identifiable):
    """
    Complex type AR:POSSIBLE-ERROR-REACTION
    Tag variants: 'POSSIBLE-ERROR-REACTION'
    """

    def __init__(self,
                 name: str,
                 reaction_code: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .REACTION-CODE
        self.reaction_code: int | None = None

        self._assign_optional_positive_int("reaction_code", reaction_code)


class TransientFault(TracedFailure):
    """
    Complex type AR:TRANSIENT-FAULT
    Tag variants: 'TRANSIENT-FAULT'
    """

    def __init__(self,
                 name: str,
                 id: int | None = None,  # pylint: disable=redefined-builtin
                 possible_error_reactions: PossibleErrorReaction | list[PossibleErrorReaction] | None = None,
                 **kwargs) -> None:
        super().__init__(name, id=id, **kwargs)
        # .POSSIBLE-ERROR-REACTIONS
        self.possible_error_reactions: list[PossibleErrorReaction] = []

        if possible_error_reactions is not None:
            if isinstance(possible_error_reactions, PossibleErrorReaction):
                self.append_possible_error_reaction(possible_error_reactions)
            elif isinstance(possible_error_reactions, list):
                for reaction in possible_error_reactions:
                    self.append_possible_error_reaction(reaction)
            else:
                raise TypeError("possible_error_reactions: Expected PossibleErrorReaction or list")

    def append_possible_error_reaction(self, reaction: PossibleErrorReaction) -> None:
        """
        Appends reaction to internal list of possible error reactions
        """
        if isinstance(reaction, PossibleErrorReaction):
            self.possible_error_reactions.append(reaction)
        else:
            raise TypeError("reaction: Expected type PossibleErrorReaction")

    append = append_possible_error_reaction


TracedFailureType = DevelopmentError | RuntimeError | TransientFault


class ErrorTracerNeeds(ServiceNeeds):
    """
    Complex type AR:ERROR-TRACER-NEEDS
    Tag variants: 'ERROR-TRACER-NEEDS'
    """

    def __init__(self,
                 name: str,
                 traced_failures: TracedFailureType | list[TracedFailureType] | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .TRACED-FAILURES
        self.traced_failures: list[TracedFailure] = []

        if traced_failures is not None:
            if isinstance(traced_failures, TracedFailure):
                self.append_traced_failure(traced_failures)
            elif isinstance(traced_failures, list):
                for failure in traced_failures:
                    self.append_traced_failure(failure)
            else:
                raise TypeError("traced_failures: Expected TracedFailure or list")

    def append_traced_failure(self, failure: TracedFailure) -> None:
        """
        Appends failure to internal list of traced failures
        """
        if isinstance(failure, TracedFailure):
            self.traced_failures.append(failure)
        else:
            raise TypeError("failure: Expected type TracedFailure")

    append = append_traced_failure


class FunctionInhibitionAvailabilityNeeds(ServiceNeeds):
    """
    Complex type AR:FUNCTION-INHIBITION-AVAILABILITY-NEEDS
    Tag variants: 'FUNCTION-INHIBITION-AVAILABILITY-NEEDS'
    """

    def __init__(self,
                 name: str,
                 controlled_fid_ref: FunctionInhibitionNeedsRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CONTROLLED-FID-REF
        self.controlled_fid_ref: FunctionInhibitionNeedsRef | None = None

        self._assign_optional("controlled_fid_ref",
                              controlled_fid_ref,
                              FunctionInhibitionNeedsRef)


class FunctionInhibitionNeeds(ServiceNeeds):
    """
    Complex type AR:FUNCTION-INHIBITION-NEEDS
    Tag variants: 'FUNCTION-INHIBITION-NEEDS'

    Same constructor as parent class
    """


class FurtherActionByteNeeds(DoIpServiceNeeds):
    """
    Complex type AR:FURTHER-ACTION-BYTE-NEEDS
    Tag variants: 'FURTHER-ACTION-BYTE-NEEDS'

    Same constructor as parent class
    """


class GlobalSupervisionNeeds(ServiceNeeds):
    """
    Complex type AR:GLOBAL-SUPERVISION-NEEDS
    Tag variants: 'GLOBAL-SUPERVISION-NEEDS'

    Same constructor as parent class
    """


class HardwareTestNeeds(ServiceNeeds):
    """
    Complex type AR:HARDWARE-TEST-NEEDS
    Tag variants: 'HARDWARE-TEST-NEEDS'

    Same constructor as parent class
    """


class IdsMgrCustomTimestampNeeds(ServiceNeeds):
    """
    Complex type AR:IDS-MGR-CUSTOM-TIMESTAMP-NEEDS
    Tag variants: 'IDS-MGR-CUSTOM-TIMESTAMP-NEEDS'

    Same constructor as parent class
    """


class IdsMgrNeeds(ServiceNeeds):
    """
    Complex type AR:IDS-MGR-NEEDS
    Tag variants: 'IDS-MGR-NEEDS'
    """

    def __init__(self,
                 name: str,
                 use_smart_sensor_api: bool | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .USE-SMART-SENSOR-API
        self.use_smart_sensor_api: bool | None = None

        self._assign_optional("use_smart_sensor_api", use_smart_sensor_api, bool)


class IndicatorStatusNeeds(ServiceNeeds):
    """
    Complex type AR:INDICATOR-STATUS-NEEDS
    Tag variants: 'INDICATOR-STATUS-NEEDS'
    """

    def __init__(self,
                 name: str,
                 type: ar_enum.DiagnosticIndicatorType | str | None = None,  # pylint: disable=redefined-builtin
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .TYPE
        self.type: ar_enum.DiagnosticIndicatorType | None = None

        self._assign_optional("type",
                              type,
                              ar_enum.DiagnosticIndicatorType)


class J1939DcmDm19Support(ServiceNeeds):
    """
    Complex type AR:J-1939-DCM-DM-19-SUPPORT
    Tag variants: 'J-1939-DCM-DM-19-SUPPORT'

    Same constructor as parent class
    """


class J1939RmIncomingRequestServiceNeeds(ServiceNeeds):
    """
    Complex type AR:J-1939-RM-INCOMING-REQUEST-SERVICE-NEEDS
    Tag variants: 'J-1939-RM-INCOMING-REQUEST-SERVICE-NEEDS'

    Same constructor as parent class
    """


class J1939RmOutgoingRequestServiceNeeds(ServiceNeeds):
    """
    Complex type AR:J-1939-RM-OUTGOING-REQUEST-SERVICE-NEEDS
    Tag variants: 'J-1939-RM-OUTGOING-REQUEST-SERVICE-NEEDS'

    Same constructor as parent class
    """


class NvBlockNeeds(ServiceNeeds):
    """
    Complex type AR:NV-BLOCK-NEEDS
    Tag variants: 'NV-BLOCK-NEEDS'
    """

    def __init__(self,
                 name: str,
                 calc_ram_block_crc: bool | None = None,
                 check_static_block_id: bool | None = None,
                 cyclic_writing_period: float | int | None = None,
                 n_data_sets: int | None = None,
                 n_rom_blocks: int | None = None,
                 ram_block_status_control: ar_enum.RamBlockStatusControl | str | None = None,
                 readonly: bool | None = None,
                 reliability: ar_enum.NvBlockNeedsReliability | str | None = None,
                 resistant_to_changed_sw: bool | None = None,
                 restore_at_start: bool | None = None,
                 select_block_for_first_init_all: bool | None = None,
                 store_at_shutdown: bool | None = None,
                 store_cyclic: bool | None = None,
                 store_emergency: bool | None = None,
                 store_immediate: bool | None = None,
                 store_on_change: bool | None = None,
                 use_auto_validation_at_shut_down: bool | None = None,
                 use_crc_comp_mechanism: bool | None = None,
                 write_only_once: bool | None = None,
                 write_verification: bool | None = None,
                 writing_frequency: int | None = None,
                 writing_priority: ar_enum.NvBlockNeedsWritingPriority | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CALC-RAM-BLOCK-CRC
        self.calc_ram_block_crc: bool | None = None
        # .CHECK-STATIC-BLOCK-ID
        self.check_static_block_id: bool | None = None
        # .CYCLIC-WRITING-PERIOD
        self.cyclic_writing_period: float | int | None = None
        # .N-DATA-SETS
        self.n_data_sets: int | None = None
        # .N-ROM-BLOCKS
        self.n_rom_blocks: int | None = None
        # .RAM-BLOCK-STATUS-CONTROL
        self.ram_block_status_control: ar_enum.RamBlockStatusControl | None = None
        # .READONLY
        self.readonly: bool | None = None
        # .RELIABILITY
        self.reliability: ar_enum.NvBlockNeedsReliability | None = None
        # .RESISTANT-TO-CHANGED-SW
        self.resistant_to_changed_sw: bool | None = None
        # .RESTORE-AT-START
        self.restore_at_start: bool | None = None
        # .SELECT-BLOCK-FOR-FIRST-INIT-ALL
        self.select_block_for_first_init_all: bool | None = None
        # .STORE-AT-SHUTDOWN
        self.store_at_shutdown: bool | None = None
        # .STORE-CYCLIC
        self.store_cyclic: bool | None = None
        # .STORE-EMERGENCY
        self.store_emergency: bool | None = None
        # .STORE-IMMEDIATE
        self.store_immediate: bool | None = None
        # .STORE-ON-CHANGE
        self.store_on_change: bool | None = None
        # .USE-AUTO-VALIDATION-AT-SHUT-DOWN
        self.use_auto_validation_at_shut_down: bool | None = None
        # .USE-CRC-COMP-MECHANISM
        self.use_crc_comp_mechanism: bool | None = None
        # .WRITE-ONLY-ONCE
        self.write_only_once: bool | None = None
        # .WRITE-VERIFICATION
        self.write_verification: bool | None = None
        # .WRITING-FREQUENCY
        self.writing_frequency: int | None = None
        # .WRITING-PRIORITY
        self.writing_priority: ar_enum.NvBlockNeedsWritingPriority | None = None

        self._assign_optional("calc_ram_block_crc", calc_ram_block_crc, bool)
        self._assign_optional("check_static_block_id", check_static_block_id, bool)
        self._assign_optional("cyclic_writing_period", cyclic_writing_period, float)
        self._assign_optional_positive_int("n_data_sets", n_data_sets)
        self._assign_optional_positive_int("n_rom_blocks", n_rom_blocks)
        self._assign_optional("ram_block_status_control", ram_block_status_control, ar_enum.RamBlockStatusControl)
        self._assign_optional("readonly", readonly, bool)
        self._assign_optional("reliability", reliability, ar_enum.NvBlockNeedsReliability)
        self._assign_optional("resistant_to_changed_sw", resistant_to_changed_sw, bool)
        self._assign_optional("restore_at_start", restore_at_start, bool)
        self._assign_optional("select_block_for_first_init_all", select_block_for_first_init_all, bool)
        self._assign_optional("store_at_shutdown", store_at_shutdown, bool)
        self._assign_optional("store_cyclic", store_cyclic, bool)
        self._assign_optional("store_emergency", store_emergency, bool)
        self._assign_optional("store_immediate", store_immediate, bool)
        self._assign_optional("store_on_change", store_on_change, bool)
        self._assign_optional("use_auto_validation_at_shut_down", use_auto_validation_at_shut_down, bool)
        self._assign_optional("use_crc_comp_mechanism", use_crc_comp_mechanism, bool)
        self._assign_optional("write_only_once", write_only_once, bool)
        self._assign_optional("write_verification", write_verification, bool)
        self._assign_optional_positive_int("writing_frequency", writing_frequency)
        self._assign_optional("writing_priority", writing_priority, ar_enum.NvBlockNeedsWritingPriority)


class ObdControlServiceNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:OBD-CONTROL-SERVICE-NEEDS
    Tag variants: 'OBD-CONTROL-SERVICE-NEEDS'

    Same constructor as parent class
    """


class ObdInfoServiceNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:OBD-INFO-SERVICE-NEEDS
    Tag variants: 'OBD-INFO-SERVICE-NEEDS'

    Same constructor as parent class
    """


class ObdMonitorServiceNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:OBD-MONITOR-SERVICE-NEEDS
    Tag variants: 'OBD-MONITOR-SERVICE-NEEDS'
    """

    def __init__(self,
                 name: str,
                 appl_data_type_ref: ApplicationDataTypeRef | str | None = None,
                 event_needs_ref: DiagnosticEventNeedsRef | str | None = None,
                 unit_and_scaling_id: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .APPLICATION-DATA-TYPE-REF
        self.appl_data_type_ref: ApplicationDataTypeRef | None = None
        # .EVENT-NEEDS-REF
        self.event_needs_ref: DiagnosticEventNeedsRef | None = None
        # .UNIT-AND-SCALING-ID
        self.unit_and_scaling_id: int | None = None

        self._assign_optional_strict("appl_data_type_ref",
                                     appl_data_type_ref,
                                     ApplicationDataTypeRef)
        self._assign_optional("event_needs_ref",
                              event_needs_ref,
                              DiagnosticEventNeedsRef)
        self._assign_optional_positive_int("unit_and_scaling_id", unit_and_scaling_id)


class ObdPidServiceNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:OBD-PID-SERVICE-NEEDS
    Tag variants: 'OBD-PID-SERVICE-NEEDS'

    Same constructor as parent class
    """


class ObdRatioDenominatorNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:OBD-RATIO-DENOMINATOR-NEEDS
    Tag variants: 'OBD-RATIO-DENOMINATOR-NEEDS'
    """

    def __init__(self,
                 name: str,
                 denominator_condition: ar_enum.DiagnosticDenominatorCondition | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .DENOMINATOR-CONDITION
        self.denominator_condition: ar_enum.DiagnosticDenominatorCondition | None = None

        self._assign_optional("denominator_condition",
                              denominator_condition,
                              ar_enum.DiagnosticDenominatorCondition)


class ObdRatioServiceNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:OBD-RATIO-SERVICE-NEEDS
    Tag variants: 'OBD-RATIO-SERVICE-NEEDS'
    """

    def __init__(self,
                 name: str,
                 connection_type: ar_enum.ObdRatioConnectionKind | str | None = None,
                 rate_based_monitored_event_ref: DiagnosticEventNeedsRef | str | None = None,
                 used_fid_ref: FunctionInhibitionNeedsRef | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .CONNECTION-TYPE
        self.connection_type: ar_enum.ObdRatioConnectionKind | None = None
        # .RATE-BASED-MONITORED-EVENT-REF
        self.rate_based_monitored_event_ref: DiagnosticEventNeedsRef | None = None
        # .USED-FID-REF
        self.used_fid_ref: FunctionInhibitionNeedsRef | None = None

        self._assign_optional("connection_type",
                              connection_type,
                              ar_enum.ObdRatioConnectionKind)
        self._assign_optional("rate_based_monitored_event_ref",
                              rate_based_monitored_event_ref,
                              DiagnosticEventNeedsRef)
        self._assign_optional("used_fid_ref",
                              used_fid_ref,
                              FunctionInhibitionNeedsRef)


class SecureOnBoardCommunicationNeeds(ServiceNeeds):
    """
    Complex type AR:SECURE-ON-BOARD-COMMUNICATION-NEEDS
    Tag variants: 'SECURE-ON-BOARD-COMMUNICATION-NEEDS'
    """

    def __init__(self,
                 name: str,
                 verification_status_indication_mode: ar_enum.VerificationStatusIndicationMode | str | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .VERIFICATION-STATUS-INDICATION-MODE
        self.verification_status_indication_mode: ar_enum.VerificationStatusIndicationMode | None = None

        self._assign_optional("verification_status_indication_mode",
                              verification_status_indication_mode,
                              ar_enum.VerificationStatusIndicationMode)


class SupervisedEntityCheckpointNeedsRefConditional(ARObject):
    """
    Complex type AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF-CONDITIONAL
    Tag variants: 'SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF-CONDITIONAL'
    """

    def __init__(self,
                 checkpoint_ref: SupervisedEntityCheckpointNeedsRef | str | None = None) -> None:
        super().__init__()
        # .SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF
        self.checkpoint_ref: SupervisedEntityCheckpointNeedsRef | None = None

        self._assign_optional("checkpoint_ref", checkpoint_ref, SupervisedEntityCheckpointNeedsRef)


SupervisedEntityCheckpointArgumentType = (SupervisedEntityCheckpointNeedsRefConditional |
                                          SupervisedEntityCheckpointNeedsRef |
                                          str)


class SupervisedEntityCheckpointNeeds(ServiceNeeds):
    """
    Complex type AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS
    Tag variants: 'SUPERVISED-ENTITY-CHECKPOINT-NEEDS'

    Same constructor as parent class
    """


class SupervisedEntityNeeds(ServiceNeeds):
    """
    Complex type AR:SUPERVISED-ENTITY-NEEDS
    Tag variants: 'SUPERVISED-ENTITY-NEEDS'
    """

    def __init__(self,
                 name: str,
                 activate_at_start: bool | None = None,
                 checkpoints: (SupervisedEntityCheckpointArgumentType |
                               list[SupervisedEntityCheckpointArgumentType] |
                               None) = None,
                 enable_deactivation: bool | None = None,
                 expected_alive_cycle: float | int | None = None,
                 max_alive_cycle: float | int | None = None,
                 min_alive_cycle: float | int | None = None,
                 tolerated_failed_cycles: int | None = None,
                 **kwargs) -> None:
        super().__init__(name, **kwargs)
        # .ACTIVATE-AT-START
        self.activate_at_start: bool | None = None
        # .CHECKPOINTSS
        self.checkpoints: list[SupervisedEntityCheckpointNeedsRefConditional] = []
        # .ENABLE-DEACTIVATION
        self.enable_deactivation: bool | None = None
        # .EXPECTED-ALIVE-CYCLE
        self.expected_alive_cycle: float | None = None
        # .MAX-ALIVE-CYCLE
        self.max_alive_cycle: float | None = None
        # .MIN-ALIVE-CYCLE
        self.min_alive_cycle: float | None = None
        # .TOLERATED-FAILED-CYCLES
        self.tolerated_failed_cycles: int | None = None

        self._assign_optional("activate_at_start", activate_at_start, bool)
        if checkpoints is not None:
            if isinstance(checkpoints, list):
                for checkpoint in checkpoints:
                    self.append_checkpoint(checkpoint)
            else:
                self.append_checkpoint(checkpoints)
        self._assign_optional("enable_deactivation", enable_deactivation, bool)
        self._assign_optional("expected_alive_cycle", expected_alive_cycle, float)
        self._assign_optional("max_alive_cycle", max_alive_cycle, float)
        self._assign_optional("min_alive_cycle", min_alive_cycle, float)
        self._assign_optional_positive_int("tolerated_failed_cycles", tolerated_failed_cycles)

    def append_checkpoint(self, checkpoint: SupervisedEntityCheckpointArgumentType) -> None:
        """
        Appends checkpoint reference conditional to internal list of checkpoints
        """
        if isinstance(checkpoint, SupervisedEntityCheckpointNeedsRefConditional):
            self.checkpoints.append(checkpoint)
        elif isinstance(checkpoint, (SupervisedEntityCheckpointNeedsRef, str)):
            self.checkpoints.append(SupervisedEntityCheckpointNeedsRefConditional(checkpoint))
        else:
            raise TypeError("checkpoint: Expected SupervisedEntityCheckpointNeedsRefConditional, "
                            "SupervisedEntityCheckpointNeedsRef or str")

    append = append_checkpoint


class SyncTimeBaseMgrUserNeeds(ServiceNeeds):
    """
    Complex type AR:SYNC-TIME-BASE-MGR-USER-NEEDS
    Tag variants: 'SYNC-TIME-BASE-MGR-USER-NEEDS'

    Same constructor as parent class
    """


class VendorSpecificServiceNeeds(ServiceNeeds):
    """
    Complex type AR:VENDOR-SPECIFIC-SERVICE-NEEDS
    Tag variants: 'VENDOR-SPECIFIC-SERVICE-NEEDS'

    Same constructor as parent class
    """


class V2xDataManagerNeeds(ServiceNeeds):
    """
    Complex type AR:V-2-X-DATA-MANAGER-NEEDS
    Tag variants: 'V-2-X-DATA-MANAGER-NEEDS'

    Same constructor as parent class
    """


class V2xFacUserNeeds(ServiceNeeds):
    """
    Complex type AR:V-2-X-FAC-USER-NEEDS
    Tag variants: 'V-2-X-FAC-USER-NEEDS'

    Same constructor as parent class
    """


class V2xMUserNeeds(ServiceNeeds):
    """
    Complex type AR:V-2-X-M-USER-NEEDS
    Tag variants: 'V-2-X-M-USER-NEEDS'

    Same constructor as parent class
    """


class WarningIndicatorRequestedBitNeeds(DiagnosticCapabilityElement):
    """
    Complex type AR:WARNING-INDICATOR-REQUESTED-BIT-NEEDS
    Tag variants: 'WARNING-INDICATOR-REQUESTED-BIT-NEEDS'

    Same constructor as parent class
    """


__all__ = [
    "ServiceNeeds",
    "BswMgrNeeds",
    "ComMgrUserNeeds",
    "CryptoCertificateKeySlotNeeds",
    "CryptoKeyManagementNeeds",
    "CryptoServiceJobNeeds",
    "CryptoServiceNeeds",
    "DiagEventDebounceAlgorithm",
    "DiagEventDebounceCounterBased",
    "DiagEventDebounceMonitorInternal",
    "DiagEventDebounceTimeBased",
    "DiagnosticCapabilityElement",
    "DiagnosticClearConditionNeeds",
    "DiagnosticCommunicationManagerNeeds",
    "DiagnosticComponentNeeds",
    "DiagnosticControlNeeds",
    "DiagnosticEnableConditionNeeds",
    "DiagEventDebounceAlgorithmType",
    "InhibitingSecondaryFidRefType",
    "DiagnosticEventNeeds",
    "DiagnosticEventInfoNeeds",
    "DiagnosticEventManagerNeeds",
    "DiagnosticGenericUdsNeeds",
    "DiagnosticIndicatorNeeds",
    "DiagnosticIoControlNeeds",
    "DiagnosticOperationCycleNeeds",
    "DiagnosticRequestFileTransferNeeds",
    "DiagnosticResponseOnEventNeeds",
    "DiagnosticRoutineNeeds",
    "DiagnosticStorageConditionNeeds",
    "DiagnosticUploadDownloadNeeds",
    "DiagnosticValueNeeds",
    "DiagnosticsCommunicationSecurityNeeds",
    "DltUserNeeds",
    "DoIpServiceNeeds",
    "DoIpActivationLineNeeds",
    "DoIpGidNeeds",
    "DoIpGidSynchronizationNeeds",
    "DoIpPowerModeStatusNeeds",
    "DoIpRoutingActivationAuthenticationNeeds",
    "DoIpRoutingActivationConfirmationNeeds",
    "DtcStatusChangeNotificationNeeds",
    "EcuStateMgrUserNeeds",
    "TracedFailure",
    "DevelopmentError",
    "RuntimeError",
    "PossibleErrorReaction",
    "TransientFault",
    "TracedFailureType",
    "ErrorTracerNeeds",
    "FunctionInhibitionAvailabilityNeeds",
    "FunctionInhibitionNeeds",
    "FurtherActionByteNeeds",
    "GlobalSupervisionNeeds",
    "HardwareTestNeeds",
    "IdsMgrCustomTimestampNeeds",
    "IdsMgrNeeds",
    "IndicatorStatusNeeds",
    "J1939DcmDm19Support",
    "J1939RmIncomingRequestServiceNeeds",
    "J1939RmOutgoingRequestServiceNeeds",
    "NvBlockNeeds",
    "ObdControlServiceNeeds",
    "ObdInfoServiceNeeds",
    "ObdMonitorServiceNeeds",
    "ObdPidServiceNeeds",
    "ObdRatioDenominatorNeeds",
    "ObdRatioServiceNeeds",
    "SecureOnBoardCommunicationNeeds",
    "SupervisedEntityCheckpointNeedsRefConditional",
    "SupervisedEntityCheckpointArgumentType",
    "SupervisedEntityCheckpointNeeds",
    "SupervisedEntityNeeds",
    "SyncTimeBaseMgrUserNeeds",
    "VendorSpecificServiceNeeds",
    "V2xDataManagerNeeds",
    "V2xFacUserNeeds",
    "V2xMUserNeeds",
    "WarningIndicatorRequestedBitNeeds",
]
