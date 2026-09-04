"""
ARXML writer module
"""
# pylint: disable=consider-using-with, duplicate-code
from io import StringIO
from typing import TextIO
import sys
import math
import decimal
import autosar.base as ar_base
import autosar.xml.document as ar_document
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
# import autosar.xml.exception

# Type aliases

MultiLanguageOverviewParagraph = ar_element.MultiLanguageOverviewParagraph
TupleList = list[tuple[str, str]]


class _XMLWriter:
    def __init__(self, indentation_step: int) -> None:
        self.file_path: str = None
        self.fh: TextIO = None  # pylint: disable=invalid-name
        self.indentation_char: str = ' '
        # Number of characters (spaces) per indendation
        self.indentation_step = indentation_step
        self.indentation_level: int = 0  # current indentation level
        self.indentation_str: str = ''
        self.tag_stack = []  # stack of tag names
        self.line_number: int = 0

    def _str_open(self):
        self.fh = StringIO()
        self.line_number = 1
        self.indentation_level = 0
        self.indentation_str = ''
        self.tag_stack.clear()

    def _open(self, file_path: str):
        self.fh = open(file_path, 'w', encoding='utf-8')
        self.file_path = file_path
        self.line_number = 1
        self.indentation_level = 0
        self.indentation_str = ''
        self.tag_stack.clear()

    def _close(self):
        self.fh.close()

    def _indent(self):
        self.indentation_level += 1
        self.indentation_str = self.indentation_char * \
            (self.indentation_level * self.indentation_step)

    def _dedent(self):
        self.indentation_level -= 1
        if self.indentation_level == 0:
            self.indentation_str = ''
        else:
            self.indentation_str = self.indentation_char * \
                (self.indentation_level * self.indentation_step)

    def _add_line(self, text):
        if self.line_number > 1:
            self.fh.write('\n')
        self.line_number += 1
        self.fh.write(self.indentation_str)
        self.fh.write(text)

    def _add_inline_text(self, text):
        self.fh.write(text)

    def _add_child(self, tag: str, attr: TupleList | None = None):
        if attr:
            self._add_line(f'<{tag} {self._attr_to_str(attr)}>')
        else:
            self._add_line(f'<{tag}>')
        self.tag_stack.append(tag)
        self._indent()

    def _leave_child(self):
        tag = self.tag_stack.pop()
        self._dedent()
        self._add_line(f'</{tag}>')

    def _begin_line(self, tag: str, attr: TupleList | None = None):
        if self.line_number > 1:
            self.fh.write('\n')
        self.line_number += 1
        self.fh.write(self.indentation_str)
        if attr is None or len(attr) == 0:
            text = f'<{tag}>'
        else:
            text = f'<{tag} {self._attr_to_str(attr)}>'
        self._add_inline_text(text)

    def _end_line(self, tag: str):
        text = f'</{tag}>'
        self.fh.write(text)

    def _add_content(self, tag: str, content: str = '', attr: TupleList | None = None, inline: bool = False):
        assert isinstance(content, str)
        if attr:
            if content:
                text = f'<{tag} {self._attr_to_str(attr)}>{content}</{tag}>'
            else:
                text = f'<{tag} {self._attr_to_str(attr)}/>'
        else:
            if content:
                text = f'<{tag}>{content}</{tag}>'
            else:
                text = f'<{tag}/>'
        if inline:
            self._add_inline_text(text)
        else:
            self._add_line(text)

    def _attr_to_str(self, attr: TupleList) -> str:
        """
        Converts pairs (2-tuples) into attribute XML string
        """
        parts = [f'{elem[0]}="{elem[1]}"' for elem in attr]
        return ' '.join(parts)

    def _format_float(self, value: float) -> str:
        """
        Formats a float into a printable number string.
        The fractional part will automatically be stripped if possible
        """
        if math.isinf(value):
            return '-INF' if value < 0 else 'INF'
        if math.isnan(value):
            return 'NaN'
        else:
            tmp = decimal.Decimal(str(value))
            result = tmp.quantize(decimal.Decimal(1)) if tmp == tmp.to_integral() else tmp.normalize()
            return str(result)

    def _format_number(self, number: int | float | ar_element.NumericalValue) -> str:
        """
        Converts number to string
        """
        if isinstance(number, int):
            return str(number)
        elif isinstance(number, float):
            return self._format_float(number)
        elif isinstance(number, ar_element.NumericalValue):
            return self._format_numerical_value(number)
        else:
            raise TypeError("Not supported: " + str(type(number)))

    def _format_boolean(self, value: bool) -> str:
        """
        Converts bool to AR:BOOLEAN
        """
        assert isinstance(value, bool)
        return 'true' if value else 'false'

    def _format_numerical_value(self, number: ar_element.NumericalValue) -> str:
        if number.value_format in (ar_enum.ValueFormat.DEFAULT, ar_enum.ValueFormat.DECIMAL):
            return self._format_number(number.value)
        elif number.value_format == ar_enum.ValueFormat.HEXADECIMAL:
            return f"0x{number.value:x}"
        elif number.value_format == ar_enum.ValueFormat.BINARY:
            return f"0b{number.value:b}"
        elif number.value_format == ar_enum.ValueFormat.SCIENTIFIC:
            return f"{number.value:e}"
        else:
            raise NotImplementedError

    def _warn(self, msg: str):
        """
        Prints warning message to stderr
        """
        print(msg, file=sys.stderr)


class Writer(_XMLWriter):
    """
    ARXML writer class
    """

    def __init__(self,
                 schema_version: int = ar_base.DEFAULT_SCHEMA_VERSION) -> None:
        super().__init__(indentation_step=2)
        self.schema_version = schema_version

        # Elements found in AR:PACKAGE
        self.switcher_collectable = {
            # Package
            'Package': self._write_package,
            # CompuMethod elements
            'CompuMethod': self._write_compu_method,
            # Common structure and general template elements
            'DataFilter': self._write_data_filter,
            'AutosarEngineeringObject': self._write_autosar_engineering_object,
            'Code': self._write_code,
            'Trigger': self._write_trigger,
            # Data type elements
            'ApplicationArrayDataType': self._write_application_array_data_type,
            'ApplicationRecordDataType': self._write_application_record_data_type,
            'ApplicationPrimitiveDataType': self._write_application_primitive_data_type,
            'SwBaseType': self._write_sw_base_type,
            'SwAddrMethod': self._write_sw_addr_method,
            'ImplementationDataType': self._write_implementation_data_type,
            'DataTypeMappingSet': self._write_data_type_mapping_set,
            # DataConstraint elements
            'DataConstraint': self._write_data_constraint,
            # Unit elements
            'Unit': self._write_unit,
            # Constant elements
            'ConstantSpecification': self._write_constant_specification,
            'ConstantSpecificationMappingSet': self._write_constant_specification_mapping_set,
            # Port interface elements
            'NvDataInterface': self._write_nv_data_interface,
            'ParameterInterface': self._write_parameter_interface,
            'SenderReceiverInterface': self._write_sender_receiver_interface,
            'ClientServerInterface': self._write_client_server_interface,
            'ModeSwitchInterface': self._write_mode_switch_interface,
            'TriggerInterface': self._write_trigger_interface,
            # Mode declaration elements
            'ModeDeclarationGroup': self._write_mode_declaration_group,
            # System template elements
            'E2EProfileCompatibilityProps': self._write_e2e_profile_compatibility_props,
            # Software component elements
            'ApplicationSoftwareComponentType': self._write_application_software_component_type,
            'ComplexDeviceDriverSwComponentType': self._write_complex_device_driver_sw_component_type,
            'NvBlockSwComponentType': self._write_nv_block_sw_component_type,
            'EcuAbstractionSwComponentType': self._write_ecu_abstraction_sw_component_type,
            'SensorActuatorSwComponentType': self._write_sensor_actuator_sw_component_type,
            'ServiceSwComponentType': self._write_service_sw_component_type,
            'ServiceProxySwComponentType': self._write_service_proxy_sw_component_type,
            'CompositionSwComponentType': self._write_composition_sw_component_type,
            'SwcImplementation': self._write_swc_implementation,
        }
        # Value specification elements
        self.switcher_value_specification = {
            'TextValueSpecification': self._write_text_value_specification,
            'NumericalValueSpecification': self._write_numerical_value_specification,
            'NotAvailableValueSpecification': self._write_not_available_value_specification,
            'ArrayValueSpecification': self._write_array_value_specification,
            'RecordValueSpecification': self._write_record_value_specification,
            'ApplicationValueSpecification': self._write_application_value_specification,
            'ConstantReference': self._write_constant_reference,
            'ReferenceValueSpecification': self._write_reference_value_specification,
            'NumericalRuleBasedValueSpecification': self._write_numerical_rule_based_value_specification,
            'ApplicationRuleBasedValueSpecification': self._write_application_rule_based_value_specification,
            'CompositeRuleBasedValueSpecification': self._write_composite_rule_based_value_specification,
        }
        # Com-spec elements
        self.switcher_provided_com_spec = {
            'ModeSwitchSenderComSpec': self._write_mode_switch_sender_com_spec,
            'QueuedSenderComSpec': self._write_queued_sender_com_spec,
            'NonqueuedSenderComSpec': self._write_non_queued_sender_com_spec,
            'NvProvideComSpec': self._write_nv_provide_com_spec,
            'ParameterProvideComSpec': self._write_parameter_provide_com_spec,
            'ServerComSpec': self._write_server_com_spec,
        }
        self.switcher_required_com_spec = {
            'QueuedReceiverComSpec': self._write_queued_receiver_com_spec,
            'NonqueuedReceiverComSpec': self._write_nonqueued_receiver_com_spec,
            'NvRequireComSpec': self._write_nv_require_com_spec,
            'ParameterRequireComSpec': self._write_parameter_require_com_spec,
            'ModeSwitchReceiverComSpec': self._write_mode_switch_receiver_com_spec,
            'ClientComSpec': self._write_client_com_spec,
        }
        self.switcher_rte_event = {
            'AsynchronousServerCallReturnsEvent': self._write_async_server_call_returns_event,
            'BackgroundEvent': self._write_background_event,
            'DataReceiveErrorEvent': self._write_data_receive_error_event,
            'DataReceivedEvent': self._write_data_received_event,
            'DataSendCompletedEvent': self._write_data_send_completed_event,
            'DataWriteCompletedEvent': self._write_data_write_completed_event,
            'ExternalTriggerOccurredEvent': self._write_external_trigger_occured_event,
            'InitEvent': self._write_init_event,
            'InternalTriggerOccurredEvent': self._write_internal_trigger_occured_event,
            'ModeSwitchedAckEvent': self._write_mode_switched_ack_event,
            'OperationInvokedEvent': self._write_operation_invoked_event,
            'SwcModeManagerErrorEvent': self._write_swc_mode_manager_error_event,
            'SwcModeSwitchEvent': self._write_swc_mode_switch_event,
            'TimingEvent': self._write_timing_event,
            'TransformerHardErrorEvent': self._write_transformer_hard_error_event,
        }
        # Elements used only for unit test purposes
        self.switcher_non_collectable = {
            # Documentation elements
            'Annotation': self._write_annotation,
            'Break': self._write_break,
            'DocumentationBlock': self._write_documentation_block,
            'EmphasisText': self._write_emphasis_text,
            'IndexEntry': self._write_index_entry,
            'MultilanguageLongName': self._write_multi_language_long_name,
            'MultiLanguageOverviewParagraph': self._write_multi_language_overview_paragraph,
            'MultiLanguageParagraph': self._write_multi_language_paragraph,
            'MultiLanguageVerbatim': self._write_multi_language_verbatim,
            'LanguageLongName': self._write_language_long_name,
            'LanguageParagraph': self._write_language_paragraph,
            'LanguageVerbatim': self._write_language_verbatim,
            'Package': self._write_package,
            'SingleLanguageUnitNames': self._write_single_language_unit_names,
            'Superscript': self._write_superscript,
            'Subscript': self._write_subscript,
            'TechnicalTerm': self._write_technical_term,
            'MultiLanguagePlainText': self._write_multi_language_plain_text,
            'Date': self._write_date,
            'RevisionLabelString': self._write_revision_label_string,
            # AdminData elements
            'SpecialDataGroup': self._write_special_data_group,
            'Modification': self._write_modification,
            'DocRevision': self._write_doc_revision,
            'AdminData': self._write_admin_data,
            # CompuMethod elements
            'Computation': self._write_computation,
            'CompuRational': self._write_compu_rational,
            'CompuScale': self._write_compu_scale,
            # Constant elements
            'NumericalOrText': self._write_numerical_or_text,
            'RuleArguments': self._write_rule_arguments,
            'RuleBasedValueSpecification': self._write_rule_based_value_specification,
            # Constraint elements
            'ScaleConstraint': self._write_scale_constraint,
            'InternalConstraint': self._write_internal_constraint,
            'PhysicalConstraint': self._write_physical_constraint,
            'DataConstraintRule': self._write_data_constraint_rule,
            # DataType and DataDictionary elements
            'SwDataDefPropsConditional': self._write_sw_data_def_props_conditional,
            'SwBaseTypeRef': self._write_sw_base_type_ref,
            'SwBitRepresentation': self._write_sw_bit_represenation,
            'SwTextProps': self._write_sw_text_props,
            'SwPointerTargetProps': self._write_sw_pointer_target_props,
            'SymbolProps': self._write_symbol_props,
            'ImplementationDataTypeElement': self._write_implementation_data_type_element,
            'ApplicationArrayElement': self._write_application_array_element,
            'ApplicationRecordElement': self._write_application_record_element,
            'DataTypeMap': self._write_data_type_map,
            'ConstantSpecificationMapping': self._write_constant_specification_mapping,
            'ValueList': self._write_value_list,
            'VariableDataPrototype': self._write_variable_data_prototype,
            'ParameterDataPrototype': self._write_parameter_data_prototype,
            'ArgumentDataPrototype': self._write_argument_data_prototype,
            'ModeRequestTypeMap': self._write_mode_request_type_map,
            # CalibrationData elements
            'SwValues': self._write_sw_values,
            'SwAxisCont': self._write_sw_axis_cont,
            'SwValueCont': self._write_sw_value_cont,
            'RuleBasedAxisCont': self._write_rule_based_axis_cont,
            'RuleBasedValueCont': self._write_rule_based_value_cont,
            'MultidimensionalTime': self._write_multidimensional_time,
            # Reference elements
            'PhysicalDimensionRef': self._write_physical_dimension_ref,
            'ApplicationDataTypeRef': self._write_application_data_type_ref,
            'ConstantRef': self._write_constant_ref,
            'ConstantSpecificationMappingSetRef': self._write_constant_specification_mapping_set_ref,
            # Port interface elements
            'InvalidationPolicy': self._write_invalidation_policy,
            'ApplicationError': self._write_application_error,
            'ClientServerOperation': self._write_client_server_operation,
            # ModeDeclaration elements
            'ModeDeclaration': self._write_mode_declaration,
            'ModeErrorBehavior': self._write_mode_error_behavior,
            'ModeTransition': self._write_mode_transition,
            'ModeDeclarationGroupPrototype': self._write_mode_declaration_group_prototype,
            # System template elements
            'EndToEndTransformationComSpecProps': self._write_e2e_transformation_com_spec_props,
            # Software component elements
            'ModeSwitchedAckRequest': self._write_mode_switched_ack_request,
            'TransmissionAcknowledgementRequest': self._write_transmission_acknowledgement_request,
            'TransmissionComSpecProps': self._write_tranmsission_com_spec_props,
            'ReceptionComSpecProps': self._write_reception_com_spec_props,
            'ClientComSpec': self._write_client_com_spec,
            'ProvidePortPrototype': self._write_provide_port_prototype,
            'RequirePortPrototype': self._write_require_port_prototype,
            'PRPortPrototype': self._write_pr_port_prototype,
            'SwComponentPrototype': self._write_sw_component_prototype,
            'PortInCompositionTypeInstanceRef': self._write_port_in_composition_type_instance_ref,
            'AssemblySwConnector': self._write_assembly_sw_connector,
            'DelegationSwConnector': self._write_delegation_sw_connector,
            'PassThroughSwConnector': self._write_passthrough_sw_connector,
            'RModeInAtomicSwcInstanceRef': self._write_r_mode_in_atomic_swc_instance_ref,
            'RModeGroupInAtomicSwcInstanceRef': self._write_r_mode_group_in_atomic_swc_instance_ref,
            # Service needs elements
            'BswMgrNeeds': self._write_bsw_mgr_needs,
            'ComMgrUserNeeds': self._write_com_mgr_user_needs,
            'CryptoCertificateKeySlotNeeds': self._write_crypto_certificate_key_slot_needs,
            'CryptoKeyManagementNeeds': self._write_crypto_key_management_needs,
            'CryptoServiceJobNeeds': self._write_crypto_service_job_needs,
            'CryptoServiceNeeds': self._write_crypto_service_needs,
            'DevelopmentError': self._write_development_error,
            'DiagEventDebounceCounterBased': self._write_diag_event_debounce_counter_based,
            'DiagEventDebounceMonitorInternal': self._write_diag_event_debounce_monitor_internal,
            'DiagEventDebounceTimeBased': self._write_diag_event_debounce_time_based,
            'DiagnosticClearConditionNeeds': self._write_diagnostic_clear_condition_needs,
            'DiagnosticCommunicationManagerNeeds': self._write_diagnostic_communication_manager_needs,
            'DiagnosticComponentNeeds': self._write_diagnostic_component_needs,
            'DiagnosticControlNeeds': self._write_diagnostic_control_needs,
            'DiagnosticEnableConditionNeeds': self._write_diagnostic_enable_condition_needs,
            'DiagnosticEventInfoNeeds': self._write_diagnostic_event_info_needs,
            'DiagnosticEventManagerNeeds': self._write_diagnostic_event_manager_needs,
            'DiagnosticEventNeeds': self._write_diagnostic_event_needs,
            'DiagnosticGenericUdsNeeds': self._write_diagnostic_generic_uds_needs,
            'DiagnosticIndicatorNeeds': self._write_diagnostic_indicator_needs,
            'DiagnosticIoControlNeeds': self._write_diagnostic_io_control_needs,
            'DiagnosticOperationCycleNeeds': self._write_diagnostic_operation_cycle_needs,
            'DiagnosticRequestFileTransferNeeds': self._write_diagnostic_request_file_transfer_needs,
            'DiagnosticResponseOnEventNeeds': self._write_diagnostic_response_on_event_needs,
            'DiagnosticRoutineNeeds': self._write_diagnostic_routine_needs,
            'DiagnosticStorageConditionNeeds': self._write_diagnostic_storage_condition_needs,
            'DiagnosticUploadDownloadNeeds': self._write_diagnostic_upload_download_needs,
            'DiagnosticValueNeeds': self._write_diagnostic_value_needs,
            'DiagnosticsCommunicationSecurityNeeds': self._write_diagnostics_communication_security_needs,
            'DltUserNeeds': self._write_dlt_user_needs,
            'DoIpActivationLineNeeds': self._write_do_ip_activation_line_needs,
            'DoIpGidNeeds': self._write_do_ip_gid_needs,
            'DoIpGidSynchronizationNeeds': self._write_do_ip_gid_synchronization_needs,
            'DoIpPowerModeStatusNeeds': self._write_do_ip_power_mode_status_needs,
            'DoIpRoutingActivationAuthenticationNeeds': self._write_do_ip_routing_activation_authentication_needs,
            'DoIpRoutingActivationConfirmationNeeds': self._write_do_ip_routing_activation_confirmation_needs,
            'DtcStatusChangeNotificationNeeds': self._write_dtc_status_change_notification_needs,
            'EcuStateMgrUserNeeds': self._write_ecu_state_mgr_user_needs,
            'ErrorTracerNeeds': self._write_error_tracer_needs,
            'FunctionInhibitionAvailabilityNeeds': self._write_function_inhibition_availability_needs,
            'FunctionInhibitionNeeds': self._write_function_inhibition_needs,
            'FurtherActionByteNeeds': self._write_further_action_byte_needs,
            'GlobalSupervisionNeeds': self._write_global_supervision_needs,
            'HardwareTestNeeds': self._write_hardware_test_needs,
            'IdsMgrCustomTimestampNeeds': self._write_ids_mgr_custom_timestamp_needs,
            'IdsMgrNeeds': self._write_ids_mgr_needs,
            'IndicatorStatusNeeds': self._write_indicator_status_needs,
            'J1939DcmDm19Support': self._write_j1939_dcm_dm_19_support,
            'J1939RmIncomingRequestServiceNeeds': self._write_j1939_rm_incoming_request_service_needs,
            'J1939RmOutgoingRequestServiceNeeds': self._write_j1939_rm_outgoing_request_service_needs,
            'NvBlockNeeds': self._write_nv_block_needs,
            'ObdControlServiceNeeds': self._write_obd_control_service_needs,
            'ObdInfoServiceNeeds': self._write_obd_info_service_needs,
            'ObdMonitorServiceNeeds': self._write_obd_monitor_service_needs,
            'ObdPidServiceNeeds': self._write_obd_pid_service_needs,
            'ObdRatioDenominatorNeeds': self._write_obd_ratio_denominator_needs,
            'ObdRatioServiceNeeds': self._write_obd_ratio_service_needs,
            'PossibleErrorReaction': self._write_possible_error_reaction,
            'RuntimeError': self._write_runtime_error,
            'SecureOnBoardCommunicationNeeds': self._write_secure_on_board_communication_needs,
            'SupervisedEntityCheckpointNeeds': self._write_supervised_entity_checkpoint_needs,
            'SupervisedEntityCheckpointNeedsRefConditional':
            self._write_supervised_entity_checkpoint_needs_ref_conditional,
            'SupervisedEntityNeeds': self._write_supervised_entity_needs,
            'SyncTimeBaseMgrUserNeeds': self._write_sync_time_base_mgr_user_needs,
            'TransientFault': self._write_transient_fault,
            'VendorSpecificServiceNeeds': self._write_vendor_specific_service_needs,
            'V2xDataManagerNeeds': self._write_v2x_data_manager_needs,
            'V2xFacUserNeeds': self._write_v2x_fac_user_needs,
            'V2xMUserNeeds': self._write_v2x_m_user_needs,
            'WarningIndicatorRequestedBitNeeds': self._write_warning_indicator_requested_bit_needs,
            # SWC internal behavior elements
            'ArVariableInImplementationDataInstanceRef': self._write_variable_in_impl_data_instance_ref,
            'VariableInAtomicSWCTypeInstanceRef': self._write_variable_in_atomic_swc_type_instance_ref,
            'AutosarVariableRef': self._write_autosar_variable_ref,
            'VariableAccess': self._write_variable_access,
            'SwcInternalBehavior': self._write_swc_internal_behavior,
            'ExclusiveArea': self._write_exclusive_area,
            'ExclusiveAreaNestingOrder': self._write_exclusive_area_nesting_order,
            'ExecutableEntityActivationReason': self._write_executable_entity_activation_reason,
            'ExclusiveAreaRefConditional': self._write_exclusive_area_ref_conditional,
            'SwcExclusiveAreaPolicy': self._write_swc_exclusive_area_policy,
            'IncludedDataTypeSet': self._write_included_data_type_set,
            'IncludedModeDeclarationGroupSet': self._write_included_mode_declaration_group_set,
            'InstantiationDataDefProps': self._write_instantiation_data_def_props,
            'PerInstanceMemory': self._write_per_instance_memory,
            'RunnableEntityArgument': self._write_runnable_entity_argument,
            'RunnableEntity': self._write_runnable_entity,
            'AsynchronousServerCallReturnsEvent': self._write_async_server_call_returns_event,
            'BackgroundEvent': self._write_background_event,
            'DataReceiveErrorEvent': self._write_data_receive_error_event,
            'DataReceivedEvent': self._write_data_received_event,
            'DataSendCompletedEvent': self._write_data_send_completed_event,
            'DataWriteCompletedEvent': self._write_data_write_completed_event,
            'ExternalTriggerOccurredEvent': self._write_external_trigger_occured_event,
            'InitEvent': self._write_init_event,
            'InternalTriggerOccurredEvent': self._write_internal_trigger_occured_event,
            'ModeSwitchedAckEvent': self._write_mode_switched_ack_event,
            'OperationInvokedEvent': self._write_operation_invoked_event,
            'SwcModeManagerErrorEvent': self._write_swc_mode_manager_error_event,
            'SwcModeSwitchEvent': self._write_swc_mode_switch_event,
            'TimingEvent': self._write_timing_event,
            'TransformerHardErrorEvent': self._write_transformer_hard_error_event,
            'PortDefinedArgumentValue': self._write_port_defined_argument_value,
            'CommunicationBufferLocking': self._write_communication_buffer_locking,
            'PortApiOption': self._write_port_api_option,
            'AsynchronousServerCallPoint': self._write_async_server_call_point,
            'SynchronousServerCallPoint': self._write_sync_server_call_point,
            'AsynchronousServerCallResultPoint': self._write_async_server_call_result_point,
            'ExternalTriggeringPoint': self._write_external_triggering_point,
            'InternalTriggeringPoint': self._write_internal_triggering_point,
            'ModeAccessPoint': self._write_mode_access_point,
            'ModeSwitchPoint': self._write_mode_switch_point,
            'ParameterInAtomicSwcTypeInstanceRef': self._write_parameter_in_atomic_swc_type_instance_ref,
            'AutosarParameterRef': self._write_autosar_parameter_ref,
            'ParameterAccess': self._write_parameter_access,
            'RoleBasedDataAssignment': self._write_role_based_data_assignment,
            'RoleBasedDataTypeAssignment': self._write_role_based_data_type_assignment,
            'RoleBasedPortAssignment': self._write_role_based_port_assignment,
            'SymbolicNameProps': self._write_symbolic_name_props,
            'SwcServiceDependency': self._write_swc_service_dependency,
            'WaitPoint': self._write_wait_point,
        }
        #
        self.switcher_all = {}  # All concrete elements (used for unit testing)
        self.switcher_all.update(self.switcher_collectable)
        self.switcher_all.update(self.switcher_value_specification)
        self.switcher_all.update(self.switcher_provided_com_spec)
        self.switcher_all.update(self.switcher_required_com_spec)
        self.switcher_all.update(self.switcher_non_collectable)

    def write_str(self, document: ar_document.Document, skip_root_attr: bool = True) -> str:
        """
        Serializes the document to string.
        """
        self._str_open()
        self._write_document(document, skip_root_attr)
        return self.fh.getvalue()

    def write_file(self, document: ar_document.Document, file_path: str):
        """
        Serialized the document to file
        """
        self._open(file_path)
        self._write_document(document)
        self._close()

    def write_str_elem(self, elem: ar_element.ARObject, tag: str | None = None):
        """
        Writes single ARXML element as string
        """
        self._str_open()
        class_name = elem.__class__.__name__
        write_method = self.switcher_all.get(class_name, None)
        if write_method is not None:
            if tag is not None:
                write_method(elem, tag)
            else:
                write_method(elem)
        else:
            raise NotImplementedError(
                f"Found no writer for class {class_name}")
        return self.fh.getvalue()

    def write_file_elem(self, elem: ar_element.ARElement, file_path: str):
        """
        Writes single ARXML element to file
        """
        self._open(file_path)
        class_name = elem.__class__.__name__
        write_method = self.switcher_collectable.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for {class_name}")
        self._close()

    # Abstract base classes

    def _write_referrable(self, elem: ar_element.MultiLanguageReferrable):
        """
        Writes group AR:REFERRABLE
        """
        self._add_content('SHORT-NAME', elem.name)

    def _write_multilanguage_referrable(self, elem: ar_element.MultiLanguageReferrable):
        """
        Writes AR:MULTILANGUAGE-REFFERABLE
        """
        if elem.long_name is not None:
            self._write_multi_language_long_name(elem.long_name, 'LONG-NAME')

    def _collect_identifiable_attributes(self, elem: ar_element.Identifiable, attr: TupleList):
        if elem.uuid is not None:
            attr.append(('UUID', elem.uuid))
        if len(attr) > 0:
            return attr
        return None

    def _write_identifiable(self, elem: ar_element.Identifiable) -> None:
        """
        Writes group AR:IDENTIFIABLE
        """
        if elem.desc:
            self._write_multi_language_overview_paragraph(elem.desc, 'DESC')
        if elem.category:
            self._add_content('CATEGORY', elem.category)
        if elem.admin_data:
            self._write_admin_data(elem.admin_data)
        if elem.introduction:
            self._write_documentation_block(elem.introduction, 'INTRODUCTION')
        if elem.annotations:
            self._write_annotations(elem.annotations)

    # AdminData

    def _write_special_data_group(self, elem: ar_element.SpecialDataGroup) -> None:
        """
        Writes complex type AR:SDG
        Multi-tagged: False
        """
        tag = "SDG"
        assert isinstance(elem, ar_element.SpecialDataGroup)
        attr: TupleList = []
        if elem.gid is not None:
            attr.append(('GID', elem.gid))
        if elem.is_empty_with_ignore({"gid"}):
            self._add_content(tag, attr=attr)
            return
        self._add_child(tag, attr)
        self._write_special_data_group_internal(elem)
        self._leave_child()

    def _write_special_data_group_internal(self, elem: ar_element.SpecialDataGroup) -> None:
        """
        Writes group AR:SDG
        """
        if elem.caption is not None:
            self._add_content('SDG-CAPTION', elem.caption)
        if elem.content:
            for child in elem.content:
                if isinstance(child, ar_element.SpecialDataElement):
                    self._write_special_data_element(child)
                elif isinstance(child, ar_element.SpecialDataValue):
                    self._write_special_data_value(child)
                elif isinstance(child, ar_element.SpecialDataGroup):
                    self._write_special_data_group(child)

    def _write_special_data_element(self, elem: ar_element.SpecialDataElement) -> None:
        """
        Writes special data content
        """
        assert isinstance(elem, ar_element.SpecialDataElement)
        if elem.gid is None:
            self._add_content("SD", elem.text)
        else:
            self._add_content("SD", elem.text, [("GID", elem.gid)])

    def _write_special_data_value(self, elem: ar_element.SpecialDataValue) -> None:
        """
        Writes numerical special data content
        """
        assert isinstance(elem, ar_element.SpecialDataValue)
        if elem.gid is None:
            self._add_content("SDF", self._format_float(elem.value))
        else:
            self._add_content("SDF", self._format_float(elem.value), [("GID", elem.gid)])

    def _write_modification(self, elem: ar_element.Modification) -> None:
        """
        Writes complex type AR:MODIFICATION
        Multi-tagged: False
        """
        tag = "MODIFICATION"
        assert isinstance(elem, ar_element.Modification)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_modification_group(elem)
            self._leave_child()

    def _write_modification_group(self, elem: ar_element.Modification) -> None:
        """
        Writes group AR:MODIFICATION
        """
        if elem.change is not None:
            self._write_multi_language_overview_paragraph(elem.change, "CHANGE")
        if elem.reason is not None:
            self._write_multi_language_overview_paragraph(elem.reason, "REASON")

    def _write_doc_revision(self, elem: ar_element.DocRevision) -> None:
        """
        Writes complex type AR:DOC-REVISION
        Multi-tagged: False
        """
        tag = "DOC-REVISION"
        assert isinstance(elem, ar_element.DocRevision)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_doc_revision_group(elem)
            self._leave_child()

    def _write_doc_revision_group(self, elem: ar_element.DocRevision) -> None:
        """
        Writes group AR:DOC-REVISION
        """
        if elem.revision_label is not None:
            self._write_revision_label_string(elem.revision_label, "REVISION-LABEL")
        if elem.revision_label_p1 is not None:
            self._write_revision_label_string(elem.revision_label_p1, "REVISION-LABEL-P1")
        if elem.revision_label_p2 is not None:
            self._write_revision_label_string(elem.revision_label_p2, "REVISION-LABEL-P2")
        if elem.state is not None:
            self._add_content("STATE", elem.state)
        if elem.issued_by is not None:
            self._add_content("ISSUED-BY", elem.issued_by)
        if elem.date is not None:
            self._write_date(elem.date)
        if elem.modifications:
            self._add_child("MODIFICATIONS")
            for modification in elem.modifications:
                self._write_modification(modification)
            self._leave_child()

    def _write_admin_data(self, elem: ar_element.AdminData) -> None:
        """
        Writes complex type AR:ADMIN-DATA
        Multi-tagged: False
        """
        tag = "ADMIN-DATA"
        assert isinstance(elem, ar_element.AdminData)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_admin_data_group(elem)
            self._leave_child()

    def _write_admin_data_group(self, elem: ar_element.AdminData) -> None:
        """
        Writes group AR:ADMIN-DATA
        """
        if elem.language is not None:
            self._add_content("LANGUAGE", ar_enum.enum_to_xml(elem.language))
        if elem.used_languages is not None:
            self._write_multi_language_plain_text(elem.used_languages, "USED-LANGUAGES")
        if elem.doc_revisions:
            self._add_child("DOC-REVISIONS")
            for revision in elem.doc_revisions:
                self._write_doc_revision(revision)
            self._leave_child()
        if elem.sdgs:
            self._add_child("SDGS")
            for sdg in elem.sdgs:
                self._write_special_data_group(sdg)
            self._leave_child()

    # AUTOSAR Document

    def _write_document(self, document: ar_document.Document, skip_root_attr: bool = False):
        self.schema_version = document.schema_version
        self._add_line('<?xml version="1.0" encoding="utf-8"?>')
        if skip_root_attr:
            self._add_child("AUTOSAR")
        else:
            self._add_child("AUTOSAR", [('xsi:schemaLocation',
                                         f'http://autosar.org/schema/r4.0 {document.schema_file}'),
                                        ('xmlns', 'http://autosar.org/schema/r4.0'),
                                        ('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')])
        if len(document.packages) > 0:
            self._write_packages(document.packages)
        self._leave_child()

    def _write_packages(self, packages: list[ar_element.Package]):
        self._add_child("AR-PACKAGES")
        for package in packages:
            self._write_package(package)
        self._leave_child()

    # AUTOSAR PACKAGE

    def _write_package(self, package: ar_element.Package) -> None:
        """
        Writes complex type AR:AR-PACKAGE
        Multi-tagged: False
        """
        assert isinstance(package, ar_element.Package)
        attr: TupleList = []
        self._collect_identifiable_attributes(package, attr)
        self._add_child("AR-PACKAGE", attr)
        self._write_referrable(package)
        self._write_multilanguage_referrable(package)
        self._write_identifiable(package)
        if len(package.elements) > 0:
            self._write_package_elements(package)
        if len(package.packages) > 0:
            self._write_sub_packages(package)
        self._leave_child()

    def _write_package_elements(self, package: ar_element.Package) -> None:
        self._add_child('ELEMENTS')
        for elem in package.elements:
            class_name = elem.__class__.__name__
            write_method = self.switcher_collectable.get(class_name, None)
            if write_method is not None:
                write_method(elem)
            else:
                raise NotImplementedError(
                    f"Package: Found no writer for {class_name}")
        self._leave_child()

    def _write_sub_packages(self, package: ar_element.Package) -> None:
        self._add_child('AR-PACKAGES')
        for sub_package in package.packages:
            self._write_package(sub_package)
        self._leave_child()

    # Documentation Elements

    def _write_annotation(self, elem: ar_element.Annotation) -> None:
        """
        Writes AR:ANNOTATION
        """
        assert isinstance(elem, ar_element.Annotation)
        tag = 'ANNOTATION'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_general_annotation(elem)
            self._leave_child()

    def _write_annotations(self, elements: list[ar_element.Annotation]) -> None:
        """
        Writes an unbounded list of AR:ANNOTATION
        """
        tag = 'ANNOTATIONS'
        if elements:
            for elem in elements:
                self._add_child(tag)
                self._write_annotation(elem)
                self._leave_child()
        else:
            self._add_content(tag)

    def _write_break(self, elem: ar_element.Break, inline=True) -> None:
        """
        Writes AR:BR
        """
        assert isinstance(elem, ar_element.Break)
        self._add_content('BR', '', inline=inline)

    def _write_documentation_block(self, elem: ar_element.DocumentationBlock, tag: str):
        """
        Writes AR:DOCUMENTATION-BLOCK
        """
        assert isinstance(elem, ar_element.DocumentationBlock)
        if not elem.elements:
            self._add_content(tag)
        else:
            self._add_child(tag)
            for child_elem in elem.elements:
                if isinstance(child_elem, ar_element.MultiLanguageParagraph):
                    self._write_multi_language_paragraph(child_elem)
                elif isinstance(child_elem, ar_element.MultiLanguageVerbatim):
                    self._write_multi_language_verbatim(child_elem)
                else:
                    raise NotImplementedError(str(type(child_elem)))
            self._leave_child()

    def _write_emphasis_text(self, elem: ar_element.EmphasisText, inline=True):
        """
        Writes AR:EMPHASIS-TEXT

        TagName: E
        """
        assert isinstance(elem, ar_element.EmphasisText)
        attr = self._collect_emphasis_text_attributes(elem)
        if len(elem.elements) == 1 and isinstance(elem.elements[0], str):
            self._add_content('E', elem.elements[0], attr, inline=inline)
        else:
            raise NotImplementedError(
                'EMPHASIS-TEXT currently supports single str element only')

    def _collect_emphasis_text_attributes(self, elem: ar_element.EmphasisText) -> None | TupleList:
        attr: TupleList = []
        if elem.color is not None:
            attr.append(('COLOR', elem.color))
        if elem.font is not None:
            attr.append(('FONT', ar_enum.enum_to_xml(elem.font)))
        if elem.type is not None:
            attr.append(('TYPE', ar_enum.enum_to_xml(elem.type)))
        if len(attr) > 0:
            return attr
        return None

    def _write_index_entry(self, elem: ar_element.IndexEntry, inline=True):
        """
        Writes IndexEntry (AR:INDEX-ENTRY)
        """
        assert isinstance(elem, ar_element.IndexEntry)
        self._add_content('IE', elem.text, inline=inline)

    def _write_technical_term(self, elem: ar_element.TechnicalTerm, inline=True):
        """
        Writes AR:TT

        TagName: TT
        """
        assert isinstance(elem, ar_element.TechnicalTerm)
        attr: TupleList = []
        self._collect_technical_term_attributes(elem, attr)
        self._add_content('TT', elem.text, attr, inline)

    def _collect_technical_term_attributes(self, elem: ar_element.TechnicalTerm, attr: TupleList):
        """
        Writes group AR:TT
        """
        if elem.tex_render is not None:
            attr.append(('TEX-RENDER', elem.tex_render))
        if elem.type is not None:
            attr.append(('TYPE', elem.type))

    def _write_superscript(self, elem: ar_element.Superscript, inline=True):
        """
        Writes Superscript (AR:SUPSCRIPT)
        """
        assert isinstance(elem, ar_element.Superscript)
        self._add_content('SUP', elem.text, inline=inline)

    def _write_subscript(self, elem: ar_element.Subscript, inline=True):
        """
        Writes Subscript (AR:SUPSCRIPT)
        """
        assert isinstance(elem, ar_element.Subscript)
        self._add_content('SUB', elem.text, inline=inline)

    def _write_multi_language_long_name(self, elem: ar_element.MultilanguageLongName, tag: str) -> None:
        """
        Writes complex type AR:MULTILANGUAGE-LONG-NAME
        Multi-tagged: True
        """
        # assert isinstance(elem.tag, str)
        self._add_child(tag)
        for child_elem in elem.elements:
            self._write_language_long_name(child_elem)
        self._leave_child()

    def _write_language_long_name(self, elem: ar_element.LanguageLongName):
        """
        Writes complex type AR:L-LONG-NAME
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.LanguageLongName)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-4'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.IndexEntry):
                self._write_index_entry(part, inline=True)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part, inline=True)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: ' + str(type(part)))
        self._end_line(tag)

    def _collect_language_specific_attr(self, elem: ar_element.LanguageSpecific, attr: TupleList) -> None:
        """
        Writes group AR:LANGUAGE-SPECIFIC
        """
        attr.append(('L', ar_enum.enum_to_xml(elem.language))
                    )  # The L attribute is mandatory

    def _write_multi_language_overview_paragraph(self, elem: MultiLanguageOverviewParagraph, tag: str) -> None:
        """
        Writes complex type AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
        Multi-tagged: True
        """
        assert isinstance(elem, MultiLanguageOverviewParagraph)
        if tag not in {'DESC', 'ITEM-LABEL', 'CHANGE', 'REASON'}:
            raise ValueError('Invalid tag parameter: ' + tag)
        self._add_child(tag)
        for child_elem in elem.elements:
            self._write_language_overview_paragraph(child_elem)
        self._leave_child()

    def _write_multi_language_verbatim(self, elem: ar_element.MultiLanguageVerbatim) -> None:
        """
        Writes complex type AR:MULTI-LANGUAGE-VERBATIM
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.MultiLanguageVerbatim)
        attr: TupleList = []
        self._collect_document_view_selectable_attributes(elem, attr)
        self._collect_paginateable_attributes(elem, attr)
        self._collect_multi_language_verbatim_attributes(elem, attr)
        self._add_child('VERBATIM', attr)
        for child_elem in elem.elements:
            self._write_language_verbatim(child_elem)
        self._leave_child()

    def _collect_multi_language_verbatim_attributes(self,
                                                    elem: ar_element.MultiLanguageVerbatim,
                                                    attr: TupleList):
        """
        Writes group AR:MULTI-LANGUAGE-VERBATIM
        """
        if elem.allow_break is not None:
            attr.append(('ALLOW-BREAK', elem.allow_break))
        if elem.float is not None:
            attr.append(('FLOAT', ar_enum.enum_to_xml(elem.float)))
        if elem.help_entry is not None:
            attr.append(('HELP-ENTRY', elem.help_entry))
        if elem.page_wide is not None:
            attr.append(('PGWIDE', ar_enum.enum_to_xml(elem.page_wide)))

    def _write_language_overview_paragraph(self, elem: ar_element.LanguageOverviewParagraph) -> None:
        """
        Writes complex type AR:L-OVERVIEW-PARAGRAPH
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.LanguageOverviewParagraph)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-2'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Break):
                self._write_break(part, inline=True)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.IndexEntry):
                self._write_index_entry(part, inline=True)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part, inline=True)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: ' + str(type(part)))
        self._end_line(tag)

    def _write_language_paragraph(self, elem: ar_element.LanguageParagraph) -> None:
        """
        Writes complex type AR:L-PARAGRAPH
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.LanguageParagraph)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-1'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Break):
                self._write_break(part, inline=True)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.IndexEntry):
                self._write_index_entry(part, inline=True)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part, inline=True)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: ' + str(type(part)))
        self._end_line(tag)

    def _write_language_verbatim(self, elem: ar_element.LanguageVerbatim) -> None:
        """
        Writes complex type AR:L-VERBATIM
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.LanguageVerbatim)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        tag = 'L-5'
        self._begin_line(tag, attr)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Break):
                self._write_break(part, inline=True)
            elif isinstance(part, ar_element.EmphasisText):
                self._write_emphasis_text(part, inline=True)
            elif isinstance(part, ar_element.TechnicalTerm):
                self._write_technical_term(part, inline=True)
            else:
                raise TypeError('Unsupported type: ' + str(type(part)))
        self._end_line(tag)

    def _write_multi_language_paragraph(self, elem: ar_element.MultiLanguageParagraph) -> None:
        """
        Writes complex type AR:MULTI-LANGUAGE-PARAGRAPH
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.MultiLanguageParagraph)
        attr: TupleList = []
        self._collect_document_view_selectable_attributes(elem, attr)
        self._collect_paginateable_attributes(elem, attr)
        self._collect_multi_language_paragraph_attributes(elem, attr)
        self._add_child('P', attr)
        for child_elem in elem.elements:
            self._write_language_paragraph(child_elem)
        self._leave_child()

    def _collect_multi_language_paragraph_attributes(self,
                                                     elem: ar_element.MultiLanguageParagraph,
                                                     attr: TupleList):
        """
        Writes group AR:MULTI-LANGUAGE-PARAGRAPH
        """
        if elem.help_entry is not None:
            attr.append(('HELP-ENTRY', elem.help_entry))

    def _collect_document_view_selectable_attributes(self,
                                                     elem: ar_element.DocumentViewSelectable,
                                                     attr: TupleList):
        """
        Writes group AR:DOCUMENT-VIEW-SELECTABLE
        """
        if elem.semantic_information is not None:
            attr.append(('SI', elem.semantic_information))
        if elem.view is not None:
            attr.append(('VIEW', elem.view))

    def _collect_paginateable_attributes(self,
                                         elem: ar_element.Paginateable,
                                         attr: TupleList):
        """
        Writes group AR:PAGINATEABLE
        """
        if elem.page_break is not None:
            attr.append(('BREAK', ar_enum.enum_to_xml(elem.page_break)))
        if elem.keep_with_previous is not None:
            attr.append(
                ('KEEP-WITH-PREVIOUS', ar_enum.enum_to_xml(elem.keep_with_previous)))

    def _write_general_annotation(self, elem: ar_element.GeneralAnnotation) -> None:
        """
        Writes group AR:GENERAL-ANNOTATION
        """
        if elem.label is not None:
            self._write_multi_language_long_name(elem.label, 'LABEL')
        if elem.origin is not None:
            self._add_content('ANNOTATION-ORIGIN', str(elem.origin))
        if elem.text is not None:
            self._write_documentation_block(elem.text, 'ANNOTATION-TEXT')

    def _write_single_language_unit_names(self, elem: ar_element.SingleLanguageUnitNames, tag: str) -> None:
        """
        Writes complex type AR:SINGLE-LANGUAGE-UNIT-NAMES
        Multi-tagged: True

        Tab variants: 'PRM-UNIT' | 'UNIT-DISPLAY-NAME' | 'UNIT-DISPLAY-NAME' | 'DISPLAY-NAME'
        """
        assert isinstance(elem, ar_element.SingleLanguageUnitNames)
        self._begin_line(tag)
        for part in elem.parts:
            if isinstance(part, str):
                self._add_inline_text(part)
            elif isinstance(part, ar_element.Subscript):
                self._write_subscript(part)
            elif isinstance(part, ar_element.Superscript):
                self._write_superscript(part)
            else:
                raise TypeError('Unsupported type: ' + str(type(part)))
        self._end_line(tag)

    def _write_describable(self, elem: ar_element.Describable) -> None:
        """
        Writes group AR:DESCRIBABLE
        """
        assert isinstance(elem, ar_element.Describable)
        if elem.desc is not None:
            self._write_multi_language_overview_paragraph(elem.desc, "DESC")
        if elem.category is not None:
            self._add_content("CATEGORY", elem.category)
        if elem.introduction is not None:
            self._write_documentation_block(elem.introduction, "INTRODUCTION")
        if elem.admin_data is not None:
            self._write_admin_data(elem.admin_data)

    def _write_language_plain_text(self, elem: ar_element.LanguagePlainText) -> None:
        """
        Writes complex type AR:L-PLAIN-TEXT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.LanguagePlainText)
        attr: TupleList = []
        self._collect_language_specific_attr(elem, attr)
        self._add_content("L-10", elem.text, attr)

    def _write_multi_language_plain_text(self, elem: ar_element.MultiLanguagePlainText, tag: str) -> None:
        """
        Writes complex type AR:MULTI-LANGUAGE-PLAIN-TEXT
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.MultiLanguagePlainText)
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        for element in elem.elements:
            self._write_language_plain_text(element)
        self._leave_child()

    def _write_date(self, elem: ar_element.Date) -> None:
        """
        Writes complex type AR:DATE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.Date)
        self._add_content("DATE", str(elem))

    def _write_revision_label_string(self, elem: ar_element.RevisionLabelString, tag: str) -> None:
        """
        Writes complex type AR:REVISION-LABEL-STRING
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.RevisionLabelString)
        self._add_content(tag, str(elem))

    # CompuMethod elements

    def _write_compu_method(self, elem: ar_element.CompuMethod) -> None:
        """
        Writes complex type AR:COMPU-METHOD
        Multi-tagged: False

        Tab variants: 'COMPU-METHOD'
        """
        assert isinstance(elem, ar_element.CompuMethod)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child("COMPU-METHOD", attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_compu_method_group(elem)
        self._leave_child()

    def _write_compu_method_group(self, elem: ar_element.CompuMethod) -> None:
        """
        Writes group AR:COMPU-METHOD
        """
        if elem.display_format is not None:
            self._add_content("DISPLAY-FORMAT", str(elem.display_format))
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)
        if elem.int_to_phys is not None:
            self._write_computation(elem.int_to_phys, "COMPU-INTERNAL-TO-PHYS")
        if elem.phys_to_int is not None:
            self._write_computation(elem.phys_to_int, "COMPU-PHYS-TO-INTERNAL")

    def _write_computation(self, elem: ar_element.Computation, tag: str) -> None:
        """
        Writes AR:COMPU
        """
        self._add_child(tag)
        if elem.compu_scales is not None:
            self._add_child("COMPU-SCALES")
            for compu_scale in elem.compu_scales:
                self._write_compu_scale(compu_scale)
            self._leave_child()
        if elem.default_value is not None:
            self._write_compu_const(elem.default_value, "COMPU-DEFAULT-VALUE")
        self._leave_child()

    def _write_compu_scale(self, elem: ar_element.CompuScale) -> None:
        """
        Writes AR:COMPU-SCALE
        """
        assert isinstance(elem, ar_element.CompuScale)
        tag = "COMPU-SCALE"
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        if elem.label is not None:
            self._add_content("SHORT-LABEL", str(elem.label))
        if elem.symbol is not None:
            self._add_content("SYMBOL", str(elem.symbol))
        if elem.desc is not None:
            self._write_multi_language_overview_paragraph(elem.desc, "DESC")
        if elem.mask is not None:
            self._add_content("MASK", str(elem.mask))
        if elem.lower_limit is not None:
            self._write_limit("LOWER-LIMIT", elem.lower_limit, elem.lower_limit_type)
        if elem.upper_limit is not None:
            self._write_limit("UPPER-LIMIT", elem.upper_limit, elem.upper_limit_type)
        if elem.inverse_value is not None:
            self._write_compu_const(elem.inverse_value, "COMPU-INVERSE-VALUE")
        if elem.content is not None:
            if isinstance(elem.content, ar_element.CompuConst):
                self._write_compu_const(elem.content, "COMPU-CONST")
            elif isinstance(elem.content, ar_element.CompuRational):
                self._write_compu_rational(elem.content)
        self._leave_child()

    def _write_limit(self,
                     tag: str,
                     limit: int | float,
                     limit_type: ar_enum.IntervalType):
        assert limit is not None
        assert limit_type is not None
        attr: TupleList = [("INTERVAL-TYPE", ar_enum.enum_to_xml(limit_type))]
        if isinstance(limit, float):
            text = self._format_float(limit)
        elif isinstance(limit, int):
            text = str(limit)
        else:
            raise TypeError(f"Unsupported type: {str(type(limit))}")
        self._add_content(tag, text, attr)

    def _write_compu_const(self, elem: ar_element.CompuConst, tag) -> None:
        """
        Writes AR:COMPU-CONST
        """
        assert isinstance(elem, ar_element.CompuConst)
        self._add_child(tag)
        if isinstance(elem.value, str):
            self._add_content("VT", elem.value)
        elif isinstance(elem.value, float):
            self._add_content("V", self._format_float(elem.value))
        elif isinstance(elem.value, int):
            self._add_content("V", str(elem.value))
        else:
            raise TypeError(f"Unsupported type: {str(type(elem.value))}")
        self._leave_child()

    def _write_compu_rational(self, elem: ar_element.CompuRational) -> None:
        """
        Writes AR:COMPU-RATIONAL-COEFFS
        """
        assert isinstance(elem, ar_element.CompuRational)
        tag = 'COMPU-RATIONAL-COEFFS'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.numerator is not None:
                self._add_child('COMPU-NUMERATOR')
                self._write_numerator_denominator_values(elem.numerator)
                self._leave_child()
            if elem.denominator is not None:
                self._add_child('COMPU-DENOMINATOR')
                self._write_numerator_denominator_values(elem.denominator)
                self._leave_child()
            self._leave_child()

    def _write_numerator_denominator_values(self, value: int | float | tuple):
        if isinstance(value, tuple):
            for inner_value in value:
                if isinstance(inner_value, float):
                    content = self._format_float(inner_value)
                else:
                    content = str(inner_value)
                self._add_content('V', content)
        else:
            if isinstance(value, float):
                content = self._format_float(value)
            else:
                content = str(value)
            self._add_content('V', content)

    # Constraint elements

    def _write_data_constraint(self, elem: ar_element.DataConstraint) -> None:
        """
        Writes complex type AR:DATA-CONSTR
        Multi-tagged: False

        Tab variants: 'DATA-CONSTR-RULE'
        """
        assert isinstance(elem, ar_element.DataConstraint)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child("DATA-CONSTR", attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_data_constraint_group(elem)
        self._leave_child()

    def _write_data_constraint_group(self, elem: ar_element.DataConstraint) -> None:
        """
        Writes group AR:DATA-CONSTR-RULE
        """
        if elem.rules:
            self._add_child("DATA-CONSTR-RULES")
            for rule in elem.rules:
                self._write_data_constraint_rule(rule)
            self._leave_child()

    def _write_data_constraint_rule(self, elem: ar_element.DataConstraintRule) -> None:
        """
        Writes complex type AR:DATA-CONSTR-RULE
        Multi-tagged: False
        """
        tag = "DATA-CONSTR-RULE"
        assert isinstance(elem, ar_element.DataConstraintRule)
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        if elem.level is not None:
            self._add_content("CONSTR-LEVEL", str(elem.level))
        if elem.physical is not None:
            self._write_physical_constraint(elem.physical)
        if elem.internal is not None:
            self._write_internal_constraint(elem.internal)
        self._leave_child()

    def _write_internal_constraint(self, elem: ar_element.InternalConstraint) -> None:
        """
        Writes complex type AR:INTERNAL-CONSTRS
        Multi-tagged: False
        """
        tag = "INTERNAL-CONSTRS"
        assert isinstance(elem, ar_element.InternalConstraint)
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        self._write_constraint_base(elem)
        self._leave_child()

    def _write_physical_constraint(self, elem: ar_element.PhysicalConstraint) -> None:
        """
        Writes complex type AR:PHYS-CONSTRS
        Multi-tagged: False
        """
        tag = "PHYS-CONSTRS"
        assert isinstance(elem, ar_element.PhysicalConstraint)
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        self._write_constraint_base(elem)
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)
        self._leave_child()

    def _write_constraint_base(self,
                               elem: ar_element.InternalConstraint | ar_element.PhysicalConstraint) -> None:
        """
        Writes elements common for both AR:INTERNAL-CONSTRS and AR:PHYS-CONSTRS
        """
        if elem.lower_limit is not None:
            self._write_limit("LOWER-LIMIT", elem.lower_limit, elem.lower_limit_type)
        if elem.upper_limit is not None:
            self._write_limit("UPPER-LIMIT", elem.upper_limit, elem.upper_limit_type)
        if elem.scale_constrs:
            self._add_child("SCALE-CONSTRS")
            for scale_constr in elem.scale_constrs:
                self._write_scale_constraint(scale_constr)
            self._leave_child()
        if elem.max_gradient is not None:
            self._add_content("MAX-GRADIENT", self._format_number(elem.max_gradient))
        if elem.max_diff is not None:
            self._add_content("MAX-DIFF", self._format_number(elem.max_diff))
        if elem.monotony is not None:
            self._add_content("MONOTONY", ar_enum.enum_to_xml(elem.monotony))

    def _write_scale_constraint(self, elem: ar_element.ScaleConstraint) -> None:
        """
        Writes complex type AR:SCALE-CONSTR
        Multi-tagged: False
        """
        tag = "SCALE-CONSTR"
        assert isinstance(elem, ar_element.ScaleConstraint)
        attr: TupleList = []
        if elem.validity is not None:
            attr.append(("VALIDITY", ar_enum.enum_to_xml(elem.validity)))
        if elem.is_empty:
            self._add_content(tag, attr=attr)
            return
        self._add_child(tag, attr)
        if elem.label is not None:
            self._add_content("SHORT-LABEL", elem.label)
        if elem.desc is not None:
            self._write_multi_language_overview_paragraph(elem.desc, "DESC")
        if elem.lower_limit is not None:
            self._write_limit("LOWER-LIMIT", elem.lower_limit, elem.lower_limit_type)
        if elem.upper_limit is not None:
            self._write_limit("UPPER-LIMIT", elem.upper_limit, elem.upper_limit_type)
        self._leave_child()

    # Unit elements

    def _write_unit(self, elem: ar_element.Unit) -> None:
        """
        Writes complex type AR:UNIT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.Unit)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('UNIT', attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_unit_group(elem)
        self._leave_child()

    def _write_unit_group(self, elem: ar_element.Unit) -> None:
        if elem.display_name is not None:
            self._write_single_language_unit_names(elem.display_name, "DISPLAY-NAME")
        if elem.factor is not None:
            self._add_content("FACTOR-SI-TO-UNIT", self._format_float(elem.factor))
        if elem.offset is not None:
            self._add_content("OFFSET-SI-TO-UNIT", self._format_float(elem.offset))
        if elem.physical_dimension_ref is not None:
            self._write_physical_dimension_ref(elem.physical_dimension_ref)

    # Common structure elements

    def _write_data_filter(self, elem: ar_element.DataFilter, tag: str) -> None:
        """
        Writes complex type AR:DATA-FILTER
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.DataFilter)
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        self._write_data_filter_group(elem)
        self._leave_child()

    def _write_data_filter_group(self, elem: ar_element.DataFilter) -> None:
        """
        Writes group AR:DATA-FILTER
        """
        if elem.data_filter_type is not None:
            self._add_content("DATA-FILTER-TYPE", ar_enum.enum_to_xml(elem.data_filter_type))
        if elem.mask is not None:
            self._add_content("MASK", str(elem.mask))
        if elem.max_val is not None:
            self._add_content("MAX", str(elem.max_val))
        if elem.min_val is not None:
            self._add_content("MIN", str(elem.min_val))
        if elem.offset is not None:
            self._add_content("OFFSET", str(elem.offset))
        if elem.period is not None:
            self._add_content("PERIOD", str(elem.period))
        if elem.x is not None:
            self._add_content("X", str(elem.x))

    def _write_engineering_object(self, elem: ar_element.EngineeringObject) -> None:
        """
        Writes group AR:ENGINEERING-OBJECT
        """
        if elem.label is not None:
            self._add_content("SHORT-LABEL", str(elem.label))
        if elem.category is not None:
            self._add_content("CATEGORY", str(elem.category))

    def _write_autosar_engineering_object(self, elem: ar_element.AutosarEngineeringObject, tag: str) -> None:
        """
        Writes complex type AR:AUTOSAR-ENGINEERING-OBJECT
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.AutosarEngineeringObject)
        if elem.is_empty:
            self._add_content(tag)
            return
        self._add_child(tag)
        self._write_engineering_object(elem)
        self._leave_child()

    def _write_code(self, elem: ar_element.Code) -> None:
        """
        Writes complex type AR:CODE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.Code)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('CODE', attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.artifact_descriptors:
            self._add_child('ARTIFACT-DESCRIPTORS')
            for artifact_descriptor in elem.artifact_descriptors:
                self._write_autosar_engineering_object(artifact_descriptor, "AUTOSAR-ENGINEERING-OBJECT")
            self._leave_child()
        self._leave_child()
        # .CALLBACK-HEADER-REFS not yet implemented

    def _write_implementtion(self, elem: ar_element.Implementation) -> None:
        """
        Writes group AR:IMPLEMENTATION
        """
        # .BUILD-ACTION-MANIFESTS not yet supported
        if elem.code_descriptors:
            self._add_child("CODE-DESCRIPTORS")
            for code_descriptor in elem.code_descriptors:
                self._write_code(code_descriptor)
            self._leave_child()
        # .COMPILERS not yet supported
        # .GENERATED-ARTIFACTS not yet supported
        # .HW-ELEMENT-REFS not yet supported
        # .LINKERS not yet supported
        # .MC-SUPPORT not yet supported
        # .PROGRAMMING-LANGUAGE not yet supported
        # .REQUIRED-ARTIFACTS not yet supported
        # .REQUIRED-GENERATOR-TOOLS not yet supported
        # .RESOURCE-CONSUMPTION not yet supported
        # .SW-VERSION not yet supported
        # .SWC-BSW-MAPPING-REF not yet supported
        # .USED-CODE-GENERATOR not yet supported
        # .VENDOR-ID not yet supported

    def _write_trigger(self, elem: ar_element.Trigger) -> None:
        """
        Writes complex type AR:TRIGGER
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.Trigger)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('TRIGGER', attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_trigger_group(elem)
        self._leave_child()

    def _write_trigger_group(self, elem: ar_element.Trigger) -> None:
        """
        Writes group AR:TRIGGER
        """
        if elem.sw_impl_policy is not None:
            self._add_content("SW-IMPL-POLICY", ar_enum.enum_to_xml(elem.sw_impl_policy))
        if elem.trigger_period:
            self._write_multidimensional_time(elem.trigger_period, "TRIGGER-PERIOD")

    # Data type elements

    def _write_sw_addr_method(self, elem: ar_element.SwAddrMethod) -> None:
        """
        Writes complex type AR:SW-ADDR-METHOD
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwAddrMethod)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('SW-ADDR-METHOD', attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_addr_method_group(elem)
        self._leave_child()

    def _write_sw_addr_method_group(self, elem: ar_element.SwAddrMethod) -> None:
        """
        Writes group AR:SW-ADDR-METHOD
        """
        if elem.memory_allocation_keyword_policy:
            pass  # Not yet implemented
        if elem.options:
            pass  # Not yet implemented
        if elem.section_initialization_policy:
            pass  # Not yet implemented
        if elem.section_type:
            pass  # Not yet implemented

    def _write_sw_base_type(self, elem: ar_element.SwBaseType) -> None:
        """
        Writes complex type AR:SW-BASE-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwBaseType)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('SW-BASE-TYPE', attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_base_type(elem)
        self._leave_child()

    def _write_base_type(self, elem: ar_element.SwBaseType) -> None:
        """
        Writes groups AR:BASE-TYPE and AR:BASE-TYPE-DIRECT-DEFINITION
        """
        if elem.size is not None:
            self._add_content('BASE-TYPE-SIZE', str(elem.size))
        if elem.encoding is not None:
            self._add_content('BASE-TYPE-ENCODING', str(elem.encoding))
        if elem.alignment is not None:
            self._add_content('MEM-ALIGNMENT', str(elem.alignment))
        if elem.byte_order is not None:
            self._add_content(
                'BYTE-ORDER', ar_enum.enum_to_xml(elem.byte_order))
        if elem.native_declaration is not None:
            self._add_content('NATIVE-DECLARATION',
                              str(elem.native_declaration))

    def _write_sw_data_def_props(self, elem: ar_element.SwDataDefProps, tag: str) -> None:
        """
        Writes complex type AR:SW-DATA-DEF-PROPS
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.SwDataDefProps)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if len(elem) > 0:
                self._add_child("SW-DATA-DEF-PROPS-VARIANTS")
                for child_elem in iter(elem):
                    self._write_sw_data_def_props_conditional(child_elem)
                self._leave_child()
            self._leave_child()

    def _write_sw_data_def_props_conditional(self, elem: ar_element.SwDataDefPropsConditional) -> None:
        """
        Writes complex type AR:SW-DATA-DEF-PROPS-CONDITIONAL
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwDataDefPropsConditional)
        tag = 'SW-DATA-DEF-PROPS-CONDITIONAL'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sw_data_def_props_content(elem)
            self._leave_child()

    def _write_sw_data_def_props_content(self, elem: ar_element.SwDataDefPropsConditional) -> None:
        """
        Writes group AR:SW-DATA-DEF-PROPS-CONTENT
        """
        if elem.display_presentation is not None:
            self._add_content('DISPLAY-PRESENTATION',
                              ar_enum.enum_to_xml(elem.display_presentation))
        if elem.step_size is not None:
            self._add_content('STEP-SIZE', self._format_float(elem.step_size))
        if elem.annotations:
            self._write_annotations(elem.annotations)
        if elem.sw_addr_method_ref is not None:
            self._write_sw_addr_method_ref(elem.sw_addr_method_ref)
        if elem.alignment is not None:
            self._add_content('SW-ALIGNMENT', str(elem.alignment))
        if elem.base_type_ref is not None:
            self._write_sw_base_type_ref(elem.base_type_ref)
        if elem.bit_representation is not None:
            self._write_sw_bit_represenation(elem.bit_representation)
        if elem.calibration_access is not None:
            self._add_content('SW-CALIBRATION-ACCESS',
                              ar_enum.enum_to_xml(elem.calibration_access))
        if elem.text_props is not None:
            self._write_sw_text_props(elem.text_props)
        if elem.compu_method_ref is not None:
            self._write_compu_method_ref(elem.compu_method_ref)
        if elem.display_format is not None:
            self._add_content('DISPLAY-FORMAT', elem.display_format)
        if elem.data_constraint_ref is not None:
            self._write_data_constraint_ref(elem.data_constraint_ref)
        if elem.impl_data_type_ref is not None:
            self._write_impl_data_type_ref(elem.impl_data_type_ref, "IMPLEMENTATION-DATA-TYPE-REF")
        if elem.impl_policy is not None:
            self._add_content('SW-IMPL-POLICY',
                              ar_enum.enum_to_xml(elem.impl_policy))
        if elem.additional_native_type_qualifier is not None:
            self._add_content('ADDITIONAL-NATIVE-TYPE-QUALIFIER',
                              str(elem.additional_native_type_qualifier))
        if elem.intended_resolution is not None:
            self._add_content('SW-INTENDED-RESOLUTION',
                              self._format_number(elem.intended_resolution))
        if elem.interpolation_method is not None:
            self._add_content('SW-INTERPOLATION-METHOD', str(elem.interpolation_method))
        if elem.is_virtual is not None:
            self._add_content('SW-IS-VIRTUAL', self._format_boolean(elem.is_virtual))
        if elem.ptr_target_props is not None:
            self._write_sw_pointer_target_props(elem.ptr_target_props)
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)

    def _write_sw_bit_represenation(self, elem: ar_element.SwBitRepresentation) -> None:
        """
        Writes AR:SW-BIT-REPRESENTATION
        """
        tag = 'SW-BIT-REPRESENTATION'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.position is not None:
                self._add_content('BIT-POSITION', str(elem.position))
            if elem.num_bits is not None:
                self._add_content('NUMBER-OF-BITS', str(elem.num_bits))
            self._leave_child()

    def _write_sw_text_props(self, elem: ar_element.SwTextProps) -> None:
        """
        Writes AR:SW-TEXT-PROPS
        """
        tag = 'SW-TEXT-PROPS'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.array_size_semantics is not None:
                self._add_content('ARRAY-SIZE-SEMANTICS', ar_enum.enum_to_xml(elem.array_size_semantics))
            if elem.max_text_size is not None:
                self._add_content('SW-MAX-TEXT-SIZE', str(elem.max_text_size))
            if elem.base_type_ref is not None:
                self._write_sw_base_type_ref(elem.base_type_ref)
            if elem.fill_char is not None:
                self._add_content('SW-FILL-CHARACTER', str(elem.fill_char))
            self._leave_child()

    def _write_sw_pointer_target_props(self, elem: ar_element.SwPointerTargetProps) -> None:
        """
        Writes AR:SW-POINTER-TARGET-PROPS
        """
        tag = 'SW-POINTER-TARGET-PROPS'
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.target_category is not None:
                self._add_content("TARGET-CATEGORY", str(elem.target_category))
            if elem.sw_data_def_props is not None:
                self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")
            if elem.function_ptr_signature_ref is not None:
                self._write_function_ptr_signature_ref(elem.function_ptr_signature_ref)
            self._leave_child()

    def _write_symbol_props(self, elem: ar_element.SymbolProps, tag: str) -> None:
        """
        Writes complex type AR:SYMBOL-PROPS
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.SymbolProps)
        self._add_child(tag)
        self._write_referrable(elem)
        self._write_implementation_props(elem)
        self._leave_child()

    def _write_implementation_props(self, elem: ar_element.ImplementationProps) -> None:
        """
        Writes group AR:IMPLEMENTATION-PROPS
        """
        if elem.symbol is not None:
            self._add_content("SYMBOL", str(elem.symbol))

    def _write_implementation_data_type_element(self, elem: ar_element.ImplementationDataTypeElement) -> None:
        """
        Writes complex type AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ImplementationDataTypeElement)
        self._add_child("IMPLEMENTATION-DATA-TYPE-ELEMENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self.__write_implementation_data_type_element_group(elem)
        self._leave_child()

    def __write_implementation_data_type_element_group(self, elem: ar_element.ImplementationDataTypeElement) -> None:
        """
        Writes group AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
        """
        if elem.array_impl_policy is not None:
            self._add_content("ARRAY-IMPL-POLICY", ar_enum.enum_to_xml(elem.array_impl_policy))
        if elem.array_size is not None:
            self._add_content("ARRAY-SIZE", str(elem.array_size))
        if elem.array_size_handling is not None:
            self._add_content("ARRAY-SIZE-HANDLING", ar_enum.enum_to_xml(elem.array_size_handling))
        if elem.array_size_semantics is not None:
            self._add_content("ARRAY-SIZE-SEMANTICS", ar_enum.enum_to_xml(elem.array_size_semantics))
        if elem.is_optional is not None:
            self._add_content("IS-OPTIONAL", self._format_boolean(elem.is_optional))
        if len(elem.sub_elements) > 0:
            self._add_child("SUB-ELEMENTS")
            for sub_elem in elem.sub_elements:
                self._write_implementation_data_type_element(sub_elem)
            self._leave_child()
        if elem.sw_data_def_props is not None:
            self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")

    def _write_implementation_data_type(self, elem: ar_element.ImplementationDataType) -> None:
        """
        Writes complex type AR:IMPLEMENTATION-DATA-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ImplementationDataType)
        self._add_child("IMPLEMENTATION-DATA-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_autosar_data_type(elem)
        self._write_implementation_data_type_group(elem)
        self._leave_child()

    def _write_implementation_data_type_group(self, elem: ar_element.ImplementationDataType) -> None:
        """
        Writes group AR:IMPLEMENTATION-DATA-TYPE
        """
        if elem.dynamic_array_size_profile is not None:
            self._add_content("DYNAMIC-ARRAY-SIZE-PROFILE", str(elem.dynamic_array_size_profile))
        if elem.is_struct_with_optional_element is not None:
            self._add_content("IS-STRUCT-WITH-OPTIONAL-ELEMENT",
                              self._format_boolean(elem.is_struct_with_optional_element))
        if len(elem.sub_elements) > 0:
            self._add_child("SUB-ELEMENTS")
            for sub_elem in elem.sub_elements:
                self._write_implementation_data_type_element(sub_elem)
            self._leave_child()
        if elem.symbol_props is not None:
            self._write_symbol_props(elem.symbol_props, "SYMBOL-PROPS")
        if elem.type_emitter is not None:
            self._add_content("TYPE-EMITTER", str(elem.type_emitter))

    def _write_autosar_data_type(self, elem: ar_element.AutosarDataType) -> None:
        """
        Writes group AR:AUTOSAR-DATA-TYPE
        """
        if elem.sw_data_def_props is not None:
            self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")

    def _write_data_prototype(self, elem: ar_element.DataPrototype) -> None:
        """
        Writes group AR:DATA-PROTOTYPE
        """
        if elem.sw_data_def_props is not None:
            self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")

    def _write_application_primitive_data_type(self, elem: ar_element.ApplicationPrimitiveDataType) -> None:
        """
        Writes complex type AR:APPLICATION-PRIMITIVE-DATA-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationPrimitiveDataType)
        self._add_child("APPLICATION-PRIMITIVE-DATA-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_autosar_data_type(elem)
        self._leave_child()

    def _write_application_composite_element_data_prototype(
            self,
            elem: ar_element.ApplicationCompositeElementDataPrototype) -> None:
        """
        Writes group AR:APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE
        """
        assert isinstance(elem, ar_element.ApplicationCompositeElementDataPrototype)
        if elem.type_ref is not None:
            self._write_application_data_type_ref(elem.type_ref, 'TYPE-TREF')

    def _write_application_array_element(self, elem: ar_element.ApplicationArrayElement) -> None:
        """
        Writes complex type AR:APPLICATION-ARRAY-ELEMENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationArrayElement)
        self._add_child("ELEMENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_data_prototype(elem)
        self._write_application_composite_element_data_prototype(elem)
        self._write_application_array_element_group(elem)
        self._leave_child()

    def _write_application_array_element_group(self, elem: ar_element.ApplicationArrayElement) -> None:
        """
        Writes group AR:APPLICATION-ARRAY-ELEMENT
        """
        if elem.array_size_handling is not None:
            self._add_content("ARRAY-SIZE-HANDLING", ar_enum.enum_to_xml(elem.array_size_handling))
        if elem.array_size_semantics is not None:
            self._add_content("ARRAY-SIZE-SEMANTICS", ar_enum.enum_to_xml(elem.array_size_semantics))
        if elem.index_data_type_ref is not None:
            self._write_index_data_type_ref(elem.index_data_type_ref)
        if elem.max_number_of_elements is not None:
            self._add_content("MAX-NUMBER-OF-ELEMENTS", str(elem.max_number_of_elements))

    def _write_application_record_element(self, elem: ar_element.ApplicationRecordElement) -> None:
        """
        Writes complex type AR:APPLICATION-RECORD-ELEMENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationRecordElement)
        self._add_child("APPLICATION-RECORD-ELEMENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_data_prototype(elem)
        self._write_application_composite_element_data_prototype(elem)
        self._write_application_record_element_group(elem)
        self._leave_child()

    def _write_application_record_element_group(self, elem: ar_element.ApplicationRecordElement) -> None:
        """
        Writes group AR:APPLICATION-RECORD-ELEMENT
        """
        if elem.is_optional is not None:
            self._add_content('IS-OPTIONAL', self._format_boolean(elem.is_optional))

    def _write_application_array_data_type(self, elem: ar_element.ApplicationArrayDataType) -> None:
        """
        Writes complex type AR:APPLICATION-ARRAY-DATA-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationArrayDataType)
        self._add_child("APPLICATION-ARRAY-DATA-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_autosar_data_type(elem)
        self._write_application_array_data_type_group(elem)
        self._leave_child()

    def _write_application_array_data_type_group(self, elem: ar_element.ApplicationArrayDataType) -> None:
        """
        Writes group AR:APPLICATION-ARRAY-DATA-TYPE
        """
        if elem.dynamic_array_size_profile is not None:
            self._add_content("DYNAMIC-ARRAY-SIZE-PROFILE", str(elem.dynamic_array_size_profile))
        if elem.element is not None:
            self._write_application_array_element(elem.element)

    def _write_application_record_data_type(self, elem: ar_element.ApplicationRecordDataType) -> None:
        """
        Writes complex type AR:APPLICATION-RECORD-DATA-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationRecordDataType)
        self._add_child("APPLICATION-RECORD-DATA-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_autosar_data_type(elem)
        self._write_application_record_data_type_group(elem)
        self._leave_child()

    def _write_application_record_data_type_group(self, elem: ar_element.ApplicationRecordDataType) -> None:
        """
        Writes group AR:APPLICATION-RECORD-DATA-TYPE
        """
        if len(elem.elements) > 0:
            self._add_child("ELEMENTS")
            for child_elem in elem.elements:
                self._write_application_record_element(child_elem)
            self._leave_child()

    def _write_data_type_map(self, elem: ar_element.DataTypeMap) -> None:
        """
        Writes complex type AR:DATA-TYPE-MAP
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DataTypeMap)
        self._add_child("DATA-TYPE-MAP")
        if elem.appl_data_type_ref is not None:
            self._write_application_data_type_ref(elem.appl_data_type_ref, "APPLICATION-DATA-TYPE-REF")
        if elem.impl_data_type_ref is not None:
            self._write_impl_data_type_ref(elem.impl_data_type_ref, "IMPLEMENTATION-DATA-TYPE-REF")
        self._leave_child()

    def _write_constant_specification_mapping(self, elem: ar_element.ConstantSpecificationMapping) -> None:
        """
        Writes complex type AR:CONSTANT-SPECIFICATION-MAPPING
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ConstantSpecificationMapping)
        tag = "CONSTANT-SPECIFICATION-MAPPING"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.appl_constant_ref is not None:
                self._write_constant_ref(elem.appl_constant_ref, "APPL-CONSTANT-REF")
            if elem.impl_constant_ref is not None:
                self._write_constant_ref(elem.impl_constant_ref, "IMPL-CONSTANT-REF")
            self._leave_child()

    def _write_constant_specification_mapping_set(self, elem: ar_element.ConstantSpecificationMappingSet) -> None:
        """
        Writes complex type AR:CONSTANT-SPECIFICATION-MAPPING-SET
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ConstantSpecificationMappingSet)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child("CONSTANT-SPECIFICATION-MAPPING-SET", attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if len(elem.mappings) > 0:
            self._add_child("MAPPINGS")
            for child_elem in elem.mappings:
                self._write_constant_specification_mapping(child_elem)
            self._leave_child()
        self._leave_child()

    def _write_data_type_mapping_set(self, elem: ar_element.DataTypeMappingSet) -> None:
        """
        Writes complex type AR:DATA-TYPE-MAPPING-SET
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DataTypeMappingSet)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child("DATA-TYPE-MAPPING-SET", attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if len(elem.data_type_maps) > 0:
            self._add_child("DATA-TYPE-MAPS")
            for child_elem in elem.data_type_maps:
                self._write_data_type_map(child_elem)
            self._leave_child()
        if len(elem.mode_request_type_maps) > 0:
            self._add_child("MODE-REQUEST-TYPE-MAPS")
            for child_elem in elem.mode_request_type_maps:
                self._write_mode_request_type_map(child_elem)
            self._leave_child()
        self._leave_child()

    def _write_value_list(self, elem: ar_element.ValueList) -> None:
        """
        Writes complex type AR:VALUE-LIST
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ValueList)
        tag = "SW-ARRAYSIZE"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_list_group(elem)
            self._leave_child()

    def _write_value_list_group(self, elem: ar_element.SwValues) -> None:
        """
        Writes group AR:VALUE-LIST
        """
        for value in elem.values:
            content = self._format_number(value)
            self._add_content("V", content)

    def _write_autosar_data_prototype(self, elem: ar_element.AutosarDataPrototype) -> None:
        """
        Writes group AR:AUTOSAR-DATA-PROTOTYPE
        """
        if elem.type_ref is not None:
            self._write_autosar_data_type_ref(elem.type_ref, "TYPE-TREF")

    def _write_variable_data_prototype(self, elem: ar_element.VariableDataPrototype, tag: str) -> None:
        """
        Writes complex type AR:VARIABLE-DATA-PROTOTYPE
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.VariableDataPrototype)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child(tag, attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_data_prototype(elem)
        self._write_autosar_data_prototype(elem)
        self._write_variable_data_prototype_group(elem)
        self._leave_child()

    def _write_variable_data_prototype_group(self, elem: ar_element.VariableDataPrototype) -> None:
        """
        Writes group AR:VARIABLE-DATA-PROTOTYPE
        """
        if elem.init_value is not None:
            self._add_child("INIT-VALUE")
            self._write_value_specification_element(elem.init_value)
            self._leave_child()

    def _write_parameter_data_prototype(self, elem: ar_element.ParameterDataPrototype, tag: str) -> None:
        """
        Writes complex type AR:PARAMETER-DATA-PROTOTYPE
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.ParameterDataPrototype)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child(tag, attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_data_prototype(elem)
        self._write_autosar_data_prototype(elem)
        self._write_variable_data_prototype_group(elem)
        self._leave_child()

    def _write_parameter_data_prototype_group(self, elem: ar_element.ParameterDataPrototype) -> None:
        """
        Writes group AR:PARAMETER-DATA-PROTOTYPE
        """
        if elem.init_value is not None:
            self._add_child("INIT-VALUE")
            self._write_value_specification_element(elem.init_value)
            self._leave_child()

    def _write_argument_data_prototype(self, elem: ar_element.ArgumentDataPrototype) -> None:
        """
        Writes complex type AR:ARGUMENT-DATA-PROTOTYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ArgumentDataPrototype)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child("ARGUMENT-DATA-PROTOTYPE", attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_data_prototype(elem)
        self._write_autosar_data_prototype(elem)
        self._write_argument_data_prototype_group(elem)
        self._leave_child()

    def _write_argument_data_prototype_group(self, elem: ar_element.ArgumentDataPrototype) -> None:
        """
        Writes group AR:ARGUMENT-DATA-PROTOTYPE
        """
        if elem.direction is not None:
            self._add_content("DIRECTION", ar_enum.enum_to_xml(elem.direction))
        if elem.server_arg_impl_policy is not None:
            self._add_content("SERVER-ARGUMENT-IMPL-POLICY", ar_enum.enum_to_xml(elem.server_arg_impl_policy))

    def _write_mode_request_type_map(self, elem: ar_element.ModeRequestTypeMap) -> None:
        """
        Writes complex type AR:MODE-REQUEST-TYPE-MAP
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeRequestTypeMap)
        tag = "MODE-REQUEST-TYPE-MAP"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.implementation_data_type is not None:
                self._write_impl_data_type_ref(elem.implementation_data_type, "IMPLEMENTATION-DATA-TYPE-REF")
            if elem.mode_group is not None:
                self._write_mode_declaration_group_ref(elem.mode_group, "MODE-GROUP-REF")
            self._leave_child()

# --- Reference Elements

    def _collect_base_ref_attr(self,
                               elem: ar_element.BaseRef,
                               attr: TupleList) -> None:
        attr.append(('DEST', ar_enum.enum_to_xml(elem.dest)))

    def _write_ref_content(self, elem: ar_element.BaseRef, tag: str):
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_compu_method_ref(self, elem: ar_element.CompuMethodRef) -> None:
        """
        Writes complex type AR:COMPU-METHOD-REF
        Multi-tagged: False

        Note: The name of the complex-type is anonymous in the XML schema.
        """
        assert isinstance(elem, ar_element.CompuMethodRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('COMPU-METHOD-REF', elem.value, attr)

    def _write_data_constraint_ref(self, elem: ar_element.DataConstraintRef) -> None:
        """
        Writes complex type AR:DATA-CONSTR-REF
        Multi-tagged: False

        Note: The name of the complex-type is anonymous in the XML schema.
        """
        assert isinstance(elem, ar_element.DataConstraintRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('DATA-CONSTR-REF', elem.value, attr)

    def _write_function_ptr_signature_ref(self, elem: ar_element.FunctionPtrSignatureRef) -> None:
        """
        Writes complex type AR:FunctionPtrSignatureRef
        Multi-tagged: False

        Note: The name of the complex-type is anonymous in the XML schema.
        """
        assert isinstance(elem, ar_element.FunctionPtrSignatureRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('FUNCTION-POINTER-SIGNATURE-REF', elem.value, attr)

    def _write_impl_data_type_ref(self, elem: ar_element.ImplementationDataTypeRef, tag: str) -> None:
        """
        Writes reference to AR:IMPLEMENTATION-DATA-TYPE-REF

        Note: The name of the complex-type is anonymous in the XML schema.
        """
        assert isinstance(elem, ar_element.ImplementationDataTypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_sw_base_type_ref(self, elem: ar_element.SwBaseTypeRef) -> None:
        """
        Writes complex type AR:SW-BASE-TYPE-REF
        Multi-tagged: False

        Note: The name of the complex-type is anonymous in the XML schema.
        """
        assert isinstance(elem, ar_element.SwBaseTypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('BASE-TYPE-REF', elem.value, attr)

    def _write_sw_addr_method_ref(self, elem: ar_element.SwAddrMethodRef) -> None:
        """
        Writes reference to AR:SW-ADDR-METHOD--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.SwAddrMethodRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('SW-ADDR-METHOD-REF', elem.value, attr)

    def _write_unit_ref(self, elem: ar_element.UnitRef) -> None:
        """
        Writes complex type AR:UNIT-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.UnitRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('UNIT-REF', elem.value, attr)

    def _write_physical_dimension_ref(self, elem: ar_element.PhysicalDimensionRef) -> None:
        """
        Writes PHYSICAL-DIMENSION-REF
        """
        assert isinstance(elem, ar_element.PhysicalDimensionRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('PHYSICAL-DIMENSION-REF', elem.value, attr)

    def _write_index_data_type_ref(self, elem: ar_element.IndexDataTypeRef) -> None:
        """
        Writes reference to IndexDataType
        """
        assert isinstance(elem, ar_element.IndexDataTypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content('INDEX-DATA-TYPE-REF', elem.value, attr)

    def _write_application_data_type_ref(self, elem: ar_element.ApplicationDataTypeRef, tag: str) -> None:
        """
        Writes reference to ApplicationDataType
        """
        assert isinstance(elem, ar_element.ApplicationDataTypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_constant_ref(self, elem: ar_element.ApplicationDataTypeRef, tag: str) -> None:
        """
        Writes reference to ConstantSpecification

        Don't confuse this with the ConstantReference class.
        """
        assert isinstance(elem, ar_element.ConstantRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_autosar_data_type_ref(self, elem: ar_element.AutosarDataTypeRef, tag: str) -> None:
        """
        Writes reference to AutosarDataTypeRef
        """
        assert isinstance(elem, ar_element.AutosarDataTypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_variable_data_prototype_ref(self, elem: ar_element.VariableDataPrototypeRef, tag: str) -> None:
        """
        Write reference to VariableDataPrototype
        """
        assert isinstance(elem, ar_element.VariableDataPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_parameter_data_prototype_ref(self, elem: ar_element.ParameterDataPrototypeRef, tag: str) -> None:
        """
        Write reference ParameterDataPrototype
        """
        assert isinstance(elem, ar_element.ParameterDataPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_application_error_ref(self, elem: ar_element.ApplicationErrorRef, tag: str) -> None:
        """
        Writes reference to ApplicationError
        """
        assert isinstance(elem, ar_element.ApplicationErrorRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_mode_declaration_ref(self, elem: ar_element.ModeDeclarationRef, tag: str) -> None:
        """
        Writes reference to ModeDeclaration
        """
        assert isinstance(elem, ar_element.ModeDeclarationRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_mode_declaration_group_ref(self, elem: ar_element.ModeDeclarationGroupRef, tag: str) -> None:
        """
        Writes reference to ModeDeclaration
        """
        assert isinstance(elem, ar_element.ModeDeclarationGroupRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_mode_declaration_group_prototype_ref(self,
                                                    elem: ar_element.ModeDeclarationGroupPrototypeRef,
                                                    tag: str) -> None:
        """
        Writes reference to ModeDeclarationGroupPrototype
        """
        assert isinstance(elem, ar_element.ModeDeclarationGroupPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_autosar_data_prototype_ref(self,
                                          elem: ar_element.AutosarDataPrototypeRef,
                                          tag: str) -> None:
        """
        Writes reference to elements that derives from AutosarDataPrototype
        """
        assert isinstance(elem, ar_element.AutosarDataPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_e2e_profile_compatibility_props_ref(self,
                                                   elem: ar_element.E2EProfileCompatibilityPropsRef
                                                   ) -> None:
        """
        Writes reference to E2EProfileCompatibilityProps
        """
        assert isinstance(elem, ar_element.E2EProfileCompatibilityPropsRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content("E-2-E-PROFILE-COMPATIBILITY-PROPS-REF", elem.value, attr)

    def _write_client_server_operation_ref(self,
                                           elem: ar_element.ClientServerOperationRef,
                                           tag: str) -> None:
        """
        Writes reference to ClientServerOperation
        """
        assert isinstance(elem, ar_element.ClientServerOperationRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_port_prototype_ref(self,
                                  elem: ar_element.PortPrototypeRef,
                                  tag: str) -> None:
        """
        Writes references to AR:PORT-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.PortPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_abstract_impl_data_type_element_ref(self,
                                                   elem: ar_element.AbstractImplementationDataTypeElementRef,
                                                   tag: str) -> None:
        """
        Writes references to AR:VARIABLE-DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.AbstractImplementationDataTypeElementRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_appl_composite_element_data_proto_ref(self,
                                                     elem: ar_element.ApplicationCompositeElementDataPrototypeRef,
                                                     tag: str) -> None:
        """
        Writes references to APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ApplicationCompositeElementDataPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_data_prototype_ref(self,
                                  elem: ar_element.DataPrototypeRef,
                                  tag: str) -> None:
        """
        Writes references to DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.DataPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_port_interface_ref(self,
                                  elem: ar_element.PortInterfaceRef,
                                  tag: str) -> None:
        """
        Writes references to PORT-INTERFACE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.PortInterfaceRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_sw_component_type_ref(self,
                                     elem: ar_element.SwComponentTypeRef,
                                     tag: str) -> None:
        """
        Writes references to SW-COMPONENT-TYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.SwComponentTypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_sw_component_prototype_ref(self,
                                          elem: ar_element.SwComponentPrototypeRef,
                                          tag: str) -> None:
        """
        Writes references to SW-COMPONENT-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.SwComponentPrototypeRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_exclusive_area_ref(self,
                                  elem: ar_element.ExclusiveAreaRef,
                                  tag: str) -> None:
        """
        Writes references to EXCLUSIVE-AREA--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ExclusiveAreaRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_exclusive_area_nesting_order_ref(self,
                                                elem: ar_element.ExclusiveAreaNestingOrderRef,
                                                tag: str) -> None:
        """
        Writes references to EXCLUSIVE-AREA-NESTING-ORDER--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ExclusiveAreaNestingOrderRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_abstract_required_port_prototype_ref(self,
                                                    elem: ar_element.AbstractRequiredPortPrototypeRef,
                                                    tag: str) -> None:
        """
        Writes references to AR:ABSTRACT-REQUIRED-PORT'-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.AbstractRequiredPortPrototypeRef)
        self._write_ref_content(elem, tag)

    def _write_abstract_provided_port_prototype_ref(self,
                                                    elem: ar_element.AbstractProvidedPortPrototypeRef,
                                                    tag: str) -> None:
        """
        Writes references to AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.AbstractProvidedPortPrototypeRef)
        self._write_ref_content(elem, tag)

    def _write_swc_internal_behavior_ref(self,
                                         elem: ar_element.SwcInternalBehaviorRef,
                                         tag: str) -> None:
        """
        Writes references to SWC-INTERNAL-BEHAVIOR--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.SwcInternalBehaviorRef)
        attr: TupleList = []
        self._collect_base_ref_attr(elem, attr)
        self._add_content(tag, elem.value, attr)

    def _write_runnable_entity_ref(self,
                                   elem: ar_element.RunnableEntityRef,
                                   tag: str) -> None:
        """
        Writes references to RUNNABLE-ENTITY--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.RunnableEntityRef)
        self._write_ref_content(elem, tag)

    def _write_variable_access_ref(self,
                                   elem: ar_element.VariableAccessRef,
                                   tag: str) -> None:
        """
        Writes references to AR:VARIABLE-ACCESS--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.VariableAccessRef)
        self._write_ref_content(elem, tag)

    def _write_mode_switch_point_ref(self,
                                     elem: ar_element.ModeSwitchPointRef
                                     ) -> None:
        """
        Writes references to AR:MODE-SWITCH-POINT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ModeSwitchPointRef)
        self._write_ref_content(elem, "EVENT-SOURCE-REF")

    def _write_async_server_call_point_ref(self,
                                           elem: ar_element.AsynchronousServerCallPointRef
                                           ) -> None:
        """
        Writes references to AR:ASYNCHRONOUS-SERVER-CALL-POINT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.AsynchronousServerCallPointRef)
        self._write_ref_content(elem, "ASYNCHRONOUS-SERVER-CALL-POINT-REF")

    def _write_async_server_call_result_point_ref(self,
                                                  elem: ar_element.AsynchronousServerCallResultPointRef
                                                  ) -> None:
        """
        Writes references to AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.AsynchronousServerCallResultPointRef)
        self._write_ref_content(elem, "EVENT-SOURCE-REF")

    def _write_trigger_ref(self,
                           elem: ar_element.TriggerRef,
                           tag: str) -> None:
        """
        Writes references to AR:TRIGGER--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.TriggerRef)
        self._write_ref_content(elem, tag)

    def _write_internal_triggering_point_ref(self,
                                             elem: ar_element.InternalTriggeringPointRef
                                             ) -> None:
        """
        Writes references to AR:INTERNAL-TRIGGERING-POINT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.InternalTriggeringPointRef)
        self._write_ref_content(elem, "EVENT-SOURCE-REF")

    def _write_rte_event_ref(self,
                             elem: ar_element.InternalTriggeringPointRef,
                             tag: str) -> None:
        """
        Writes references to AR:RTE-EVENT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.RteEventRef)
        self._write_ref_content(elem, tag)

    def _write_data_type_mapping_set_ref(self,
                                         elem: ar_element.DataTypeMappingSetRef,
                                         tag: str) -> None:
        """
        Writes references to AR:DATA-TYPE-MAPPING-SET--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.DataTypeMappingSetRef)
        self._write_ref_content(elem, tag)

    def _write_constant_specification_mapping_set_ref(self,
                                                      elem: ar_element.ConstantSpecificationMappingSetRef,
                                                      tag: str = "CONSTANT-VALUE-MAPPING-REF") -> None:
        """
        Writes references to AR:CONSTANT-SPECIFICATION-MAPPING-SET--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ConstantSpecificationMappingSetRef)
        self._write_ref_content(elem, tag)

    def _write_argument_data_prototype_ref(self, elem: ar_element.ArgumentDataPrototypeRef, tag: str) -> None:
        """
        Writes references to AR:ARGUMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ArgumentDataPrototypeRef)
        self._write_ref_content(elem, tag)

    def _write_application_array_element_ref(self, elem: ar_element.ApplicationArrayElementRef) -> None:
        """
        Writes references to AR:APPLICATION-ARRAY-ELEMENT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ApplicationArrayElementRef)
        self._write_ref_content(elem, "APPLICATION-ARRAY-ELEMENT-REF")

    def _write_application_record_element_ref(self, elem: ar_element.ApplicationRecordElementRef, tag: str) -> None:
        """
        Writes references to AR:APPLICATION-RECORD-ELEMENT--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.ApplicationRecordElementRef)
        self._write_ref_content(elem, tag)

    def _write_diagnostic_event_needs_ref(self, elem: ar_element.DiagnosticEventNeedsRef, tag: str) -> None:
        """
        Writes references to AR:DIAGNOSTIC-EVENT-NEEDS--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.DiagnosticEventNeedsRef)
        self._write_ref_content(elem, tag)

    def _write_diagnostic_value_needs_ref(self, elem: ar_element.DiagnosticValueNeedsRef, tag: str) -> None:
        """
        Writes references to AR:DIAGNOSTIC-VALUE-NEEDS--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.DiagnosticValueNeedsRef)
        self._write_ref_content(elem, tag)

    def _write_function_inhibition_needs_ref(self, elem: ar_element.FunctionInhibitionNeedsRef, tag: str) -> None:
        """
        Writes references to AR:FUNCTION-INHIBITION-NEEDS--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.FunctionInhibitionNeedsRef)
        self._write_ref_content(elem, tag)

    def _write_supervised_entity_checkpoint_needs_ref(
            self,
            elem: ar_element.SupervisedEntityCheckpointNeedsRef,
            tag: str) -> None:
        """
        Writes references to AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.SupervisedEntityCheckpointNeedsRef)
        self._write_ref_content(elem, tag)

    def _write_port_group_ref(self, elem: ar_element.PortGroupRef, tag: str) -> None:
        """
        Writes references to AR:PORT-GROUP--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.PortGroupRef)
        self._write_ref_content(elem, tag)

    def _write_per_instance_memory_ref(self, elem: ar_element.PerInstanceMemoryRef, tag: str) -> None:
        """
        Writes references to AR:PER-INSTANCE-MEMORY--SUBTYPES-ENUM
        """
        assert isinstance(elem, ar_element.PerInstanceMemoryRef)
        self._write_ref_content(elem, tag)

# -- Constant and value specifications

    def _write_text_value_specification(self, elem: ar_element.TextValueSpecification) -> None:
        """
        Writes AR:TEXT-VALUE-SPECIFICATION
        """
        assert isinstance(elem, ar_element.TextValueSpecification)
        tag = "TEXT-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            if elem.value is not None:
                self._add_content("VALUE", str(elem.value))
            self._leave_child()

    def _write_numerical_value_specification(self, elem: ar_element.NumericalValueSpecification) -> None:
        """
        Writes AR:NUMERICAL-VALUE-SPECIFICATION
        """
        assert isinstance(elem, ar_element.NumericalValueSpecification)
        tag = "NUMERICAL-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            if elem.value is not None:
                self._add_content("VALUE", self._format_number(elem.value))
            self._leave_child()

    def _write_not_available_value_specification(self, elem: ar_element.NotAvailableValueSpecification) -> None:
        """
        Writes AR:NOT-AVAILABLE-VALUE-SPECIFICATION
        """
        assert isinstance(elem, ar_element.NotAvailableValueSpecification)
        tag = "NOT-AVAILABLE-VALUE-SPECIFICATION"
        if elem.is_empty_with_ignore({"default_pattern_format"}):
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            if elem.default_pattern is not None:
                self._add_content("DEFAULT-PATTERN", str(elem.default_pattern))  # TODO support numerical formats
            self._leave_child()

    def _write_array_value_specification(self, elem: ar_element.ArrayValueSpecification) -> None:
        """
        Writes complex type AR:ARRAY-VALUE-SPECIFICATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ArrayValueSpecification)
        tag = "ARRAY-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_array_value_specification_group(elem)
            self._leave_child()

    def _write_array_value_specification_group(self, elem: ar_element.ArrayValueSpecification) -> None:
        """
        Writes group AR:ARRAY-VALUE-SPECIFICATION
        """
        if elem.elements:
            self._add_child("ELEMENTS")
            for child_element in elem.elements:
                self._write_value_specification_element(child_element)
            self._leave_child()

    def _write_record_value_specification(self, elem: ar_element.RecordValueSpecification) -> None:
        """
        Writes complex type AR:RECORD-VALUE-SPECIFICATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RecordValueSpecification)
        tag = "RECORD-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_record_value_specification_group(elem)
            self._leave_child()

    def _write_record_value_specification_group(self, elem: ar_element.RecordValueSpecification) -> None:
        """
        Writes group AR:RECORD-VALUE-SPECIFICATION
        """
        if elem.fields:
            self._add_child("FIELDS")
            for field in elem.fields:
                self._write_value_specification_element(field)
            self._leave_child()

    def _write_application_value_specification(self, elem: ar_element.ApplicationValueSpecification) -> None:
        """
        Writes complex type AR:APPLICATION-VALUE-SPECIFICATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationValueSpecification)
        tag = "APPLICATION-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_application_specification_group(elem)
            self._leave_child()

    def _write_application_specification_group(self, elem: ar_element.ApplicationValueSpecification) -> None:
        """
        Writes group AR:APPLICATION-VALUE-SPECIFICATION
        """
        if elem.category is not None:
            self._add_content("CATEGORY", str(elem.category))
        if elem.sw_axis_conts:
            self._add_child("SW-AXIS-CONTS")
            for child in elem.sw_axis_conts:
                self._write_sw_axis_cont(child)
            self._leave_child()
        if elem.sw_value_cont is not None:
            self._write_sw_value_cont(elem.sw_value_cont)

    def _write_value_specification_group(self, elem: ar_element.ValueSpecification) -> None:
        """
        Writes group AR:VALUE-SPECIFICATION
        """
        if elem.label is not None:
            self._add_content("SHORT-LABEL", str(elem.label))

    def _write_value_specification_element(self, elem: ar_element.ValueSpecificationElement) -> None:
        """
        Switched writer for value specification elements
        """
        class_name = elem.__class__.__name__
        write_method = self.switcher_value_specification.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for class {class_name}")

    def _write_constant_specification(self, elem: ar_element.ConstantSpecification) -> None:
        """
        Writes complex type AR:CONSTANT-SPECIFICATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ConstantSpecification)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child('CONSTANT-SPECIFICATION', attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_constant_specification_group(elem)
        self._leave_child()

    def _write_constant_specification_group(self, elem: ar_element.ConstantSpecification) -> None:
        """
        Writes group AR:CONSTANT-SPECIFICATION
        """
        if elem.value is not None:
            self._add_child("VALUE-SPEC")
            self._write_value_specification_element(elem.value)
            self._leave_child()

    def _write_constant_reference(self, elem: ar_element.ConstantReference) -> None:
        """
        Writes complex type AR:CONSTANT-REFERENCE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ConstantReference)
        tag = "CONSTANT-REFERENCE"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            if elem.constant_ref is not None:
                self._write_constant_ref(elem.constant_ref, "CONSTANT-REF")
            self._leave_child()

    def _write_reference_value_specification(self, elem: ar_element.ReferenceValueSpecification) -> None:
        """
        Writes complex type AR:REFERENCE-VALUE-SPECIFICATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ReferenceValueSpecification)
        tag = "REFERENCE-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_reference_value_specification_group(elem)
            self._leave_child()

    def _write_reference_value_specification_group(self, elem: ar_element.ReferenceValueSpecification) -> None:
        """
        Writes group AR:REFERENCE-VALUE-SPECIFICATION
        """
        if elem.reference_value is not None:
            self._write_data_prototype_ref(elem.reference_value, "REFERENCE-VALUE-REF")

    def _write_numerical_rule_based_value_specification(self,
                                                        elem: ar_element.NumericalRuleBasedValueSpecification) -> None:
        """
        Writes complex type AR:NUMERICAL-RULE-BASED-VALUE-SPECIFICATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.NumericalRuleBasedValueSpecification)
        tag = "NUMERICAL-RULE-BASED-VALUE-SPECIFICATION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_numerical_rule_based_value_specification_group(elem)
            self._leave_child()

    def _write_numerical_rule_based_value_specification_group(self,
                                                              elem: ar_element.NumericalRuleBasedValueSpecification
                                                              ) -> None:
        """
        Writes group AR:NUMERICAL-RULE-BASED-VALUE-SPECIFICATION
        """
        if elem.rule_based_values is not None:
            self._write_rule_based_value_specification(elem.rule_based_values, "RULE-BASED-VALUES")

    def _write_application_rule_based_value_specification(self,
                                                          elem: ar_element.ApplicationRuleBasedValueSpecification,
                                                          tag: str = "APPLICATION-RULE-BASED-VALUE-SPECIFICATION"
                                                          ) -> None:
        """
        Writes complex type AR:APPLICATION-RULE-BASED-VALUE-SPECIFICATION
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.ApplicationRuleBasedValueSpecification)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_application_rule_based_value_specification_group(elem)
            self._leave_child()

    def _write_application_rule_based_value_specification_group(self,
                                                                elem: ar_element.ApplicationRuleBasedValueSpecification
                                                                ) -> None:
        """
        Writes group AR:APPLICATION-RULE-BASED-VALUE-SPECIFICATION
        """
        if elem.category is not None:
            self._add_content("CATEGORY", str(elem.category))
        if len(elem.sw_axis_conts) > 0:
            self._add_child("SW-AXIS-CONTS")
            for child in elem.sw_axis_conts:
                self._write_rule_based_axis_cont(child)
            self._leave_child()
        if elem.sw_value_cont is not None:
            self._write_rule_based_value_cont(elem.sw_value_cont, "SW-VALUE-CONT")

    def _write_composite_rule_based_value_specification(self,
                                                        elem: ar_element.CompositeRuleBasedValueSpecification,
                                                        tag: str = "COMPOSITE-RULE-BASED-VALUE-SPECIFICATION"
                                                        ) -> None:
        """
        Writes complex type AR:COMPOSITE-RULE-BASED-VALUE-SPECIFICATION
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.CompositeRuleBasedValueSpecification)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_value_specification_group(elem)
            self._write_composite_rule_based_value_specification_group(elem)
            self._leave_child()

    def _write_composite_rule_based_value_specification_group(self,
                                                              elem: ar_element.CompositeRuleBasedValueSpecification
                                                              ) -> None:
        """
        Writes group AR:COMPOSITE-RULE-BASED-VALUE-SPECIFICATION
        """
        if elem.rule is not None:
            self._add_content("RULE", elem.rule)
        if len(elem.arguments) > 0:
            self._add_child("ARGUMENTS")
            for arg in elem.arguments:
                self._write_value_specification_element(arg)
            self._leave_child()
        if len(elem.compound_primitive_arguments) > 0:
            self._add_child("COMPOUND-PRIMITIVE-ARGUMENTS")
            for arg in elem.compound_primitive_arguments:
                self._write_value_specification_element(arg)
            self._leave_child()
        if elem.max_size_to_fill is not None:
            self._add_content("MAX-SIZE-TO-FILL", str(elem.max_size_to_fill))

    def _write_numerical_or_text(self, elem: ar_element.NumericalOrText) -> None:
        """
        Writes complex type AR:NUMERICAL-OR-TEXT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.NumericalOrText)
        tag = "VTF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_numerical_or_text_group(elem)
            self._leave_child()

    def _write_numerical_or_text_group(self, elem: ar_element.NumericalOrText) -> None:
        """
        Writes group AR:NUMERICAL-OR-TEXT
        """
        if elem.vf is not None:
            self._add_content("VF", self._format_number(elem.vf))
        if elem.vt is not None:
            self._add_content("VT", elem.vt)

    def _write_rule_arguments(self, elem: ar_element.RuleArguments) -> None:
        """
        Writes complex type AR:RULE-ARGUMENTS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RuleArguments)
        tag = "RULE-ARGUMENTS"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_rule_arguments_group(elem)
            self._leave_child()

    def _write_rule_arguments_group(self, elem: ar_element.RuleArguments) -> None:
        """
        Writes group AR:RULE-ARGUMENTS
        """
        for value in elem.values:
            if isinstance(value, ar_element.NumericalOrText):
                self._write_numerical_or_text(value)
            elif isinstance(value, str):
                self._add_content("VT", value)
            elif isinstance(value, (int, float, ar_element.NumericalValue)):
                self._add_content("V", self._format_number(value))
            else:
                raise NotImplementedError(str(type(value)))

    def _write_rule_based_value_specification(self,
                                              elem: ar_element.RuleBasedValueSpecification,
                                              tag: str = "RULE-BASED-VALUE-SPECIFICATION") -> None:
        """
        Writes complex type AR:RULE-BASED-VALUE-SPECIFICATION
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.RuleBasedValueSpecification)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_rule_based_value_specification_group(elem)
            self._leave_child()

    def _write_rule_based_value_specification_group(self, elem: ar_element.RuleBasedValueSpecification) -> None:
        """
        Writes group AR:RULE-BASED-VALUE-SPECIFICATION
        """
        if elem.rule is not None:
            self._add_content("RULE", elem.rule)
        if len(elem.arguments) > 0:
            self._add_child("ARGUMENTSS")
            for arg in elem.arguments:
                self._write_rule_arguments(arg)
            self._leave_child()
        if elem.max_size_to_fill is not None:
            self._add_content("MAX-SIZE-TO-FILL", str(elem.max_size_to_fill))

# --- CalibrationData elements

    def _write_sw_values(self, elem: ar_element.SwValues) -> None:
        """
        Writes complex type AR:SW-VALUES
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwValues)
        tag = "SW-VALUES-PHYS"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sw_values_group(elem)
            self._leave_child()

    def _write_sw_values_group(self, elem: ar_element.SwValues) -> None:
        """
        Writes group AR:SW-VALUES
        """
        for value in elem.values:
            if isinstance(value, ar_element.NumericalOrText):
                self._write_numerical_or_text(value)
            elif isinstance(value, str):
                self._add_content("VT", value)
            elif isinstance(value, (int, float, ar_element.NumericalValue)):
                self._add_content("V", self._format_number(value))
            elif isinstance(value, ar_element.ValueGroup):
                self._write_value_group(value, "VG")
            else:
                raise NotImplementedError(str(type(value)))

    def _write_value_group(self, elem: ar_element.ValueGroup, tag: str) -> None:
        """
        Writes complex type AR:VALUE-GROUP
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.ValueGroup)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.label is not None:
                self._write_multi_language_long_name(elem.label, "LABEL")
            self._write_sw_values_group(elem)
            self._leave_child()

    def _write_sw_axis_cont(self, elem: ar_element.SwAxisCont) -> None:
        """
        Writes complex type AR:SW-AXIS-CONT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwAxisCont)
        tag = "SW-AXIS-CONT"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sw_axis_cont_group(elem)
            self._leave_child()

    def _write_sw_axis_cont_group(self, elem: ar_element.SwAxisCont) -> None:
        """
        Writes group AR:SW-AXIS-CONT
        """
        if elem.category is not None:
            self._add_content("CATEGORY", ar_enum.enum_to_xml(elem.category))
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)
        if elem.unit_display_name is not None:
            self._write_single_language_unit_names(elem.unit_display_name, "UNIT-DISPLAY-NAME")
        if elem.sw_axis_index is not None:
            self._add_content("SW-AXIS-INDEX", str(elem.sw_axis_index))
        if elem.sw_array_size is not None:
            self._write_value_list(elem.sw_array_size)
        if elem.sw_values_phys is not None:
            self._write_sw_values(elem.sw_values_phys)

    def _write_sw_value_cont(self, elem: ar_element.SwValueCont) -> None:
        """
        Writes complex type AR:SW-VALUE-CONT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwValueCont)
        tag = "SW-VALUE-CONT"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sw_value_cont_group(elem)
            self._leave_child()

    def _write_sw_value_cont_group(self, elem: ar_element.SwValueCont) -> None:
        """
        Writes group AR:SW-VALUE-CONT
        """
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)
        if elem.unit_display_name is not None:
            self._write_single_language_unit_names(elem.unit_display_name, "UNIT-DISPLAY-NAME")
        if elem.sw_array_size is not None:
            self._write_value_list(elem.sw_array_size)
        if elem.sw_values_phys is not None:
            self._write_sw_values(elem.sw_values_phys)

    def _write_rule_based_axis_cont(self,
                                    elem: ar_element.RuleBasedAxisCont,
                                    tag: str = "RULE-BASED-AXIS-CONT") -> None:
        """
        Writes complex type AR:RULE-BASED-AXIS-CONT
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.RuleBasedAxisCont)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_rule_based_axis_cont_group(elem)
            self._leave_child()

    def _write_rule_based_axis_cont_group(self, elem: ar_element.RuleBasedAxisCont) -> None:
        """
        Writes group AR:RULE-BASED-AXIS-CONT
        """
        if elem.category is not None:
            self._add_content("CATEGORY", ar_enum.enum_to_xml(elem.category))
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)
        if elem.sw_array_size is not None:
            self._write_value_list(elem.sw_array_size)
        if elem.sw_axis_index is not None:
            self._add_content("SW-AXIS-INDEX", str(elem.sw_axis_index))
        if elem.rule_based_values is not None:
            self._write_rule_based_value_specification(elem.rule_based_values, "RULE-BASED-VALUES")

    def _write_rule_based_value_cont(self,
                                     elem: ar_element.RuleBasedValueCont,
                                     tag: str = "RULE-BASED-VALUE-CONT") -> None:
        """
        Writes complex type AR:RULE-BASED-VALUE-CONT
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.RuleBasedValueCont)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_rule_based_value_cont_group(elem)
            self._leave_child()

    def _write_rule_based_value_cont_group(self, elem: ar_element.RuleBasedValueCont) -> None:
        """
        Writes group AR:RULE-BASED-VALUE-CONT
        """
        if elem.unit_ref is not None:
            self._write_unit_ref(elem.unit_ref)
        if elem.sw_array_size is not None:
            self._write_value_list(elem.sw_array_size)
        if elem.rule_based_values is not None:
            self._write_rule_based_value_specification(elem.rule_based_values, "RULE-BASED-VALUES")

    def _write_multidimensional_time(self, elem: ar_element.MultidimensionalTime, tag: str) -> None:
        """
        Writes complex type AR:MULTIDIMENSIONAL-TIME
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.MultidimensionalTime)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.time_base is not None:
                self._add_content("CSE-CODE", str(elem.time_base))
            if elem.scaling_factor is not None:
                self._add_content("CSE-CODE-FACTOR", str(elem.scaling_factor))
            self._leave_child()

    # --- ModeDeclaration elements

    def _write_mode_declaration(self, elem: ar_element.ModeDeclaration) -> None:
        """
        Writes complex type AR:MODE-DECLARATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeDeclaration)
        self._add_child("MODE-DECLARATION")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.value is not None:
            self._add_content("VALUE", str(elem.value))
        self._leave_child()

    def _write_mode_error_behavior(self, elem: ar_element.ModeErrorBehavior, tag: str) -> None:
        """
        Writes complex type AR:MODE-ERROR-BEHAVIOR
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.ModeErrorBehavior)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.default_mode_ref is not None:
                self._write_mode_declaration_ref(elem.default_mode_ref, "DEFAULT-MODE-REF")
            if elem.error_reaction_policy is not None:
                self._add_content("ERROR-REACTION-POLICY", ar_enum.enum_to_xml(elem.error_reaction_policy))
            self._leave_child()

    def _write_mode_transition(self, elem: ar_element.ModeTransition) -> None:
        """
        Writes complex type AR:MODE-TRANSITION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeTransition)
        self._add_child("MODE-TRANSITION")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_mode_transition_group(elem)
        self._leave_child()

    def _write_mode_transition_group(self, elem: ar_element.ModeTransition) -> None:
        """
        Writes group AR:MODE-TRANSITION
        """
        if elem.entered_mode_ref:
            self._write_mode_declaration_ref(elem.entered_mode_ref, "ENTERED-MODE-REF")
        if elem.exited_mode_ref:
            self._write_mode_declaration_ref(elem.exited_mode_ref, "EXITED-MODE-REF")

    def _write_mode_declaration_group(self, elem: ar_element.ModeDeclarationGroup) -> None:
        """
        Writes complex type AR:MODE-DECLARATION-GROUP
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeDeclarationGroup)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child("MODE-DECLARATION-GROUP", attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_mode_declaration_group_data(elem)
        self._leave_child()

    def _write_mode_declaration_group_data(self, elem: ar_element.ModeDeclarationGroup) -> None:
        """
        Writes group AR:MODE-DECLARATION-GROUP
        """
        if elem.initial_mode_ref is not None:
            self._write_mode_declaration_ref(elem.initial_mode_ref, "INITIAL-MODE-REF")
        if elem.mode_declarations:
            self._add_child("MODE-DECLARATIONS")
            for mode_declaration in elem.mode_declarations:
                self._write_mode_declaration(mode_declaration)
            self._leave_child()
        if elem.mode_manager_error_behavior is not None:
            self._write_mode_error_behavior(elem.mode_manager_error_behavior, "MODE-MANAGER-ERROR-BEHAVIOR")
        if elem.mode_transitions:
            self._add_child("MODE-TRANSITIONS")
            for mode_transition in elem.mode_transitions:
                self._write_mode_transition(mode_transition)
            self._leave_child()
        if elem.mode_user_error_behavior is not None:
            self._write_mode_error_behavior(elem.mode_user_error_behavior, "MODE-USER-ERROR-BEHAVIOR")
        if elem.on_transition_value is not None:
            self._add_content("ON-TRANSITION-VALUE", str(elem.on_transition_value))

    def _write_mode_declaration_group_prototype(self, elem: ar_element.ModeDeclarationGroupPrototype, tag: str) -> None:
        """
        Writes complex type AR:MODE-DECLARATION-GROUP-PROTOTYPE
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.ModeDeclarationGroupPrototype)
        attr: TupleList = []
        self._collect_identifiable_attributes(elem, attr)
        self._add_child(tag, attr)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_mode_declaration_group_prototype_data(elem)
        self._leave_child()

    def _write_mode_declaration_group_prototype_data(self, elem: ar_element.ModeDeclarationGroupPrototype) -> None:
        """
        Writes group AR:MODE-DECLARATION-GROUP-PROTOTYPE
        """
        if elem.calibration_access is not None:
            self._add_content('SW-CALIBRATION-ACCESS',
                              ar_enum.enum_to_xml(elem.calibration_access))
        if elem.type_ref is not None:
            self._write_mode_declaration_group_ref(elem.type_ref, "TYPE-TREF")

    # --- Port interface elements

    def _write_port_interface(self, elem: ar_element.PortInterface) -> None:
        """
        Writes group AR:PORTINTERFACE
        """
        if elem.is_service is not None:
            self._add_content("IS-SERVICE", self._format_boolean(elem.is_service))
        if elem.service_kind is not None:
            self._add_content("SERVICE-KIND", ar_enum.enum_to_xml(elem.service_kind))

    def _write_nv_data_interface(self, elem: ar_element.NvDataInterface) -> None:
        """
        Writes complex type AR:NV-DATA-INTERFACE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.NvDataInterface)
        self._add_child("NV-DATA-INTERFACE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_port_interface(elem)
        self._write_nv_data_interface_group(elem)
        self._leave_child()

    def _write_nv_data_interface_group(self, elem: ar_element.NvDataInterface) -> None:
        """
        Writes group AR:NV-DATA-INTERFACE
        """
        if elem.data_elements:
            self._add_child("NV-DATAS")
            for data_element in elem.data_elements:
                self._write_variable_data_prototype(data_element, "VARIABLE-DATA-PROTOTYPE")
            self._leave_child()

    def _write_parameter_interface(self, elem: ar_element.ParameterInterface) -> None:
        """
        Writes complex type AR:PARAMETER-INTERFACE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ParameterInterface)
        self._add_child("PARAMETER-INTERFACE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_port_interface(elem)
        self._write_parameter_interface_group(elem)
        self._leave_child()

    def _write_parameter_interface_group(self, elem: ar_element.ParameterInterface) -> None:
        """
        Writes group AR:PARAMETER-INTERFACE
        """
        if elem.parameters:
            self._add_child("PARAMETERS")
            for parameter in elem.parameters:
                self._write_parameter_data_prototype(parameter, "PARAMETER-DATA-PROTOTYPE")
            self._leave_child()

    def _write_sender_receiver_interface(self, elem: ar_element.SenderReceiverInterface) -> None:
        """
        Writes complex type AR:SENDER-RECEIVER-INTERFACE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SenderReceiverInterface)
        self._add_child("SENDER-RECEIVER-INTERFACE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_port_interface(elem)
        self._write_sender_receiver_interface_group(elem)
        self._leave_child()

    def _write_sender_receiver_interface_group(self, elem: ar_element.SenderReceiverInterface) -> None:
        """
        Writes group AR:SENDER-RECEIVER-INTERFACE
        """
        if elem.data_elements:
            self._add_child("DATA-ELEMENTS")
            for data_element in elem.data_elements:
                self._write_variable_data_prototype(data_element, "VARIABLE-DATA-PROTOTYPE")
            self._leave_child()
        if elem.invalidation_policies:
            self._add_child("INVALIDATION-POLICYS")
            for invalidation_policy in elem.invalidation_policies:
                self._write_invalidation_policy(invalidation_policy)
            self._leave_child()

    def _write_invalidation_policy(self, elem: ar_element.InvalidationPolicy) -> None:
        """
        Writes complex type AR:INVALIDATION-POLICY
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.InvalidationPolicy)
        tag = "INVALIDATION-POLICY"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_invalidation_policy_group(elem)
            self._leave_child()

    def _write_invalidation_policy_group(self, elem: ar_element.InvalidationPolicy) -> None:
        """
        Writes group AR:INVALIDATION-POLICY
        """
        if elem.data_element_ref is not None:
            self._write_variable_data_prototype_ref(elem.data_element_ref, "DATA-ELEMENT-REF")
        if elem.handle_invalid is not None:
            self._add_content("HANDLE-INVALID", ar_enum.enum_to_xml(elem.handle_invalid))

    def _write_application_error(self, elem: ar_element.ApplicationError) -> None:
        """
        Writes complex type AR:APPLICATION-ERROR
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationError)
        self._add_child("APPLICATION-ERROR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_application_error_group(elem)
        self._leave_child()

    def _write_application_error_group(self, elem: ar_element.ApplicationError) -> None:
        """
        Writes group AR:APPLICATION-ERROR
        """
        if elem.error_code is not None:
            self._add_content("ERROR-CODE", str(elem.error_code))

    def _write_client_server_operation(self, elem: ar_element.ClientServerOperation) -> None:
        """
        Writes complex type AR:CLIENT-SERVER-OPERATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ClientServerOperation)
        self._add_child("CLIENT-SERVER-OPERATION")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_client_server_operation_group(elem)
        self._leave_child()

    def _write_client_server_operation_group(self, elem: ar_element.ClientServerOperation) -> None:
        """
        Writes group AR:CLIENT-SERVER-OPERATION
        """
        if elem.arguments:
            self._add_child("ARGUMENTS")
            for argument in elem.arguments:
                self._write_argument_data_prototype(argument)
            self._leave_child()
        if elem.diag_arg_integrity is not None:
            self._add_content("DIAG-ARG-INTEGRITY", self._format_boolean(elem.diag_arg_integrity))
        if elem.possible_error_refs:
            self._add_child("POSSIBLE-ERROR-REFS")
            for possible_error_ref in elem.possible_error_refs:
                self._write_application_error_ref(possible_error_ref, "POSSIBLE-ERROR-REF")
            self._leave_child()

    def _write_client_server_interface(self, elem: ar_element.ClientServerInterface) -> None:
        """
        Writes complex type AR:CLIENT-SERVER-INTERFACE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ClientServerInterface)
        self._add_child("CLIENT-SERVER-INTERFACE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_port_interface(elem)
        self._write_client_server_interface_group(elem)
        self._leave_child()

    def _write_client_server_interface_group(self, elem: ar_element.ClientServerInterface) -> None:
        """
        Writes group AR:CLIENT-SERVER-INTERFACE
        """
        if elem.operations:
            self._add_child("OPERATIONS")
            for operation in elem.operations:
                self._write_client_server_operation(operation)
            self._leave_child()
        if elem.possible_errors:
            self._add_child("POSSIBLE-ERRORS")
            for possible_error in elem.possible_errors:
                self._write_application_error(possible_error)
            self._leave_child()

    def _write_mode_switch_interface(self, elem: ar_element.ModeSwitchInterface) -> None:
        """
        Writes complex type AR:MODE-SWITCH-INTERFACE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeSwitchInterface)
        self._add_child("MODE-SWITCH-INTERFACE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_port_interface(elem)
        if elem.mode_group is not None:
            self._write_mode_declaration_group_prototype(elem.mode_group, "MODE-GROUP")
        self._leave_child()

    def _write_trigger_interface(self, elem: ar_element.TriggerInterface) -> None:
        """
        Writes complex type AR:TRIGGER-INTERFACE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.TriggerInterface)
        self._add_child("TRIGGER-INTERFACE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_port_interface(elem)
        if elem.triggers:
            self._add_child("TRIGGERS")
            for trigger in elem.triggers:
                self._write_trigger(trigger)
            self._leave_child()
        self._leave_child()

    # --- System template elements

    def _write_e2e_transformation_com_spec_props(self, elem: ar_element.EndToEndTransformationComSpecProps) -> None:
        """
        Writes complex type AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
        Multi-tagged: False
        """
        tag = "END-TO-END-TRANSFORMATION-COM-SPEC-PROPS"
        assert isinstance(elem, ar_element.EndToEndTransformationComSpecProps)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_describable(elem)
            self._write_e2e_transformation_com_spec_props_group(elem)
            self._leave_child()

    def _write_e2e_transformation_com_spec_props_group(self,
                                                       elem: ar_element.EndToEndTransformationComSpecProps) -> None:
        """
        Writes group AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
        """
        if elem.clear_from_valid_to_invalid is not None:
            self._add_content("CLEAR-FROM-VALID-TO-INVALID", self._format_boolean(elem.clear_from_valid_to_invalid))
        if elem.disable_e2e_check is not None:
            self._add_content("DISABLE-END-TO-END-CHECK", self._format_boolean(elem.disable_e2e_check))
        if elem.disable_e2e_state_machine is not None:
            self._add_content("DISABLE-END-TO-END-STATE-MACHINE", self._format_boolean(elem.disable_e2e_state_machine))
        if elem.e2e_profile_compatibility_props_ref is not None:
            self._write_e2e_profile_compatibility_props_ref(elem.e2e_profile_compatibility_props_ref)
        if elem.max_delta_counter is not None:
            self._add_content("MAX-DELTA-COUNTER", str(elem.max_delta_counter))
        if elem.max_error_state_init is not None:
            self._add_content("MAX-ERROR-STATE-INIT", str(elem.max_error_state_init))
        if elem.max_error_state_invalid is not None:
            self._add_content("MAX-ERROR-STATE-INVALID", str(elem.max_error_state_invalid))
        if elem.max_error_state_valid is not None:
            self._add_content("MAX-ERROR-STATE-VALID", str(elem.max_error_state_valid))
        if elem.max_no_new_repeated_data is not None:
            self._add_content("MAX-NO-NEW-OR-REPEATED-DATA", str(elem.max_no_new_repeated_data))
        if elem.min_ok_state_init is not None:
            self._add_content("MIN-OK-STATE-INIT", str(elem.min_ok_state_init))
        if elem.min_ok_state_invalid is not None:
            self._add_content("MIN-OK-STATE-INVALID", str(elem.min_ok_state_invalid))
        if elem.min_ok_state_valid is not None:
            self._add_content("MIN-OK-STATE-VALID", str(elem.min_ok_state_valid))
        if elem.sync_counter_init is not None:
            self._add_content("SYNC-COUNTER-INIT", str(elem.sync_counter_init))
        if elem.window_size_init is not None:
            self._add_content("WINDOW-SIZE-INIT", str(elem.window_size_init))
        if elem.window_size_invalid is not None:
            self._add_content("WINDOW-SIZE-INVALID", str(elem.window_size_invalid))
        if elem.window_size_valid is not None:
            self._add_content("WINDOW-SIZE-VALID", str(elem.window_size_valid))

    def _write_e2e_profile_compatibility_props(self, elem: ar_element.E2EProfileCompatibilityProps) -> None:
        """
        Writes complex type AR:E-2-E-PROFILE-COMPATIBILITY-PROPS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.E2EProfileCompatibilityProps)
        self._add_child("E-2-E-PROFILE-COMPATIBILITY-PROPS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.transit_to_invalid_extended is not None:
            self._add_content("TRANSIT-TO-INVALID-EXTENDED", self._format_boolean(elem.transit_to_invalid_extended))
        self._leave_child()

    # --- Software component elements

    def _write_mode_switched_ack_request(self, elem: ar_element.ModeSwitchedAckRequest) -> None:
        """
        Writes complex type AR:MODE-SWITCHED-ACK-REQUEST
        Multi-tagged: False
        """
        tag = "MODE-SWITCHED-ACK"
        assert isinstance(elem, ar_element.ModeSwitchedAckRequest)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.timeout is not None:
                self._add_content("TIMEOUT", self._format_float(elem.timeout))
            self._leave_child()

    def _write_mode_switch_sender_com_spec(self, elem: ar_element.ModeSwitchSenderComSpec) -> None:
        """
        Writes complex type AR:MODE-SWITCH-SENDER-COM-SPEC
        Multi-tagged: False
        """
        tag = "MODE-SWITCH-SENDER-COM-SPEC"
        assert isinstance(elem, ar_element.ModeSwitchSenderComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_mode_switch_sender_com_spec_group(elem)
            self._leave_child()

    def _write_mode_switch_sender_com_spec_group(self,
                                                 elem: ar_element.ModeSwitchSenderComSpec
                                                 ) -> None:
        """
        Writes group AR:MODE-SWITCH-SENDER-COM-SPEC
        """
        if elem.enhanced_mode_api is not None:
            self._add_content("ENHANCED-MODE-API", self._format_boolean(elem.enhanced_mode_api))
        if elem.mode_group_ref is not None:
            self._write_mode_declaration_group_prototype_ref(elem.mode_group_ref, "MODE-GROUP-REF")
        if elem.mode_switched_ack is not None:
            self._write_mode_switched_ack_request(elem.mode_switched_ack)
        if elem.queue_length is not None:
            self._add_content("QUEUE-LENGTH", str(elem.queue_length))

    def _write_transmission_acknowledgement_request(self, elem: ar_element.TransmissionAcknowledgementRequest) -> None:
        """
        Writes complex type AR:TRANSMISSION-ACKNOWLEDGEMENT-REQUEST
        Multi-tagged: False
        """
        tag = "TRANSMISSION-ACKNOWLEDGE"
        assert isinstance(elem, ar_element.TransmissionAcknowledgementRequest)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.timeout is not None:
                self._add_content("TIMEOUT", self._format_float(elem.timeout))
            self._leave_child()

    def _write_tranmsission_com_spec_props(self, elem: ar_element.TransmissionComSpecProps) -> None:
        """
        Writes complex type AR:TRANSMISSION-COM-SPEC-PROPS
        Multi-tagged: False
        """
        tag = "TRANSMISSION-PROPS"
        assert isinstance(elem, ar_element.TransmissionComSpecProps)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.data_update_period is not None:
                self._add_content("DATA-UPDATE-PERIOD", self._format_float(elem.data_update_period))
            if elem.minimum_send_interval is not None:
                self._add_content("MINIMUM-SEND-INTERVAL", self._format_float(elem.minimum_send_interval))
            if elem.transmission_mode is not None:
                self._add_content("TRANSMISSION-MODE", ar_enum.enum_to_xml(elem.transmission_mode))
            self._leave_child()

    def _write_sender_com_spec_group(self, elem: ar_element.SenderComSpec) -> None:
        """
        Writes group AR:SENDER-COM-SPEC
        """
        assert isinstance(elem, ar_element.SenderComSpec)
        if elem.data_element_ref is not None:
            self._write_autosar_data_prototype_ref(elem.data_element_ref, "DATA-ELEMENT-REF")
        if elem.handle_out_of_range is not None:
            self._add_content("HANDLE-OUT-OF-RANGE", ar_enum.enum_to_xml(elem.handle_out_of_range))
        if elem.network_representation is not None:
            self._write_sw_data_def_props(elem.network_representation, "NETWORK-REPRESENTATION")
        if elem.transmission_acknowledge is not None:
            self._write_transmission_acknowledgement_request(elem.transmission_acknowledge)
        if elem.tranmsission_props is not None:
            self._write_tranmsission_com_spec_props(elem.tranmsission_props)
        if elem.uses_end_to_end_protection is not None:
            self._add_content("USES-END-TO-END-PROTECTION", self._format_boolean(elem.uses_end_to_end_protection))

    def _write_queued_sender_com_spec(self, elem: ar_element.QueuedSenderComSpec) -> None:
        """
        Writes complex type AR:QUEUED-SENDER-COM-SPEC
        Multi-tagged: False
        """
        tag = "QUEUED-SENDER-COM-SPEC"
        assert isinstance(elem, ar_element.QueuedSenderComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sender_com_spec_group(elem)
            self._leave_child()

    def _write_non_queued_sender_com_spec(self, elem: ar_element.NonqueuedSenderComSpec) -> None:
        """
        Writes complex type AR:NONQUEUED-SENDER-COM-SPEC
        Multi-tagged: False
        """
        tag = "NONQUEUED-SENDER-COM-SPEC"
        assert isinstance(elem, ar_element.NonqueuedSenderComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_sender_com_spec_group(elem)
            self._write_non_queued_sender_com_spec_group(elem)
            self._leave_child()

    def _write_non_queued_sender_com_spec_group(self, elem: ar_element.NonqueuedSenderComSpec) -> None:
        """
        Writes group AR:NONQUEUED-SENDER-COM-SPEC
        """
        if elem.data_filter is not None:
            self._write_data_filter(elem.data_filter, "DATA-FILTER")
        if elem.init_value is not None:
            self._add_child("INIT-VALUE")
            self._write_value_specification_element(elem.init_value)
            self._leave_child()

    def _write_nv_provide_com_spec(self, elem: ar_element.NonqueuedSenderComSpec) -> None:
        """
        Writes complex type AR:NV-PROVIDE-COM-SPEC
        Multi-tagged: False
        """
        tag = "NV-PROVIDE-COM-SPEC"
        assert isinstance(elem, ar_element.NvProvideComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.ram_block_init_value is not None:
                self._add_child("RAM-BLOCK-INIT-VALUE")
                self._write_value_specification_element(elem.ram_block_init_value)
                self._leave_child()
            if elem.rom_block_init_value is not None:
                self._add_child("ROM-BLOCK-INIT-VALUE")
                self._write_value_specification_element(elem.rom_block_init_value)
                self._leave_child()
            if elem.variable_ref is not None:
                self._write_variable_data_prototype_ref(elem.variable_ref, "VARIABLE-REF")
            self._leave_child()

    def _write_parameter_provide_com_spec(self, elem: ar_element.ParameterProvideComSpec) -> None:
        """
        Writes complex type AR:PARAMETER-PROVIDE-COM-SPEC
        Multi-tagged: False
        """
        tag = "PARAMETER-PROVIDE-COM-SPEC"
        assert isinstance(elem, ar_element.ParameterProvideComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.init_value is not None:
                self._add_child("INIT-VALUE")
                self._write_value_specification_element(elem.init_value)
                self._leave_child()
            if elem.parameter_ref is not None:
                self._write_parameter_data_prototype_ref(elem.parameter_ref, "PARAMETER-REF")
            self._leave_child()

    def _write_server_com_spec(self, elem: ar_element.ServerComSpec) -> None:
        """
        Writes complex type AR:SERVER-COM-SPEC
        Multi-tagged: False
        """
        tag = "SERVER-COM-SPEC"
        assert isinstance(elem, ar_element.ServerComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.operation_ref is not None:
                self._write_client_server_operation_ref(elem.operation_ref, "OPERATION-REF")
            if elem.queue_length is not None:
                self._add_content("QUEUE-LENGTH", str(elem.queue_length))
            if elem.transformation_com_spec_props:
                self._add_child("TRANSFORMATION-COM-SPEC-PROPSS")
                for com_spec_props in elem.transformation_com_spec_props:
                    self._write_e2e_transformation_com_spec_props(com_spec_props)
                self._leave_child()
            self._leave_child()

    def _write_reception_com_spec_props(self, elem: ar_element.ReceptionComSpecProps):
        """
        Writes complex type AR:RECEPTION-COM-SPEC-PROPS
        Multi-tagged: False
        """
        tag = "RECEPTION-PROPS"
        assert isinstance(elem, ar_element.ReceptionComSpecProps)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.data_update_period is not None:
                self._add_content("DATA-UPDATE-PERIOD", self._format_float(elem.data_update_period))
            if elem.timeout is not None:
                self._add_content("TIMEOUT", self._format_float(elem.timeout))
            self._leave_child()

    def _write_receiver_com_spec_group(self, elem: ar_element.ReceiverComSpec) -> None:
        """
        Writes group AR:RECEIVER-COM-SPEC
        """
        if elem.data_element_ref is not None:
            self._write_autosar_data_prototype_ref(elem.data_element_ref, "DATA-ELEMENT-REF")
        if elem.handle_out_of_range is not None:
            self._add_content("HANDLE-OUT-OF-RANGE", ar_enum.enum_to_xml(elem.handle_out_of_range))
        if elem.handle_out_of_range_status is not None:
            self._add_content("HANDLE-OUT-OF-RANGE-STATUS", ar_enum.enum_to_xml(elem.handle_out_of_range_status))
        if elem.max_delta_counter_init is not None:
            self._add_content("MAX-DELTA-COUNTER-INIT", str(elem.max_delta_counter_init))
        if elem.max_no_new_repeated_data is not None:
            self._add_content("MAX-NO-NEW-OR-REPEATED-DATA", str(elem.max_no_new_repeated_data))
        if elem.network_representation is not None:
            self._write_sw_data_def_props(elem.network_representation, "NETWORK-REPRESENTATION")
        if elem.reception_props is not None:
            self._write_reception_com_spec_props(elem.reception_props)
        if elem.replace_with is not None:
            self._write_variable_access(elem.replace_with, "REPLACE-WITH")
        if elem.sync_counter_init is not None:
            self._add_content("SYNC-COUNTER-INIT", str(elem.sync_counter_init))
        if elem.transformation_com_spec_props:
            self._add_child("TRANSFORMATION-COM-SPEC-PROPSS")
            for com_spec_props in elem.transformation_com_spec_props:
                self._write_e2e_transformation_com_spec_props(com_spec_props)
            self._leave_child()
        if elem.uses_end_to_end_protection is not None:
            self._add_content("USES-END-TO-END-PROTECTION", self._format_boolean(elem.uses_end_to_end_protection))

    def _write_queued_receiver_com_spec(self, elem: ar_element.QueuedReceiverComSpec) -> None:
        """
        Writes complex type AR:QUEUED-RECEIVER-COM-SPEC
        Multi-tagged: False
        """
        tag = "QUEUED-RECEIVER-COM-SPEC"
        assert isinstance(elem, ar_element.QueuedReceiverComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_receiver_com_spec_group(elem)
            if elem.queue_length is not None:
                self._add_content("QUEUE-LENGTH", str(elem.queue_length))
            self._leave_child()

    def _write_nonqueued_receiver_com_spec(self, elem: ar_element.NonqueuedReceiverComSpec) -> None:
        """
        Writes complex type AR:NONQUEUED-RECEIVER-COM-SPEC
        Multi-tagged: False
        """
        tag = "NONQUEUED-RECEIVER-COM-SPEC"
        assert isinstance(elem, ar_element.NonqueuedReceiverComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_receiver_com_spec_group(elem)
            self._write_nonqueued_receiver_com_spec_group(elem)
            self._leave_child()

    def _write_nonqueued_receiver_com_spec_group(self, elem: ar_element.NonqueuedReceiverComSpec) -> None:
        """
        Writes group AR:NONQUEUED-RECEIVER-COM-SPEC
        """
        if elem.alive_timeout is not None:
            self._add_content("ALIVE-TIMEOUT", self._format_float(elem.alive_timeout))
        if elem.enable_update is not None:
            self._add_content("ENABLE-UPDATE", self._format_boolean(elem.enable_update))
        if elem.data_filter is not None:
            self._write_data_filter(elem.data_filter, "FILTER")
        if elem.handle_data_status is not None:
            self._add_content("HANDLE-DATA-STATUS", self._format_boolean(elem.handle_data_status))
        if elem.handle_never_received is not None:
            self._add_content("HANDLE-NEVER-RECEIVED", self._format_boolean(elem.handle_never_received))
        if elem.handle_timeout_type is not None:
            self._add_content("HANDLE-TIMEOUT-TYPE", ar_enum.enum_to_xml(elem.handle_timeout_type))
        if elem.init_value is not None:
            self._add_child("INIT-VALUE")
            self._write_value_specification_element(elem.init_value)
            self._leave_child()
        if elem.timeout_substitution_value is not None:
            self._add_child("TIMEOUT-SUBSTITUTION-VALUE")
            self._write_value_specification_element(elem.timeout_substitution_value)
            self._leave_child()

    def _write_nv_require_com_spec(self, elem: ar_element.NvRequireComSpec) -> None:
        """
        Writes complex type AR:NV-REQUIRE-COM-SPEC
        Multi-tagged: False
        """
        tag = "NV-REQUIRE-COM-SPEC"
        assert isinstance(elem, ar_element.NvRequireComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.init_value is not None:
                self._add_child("INIT-VALUE")
                self._write_value_specification_element(elem.init_value)
                self._leave_child()
            if elem.variable_ref is not None:
                self._write_variable_data_prototype_ref(elem.variable_ref, "VARIABLE-REF")
            self._leave_child()

    def _write_parameter_require_com_spec(self, elem: ar_element.ParameterRequireComSpec) -> None:
        """
        Writes complex type AR:PARAMETER-REQUIRE-COM-SPEC
        Multi-tagged: False
        """
        tag = "PARAMETER-REQUIRE-COM-SPEC"
        assert isinstance(elem, ar_element.ParameterRequireComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.init_value is not None:
                self._add_child("INIT-VALUE")
                self._write_value_specification_element(elem.init_value)
                self._leave_child()
            if elem.parameter_ref is not None:
                self._write_parameter_data_prototype_ref(elem.parameter_ref, "PARAMETER-REF")
            self._leave_child()

    def _write_mode_switch_receiver_com_spec(self, elem: ar_element.ModeSwitchReceiverComSpec) -> None:
        """
        Writes complex type AR:MODE-SWITCH-RECEIVER-COM-SPEC
        Multi-tagged: False
        """
        tag = "MODE-SWITCH-RECEIVER-COM-SPEC"
        assert isinstance(elem, ar_element.ModeSwitchReceiverComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.enhanced_mode_api is not None:
                self._add_content("ENHANCED-MODE-API", self._format_boolean(elem.enhanced_mode_api))
            if elem.mode_group_ref is not None:
                self._write_mode_declaration_group_prototype_ref(elem.mode_group_ref, "MODE-GROUP-REF")
            if elem.supports_async is not None:
                self._add_content("SUPPORTS-ASYNCHRONOUS-MODE-SWITCH",
                                  self._format_boolean(elem.supports_async))
            self._leave_child()

    def _write_client_com_spec(self, elem: ar_element.ClientComSpec) -> None:
        """
        Writes complex type AR:CLIENT-COM-SPEC
        Multi-tagged: False
        """
        tag = "CLIENT-COM-SPEC"
        assert isinstance(elem, ar_element.ClientComSpec)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.e2e_call_respone_timeout is not None:
                self._add_content("END-TO-END-CALL-RESPONSE-TIMEOUT",
                                  self._format_float(elem.e2e_call_respone_timeout))
            if elem.operation_ref is not None:
                self._write_client_server_operation_ref(elem.operation_ref, "OPERATION-REF")
            if elem.transformation_com_spec_props:
                self._add_child("TRANSFORMATION-COM-SPEC-PROPSS")
                for com_spec_props in elem.transformation_com_spec_props:
                    self._write_e2e_transformation_com_spec_props(com_spec_props)
                self._leave_child()
            self._leave_child()

    def _write_provided_com_spec(self, elem: ar_element.ProvidePortComSpec) -> None:
        """
        Writes COM-SPEC for P-PORT
        """
        class_name = elem.__class__.__name__
        write_method = self.switcher_provided_com_spec.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for class {class_name}")

    def _write_required_com_spec(self, elem: ar_element.ProvidePortComSpec) -> None:
        """
        Writes COM-SPEC for R-PORT
        """
        class_name = elem.__class__.__name__
        write_method = self.switcher_required_com_spec.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for class {class_name}")

    def _write_provide_port_prototype(self, elem: ar_element.ProvidePortPrototype) -> None:
        """
        Writes complex type AR:P-PORT-PROTOTYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ProvidePortPrototype)
        self._add_child("P-PORT-PROTOTYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_provide_port_prototype_group(elem)
        self._leave_child()

    def _write_provide_port_prototype_group(self, elem: ar_element.ProvidePortPrototype) -> None:
        """
        Writes group AR:P-PORT-PROTOTYPE
        """
        if elem.com_spec:
            self._add_child("PROVIDED-COM-SPECS")
            for com_spec_elem in elem.com_spec:
                self._write_provided_com_spec(com_spec_elem)
            self._leave_child()
        if elem.port_interface_ref is not None:
            self._write_port_interface_ref(elem.port_interface_ref, "PROVIDED-INTERFACE-TREF")

    def _write_require_port_prototype(self, elem: ar_element.RequirePortPrototype) -> None:
        """
        Writes complex type AR:R-PORT-PROTOTYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RequirePortPrototype)
        self._add_child("R-PORT-PROTOTYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_require_port_prototype_group(elem)
        self._leave_child()

    def _write_require_port_prototype_group(self, elem: ar_element.RequirePortPrototype) -> None:
        """
        Writes group AR:R-PORT-PROTOTYPE
        """
        if elem.allow_unconnected is not None:
            self._add_content("MAY-BE-UNCONNECTED", self._format_boolean(elem.allow_unconnected))
        if elem.com_spec:
            self._add_child("REQUIRED-COM-SPECS")
            for com_spec_elem in elem.com_spec:
                self._write_required_com_spec(com_spec_elem)
            self._leave_child()
        if elem.port_interface_ref is not None:
            self._write_port_interface_ref(elem.port_interface_ref, "REQUIRED-INTERFACE-TREF")

    def _write_pr_port_prototype(self, elem: ar_element.PRPortPrototype) -> None:
        """
        Writes complex type AR:PR-PORT-PROTOTYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.PRPortPrototype)
        self._add_child("PR-PORT-PROTOTYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_pr_port_prototype_group(elem)
        self._leave_child()

    def _write_pr_port_prototype_group(self, elem: ar_element.PRPortPrototype) -> None:
        """
        Writes group AR:PR-PORT-PROTOTYPE
        """
        if elem.provided_com_spec:
            self._add_child("PROVIDED-COM-SPECS")
            for com_spec_elem in elem.provided_com_spec:
                self._write_provided_com_spec(com_spec_elem)
            self._leave_child()
        if elem.required_com_spec:
            self._add_child("REQUIRED-COM-SPECS")
            for com_spec_elem in elem.required_com_spec:
                self._write_required_com_spec(com_spec_elem)
            self._leave_child()
        if elem.port_interface_ref is not None:
            self._write_port_interface_ref(elem.port_interface_ref, "PROVIDED-REQUIRED-INTERFACE-TREF")

    def _write_port_prototype(self, elem: ar_element.PortPrototypeElement) -> None:
        """
        Writes port protype elements
        """
        if isinstance(elem, ar_element.ProvidePortPrototype):
            self._write_provide_port_prototype(elem)
        elif isinstance(elem, ar_element.RequirePortPrototype):
            self._write_require_port_prototype(elem)
        elif isinstance(elem, ar_element.PRPortPrototype):
            self._write_pr_port_prototype(elem)
        else:
            raise NotImplementedError(str(type(elem)))

    def _write_sw_component_type(self, elem: ar_element.SwComponentType) -> None:
        """
        Writes group AR:SW-COMPONENT-TYPE
        """
        if elem.ports:
            self._add_child("PORTS")
            for port in elem.ports:
                self._write_port_prototype(port)
            self._leave_child()

    def _write_atomic_sw_component_type(self, elem: ar_element.AtomicSoftwareComponentType) -> None:
        """
        Writes AR:ATOMIC-SW-COMPONENT-TYPE
        """
        if elem.internal_behavior is not None:
            self._add_child("INTERNAL-BEHAVIORS")
            self._write_swc_internal_behavior(elem.internal_behavior)
            self._leave_child()
        if elem.symbol_props is not None:
            self._write_symbol_props(elem.symbol_props, "SYMBOL-PROPS")

    def _write_application_software_component_type(self, elem: ar_element.ApplicationSoftwareComponentType) -> None:
        """
        Writes complex type AR:APPLICATION-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ApplicationSoftwareComponentType)
        self._add_child("APPLICATION-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_complex_device_driver_sw_component_type(self,
                                                       elem: ar_element.ComplexDeviceDriverSwComponentType) -> None:
        """
        Writes complex type AR:COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ComplexDeviceDriverSwComponentType)
        self._add_child("COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_nv_block_sw_component_type(self, elem: ar_element.NvBlockSwComponentType) -> None:
        """
        Writes complex type AR:NV-BLOCK-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.NvBlockSwComponentType)
        self._add_child("NV-BLOCK-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_ecu_abstraction_sw_component_type(self, elem: ar_element.EcuAbstractionSwComponentType) -> None:
        """
        Writes complex type AR:ECU-ABSTRACTION-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.EcuAbstractionSwComponentType)
        self._add_child("ECU-ABSTRACTION-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_sensor_actuator_sw_component_type(self, elem: ar_element.SensorActuatorSwComponentType) -> None:
        """
        Writes complex type AR:SENSOR-ACTUATOR-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SensorActuatorSwComponentType)
        self._add_child("SENSOR-ACTUATOR-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_service_sw_component_type(self, elem: ar_element.ServiceSwComponentType) -> None:
        """
        Writes complex type AR:SERVICE-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ServiceSwComponentType)
        self._add_child("SERVICE-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_service_proxy_sw_component_type(self, elem: ar_element.ServiceProxySwComponentType) -> None:
        """
        Writes complex type AR:SERVICE-PROXY-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ServiceProxySwComponentType)
        self._add_child("SERVICE-PROXY-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_atomic_sw_component_type(elem)
        self._leave_child()

    def _write_sw_component_prototype(self, elem: ar_element.SwComponentPrototype) -> None:
        """
        Writes complex type AR:SW-COMPONENT-PROTOTYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwComponentPrototype)
        self._add_child("SW-COMPONENT-PROTOTYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.type_ref is not None:
            self._write_sw_component_type_ref(elem.type_ref, "TYPE-TREF")
        self._leave_child()

    def _write_port_in_composition_type_instance_ref(self,
                                                     elem: ar_element.PortInCompositionTypeInstanceRef,
                                                     elem_tag: str) -> None:
        """
        Writes merge of complex types AR:P-PORT-IN-COMPOSITION-INSTANCE-REF and R-PORT-IN-COMPOSITION-INSTANCE-REF

        and R-PORT-IN-COMPOSITION-INSTANCE-REF
        """
        assert isinstance(elem, ar_element.PortInCompositionTypeInstanceRef)
        if elem.is_empty:
            self._add_content(elem_tag)
        else:
            self._add_child(elem_tag)
            if elem.component_ref is not None:
                self._write_sw_component_prototype_ref(elem.component_ref, "CONTEXT-COMPONENT-REF")
            if elem.port_ref is not None:
                if elem_tag in ("PROVIDER-IREF", "P-PORT-IN-COMPOSITION-INSTANCE-REF"):
                    port_ref_tag = "TARGET-P-PORT-REF"
                    assert elem.port_ref.is_provide_port_ref
                elif elem_tag in ("REQUESTER-IREF", "R-PORT-IN-COMPOSITION-INSTANCE-REF"):
                    port_ref_tag = "TARGET-R-PORT-REF"
                    assert elem.port_ref.is_require_port_ref
                else:
                    self._leave_child()
                    return
                self._write_port_prototype_ref(elem.port_ref, port_ref_tag)
            self._leave_child()

    def _write_assembly_sw_connector(self, elem: ar_element.AssemblySwConnector) -> None:
        """
        Writes complex type AR:ASSEMBLY-SW-CONNECTOR
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.AssemblySwConnector)
        self._add_child("ASSEMBLY-SW-CONNECTOR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.provide_port is not None:
            self._write_port_in_composition_type_instance_ref(elem.provide_port, "PROVIDER-IREF")
        if elem.require_port is not None:
            self._write_port_in_composition_type_instance_ref(elem.require_port, "REQUESTER-IREF")
        self._leave_child()

    def _write_delegation_sw_connector(self, elem: ar_element.DelegationSwConnector) -> None:
        """
        Writes complex type AR:DELEGATION-SW-CONNECTOR
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DelegationSwConnector)
        self._add_child("DELEGATION-SW-CONNECTOR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.inner_port is not None:
            xml_tag = elem.xml_tag
            if xml_tag is not None:
                self._add_child("INNER-PORT-IREF")
                self._write_port_in_composition_type_instance_ref(elem.inner_port, xml_tag)
                self._leave_child()
            else:
                self._warn(f"Unable to determine direction of port reference for '{elem.name}', Skipping.")
        if elem.outer_port is not None:
            self._write_port_prototype_ref(elem.outer_port, "OUTER-PORT-REF")
        self._leave_child()

    def _write_passthrough_sw_connector(self, elem: ar_element.PassThroughSwConnector) -> None:
        """
        Writes complex type AR:PASS-THROUGH-SW-CONNECTOR
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.PassThroughSwConnector)
        self._add_child("PASS-THROUGH-SW-CONNECTOR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.provide_port is not None:
            self._write_port_prototype_ref(elem.provide_port, "PROVIDED-OUTER-PORT-REF")
        if elem.require_port is not None:
            self._write_port_prototype_ref(elem.require_port, "REQUIRED-OUTER-PORT-REF")
        self._leave_child()

    def _write_composition_sw_component_type(self, elem: ar_element.CompositionSwComponentType) -> None:
        """
        Writes complex type AR:COMPOSITION-SW-COMPONENT-TYPE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.CompositionSwComponentType)
        self._add_child("COMPOSITION-SW-COMPONENT-TYPE")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_sw_component_type(elem)
        self._write_composition_sw_component_type_group(elem)
        self._leave_child()

    def _write_composition_sw_component_type_group(self, elem: ar_element.CompositionSwComponentType) -> None:
        """
        Writes group AR:COMPOSITION-SW-COMPONENT-TYPE
        """
        if elem.components:
            self._add_child("COMPONENTS")
            for component in elem.components:
                self._write_sw_component_prototype(component)
            self._leave_child()
        if elem.connectors:
            self._add_child("CONNECTORS")
            for connector in elem.connectors:
                if isinstance(connector, ar_element.AssemblySwConnector):
                    self._write_assembly_sw_connector(connector)
                elif isinstance(connector, ar_element.DelegationSwConnector):
                    self._write_delegation_sw_connector(connector)
                elif isinstance(connector, ar_element.PassThroughSwConnector):
                    self._write_passthrough_sw_connector(connector)
            self._leave_child()

    def _write_swc_implementation(self, elem: ar_element.SwcImplementation) -> None:
        """
        Writes complex type AR:SWC-IMPLEMENTATION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwcImplementation)
        self._add_child("SWC-IMPLEMENTATION")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_implementtion(elem)
        self._write_swc_implementation_group(elem)
        self._leave_child()

    def _write_swc_implementation_group(self, elem: ar_element.SwcImplementation) -> None:
        """
        Writes group AR:SWC-IMPLEMENTATION
        """
        if elem.behavior_ref is not None:
            self._write_swc_internal_behavior_ref(elem.behavior_ref, "BEHAVIOR-REF")
        # .PER-INSTANCE-MEMORY-SIZES not yet supported
        if elem.required_rte_vendor is not None:
            self._add_content("REQUIRED-RTE-VENDOR", elem.required_rte_vendor)

    def _write_p_mode_group_in_atomic_swc_instance_ref(self,
                                                       elem: ar_element.PModeGroupInAtomicSwcInstanceRef,
                                                       tag: str) -> None:
        """
        Writes complex type AR:P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.PModeGroupInAtomicSwcInstanceRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_provided_port_prototype_ref(elem.context_port, "CONTEXT-P-PORT-REF")
            if elem.target_mode_group is not None:
                self._write_mode_declaration_group_prototype_ref(elem.target_mode_group,
                                                                 "TARGET-MODE-GROUP-REF")
            self._leave_child()

    def _write_p_operation_in_atomic_swc_instance_ref(self,
                                                      elem: ar_element.POperationInAtomicSwcInstanceRef
                                                      ) -> None:
        """
        Writes complex type AR:P-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.POperationInAtomicSwcInstanceRef)
        tag = "OPERATION-IREF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_provided_port_prototype_ref(elem.context_port, "CONTEXT-P-PORT-REF")
            if elem.target_provided_operation is not None:
                self._write_client_server_operation_ref(elem.target_provided_operation,
                                                        "TARGET-PROVIDED-OPERATION-REF")
            self._leave_child()

    def _write_p_trigger_in_atomic_swc_instance_ref(self,
                                                    elem: ar_element.PTriggerInAtomicSwcTypeInstanceRef,
                                                    tag: str
                                                    ) -> None:
        """
        Writes complex type AR:P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.PTriggerInAtomicSwcTypeInstanceRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_provided_port_prototype_ref(elem.context_port, "CONTEXT-P-PORT-REF")
            if elem.target_trigger is not None:
                self._write_trigger_ref(elem.target_trigger, "TARGET-TRIGGER-REF")
            self._leave_child()

    def _write_r_mode_in_atomic_swc_instance_ref(self, elem: ar_element.RModeInAtomicSwcInstanceRef, tag: str) -> None:
        """
        Writes complex type AR:R-MODE-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.RModeInAtomicSwcInstanceRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_required_port_prototype_ref(elem.context_port, "CONTEXT-PORT-REF")
            if elem.context_mode_declaration_group_prototype is not None:
                self._write_mode_declaration_group_prototype_ref(elem.context_mode_declaration_group_prototype,
                                                                 "CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF")
            if elem.target_mode_declaration is not None:
                self._write_mode_declaration_ref(elem.target_mode_declaration, "TARGET-MODE-DECLARATION-REF")
            self._leave_child()

    def _write_r_mode_group_in_atomic_swc_instance_ref(self,
                                                       elem: ar_element.RModeGroupInAtomicSwcInstanceRef) -> None:
        """
        Writes complex type AR:R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RModeGroupInAtomicSwcInstanceRef)
        tag = "R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_required_port_prototype_ref(elem.context_port, "CONTEXT-R-PORT-REF")
            if elem.target_mode_group is not None:
                self._write_mode_declaration_group_prototype_ref(elem.target_mode_group, "TARGET-MODE-GROUP-REF")
            self._leave_child()

    def _write_r_operation_in_atomic_swc_instance_ref(self,
                                                      elem: ar_element.ROperationInAtomicSwcInstanceRef
                                                      ) -> None:
        """
        Writes complex type AR:R-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ROperationInAtomicSwcInstanceRef)
        tag = "OPERATION-IREF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_required_port_prototype_ref(elem.context_port, "CONTEXT-R-PORT-REF")
            if elem.target_required_operation is not None:
                self._write_client_server_operation_ref(elem.target_required_operation,
                                                        "TARGET-REQUIRED-OPERATION-REF")
            self._leave_child()

    def _write_r_variable_in_atomic_swc_instance_ref(self,
                                                     elem: ar_element.RVariableInAtomicSwcInstanceRef
                                                     ) -> None:
        """
        Writes complex type AR:R-VARIABLE-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RVariableInAtomicSwcInstanceRef)
        tag = "DATA-IREF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_required_port_prototype_ref(elem.context_port, "CONTEXT-R-PORT-REF")
            if elem.target_data_element is not None:
                self._write_variable_data_prototype_ref(elem.target_data_element, "TARGET-DATA-ELEMENT-REF")
            self._leave_child()

    def _write_r_trigger_in_atomic_swc_instance_ref(self,
                                                    elem: ar_element.RTriggerInAtomicSwcInstanceRef,
                                                    tag: str
                                                    ) -> None:
        """
        Writes complex type AR:R-TRIGGER-IN-ATOMIC-SWC-INSTANCE-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.RTriggerInAtomicSwcInstanceRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.context_port is not None:
                self._write_abstract_required_port_prototype_ref(elem.context_port, "CONTEXT-R-PORT-REF")
            if elem.target_trigger is not None:
                self._write_trigger_ref(elem.target_trigger, "TARGET-TRIGGER-REF")
            self._leave_child()

    # --- SWC Internal behavior elements

    def _write_variable_in_impl_data_instance_ref(self,
                                                  elem: ar_element.ArVariableInImplementationDataInstanceRef,
                                                  tag: str) -> None:
        """
        Writes complex type AR:AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.ArVariableInImplementationDataInstanceRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.port_prototype_ref is not None:
                self._write_port_prototype_ref(elem.port_prototype_ref, "PORT-PROTOTYPE-REF")
            if elem.root_variable_data_prototype_ref is not None:
                self._write_variable_data_prototype_ref(elem.root_variable_data_prototype_ref,
                                                        "ROOT-VARIABLE-DATA-PROTOTYPE-REF")
            if elem.context_data_prototype_refs:
                self._add_child("CONTEXT-DATA-PROTOTYPE-REFS")
                for child_elem in elem.context_data_prototype_refs:
                    self._write_abstract_impl_data_type_element_ref(child_elem, "CONTEXT-DATA-PROTOTYPE-REF")
                self._leave_child()
            if elem.target_data_prototype_ref is not None:
                self._write_abstract_impl_data_type_element_ref(elem.target_data_prototype_ref,
                                                                "TARGET-DATA-PROTOTYPE-REF")
            self._leave_child()

    def _write_variable_in_atomic_swc_type_instance_ref(self,
                                                        elem: ar_element.VariableInAtomicSWCTypeInstanceRef
                                                        ) -> None:
        """
        Writes complex type AR:VARIABLE-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.VariableInAtomicSWCTypeInstanceRef)
        tag = "AUTOSAR-VARIABLE-IREF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.port_prototype_ref is not None:
                self._write_port_prototype_ref(elem.port_prototype_ref, "PORT-PROTOTYPE-REF")
            if elem.root_variable_data_prototype_ref is not None:
                self._write_variable_data_prototype_ref(elem.root_variable_data_prototype_ref,
                                                        "ROOT-VARIABLE-DATA-PROTOTYPE-REF")
            if elem.context_data_prototype_refs:
                for child_elem in elem.context_data_prototype_refs:
                    self._write_appl_composite_element_data_proto_ref(child_elem, "CONTEXT-DATA-PROTOTYPE-REF")
            if elem.target_data_prototype_ref is not None:
                self._write_data_prototype_ref(elem.target_data_prototype_ref, "TARGET-DATA-PROTOTYPE-REF")
            self._leave_child()

    def _write_autosar_variable_ref(self,
                                    elem: ar_element.AutosarVariableRef,
                                    tag: str) -> None:
        """
        Writes complex type AR:AUTOSAR-VARIABLE-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.AutosarVariableRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.ar_variable_in_impl_datatype is not None:
                self._write_variable_in_impl_data_instance_ref(elem.ar_variable_in_impl_datatype,
                                                               "AUTOSAR-VARIABLE-IN-IMPL-DATATYPE")
            if elem.ar_variable_iref is not None:
                self._write_variable_in_atomic_swc_type_instance_ref(elem.ar_variable_iref)
            if elem.local_variable_ref is not None:
                self._write_variable_data_prototype_ref(elem.local_variable_ref,
                                                        "LOCAL-VARIABLE-REF")
            self._leave_child()

    def _write_variable_access(self, elem: ar_element.VariableAccess, tag: str) -> None:
        """
        Writes complex type AR:VARIABLE-ACCESS
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.VariableAccess)
        self._add_child(tag)
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        if elem.accessed_variable is not None:
            self._write_autosar_variable_ref(elem.accessed_variable, "ACCESSED-VARIABLE")
        if elem.scope is not None:
            self._add_content("SCOPE", ar_enum.enum_to_xml(elem.scope))
        self._leave_child()

    def _write_runnable_entity_argument(self, elem: ar_element.RunnableEntityArgument) -> None:
        """
        Writes complex type AR:RUNNABLE-ENTITY-ARGUMENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RunnableEntityArgument)
        tag = "RUNNABLE-ENTITY-ARGUMENT"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.symbol is not None:
                self._add_content("SYMBOL", elem.symbol)
            self._leave_child()

    def _write_executable_entity_activation_reason(self,
                                                   elem: ar_element.ExecutableEntityActivationReason) -> None:
        """
        Writes complex type AR:EXECUTABLE-ENTITY-ACTIVATION-REASON
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ExecutableEntityActivationReason)
        self._add_child("EXECUTABLE-ENTITY-ACTIVATION-REASON")
        self._write_referrable(elem)
        self._write_implementation_props(elem)
        if elem.bit_position is not None:
            self._add_content("BIT-POSITION", str(elem.bit_position))
        self._leave_child()

    def _write_exclusive_area_ref_conditional(self,
                                              elem: ar_element.ExclusiveAreaRefConditional) -> None:
        """
        Writes complex type AR:EXCLUSIVE-AREA-REF-CONDITIONAL
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ExclusiveAreaRefConditional)
        tag = "EXCLUSIVE-AREA-REF-CONDITIONAL"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.exclusive_area is not None:
                self._write_exclusive_area_ref(elem.exclusive_area, "EXCLUSIVE-AREA-REF")
            self._leave_child()

    def _write_swc_exclusive_area_policy(self, elem: ar_element.SwcExclusiveAreaPolicy) -> None:
        """
        Writes complex type AR:SWC-EXCLUSIVE-AREA-POLICY
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwcExclusiveAreaPolicy)
        tag = "SWC-EXCLUSIVE-AREA-POLICY"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_swc_exclusive_area_policy_group(elem)
            self._leave_child()

    def _write_swc_exclusive_area_policy_group(self, elem: ar_element.SwcExclusiveAreaPolicy) -> None:
        """
        Writes group AR:SWC-EXCLUSIVE-AREA-POLICY
        """
        if elem.api_principle is not None:
            self._add_content("API-PRINCIPLE", ar_enum.enum_to_xml(elem.api_principle))
        if elem.exclusive_area is not None:
            self._write_exclusive_area_ref(elem.exclusive_area, "EXCLUSIVE-AREA-REF")

    def _write_included_data_type_set(self, elem: ar_element.IncludedDataTypeSet) -> None:
        """
        Writes complex type AR:INCLUDED-DATA-TYPE-SET
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.IncludedDataTypeSet)
        tag = "INCLUDED-DATA-TYPE-SET"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_included_data_type_set_group(elem)
            self._leave_child()

    def _write_included_data_type_set_group(self, elem: ar_element.IncludedDataTypeSet) -> None:
        """
        Writes group AR:INCLUDED-DATA-TYPE-SET
        """
        if elem.data_type:
            self._add_child("DATA-TYPE-REFS")
            for item in elem.data_type:
                self._write_autosar_data_type_ref(item, "DATA-TYPE-REF")
            self._leave_child()
        if elem.literal_prefix is not None:
            self._add_content("LITERAL-PREFIX", elem.literal_prefix)

    def _write_included_mode_declaration_group_set(self,
                                                   elem: ar_element.IncludedModeDeclarationGroupSet
                                                   ) -> None:
        """
        Writes complex type AR:INCLUDED-MODE-DECLARATION-GROUP-SET
        """
        assert isinstance(elem, ar_element.IncludedModeDeclarationGroupSet)
        tag = "INCLUDED-MODE-DECLARATION-GROUP-SET"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_included_mode_declaration_group_set_group(elem)
            self._leave_child()

    def _write_included_mode_declaration_group_set_group(self,
                                                         elem: ar_element.IncludedModeDeclarationGroupSet
                                                         ) -> None:
        """
        Writes group AR:INCLUDED-MODE-DECLARATION-GROUP-SET
        """
        if elem.mode_declaration_group:
            self._add_child("MODE-DECLARATION-GROUP-REFS")
            for item in elem.mode_declaration_group:
                self._write_mode_declaration_group_ref(item, "MODE-DECLARATION-GROUP-REF")
            self._leave_child()
        if elem.prefix is not None:
            self._add_content("PREFIX", elem.prefix)

    def _write_instantiation_data_def_props(self,
                                            elem: ar_element.InstantiationDataDefProps,
                                            tag: str = "INSTANTIATION-DATA-DEF-PROPS"
                                            ) -> None:
        """
        Writes complex type AR:INSTANTIATION-DATA-DEF-PROPS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.InstantiationDataDefProps)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_instantiation_data_def_props_group(elem)
            self._leave_child()

    def _write_instantiation_data_def_props_group(self, elem: ar_element.InstantiationDataDefProps) -> None:
        """
        Writes group AR:INSTANTIATION-DATA-DEF-PROPS
        """
        if elem.parameter_instance is not None:
            self._write_autosar_parameter_ref(elem.parameter_instance, "PARAMETER-INSTANCE")
        if elem.sw_data_def_props is not None:
            self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")
        if elem.variable_instance is not None:
            self._write_autosar_variable_ref(elem.variable_instance, "VARIABLE-INSTANCE")

    def _write_per_instance_memory(self, elem: ar_element.PerInstanceMemory) -> None:
        """
        Writes complex type AR:PER-INSTANCE-MEMORY
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.PerInstanceMemory)
        self._add_child("PER-INSTANCE-MEMORY")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_per_instance_memory_group(elem)
        self._leave_child()

    def _write_per_instance_memory_group(self, elem: ar_element.PerInstanceMemory) -> None:
        """
        Writes group AR:PER-INSTANCE-MEMORY
        """
        if elem.init_value is not None:
            self._add_content("INIT-VALUE", elem.init_value)
        if elem.sw_data_def_props is not None:
            self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")
        if elem.type is not None:
            self._add_content("TYPE", elem.type)
        if elem.type_definition is not None:
            self._add_content("TYPE-DEFINITION", elem.type_definition)

    # Service needs elements

    def _write_bsw_mgr_needs(self, elem: ar_element.BswMgrNeeds) -> None:
        """
        Writes complex type AR:BSW-MGR-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.BswMgrNeeds)
        self._add_child("BSW-MGR-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:BSW-MGR-NEEDS contain no elements
        self._leave_child()

    def _write_com_mgr_user_needs(self, elem: ar_element.ComMgrUserNeeds) -> None:
        """
        Writes complex type AR:COM-MGR-USER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ComMgrUserNeeds)
        self._add_child("COM-MGR-USER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_com_mgr_user_needs_group(elem)
        self._leave_child()

    def _write_com_mgr_user_needs_group(self, elem: ar_element.ComMgrUserNeeds) -> None:
        """
        Writes group AR:COM-MGR-USER-NEEDS
        """
        if elem.max_comm_mode is not None:
            self._add_content("MAX-COMM-MODE", ar_enum.enum_to_xml(elem.max_comm_mode))

    def _write_crypto_certificate_key_slot_needs(
            self,
            elem: ar_element.CryptoCertificateKeySlotNeeds) -> None:
        """
        Writes complex type AR:CRYPTO-CERTIFICATE-KEY-SLOT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.CryptoCertificateKeySlotNeeds)
        self._add_child("CRYPTO-CERTIFICATE-KEY-SLOT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:CRYPTO-CERTIFICATE-KEY-SLOT-NEEDS contains no elements
        self._leave_child()

    def _write_crypto_key_management_needs(self, elem: ar_element.CryptoKeyManagementNeeds) -> None:
        """
        Writes complex type AR:CRYPTO-KEY-MANAGEMENT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.CryptoKeyManagementNeeds)
        self._add_child("CRYPTO-KEY-MANAGEMENT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:CRYPTO-KEY-MANAGEMENT-NEEDS contains no elements
        self._leave_child()

    def _write_crypto_service_job_needs(self, elem: ar_element.CryptoServiceJobNeeds) -> None:
        """
        Writes complex type AR:CRYPTO-SERVICE-JOB-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.CryptoServiceJobNeeds)
        self._add_child("CRYPTO-SERVICE-JOB-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:CRYPTO-SERVICE-JOB-NEEDS contains no elements
        self._leave_child()

    def _write_crypto_service_needs(self, elem: ar_element.CryptoServiceNeeds) -> None:
        """
        Writes complex type AR:CRYPTO-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.CryptoServiceNeeds)
        self._add_child("CRYPTO-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_crypto_service_needs_group(elem)
        self._leave_child()

    def _write_crypto_service_needs_group(self, elem: ar_element.CryptoServiceNeeds) -> None:
        """
        Writes group AR:CRYPTO-SERVICE-NEEDS
        """
        if elem.algorithm_family is not None:
            self._add_content("ALGORITHM-FAMILY", elem.algorithm_family)
        if elem.algorithm_mode is not None:
            self._add_content("ALGORITHM-MODE", elem.algorithm_mode)
        if elem.crypto_key_description is not None:
            self._add_content("CRYPTO-KEY-DESCRIPTION", elem.crypto_key_description)
        if elem.maximum_key_length is not None:
            self._add_content("MAXIMUM-KEY-LENGTH", str(elem.maximum_key_length))

    def _write_traced_failure_group(self, elem: ar_element.TracedFailure) -> None:
        """
        Writes group AR:TRACED-FAILURE
        """
        if elem.id is not None:
            self._add_content("ID", str(elem.id))

    def _write_development_error(self, elem: ar_element.DevelopmentError) -> None:
        """
        Writes complex type AR:DEVELOPMENT-ERROR
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DevelopmentError)
        self._add_child("DEVELOPMENT-ERROR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_traced_failure_group(elem)
        self._leave_child()

    def _write_diag_event_debounce_algorithm(
            self,
            elem: ar_element.DiagEventDebounceAlgorithmType) -> None:
        """
        Writes choice AR:DIAG-EVENT-DEBOUNCE-ALGORITHM
        """
        write_method = self.switcher_non_collectable.get(elem.__class__.__name__, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for class '{elem.__class__.__name__}'")

    def _write_diag_event_debounce_counter_based(
            self,
            elem: ar_element.DiagEventDebounceCounterBased) -> None:
        """
        Writes complex type AR:DIAG-EVENT-DEBOUNCE-COUNTER-BASED
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagEventDebounceCounterBased)
        self._add_child("DIAG-EVENT-DEBOUNCE-COUNTER-BASED")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:DIAG-EVENT-DEBOUNCE-ALGORITHM contains no elements
        self._write_diag_event_debounce_counter_based_group(elem)
        self._leave_child()

    def _write_diag_event_debounce_counter_based_group(
            self,
            elem: ar_element.DiagEventDebounceCounterBased) -> None:
        """
        Writes group AR:DIAG-EVENT-DEBOUNCE-COUNTER-BASED
        """
        if elem.counter_based_fdc_threshold_storage_value is not None:
            self._add_content("COUNTER-BASED-FDC-THRESHOLD-STORAGE-VALUE",
                              str(elem.counter_based_fdc_threshold_storage_value))
        if elem.counter_decrement_step_size is not None:
            self._add_content("COUNTER-DECREMENT-STEP-SIZE", str(elem.counter_decrement_step_size))
        if elem.counter_failed_threshold is not None:
            self._add_content("COUNTER-FAILED-THRESHOLD", str(elem.counter_failed_threshold))
        if elem.counter_increment_step_size is not None:
            self._add_content("COUNTER-INCREMENT-STEP-SIZE", str(elem.counter_increment_step_size))
        if elem.counter_jump_down is not None:
            self._add_content("COUNTER-JUMP-DOWN", self._format_boolean(elem.counter_jump_down))
        if elem.counter_jump_down_value is not None:
            self._add_content("COUNTER-JUMP-DOWN-VALUE", str(elem.counter_jump_down_value))
        if elem.counter_jump_up is not None:
            self._add_content("COUNTER-JUMP-UP", self._format_boolean(elem.counter_jump_up))
        if elem.counter_jump_up_value is not None:
            self._add_content("COUNTER-JUMP-UP-VALUE", str(elem.counter_jump_up_value))
        if elem.counter_passed_threshold is not None:
            self._add_content("COUNTER-PASSED-THRESHOLD", str(elem.counter_passed_threshold))

    def _write_diag_event_debounce_monitor_internal(
            self,
            elem: ar_element.DiagEventDebounceMonitorInternal) -> None:
        """
        Writes complex type AR:DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagEventDebounceMonitorInternal)
        self._add_child("DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:DIAG-EVENT-DEBOUNCE-ALGORITHM contains no elements
        # Group AR:DIAG-EVENT-DEBOUNCE-MONITOR-INTERNAL contains no elements
        self._leave_child()

    def _write_diag_event_debounce_time_based(
            self,
            elem: ar_element.DiagEventDebounceTimeBased) -> None:
        """
        Writes complex type AR:DIAG-EVENT-DEBOUNCE-TIME-BASED
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagEventDebounceTimeBased)
        self._add_child("DIAG-EVENT-DEBOUNCE-TIME-BASED")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:DIAG-EVENT-DEBOUNCE-ALGORITHM contains no elements
        self._write_diag_event_debounce_time_based_group(elem)
        self._leave_child()

    def _write_diag_event_debounce_time_based_group(
            self,
            elem: ar_element.DiagEventDebounceTimeBased) -> None:
        """
        Writes group AR:DIAG-EVENT-DEBOUNCE-TIME-BASED
        """
        if elem.time_based_fdc_threshold_storage_value is not None:
            self._add_content("TIME-BASED-FDC-THRESHOLD-STORAGE-VALUE",
                              str(elem.time_based_fdc_threshold_storage_value))
        if elem.time_failed_threshold is not None:
            self._add_content("TIME-FAILED-THRESHOLD", str(elem.time_failed_threshold))
        if elem.time_passed_threshold is not None:
            self._add_content("TIME-PASSED-THRESHOLD", str(elem.time_passed_threshold))

    def _write_diagnostic_capability_element_group(self, elem: ar_element.DiagnosticCapabilityElement) -> None:
        """
        Writes group AR:DIAGNOSTIC-CAPABILITY-ELEMENT
        """
        if len(elem.audience) > 0:
            self._add_child("AUDIENCES")
            for audience in elem.audience:
                self._add_content("AUDIENCE", ar_enum.enum_to_xml(audience))
            self._leave_child()
        if elem.diag_requirement is not None:
            self._add_content("DIAG-REQUIREMENT", elem.diag_requirement)
        if elem.security_access_level is not None:
            self._add_content("SECURITY-ACCESS-LEVEL", str(elem.security_access_level))

    def _write_diagnostic_clear_condition_needs(
            self,
            elem: ar_element.DiagnosticClearConditionNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-CLEAR-CONDITION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticClearConditionNeeds)
        self._add_child("DIAGNOSTIC-CLEAR-CONDITION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-CLEAR-CONDITION-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_communication_manager_needs(
            self,
            elem: ar_element.DiagnosticCommunicationManagerNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticCommunicationManagerNeeds)
        self._add_child("DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_communication_manager_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_communication_manager_needs_group(
            self,
            elem: ar_element.DiagnosticCommunicationManagerNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-COMMUNICATION-MANAGER-NEEDS
        """
        if elem.service_request_callback_type is not None:
            self._add_content("SERVICE-REQUEST-CALLBACK-TYPE",
                              ar_enum.enum_to_xml(elem.service_request_callback_type))

    def _write_diagnostic_component_needs(
            self,
            elem: ar_element.DiagnosticComponentNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-COMPONENT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticComponentNeeds)
        self._add_child("DIAGNOSTIC-COMPONENT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-COMPONENT-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_control_needs(
            self,
            elem: ar_element.DiagnosticControlNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-CONTROL-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticControlNeeds)
        self._add_child("DIAGNOSTIC-CONTROL-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-CONTROL-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_enable_condition_needs(
            self,
            elem: ar_element.DiagnosticEnableConditionNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-ENABLE-CONDITION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticEnableConditionNeeds)
        self._add_child("DIAGNOSTIC-ENABLE-CONDITION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_enable_condition_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_enable_condition_needs_group(
            self,
            elem: ar_element.DiagnosticEnableConditionNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-ENABLE-CONDITION-NEEDS
        """
        if elem.initial_status is not None:
            self._add_content("INITIAL-STATUS", ar_enum.enum_to_xml(elem.initial_status))

    def _write_diagnostic_event_needs(
            self,
            elem: ar_element.DiagnosticEventNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-EVENT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticEventNeeds)
        self._add_child("DIAGNOSTIC-EVENT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_event_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_event_needs_group(
            self,
            elem: ar_element.DiagnosticEventNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-EVENT-NEEDS
        """
        if elem.consider_pto_status is not None:
            self._add_content("CONSIDER-PTO-STATUS", self._format_boolean(elem.consider_pto_status))
        if elem.diag_event_debounce_algorithm is not None:
            self._add_child("DIAG-EVENT-DEBOUNCE-ALGORITHM")
            self._write_diag_event_debounce_algorithm(elem.diag_event_debounce_algorithm)
            self._leave_child()
        if elem.dtc_kind is not None:
            self._add_content("DTC-KIND", ar_enum.enum_to_xml(elem.dtc_kind))
        if elem.dtc_number is not None:
            self._add_content("DTC-NUMBER", str(elem.dtc_number))
        if elem.inhibiting_fid_ref is not None:
            self._write_function_inhibition_needs_ref(elem.inhibiting_fid_ref, "INHIBITING-FID-REF")
        if len(elem.inhibiting_secondary_fid_refs) > 0:
            self._add_child("INHIBITING-SECONDARY-FID-REFS")
            for ref in elem.inhibiting_secondary_fid_refs:
                self._write_function_inhibition_needs_ref(ref, "INHIBITING-SECONDARY-FID-REF")
            self._leave_child()
        if elem.obd_dtc_number is not None:
            self._add_content("OBD-DTC-NUMBER", str(elem.obd_dtc_number))
        if elem.prestored_freezeframe_stored_in_nvm is not None:
            self._add_content("PRESTORED-FREEZEFRAME-STORED-IN-NVM",
                              self._format_boolean(elem.prestored_freezeframe_stored_in_nvm))
        if elem.report_behavior is not None:
            self._add_content("REPORT-BEHAVIOR", ar_enum.enum_to_xml(elem.report_behavior))
        if elem.uds_dtc_number is not None:
            self._add_content("UDS-DTC-NUMBER", str(elem.uds_dtc_number))
        if elem.uses_monitor_data is not None:
            self._add_content("USES-MONITOR-DATA", self._format_boolean(elem.uses_monitor_data))

    def _write_diagnostic_event_info_needs(
            self,
            elem: ar_element.DiagnosticEventInfoNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-EVENT-INFO-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticEventInfoNeeds)
        self._add_child("DIAGNOSTIC-EVENT-INFO-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_event_info_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_event_info_needs_group(
            self,
            elem: ar_element.DiagnosticEventInfoNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-EVENT-INFO-NEEDS
        """
        if elem.obd_dtc_number is not None:
            self._add_content("OBD-DTC-NUMBER", str(elem.obd_dtc_number))
        if elem.uds_dtc_number is not None:
            self._add_content("UDS-DTC-NUMBER", str(elem.uds_dtc_number))

    def _write_diagnostic_event_manager_needs(
            self,
            elem: ar_element.DiagnosticEventManagerNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-EVENT-MANAGER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticEventManagerNeeds)
        self._add_child("DIAGNOSTIC-EVENT-MANAGER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-EVENT-MANAGER-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_generic_uds_needs(
            self,
            elem: ar_element.DiagnosticGenericUdsNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-GENERIC-UDS-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticGenericUdsNeeds)
        self._add_child("DIAGNOSTIC-GENERIC-UDS-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-GENERIC-UDS-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_indicator_needs(
            self,
            elem: ar_element.DiagnosticIndicatorNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-INDICATOR-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticIndicatorNeeds)
        self._add_child("DIAGNOSTIC-INDICATOR-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-INDICATOR-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_io_control_needs(
            self,
            elem: ar_element.DiagnosticIoControlNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-IO-CONTROL-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticIoControlNeeds)
        self._add_child("DIAGNOSTIC-IO-CONTROL-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_io_control_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_io_control_needs_group(
            self,
            elem: ar_element.DiagnosticIoControlNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-IO-CONTROL-NEEDS
        """
        if elem.current_value_ref is not None:
            self._write_diagnostic_value_needs_ref(elem.current_value_ref, "CURRENT-VALUE-REF")
        if elem.freeze_current_state_supported is not None:
            self._add_content("FREEZE-CURRENT-STATE-SUPPORTED",
                              self._format_boolean(elem.freeze_current_state_supported))
        if elem.reset_to_default_supported is not None:
            self._add_content("RESET-TO-DEFAULT-SUPPORTED",
                              self._format_boolean(elem.reset_to_default_supported))
        if elem.short_term_adjustment_supported is not None:
            self._add_content("SHORT-TERM-ADJUSTMENT-SUPPORTED",
                              self._format_boolean(elem.short_term_adjustment_supported))

    def _write_diagnostic_operation_cycle_needs(
            self,
            elem: ar_element.DiagnosticOperationCycleNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-OPERATION-CYCLE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticOperationCycleNeeds)
        self._add_child("DIAGNOSTIC-OPERATION-CYCLE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_operation_cycle_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_operation_cycle_needs_group(
            self,
            elem: ar_element.DiagnosticOperationCycleNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-OPERATION-CYCLE-NEEDS
        """
        if elem.operation_cycle is not None:
            self._add_content("OPERATION-CYCLE", ar_enum.enum_to_xml(elem.operation_cycle))

    def _write_diagnostic_request_file_transfer_needs(
            self,
            elem: ar_element.DiagnosticRequestFileTransferNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticRequestFileTransferNeeds)
        self._add_child("DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-REQUEST-FILE-TRANSFER-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_response_on_event_needs(
            self,
            elem: ar_element.DiagnosticResponseOnEventNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-RESPONSE-ON-EVENT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticResponseOnEventNeeds)
        self._add_child("DIAGNOSTIC-RESPONSE-ON-EVENT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-RESPONSE-ON-EVENT-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_routine_needs(
            self,
            elem: ar_element.DiagnosticRoutineNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-ROUTINE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticRoutineNeeds)
        self._add_child("DIAGNOSTIC-ROUTINE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_routine_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_routine_needs_group(
            self,
            elem: ar_element.DiagnosticRoutineNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-ROUTINE-NEEDS
        """
        if elem.diag_routine_type is not None:
            self._add_content("DIAG-ROUTINE-TYPE", ar_enum.enum_to_xml(elem.diag_routine_type))

    def _write_diagnostic_storage_condition_needs(
            self,
            elem: ar_element.DiagnosticStorageConditionNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-STORAGE-CONDITION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticStorageConditionNeeds)
        self._add_child("DIAGNOSTIC-STORAGE-CONDITION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_storage_condition_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_storage_condition_needs_group(
            self,
            elem: ar_element.DiagnosticStorageConditionNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-STORAGE-CONDITION-NEEDS
        """
        if elem.initial_status is not None:
            self._add_content("INITIAL-STATUS", ar_enum.enum_to_xml(elem.initial_status))

    def _write_diagnostic_upload_download_needs(
            self,
            elem: ar_element.DiagnosticUploadDownloadNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticUploadDownloadNeeds)
        self._add_child("DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTIC-UPLOAD-DOWNLOAD-NEEDS contains no elements
        self._leave_child()

    def _write_diagnostic_value_needs(
            self,
            elem: ar_element.DiagnosticValueNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTIC-VALUE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticValueNeeds)
        self._add_child("DIAGNOSTIC-VALUE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_diagnostic_value_needs_group(elem)
        self._leave_child()

    def _write_diagnostic_value_needs_group(
            self,
            elem: ar_element.DiagnosticValueNeeds) -> None:
        """
        Writes group AR:DIAGNOSTIC-VALUE-NEEDS
        """
        if elem.data_length is not None:
            self._add_content("DATA-LENGTH", str(elem.data_length))
        if elem.diagnostic_value_access is not None:
            self._add_content("DIAGNOSTIC-VALUE-ACCESS", ar_enum.enum_to_xml(elem.diagnostic_value_access))
        if elem.fixed_length is not None:
            self._add_content("FIXED-LENGTH", self._format_boolean(elem.fixed_length))
        if elem.processing_style is not None:
            self._add_content("PROCESSING-STYLE", ar_enum.enum_to_xml(elem.processing_style))

    def _write_diagnostics_communication_security_needs(
            self,
            elem: ar_element.DiagnosticsCommunicationSecurityNeeds) -> None:
        """
        Writes complex type AR:DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DiagnosticsCommunicationSecurityNeeds)
        self._add_child("DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:DIAGNOSTICS-COMMUNICATION-SECURITY-NEEDS contains no elements
        self._leave_child()

    def _write_dlt_user_needs(
            self,
            elem: ar_element.DltUserNeeds) -> None:
        """
        Writes complex type AR:DLT-USER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DltUserNeeds)
        self._add_child("DLT-USER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:DLT-USER-NEEDS contain no elements
        self._leave_child()

    def _write_do_ip_activation_line_needs(
            self,
            elem: ar_element.DoIpActivationLineNeeds) -> None:
        """
        Writes complex type AR:DO-IP-ACTIVATION-LINE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DoIpActivationLineNeeds)
        self._add_child("DO-IP-ACTIVATION-LINE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS, AR:DO-IP-SERVICE-NEEDS, and AR:DO-IP-ACTIVATION-LINE-NEEDS contain no elements
        self._leave_child()

    def _write_do_ip_gid_needs(
            self,
            elem: ar_element.DoIpGidNeeds) -> None:
        """
        Writes complex type AR:DO-IP-GID-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DoIpGidNeeds)
        self._add_child("DO-IP-GID-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS, AR:DO-IP-SERVICE-NEEDS, and AR:DO-IP-GID-NEEDS contain no elements
        self._leave_child()

    def _write_do_ip_gid_synchronization_needs(
            self,
            elem: ar_element.DoIpGidSynchronizationNeeds) -> None:
        """
        Writes complex type AR:DO-IP-GID-SYNCHRONIZATION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DoIpGidSynchronizationNeeds)
        self._add_child("DO-IP-GID-SYNCHRONIZATION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS, AR:DO-IP-SERVICE-NEEDS, and AR:DO-IP-GID-SYNCHRONIZATION-NEEDS contain no elements
        self._leave_child()

    def _write_do_ip_power_mode_status_needs(
            self,
            elem: ar_element.DoIpPowerModeStatusNeeds) -> None:
        """
        Writes complex type AR:DO-IP-POWER-MODE-STATUS-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DoIpPowerModeStatusNeeds)
        self._add_child("DO-IP-POWER-MODE-STATUS-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS, AR:DO-IP-SERVICE-NEEDS, and AR:DO-IP-POWER-MODE-STATUS-NEEDS contain no elements
        self._leave_child()

    def _write_do_ip_routing_activation_authentication_needs(
            self,
            elem: ar_element.DoIpRoutingActivationAuthenticationNeeds) -> None:
        """
        Writes complex type AR:DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DoIpRoutingActivationAuthenticationNeeds)
        self._add_child("DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:DO-IP-SERVICE-NEEDS contain no elements
        self._write_do_ip_routing_activation_authentication_needs_group(elem)
        self._leave_child()

    def _write_do_ip_routing_activation_authentication_needs_group(
            self,
            elem: ar_element.DoIpRoutingActivationAuthenticationNeeds) -> None:
        """
        Writes group AR:DO-IP-ROUTING-ACTIVATION-AUTHENTICATION-NEEDS
        """
        if elem.data_length_request is not None:
            self._add_content("DATA-LENGTH-REQUEST", str(elem.data_length_request))
        if elem.data_length_response is not None:
            self._add_content("DATA-LENGTH-RESPONSE", str(elem.data_length_response))
        if elem.routing_activation_type is not None:
            self._add_content("ROUTING-ACTIVATION-TYPE", elem.routing_activation_type)

    def _write_do_ip_routing_activation_confirmation_needs(
            self,
            elem: ar_element.DoIpRoutingActivationConfirmationNeeds) -> None:
        """
        Writes complex type AR:DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DoIpRoutingActivationConfirmationNeeds)
        self._add_child("DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:DO-IP-SERVICE-NEEDS contain no elements
        self._write_do_ip_routing_activation_confirmation_needs_group(elem)
        self._leave_child()

    def _write_do_ip_routing_activation_confirmation_needs_group(
            self,
            elem: ar_element.DoIpRoutingActivationConfirmationNeeds) -> None:
        """
        Writes group AR:DO-IP-ROUTING-ACTIVATION-CONFIRMATION-NEEDS
        """
        if elem.data_length_request is not None:
            self._add_content("DATA-LENGTH-REQUEST", str(elem.data_length_request))
        if elem.data_length_response is not None:
            self._add_content("DATA-LENGTH-RESPONSE", str(elem.data_length_response))
        if elem.routing_activation_type is not None:
            self._add_content("ROUTING-ACTIVATION-TYPE", elem.routing_activation_type)

    def _write_dtc_status_change_notification_needs(
            self,
            elem: ar_element.DtcStatusChangeNotificationNeeds) -> None:
        """
        Writes complex type AR:DTC-STATUS-CHANGE-NOTIFICATION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DtcStatusChangeNotificationNeeds)
        self._add_child("DTC-STATUS-CHANGE-NOTIFICATION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_dtc_status_change_notification_needs_group(elem)
        self._leave_child()

    def _write_dtc_status_change_notification_needs_group(
            self,
            elem: ar_element.DtcStatusChangeNotificationNeeds) -> None:
        """
        Writes group AR:DTC-STATUS-CHANGE-NOTIFICATION-NEEDS
        """
        if elem.notification_time is not None:
            self._add_content("NOTIFICATION-TIME", ar_enum.enum_to_xml(elem.notification_time))

    def _write_ecu_state_mgr_user_needs(self, elem: ar_element.EcuStateMgrUserNeeds) -> None:
        """
        Writes complex type AR:ECU-STATE-MGR-USER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.EcuStateMgrUserNeeds)
        self._add_child("ECU-STATE-MGR-USER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:ECU-STATE-MGR-USER-NEEDS contain no elements
        self._leave_child()

    def _write_error_tracer_needs(self, elem: ar_element.ErrorTracerNeeds) -> None:
        """
        Writes complex type AR:ERROR-TRACER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ErrorTracerNeeds)
        self._add_child("ERROR-TRACER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_error_tracer_needs_group(elem)
        self._leave_child()

    def _write_error_tracer_needs_group(self, elem: ar_element.ErrorTracerNeeds) -> None:
        """
        Writes group AR:ERROR-TRACER-NEEDS
        """
        if len(elem.traced_failures) > 0:
            self._add_child("TRACED-FAILURES")
            for failure in elem.traced_failures:
                if isinstance(failure, ar_element.DevelopmentError):
                    self._write_development_error(failure)
                elif isinstance(failure, ar_element.RuntimeError):
                    self._write_runtime_error(failure)
                elif isinstance(failure, ar_element.TransientFault):
                    self._write_transient_fault(failure)
                else:
                    raise NotImplementedError(f"Unsupported failure type: {type(failure)}")
            self._leave_child()

    def _write_function_inhibition_availability_needs(
            self,
            elem: ar_element.FunctionInhibitionAvailabilityNeeds) -> None:
        """
        Writes complex type AR:FUNCTION-INHIBITION-AVAILABILITY-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.FunctionInhibitionAvailabilityNeeds)
        self._add_child("FUNCTION-INHIBITION-AVAILABILITY-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_function_inhibition_availability_needs_group(elem)
        self._leave_child()

    def _write_function_inhibition_availability_needs_group(
            self,
            elem: ar_element.FunctionInhibitionAvailabilityNeeds) -> None:
        """
        Writes group AR:FUNCTION-INHIBITION-AVAILABILITY-NEEDS
        """
        if elem.controlled_fid_ref is not None:
            self._write_function_inhibition_needs_ref(elem.controlled_fid_ref, "CONTROLLED-FID-REF")

    def _write_function_inhibition_needs(
            self,
            elem: ar_element.FunctionInhibitionNeeds) -> None:
        """
        Writes complex type AR:FUNCTION-INHIBITION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.FunctionInhibitionNeeds)
        self._add_child("FUNCTION-INHIBITION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Group AR:FUNCTION-INHIBITION-NEEDS contains no elements
        self._leave_child()

    def _write_further_action_byte_needs(
            self,
            elem: ar_element.FurtherActionByteNeeds) -> None:
        """
        Writes complex type AR:FURTHER-ACTION-BYTE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.FurtherActionByteNeeds)
        self._add_child("FURTHER-ACTION-BYTE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:DO-IP-SERVICE-NEEDS and AR:FURTHER-ACTION-BYTE-NEEDS contain no elements
        self._leave_child()

    def _write_global_supervision_needs(self, elem: ar_element.GlobalSupervisionNeeds) -> None:
        """
        Writes complex type AR:GLOBAL-SUPERVISION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.GlobalSupervisionNeeds)
        self._add_child("GLOBAL-SUPERVISION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:GLOBAL-SUPERVISION-NEEDS contain no elements
        self._leave_child()

    def _write_hardware_test_needs(self, elem: ar_element.HardwareTestNeeds) -> None:
        """
        Writes complex type AR:HARDWARE-TEST-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.HardwareTestNeeds)
        self._add_child("HARDWARE-TEST-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:HARDWARE-TEST-NEEDS contain no elements
        self._leave_child()

    def _write_ids_mgr_custom_timestamp_needs(
            self,
            elem: ar_element.IdsMgrCustomTimestampNeeds) -> None:
        """
        Writes complex type AR:IDS-MGR-CUSTOM-TIMESTAMP-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.IdsMgrCustomTimestampNeeds)
        self._add_child("IDS-MGR-CUSTOM-TIMESTAMP-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:IDS-MGR-CUSTOM-TIMESTAMP-NEEDS contain no elements
        self._leave_child()

    def _write_ids_mgr_needs(self, elem: ar_element.IdsMgrNeeds) -> None:
        """
        Writes complex type AR:IDS-MGR-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.IdsMgrNeeds)
        self._add_child("IDS-MGR-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_ids_mgr_needs_group(elem)
        self._leave_child()

    def _write_ids_mgr_needs_group(self, elem: ar_element.IdsMgrNeeds) -> None:
        """
        Writes group AR:IDS-MGR-NEEDS
        """
        if elem.use_smart_sensor_api is not None:
            self._add_content("USE-SMART-SENSOR-API", self._format_boolean(elem.use_smart_sensor_api))

    def _write_indicator_status_needs(
            self,
            elem: ar_element.IndicatorStatusNeeds) -> None:
        """
        Writes complex type AR:INDICATOR-STATUS-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.IndicatorStatusNeeds)
        self._add_child("INDICATOR-STATUS-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_indicator_status_needs_group(elem)
        self._leave_child()

    def _write_indicator_status_needs_group(
            self,
            elem: ar_element.IndicatorStatusNeeds) -> None:
        """
        Writes group AR:INDICATOR-STATUS-NEEDS
        """
        if elem.type is not None:
            self._add_content("TYPE", ar_enum.enum_to_xml(elem.type))

    def _write_j1939_dcm_dm_19_support(self, elem: ar_element.J1939DcmDm19Support) -> None:
        """
        Writes complex type AR:J-1939-DCM-DM-19-SUPPORT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.J1939DcmDm19Support)
        self._add_child("J-1939-DCM-DM-19-SUPPORT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:J-1939-DCM-DM-19-SUPPORT contain no elements
        self._leave_child()

    def _write_j1939_rm_incoming_request_service_needs(
            self,
            elem: ar_element.J1939RmIncomingRequestServiceNeeds) -> None:
        """
        Writes complex type AR:J-1939-RM-INCOMING-REQUEST-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.J1939RmIncomingRequestServiceNeeds)
        self._add_child("J-1939-RM-INCOMING-REQUEST-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:J-1939-RM-INCOMING-REQUEST-SERVICE-NEEDS contain no elements
        self._leave_child()

    def _write_j1939_rm_outgoing_request_service_needs(
            self,
            elem: ar_element.J1939RmOutgoingRequestServiceNeeds) -> None:
        """
        Writes complex type AR:J-1939-RM-OUTGOING-REQUEST-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.J1939RmOutgoingRequestServiceNeeds)
        self._add_child("J-1939-RM-OUTGOING-REQUEST-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:J-1939-RM-OUTGOING-REQUEST-SERVICE-NEEDS contain no elements
        self._leave_child()

    def _write_nv_block_needs(
            self,
            elem: ar_element.NvBlockNeeds) -> None:
        """
        Writes complex type AR:NV-BLOCK-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.NvBlockNeeds)
        self._add_child("NV-BLOCK-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_nv_block_needs_group(elem)
        self._leave_child()

    def _write_nv_block_needs_group(
            self,
            elem: ar_element.NvBlockNeeds) -> None:
        """
        Writes group AR:NV-BLOCK-NEEDS
        """
        if elem.calc_ram_block_crc is not None:
            self._add_content("CALC-RAM-BLOCK-CRC", self._format_boolean(elem.calc_ram_block_crc))
        if elem.check_static_block_id is not None:
            self._add_content("CHECK-STATIC-BLOCK-ID", self._format_boolean(elem.check_static_block_id))
        if elem.cyclic_writing_period is not None:
            self._add_content("CYCLIC-WRITING-PERIOD", str(elem.cyclic_writing_period))
        if elem.n_data_sets is not None:
            self._add_content("N-DATA-SETS", str(elem.n_data_sets))
        if elem.n_rom_blocks is not None:
            self._add_content("N-ROM-BLOCKS", str(elem.n_rom_blocks))
        if elem.ram_block_status_control is not None:
            self._add_content("RAM-BLOCK-STATUS-CONTROL", ar_enum.enum_to_xml(elem.ram_block_status_control))
        if elem.readonly is not None:
            self._add_content("READONLY", self._format_boolean(elem.readonly))
        if elem.reliability is not None:
            self._add_content("RELIABILITY", ar_enum.enum_to_xml(elem.reliability))
        if elem.resistant_to_changed_sw is not None:
            self._add_content("RESISTANT-TO-CHANGED-SW", self._format_boolean(elem.resistant_to_changed_sw))
        if elem.restore_at_start is not None:
            self._add_content("RESTORE-AT-START", self._format_boolean(elem.restore_at_start))
        if elem.select_block_for_first_init_all is not None:
            self._add_content("SELECT-BLOCK-FOR-FIRST-INIT-ALL",
                              self._format_boolean(elem.select_block_for_first_init_all))
        if elem.store_at_shutdown is not None:
            self._add_content("STORE-AT-SHUTDOWN", self._format_boolean(elem.store_at_shutdown))
        if elem.store_cyclic is not None:
            self._add_content("STORE-CYCLIC", self._format_boolean(elem.store_cyclic))
        if elem.store_emergency is not None:
            self._add_content("STORE-EMERGENCY", self._format_boolean(elem.store_emergency))
        if elem.store_immediate is not None:
            self._add_content("STORE-IMMEDIATE", self._format_boolean(elem.store_immediate))
        if elem.store_on_change is not None:
            self._add_content("STORE-ON-CHANGE", self._format_boolean(elem.store_on_change))
        if elem.use_auto_validation_at_shut_down is not None:
            self._add_content("USE-AUTO-VALIDATION-AT-SHUT-DOWN",
                              self._format_boolean(elem.use_auto_validation_at_shut_down))
        if elem.use_crc_comp_mechanism is not None:
            self._add_content("USE-CRC-COMP-MECHANISM", self._format_boolean(elem.use_crc_comp_mechanism))
        if elem.write_only_once is not None:
            self._add_content("WRITE-ONLY-ONCE", self._format_boolean(elem.write_only_once))
        if elem.write_verification is not None:
            self._add_content("WRITE-VERIFICATION", self._format_boolean(elem.write_verification))
        if elem.writing_frequency is not None:
            self._add_content("WRITING-FREQUENCY", str(elem.writing_frequency))
        if elem.writing_priority is not None:
            self._add_content("WRITING-PRIORITY", ar_enum.enum_to_xml(elem.writing_priority))

    def _write_obd_control_service_needs(
            self,
            elem: ar_element.ObdControlServiceNeeds) -> None:
        """
        Writes complex type AR:OBD-CONTROL-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ObdControlServiceNeeds)
        self._add_child("OBD-CONTROL-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:OBD-CONTROL-SERVICE-NEEDS contains no elements
        self._leave_child()

    def _write_obd_info_service_needs(
            self,
            elem: ar_element.ObdInfoServiceNeeds) -> None:
        """
        Writes complex type AR:OBD-INFO-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ObdInfoServiceNeeds)
        self._add_child("OBD-INFO-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:OBD-INFO-SERVICE-NEEDS contains no elements
        self._leave_child()

    def _write_obd_monitor_service_needs(
            self,
            elem: ar_element.ObdMonitorServiceNeeds) -> None:
        """
        Writes complex type AR:OBD-MONITOR-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ObdMonitorServiceNeeds)
        self._add_child("OBD-MONITOR-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_obd_monitor_service_needs_group(elem)
        self._leave_child()

    def _write_obd_monitor_service_needs_group(
            self,
            elem: ar_element.ObdMonitorServiceNeeds) -> None:
        """
        Writes group AR:OBD-MONITOR-SERVICE-NEEDS
        """
        if elem.appl_data_type_ref is not None:
            self._write_application_data_type_ref(elem.appl_data_type_ref, "APPLICATION-DATA-TYPE-REF")
        if elem.event_needs_ref is not None:
            self._write_diagnostic_event_needs_ref(elem.event_needs_ref, "EVENT-NEEDS-REF")
        if elem.unit_and_scaling_id is not None:
            self._add_content("UNIT-AND-SCALING-ID", str(elem.unit_and_scaling_id))

    def _write_obd_pid_service_needs(
            self,
            elem: ar_element.ObdPidServiceNeeds) -> None:
        """
        Writes complex type AR:OBD-PID-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ObdPidServiceNeeds)
        self._add_child("OBD-PID-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:OBD-PID-SERVICE-NEEDS contains no elements
        self._leave_child()

    def _write_obd_ratio_denominator_needs(
            self,
            elem: ar_element.ObdRatioDenominatorNeeds) -> None:
        """
        Writes complex type AR:OBD-RATIO-DENOMINATOR-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ObdRatioDenominatorNeeds)
        self._add_child("OBD-RATIO-DENOMINATOR-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_obd_ratio_denominator_needs_group(elem)
        self._leave_child()

    def _write_obd_ratio_denominator_needs_group(
            self,
            elem: ar_element.ObdRatioDenominatorNeeds) -> None:
        """
        Writes group AR:OBD-RATIO-DENOMINATOR-NEEDS
        """
        if elem.denominator_condition is not None:
            self._add_content("DENOMINATOR-CONDITION", ar_enum.enum_to_xml(elem.denominator_condition))

    def _write_obd_ratio_service_needs(
            self,
            elem: ar_element.ObdRatioServiceNeeds) -> None:
        """
        Writes complex type AR:OBD-RATIO-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ObdRatioServiceNeeds)
        self._add_child("OBD-RATIO-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        self._write_obd_ratio_service_needs_group(elem)
        self._leave_child()

    def _write_obd_ratio_service_needs_group(
            self,
            elem: ar_element.ObdRatioServiceNeeds) -> None:
        """
        Writes group AR:OBD-RATIO-SERVICE-NEEDS
        """
        if elem.connection_type is not None:
            self._add_content("CONNECTION-TYPE", ar_enum.enum_to_xml(elem.connection_type))
        if elem.rate_based_monitored_event_ref is not None:
            self._write_diagnostic_event_needs_ref(elem.rate_based_monitored_event_ref,
                                                   "RATE-BASED-MONITORED-EVENT-REF")
        if elem.used_fid_ref is not None:
            self._write_function_inhibition_needs_ref(elem.used_fid_ref, "USED-FID-REF")

    def _write_possible_error_reaction(self, elem: ar_element.PossibleErrorReaction) -> None:
        """
        Writes complex type AR:POSSIBLE-ERROR-REACTION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.PossibleErrorReaction)
        self._add_child("POSSIBLE-ERROR-REACTION")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_possible_error_reaction_group(elem)
        self._leave_child()

    def _write_possible_error_reaction_group(self, elem: ar_element.PossibleErrorReaction) -> None:
        """
        Writes group AR:POSSIBLE-ERROR-REACTION
        """
        if elem.reaction_code is not None:
            self._add_content("REACTION-CODE", str(elem.reaction_code))

    def _write_runtime_error(self, elem: ar_element.RuntimeError) -> None:
        """
        Writes complex type AR:RUNTIME-ERROR
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.RuntimeError)
        self._add_child("RUNTIME-ERROR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_traced_failure_group(elem)
        self._leave_child()

    def _write_secure_on_board_communication_needs(
            self,
            elem: ar_element.SecureOnBoardCommunicationNeeds) -> None:
        """
        Writes complex type AR:SECURE-ON-BOARD-COMMUNICATION-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SecureOnBoardCommunicationNeeds)
        self._add_child("SECURE-ON-BOARD-COMMUNICATION-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_secure_on_board_communication_needs_group(elem)
        self._leave_child()

    def _write_secure_on_board_communication_needs_group(
            self,
            elem: ar_element.SecureOnBoardCommunicationNeeds) -> None:
        """
        Writes group AR:SECURE-ON-BOARD-COMMUNICATION-NEEDS
        """
        if elem.verification_status_indication_mode is not None:
            self._add_content("VERIFICATION-STATUS-INDICATION-MODE",
                              ar_enum.enum_to_xml(elem.verification_status_indication_mode))

    def _write_supervised_entity_checkpoint_needs(
            self,
            elem: ar_element.SupervisedEntityCheckpointNeeds) -> None:
        """
        Writes complex type AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SupervisedEntityCheckpointNeeds)
        self._add_child("SUPERVISED-ENTITY-CHECKPOINT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS contain no elements
        self._leave_child()

    def _write_supervised_entity_checkpoint_needs_ref_conditional(
            self,
            elem: ar_element.SupervisedEntityCheckpointNeedsRefConditional) -> None:
        """
        Writes complex type AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF-CONDITIONAL
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SupervisedEntityCheckpointNeedsRefConditional)
        self._add_child("SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF-CONDITIONAL")
        self._write_supervised_entity_checkpoint_needs_ref_conditional_group(elem)
        self._leave_child()

    def _write_supervised_entity_checkpoint_needs_ref_conditional_group(
            self,
            elem: ar_element.SupervisedEntityCheckpointNeedsRefConditional) -> None:
        """
        Writes group AR:SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF-CONDITIONAL
        """
        if elem.checkpoint_ref is not None:
            self._write_supervised_entity_checkpoint_needs_ref(elem.checkpoint_ref,
                                                               "SUPERVISED-ENTITY-CHECKPOINT-NEEDS-REF")

    def _write_supervised_entity_needs(self, elem: ar_element.SupervisedEntityNeeds) -> None:
        """
        Writes complex type AR:SUPERVISED-ENTITY-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SupervisedEntityNeeds)
        self._add_child("SUPERVISED-ENTITY-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_supervised_entity_needs_group(elem)
        self._leave_child()

    def _write_supervised_entity_needs_group(self, elem: ar_element.SupervisedEntityNeeds) -> None:
        """
        Writes group AR:SUPERVISED-ENTITY-NEEDS
        """
        if elem.activate_at_start is not None:
            self._add_content("ACTIVATE-AT-START", self._format_boolean(elem.activate_at_start))
        if len(elem.checkpoints) > 0:
            self._add_child("CHECKPOINTSS")
            for item in elem.checkpoints:
                self._write_supervised_entity_checkpoint_needs_ref_conditional(item)
            self._leave_child()
        if elem.enable_deactivation is not None:
            self._add_content("ENABLE-DEACTIVATION", self._format_boolean(elem.enable_deactivation))
        if elem.expected_alive_cycle is not None:
            self._add_content("EXPECTED-ALIVE-CYCLE", self._format_number(elem.expected_alive_cycle))
        if elem.max_alive_cycle is not None:
            self._add_content("MAX-ALIVE-CYCLE", self._format_number(elem.max_alive_cycle))
        if elem.min_alive_cycle is not None:
            self._add_content("MIN-ALIVE-CYCLE", self._format_number(elem.min_alive_cycle))
        if elem.tolerated_failed_cycles is not None:
            self._add_content("TOLERATED-FAILED-CYCLES", str(elem.tolerated_failed_cycles))

    def _write_sync_time_base_mgr_user_needs(
            self,
            elem: ar_element.SyncTimeBaseMgrUserNeeds) -> None:
        """
        Writes complex type AR:SYNC-TIME-BASE-MGR-USER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SyncTimeBaseMgrUserNeeds)
        self._add_child("SYNC-TIME-BASE-MGR-USER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:SYNC-TIME-BASE-MGR-USER-NEEDS contain no elements
        self._leave_child()

    def _write_transient_fault(self, elem: ar_element.TransientFault) -> None:
        """
        Writes complex type AR:TRANSIENT-FAULT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.TransientFault)
        self._add_child("TRANSIENT-FAULT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_traced_failure_group(elem)
        self._write_transient_fault_group(elem)
        self._leave_child()

    def _write_transient_fault_group(self, elem: ar_element.TransientFault) -> None:
        """
        Writes group AR:TRANSIENT-FAULT
        """
        if len(elem.possible_error_reactions) > 0:
            self._add_child("POSSIBLE-ERROR-REACTIONS")
            for item in elem.possible_error_reactions:
                self._write_possible_error_reaction(item)
            self._leave_child()

    def _write_vendor_specific_service_needs(self, elem: ar_element.VendorSpecificServiceNeeds) -> None:
        """
        Writes complex type AR:VENDOR-SPECIFIC-SERVICE-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.VendorSpecificServiceNeeds)
        self._add_child("VENDOR-SPECIFIC-SERVICE-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:VENDOR-SPECIFIC-SERVICE-NEEDS contain no elements
        self._leave_child()

    def _write_v2x_data_manager_needs(self, elem: ar_element.V2xDataManagerNeeds) -> None:
        """
        Writes complex type AR:V-2-X-DATA-MANAGER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.V2xDataManagerNeeds)
        self._add_child("V-2-X-DATA-MANAGER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:V-2-X-DATA-MANAGER-NEEDS contain no elements
        self._leave_child()

    def _write_v2x_fac_user_needs(self, elem: ar_element.V2xFacUserNeeds) -> None:
        """
        Writes complex type AR:V-2-X-FAC-USER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.V2xFacUserNeeds)
        self._add_child("V-2-X-FAC-USER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:V-2-X-FAC-USER-NEEDS contain no elements
        self._leave_child()

    def _write_v2x_m_user_needs(self, elem: ar_element.V2xMUserNeeds) -> None:
        """
        Writes complex type AR:V-2-X-M-USER-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.V2xMUserNeeds)
        self._add_child("V-2-X-M-USER-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        # Groups AR:SERVICE-NEEDS and AR:V-2-X-M-USER-NEEDS contain no elements
        self._leave_child()

    def _write_warning_indicator_requested_bit_needs(
            self,
            elem: ar_element.WarningIndicatorRequestedBitNeeds) -> None:
        """
        Writes complex type AR:WARNING-INDICATOR-REQUESTED-BIT-NEEDS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.WarningIndicatorRequestedBitNeeds)
        self._add_child("WARNING-INDICATOR-REQUESTED-BIT-NEEDS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_diagnostic_capability_element_group(elem)
        # Group AR:WARNING-INDICATOR-REQUESTED-BIT-NEEDS contains no elements
        self._leave_child()

    def _write_abstract_access_point(self, elem: ar_element.AbstractAccessPoint) -> None:
        """
        Writes group AR:ABSTRACT-ACCESS-POINT
        """
        if elem.return_value_provision is not None:
            self._add_content("RETURN-VALUE-PROVISION", ar_enum.enum_to_xml(elem.return_value_provision))

    def _write_server_call_point(self, elem: ar_element.ServerCallPoint) -> None:
        """
        Writes group AR:SERVER-CALL-POINT
        """
        if elem.operation is not None:
            self._write_r_operation_in_atomic_swc_instance_ref(elem.operation)
        if elem.timeout is not None:
            self._add_content("TIMEOUT", self._format_number(elem.timeout))

    def _write_async_server_call_point(self, elem: ar_element.AsynchronousServerCallPoint) -> None:
        """
        Writes complex type AR:ASYNCHRONOUS-SERVER-CALL-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.AsynchronousServerCallPoint)
        self._add_child("ASYNCHRONOUS-SERVER-CALL-POINT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        self._write_server_call_point(elem)
        self._leave_child()

    def _write_sync_server_call_point(self, elem: ar_element.SynchronousServerCallPoint) -> None:
        """
        Writes complex type AR:SYNCHRONOUS-SERVER-CALL-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SynchronousServerCallPoint)
        self._add_child("SYNCHRONOUS-SERVER-CALL-POINT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        self._write_server_call_point(elem)
        if elem.called_from_within_exclusive_area is not None:
            self._write_exclusive_area_nesting_order_ref(elem.called_from_within_exclusive_area,
                                                         "CALLED-FROM-WITHIN-EXCLUSIVE-AREA-REF")
        self._leave_child()

    def _write_async_server_call_result_point(self, elem: ar_element.AsynchronousServerCallResultPoint) -> None:
        """
        Writes complex type AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.AsynchronousServerCallResultPoint)
        self._add_child("ASYNCHRONOUS-SERVER-CALL-RESULT-POINT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        self._write_async_server_call_result_point_group(elem)
        self._leave_child()

    def _write_async_server_call_result_point_group(self, elem: ar_element.AsynchronousServerCallResultPoint) -> None:
        """
        Writes group AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT
        """
        if elem.async_server_call_point is not None:
            self._write_async_server_call_point_ref(elem.async_server_call_point)

    def _write_external_triggering_point_ident(self, elem: ar_element.ExternalTriggeringPointIdent) -> None:
        """
        Writes complex type AR:EXTERNAL-TRIGGERING-POINT-IDENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ExternalTriggeringPointIdent)
        self._add_child("IDENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        self._leave_child()

    def _write_external_triggering_point(self, elem: ar_element.ExternalTriggeringPoint) -> None:
        """
        Writes complex type AR:EXTERNAL-TRIGGERING-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ExternalTriggeringPoint)
        tag = "EXTERNAL-TRIGGERING-POINT"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.ident is not None:
                self._write_external_triggering_point_ident(elem.ident)
            if elem.trigger is not None:
                self._write_p_trigger_in_atomic_swc_instance_ref(elem.trigger, "TRIGGER-IREF")
            self._leave_child()

    def _write_internal_triggering_point(self, elem: ar_element.InternalTriggeringPoint) -> None:
        """
        Writes complex type AR:INTERNAL-TRIGGERING-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.InternalTriggeringPoint)
        self._add_child("INTERNAL-TRIGGERING-POINT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        if elem.sw_impl_policy is not None:
            self._add_content("SW-IMPL-POLICY", ar_enum.enum_to_xml(elem.sw_impl_policy))
        self._leave_child()

    def _write_mode_access_point_ident(self, elem: ar_element.ModeAccessPointIdent) -> None:
        """
        Writes complex type AR:MODE-ACCESS-POINT-IDENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeAccessPointIdent)
        self._add_child("IDENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        self._leave_child()

    def _write_mode_access_point(self, elem: ar_element.ModeAccessPoint) -> None:
        """
        Writes complex type AR:MODE-ACCESS-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeAccessPoint)
        tag = "MODE-ACCESS-POINT"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.ident is not None:
                self._write_mode_access_point_ident(elem.ident)
            if elem.mode_group is not None:
                self._add_child("MODE-GROUP-IREF")
                if isinstance(elem.mode_group, ar_element.PModeGroupInAtomicSwcInstanceRef):
                    self._write_p_mode_group_in_atomic_swc_instance_ref(elem.mode_group,
                                                                        "P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF")
                elif isinstance(elem.mode_group, ar_element.RModeGroupInAtomicSwcInstanceRef):
                    self._write_r_mode_group_in_atomic_swc_instance_ref(elem.mode_group)
                else:
                    raise TypeError(f"mode_group: Invalid type: {str(type(elem.mode_group))}")
                self._leave_child()
            self._leave_child()

    def _write_mode_switch_point(self, elem: ar_element.ModeSwitchPoint) -> None:
        """
        Writes complex type AR:MODE-SWITCH-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeSwitchPoint)
        self._add_child("MODE-SWITCH-POINT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        if elem.mode_group is not None:
            self._write_p_mode_group_in_atomic_swc_instance_ref(elem.mode_group, 'MODE-GROUP-IREF')
        self._leave_child()

    def _write_parameter_in_atomic_swc_type_instance_ref(self,
                                                         elem: ar_element.ParameterInAtomicSwcTypeInstanceRef
                                                         ) -> None:
        """
        Writes complex type AR:PARAMETER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ParameterInAtomicSwcTypeInstanceRef)
        tag = "AUTOSAR-PARAMETER-IREF"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.port_prototype is not None:
                self._write_port_prototype_ref(elem.port_prototype, "PORT-PROTOTYPE-REF")
            if elem.root_parameter_data_prototype is not None:
                self._write_data_prototype_ref(elem.root_parameter_data_prototype, "ROOT-PARAMETER-DATA-PROTOTYPE-REF")
            if elem.context_data_prototype is not None:
                self._write_appl_composite_element_data_proto_ref(elem.context_data_prototype,
                                                                  "CONTEXT-DATA-PROTOTYPE-REF")
            if elem.target_data_prototype is not None:
                self._write_data_prototype_ref(elem.target_data_prototype, "TARGET-DATA-PROTOTYPE-REF")
            self._leave_child()

    def _write_autosar_parameter_ref(self, elem: ar_element.AutosarParameterRef, tag: str) -> None:
        """
        Writes complex type AR:AUTOSAR-PARAMETER-REF
        Multi-tagged: True
        """
        assert isinstance(elem, ar_element.AutosarParameterRef)
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.autosar_parameter is not None:
                self._write_parameter_in_atomic_swc_type_instance_ref(elem.autosar_parameter)
            if elem.local_parameter is not None:
                self._write_data_prototype_ref(elem.local_parameter, "LOCAL-PARAMETER-REF")
            self._leave_child()

    def _write_parameter_access(self, elem: ar_element.ParameterAccess) -> None:
        """
        Writes complex type AR:PARAMETER-ACCESS
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ParameterAccess)
        self._add_child("PARAMETER-ACCESS")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_abstract_access_point(elem)
        self._write_parameter_access_group(elem)
        self._leave_child()

    def _write_parameter_access_group(self, elem: ar_element.ParameterAccess) -> None:
        """
        Writes group AR:PARAMETER-ACCESS
        """
        if elem.accessed_parameter is not None:
            self._write_autosar_parameter_ref(elem.accessed_parameter, "ACCESSED-PARAMETER")
        if elem.sw_data_def_props is not None:
            self._write_sw_data_def_props(elem.sw_data_def_props, "SW-DATA-DEF-PROPS")

    def _write_wait_point(self, elem: ar_element.WaitPoint) -> None:
        """
        Writes complex type AR:WAIT-POINT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.WaitPoint)
        self._add_child("WAIT-POINT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_wait_point_group(elem)
        self._leave_child()

    def _write_wait_point_group(self, elem: ar_element.WaitPoint) -> None:
        """
        Writes group AR:WAIT-POINT
        """
        if elem.timeout is not None:
            self._add_content("TIMEOUT", self._format_number(elem.timeout))
        if elem.trigger is not None:
            self._write_rte_event_ref(elem.trigger, "TRIGGER-REF")

    def _write_executable_entity(self, elem: ar_element.ExecutableEntity) -> None:
        """
        Writes group AR:EXECUTABLE-ENTITY
        """
        if elem.activation_reasons:
            self._add_child("ACTIVATION-REASONS")
            for activation_reason in elem.activation_reasons:
                self._write_executable_entity_activation_reason(activation_reason)
            self._leave_child()
        if elem.can_enter_leave:
            if not isinstance(self.schema_version, int):
                raise RuntimeError("Schema version is not set, unable to proceed")
            if self.schema_version < 50:
                self._add_child("CAN-ENTER-EXCLUSIVE-AREA-REFS")
                for child_elem in elem.can_enter_leave:
                    self._write_exclusive_area_ref(child_elem.exclusive_area,
                                                   "CAN-ENTER-EXCLUSIVE-AREA-REF")
                self._leave_child()
            else:
                self._add_child("CAN-ENTERS")
                for child_elem in elem.can_enter_leave:
                    self._write_exclusive_area_ref_conditional(child_elem)
                self._leave_child()
        if elem.exclusive_area_nesting_order:
            self._add_child("EXCLUSIVE-AREA-NESTING-ORDER-REFS")
            for nesting_order_ref in elem.exclusive_area_nesting_order:
                self._write_exclusive_area_nesting_order_ref(nesting_order_ref,
                                                             "EXCLUSIVE-AREA-NESTING-ORDER-REF")
            self._leave_child()
        if elem.minimum_start_interval is not None:
            self._add_content("MINIMUM-START-INTERVAL", self._format_number(elem.minimum_start_interval))
        if elem.reentrancy_level is not None:
            self._add_content("REENTRANCY-LEVEL", ar_enum.enum_to_xml(elem.reentrancy_level))
        if elem.runs_insides:
            if not isinstance(self.schema_version, int):
                raise RuntimeError("Schema version is not set, unable to proceed")
            if self.schema_version < 50:
                self._add_child("RUNS-INSIDE-EXCLUSIVE-AREA-REFS")
                for child_elem in elem.runs_insides:
                    self._write_exclusive_area_ref(child_elem.exclusive_area,
                                                   "RUNS-INSIDE-EXCLUSIVE-AREA-REF")
                self._leave_child()
            else:
                self._add_child("RUNS-INSIDES")
                for child_elem in elem.runs_insides:
                    self._write_exclusive_area_ref_conditional(child_elem)
                self._leave_child()
        if elem.sw_addr_method is not None:
            self._write_sw_addr_method_ref(elem.sw_addr_method)

    def _write_runnable_entity(self, elem: ar_element.RunnableEntity) -> None:
        """
        Writes complex type AR:RUNNABLE-ENTITY
        Multi-tagged: False

        This is in early stage, most will be implemented later
        """
        assert isinstance(elem, ar_element.RunnableEntity)
        self._add_child("RUNNABLE-ENTITY")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_executable_entity(elem)
        self._write_runnable_entity_group(elem)
        self._leave_child()

    def _write_runnable_entity_group(self, elem: ar_element.RunnableEntity) -> None:
        """
        Writes group AR:RUNNABLE-ENTITY
        """
        if len(elem.argument) > 0:
            self._add_child("ARGUMENTS")
            for argument in elem.argument:
                self._write_runnable_entity_argument(argument)
            self._leave_child()
        if len(elem.async_server_call_result_point) > 0:
            self._add_child("ASYNCHRONOUS-SERVER-CALL-RESULT-POINTS")
            for async_server_call_result_point in elem.async_server_call_result_point:
                self._write_async_server_call_result_point(async_server_call_result_point)
            self._leave_child()
        if elem.can_be_invoked_concurrently is not None:
            self._add_content("CAN-BE-INVOKED-CONCURRENTLY", self._format_boolean(elem.can_be_invoked_concurrently))
        if len(elem.data_read_access) > 0:
            self._add_child("DATA-READ-ACCESSS")
            for child in elem.data_read_access:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()
        if len(elem.data_receive_point_by_argument) > 0:
            self._add_child("DATA-RECEIVE-POINT-BY-ARGUMENTS")
            for child in elem.data_receive_point_by_argument:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()
        if len(elem.data_receive_point_by_value) > 0:
            self._add_child("DATA-RECEIVE-POINT-BY-VALUES")
            for child in elem.data_receive_point_by_value:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()
        if len(elem.data_send_point) > 0:
            self._add_child("DATA-SEND-POINTS")
            for child in elem.data_send_point:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()
        if len(elem.data_write_access) > 0:
            self._add_child("DATA-WRITE-ACCESSS")
            for child in elem.data_write_access:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()
        if len(elem.external_triggering_point) > 0:
            self._add_child("EXTERNAL-TRIGGERING-POINTS")
            for child in elem.external_triggering_point:
                self._write_external_triggering_point(child)
            self._leave_child()
        if len(elem.internal_triggering_point) > 0:
            self._add_child("INTERNAL-TRIGGERING-POINTS")
            for child in elem.internal_triggering_point:
                self._write_internal_triggering_point(child)
            self._leave_child()
        if len(elem.mode_access_point) > 0:
            self._add_child("MODE-ACCESS-POINTS")
            for child in elem.mode_access_point:
                self._write_mode_access_point(child)
            self._leave_child()
        if len(elem.mode_switch_point) > 0:
            self._add_child("MODE-SWITCH-POINTS")
            for child in elem.mode_switch_point:
                self._write_mode_switch_point(child)
            self._leave_child()
        if len(elem.parameter_access) > 0:
            self._add_child("PARAMETER-ACCESSS")
            for child in elem.parameter_access:
                self._write_parameter_access(child)
            self._leave_child()
        if len(elem.read_local_variable) > 0:
            self._add_child("READ-LOCAL-VARIABLES")
            for child in elem.read_local_variable:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()
        if len(elem.server_call_point) > 0:
            self._add_child("SERVER-CALL-POINTS")
            for child in elem.server_call_point:
                if isinstance(child, ar_element.AsynchronousServerCallPoint):
                    self._write_async_server_call_point(child)
                else:
                    self._write_sync_server_call_point(child)
            self._leave_child()
        if elem.symbol is not None:
            self._add_content("SYMBOL", str(elem.symbol))
        if len(elem.wait_point) > 0:
            self._add_child("WAIT-POINTS")
            for child in elem.wait_point:
                self._write_wait_point(child)
            self._leave_child()
        if len(elem.write_local_variable) > 0:
            self._add_child("WRITTEN-LOCAL-VARIABLES")
            for child in elem.write_local_variable:
                self._write_variable_access(child, "VARIABLE-ACCESS")
            self._leave_child()

    def _write_rte_event_group(self, elem: ar_element.RteEvent) -> None:
        """
        Writes group AR:RTE-EVENT
        """
        if elem.disabled_modes:
            self._add_child("DISABLED-MODE-IREFS")
            for disabled_mode in elem.disabled_modes:
                self._write_r_mode_in_atomic_swc_instance_ref(disabled_mode, "DISABLED-MODE-IREF")
            self._leave_child()
        if elem.start_on_event is not None:
            self._write_runnable_entity_ref(elem.start_on_event, "START-ON-EVENT-REF")

    def _write_async_server_call_returns_event(self, elem: ar_element.AsynchronousServerCallReturnsEvent) -> None:
        """
        Writes complex type AR:ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.AsynchronousServerCallReturnsEvent)
        self._add_child("ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.event_source is not None:
            self._write_async_server_call_result_point_ref(elem.event_source)
        self._leave_child()

    def _write_background_event(self, elem: ar_element.BackgroundEvent) -> None:
        """
        Writes complex type AR:BACKGROUND-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.BackgroundEvent)
        self._add_child("BACKGROUND-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        self._leave_child()

    def _write_data_receive_error_event(self, elem: ar_element.DataReceiveErrorEvent) -> None:
        """
        Writes complex type AR:DATA-RECEIVE-ERROR-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DataReceiveErrorEvent)
        self._add_child("DATA-RECEIVE-ERROR-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.data is not None:
            self._write_r_variable_in_atomic_swc_instance_ref(elem.data)
        self._leave_child()

    def _write_data_received_event(self, elem: ar_element.DataReceivedEvent) -> None:
        """
        Writes complex type AR:DATA-RECEIVED-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DataReceivedEvent)
        self._add_child("DATA-RECEIVED-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.data is not None:
            self._write_r_variable_in_atomic_swc_instance_ref(elem.data)
        self._leave_child()

    def _write_data_send_completed_event(self, elem: ar_element.DataSendCompletedEvent) -> None:
        """
        Writes complex type AR:DATA-SEND-COMPLETED-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DataSendCompletedEvent)
        self._add_child("DATA-SEND-COMPLETED-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.event_source is not None:
            self._write_variable_access_ref(elem.event_source, "EVENT-SOURCE-REF")
        self._leave_child()

    def _write_data_write_completed_event(self, elem: ar_element.DataWriteCompletedEvent) -> None:
        """
        Writes complex type AR:DATA-WRITE-COMPLETED-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.DataWriteCompletedEvent)
        self._add_child("DATA-WRITE-COMPLETED-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.event_source is not None:
            self._write_variable_access_ref(elem.event_source, "EVENT-SOURCE-REF")
        self._leave_child()

    def _write_external_trigger_occured_event(self, elem: ar_element.ExternalTriggerOccurredEvent) -> None:
        """
        Writes complex type AR:EXTERNAL-TRIGGER-OCCURRED-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ExternalTriggerOccurredEvent)
        self._add_child("EXTERNAL-TRIGGER-OCCURRED-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.trigger is not None:
            self._write_r_trigger_in_atomic_swc_instance_ref(elem.trigger, "TRIGGER-IREF")
        self._leave_child()

    def _write_init_event(self, elem: ar_element.InitEvent) -> None:
        """
        Writes complex type AR:INIT-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.InitEvent)
        self._add_child("INIT-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        self._leave_child()

    def _write_internal_trigger_occured_event(self, elem: ar_element.InternalTriggerOccurredEvent) -> None:
        """
        Writes complex type AR:INTERNAL-TRIGGER-OCCURRED-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.InternalTriggerOccurredEvent)
        self._add_child("INTERNAL-TRIGGER-OCCURRED-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.event_source is not None:
            self._write_internal_triggering_point_ref(elem.event_source)
        self._leave_child()

    def _write_mode_switched_ack_event(self, elem: ar_element.ModeSwitchedAckEvent) -> None:
        """
        Writes complex type AR:MODE-SWITCHED-ACK-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.ModeSwitchedAckEvent)
        self._add_child("MODE-SWITCHED-ACK-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.event_source is not None:
            self._write_mode_switch_point_ref(elem.event_source)
        self._leave_child()

    def _write_operation_invoked_event(self, elem: ar_element.OperationInvokedEvent) -> None:
        """
        Writes complex type AR:OPERATION-INVOKED-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.OperationInvokedEvent)
        self._add_child("OPERATION-INVOKED-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.operation is not None:
            self._write_p_operation_in_atomic_swc_instance_ref(elem.operation)
        self._leave_child()

    def _write_swc_mode_manager_error_event(self, elem: ar_element.SwcModeManagerErrorEvent) -> None:
        """
        Writes complex type AR:SWC-MODE-MANAGER-ERROR-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwcModeManagerErrorEvent)
        self._add_child("SWC-MODE-MANAGER-ERROR-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.mode_group is not None:
            self._write_p_mode_group_in_atomic_swc_instance_ref(elem.mode_group, "MODE-GROUP-IREF")
        self._leave_child()

    def _write_swc_mode_switch_event(self, elem: ar_element.SwcModeSwitchEvent) -> None:
        """
        Writes complex type AR:SWC-MODE-SWITCH-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.SwcModeSwitchEvent)
        self._add_child("SWC-MODE-SWITCH-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        self._write_swc_mode_switch_event_group(elem)
        self._leave_child()

    def _write_swc_mode_switch_event_group(self, elem: ar_element.SwcModeSwitchEvent) -> None:
        """
        Writes group AR:SWC-MODE-SWITCH-EVENT
        """
        if elem.activation is not None:
            self._add_content("ACTIVATION", ar_enum.enum_to_xml(elem.activation))
        if elem.mode is not None:
            self._add_child("MODE-IREFS")
            if isinstance(elem.mode, tuple):
                self._write_r_mode_in_atomic_swc_instance_ref(elem.mode[0], "MODE-IREF")
                self._write_r_mode_in_atomic_swc_instance_ref(elem.mode[1], "MODE-IREF")
            else:
                self._write_r_mode_in_atomic_swc_instance_ref(elem.mode, "MODE-IREF")
            self._leave_child()

    def _write_timing_event(self, elem: ar_element.TimingEvent) -> None:
        """
        Writes complex type AR:TIMING-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.TimingEvent)
        self._add_child("TIMING-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        if elem.offset is not None:
            self._add_content("OFFSET", self._format_number(elem.offset))
        if elem.period is not None:
            self._add_content("PERIOD", self._format_number(elem.period))
        self._leave_child()

    def _write_transformer_hard_error_event(self, elem: ar_element.TransformerHardErrorEvent) -> None:
        """
        Writes complex type AR:TRANSFORMER-HARD-ERROR-EVENT
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.TransformerHardErrorEvent)
        self._add_child("TRANSFORMER-HARD-ERROR-EVENT")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_rte_event_group(elem)
        self._write_transformer_hard_error_event_group(elem)
        self._leave_child()

    def _write_transformer_hard_error_event_group(self, elem: ar_element.TransformerHardErrorEvent) -> None:
        if elem.operation is not None:
            self._write_p_operation_in_atomic_swc_instance_ref(elem.operation)
        if elem.required_trigger is not None:
            self._write_r_trigger_in_atomic_swc_instance_ref(elem.required_trigger, "REQUIRED-TRIGGER-IREF")

    def _write_port_defined_argument_value(self, elem: ar_element.PortDefinedArgumentValue) -> None:
        """
        Writes complex type AR:PORT-DEFINED-ARGUMENT-VALUE
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.PortDefinedArgumentValue)
        tag = "PORT-DEFINED-ARGUMENT-VALUE"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.value is not None:
                self._add_child("VALUE")
                self._write_value_specification_element(elem.value)
                self._leave_child()
            if elem.value_type is not None:
                self._write_impl_data_type_ref(elem.value_type, "VALUE-TYPE-TREF")
            self._leave_child()

    def _write_communication_buffer_locking(self, elem: ar_element.CommunicationBufferLocking) -> None:
        """
        Writes complex type AR:COMMUNICATION-BUFFER-LOCKING
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.CommunicationBufferLocking)
        tag = "COMMUNICATION-BUFFER-LOCKING"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            if elem.support_buffer_locking is not None:
                self._add_content("SUPPORT-BUFFER-LOCKING", ar_enum.enum_to_xml(elem.support_buffer_locking))
            self._leave_child()

    def _write_port_api_option(self, elem: ar_element.PortApiOption) -> None:
        """
        Writes complex type AR:PORT-API-OPTION
        Multi-tagged: False
        """
        assert isinstance(elem, ar_element.PortApiOption)
        tag = "PORT-API-OPTION"
        if elem.is_empty:
            self._add_content(tag)
        else:
            self._add_child(tag)
            self._write_port_api_option_group(elem)
            self._leave_child()

    def _write_port_api_option_group(self, elem: ar_element.PortApiOption) -> None:
        """
        Writes group AR:PORT-API-OPTION
        """
        if elem.enable_take_address is not None:
            self._add_content("ENABLE-TAKE-ADDRESS", self._format_boolean(elem.enable_take_address))
        if elem.error_handling is not None:
            self._add_content("ERROR-HANDLING", ar_enum.enum_to_xml(elem.error_handling))
        if elem.indirect_api is not None:
            self._add_content("INDIRECT-API", self._format_boolean(elem.indirect_api))
        if len(elem.port_arg_values) > 0:
            self._add_child("PORT-ARG-VALUES")
            for port_arg_value in elem.port_arg_values:
                self._write_port_defined_argument_value(port_arg_value)
            self._leave_child()
        if elem.port is not None:
            self._write_port_prototype_ref(elem.port, "PORT-REF")
        if len(elem.supported_features) > 0:
            self._add_child("SUPPORTED-FEATURES")
            for supported_feature in elem.supported_features:
                if isinstance(supported_feature, ar_element.CommunicationBufferLocking):
                    self._write_communication_buffer_locking(supported_feature)
                else:
                    raise NotImplementedError(str(type(supported_feature)))
            self._leave_child()
        if elem.transformer_status_forwarding is not None:
            self._add_content("TRANSFORMER-STATUS-FORWARDING", ar_enum.enum_to_xml(elem.transformer_status_forwarding))

    def _write_exclusive_area(self, elem: ar_element.ExclusiveArea) -> None:
        """
        Writes complex type AR:EXCLUSIVE-AREA
        Multi-tagged: False
        """
        self._add_child("EXCLUSIVE-AREA")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._leave_child()

    def _write_exclusive_area_nesting_order(self, elem: ar_element.ExclusiveAreaNestingOrder) -> None:
        """
        Writes complex type AR:EXCLUSIVE-AREA-NESTING-ORDER
        Multi-tagged: False
        """
        self._add_child("EXCLUSIVE-AREA-NESTING-ORDER")
        self._write_referrable(elem)
        self._write_exclusive_area_nesting_order_group(elem)
        self._leave_child()

    def _write_exclusive_area_nesting_order_group(self, elem: ar_element.ExclusiveAreaNestingOrder) -> None:
        """
        Writes group AR:EXCLUSIVE-AREA-NESTING-ORDER
        """
        if elem.exclusive_area:
            self._add_child("EXCLUSIVE-AREA-REFS")
            for ref in elem.exclusive_area:
                self._write_exclusive_area_ref(ref, "EXCLUSIVE-AREA-REF")
            self._leave_child()

    def _write_swc_internal_behavior(self, elem: ar_element.SwcInternalBehavior) -> None:
        """
        Writes complex type AR:SWC-INTERNAL-BEHAVIOR
        Multi-tagged: False
        """
        self._add_child("SWC-INTERNAL-BEHAVIOR")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_internal_behavior_group(elem)
        self._write_swc_internal_behavior_group(elem)
        self._leave_child()

    def _write_internal_behavior_group(self, elem: ar_element.InternalBehavior) -> None:
        """
        Writes group AR:INTERNAL-BEHAVIOR
        """
        if elem.constant_memory:
            self._add_child("CONSTANT-MEMORYS")
            for item in elem.constant_memory:
                self._write_parameter_data_prototype(item, "PARAMETER-DATA-PROTOTYPE")
            self._leave_child()
        if elem.constant_value_mapping:
            self._add_child("CONSTANT-VALUE-MAPPING-REFS")
            for mapping_set in elem.constant_value_mapping:
                self._write_constant_specification_mapping_set_ref(mapping_set, "CONSTANT-VALUE-MAPPING-REF")
            self._leave_child()
        if elem.data_type_mapping:
            self._add_child("DATA-TYPE-MAPPING-REFS")
            for mapping_set in elem.data_type_mapping:
                self._write_data_type_mapping_set_ref(mapping_set, "DATA-TYPE-MAPPING-REF")
            self._leave_child()
        if elem.exclusive_area:
            self._add_child("EXCLUSIVE-AREAS")
            for exclusive_area in elem.exclusive_area:
                self._write_exclusive_area(exclusive_area)
            self._leave_child()
        if elem.exclusive_area_nesting_order:
            self._add_child("EXCLUSIVE-AREA-NESTING-ORDERS")
            for order in elem.exclusive_area_nesting_order:
                self._write_exclusive_area_nesting_order(order)
            self._leave_child()
        if elem.static_memory:
            self._add_child("STATIC-MEMORYS")
            for item in elem.static_memory:
                self._write_variable_data_prototype(item, "VARIABLE-DATA-PROTOTYPE")
            self._leave_child()

    def _write_swc_internal_behavior_group(self, elem: ar_element.SwcInternalBehavior) -> None:
        """
        Writes group AR:SWC-INTERNAL-BEHAVIOR

        Most of it will be implemented in a future version
        """
        if elem.ar_typed_per_instance_memory:
            self._add_child("AR-TYPED-PER-INSTANCE-MEMORYS")
            for item in elem.ar_typed_per_instance_memory:
                self._write_variable_data_prototype(item, "VARIABLE-DATA-PROTOTYPE")
            self._leave_child()
        if elem.event:
            self._add_child("EVENTS")
            for event in elem.event:
                self._write_rte_event_element(event)
            self._leave_child()
        if elem.exclusive_area_policy:
            self._add_child("EXCLUSIVE-AREA-POLICYS")
            for policy in elem.exclusive_area_policy:
                self._write_swc_exclusive_area_policy(policy)
            self._leave_child()
        if elem.explicit_inter_runnable_variable:
            self._add_child("EXPLICIT-INTER-RUNNABLE-VARIABLES")
            for item in elem.explicit_inter_runnable_variable:
                self._write_variable_data_prototype(item, "VARIABLE-DATA-PROTOTYPE")
            self._leave_child()
        if elem.handle_termination_and_restart is not None:
            self._add_content("HANDLE-TERMINATION-AND-RESTART",
                              ar_enum.enum_to_xml(elem.handle_termination_and_restart))
        if elem.implicit_inter_runnable_variable:
            self._add_child("IMPLICIT-INTER-RUNNABLE-VARIABLES")
            for item in elem.implicit_inter_runnable_variable:
                self._write_variable_data_prototype(item, "VARIABLE-DATA-PROTOTYPE")
            self._leave_child()
        if elem.included_data_type_set:
            self._add_child("INCLUDED-DATA-TYPE-SETS")
            for item in elem.included_data_type_set:
                self._write_included_data_type_set(item)
            self._leave_child()
        if elem.included_mode_declaration_group_set:
            self._add_child("INCLUDED-MODE-DECLARATION-GROUP-SETS")
            for item in elem.included_mode_declaration_group_set:
                self._write_included_mode_declaration_group_set(item)
            self._leave_child()
        if elem.instantiation_data_def_props:
            self._add_child("INSTANTIATION-DATA-DEF-PROPSS")
            for item in elem.instantiation_data_def_props:
                self._write_instantiation_data_def_props(item)
            self._leave_child()
        if elem.per_instance_memory:
            self._add_child("PER-INSTANCE-MEMORYS")
            for item in elem.per_instance_memory:
                self._write_per_instance_memory(item)
            self._leave_child()
        if elem.per_instance_parameter:
            self._add_child("PER-INSTANCE-PARAMETERS")
            for item in elem.per_instance_parameter:
                self._write_parameter_data_prototype(item, "PARAMETER-DATA-PROTOTYPE")
            self._leave_child()
        if elem.port_api_option:
            self._add_child("PORT-API-OPTIONS")
            for element in elem.port_api_option.values():
                self._write_port_api_option(element)
            self._leave_child()
        if elem.runnable:
            self._add_child("RUNNABLES")
            for runnable in elem.runnable:
                self._write_runnable_entity(runnable)
            self._leave_child()
        if elem.service_dependency:
            self._add_child("SERVICE-DEPENDENCYS")
            for item in elem.service_dependency:
                self._write_swc_service_dependency(item)
            self._leave_child()
        if elem.shared_parameter:
            self._add_child("SHARED-PARAMETERS")
            for item in elem.shared_parameter:
                self._write_parameter_data_prototype(item, "PARAMETER-DATA-PROTOTYPE")
            self._leave_child()
        if elem.supports_multiple_instantiation is not None:
            self._add_content("SUPPORTS-MULTIPLE-INSTANTIATION",
                              self._format_boolean(elem.supports_multiple_instantiation))

    def _write_rte_event_element(self, elem: ar_element.RteEvent) -> None:
        """
        Writes COM-SPEC for R-PORT
        """
        class_name = elem.__class__.__name__
        write_method = self.switcher_rte_event.get(class_name, None)
        if write_method is not None:
            write_method(elem)
        else:
            raise NotImplementedError(f"Found no writer for class {class_name}")

    def _write_role_based_data_assignment(self, elem: ar_element.RoleBasedDataAssignment,
                                          tag: str = "ROLE-BASED-DATA-ASSIGNMENT") -> None:
        """
        Writes complex type AR:ROLE-BASED-DATA-ASSIGNMENT
        """
        self._add_child(tag)
        if elem.role is not None:
            self._add_content("ROLE", elem.role)
        if elem.used_data_element is not None:
            self._write_autosar_variable_ref(elem.used_data_element, "USED-DATA-ELEMENT")
        if elem.used_parameter_element is not None:
            self._write_autosar_parameter_ref(elem.used_parameter_element, "USED-PARAMETER-ELEMENT")
        if elem.used_pim_ref is not None:
            self._write_per_instance_memory_ref(elem.used_pim_ref, "USED-PIM-REF")
        self._leave_child()

    def _write_role_based_data_type_assignment(self, elem: ar_element.RoleBasedDataTypeAssignment,
                                               tag: str = "ROLE-BASED-DATA-TYPE-ASSIGNMENT") -> None:
        """
        Writes complex type AR:ROLE-BASED-DATA-TYPE-ASSIGNMENT
        """
        self._add_child(tag)
        if elem.role is not None:
            self._add_content("ROLE", elem.role)
        if elem.used_implementation_data_type_ref is not None:
            self._write_impl_data_type_ref(elem.used_implementation_data_type_ref,
                                           "USED-IMPLEMENTATION-DATA-TYPE-REF")
        self._leave_child()

    def _write_role_based_port_assignment(self, elem: ar_element.RoleBasedPortAssignment,
                                          tag: str = "ROLE-BASED-PORT-ASSIGNMENT") -> None:
        """
        Writes complex type AR:ROLE-BASED-PORT-ASSIGNMENT
        """
        self._add_child(tag)
        if elem.port_prototype_ref is not None:
            self._write_port_prototype_ref(elem.port_prototype_ref, "PORT-PROTOTYPE-REF")
        if elem.role is not None:
            self._add_content("ROLE", elem.role)
        self._leave_child()

    def _write_symbolic_name_props(self, elem: ar_element.SymbolicNameProps,
                                   tag: str = "SYMBOLIC-NAME-PROPS") -> None:
        """
        Writes complex type AR:SYMBOLIC-NAME-PROPS
        """
        self._add_child(tag)
        self._write_referrable(elem)
        if elem.symbol is not None:
            self._add_content("SYMBOL", elem.symbol)
        self._leave_child()

    def _write_service_dependency_group(self, elem: ar_element.ServiceDependency) -> None:
        """
        Writes group AR:SERVICE-DEPENDENCY
        """
        if elem.assigned_data_types:
            self._add_child("ASSIGNED-DATA-TYPES")
            for item in elem.assigned_data_types:
                self._write_role_based_data_type_assignment(item)
            self._leave_child()
        if elem.diagnostic_relevance is not None:
            self._add_content("DIAGNOSTIC-RELEVANCE",
                              ar_enum.enum_to_xml(elem.diagnostic_relevance))
        if elem.symbolic_name_props is not None:
            self._write_symbolic_name_props(elem.symbolic_name_props)

    def _write_swc_service_dependency_group(self, elem: ar_element.SwcServiceDependency) -> None:
        """
        Writes group AR:SWC-SERVICE-DEPENDENCY
        """
        if elem.assigned_datas:
            self._add_child("ASSIGNED-DATAS")
            for item in elem.assigned_datas:
                self._write_role_based_data_assignment(item)
            self._leave_child()
        if elem.assigned_ports:
            self._add_child("ASSIGNED-PORTS")
            for item in elem.assigned_ports:
                self._write_role_based_port_assignment(item)
            self._leave_child()
        if elem.represented_port_group_ref is not None:
            self._write_port_group_ref(elem.represented_port_group_ref, "REPRESENTED-PORT-GROUP-REF")
        if elem.service_needs is not None:
            self._add_child("SERVICE-NEEDS")
            class_name = elem.service_needs.__class__.__name__
            write_method = self.switcher_non_collectable.get(class_name, None)
            if write_method is not None:
                write_method(elem.service_needs)
            else:
                raise NotImplementedError(f"Found no writer for service_needs class {class_name}")
            self._leave_child()

    def _write_swc_service_dependency(self, elem: ar_element.SwcServiceDependency) -> None:
        """
        Writes complex type AR:SWC-SERVICE-DEPENDENCY
        Multi-tagged: False
        """
        self._add_child("SWC-SERVICE-DEPENDENCY")
        self._write_referrable(elem)
        self._write_multilanguage_referrable(elem)
        self._write_identifiable(elem)
        self._write_service_dependency_group(elem)
        self._write_swc_service_dependency_group(elem)
        self._leave_child()
