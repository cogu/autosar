"""
ARXML reader module
"""
import os
import re
import sys
# pylint: disable=duplicate-code
from typing import Iterable, Union, Any
import lxml.etree as ElementTree
import autosar.base as ar_base
import autosar.xml.document as ar_document
import autosar.xml.exception as ar_exception
import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum

# Type aliases

MultiLanguageOverviewParagraph = ar_element.MultiLanguageOverviewParagraph
ProvidePortComSpecElement = Union[ar_element.SenderComSpec,
                                  ar_element.ModeSwitchSenderComSpec,
                                  ar_element.QueuedSenderComSpec,
                                  ar_element.NonqueuedSenderComSpec,
                                  ar_element.NvProvideComSpec,
                                  ar_element.ParameterProvideComSpec]
RequirePortComSpecElement = Union[ar_element.QueuedReceiverComSpec,
                                  ar_element.NonqueuedReceiverComSpec,
                                  ar_element.NvRequireComSpec,
                                  ar_element.ParameterRequireComSpec,
                                  ar_element.ModeSwitchReceiverComSpec,
                                  ar_element.ClientComSpec]

RteEventElement = Union[ar_element.AsynchronousServerCallReturnsEvent,
                        ar_element.BackgroundEvent,
                        ar_element.DataReceivedEvent,
                        ar_element.DataReceiveErrorEvent,
                        ar_element.DataSendCompletedEvent,
                        ar_element.DataWriteCompletedEvent,
                        ar_element.ExternalTriggerOccurredEvent,
                        ar_element.InitEvent,
                        ar_element.InternalTriggerOccurredEvent,
                        ar_element.ModeSwitchedAckEvent,
                        ar_element.OperationInvokedEvent,
                        ar_element.SwcModeManagerErrorEvent,
                        ar_element.SwcModeSwitchEvent,
                        ar_element.TimingEvent,
                        ar_element.TransformerHardErrorEvent]

# Helper classes


class WrappedElement:
    """
    Wrapped XML Element
    """

    def __init__(self, elem: ElementTree.Element) -> None:
        self._elem = elem
        self.is_accessed: bool = False

    @property
    def elem(self) -> ElementTree.Element:
        """
        Returns element with some book-keeping
        """
        self.is_accessed = True
        return self._elem


class ChildElementMap:
    """
    Container for ARXML child elements
    """

    def __init__(self, elem: ElementTree.Element) -> None:
        self.elements: dict[str, WrappedElement] = {}
        for child_elem in elem.findall('./*'):
            tag = str(child_elem.tag)
            if tag not in self.elements:
                self.elements[tag] = WrappedElement(child_elem)

    def get(self, tag: str) -> ElementTree.Element:
        """
        Returns unwrapped element if it exists
        """
        wrapped = self.elements.get(tag, None)
        if wrapped is not None:
            return wrapped.elem
        return None

    def skip(self, tag: str) -> None:
        """
        Touches element but does not return it.
        This is used to skip elements that are not implemented
        but where we don't want to warn about them not being
        supported.
        """
        wrapped = self.elements.get(tag, None)
        if wrapped is not None:
            wrapped.is_accessed = True

    def values(self) -> Iterable[WrappedElement]:
        """
        Returns values of inner dict
        """
        return self.elements.values()


# Reader class


class Reader:
    """
    ARXML Reader class
    """

    def __init__(self,
                 warn_on_unprocessed_element: bool = True,
                 use_full_path_on_warning: bool = False,
                 schema_version: int = ar_base.DEFAULT_SCHEMA_VERSION) -> None:
        self.xml_root: ElementTree.Element = None
        self.file_path: str = None
        self.file_base_name: str = None
        self.warn_on_unprocessed_element = warn_on_unprocessed_element
        self.use_full_path_on_warning = use_full_path_on_warning
        self.observed_unsupported_elements = None
        self.schema_file: str = ''
        self.schema_version = schema_version
        self.document: ar_document.Document = None
        self.stop_on_error = False
        self.switcher_collectable = {  # Collectable elements
            # CompuMethod
            'COMPU-METHOD': self._read_compu_method,

            # Common structure and general template elements
            'DATA-FILTER': self._read_data_filter,
            'AUTOSAR-ENGINEERING-OBJECT': self._read_autosar_engineering_object,
            'CODE': self._read_code,

            # DataType and DataDictionary elements
            'APPLICATION-ARRAY-DATA-TYPE': self._read_application_array_data_type,
            'APPLICATION-RECORD-DATA-TYPE': self._read_application_record_data_type,
            'APPLICATION-PRIMITIVE-DATA-TYPE': self._read_application_primitive_data_type,
            'SW-BASE-TYPE': self._read_sw_base_type,
            'SW-ADDR-METHOD': self._read_sw_addr_method,
            'IMPLEMENTATION-DATA-TYPE': self._read_implementation_data_type,
            'DATA-TYPE-MAPPING-SET': self._read_data_type_mapping_set,


            # Constraint elements
            'DATA-CONSTR': self._read_data_constraint,

            # Port interface
            'NV-DATA-INTERFACE': self._read_nv_data_interface,
            'PARAMETER-INTERFACE': self._read_parameter_interface,
            'SENDER-RECEIVER-INTERFACE': self._read_sender_receiver_interface,
            'CLIENT-SERVER-INTERFACE': self._read_client_server_interface,
            'MODE-SWITCH-INTERFACE': self._read_mode_switch_interface,

            # Unit elements
            'UNIT': self._read_unit,

            # Constant elements
            'CONSTANT-SPECIFICATION': self._read_constant_specification,

            # Mode declaration elements
            'MODE-DECLARATION-GROUP': self._read_mode_declaration_group,

            # System template elements
            'E-2-E-PROFILE-COMPATIBILITY-PROPS': self._read_e2e_profile_compatibility_props,

            # Software component elements
            'APPLICATION-SW-COMPONENT-TYPE': self._read_application_sw_component_type,
            'COMPOSITION-SW-COMPONENT-TYPE': self._read_composition_sw_component_type,
            'SWC-IMPLEMENTATION': self._read_swc_implementation,

        }
        # Value specification elements
        self.switcher_value_specification = {
            'TEXT-VALUE-SPECIFICATION': self._read_text_value_specification,
            'NUMERICAL-VALUE-SPECIFICATION': self._read_numerical_value_specification,
            'NOT-AVAILABLE-VALUE-SPECIFICATION': self._read_not_available_value_specification,
            'ARRAY-VALUE-SPECIFICATION': self._read_array_value_specification,
            'RECORD-VALUE-SPECIFICATION': self._read_record_value_specification,
            'APPLICATION-VALUE-SPECIFICATION': self._read_application_value_specification,
            'CONSTANT-REFERENCE': self._read_constant_reference,

        }
        self.switcher_provided_com_spec = {
            'QUEUED-SENDER-COM-SPEC': self._read_queued_sender_com_spec,
            'MODE-SWITCH-SENDER-COM-SPEC': self._read_mode_switch_sender_com_spec,
            'NONQUEUED-SENDER-COM-SPEC': self._read_nonqueued_sender_com_spec,
            'NV-PROVIDE-COM-SPEC': self._read_nv_provider_com_spec,
            'PARAMETER-PROVIDE-COM-SPEC': self._read_parameter_provide_com_spec,
            'SERVER-COM-SPEC': self._read_server_com_spec,
        }
        self.switcher_required_com_spec = {
            'QUEUED-RECEIVER-COM-SPEC': self._read_queued_receiver_com_spec,
            'NONQUEUED-RECEIVER-COM-SPEC': self._read_nonqueued_receiver_com_spec,
            'NV-REQUIRE-COM-SPEC': self._read_nv_require_com_spec,
            'PARAMETER-REQUIRE-COM-SPEC': self._read_parameter_require_com_spec,
            'MODE-SWITCH-RECEIVER-COM-SPEC': self._read_mode_switch_receiver_com_spec,
            'CLIENT-COM-SPEC': self._read_client_com_spec,
        }
        self.switcher_rte_event = {
            'ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT': self._read_async_server_call_returns_event,
            'BACKGROUND-EVENT': self._read_background_event,
            'DATA-RECEIVE-ERROR-EVENT': self._read_data_receive_error_event,
            'DATA-RECEIVED-EVENT': self._read_data_received_event,
            'DATA-SEND-COMPLETED-EVENT': self._read_data_send_completed_event,
            'DATA-WRITE-COMPLETED-EVENT': self._read_data_write_completed_event,
            'EXTERNAL-TRIGGER-OCCURRED-EVENT': self._read_external_trigger_occured_event,
            'INIT-EVENT': self._read_init_event,
            'INTERNAL-TRIGGER-OCCURRED-EVENT': self._read_internal_trigger_occured_event,
            'MODE-SWITCHED-ACK-EVENT': self._read_mode_switched_ack_event,
            'OPERATION-INVOKED-EVENT': self._read_operation_invoked_event,
            'SWC-MODE-MANAGER-ERROR-EVENT': self._read_swc_mode_manager_error_event,
            'SWC-MODE-SWITCH-EVENT': self._read_swc_mode_switch_event,
            'TIMING-EVENT': self._read_timing_event,
            'TRANSFORMER-HARD-ERROR-EVENT': self._read_transformer_hard_error_event,
        }
        self.switcher_non_collectable = {  # Non-collectable, used only for unit testing
            # Documentation elements
            'ANNOTATION': self._read_annotation,
            'ANNOTATION-TEXT': self._read_documentation_block,
            'BR': self._read_break,
            'DESC': self._read_multi_language_overview_paragraph,
            'E': self._read_emphasis_text,
            'IE': self._read_index_entry,
            'L-4': self._read_language_long_name,
            'L-1': self._read_language_paragraph,
            'L-5': self._read_language_verbatim,
            'LABEL': self._read_multi_language_long_name,
            'LONG-NAME': self._read_multi_language_long_name,
            'P': self._read_multi_language_paragraph,
            'DISPLAY-NAME': self._read_single_language_unit_names,
            'SUP': self._read_superscript,
            'SUB': self._read_subscript,
            'TT': self._read_technical_term,
            'VERBATIM': self._read_multi_language_verbatim,
            'USED-LANGUAGES': self._read_multi_language_plain_text,
            'DATE': self._read_date,
            'REVISION-LABEL': self._read_revision_label_string,
            # AdminData elements
            'SDG': self._read_special_data_group,
            'MODIFICATION': self._read_modification,
            'DOC-REVISION': self._read_doc_revision,
            'ADMIN-DATA': self._read_admin_data,
            # CompuMethod elements
            'COMPU-INTERNAL-TO-PHYS': self._read_computation,
            'COMPU-RATIONAL-COEFFS': self._read_compu_rational,
            'COMPU-SCALE': self._read_compu_scale,
            # Constraint elements
            'SCALE-CONSTR': self._read_scale_constraint,
            'INTERNAL-CONSTRS': self._read_internal_constraint,
            'PHYS-CONSTRS': self._read_physical_constraint,
            'DATA-CONSTR-RULE': self._read_data_constraint_rule,
            # DataType and DataDictionary elements
            'BASE-TYPE-REF': self._read_sw_base_type_ref,
            'SW-BIT-REPRESENTATION': self._read_sw_bit_representation,
            'SW-DATA-DEF-PROPS-CONDITIONAL': self._read_sw_data_def_props_conditional,
            'SW-TEXT-PROPS': self._read_sw_text_props,
            'SW-POINTER-TARGET-PROPS': self._read_sw_pointer_target_props,
            'SYMBOL-PROPS': self._read_symbol_props,
            'IMPLEMENTATION-DATA-TYPE-ELEMENT': self._read_implementation_data_type_element,
            'APPLICATION-RECORD-ELEMENT': self._read_application_record_element,
            'ARGUMENT-DATA-PROTOTYPE': self._read_argument_data_prototype,
            'DATA-TYPE-MAP': self._read_data_type_map,
            'SW-ARRAYSIZE': self._read_value_list,
            'MODE-REQUEST-TYPE-MAP': self._read_mode_request_type_map,
            # CalibrationData elements
            'SW-VALUES-PHYS': self._read_sw_values,
            'SW-AXIS-CONT': self._read_sw_axis_cont,
            'SW-VALUE-CONT': self._read_sw_value_cont,
            # Reference elements
            'PHYSICAL-DIMENSION-REF': self._read_physical_dimension_ref,
            'APPLICATION-DATA-TYPE-REF': self._read_application_data_type_ref,
            'CONSTANT-REF': self._read_constant_ref,
            # Port interface elements
            'INVALIDATION-POLICY': self._read_invalidation_policy,
            'APPLICATION-ERROR': self._read_application_error,
            'CLIENT-SERVER-OPERATION': self._read_client_server_operation,
            # ModeDeclaration elements
            'MODE-DECLARATION': self._read_mode_declaration,
            'MODE-MANAGER-ERROR-BEHAVIOR': self._read_mode_error_behavior,
            'MODE-USER-ERROR-BEHAVIOR': self._read_mode_error_behavior,
            'MODE-TRANSITION': self._read_mode_transition,
            'MODE-DECLARATION-GROUP-PROTOTYPE': self._read_mode_declaration_group_prototype,
            # SystemTemplate elements
            'END-TO-END-TRANSFORMATION-COM-SPEC-PROPS': self._read_e2e_transformation_com_spec_props,
            # Software component elements
            'MODE-SWITCHED-ACK': self._read_mode_switched_ack_request,
            'TRANSMISSION-PROPS': self._read_tranmsission_com_spec_props,
            'TRANSMISSION-ACKNOWLEDGE': self._read_transmission_acknowledgement_request,
            'RECEPTION-PROPS': self._read_reception_com_spec_props,
            'P-PORT-PROTOTYPE': self._read_provide_port_prototype,
            'R-PORT-PROTOTYPE': self._read_require_port_prototype,
            'PR-PORT-PROTOTYPE': self._read_pr_port_prototype,
            'SW-COMPONENT-PROTOTYPE': self._read_sw_component_prototype,
            'PROVIDER-IREF': self._read_port_in_composition_type_instance_ref,
            'REQUESTER-IREF': self._read_port_in_composition_type_instance_ref,
            'ASSEMBLY-SW-CONNECTOR': self._read_assembly_sw_connector,
            'DELEGATION-SW-CONNECTOR': self._read_delegation_sw_connector,
            'PASS-THROUGH-SW-CONNECTOR': self._read_pass_through_sw_connector,
            'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF': self._read_r_mode_group_in_atomic_swc_instance_ref,
            # SWC internal behavior elements
            'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE': self._read_variable_in_impl_data_instance_ref,
            'AUTOSAR-VARIABLE-IREF': self._read_variable_in_atomic_swc_type_instance_ref,
            'ACCESSED-VARIABLE': self._read_autosar_variable_ref,
            'VARIABLE-ACCESS': self._read_variable_access,
            'EXECUTABLE-ENTITY-ACTIVATION-REASON': self._read_executable_entity_activation_reason,
            'EXCLUSIVE-AREA-REF-CONDITIONAL': self._read_exclusive_area_ref_conditional,
            'DISABLED-MODE-IREF': self._read_r_mode_in_atomic_swc_instance_ref,
            'SWC-INTERNAL-BEHAVIOR': self._read_swc_internal_behavior,
            'RUNNABLE-ENTITY-ARGUMENT': self._read_runnable_entity_argument,
            'RUNNABLE-ENTITY': self._read_runnable_entity,
            'ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT': self._read_async_server_call_returns_event,
            'BACKGROUND-EVENT': self._read_background_event,
            'DATA-RECEIVE-ERROR-EVENT': self._read_data_receive_error_event,
            'DATA-RECEIVED-EVENT': self._read_data_received_event,
            'DATA-SEND-COMPLETED-EVENT': self._read_data_send_completed_event,
            'DATA-WRITE-COMPLETED-EVENT': self._read_data_write_completed_event,
            'EXTERNAL-TRIGGER-OCCURRED-EVENT': self._read_external_trigger_occured_event,
            'INIT-EVENT': self._read_init_event,
            'INTERNAL-TRIGGER-OCCURRED-EVENT': self._read_internal_trigger_occured_event,
            'MODE-SWITCHED-ACK-EVENT': self._read_mode_switched_ack_event,
            'OPERATION-INVOKED-EVENT': self._read_operation_invoked_event,
            'SWC-MODE-MANAGER-ERROR-EVENT': self._read_swc_mode_manager_error_event,
            'SWC-MODE-SWITCH-EVENT': self._read_swc_mode_switch_event,
            'TIMING-EVENT': self._read_timing_event,
            'TRANSFORMER-HARD-ERROR-EVENT': self._read_transformer_hard_error_event,
            'PORT-DEFINED-ARGUMENT-VALUE': self._read_port_defined_argument_value,
            'COMMUNICATION-BUFFER-LOCKING': self._read_communication_buffer_locking,
            'PORT-API-OPTION': self._read_port_api_option,
            'ASYNCHRONOUS-SERVER-CALL-POINT': self._read_async_server_call_point,
            'SYNCHRONOUS-SERVER-CALL-POINT': self._read_sync_server_call_point,
            'ASYNCHRONOUS-SERVER-CALL-RESULT-POINT': self._read_async_server_call_result_point,
            'EXTERNAL-TRIGGERING-POINT': self._read_external_triggering_point,
            'INTERNAL-TRIGGERING-POINT': self._read_internal_triggering_point,
            'MODE-ACCESS-POINT': self._read_mode_access_point,
            'MODE-SWITCH-POINT': self._read_mode_switch_point,
            'AUTOSAR-PARAMETER-IREF': self._read_parameter_in_atomic_swc_type_instance_ref,
            'ACCESSED-PARAMETER': self._read_autosar_parameter_ref,
            'PARAMETER-ACCESS': self._read_parameter_access,
            'WAIT-POINT': self._read_wait_point,
        }
        self.switcher_all = {}
        self.switcher_all.update(self.switcher_collectable)
        self.switcher_all.update(self.switcher_value_specification)
        self.switcher_all.update(self.switcher_provided_com_spec)
        self.switcher_all.update(self.switcher_required_com_spec)
        self.switcher_all.update(self.switcher_non_collectable)
        self._switcher_type_name = {
            "ApplicationArrayElement": self._read_application_array_element,
            "ParameterDataPrototype": self._read_parameter_data_prototype,
            "VariableDataPrototype": self._read_variable_data_prototype,
        }

    def read_file(self, file_path: str, stop_on_error: bool = False) -> ar_document.Document:
        """
        Reads ARXML document file
        """
        self.document = None
        self.xml_root = ElementTree.ElementTree().parse(file_path)
        self.file_path = file_path
        self.file_base_name = os.path.basename(file_path)
        self.observed_unsupported_elements = set()
        self.stop_on_error = stop_on_error
        self._clean_namespace('http://autosar.org/schema/r4.0')
        self._read_root_element()
        self._read_packages()
        return self.document

    def read_str(self, xml: str, stop_on_error: bool = False) -> None | ar_document.Document:
        """
        Reads ARXML document from string.
        """
        self.observed_unsupported_elements = set()
        self.document = None
        self.xml_root = ElementTree.fromstring(bytes(xml, encoding="utf-8"))
        self.file_path = ""
        self.file_base_name = ""
        self.stop_on_error = stop_on_error
        self._clean_namespace('http://autosar.org/schema/r4.0')
        self._read_root_element()
        self._read_packages()
        return self.document

    def read_str_elem(self, xml: str, type_name: str | None = None) -> None | ar_element.ARObject:
        """
        Reads a concrete ARXML element from string.
        This is primarily used for unit-testing.
        """
        self.observed_unsupported_elements = set()
        elem = ElementTree.fromstring(xml)
        if type_name is not None:
            read_method = self._switcher_type_name.get(type_name, None)
        else:
            read_method = self.switcher_all.get(elem.tag, None)
        if read_method is not None:
            return read_method(elem)
        else:
            raise NotImplementedError(f"Found no reader for '{elem.tag}'")

    # --- Utility methods

    def _report_unprocessed_elements(self, xml_elements: ChildElementMap):
        """
        Reports about unprocessed child elements
        """
        for xml_elem in [x.elem for x in xml_elements.values() if not x.is_accessed]:
            assert xml_elem is not None
            self._report_unprocessed_element(xml_elem)

    def _report_unprocessed_element(self, xml_elem: ElementTree.Element):
        """
        Reports about a single child element
        """
        if xml_elem.tag not in self.observed_unsupported_elements:
            self.observed_unsupported_elements.add(xml_elem.tag)
            if self.warn_on_unprocessed_element:
                if self.file_path is not None:
                    file = self.file_path if self.use_full_path_on_warning else self.file_base_name
                    print(f"{file}({xml_elem.sourceline}): Unprocessed element <{xml_elem.tag}>", file=sys.stderr)
                else:
                    print(f"Unprocessed element <{xml_elem.tag}>", file=sys.stderr)

    def _element_error_message(self, element: ElementTree.Element, message: str) -> str:
        """
        Generates an error message with file-name and source-line
        """
        file = self.file_path if self.use_full_path_on_warning else self.file_base_name
        header = f"{file}({element.sourceline}): "
        return header + message

    def _raise_parse_error(self, element: ElementTree.Element, message: str):
        """
        Raises an ARXML parse error with message
        """
        raise ar_exception.ParseError(self._element_error_message(element, message))

    def _clean_namespace(self, namespace: str) -> None:
        """
        Removes XML namespace in place.
        """
        wrapped = '{' + namespace + '}'
        wrapped_len = len(wrapped)
        for elem in self.xml_root.iter():
            if isinstance(elem.tag, str) and elem.tag.startswith(wrapped):
                elem.tag = elem.tag[wrapped_len:]

    def _read_boolean(self, value: str) -> bool:
        """
        Reads simpleType AR:BOOLEAN--SIMPLE
        """
        if value in ('0', 'false'):
            return False
        elif value in ('1', 'true'):
            return True
        else:
            raise ar_exception.ParseError('Not a boolean value: ' + str(value))

    def _read_number(self, text: str) -> int | float:
        """
        Attempts to convert text to either int or float
        """
        try:
            value = int(text)
        except ValueError:
            try:
                value = float(text)
            except ValueError as exc:
                raise ar_exception.ParseError(f"Not a number: {text}") from exc
        return value

    def _read_integer(self, text: str) -> int:
        """
        Reads AR:INTEGER
        """
        try:
            value = int(text, 0)
        except ValueError as exc:
            raise ar_exception.ParseError(f"Failed to parse integer: {text}") from exc
        return value

    # --- Abstract base classes

    def _read_referrable(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:REFERRABLE
        Type: Abstract
        """
        short_name = element_map.get('SHORT-NAME')
        if short_name is not None:
            data['name'] = short_name.text
        else:
            raise ar_exception.ParseError(
                "Missing required element SHORT-NAME")
        xml_long_name = element_map.get('LONG-NAME')
        if xml_long_name is not None:
            data['long_name'] = self._read_multi_language_long_name(
                xml_long_name)

    def _read_multi_language_referrable(self, element_map: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:MULTILANGUAGE-REFERRABLE
        Type: Abstract
        """
        xml_long_name = element_map.get('LONG-NAME')
        if xml_long_name is not None:
            data['long_name'] = self._read_multi_language_long_name(xml_long_name)

    def _read_identifiable(self, element_map: ChildElementMap, attr: dict, data: dict) -> None:
        """
        Reads group AR:IDENTIFIABLE
        Type: Abstract
        """
        self._read_identifiable_attributes(attr, data)
        xml_child: ElementTree.Element | None = None
        xml_child = element_map.get('DESC')
        if xml_child is not None:
            data['desc'] = self._read_multi_language_overview_paragraph(
                xml_child)
        xml_child = element_map.get('CATEGORY')
        if xml_child is not None:
            data['category'] = xml_child.text
        xml_child = element_map.get('ADMIN-DATA')
        if xml_child is not None:
            data['admin_data'] = self._read_admin_data(xml_child)
        xml_child = element_map.get('INTRODUCTION')
        if xml_child is not None:
            data['introduction'] = self._read_documentation_block(xml_child)
        xml_child = element_map.get('ANNOTATIONS')
        if xml_child is not None:
            data['annotations'] = self._read_annotations(xml_child)

    def _read_identifiable_attributes(self, attr: dict, data: dict) -> None:
        uuid = attr.get('UUID', None)
        if uuid is not None:
            data['uuid'] = uuid

    # AdminData

    def _read_special_data_group(self, xml_element: ElementTree.Element) -> ar_element.SpecialDataGroup:
        """
        Reads complex type AR:SDG
        Tag variants: 'SDG'
        """
        data = {}
        self._read_special_data_group_internal(xml_element, data)
        return ar_element.SpecialDataGroup(**data)

    def _read_special_data_group_internal(self, xml_element: ElementTree.Element, data: dict) -> None:
        """
        Reads group AR:SDG
        """
        if "GID" in xml_element.attrib:
            data["gid"] = xml_element.attrib["GID"]
        xml_child = xml_element.find("./SDG-CAPTION")
        if xml_child is not None:
            data["caption"] = xml_child.text
        content = []
        for xml_child in xml_element.findall("./*"):
            if xml_child.tag == "SD":
                gid = xml_child.attrib.get("GID")
                if gid:
                    content.append((gid, xml_child.text))
                else:
                    content.append(xml_child.text)
            elif xml_child.tag == "SDF":
                gid = xml_child.attrib.get("GID")
                value = self._read_number(xml_child.text)
                if gid:
                    content.append((gid, value))
                else:
                    content.append(value)
            elif xml_child.tag == "SDG":
                child = self._read_special_data_group(xml_child)
                content.append({"gid": child.gid, "caption": child.caption, "content": child.content})
        if len(content) > 0:
            data["content"] = content

    def _read_modification(self, xml_element: ElementTree.Element) -> ar_element.Modification:
        """
        Reads complex type AR:MODIFICATION
        Tag variants: 'MODIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_modification_group(child_elements, data)
        return ar_element.Modification(**data)

    def _read_modification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:MODIFICATION
        Tag variants: 'MODIFICATION'
        """
        xml_child = child_elements.get("CHANGE")
        if xml_child is not None:
            data["change"] = self._read_multi_language_overview_paragraph(xml_child)
        xml_child = child_elements.get("REASON")
        if xml_child is not None:
            data["reason"] = self._read_multi_language_overview_paragraph(xml_child)

    def _read_doc_revision(self, xml_element: ElementTree.Element) -> ar_element.DocRevision:
        """
        Reads complex type AR:DOC-REVISION
        Tag variants: 'DOC-REVISION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_doc_revision_group(child_elements, data)
        return ar_element.DocRevision(**data)

    def _read_doc_revision_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:DOC-REVISION
        """
        xml_child = child_elements.get("REVISION-LABEL")
        if xml_child is not None:
            data["revision_label"] = self._read_revision_label_string(xml_child)
        xml_child = child_elements.get("REVISION-LABEL-P1")
        if xml_child is not None:
            data["revision_label_p1"] = self._read_revision_label_string(xml_child)
        xml_child = child_elements.get("REVISION-LABEL-P2")
        if xml_child is not None:
            data["revision_label_p2"] = self._read_revision_label_string(xml_child)
        xml_child = child_elements.get("STATE")
        if xml_child is not None:
            data["state"] = xml_child.text
        xml_child = child_elements.get("ISSUED-BY")
        if xml_child is not None:
            data["issued_by"] = xml_child.text
        xml_child = child_elements.get("DATE")
        if xml_child is not None:
            data["date"] = self._read_date(xml_child)
        xml_child = child_elements.get("MODIFICATIONS")
        if xml_child is not None:
            elements = []
            for xml_grand_child in xml_child.findall("./MODIFICATION"):
                elements.append(self._read_modification(xml_grand_child))
            data["modifications"] = elements

    def _read_admin_data(self, xml_element: ElementTree.Element) -> ar_element.AdminData:
        """
        Reads Complex-type AR:ADMIN-DATA

        Tag variants: 'ADMIN-DATA'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_admin_data_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AdminData(**data)

    def _read_admin_data_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ADMIN-DATA
        """
        xml_child = child_elements.get('LANGUAGE')
        if xml_child is not None:
            data["language"] = ar_enum.xml_to_enum("Language", xml_child.text)
        xml_child = child_elements.get('USED-LANGUAGES')
        if xml_child is not None:
            data["used_languages"] = self._read_multi_language_plain_text(xml_child)
        xml_child = child_elements.get("DOC-REVISIONS")
        if xml_child is not None:
            elements = []
            for xml_grand_child in xml_child.findall("./DOC-REVISION"):
                elements.append(self._read_doc_revision(xml_grand_child))
            data["doc_revisions"] = elements
        xml_child = child_elements.get('SDGS')
        if xml_child is not None:
            data['sdgs'] = self._read_admin_data_sdgs(xml_child)
        return ar_element.AdminData(**data)

    def _read_admin_data_sdgs(self, xml_element: ElementTree.Element) -> list:
        """
        Reads SDGS element in ADMIN-DATA
        """
        sdg_list = []
        for xml_child in xml_element.findall('./SDG'):
            sdg = self._read_special_data_group(xml_child)
            sdg_list.append(sdg)
        return sdg_list

    # --- AUTOSAR Document

    def _read_root_element(self) -> None:
        self._read_schema_version()
        self.document = ar_document.Document()
        self.document.schema_version = self.schema_version
#        for xml_node in self.xml_root.findall('./*'):
#            if xml_node.tag == 'FILE-INFO-COMMENT':
#                self._read_file_info_comment(xml_node, self.document)

    def _read_schema_version(self) -> None:
        for key in self.xml_root.attrib.keys():
            if key.endswith('schemaLocation'):
                match = re.search(r'AUTOSAR_(\d+).xsd',
                                  self.xml_root.attrib[key])
                if match is not None:
                    self.schema_file = 'AUTOSAR_' + match.group(1) + '.xsd'
                    self.schema_version = int(match.group(1))

    # def _read_file_info_comment(self, xml_node, parent):
    #     """
    #     Parse AR:FILE-INFO-COMMENT
    #     """
    #     sdg_list = self._read_special_data_groups(xml_node)

    # AUTOSAR Package

    def _read_packages(self):
        for xml_node in self.xml_root.findall('./AR-PACKAGES/*'):
            if xml_node.tag == 'AR-PACKAGE':
                package = self._read_package(xml_node)
                self.document.append(package)

    def _read_package(self, elem: ElementTree.Element) -> ar_element.Package:
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        package = ar_element.Package(**data)
        self._read_package_group(child_elements, package)
        self._report_unprocessed_elements(child_elements)
        return package

    def _read_package_group(self, element_map: ChildElementMap, package: ar_element.Package) -> None:
        """
        Reads group AR:AR-PACKAGE
        Type: Utility
        """
        # REFERECE-BASES not implemented
        xml_elements = element_map.get('ELEMENTS')
        xml_packages = element_map.get('AR-PACKAGES')
        # VARIATION-POINT will not be supported
        if xml_elements is not None:
            self._read_package_elements(package, xml_elements)
        if xml_packages is not None:
            self._read_sub_packages(package, xml_packages)

    def _read_package_elements(self, package: ar_element.Package, xml_elements: ElementTree.Element) -> None:
        """
        Reads AR:AR-PACKAGE.ELEMENTS
        Type: Utility
        """
        for xml_child_elem in xml_elements.findall('./*'):
            read_method = self.switcher_collectable.get(
                xml_child_elem.tag, None)
            if read_method is not None:
                try:
                    element = read_method(xml_child_elem)
                    assert isinstance(element, ar_element.ARElement)
                    package.append(element)
                except ar_exception.ParseError as exc:
                    msg = "Parse error encountered while reading element starting on this line"
                    message = self._element_error_message(xml_child_elem, msg)
                    if self.stop_on_error:
                        raise ar_exception.ParseError(message) from exc
                    print(message + ":")
                    print("    " + str(exc))
                except ar_exception.DuplicateElement as exc:
                    message = self._element_error_message(xml_child_elem,
                                                          str(exc))
                    if self.stop_on_error:
                        raise ar_exception.DuplicateElement(message) from exc
                    print(message)
            else:
                self._report_unprocessed_element(xml_child_elem)

    def _read_sub_packages(self, package: ar_element.Package, xml_packages: ElementTree.Element) -> None:
        """
        Reads AR:AR-PACKAGE.ELEMENTS
        Type: Utility
        """
        for xml_child_package in xml_packages.findall('./AR-PACKAGE'):
            child_package = self._read_package(xml_child_package)
            assert isinstance(child_package, ar_element.Package)
            package.append(child_package)

    # --- Documentation elements

    def _read_annotation(self, xml_elem: ElementTree.Element) -> ar_element.Annotation:
        """
        Reads Complex-type AR:ANNOTATION
        """
        data = {}
        self._read_general_annotation(xml_elem, data)
        elem = ar_element.Annotation(**data)
        return elem

    def _read_annotations(self, xml_elem: ElementTree.Element) -> list[ar_element.Annotation]:
        """
        Reads unbounded list of AR:ANNOTATION
        """
        elements = []
        for xml_child in xml_elem.findall('./ANNOTATION'):
            elements.append(self._read_annotation(xml_child))
        return elements

    def _read_general_annotation(self, xml_elem: ElementTree.Element, data: dict) -> None:
        """
        Reads Group AR:GENERAL-ANNOTATION
        """
        xml_label = xml_elem.find('./LABEL')
        xml_origin = xml_elem.find('./ANNOTATION-ORIGIN')
        xml_text = xml_elem.find('./ANNOTATION-TEXT')

        if xml_label is not None:
            data['label'] = self._read_multi_language_long_name(xml_label)
        if xml_origin is not None:
            data['origin'] = xml_origin.text
        if xml_text is not None:
            data['text'] = self._read_documentation_block(xml_text)

    def _read_break(self, xml_elem: ElementTree.Element) -> ar_element.Break:  # pylint: disable=unused-argument
        """
        Reads complexType AR:BR
        Type: Concrete
        """
        return ar_element.Break()

    def _read_documentation_block(self, xml_elem: ElementTree.Element) -> ar_element.DocumentationBlock:
        """
        Reads complexType AR:DOCUMENTATION-BLOCK
        Type: Concrete
        """
        elem = ar_element.DocumentationBlock()
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'P':
                elem.append(
                    self._read_multi_language_paragraph(xml_child_elem))
            elif xml_child_elem.tag == 'VERBATIM':
                elem.append(self._read_multi_language_verbatim(xml_child_elem))
            else:
                self._report_unprocessed_element(xml_child_elem)
        return elem

    def _read_emphasis_text(self, elem: ElementTree.Element) -> ar_element.EmphasisText:
        """
        Reads complexType AR:EMPHASIS-TEXT
        We only support plain elements for now. No nesting (mixed-content) supported.

        Type: Concrete
        """
        data = {}
        self._read_emphasis_text_attr(elem.attrib, data)
        if len(elem.findall('./*')) > 0:
            raise NotImplementedError(
                "Nesting inside <E> elements not yet supported")
        data['elements'] = elem.text
        return ar_element.EmphasisText(**data)

    def _read_emphasis_text_attr(self, attrib: dict, data: dict) -> None:
        """
        Reads attributeGroup AR:EMPHASIS-TEXT
        """
        if 'COLOR' in attrib:
            data['color'] = str(attrib['COLOR'])
        if 'FONT' in attrib:
            data['font'] = ar_enum.xml_to_enum(
                'EmphasisFont', attrib['FONT'], self.schema_version)
        if 'TYPE' in attrib:
            data['type'] = ar_enum.xml_to_enum(
                'EmphasisType', attrib['TYPE'], self.schema_version)

    def _read_index_entry(self, elem: ElementTree.Element) -> ar_element.IndexEntry:
        """
        Reads complexType AR:INDEX-ENTRY
        Limitations: Doesn't support child-elements even though it's allowed in the scehema
        Type: Concrete
        """
        return ar_element.IndexEntry(elem.text)

    def _read_technical_term(self,
                             elem: ElementTree.Element) -> ar_element.TechnicalTerm:
        """
        Reads complexType AR:TT
        Type: Concrete
        """
        data = {}
        self._read_technical_term_attr(elem.attrib, data)
        if len(elem.findall('./*')) > 0:
            self._raise_parse_error(
                elem, 'Child elements in "AR:TT" not allowed')
        data['text'] = elem.text
        return ar_element.TechnicalTerm(**data)

    def _read_technical_term_attr(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from attribute group AR:TT
        """
        if 'TEX-RENDER' in attrib:
            data['tex_render'] = str(attrib['TEX-RENDER'])
        if 'TYPE' in attrib:
            data['type'] = str(attrib['TYPE'])

    def _read_superscript(self, elem: ElementTree.Element) -> ar_element.TechnicalTerm:
        """
        Reads complexType AR:SUPSCRIPT for tag SUP
        Type: Concrete
        """
        return ar_element.Superscript(elem.text)

    def _read_subscript(self, elem: ElementTree.Element) -> ar_element.TechnicalTerm:
        """
        Reads complexType AR:SUPSCRIPT for tag SUB
        Type: Concrete
        """
        return ar_element.Subscript(elem.text)

    def _read_multi_language_long_name(self, xml_elem: ElementTree.Element) -> ar_element.MultilanguageLongName:
        """
        Reads complexType AR:MULTILANGUAGE-LONG-NAME
        Type: Concrete
        Tag variants: 'LABEL' | 'LONG-NAME'
        """
        assert xml_elem.tag in {'LONG-NAME', 'LABEL'}
        elem = ar_element.MultilanguageLongName()
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-4':
                elem.append(self._read_language_long_name(xml_child_elem))
        return elem

    def _read_language_long_name(self, xml_elem: ElementTree.Element) -> ar_element.LanguageLongName:
        """
        Reads complexType AR:L-LONG-NAME (L-4 tags)
        Type: Concrete
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageLongName(data['language'])
        self._read_mixed_content_for_long_name(xml_elem, elem)
        return elem

    def _read_language_specific_attr(self, attrib: dict, data: dict) -> None:
        """
        Reads attributeGroup AR:LANGUAGE-SPECIFIC
        """
        data['language'] = ar_enum.xml_to_enum(
            'Language', attrib['L'])  # L is a mandatory attribute

    def _read_mixed_content_for_long_name(self,
                                          xml_elem: ElementTree.Element,
                                          elem: ar_element.LanguageLongName) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-LONG-NAME

        This includes reading mixed content from L-LONG-NAME or
        SINGLE-LANGUAGE-LONG-NAME

        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            elif xml_child_elem.tag == 'IE':
                elem.append(self._read_index_entry(xml_child_elem))
            elif xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_multi_language_overview_paragraph(self,
                                                xml_elem: ElementTree.Element) -> MultiLanguageOverviewParagraph:
        """
        Reads complexType AR:MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'DESC' | 'ITEM-LABEL' | 'CHANGE' | 'REASON'
        """
        assert xml_elem.tag in {'DESC', 'ITEM-LABEL', 'CHANGE', 'REASON'}
        elem = MultiLanguageOverviewParagraph()
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-2':
                elem.append(
                    self._read_language_overview_paragraph(xml_child_elem))
        return elem

    def _read_language_overview_paragraph(self,
                                          xml_elem: ElementTree.Element) -> ar_element.LanguageOverviewParagraph:
        """
        Reads complexType AR:L-OVERVIEW-PARAGRAPH
        Type: Concrete
        Tag variants: 'L-2'
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageOverviewParagraph(data['language'])
        self._read_mixed_content_for_overview_paragraph(xml_elem, elem)
        return elem

    def _read_mixed_content_for_overview_paragraph(self,
                                                   xml_elem: ElementTree.Element,
                                                   elem: ar_element.LanguageOverviewParagraph) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-OVERVIEW-PARAGRAPH

        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'BR':
                elem.append(self._read_break(xml_child_elem))
            elif xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            elif xml_child_elem.tag == 'IE':
                elem.append(self._read_index_entry(xml_child_elem))
            elif xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            elif xml_child_elem.tag in {'FT', 'TRACE-REF', 'XREF'}:
                # These elements are not yet supported
                self._report_unprocessed_element(xml_child_elem)
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_language_paragraph(self, xml_elem: ElementTree.Element) -> ar_element.LanguageParagraph:
        """
        Reads complexType AR:L-PARAGRAPH
        Type: Concrete
        Tag variants: 'L-1'
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageParagraph(data['language'])
        self._read_mixed_content_for_paragraph(xml_elem, elem)
        return elem

    def _read_language_verbatim(self, xml_elem: ElementTree.Element) -> ar_element.LanguageVerbatim:
        """
        Reads complexType AR:L-VERBATIM
        Type: Concrete
        Tag variants: 'L-5'
        """
        data = {}
        self._read_language_specific_attr(xml_elem.attrib, data)
        elem = ar_element.LanguageVerbatim(data['language'])
        self._read_mixed_content_for_verbatim(xml_elem, elem)
        return elem

    def _read_mixed_content_for_paragraph(self,
                                          xml_elem: ElementTree.Element,
                                          elem: ar_element.LanguageParagraph) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-PARAGRAPH
        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'BR':
                elem.append(self._read_break(xml_child_elem))
            elif xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            elif xml_child_elem.tag == 'IE':
                elem.append(self._read_index_entry(xml_child_elem))
            elif xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            elif xml_child_elem.tag in {'FT',
                                        'STD',
                                        'TRACE-REF',
                                        'XDOC',
                                        'XFILE',
                                        'XREF',
                                        'XREF-TARGET'}:
                # These elements are not yet supported
                self._report_unprocessed_element(xml_child_elem)
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_mixed_content_for_verbatim(self,
                                         xml_elem: ElementTree.Element,
                                         elem: ar_element.LanguageVerbatim) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-VERBATIM
        Type: Abstract
        """
        if xml_elem.text:
            elem.append(xml_elem.text)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'BR':
                elem.append(self._read_break(xml_child_elem))
            elif xml_child_elem.tag == 'E':
                elem.append(self._read_emphasis_text(xml_child_elem))
            if xml_child_elem.tag == 'TT':
                elem.append(self._read_technical_term(xml_child_elem))
            elif xml_child_elem.tag in {'XREF'}:
                # These elements are not yet supported
                self._report_unprocessed_element(xml_child_elem)
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_elem.text)

    def _read_multi_language_paragraph(self,
                                       xml_elem: ElementTree.Element) -> ar_element.MultiLanguageParagraph:
        """
        Reads complexType AR:MULTI-LANGUAGE-PARAGRAPH
        Type: Concrete
        Tag variants: 'P'
        """
        attr = {}
        self._read_document_view_selectable_attrib(xml_elem.attrib, attr)
        self._read_paginateable_attrib(xml_elem.attrib, attr)
        self._read_multi_language_paragraph_attrib(xml_elem.attrib, attr)
        elem = ar_element.MultiLanguageParagraph(**attr)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-1':
                elem.append(self._read_language_paragraph(xml_child_elem))
        return elem

    def _read_document_view_selectable_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:DOCUMENT-VIEW-SELECTABLE
        """
        if 'SI' in attrib:
            data['semantic_information'] = str(attrib['SI'])
        if 'VIEW' in attrib:
            data['view'] = str(attrib['VIEW'])

    def _read_paginateable_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:PAGINATEABLE
        """
        if 'BREAK' in attrib:
            data['page_break'] = ar_enum.xml_to_enum(
                'PageBreak', attrib['BREAK'])
        if 'KEEP-WITH-PREVIOUS' in attrib:
            data['keep_with_previous'] = ar_enum.xml_to_enum(
                'KeepWithPrevious', attrib['KEEP-WITH-PREVIOUS'])

    def _read_multi_language_paragraph_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:MULTI-LANGUAGE-PARAGRAPH
        """
        if 'HELP-ENTRY' in attrib:
            data['help_entry'] = str(attrib['HELP-ENTRY'])

    def _read_multi_language_verbatim(self,
                                      xml_elem: ElementTree.Element) -> ar_element.MultiLanguageVerbatim:
        """
        Reads complexType AR:MULTI-LANGUAGE-VERBATIM
        Type: Concrete
        Tag variants: 'VERBATIM'
        """
        attr = {}
        self._read_document_view_selectable_attrib(xml_elem.attrib, attr)
        self._read_paginateable_attrib(xml_elem.attrib, attr)
        self._read_multi_language_verbatim_attrib(xml_elem.attrib, attr)
        elem = ar_element.MultiLanguageVerbatim(**attr)
        for xml_child_elem in xml_elem.findall('./*'):
            if xml_child_elem.tag == 'L-5':
                elem.append(self._read_language_verbatim(xml_child_elem))
        return elem

    def _read_multi_language_verbatim_attrib(self, attrib: dict, data: dict) -> None:
        """
        Reads attributes from AttributeGroup AR:MULTI-LANGUAGE-VERBATIM
        """
        if 'ALLOW-BREAK' in attrib:
            data['allow_break'] = str(attrib['ALLOW-BREAK'])
        if 'FLOAT' in attrib:
            data['float'] = ar_enum.xml_to_enum('Float', attrib['FLOAT'])
        if 'HELP-ENTRY' in attrib:
            data['help_entry'] = str(attrib['HELP-ENTRY'])
        if 'PGWIDE' in attrib:
            data['page_wide'] = ar_enum.xml_to_enum(
                'PageWide', attrib['PGWIDE'])

    def _read_single_language_unit_names(self, xml_element: ElementTree.Element) -> ar_element.SingleLanguageUnitNames:
        """
        Reads complex type AR:SINGLE-LANGUAGE-UNIT-NAMES
        Type: concrete
        Tag variants: 'PRM-UNIT' | 'UNIT-DISPLAY-NAME' | 'UNIT-DISPLAY-NAME' | 'DISPLAY-NAME'
        """
        elem = ar_element.SingleLanguageUnitNames()
        self._read_mixed_content_for_unit_names(xml_element, elem)
        return elem

    def _read_mixed_content_for_unit_names(self,
                                           xml_element: ElementTree.Element,
                                           elem: ar_element.SingleLanguageUnitNames) -> None:
        """
        Reads group AR:MIXED-CONTENT-FOR-UNIT-NAMES
        Type: Abstract
        """
        if xml_element.text:
            elem.append(xml_element.text)
        for xml_child_elem in xml_element.findall('./*'):
            if xml_child_elem.tag == 'SUB':
                elem.append(self._read_subscript(xml_child_elem))
            elif xml_child_elem.tag == 'SUP':
                elem.append(self._read_superscript(xml_child_elem))
            else:
                self._raise_parse_error(
                    xml_child_elem, f"Invalid element: <{xml_child_elem.tag}>")
            if xml_child_elem.tail:
                elem.append(xml_element.text)

    def _read_describable(self,
                          child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:DESCRIBABLE
        """
        xml_child = child_elements.get("DESC")
        if xml_child is not None:
            data["desc"] = self._read_multi_language_overview_paragraph(xml_child)
        xml_child = child_elements.get("CATEGORY")
        if xml_child is not None:
            data["category"] = xml_child.text
        xml_child = child_elements.get("INTRODUCTION")
        if xml_child is not None:
            data["introduction"] = self._read_documentation_block(xml_child)
        child_elements.skip("ADMIN-DATA")  # To be implemented

    def _read_language_plain_text(self, xml_element: ElementTree.Element) -> ar_element.LanguagePlainText:
        """
        Writes complex type AR:L-PLAIN-TEXT
        Tag variants: 'L-10'
        """
        data = {}
        self._read_language_specific_attr(xml_element.attrib, data)
        return ar_element.LanguagePlainText(data["language"], xml_element.text)

    def _read_multi_language_plain_text(self, xml_element: ElementTree.Element) -> ar_element.MultiLanguagePlainText:
        """
        Writes complex type AR:MULTI-LANGUAGE-PLAIN-TEXT
        Tag variants: 'USED-LANGUAGES' | 'TEX-MATH' | 'GENERIC-MATH'
        """
        data = {}
        elements = []
        for xml_child in xml_element.findall("./L-10"):
            elements.append(self._read_language_plain_text(xml_child))
        data["elements"] = elements
        return ar_element.MultiLanguagePlainText(**data)

    def _read_date(self, xml_element: ElementTree.Element) -> ar_element.Date:
        """
        Reads complex type AR:DATE
        Tag variant: 'DATE'
        """
        return ar_element.Date(xml_element.text)

    def _read_revision_label_string(self, xml_element: ElementTree.Element) -> ar_element.RevisionLabelString:
        """
        Reads complex type AR:REVISION-LABEL-STRING
        Tag variants: 'AR-RELEASE-VERSION' | 'REVISION-LABEL' | 'REVISION-LABEL-P1' | 'REVISION-LABEL-P2' |
                  'ECUC-DEF-EDITION' | 'SW-VERSION' | 'PRODUCT-RELEASE' | 'MINIMUM-SUPPORTED-UCM-VERSION' |
                  'ECU-EXTRACT-VERSION' | 'SYSTEM-VERSION'
        """
        return ar_element.RevisionLabelString(xml_element.text)

    # --- CompuMethod elements

    def _read_compu_method(self, xml_element: ElementTree.Element) -> ar_element.CompuMethod:
        """
        Reads Complex type AR:COMPU-METHOD
        Type: Concrete
        Tag variants: 'COMPU-METHOD'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_compu_method_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompuMethod(**data)

    def _read_compu_method_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group type AR:COMPU-METHOD
        Type: Abstract
        Tag variants: 'COMPU-METHOD'
        """
        xml_child = child_elements.get("DISPLAY-FORMAT")
        if xml_child is not None:
            data["display_format"] = xml_child.text
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        xml_child = child_elements.get("COMPU-INTERNAL-TO-PHYS")
        if xml_child is not None:
            data["int_to_phys"] = self._read_computation(xml_child)
        xml_child = child_elements.get("COMPU-PHYS-TO-INTERNAL")
        if xml_child is not None:
            data["phys_to_int"] = self._read_computation(xml_child)

    def _read_computation(self, xml_element: ElementTree.Element) -> ar_element.Computation:
        """
        Reads AR:COMPUTATION
        Type: Concrete
        Tag variants: 'COMPU-INT-TO-PHYS', 'COMPU-PHYS-TO-INT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('COMPU-SCALES')
        if xml_child is not None:
            data["compu_scales"] = self._read_compu_scales(xml_child)
        xml_child = child_elements.get('COMPU-DEFAULT-VALUE')
        if xml_child is not None:
            data["default_value"] = self._read_compu_const(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.Computation(**data)

    def _read_compu_scales(self, xml_element: ElementTree.Element) -> list[ar_element.CompuScale]:
        """
        Reads AR:COMPU-SCALES
        Type: Concrete
        Tag variants: 'COMPU-SCALES'
        """
        compu_scales = []
        for xml_child in xml_element.findall("./COMPU-SCALE"):
            compu_scales.append(self._read_compu_scale(xml_child))
        return compu_scales

    def _read_compu_scale(self, xml_element: ElementTree.Element) -> list[ar_element.CompuScale]:
        """
        Reads AR:COMPU-SCALE
        Type: Concrete
        Tag variants: 'COMPU-SCALE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text
        xml_child = child_elements.get("SYMBOL")
        if xml_child is not None:
            data["symbol"] = xml_child.text
        xml_child = child_elements.get("DESC")
        if xml_child is not None:
            data["desc"] = self._read_multi_language_overview_paragraph(xml_child)
        xml_child = child_elements.get("MASK")
        if xml_child is not None:
            data["mask"] = int(xml_child.text)
        xml_child = child_elements.get("LOWER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["lower_limit"] = limit
            data["lower_limit_type"] = interval_type
        xml_child = child_elements.get("UPPER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["upper_limit"] = limit
            data["upper_limit_type"] = interval_type
        xml_child = child_elements.get("COMPU-INVERSE-VALUE")
        if xml_child is not None:
            data["inverse_value"] = self._read_compu_const(xml_child)
        compu_const_xml = child_elements.get("COMPU-CONST")
        compu_rational_xml = child_elements.get("COMPU-RATIONAL-COEFFS")
        if (compu_const_xml is not None) and (compu_rational_xml is not None):
            raise ar_exception.ParseError("Can't define both COMPU-CONST and COMPU-RATIONAL-COEFFS"
                                          "in the same COMPU-SCALE element")
        if compu_const_xml is not None:
            data["content"] = self._read_compu_const(compu_const_xml)
        elif compu_rational_xml is not None:
            data["content"] = self._read_compu_rational(compu_rational_xml)
        child_elements.skip("VARIATION-POINT")  # Not supported
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompuScale(**data)

    def _read_limit(self, xml_element: ElementTree.Element) -> tuple[int | float, ar_enum.IntervalType]:
        interval_type = xml_element.attrib.get("INTERVAL-TYPE")
        if interval_type is not None:
            interval_type = ar_enum.xml_to_enum("IntervalType", interval_type)
        else:
            # If the attribute is missing the interval shall be considered as "CLOSED"
            interval_type = ar_enum.IntervalType.CLOSED
        limit = self._read_number(xml_element.text)
        return limit, interval_type

    def _read_compu_const(self, xml_element: ElementTree.Element) -> ar_element.CompuConst:
        """
        Reads AR:COMPU-CONST
        Type: Concrete
        Tag variants: 'COMPU-CONST'
        """
        v_xml = xml_element.find("V")
        vt_xml = xml_element.find("VT")
        if (v_xml is not None) and (vt_xml is not None):
            raise ar_exception.ParseError("Can't define both V and VT"
                                          "in the same COMPU-CONST element")
        if v_xml is not None:
            value = self._read_number(v_xml.text)
        elif vt_xml is not None:
            value = vt_xml.text
        else:
            raise ar_exception.ParseError("COMPU-CONST without value isn't supported")
        return ar_element.CompuConst(value)

    def _read_compu_rational(self, xml_element: ElementTree.Element) -> ar_element.CompuRational:
        """
        Reads AR:COMPU-RATIONAL-COEFFS
        Type: Concrete
        Tag variants: 'COMPU-RATIONAL-COEFFS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('COMPU-NUMERATOR')
        if xml_child is not None:
            data['numerator'] = self._read_compu_numerator_denominator_values(xml_child)
        xml_child = child_elements.get('COMPU-DENOMINATOR')
        if xml_child is not None:
            data['denominator'] = self._read_compu_numerator_denominator_values(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompuRational(**data)

    def _read_compu_numerator_denominator_values(self, xml_element: ElementTree.Element) -> tuple:
        """
        Reads AR:COMPU-NOMINATOR-DENOMINATOR
        Type: Concrete
        Tag variants: 'COMPU-NUMERATOR' | 'COMPU-DENOMINATOR'
        """
        values = []
        for xml_child in xml_element.findall('./V'):
            num_val = ar_element.NumericalValue(xml_child.text)
            values.append(num_val.value)
        return tuple(values)

    # --- Constraint elements

    def _read_data_constraint(self, xml_element: ElementTree.Element) -> ar_element.DataConstraint:
        """
        Writes complex type AR:DATA-CONSTRS
        Type: Concrete
        Tag variants: 'DATA-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_data_constraint_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataConstraint(**data)

    def _read_data_constraint_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group type AR:DATA-CONSTRS
        Type: Abstract
        """
        xml_child = child_elements.get("DATA-CONSTR-RULES")
        if xml_child is not None:
            rules = []
            for xml_data_constr_rule in xml_child.findall("./DATA-CONSTR-RULE"):
                rules.append(self._read_data_constraint_rule(xml_data_constr_rule))
            data["rules"] = rules

    def _read_data_constraint_rule(self, xml_element: ElementTree.Element) -> ar_element.DataConstraintRule:
        """
        Writes complex type AR:INTERNAL-CONSTRS
        Type: Concrete
        Tag variants: 'INTERNAL-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONSTR-LEVEL")
        if xml_child is not None:
            data["level"] = int(xml_child.text)
        xml_child = child_elements.get("PHYS-CONSTRS")
        if xml_child is not None:
            data["physical"] = self._read_physical_constraint(xml_child)
        xml_child = child_elements.get("INTERNAL-CONSTRS")
        if xml_child is not None:
            data["internal"] = self._read_internal_constraint(xml_child)
        return ar_element.DataConstraintRule(**data)

    def _read_internal_constraint(self, xml_element: ElementTree.Element) -> ar_element.InternalConstraint:
        """
        Writes complex type AR:INTERNAL-CONSTRS
        Type: Concrete
        Tag variants: 'INTERNAL-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_constraint_base(child_elements, data)
        return ar_element.InternalConstraint(**data)

    def _read_physical_constraint(self, xml_element: ElementTree.Element) -> ar_element.PhysicalConstraint:
        """
        Writes complex type AR:PHYS-CONSTRS
        Type: Concrete
        Tag variants: 'PHYS-CONSTRS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_constraint_base(child_elements, data)
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        return ar_element.PhysicalConstraint(**data)

    def _read_constraint_base(self, child_elements: ChildElementMap, data: dict[str, Any]) -> None:
        """
        Reads elements common for both AR:INTERNAL-CONSTRS and AR:PHYS-CONSTRS
        Type: Abstract
        """
        xml_child = child_elements.get("LOWER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["lower_limit"] = limit
            data["lower_limit_type"] = interval_type
        xml_child = child_elements.get("UPPER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["upper_limit"] = limit
            data["upper_limit_type"] = interval_type
        xml_child = child_elements.get("SCALE-CONSTRS")
        if xml_child is not None:
            data["scale_constr"] = self._read_scale_constraints(xml_child)
        xml_child = child_elements.get("MAX-GRADIENT")
        if xml_child is not None:
            data["max_gradient"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("MAX-DIFF")
        if xml_child is not None:
            data["max_diff"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("MONOTONY")
        if xml_child is not None:
            data["monotony"] = ar_enum.xml_to_enum("Monotony", xml_child.text)

    def _read_scale_constraints(self, xml_element: ElementTree.Element) -> list[ar_element.ScaleConstraint]:
        """
        Reads SCALE-CONSTRS (list of AR:SCALE-CONSTR)
        Type: Concrete
        Tag variant: Not applicable
        """
        scale_constrs = []
        for xml_child in xml_element.findall('./SCALE-CONSTR'):
            props_conditional = self._read_scale_constraint(
                xml_child)
            scale_constrs.append(props_conditional)
        return scale_constrs

    def _read_scale_constraint(self, xml_element: ElementTree.Element) -> ar_element.ScaleConstraint:
        """
        Writes complex type AR:SCALE-CONSTR
        Type: Concrete
        Tag variants: 'SCALE-CONSTR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text
        xml_child = child_elements.get("DESC")
        if xml_child is not None:
            data["desc"] = self._read_multi_language_overview_paragraph(xml_child)
        xml_child = child_elements.get("LOWER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["lower_limit"] = limit
            data["lower_limit_type"] = interval_type
        xml_child = child_elements.get("UPPER-LIMIT")
        if xml_child is not None:
            limit, interval_type = self._read_limit(xml_child)
            data["upper_limit"] = limit
            data["upper_limit_type"] = interval_type
        return ar_element.ScaleConstraint(**data)

    # --- Unit elements

    def _read_unit(self, xml_element: ElementTree.Element) -> ar_element.Unit:
        """
        Reads Complex type AR:UNIT
        Type: Concrete
        Tag variants: 'UNIT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_unit_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.Unit(**data)

    def _read_unit_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-ADDR-METHOD
        Type: Utility
        """
        xml_child = child_elements.get("DISPLAY-NAME")
        if xml_child is not None:
            data["display_name"] = self._read_single_language_unit_names(xml_child)
        xml_child = child_elements.get("FACTOR-SI-TO-UNIT")
        if xml_child is not None:
            data["factor"] = float(xml_child.text)
        xml_child = child_elements.get("OFFSET-SI-TO-UNIT")
        if xml_child is not None:
            data["offset"] = float(xml_child.text)
        xml_child = child_elements.get("PHYSICAL-DIMENSION-REF")
        if xml_child is not None:
            data["physical_dimension_ref"] = self._read_physical_dimension_ref(xml_child)

    # --- Common structure elements

    def _read_data_filter(self, xml_element: ElementTree.Element) -> ar_element.DataFilter:
        """
        Reads complex type AR:DATA-FILTER
        Tag variants: 'FILTER' | 'DATA-FILTER'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("DATA-FILTER-TYPE")
        if xml_child is not None:
            data["data_filter_type"] = ar_enum.xml_to_enum("DataFilterType", xml_child.text)
        xml_child = child_elements.get("MASK")
        if xml_child is not None:
            data["mask"] = self._read_integer(xml_child.text)
        xml_child = child_elements.get("MAX")
        if xml_child is not None:
            data["max_val"] = self._read_integer(xml_child.text)
        xml_child = child_elements.get("MIN")
        if xml_child is not None:
            data["min_val"] = self._read_integer(xml_child.text)
        xml_child = child_elements.get("OFFSET")
        if xml_child is not None:
            data["offset"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("PERIOD")
        if xml_child is not None:
            data["period"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("X")
        if xml_child is not None:
            data["x"] = self._read_integer(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataFilter(**data)

    def _read_engineering_object(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ENGINEERING-OBJECT
        """
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text
        xml_child = child_elements.get("CATEGORY")
        if xml_child is not None:
            data["category"] = xml_child.text

    def _read_autosar_engineering_object(self, xml_element: ElementTree.Element) -> ar_element.AutosarEngineeringObject:
        """
        Complex type AR:AUTOSAR-ENGINEERING-OBJECT
        Tag variants: 'AUTOSAR-ENGINEERING-OBJECT' | 'ARTIFACT-DESCRIPTOR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_engineering_object(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AutosarEngineeringObject(**data)

    def _read_code(self, xml_element: ElementTree.Element) -> ar_element.Code:
        """
        Reads complex type AR:CODE
        Tag variants: 'CODE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        xml_child = child_elements.get('ARTIFACT-DESCRIPTORS')
        if xml_child is not None:
            elements = []
            for xml_grand_child in xml_child.findall("./AUTOSAR-ENGINEERING-OBJECT"):
                elements.append(self._read_autosar_engineering_object(xml_grand_child))
            data["artifact_descriptors"] = elements
        child_elements.skip('CALLBACK-HEADER-REFS')  # Not yet supported
        self._report_unprocessed_elements(child_elements)
        return ar_element.Code(**data)

    def _read_implementation(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION
        """
        child_elements.skip("BUILD-ACTION-MANIFESTS")
        xml_child = child_elements.get("CODE-DESCRIPTORS")
        if xml_child is not None:
            elements = []
            for xml_grand_child in xml_child.findall("./CODE"):
                elements.append(self._read_code(xml_grand_child))
            data["code_descriptors"] = elements
        child_elements.skip("COMPILERS")
        child_elements.skip("GENERATED-ARTIFACTS")
        child_elements.skip("HW-ELEMENT-REFS")
        child_elements.skip("LINKERS")
        child_elements.skip("MC-SUPPORT")
        child_elements.skip("PROGRAMMING-LANGUAGE")
        child_elements.skip("REQUIRED-ARTIFACTS")
        child_elements.skip("REQUIRED-GENERATOR-TOOLS")
        child_elements.skip("RESOURCE-CONSUMPTION")
        child_elements.skip("SW-VERSION")
        child_elements.skip("SWC-BSW-MAPPING-REF")
        child_elements.skip("USED-CODE-GENERATOR")
        child_elements.skip("VENDOR-ID")

    # --- Data type elements

    def _read_sw_addr_method(self, xml_element: ElementTree.Element) -> ar_element.SwAddrMethod:
        """
        Reads Complex type AR:SW-ADDR-METHOD
        Type: Concrete
        Tag variants: 'SW-ADDR-METHOD'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_addr_method_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwAddrMethod(**data)

    def _read_sw_addr_method_group(self, child_elements: ChildElementMap, _: dict) -> None:
        """
        Reads group AR:SW-ADDR-METHOD
        Type: Utility
        """
        child_elements.skip('MEMORY-ALLOCATION-KEYWORD-POLICY')  # Not implemented
        child_elements.skip('OPTIONS')  # Not implemented
        child_elements.skip('SECTION-INITIALIZATION-POLICY')  # Not implemented
        child_elements.skip('SECTION-TYPE')  # Not Implemented

    def _read_sw_base_type(self, xml_element: ElementTree.Element) -> ar_element.SwBaseType:
        """
        Reads Complex-type AR:SW-BASE-TYPE
        Type: Concrete
        Tag variants: 'SW-BASE-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_base_type(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwBaseType(**data)

    def _read_base_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads groups AR:BASE-TYPE and AR:BASE-TYPE-DIRECT-DEFINITION
        Type: Abstract
        """
        xml_child: ElementTree.Element | None = None
        xml_child = child_elements.get('BASE-TYPE-SIZE')
        if xml_child is not None:
            data['size'] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get('MAX-BASE-TYPE-SIZE')
        if xml_child is not None:
            data['max_size'] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get('BASE-TYPE-ENCODING')
        if xml_child is not None:
            data['encoding'] = str(xml_child.text)
        xml_child = child_elements.get('MEM-ALIGNMENT')
        if xml_child is not None:
            data['alignment'] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get('BYTE-ORDER')
        if xml_child is not None:
            data['byte_order'] = ar_enum.xml_to_enum(
                'ByteOrder', xml_child.text)
        xml_child = child_elements.get('NATIVE-DECLARATION')
        if xml_child is not None:
            data['native_declaration'] = str(xml_child.text)

    def _read_sw_bit_representation(self, xml_element: ElementTree.Element) -> ar_element.SwBitRepresentation:
        """
        Reads AR:SW-BIT-REPRESENTATION
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        bit_position = child_elements.get('BIT-POSITION')
        if bit_position is not None:
            data['position'] = int(bit_position.text)
        number_of_bits = child_elements.get('NUMBER-OF-BITS')
        if number_of_bits is not None:
            data['num_bits'] = int(number_of_bits.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwBitRepresentation(**data)

    def _read_sw_data_def_props(self, xml_element: ElementTree.Element) -> ar_element.SwDataDefProps:
        """
        Reads complex type AR:SW-DATA-DEF-PROPS
        Type: Concrete
        Tag Variants: 'SW-DATA-DEF-PROPS', 'NETWORK-REPRESENTATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SW-DATA-DEF-PROPS-VARIANTS")
        if xml_child is not None:
            data['variants'] = self._read_sw_data_def_props_variants(xml_child)
        return ar_element.SwDataDefProps(**data)

    def _read_sw_data_def_props_variants(self,
                                         xml_elem: ElementTree.Element) -> list[ar_element.SwDataDefPropsConditional]:
        """
        Reads SW-DATA-DEF-PROPS-VARIANTS
        Type: Concrete
        """
        variants = []
        for xml_child in xml_elem.findall('./SW-DATA-DEF-PROPS-CONDITIONAL'):
            props_conditional = self._read_sw_data_def_props_conditional(
                xml_child)
            variants.append(props_conditional)
        return variants

    def _read_sw_data_def_props_conditional(self,
                                            xml_elem: ElementTree.Element) -> ar_element.SwDataDefPropsConditional:
        """
        Reads complexType AR:SW-DATA-DEF-PROPS-CONDITIONAL
        Type: Concrete
        Tag variants: 'AR:SW-DATA-DEF-PROPS-CONDITIONAL'
        """
        data = {}
        child_elements = ChildElementMap(xml_elem)
        self._read_sw_data_def_props_content(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwDataDefPropsConditional(**data)

    def _read_sw_data_def_props_content(self, child_elements: ChildElementMap, data: dict[str, Any]) -> None:
        """
        Reads Group SW-DATA-DEF-PROPS-CONTENT
        Type: Abstract
        """
        xml_child: ElementTree.Element = child_elements.get('DISPLAY-PRESENTATION')
        if xml_child is not None:
            data['display_presentation'] = ar_enum.xml_to_enum(
                'DisplayPresentation', xml_child.text)
        xml_child = child_elements.get('STEP-SIZE')
        if xml_child is not None:
            data['step_size'] = float(xml_child.text)
        # Variant-handling not supported
        child_elements.skip('SW-VALUE-BLOCK-SIZE-MULTS')
        xml_child = child_elements.get('ANNOTATIONS')
        if xml_child is not None:
            data['annotations'] = self._read_annotations(xml_child)
        xml_child = child_elements.get('SW-ADDR-METHOD-REF')
        if xml_child is not None:
            data['sw_addr_method_ref'] = self._read_sw_addr_method_ref(xml_child)
        xml_child = child_elements.get('SW-ALIGNMENT')
        if xml_child is not None:
            try:
                sw_alignment = int(xml_child.text, 0)
            except ValueError:
                sw_alignment = xml_child.text
            data['alignment'] = sw_alignment
        xml_child = child_elements.get('BASE-TYPE-REF')
        if xml_child is not None:
            data['base_type_ref'] = self._read_sw_base_type_ref(xml_child)
        xml_child = child_elements.get('SW-BIT-REPRESENTATION')
        if xml_child is not None:
            data['bit_representation'] = self._read_sw_bit_representation(
                xml_child)
        xml_child = child_elements.get('SW-CALIBRATION-ACCESS')
        if xml_child is not None:
            data['calibration_access'] = ar_enum.xml_to_enum('SwCalibrationAccess',
                                                             xml_child.text)
        xml_child = child_elements.get('SW-TEXT-PROPS')
        if xml_child is not None:
            data['text_props'] = self._read_sw_text_props(xml_child)
        xml_child = child_elements.get('COMPU-METHOD-REF')
        if xml_child is not None:
            data['compu_method_ref'] = self._read_compu_method_ref(xml_child)
        xml_child = child_elements.get('DATA-CONSTR-REF')
        if xml_child is not None:
            data['data_constraint_ref'] = self._read_data_constraint_ref(xml_child)
        xml_child = child_elements.get('DISPLAY-FORMAT')
        if xml_child is not None:
            data['display_format'] = xml_child.text
        xml_child = child_elements.get('IMPLEMENTATION-DATA-TYPE-REF')
        if xml_child is not None:
            data['impl_data_type_ref'] = self._read_impl_data_type_ref(xml_child)
        xml_child = child_elements.get('SW-IMPL-POLICY')
        if xml_child is not None:
            data['impl_policy'] = ar_enum.xml_to_enum('SwImplPolicy', xml_child.text)
        xml_child = child_elements.get('ADDITIONAL-NATIVE-TYPE-QUALIFIER')
        if xml_child is not None:
            data['additional_native_type_qualifier'] = xml_child.text
        xml_child = child_elements.get('SW-INTENDED-RESOLUTION')
        if xml_child is not None:
            data['intended_resolution'] = self._read_number(xml_child.text)
        xml_child = child_elements.get('SW-INTERPOLATION-METHOD')
        if xml_child is not None:
            data['interpolation_method'] = xml_child.text
        xml_child = child_elements.get('SW-IS-VIRTUAL')
        if xml_child is not None:
            data['is_virtual'] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get('SW-POINTER-TARGET-PROPS')
        if xml_child is not None:
            data['ptr_target_props'] = self._read_sw_pointer_target_props(xml_child)
        xml_child = child_elements.get('UNIT-REF')
        if xml_child is not None:
            data['unit_ref'] = self._read_unit_ref(xml_child)

    def _read_sw_text_props(self, xml_element: ElementTree.Element) -> ar_element.SwBitRepresentation:
        """
        Reads AR:SW-TEXT-PROPS
        Type: Concrete
        Tag variants: 'SW-TEXT-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('ARRAY-SIZE-SEMANTICS')
        if xml_child is not None:
            data['array_size_semantics'] = ar_enum.xml_to_enum('ArraySizeSemantics', xml_child.text)
        xml_child = child_elements.get('SW-MAX-TEXT-SIZE')
        if xml_child is not None:
            data['max_text_size'] = self._read_integer(xml_child.text)
        xml_child = child_elements.get('BASE-TYPE-REF')
        if xml_child is not None:
            data['base_type_ref'] = self._read_sw_base_type_ref(xml_child)
        xml_child = child_elements.get('SW-FILL-CHARACTER')
        if xml_child is not None:
            data['fill_char'] = self._read_integer(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwTextProps(**data)

    def _read_sw_pointer_target_props(self, xml_element: ElementTree.Element) -> ar_element.SwPointerTargetProps:
        """
        Reads AR:SW-POINTER-TARGET-PROPS
        Type: Concrete
        Tag variants: 'SW-POINTER-TARGET-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('TARGET-CATEGORY')
        if xml_child is not None:
            data['target_category'] = xml_child.text
        xml_child = child_elements.get('SW-DATA-DEF-PROPS')
        if xml_child is not None:
            data['sw_data_def_props'] = self._read_sw_data_def_props(xml_child)
        xml_child = child_elements.get('FUNCTION-POINTER-SIGNATURE-REF')
        if xml_child is not None:
            data['function_ptr_signature_ref'] = self._read_function_ptr_signature_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwPointerTargetProps(**data)

    def _read_symbol_props(self, xml_element: ElementTree.Element) -> ar_element.SymbolProps:
        """
        Reads complex type AR:SYMBOL-PROPS
        Type: Concrete
        Tag variants: 'SYMBOL-PROPS', 'EVENT-SYMBOL-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_implementation_props(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SymbolProps(**data)

    def _read_implementation_props(self,
                                   child_elements: ChildElementMap,
                                   data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION-PROPS
        Type: Abstract
        """
        xml_child = child_elements.get('SYMBOL')
        if xml_child is not None:
            data['symbol'] = xml_child.text

    def _read_implementation_data_type_element(self,
            xml_element: ElementTree.Element) -> ar_element.ImplementationDataTypeElement:  # noqa E128
        """
        Reads complex type AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
        Type: Concrete
        Tag variants: 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_implementation_data_type_element_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ImplementationDataTypeElement(**data)

    def _read_implementation_data_type_element_group(self,
                                                     child_elements: ChildElementMap,
                                                     data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION-DATA-TYPE-ELEMENT
        Type: Abstract
        """
        xml_child = child_elements.get("ARRAY-IMPL-POLICY")
        if xml_child is not None:
            data["array_impl_policy"] = ar_enum.xml_to_enum("ArrayImplPolicy", xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE")
        if xml_child is not None:
            data["array_size"] = int(xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE-HANDLING")
        if xml_child is not None:
            data["array_size_handling"] = ar_enum.xml_to_enum("ArraySizeHandling", xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE-SEMANTICS")
        if xml_child is not None:
            data["array_size_semantics"] = ar_enum.xml_to_enum("ArraySizeSemantics", xml_child.text)
        xml_child = child_elements.get("IS-OPTIONAL")
        if xml_child is not None:
            data["is_optional"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("SUB-ELEMENTS")
        if xml_child is not None:
            sub_elements = []
            for sub_element_xml in xml_child.findall("./IMPLEMENTATION-DATA-TYPE-ELEMENT"):
                sub_elements.append(self._read_implementation_data_type_element(sub_element_xml))
            data["sub_elements"] = sub_elements
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)
        child_elements.skip("VARIATION-POINT")  # Not supported

    def _read_implementation_data_type(self, xml_element: ElementTree.Element) -> ar_element.ImplementationDataType:
        """
        Reads complex type AR:IMPLEMENTATION-DATA-TYPE
        Type: Concrete
        Tag Variants: 'IMPLEMENTATION-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._read_implementation_data_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ImplementationDataType(**data)

    def _read_implementation_data_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:IMPLEMENTATION-DATA-TYPE
        Type: Abstract
        """
        xml_child = child_elements.get("DYNAMIC-ARRAY-SIZE-PROFILE")
        if xml_child is not None:
            data["dynamic_array_size_profile"] = xml_child.text
        xml_child = child_elements.get("IS-STRUCT-WITH-OPTIONAL-ELEMENT")
        if xml_child is not None:
            data["is_struct_with_optional_element"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("SUB-ELEMENTS")
        if xml_child is not None:
            sub_elements = []
            for sub_element_xml in xml_child.findall("./IMPLEMENTATION-DATA-TYPE-ELEMENT"):
                sub_elements.append(self._read_implementation_data_type_element(sub_element_xml))
            data["sub_elements"] = sub_elements
        xml_child = child_elements.get("SYMBOL-PROPS")
        if xml_child is not None:
            data["symbol_props"] = self._read_symbol_props(xml_child)
        xml_child = child_elements.get("TYPE-EMITTER")
        if xml_child is not None:
            data["type_emitter"] = xml_child.text

    def _read_autosar_data_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AUTOSAR-DATA-TYPE
        Type: Abstract
        """
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)

    def _read_data_prototype(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:DATA-PROTOTYPE
        Type: Abstract
        """
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)

    def _read_application_primitive_data_type(
            self,
            xml_element: ElementTree.Element) -> ar_element.ApplicationPrimitiveDataType:
        """
        Reads complex type AR:APPLICATION-PRIMITIVE-DATA-TYPE
        Type: Concrete
        Tag variants: 'APPLICATION-PRIMITIVE-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationPrimitiveDataType(**data)

    def _read_application_composite_element_data_prototype(
            self,
            child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE
        Type: Abstract
        """
        xml_child = child_elements.get("TYPE-TREF")
        if xml_child is not None:
            data["type_ref"] = self._read_application_data_type_ref(xml_child)

    def _read_autosar_data_prototype(
            self,
            child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AUTOSAR-DATA-PROTOTYPE
        Type: Abstract
        """
        xml_child = child_elements.get("TYPE-TREF")
        if xml_child is not None:
            data["type_ref"] = self._read_autosar_data_type_ref(xml_child)

    def _read_application_array_element(self, xml_element: ElementTree.Element) -> ar_element.ApplicationArrayElement:
        """
        Reads complex type AR:APPLICATION-ARRAY-ELEMENT
        Type: Concrete
        Tag variants: 'ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_application_composite_element_data_prototype(child_elements, data)
        self._read_application_array_element_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationArrayElement(**data)

    def _read_application_array_element_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads complex type AR:APPLICATION-ARRAY-ELEMENT
        Type: Abstract
        """
        xml_child = child_elements.get("ARRAY-SIZE-HANDLING")
        if xml_child is not None:
            data["array_size_handling"] = ar_enum.xml_to_enum("ArraySizeHandling", xml_child.text)
        xml_child = child_elements.get("ARRAY-SIZE-SEMANTICS")
        if xml_child is not None:
            data["array_size_semantics"] = ar_enum.xml_to_enum("ArraySizeSemantics", xml_child.text)
        xml_child = child_elements.get("INDEX-DATA-TYPE-REF")
        if xml_child is not None:
            data["index_data_type_ref"] = self._read_index_data_type_ref(xml_child)
        xml_child = child_elements.get("MAX-NUMBER-OF-ELEMENTS")
        if xml_child is not None:
            data["max_number_of_elements"] = int(xml_child.text)

    def _read_application_record_element(self, xml_element: ElementTree.Element) -> ar_element.ApplicationRecordElement:
        """
        Reads complex type AR:APPLICATION-RECORD-ELEMENT
        Type: Concrete
        Tag variants: 'APPLICATION-RECORD-ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_application_composite_element_data_prototype(child_elements, data)
        self._read_application_record_element_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationRecordElement(**data)

    def _read_application_record_element_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads complex type AR:APPLICATION-RECORD-ELEMENT
        Type: Abstract
        """
        xml_child = child_elements.get("IS-OPTIONAL")
        if xml_child is not None:
            data["is_optional"] = self._read_boolean(xml_child.text)

    def _read_application_array_data_type(
            self,
            xml_element: ElementTree.Element) -> ar_element.ApplicationArrayDataType:
        """
        Reads complex type AR:APPLICATION-ARRAY-DATA-TYPE
        Type: Concrete
        Tag variants: 'APPLICATION-ARRAY-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._read_application_array_data_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationArrayDataType(**data)

    def _read_application_array_data_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-ARRAY-DATA-TYPE
        """
        xml_child = child_elements.get("DYNAMIC-ARRAY-SIZE-PROFILE")
        if xml_child is not None:
            data["dynamic_array_size_profile"] = xml_child.text
        xml_child = child_elements.get("ELEMENT")
        if xml_child is not None:
            data["element"] = self._read_application_array_element(xml_child)

    def _read_application_record_data_type(
            self,
            xml_element: ElementTree.Element) -> ar_element.ApplicationRecordDataType:
        """
        Reads complex type AR:APPLICATION-RECORD-DATA-TYPE
        Type: Concrete
        Tag variants: 'APPLICATION-RECORD-DATA-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_autosar_data_type(child_elements, data)
        self._read_application_record_data_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationRecordDataType(**data)

    def _read_application_record_data_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-RECORD-DATA-TYPE
        """
        xml_child = child_elements.get("ELEMENTS")
        if xml_child is not None:
            elements = []
            for xml_record_element in xml_child.findall("./APPLICATION-RECORD-ELEMENT"):
                elements.append(self._read_application_record_element(xml_record_element))
            data["elements"] = elements

    def _read_data_type_map(self, xml_element: ElementTree.Element) -> ar_element.DataTypeMap:
        """
        Reads AR:DATA-TYPE-MAP
        Type: Concrete
        Tag variants: 'DATA-TYPE-MAP'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("APPLICATION-DATA-TYPE-REF")
        if xml_child is not None:
            data["appl_data_type_ref"] = self._read_application_data_type_ref(xml_child)
        xml_child = child_elements.get("IMPLEMENTATION-DATA-TYPE-REF")
        if xml_child is not None:
            data["impl_data_type_ref"] = self._read_impl_data_type_ref(xml_child)
        return ar_element.DataTypeMap(**data)

    def _read_data_type_mapping_set(self, xml_element: ElementTree.Element) -> ar_element.DataTypeMappingSet:
        """
        Reads AR:DATA-TYPE-MAPPING-SET
        Type: Concrete
        Tag variants: 'DATA-TYPE-MAPPING-SET'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_read_data_type_mapping_set_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.DataTypeMappingSet(**data)
        return element

    def _read_read_data_type_mapping_set_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:DATA-TYPE-MAPPING-SET
        Type: Abstract
        """
        xml_child = child_elements.get("DATA-TYPE-MAPS")
        if xml_child is not None:
            data_type_maps = []
            for xml_data_type_map_element in xml_child.findall("./DATA-TYPE-MAP"):
                data_type_maps.append(self._read_data_type_map(xml_data_type_map_element))
            data["data_type_maps"] = data_type_maps

    def _read_value_list(self, xml_element: ElementTree.Element) -> ar_element.ValueList:
        """
        Reads complex-type AR:VALUE-LIST
        Type: Concrete
        Tag variants: 'SW-ARRAYSIZE'
        """
        values = []
        data = {"values": values}
        for xml_value in xml_element.findall("./V"):
            number = ar_element.NumericalValue(xml_value.text)
            if number.value_format in (ar_enum.ValueFormat.HEXADECIMAL,
                                       ar_enum.ValueFormat.BINARY,
                                       ar_enum.ValueFormat.SCIENTIFIC):
                values.append(number)
            else:
                values.append(number.value)
        element = ar_element.ValueList(**data)
        return element

    def _read_parameter_data_prototype(self, elem: ElementTree.Element) -> ar_element.ParameterDataPrototype:
        """
        Reads complex-type AR:PARAMETER-DATA-PROTOTYPE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_autosar_data_prototype(child_elements, data)
        self._read_parameter_data_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ParameterDataPrototype(**data)

    def _read_parameter_data_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PARAMETER-DATA-PROTOTYPE
        """
        xml_child = child_elements.get('INIT-VALUE')
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        child_elements.skip('VARIATION-POINT')  # Not supported

    def _read_variable_data_prototype(self, elem: ElementTree.Element) -> ar_element.VariableDataPrototype:
        """
        Reads complex-type AR:VARIABLE-DATA-PROTOTYPE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_autosar_data_prototype(child_elements, data)
        self._read_variable_data_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.VariableDataPrototype(**data)

    def _read_variable_data_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:VARIABLE-DATA-PROTOTYPE
        """
        xml_child = child_elements.get('INIT-VALUE')
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        child_elements.skip('VARIATION-POINT')  # Not supported

    def _read_argument_data_prototype(self, elem: ElementTree.Element) -> ar_element.ArgumentDataPrototype:
        """
        Reads complex-type AR:ARGUMENT-DATA-PROTOTYPE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(elem)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, elem.attrib, data)
        self._read_data_prototype(child_elements, data)
        self._read_autosar_data_prototype(child_elements, data)
        self._read_argument_data_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ArgumentDataPrototype(**data)

    def _read_argument_data_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ARGUMENT-DATA-PROTOTYPE
        """
        xml_child = child_elements.get('DIRECTION')
        if xml_child is not None:
            data["direction"] = ar_enum.xml_to_enum("ArgumentDirection", xml_child.text)
        xml_child = child_elements.get('SERVER-ARGUMENT-IMPL-POLICY')
        if xml_child is not None:
            data["server_arg_impl_policy"] = ar_enum.xml_to_enum("ServerArgImplPolicy", xml_child.text)
        child_elements.skip("TYPE-BLUEPRINTS")  # Not supported
        child_elements.skip("VARIATION-POINT")  # Not supported

    def _read_mode_request_type_map(self, xml_element: ElementTree.Element) -> ar_element.ModeRequestTypeMap:
        """
        Reads complex type AR:MODE-REQUEST-TYPE-MAP
        Tag variants: 'MODE-REQUEST-TYPE-MAP'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('IMPLEMENTATION-DATA-TYPE-REF')
        if xml_child is not None:
            data['implementation_data_type'] = self._read_impl_data_type_ref(xml_child)
        xml_child = child_elements.get('MODE-GROUP-REF')
        if xml_child is not None:
            data['mode_group'] = self._read_mode_declaration_group_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeRequestTypeMap(**data)

    # --- Reference elements

    def _read_base_ref_attributes(self, attr: dict, data: dict) -> None:
        """
        Reads DEST attribute
        """
        data['dest'] = attr.get('DEST', None)
        if data['dest'] is None:
            raise ar_exception.ParseError("Missing required attribute 'DEST'")

    def _read_ref_dest(self, xml_elem: ElementTree.Element) -> ar_enum.IdentifiableSubTypes:
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        return ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)

    def _read_compu_method_ref(self, xml_elem: ElementTree.Element) -> ar_element.CompuMethodRef:
        """
        Reads AR:COMPU-METHOD-REF
        Tag Variants: 'COMPU-METHOD-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'COMPU-METHOD':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'COMPU-METHOD', got '{data['dest']}'")
        return ar_element.CompuMethodRef(xml_elem.text)

    def _read_data_constraint_ref(self, xml_elem: ElementTree.Element) -> ar_element.DataConstraintRef:
        """
        Reads AR:DATA-CONSTR-REF
        Type: Concrete
        Tag Variants: 'DATA-CONSTR-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'DATA-CONSTR':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'DATA-CONSTR', got '{data['dest']}'")
        return ar_element.DataConstraintRef(xml_elem.text)

    def _read_function_ptr_signature_ref(self, xml_elem: ElementTree.Element) -> ar_element.FunctionPtrSignatureRef:
        """
        Reads AR:FUNCTION-POINTER-SIGNATURE-REF
        Type: Concrete
        Tag Variants: 'FUNCTION-POINTER-SIGNATURE-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'BSW-MODULE-ENTRY':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'BSW-MODULE-ENTRY', got '{data['dest']}'")
        return ar_element.FunctionPtrSignatureRef(xml_elem.text)

    def _read_impl_data_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.ImplementationDataTypeRef:
        """
        Reads AR:IMPLEMENTATION-DATA-TYPE-REF
        Type: Concrete
        Tag Variants: 'IMPLEMENTATION-DATA-TYPE-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'IMPLEMENTATION-DATA-TYPE':
            raise ar_exception.ParseError(f"Invalid value for DEST. "
                                          f"Expected 'IMPLEMENTATION-DATA-TYPE', got '{data['dest']}'")
        return ar_element.ImplementationDataTypeRef(xml_elem.text)

    def _read_sw_base_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.SwAddrMethodRef:
        """
        Reads AR:SW-BASE-TYPE-REF
        Type: Concrete
        Tag Variants: 'SW-BASE-TYPE-REF'

        Note: the name of this complex type is anonymous in the XML achema
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-BASE-TYPE':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'SW-BASE-TYPE', got '{data['dest']}'")
        return ar_element.SwBaseTypeRef(xml_elem.text)

    def _read_sw_addr_method_ref(self, xml_elem: ElementTree.Element) -> ar_element.SwAddrMethodRef:
        """
        Reads AR:SW-ADDR-METHOD-REF
        Type: Concrete
        Tag variants: 'SW-ADDR-METHOD-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-ADDR-METHOD':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'SW-ADDR-METHOD', got '{data['dest']}'")
        return ar_element.SwAddrMethodRef(xml_elem.text)

    def _read_unit_ref(self, xml_elem: ElementTree.Element):
        """
        Reads AR:UNIT-REF
        Type: Concrete
        Tag variants: 'UNIT-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'UNIT':
            raise ar_exception.ParseError(f"Invalid value for DEST. Expected 'UNIT', got '{data['dest']}'")
        return ar_element.UnitRef(xml_elem.text)

    def _read_physical_dimension_ref(self, xml_elem: ElementTree.Element) -> ar_element.PhysicalDimensionRef:
        """
        Reads PHYSICAL-DIMENSION-REF
        Type: Concrete
        Tag variants: 'PHYSICAL-DIMENSION-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'PHYSICAL-DIMENSION':
            msg = f"Invalid value for DEST. Expected 'PHYSICAL-DIMENSION', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.PhysicalDimensionRef(xml_elem.text)

    def _read_index_data_type_ref(self, xml_elem: ElementTree.Element) -> ar_element.IndexDataTypeRef:
        """
        Reads reference to IndexDataType
        Type: Concrete
        Tag variants: 'INDEX-DATA-TYPE-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'APPLICATION-PRIMITIVE-DATA-TYPE':
            msg = f"Invalid value for DEST. Expected 'APPLICATION-PRIMITIVE-DATA-TYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.IndexDataTypeRef(xml_elem.text)

    def _read_application_data_type_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.ApplicationDataTypeRef:
        """
        Reads reference to ApplicationDataType
        Type: Concrete
        Tag variants: 'TYPE-TREF', 'APPLICATION-DATA-TYPE-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.ApplicationDataTypeRef(xml_elem.text, dest_enum)

    def _read_autosar_data_type_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.AutosarDataTypeRef:
        """
        Reads reference to AutosarDataType
        Type: Concrete
        Tag variants: 'TYPE-TREF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.AutosarDataTypeRef(xml_elem.text, dest_enum)

    def _read_constant_ref(self,
                           xml_elem: ElementTree.Element
                           ) -> ar_element.ConstantRef:
        """
        Reads reference to ConstantSpecification
        Type: Concrete
        Tag variants: 'CONSTANT-REF'
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'CONSTANT-SPECIFICATION':
            msg = f"Invalid value for DEST. Expected 'CONSTANT-SPECIFICATION', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ConstantRef(xml_elem.text)

    def _read_variable_data_prototype_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.VariableDataPrototypeRef:
        """
        Reads reference to VariableDataPrototype
        Type: Concrete
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'VARIABLE-DATA-PROTOTYPE':
            msg = f"Invalid value for DEST. Expected 'VARIABLE-DATA-PROTOTYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.VariableDataPrototypeRef(xml_elem.text)

    def _read_parameter_data_prototype_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.ParameterDataPrototypeRef:
        """
        Reads reference to ParameterDataPrototype
        Type: Concrete
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'PARAMETER-DATA-PROTOTYPE':
            msg = f"Invalid value for DEST. Expected 'PARAMETER-DATA-PROTOTYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ParameterDataPrototypeRef(xml_elem.text)

    def _read_application_error_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.ApplicationErrorRef:
        """
        Reads reference to ApplicationError
        Type: Concrete
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'APPLICATION-ERROR':
            msg = f"Invalid value for DEST. Expected 'APPLICATION-ERROR', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ApplicationErrorRef(xml_elem.text)

    def _read_mode_declaration_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.ModeDeclarationRef:
        """
        Reads reference to ModeDeclaration
        Type: Concrete
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'MODE-DECLARATION':
            msg = f"Invalid value for DEST. Expected 'MODE-DECLARATION', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ModeDeclarationRef(xml_elem.text)

    def _read_mode_declaration_group_ref(
            self,
            xml_elem: ElementTree.Element) -> ar_element.ModeDeclarationGroupRef:
        """
        Reads reference to ModeDeclarationGroup
        Type: Concrete
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'MODE-DECLARATION-GROUP':
            msg = f"Invalid value for DEST. Expected 'MODE-DECLARATION-GROUP', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ModeDeclarationGroupRef(xml_elem.text)

    def _read_mode_declaration_group_prototype_ref(self,
                                                   xml_elem: ElementTree.Element
                                                   ) -> ar_element.ModeDeclarationGroupPrototypeRef:
        """
        Reads reference to ModeDeclarationGroupPrototype
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'MODE-DECLARATION-GROUP-PROTOTYPE':
            msg = f"Invalid value for DEST. Expected 'MODE-DECLARATION-GROUP-PROTOTYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ModeDeclarationGroupPrototypeRef(xml_elem.text)

    def _read_autosar_data_prototype_ref(self,
                                         xml_elem: ElementTree.Element
                                         ) -> ar_element.AutosarDataPrototypeRef:
        """
        Reads reference to elements that derives from AutosarDataPrototype
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.AutosarDataPrototypeRef(xml_elem.text, dest_enum)

    def _read_e2e_profile_compatibility_props_ref(self,
                                                  xml_elem: ElementTree.Element
                                                  ) -> ar_element.E2EProfileCompatibilityPropsRef:
        """
        Reads reference to E2EProfileCompatibilityProps
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'E-2-E-PROFILE-COMPATIBILITY-PROPS':
            msg = f"Invalid value for DEST. Expected 'E-2-E-PROFILE-COMPATIBILITY-PROPS', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.E2EProfileCompatibilityPropsRef(xml_elem.text)

    def _read_client_server_operation_ref(self,
                                          xml_elem: ElementTree.Element
                                          ) -> ar_element.ClientServerOperationRef:
        """
        Reads reference to ClientServerOperation
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'CLIENT-SERVER-OPERATION':
            msg = f"Invalid value for DEST. Expected 'CLIENT-SERVER-OPERATION', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.ClientServerOperationRef(xml_elem.text)

    def _read_port_prototype_ref(self,
                                 xml_elem: ElementTree.Element
                                 ) -> ar_element.PortPrototypeRef:
        """
        Reads reference to ClientServerOperation
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.PortPrototypeRef(xml_elem.text, dest_enum)

    def _read_abstract_impl_data_type_element_ref(self,
                                                  xml_elem: ElementTree.Element
                                                  ) -> ar_element.AbstractImplementationDataTypeElementRef:
        """
        Reads references to AR:VARIABLE-DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.AbstractImplementationDataTypeElementRef(xml_elem.text, dest_enum)

    def _read_appl_composite_element_data_proto_ref(self,
                                                    xml_elem: ElementTree.Element
                                                    ) -> ar_element.ApplicationCompositeElementDataPrototypeRef:
        """
        Reads references to APPLICATION-COMPOSITE-ELEMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.ApplicationCompositeElementDataPrototypeRef(xml_elem.text, dest_enum)

    def _read_data_prototype_ref(self,
                                 xml_elem: ElementTree.Element
                                 ) -> ar_element.DataPrototypeRef:
        """
        Reads references to DATA-PROTOTYPE--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.DataPrototypeRef(xml_elem.text, dest_enum)

    def _read_port_interface_ref(self,
                                 xml_elem: ElementTree.Element
                                 ) -> ar_element.PortInterfaceRef:
        """
        Reads references to PORT-INTERFACE--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.PortInterfaceRef(xml_elem.text, dest_enum)

    def _read_sw_component_type_ref(self,
                                    xml_elem: ElementTree.Element
                                    ) -> ar_element.SwComponentTypeRef:
        """
        Reads references to SW-COMPONENT-TYPE--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.SwComponentTypeRef(xml_elem.text, dest_enum)

    def _read_sw_component_prototype_ref(self,
                                         xml_elem: ElementTree.Element
                                         ) -> ar_element.SwComponentPrototypeRef:
        """
        Reads reference to SW-COMPONENT-PROTOTYPE--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SW-COMPONENT-PROTOTYPE':
            msg = f"Invalid value for DEST. Expected 'SW-COMPONENT-PROTOTYPE', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.SwComponentPrototypeRef(xml_elem.text)

    def _read_swc_internal_behavior_ref(self,
                                        xml_elem: ElementTree.Element
                                        ) -> ar_element.SwcInternalBehaviorRef:
        """
        Reads reference to SWC-INTERNAL-BEHAVIOR--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        if data['dest'] != 'SWC-INTERNAL-BEHAVIOR':
            msg = f"Invalid value for DEST. Expected 'SWC-INTERNAL-BEHAVIOR', got '{data['dest']}'"
            raise ar_exception.ParseError(msg)
        return ar_element.SwcInternalBehaviorRef(xml_elem.text)

    def _read_exclusive_area_ref(self,
                                 xml_elem: ElementTree.Element
                                 ) -> ar_element.ExclusiveAreaRef:
        """
        Reads references to AR:EXCLUSIVE-AREA--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.ExclusiveAreaRef(xml_elem.text, dest_enum)

    def _read_exclusive_area_nesting_order_ref(self,
                                               xml_elem: ElementTree.Element
                                               ) -> ar_element.ExclusiveAreaNestingOrderRef:
        """
        Reads references to AR:EXCLUSIVE-AREA-NESTING-ORDER--SUBTYPES-ENUM
        """
        data = {}
        self._read_base_ref_attributes(xml_elem.attrib, data)
        dest_enum = ar_enum.xml_to_enum('IdentifiableSubTypes', data['dest'], self.schema_version)
        return ar_element.ExclusiveAreaNestingOrderRef(xml_elem.text, dest_enum)

    def _read_abstract_required_port_prototype_ref(self,
                                                   xml_elem: ElementTree.Element
                                                   ) -> ar_element.AbstractRequiredPortPrototypeRef:
        """
        Reads references to AR:ABSTRACT-REQUIRED-PORT-PROTOTYPE--SUBTYPES-ENUM
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.AbstractRequiredPortPrototypeRef(xml_elem.text, dest_enum)

    def _read_abstract_provided_port_prototype_ref(self,
                                                   xml_elem: ElementTree.Element
                                                   ) -> ar_element.AbstractProvidedPortPrototypeRef:
        """
        Reads references to AR:ABSTRACT-PROVIDED-PORT-PROTOTYPE--SUBTYPES-ENUM
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.AbstractProvidedPortPrototypeRef(xml_elem.text, dest_enum)

    def _read_runnable_entity_ref(self,
                                  xml_elem: ElementTree.Element
                                  ) -> ar_element.RunnableEntityRef:
        """
        Reads references to RUNNABLE-ENTITY--SUBTYPES-ENUM
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.RunnableEntityRef(xml_elem.text, dest_enum)

    def _read_variable_access_ref(self,
                                  xml_elem: ElementTree.Element
                                  ) -> ar_element.VariableAccessRef:
        """
        Reads references to AR:VARIABLE-ACCESS--SUBTYPES-ENUM
        Tag variants: 'EVENT-SOURCE-REF' | 'VARIABLE-ACCESS-REF' | 'TARGET-VARIABLE-ACCESS-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.VariableAccessRef(xml_elem.text, dest_enum)

    def _read_mode_switch_point_ref(self,
                                    xml_elem: ElementTree.Element
                                    ) -> ar_element.TriggerRef:
        """
        Reads references to AR:MODE-SWITCH-POINT--SUBTYPES-ENUM
        Tag variants: 'EVENT-SOURCE-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.ModeSwitchPointRef(xml_elem.text, dest_enum)

    def _read_async_server_call_point_ref(self,
                                          xml_elem: ElementTree.Element
                                          ) -> ar_element.AsynchronousServerCallPointRef:
        """
        Reads references to AR:ASYNCHRONOUS-SERVER-CALL-POINT--SUBTYPES-ENUM
        Tag variants: 'ASYNCHRONOUS-SERVER-CALL-POINT-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.AsynchronousServerCallPointRef(xml_elem.text, dest_enum)

    def _read_async_server_call_result_point_ref(self,
                                                 xml_elem: ElementTree.Element
                                                 ) -> ar_element.AsynchronousServerCallResultPointRef:
        """
        Reads references to AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT--SUBTYPES-ENUM
        Tag variants: 'EVENT-SOURCE-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.AsynchronousServerCallResultPointRef(xml_elem.text, dest_enum)

    def _read_trigger_ref(self,
                          xml_elem: ElementTree.Element
                          ) -> ar_element.TriggerRef:
        """
        Reads references to AR:TRIGGER--SUBTYPES-ENUM
        Tag variants: 'TRIGGER-REF' | 'RELEASED-TRIGGER-REF' | 'MASTERED-TRIGGER-REF' |
                      'TARGET-TRIGGER-REF' | 'SOURCE-TRIGGER-REF' | 'BSW-TRIGGER-REF' |
                      'FIRST-TRIGGER-REF' | 'SECOND-TRIGGER-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.TriggerRef(xml_elem.text, dest_enum)

    def _read_internal_triggering_point_ref(self,
                                            xml_elem: ElementTree.Element
                                            ) -> ar_element.InternalTriggeringPointRef:
        """
        Reads references to AR:INTERNAL-TRIGGERING-POINT--SUBTYPES-ENUM
        Tag variants: 'EVENT-SOURCE-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.InternalTriggeringPointRef(xml_elem.text, dest_enum)

    def _read_rte_event_ref(self,
                            xml_elem: ElementTree.Element
                            ) -> ar_element.RteEventRef:
        """
        Reads references to AR:RTE-EVENT--SUBTYPES-ENUM
        Tag variants: 'TARGET-EVENT-REF' | 'TARGET-RTE-EVENT-REF' | 'TRIGGER-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.RteEventRef(xml_elem.text, dest_enum)

    def _read_data_type_mapping_set_ref(self,
                                        xml_elem: ElementTree.Element
                                        ) -> ar_element.DataTypeMappingSetRef:
        """
        Reads references to AR:DATA-TYPE-MAPPING-SET--SUBTYPES-ENUM
        Tag variants: 'DATA-TYPE-MAPPING-REF' | 'DATA-TYPE-MAPPING-SET-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.DataTypeMappingSetRef(xml_elem.text, dest_enum)

    def _read_argument_data_prototype_ref(self,
                                          xml_elem: ElementTree.Element
                                          ) -> ar_element.ArgumentDataPrototypeRef:
        """
        Reads reference to AR:ARGUMENT-DATA-PROTOTYPE--SUBTYPES-ENUM
        Tag variants: 'ARGUMENT-REF' | 'ROOT-ARGUMENT-DATA-PROTOTYPE-REF' | 'TLV-ARGUMENT-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.ArgumentDataPrototypeRef(xml_elem.text, dest_enum)

    def _read_application_array_element_ref(self,
                                            xml_elem: ElementTree.Element
                                            ) -> ar_element.ApplicationArrayElementRef:
        """
        Reads references to AR:APPLICATION-ARRAY-ELEMENT--SUBTYPES-ENUM
        Tag variants: 'APPLICATION-ARRAY-ELEMENT-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.ApplicationArrayElementRef(xml_elem.text, dest_enum)

    def _read_application_record_element_ref(self,
                                             xml_elem: ElementTree.Element
                                             ) -> ar_element.ApplicationRecordElementRef:
        """
        Reads references to AR:APPLICATION-RECORD-ELEMENT--SUBTYPES-ENUM
        Tag variants: 'APPLICATION-RECORD-ELEMENT-REF' | 'TLV-RECORD-ELEMENT-REF'
        """
        dest_enum = self._read_ref_dest(xml_elem)
        return ar_element.ApplicationRecordElementRef(xml_elem.text, dest_enum)

    # --- Constant and value specifications

    def _read_text_value_specification(self,
                                       xml_element: ElementTree.Element) -> ar_element.TextValueSpecification:
        """
        Reads complex-type AR:TEXT-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'TEXT-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_text_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.TextValueSpecification(**data)
        return element

    def _read_text_value_specification_group(self,
                                             child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:TEXT-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("VALUE")
        if xml_child is not None:
            data["value"] = xml_child.text

    def _read_numerical_value_specification(self,
                                            xml_element: ElementTree.Element
                                            ) -> ar_element.NumericalValueSpecification:
        """
        Reads complex-type AR:NUMERICAL-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'NUMERICAL-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_numerical_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.NumericalValueSpecification(**data)
        return element

    def _read_numerical_value_specification_group(self,
                                                  child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NUMERICAL-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("VALUE")
        if xml_child is not None:
            data["value"] = self._read_number(xml_child.text)

    def _read_not_available_value_specification(self,
                                                xml_element: ElementTree.Element
                                                ) -> ar_element.NotAvailableValueSpecification:
        """
        Reads complex-type AR:NOT-AVAILABLE-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'NOT-AVAILABLE-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_not_available_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.NotAvailableValueSpecification(**data)
        return element

    def _read_not_available_value_specification_group(self,
                                                      child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NOT-AVAILABLE-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("DEFAULT-PATTERN")
        if xml_child is not None:
            wrapped_value = ar_element.PositiveIntegerValue(xml_child.text)
            data["default_pattern"] = wrapped_value.value
            # TODO: Add support for retaining used number format

    def _read_array_value_specification(self,
                                        xml_element: ElementTree.Element) -> ar_element.ArrayValueSpecification:
        """
        Reads complex-type AR:ARRAY-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'ARRAY-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_array_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.ArrayValueSpecification(**data)
        return element

    def _read_array_value_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ARRAY-VALUE-SPECIFICATION
        """
        xml_elements = child_elements.get("ELEMENTS")
        if xml_elements is not None:
            elements = []
            for xml_child_elem in xml_elements.findall('./*'):
                element = self._read_value_specification_element(xml_child_elem)
                elements.append(element)
            data["elements"] = elements

    def _read_record_value_specification(self,
                                         xml_element: ElementTree.Element) -> ar_element.RecordValueSpecification:
        """
        Reads complex-type AR:RECORD-VALUE-SPECIFICATION
        Type: Concrete
        Tag variants: 'RECORD-VALUE-SPECIFICATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_record_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.RecordValueSpecification(**data)
        return element

    def _read_record_value_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:RECORD-VALUE-SPECIFICATION
        """
        xml_elements = child_elements.get("FIELDS")
        if xml_elements is not None:
            fields = []
            for xml_child_elem in xml_elements.findall('./*'):
                field = self._read_value_specification_element(xml_child_elem)
                fields.append(field)
            data["fields"] = fields

    def _read_value_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("SHORT-LABEL")
        if xml_child is not None:
            data["label"] = xml_child.text

    def _read_application_value_specification(self,
                                              xml_element: ElementTree.Element
                                              ) -> ar_element.ApplicationValueSpecification:
        """
        Reads complex-type AR:APPLICATION-VALUE-SPECIFICATION
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_application_value_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.ApplicationValueSpecification(**data)
        return element

    def _read_application_value_specification_group(self,
                                                    child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-VALUE-SPECIFICATION
        """
        xml_child = child_elements.get("CATEGORY")
        if xml_child is not None:
            data["category"] = xml_child.text
        xml_child = child_elements.get("SW-AXIS-CONTS")
        if xml_child is not None:
            elements = []
            for xml_grand_child in xml_child.findall("./SW-AXIS-CONT"):
                elements.append(self._read_sw_axis_cont(xml_grand_child))
            data["sw_axis_conts"] = elements
        xml_child = child_elements.get("SW-VALUE-CONT")
        if xml_child is not None:
            data["sw_value_cont"] = self._read_sw_value_cont(xml_child)

    def _read_value_specification_element(self,
                                          xml_element: ElementTree.Element
                                          ) -> ar_element.ValueSpecificationElement:
        """
        Reads any ValueSpecificationElement
        """
        read_method = self.switcher_value_specification.get(xml_element.tag, None)
        if read_method is not None:
            return read_method(xml_element)
        else:
            raise KeyError(f"Found no reader for '{xml_element.tag}'")

    def _read_constant_specification(self,
                                     xml_element: ElementTree.Element) -> ar_element.ConstantSpecification:
        """
        Reads complex type AR:CONSTANT-SPECIFICATION
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_constant_specification_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ConstantSpecification(**data)

    def _read_constant_specification_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CONSTANT-SPECIFICATION
        """
        xml_child = child_elements.get("VALUE-SPEC")
        if xml_child is not None:
            xml_grand_child = xml_child.find("./*")
            if xml_grand_child is not None:
                data["value"] = self._read_value_specification_element(xml_grand_child)

    def _read_constant_reference(self,
                                 xml_element: ElementTree.Element
                                 ) -> ar_element.ConstantReference:
        """
        Reads complex-type AR:CONSTANT-REFERENCE
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_value_specification_group(child_elements, data)
        self._read_constant_reference_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.ConstantReference(**data)
        return element

    def _read_constant_reference_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CONSTANT-REFERENCE
        """
        xml_child = child_elements.get("CONSTANT-REF")
        if xml_child is not None:
            data["constant_ref"] = self._read_constant_ref(xml_child)

    # CalibrationData elements

    def _read_sw_values(self,
                        xml_element: ElementTree.Element) -> ar_element.SwValues:
        """
        Reads complex-type AR:SW-VALUES
        Type: Concrete
        Tag variants: 'SW-VALUES-PHYS'
        """
        data = {}
        child_elements = list(xml_element.findall("./*"))
        self._read_sw_values_group(child_elements, data)
        element = ar_element.SwValues(**data)
        return element

    def _read_sw_values_group(self,
                              xml_child_list: list[ElementTree.Element],
                              data: dict) -> None:
        """
        Reads group AR:SW-VALUES
        Type: Abstract

        XML elements not supported:

        - VTF
        - VF
        """
        values = []
        data["values"] = values
        for xml_child in xml_child_list:
            if xml_child.tag == "VT":
                values.append(xml_child.text)
            elif xml_child.tag == "V":
                number = ar_element.NumericalValue(xml_child.text)
                if number.value_format in (ar_enum.ValueFormat.HEXADECIMAL,
                                           ar_enum.ValueFormat.BINARY,
                                           ar_enum.ValueFormat.SCIENTIFIC):
                    values.append(number)
                else:
                    values.append(number.value)
            elif xml_child.tag == "VG":
                values.append(self._read_value_group(xml_child))
            elif xml_child.tag in ("VTF", "VG"):
                continue  # Not supported, skip
            else:
                print(f"Unprocessed child element in VALUE-GROUP: <{xml_child.tag}>", file=sys.stderr)

    def _read_value_group(self, xml_element: ElementTree.Element) -> ar_element.ValueGroup:
        """
        Reads complex-type AR:VALUE-GROUP
        """
        data = {}
        child_elements = list(xml_element.findall("./*"))
        if len(child_elements) > 0 and child_elements[0].tag == 'LABEL':
            data["label"] = self._read_multi_language_long_name(child_elements.pop(0))
        self._read_sw_values_group(child_elements, data)
        element = ar_element.ValueGroup(**data)
        return element

    def _read_sw_axis_cont(self, xml_element: ElementTree.Element) -> ar_element.SwAxisCont:
        """
        Reads complex-type AR:SW-AXIS-CONT
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_sw_axis_cont_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.SwAxisCont(**data)
        return element

    def _read_sw_axis_cont_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-AXIS-CONT
        """
        xml_child = child_elements.get("CATEGORY")
        if xml_child is not None:
            data["category"] = ar_enum.xml_to_enum("CalibrationAxisCategory", xml_child.text)
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        xml_child = child_elements.get("UNIT-DISPLAY-NAME")
        if xml_child is not None:
            data["unit_display_name"] = self._read_single_language_unit_names(xml_child)
        xml_child = child_elements.get("SW-AXIS-INDEX")
        if xml_child is not None:
            try:
                value = int(xml_child.text)
            except ValueError:
                value = xml_child.text
            data["sw_axis_index"] = value
        xml_child = child_elements.get("SW-ARRAYSIZE")
        if xml_child is not None:
            data["sw_array_size"] = self._read_value_list(xml_child)
        xml_child = child_elements.get("SW-VALUES-PHYS")
        if xml_child is not None:
            data["sw_values_phys"] = self._read_sw_values(xml_child)

    def _read_sw_value_cont(self, xml_element: ElementTree.Element) -> ar_element.SwValueCont:
        """
        Reads complex-type AR:SW-VALUE-CONT
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_sw_value_cont_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        element = ar_element.SwValueCont(**data)
        return element

    def _read_sw_value_cont_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-VALUE-CONT
        """
        xml_child = child_elements.get("UNIT-REF")
        if xml_child is not None:
            data["unit_ref"] = self._read_unit_ref(xml_child)
        xml_child = child_elements.get("UNIT-DISPLAY-NAME")
        if xml_child is not None:
            data["unit_display_name"] = self._read_single_language_unit_names(xml_child)
        xml_child = child_elements.get("SW-ARRAYSIZE")
        if xml_child is not None:
            data["sw_array_size"] = self._read_value_list(xml_child)
        xml_child = child_elements.get("SW-VALUES-PHYS")
        if xml_child is not None:
            data["sw_values_phys"] = self._read_sw_values(xml_child)

        # --- ModeDeclaration elements

    def _read_mode_declaration(self, xml_element: ElementTree.Element) -> ar_element.ModeDeclaration:
        """
        Reads complex type AR:MODE-DECLARATION
        Tag variants: 'MODE-DECLARATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        xml_child = child_elements.get('VALUE')
        if xml_child is not None:
            data["value"] = ar_element.PositiveIntegerValue(xml_child.text).value
        child_elements.skip("MODE-DECLARATION")  # Not supported
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeDeclaration(**data)

    def _read_mode_error_behavior(self, xml_element: ElementTree.Element) -> ar_element.ModeErrorBehavior:
        """
        Reads complex type AR:MODE-ERROR-BEHAVIOR
        Tag variants: 'MODE-ERROR-BEHAVIOR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get('DEFAULT-MODE-REF')
        if xml_child is not None:
            data["default_mode_ref"] = self._read_mode_declaration_ref(xml_child)
        xml_child = child_elements.get('ERROR-REACTION-POLICY')
        if xml_child is not None:
            data["error_reaction_policy"] = ar_enum.xml_to_enum("ModeErrorReactionPolicy", xml_child.text)
        return ar_element.ModeErrorBehavior(**data)

    def _read_mode_transition(self, xml_element: ElementTree.Element) -> ar_element.ModeTransition:
        """
        Reads complex type AR:MODE-TRANSITION
        Tag variants: 'MODE-TRANSITION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_mode_transition_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeTransition(**data)

    def _read_mode_transition_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:MODE-TRANSITION
        """
        xml_child = child_elements.get('ENTERED-MODE-REF')
        if xml_child is not None:
            data["entered_mode_ref"] = self._read_mode_declaration_ref(xml_child)
        xml_child = child_elements.get('EXITED-MODE-REF')
        if xml_child is not None:
            data["exited_mode_ref"] = self._read_mode_declaration_ref(xml_child)

    def _read_mode_declaration_group(self, xml_element: ElementTree.Element) -> ar_element.ModeDeclarationGroup:
        """
        Reads Complex type AR:MODE-DECLARATION-GROUP
        Type: Concrete
        Tag variants: 'MODE-DECLARATION-GROUP'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_mode_declaration_group_data(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeDeclarationGroup(**data)

    def _read_mode_declaration_group_data(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:MODE-DECLARATION-GROUP
        """
        xml_child = child_elements.get("INITIAL-MODE-REF")
        if xml_child is not None:
            data["initial_mode_ref"] = self._read_mode_declaration_ref(xml_child)
        xml_child = child_elements.get("MODE-DECLARATIONS")
        if xml_child is not None:
            mode_declarations = []
            data["mode_declarations"] = mode_declarations
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'MODE-DECLARATION':
                    element = self._read_mode_declaration(xml_grand_child)
                    mode_declarations.append(element)
        xml_child = child_elements.get("MODE-MANAGER-ERROR-BEHAVIOR")
        if xml_child is not None:
            data["mode_manager_error_behavior"] = self._read_mode_error_behavior(xml_child)
        xml_child = child_elements.get("MODE-TRANSITIONS")
        if xml_child is not None:
            mode_transitions = []
            data["mode_transitions"] = mode_transitions
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'MODE-TRANSITION':
                    element = self._read_mode_transition(xml_grand_child)
                    mode_transitions.append(element)
        xml_child = child_elements.get("MODE-USER-ERROR-BEHAVIOR")
        if xml_child is not None:
            data["mode_user_error_behavior"] = self._read_mode_error_behavior(xml_child)
        xml_child = child_elements.get("ON-TRANSITION-VALUE")
        if xml_child is not None:
            data["on_transition_value"] = ar_element.PositiveIntegerValue(xml_child.text).value

    def _read_mode_declaration_group_prototype(self,
                                               xml_element: ElementTree.Element
                                               ) -> ar_element.ModeDeclarationGroupPrototype:
        """
        Reads Complex type AR:MODE-DECLARATION-GROUP-PROTOTYPE
        Tag variants: 'MODE-DECLARATION-GROUP-PROTOTYPE' | 'MODE-GROUP'
                  | 'PROCESS-STATE-MACHINE' | 'STATE-MACHINE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_mode_declaration_group_prototype_data(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeDeclarationGroupPrototype(**data)

    def _read_mode_declaration_group_prototype_data(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:MODE-DECLARATION-GROUP-PROTOTYPE
        """
        xml_child = child_elements.get("SW-CALIBRATION-ACCESS")
        if xml_child is not None:
            data['calibration_access'] = ar_enum.xml_to_enum('SwCalibrationAccess',
                                                             xml_child.text)
        xml_child = child_elements.get("TYPE-TREF")
        if xml_child is not None:
            data['type_ref'] = self._read_mode_declaration_group_ref(xml_child)
        child_elements.skip("VARIATION-POINT")  # not supported

    # ---Port interface elements

    def _read_port_interface(self, xml_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PORT-INTERFACE
        Type: Abstract
        """
        inner_elem = xml_elements.get('IS-SERVICE')
        if inner_elem is not None:
            data['is_service'] = self._read_boolean(inner_elem.text)
        xml_elements.skip('NAMESPACES')  # Not supported
        xml_elements.skip('SERVICE-KIND')  # Implement later

    def _read_nv_data_interface(self, xml_element: ElementTree.Element) -> ar_element.NvDataInterface:
        """
        Reads complex type AR:NV-DATA-INTERFACE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        self._read_nv_data_interface_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.NvDataInterface(**data)

    def _read_nv_data_interface_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NV-DATA-INTERFACE
        Type: Abstract
        """
        xml_child = child_elements.get('NV-DATAS')
        if xml_child is not None:
            data_elements = []
            data["data_elements"] = data_elements
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'VARIABLE-DATA-PROTOTYPE':
                    element = self._read_variable_data_prototype(xml_grand_child)
                    data_elements.append(element)

    def _read_parameter_interface(self, xml_element: ElementTree.Element) -> ar_element.ParameterInterface:
        """
        Reads complex type AR:PARAMETER-INTERFACE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        self._read_parameter_interface_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ParameterInterface(**data)

    def _read_parameter_interface_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PARAMETER-INTERFACE
        Type: Abstract
        """
        xml_child = child_elements.get('PARAMETERS')
        if xml_child is not None:
            parameters = []
            data["parameters"] = parameters
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'PARAMETER-DATA-PROTOTYPE':
                    element = self._read_parameter_data_prototype(xml_grand_child)
                    parameters.append(element)

    def _read_sender_receiver_interface(self, xml_element: ElementTree.Element) -> ar_element.SenderReceiverInterface:
        """
        Reads complex type AR:SENDER-RECEIVER-INTERFACE
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        self._read_sender_receiver_interface_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SenderReceiverInterface(**data)

    def _read_sender_receiver_interface_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AR-SENDER-RECEIVER-INTERFACE
        Type: Abstract
        """
        xml_child = child_elements.get('DATA-ELEMENTS')
        if xml_child is not None:
            data_elements = []
            data["data_elements"] = data_elements
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'VARIABLE-DATA-PROTOTYPE':
                    element = self._read_variable_data_prototype(xml_grand_child)
                    data_elements.append(element)
        xml_child = child_elements.get('INVALIDATION-POLICYS')
        if xml_child is not None:
            policies = []
            data["invalidation_policies"] = policies
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'INVALIDATION-POLICY':
                    policy = self._read_invalidation_policy(xml_grand_child)
                    policies.append(policy)
        child_elements.skip("META-DATA-ITEM-SETS")  # Not supported

    def _read_invalidation_policy(self, xml_element: ElementTree.Element) -> ar_element.InvalidationPolicy:
        """
        Reads complex-type AR:INVALIDATION-POLICY
        Type: Concrete
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("DATA-ELEMENT-REF")
        if xml_child is not None:
            data["data_element_ref"] = self._read_variable_data_prototype_ref(xml_child)
        xml_child = child_elements.get("HANDLE-INVALID")
        if xml_child is not None:
            data["handle_invalid"] = ar_enum.xml_to_enum("HandleInvalid", xml_child.text)
        return ar_element.InvalidationPolicy(**data)

    def _read_application_error(self, xml_element: ElementTree.Element) -> ar_element.ApplicationError:
        """
        Reads complex type AR:APPLICATION-ERROR
        Tag variants: 'APPLICATION-ERROR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_application_error_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationError(**data)

    def _read_application_error_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:APPLICATION-ERROR
        """
        xml_child = child_elements.get("ERROR-CODE")
        if xml_child is not None:
            data["error_code"] = self._read_integer(xml_child.text)

    def _read_client_server_operation(self, xml_element: ElementTree.Element) -> ar_element.ClientServerOperation:
        """
        Reads complex type AR:CLIENT-SERVER-OPERATION
        Tag variants: 'CLIENT-SERVER-OPERATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_client_server_operation_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ClientServerOperation(**data)

    def _read_client_server_operation_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CLIENT-SERVER-OPERATION
        """
        xml_child = child_elements.get("ARGUMENTS")
        if xml_child is not None:
            arguments = []
            data["arguments"] = arguments
            for xml_grand_child in xml_child.findall("./*"):
                if xml_grand_child.tag == "ARGUMENT-DATA-PROTOTYPE":
                    element = self._read_argument_data_prototype(xml_grand_child)
                    arguments.append(element)
        xml_child = child_elements.get("DIAG-ARG-INTEGRITY")
        if xml_child is not None:
            data["diag_arg_integrity"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("FIRE-AND-FORGET")
        if xml_child is not None:
            data["fire_and_forget"] = self._read_boolean(xml_child.text)
        child_elements.skip("POSSIBLE-AP-ERROR-REFS")  # not supported
        child_elements.skip("POSSIBLE-AP-ERROR-SET-REFS")  # not supported
        xml_child = child_elements.get("POSSIBLE-ERROR-REFS")
        if xml_child is not None:
            possible_error_refs = []
            data["possible_error_refs"] = possible_error_refs
            for xml_grand_child in xml_child.findall("./*"):
                if xml_grand_child.tag == "POSSIBLE-ERROR-REF":
                    element = self._read_application_error_ref(xml_grand_child)
                    possible_error_refs.append(element)
        child_elements.skip("VARIATION-POINT")  # not supported

    def _read_client_server_interface(self, xml_element: ElementTree.Element) -> ar_element.ClientServerInterface:
        """
        Reads complex type AR:CLIENT-SERVER-INTERFACE
        Tag variants: 'CLIENT-SERVER-INTERFACE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        self._read_client_server_interface_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ClientServerInterface(**data)

    def _read_client_server_interface_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CLIENT-SERVER-INTERFACE
        """
        xml_child = child_elements.get('OPERATIONS')
        if xml_child is not None:
            operations = []
            data["operations"] = operations
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'CLIENT-SERVER-OPERATION':
                    element = self._read_client_server_operation(xml_grand_child)
                    operations.append(element)
        xml_child = child_elements.get('POSSIBLE-ERRORS')
        if xml_child is not None:
            possible_errors = []
            data["possible_errors"] = possible_errors
            for xml_grand_child in xml_child.findall('./*'):
                if xml_grand_child.tag == 'APPLICATION-ERROR':
                    element = self._read_application_error(xml_grand_child)
                    possible_errors.append(element)

    def _read_mode_switch_interface(self, xml_element: ElementTree.Element) -> ar_element.ModeSwitchInterface:
        """
        Reads complex type AR:MODE-SWITCH-INTERFACE
        Tag variants: 'MODE-SWITCH-INTERFACE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_port_interface(child_elements, data)
        xml_child = child_elements.get('MODE-GROUP')
        if xml_child is not None:
            data['mode_group'] = self._read_mode_declaration_group_prototype(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeSwitchInterface(**data)

    # --- System template elements

    def _read_e2e_transformation_com_spec_props(self,
                                                xml_element: ElementTree.Element
                                                ) -> ar_element.EndToEndTransformationComSpecProps:
        """
        Writes complex type AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
        Tag variants: 'END-TO-END-TRANSFORMATION-COM-SPEC-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_describable(child_elements, data)
        self._read_e2e_transformation_com_spec_props_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.EndToEndTransformationComSpecProps(**data)

    def _read_e2e_transformation_com_spec_props_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
        """
        xml_child = child_elements.get("CLEAR-FROM-VALID-TO-INVALID")
        if xml_child is not None:
            data["clear_from_valid_to_invalid"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("DISABLE-END-TO-END-CHECK")
        if xml_child is not None:
            data["disable_e2e_check"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("DISABLE-END-TO-END-STATE-MACHINE")
        if xml_child is not None:
            data["disable_e2e_state_machine"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("E-2-E-PROFILE-COMPATIBILITY-PROPS-REF")
        if xml_child is not None:
            data["e2e_profile_compatibility_props_ref"] = self._read_e2e_profile_compatibility_props_ref(xml_child)
        xml_child = child_elements.get("MAX-DELTA-COUNTER")
        if xml_child is not None:
            data["max_delta_counter"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MAX-ERROR-STATE-INIT")
        if xml_child is not None:
            data["max_error_state_init"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MAX-ERROR-STATE-INVALID")
        if xml_child is not None:
            data["max_error_state_invalid"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MAX-ERROR-STATE-VALID")
        if xml_child is not None:
            data["max_error_state_valid"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MAX-NO-NEW-OR-REPEATED-DATA")
        if xml_child is not None:
            data["max_no_new_repeated_data"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MIN-OK-STATE-INIT")
        if xml_child is not None:
            data["min_ok_state_init"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MIN-OK-STATE-INVALID")
        if xml_child is not None:
            data["min_ok_state_invalid"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MIN-OK-STATE-VALID")
        if xml_child is not None:
            data["min_ok_state_valid"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("SYNC-COUNTER-INIT")
        if xml_child is not None:
            data["sync_counter_init"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("WINDOW-SIZE")
        if xml_child is not None:
            data["window_size"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("WINDOW-SIZE-INIT")
        if xml_child is not None:
            data["window_size_init"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("WINDOW-SIZE-INVALID")
        if xml_child is not None:
            data["window_size_invalid"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("WINDOW-SIZE-VALID")
        if xml_child is not None:
            data["window_size_valid"] = ar_element.PositiveIntegerValue(xml_child.text).value

    def _read_e2e_profile_compatibility_props(self,
                                              xml_element: ElementTree.Element
                                              ) -> ar_element.E2EProfileCompatibilityProps:
        """
        Reads complex type AR:E-2-E-PROFILE-COMPATIBILITY-PROPS
        Tag variants: 'E-2-E-PROFILE-COMPATIBILITY-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_e2e_profile_compatibility_props_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.E2EProfileCompatibilityProps(**data)

    def _read_e2e_profile_compatibility_props_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:END-TO-END-TRANSFORMATION-COM-SPEC-PROPS
        """
        xml_child = child_elements.get("TRANSIT-TO-INVALID-EXTENDED")
        if xml_child is not None:
            data["transit_to_invalid_extended"] = self._read_boolean(xml_child.text)

    # --- SoftwareComponent elements

    def _read_mode_switched_ack_request(self, xml_element: ElementTree.Element) -> ar_element.ModeSwitchedAckRequest:
        """
        Reads complex type AR:MODE-SWITCHED-ACK-REQUEST
        Tag variants: 'MODE-SWITCHED-ACK'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("TIMEOUT")
        if xml_child is not None:
            data["timeout"] = self._read_number(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeSwitchedAckRequest(**data)

    def _read_mode_switch_sender_com_spec(self, xml_element: ElementTree.Element) -> ar_element.ModeSwitchSenderComSpec:
        """
        Reads complex type AR:MODE-SWITCH-SENDER-COM-SPEC
        Tag variants: 'MODE-SWITCH-SENDER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("ENHANCED-MODE-API")
        if xml_child is not None:
            data["enhanced_mode_api"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("MODE-GROUP-REF")
        if xml_child is not None:
            data["mode_group_ref"] = self._read_mode_declaration_group_prototype_ref(xml_child)
        xml_child = child_elements.get("MODE-SWITCHED-ACK")
        if xml_child is not None:
            data["mode_switched_ack"] = self._read_mode_switched_ack_request(xml_child)
        xml_child = child_elements.get("QUEUE-LENGTH")
        if xml_child is not None:
            data["queue_length"] = ar_element.PositiveIntegerValue(xml_child.text).value
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeSwitchSenderComSpec(**data)

    def _read_transmission_acknowledgement_request(self,
                                                   xml_element: ElementTree.Element
                                                   ) -> ar_element.TransmissionAcknowledgementRequest:
        """
        Reads complex type AR:TRANSMISSION-ACKNOWLEDGEMENT-REQUEST
        Tag variants: 'TRANSMISSION-ACKNOWLEDGE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("TIMEOUT")
        if xml_child is not None:
            data["timeout"] = self._read_number(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.TransmissionAcknowledgementRequest(**data)

    def _read_tranmsission_com_spec_props(self,
                                          xml_element: ElementTree.Element
                                          ) -> ar_element.TransmissionComSpecProps:
        """
        Reads complex type AR:TRANSMISSION-COM-SPEC-PROPS
        Tag variants: 'TRANSMISSION-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("DATA-UPDATE-PERIOD")
        if xml_child is not None:
            data["data_update_period"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("MINIMUM-SEND-INTERVAL")
        if xml_child is not None:
            data["minimum_send_interval"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("TRANSMISSION-MODE")
        if xml_child is not None:
            data["transmission_mode"] = ar_enum.xml_to_enum("TransmissionMode", xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.TransmissionComSpecProps(**data)

    def _read_sender_com_spec_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SENDER-COM-SPEC
        """
        child_elements.skip("COMPOSITE-NETWORK-REPRESENTATIONS")  # not implemented
        xml_child = child_elements.get("DATA-ELEMENT-REF")
        if xml_child is not None:
            data["data_element_ref"] = self._read_autosar_data_prototype_ref(xml_child)
        child_elements.skip("DATA-UPDATE-PERIOD")
        xml_child = child_elements.get("HANDLE-OUT-OF-RANGE")
        if xml_child is not None:
            data["handle_out_of_range"] = ar_enum.xml_to_enum("HandleOutOfRange", xml_child.text)
        xml_child = child_elements.get("NETWORK-REPRESENTATION")
        if xml_child is not None:
            data["network_representation"] = self._read_sw_data_def_props(xml_child)
        child_elements.skip("SENDER-INTENT")  # not supported
        xml_child = child_elements.get("TRANSMISSION-ACKNOWLEDGE")
        if xml_child is not None:
            data["transmission_acknowledge"] = self._read_transmission_acknowledgement_request(xml_child)
        xml_child = child_elements.get("TRANSMISSION-PROPS")
        if xml_child is not None:
            data["tranmsission_props"] = self._read_tranmsission_com_spec_props(xml_child)
        xml_child = child_elements.get("USES-END-TO-END-PROTECTION")
        if xml_child is not None:
            data["uses_end_to_end_protection"] = self._read_boolean(xml_child.text)

    def _read_queued_sender_com_spec(self,
                                     xml_element: ElementTree.Element
                                     ) -> ar_element.QueuedSenderComSpec:
        """
        Reads complex type AR:QUEUED-SENDER-COM-SPEC
        Tag variants: 'QUEUED-SENDER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_sender_com_spec_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.QueuedSenderComSpec(**data)

    def _read_nonqueued_sender_com_spec(self,
                                        xml_element: ElementTree.Element
                                        ) -> ar_element.NonqueuedSenderComSpec:
        """
        Reads complex type AR:NONQUEUED-SENDER-COM-SPEC
        Tag variants: 'NONQUEUED-SENDER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_sender_com_spec_group(child_elements, data)
        self._read_nonqueued_sender_com_spec_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.NonqueuedSenderComSpec(**data)

    def _read_nonqueued_sender_com_spec_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NONQUEUED-SENDER-COM-SPEC
        """
        xml_child = child_elements.get("DATA-FILTER")
        if xml_child is not None:
            data["data_filter"] = self._read_data_filter(xml_child)
        xml_child = child_elements.get("INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass

    def _read_nv_provider_com_spec(self,
                                   xml_element: ElementTree.Element
                                   ) -> ar_element.NvProvideComSpec:
        """
        Reads complex type AR:NV-PROVIDE-COM-SPEC
        Tag variants: 'NV-PROVIDE-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_nv_provider_com_spec_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.NvProvideComSpec(**data)

    def _read_nv_provider_com_spec_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NV-PROVIDE-COM-SPEC
        """
        xml_child = child_elements.get("RAM-BLOCK-INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["ram_block_init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("ROM-BLOCK-INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["rom_block_init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("VARIABLE-REF")
        if xml_child is not None:
            data["variable_ref"] = self._read_variable_data_prototype_ref(xml_child)

    def _read_parameter_provide_com_spec(self,
                                         xml_element: ElementTree.Element
                                         ) -> ar_element.ParameterProvideComSpec:
        """
        Reads complex type AR:PARAMETER-PROVIDE-COM-SPEC
        Tag variants: 'PARAMETER-PROVIDE-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("PARAMETER-REF")
        if xml_child is not None:
            data["parameter_ref"] = self._read_parameter_data_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ParameterProvideComSpec(**data)

    def _read_server_com_spec(self,
                              xml_element: ElementTree.Element
                              ) -> ar_element.ServerComSpec:
        """
        Complex type AR:SERVER-COM-SPEC
        Tag variants: 'SERVER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_server_com_spec_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ServerComSpec(**data)

    def _read_server_com_spec_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SERVER-COM-SPEC
        """
        child_elements.skip("GETTER-REF")
        xml_child = child_elements.get("OPERATION-REF")
        if xml_child is not None:
            data["operation_ref"] = self._read_client_server_operation_ref(xml_child)
        xml_child = child_elements.get("QUEUE-LENGTH")
        if xml_child is not None:
            data["queue_length"] = ar_element.PositiveIntegerValue(xml_child.text).value
        child_elements.skip("SETTER-REF")
        xml_child = child_elements.get("TRANSFORMATION-COM-SPEC-PROPSS")
        if xml_child is not None:
            com_spec_props = []
            for xml_grand_child in xml_child.findall("./END-TO-END-TRANSFORMATION-COM-SPEC-PROPS"):
                com_spec_props.append(self._read_e2e_transformation_com_spec_props(xml_grand_child))
            data["transformation_com_spec_props"] = com_spec_props

    def _read_reception_com_spec_props(self, xml_element: ElementTree.Element) -> ar_element.ReceptionComSpecProps:
        """
        Reads Complex type AR:RECEPTION-COM-SPEC-PROPS
        Tag variants: 'RECEPTION-PROPS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_receiver_com_spec(child_elements, data)
        xml_child = child_elements.get("DATA-UPDATE-PERIOD")
        if xml_child is not None:
            data["data_update_period"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("TIMEOUT")
        if xml_child is not None:
            data["timeout"] = self._read_number(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ReceptionComSpecProps(**data)

    def _read_receiver_com_spec(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:RECEIVER-COM-SPEC
        """
        child_elements.skip("COMPOSITE-NETWORK-REPRESENTATIONS")  # Not yet implemented
        xml_child = child_elements.get("DATA-ELEMENT-REF")
        if xml_child is not None:
            data["data_element_ref"] = self._read_autosar_data_prototype_ref(xml_child)
        child_elements.skip("DATA-UPDATE-PERIOD")  # Status removed
        child_elements.skip("EXTERNAL-REPLACEMENT-REF")  # Status removed
        xml_child = child_elements.get("HANDLE-OUT-OF-RANGE")
        if xml_child is not None:
            data["handle_out_of_range"] = ar_enum.xml_to_enum("HandleOutOfRange", xml_child.text)
        xml_child = child_elements.get("HANDLE-OUT-OF-RANGE-STATUS")
        if xml_child is not None:
            data["handle_out_of_range_status"] = ar_enum.xml_to_enum("HandleOutOfRangeStatus", xml_child.text)
        xml_child = child_elements.get("MAX-DELTA-COUNTER-INIT")
        if xml_child is not None:
            data["max_delta_counter_init"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("MAX-NO-NEW-OR-REPEATED-DATA")
        if xml_child is not None:
            data["max_no_new_repeated_data"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("NETWORK-REPRESENTATION")
        if xml_child is not None:
            data["network_representation"] = self._read_sw_data_def_props(xml_child)
        child_elements.skip("RECEIVER-INTENT")  # Not supported (Adaptive Platform)
        xml_child = child_elements.get("RECEPTION-PROPS")
        if xml_child is not None:
            data["reception_props"] = self._read_reception_com_spec_props(xml_child)
        xml_child = child_elements.get("REPLACE-WITH")
        if xml_child is not None:
            data["replace_with"] = self._read_variable_access(xml_child)
        xml_child = child_elements.get("SYNC-COUNTER-INIT")
        if xml_child is not None:
            data["sync_counter_init"] = ar_element.PositiveIntegerValue(xml_child.text).value
        xml_child = child_elements.get("TRANSFORMATION-COM-SPEC-PROPSS")
        if xml_child is not None:
            com_spec_props = []
            for xml_grand_child in xml_child.findall("./END-TO-END-TRANSFORMATION-COM-SPEC-PROPS"):
                com_spec_props.append(self._read_e2e_transformation_com_spec_props(xml_grand_child))
            data["transformation_com_spec_props"] = com_spec_props
        xml_child = child_elements.get("USES-END-TO-END-PROTECTION")
        if xml_child is not None:
            data["uses_end_to_end_protection"] = self._read_boolean(xml_child.text)

    def _read_queued_receiver_com_spec(self, xml_element: ElementTree.Element) -> ar_element.QueuedReceiverComSpec:
        """
        Reads complex type AR:QUEUED-RECEIVER-COM-SPEC
        Tag variants: 'QUEUED-RECEIVER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_receiver_com_spec(child_elements, data)
        xml_child = child_elements.get("QUEUE-LENGTH")
        if xml_child is not None:
            data["queue_length"] = ar_element.PositiveIntegerValue(xml_child.text).value
        self._report_unprocessed_elements(child_elements)
        return ar_element.QueuedReceiverComSpec(**data)

    def _read_nonqueued_receiver_com_spec(self,
                                          xml_element: ElementTree.Element) -> ar_element.NonqueuedReceiverComSpec:
        """
        Reads complex type AR:NONQUEUED-RECEIVER-COM-SPEC
        Tag variants: 'NONQUEUED-RECEIVER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_receiver_com_spec(child_elements, data)
        self._read_nonqueued_receiver_com_spec_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.NonqueuedReceiverComSpec(**data)

    def _read_nonqueued_receiver_com_spec_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:NONQUEUED-RECEIVER-COM-SPEC
        """
        xml_child = child_elements.get("ALIVE-TIMEOUT")
        if xml_child is not None:
            data["alive_timeout"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("ENABLE-UPDATE")
        if xml_child is not None:
            data["enable_update"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("FILTER")
        if xml_child is not None:
            data["data_filter"] = self._read_data_filter(xml_child)
        xml_child = child_elements.get("HANDLE-DATA-STATUS")
        if xml_child is not None:
            data["handle_data_status"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("HANDLE-NEVER-RECEIVED")
        if xml_child is not None:
            data["handle_never_received"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("HANDLE-TIMEOUT-TYPE")
        if xml_child is not None:
            data["handle_timeout_type"] = ar_enum.xml_to_enum("HandleTimeout", xml_child.text)
        xml_child = child_elements.get("INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("TIMEOUT-SUBSTITUTION-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["timeout_substitution_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass

    def _read_nv_require_com_spec(self, xml_element: ElementTree.Element) -> ar_element.NvRequireComSpec:
        """
        Reads complex type AR:NV-REQUIRE-COM-SPEC
        Tag variants: 'NV-REQUIRE-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("VARIABLE-REF")
        if xml_child is not None:
            data["variable_ref"] = self._read_variable_data_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.NvRequireComSpec(**data)

    def _read_parameter_require_com_spec(self,
                                         xml_element: ElementTree.Element
                                         ) -> ar_element.ParameterRequireComSpec:
        """
        Reads complex type AR:PARAMETER-REQUIRE-COM-SPEC
        Tag variants: 'PARAMETER-REQUIRE-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("INIT-VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["init_value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("PARAMETER-REF")
        if xml_child is not None:
            data["parameter_ref"] = self._read_parameter_data_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ParameterRequireComSpec(**data)

    def _read_mode_switch_receiver_com_spec(self,
                                            xml_element: ElementTree.Element
                                            ) -> ar_element.ModeSwitchReceiverComSpec:
        """
        Reads complex type AR:MODE-SWITCH-RECEIVER-COM-SPEC
        Tag variants: 'MODE-SWITCH-RECEIVER-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("ENHANCED-MODE-API")
        if xml_child is not None:
            data["enhanced_mode_api"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("MODE-GROUP-REF")
        if xml_child is not None:
            data["mode_group_ref"] = self._read_mode_declaration_group_prototype_ref(xml_child)
        xml_child = child_elements.get("SUPPORTS-ASYNCHRONOUS-MODE-SWITCH")
        if xml_child is not None:
            data["supports_async"] = self._read_boolean(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeSwitchReceiverComSpec(**data)

    def _read_client_com_spec(self,
                              xml_element: ElementTree.Element
                              ) -> ar_element.ClientComSpec:
        """
        Reads Complex type AR:CLIENT-COM-SPEC
        Tag variants: 'CLIENT-COM-SPEC'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_client_com_spec_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ClientComSpec(**data)

    def _read_client_com_spec_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:CLIENT-COM-SPEC
        """
        child_elements.skip("CLIENT-INTENT")
        xml_child = child_elements.get("END-TO-END-CALL-RESPONSE-TIMEOUT")
        if xml_child is not None:
            data["e2e_call_respone_timeout"] = self._read_number(xml_child.text)
        child_elements.skip("GETTER-REF")
        xml_child = child_elements.get("OPERATION-REF")
        if xml_child is not None:
            data["operation_ref"] = self._read_client_server_operation_ref(xml_child)
        child_elements.skip("SETTER-REF")
        xml_child = child_elements.get("TRANSFORMATION-COM-SPEC-PROPSS")
        if xml_child is not None:
            com_spec_props = []
            for xml_grand_child in xml_child.findall("./END-TO-END-TRANSFORMATION-COM-SPEC-PROPS"):
                com_spec_props.append(self._read_e2e_transformation_com_spec_props(xml_grand_child))
            data["transformation_com_spec_props"] = com_spec_props

    def _read_provided_com_spec(self, xml_element: ElementTree.Element) -> ProvidePortComSpecElement:
        """
        Reads com-spec element for p-port
        """
        read_method = self.switcher_provided_com_spec.get(xml_element.tag, None)
        if read_method is not None:
            return read_method(xml_element)
        else:
            raise KeyError(f"Found no reader for '{xml_element.tag}'")

    def _read_required_com_spec(self, xml_element: ElementTree.Element) -> RequirePortComSpecElement:
        """
        Reads com-spec element for r-port
        """
        read_method = self.switcher_required_com_spec.get(xml_element.tag, None)
        if read_method is not None:
            return read_method(xml_element)
        else:
            raise KeyError(f"Found no reader for '{xml_element.tag}'")

    def _read_provide_port_prototype(self, xml_element: ElementTree.Element) -> ar_element.ProvidePortPrototype:
        """
        Reads complex type AR:P-PORT-PROTOTYPE
        Tag variants: 'P-PORT-PROTOTYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_provide_port_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ProvidePortPrototype(**data)

    def _read_provide_port_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:P-PORT-PROTOTYPE
        """
        xml_child = child_elements.get("PROVIDED-COM-SPECS")
        if xml_child is not None:
            com_spec_list = []
            for xml_grand_child in xml_child.findall("./*"):
                com_spec_list.append(self._read_provided_com_spec(xml_grand_child))
            data["com_spec"] = com_spec_list
        xml_child = child_elements.get("PROVIDED-INTERFACE-TREF")
        if xml_child is not None:
            data["port_interface_ref"] = self._read_port_interface_ref(xml_child)

    def _read_require_port_prototype(self, xml_element: ElementTree.Element) -> ar_element.RequirePortPrototype:
        """
        Reads complex type AR:R-PORT-PROTOTYPE
        Tag variants: 'R-PORT-PROTOTYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_required_port_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.RequirePortPrototype(**data)

    def _read_required_port_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:R-PORT-PROTOTYPE
        """
        xml_child = child_elements.get("REQUIRED-COM-SPECS")
        if xml_child is not None:
            com_spec_list = []
            for xml_grand_child in xml_child.findall("./*"):
                com_spec_list.append(self._read_required_com_spec(xml_grand_child))
            data["com_spec"] = com_spec_list
        xml_child = child_elements.get("MAY-BE-UNCONNECTED")
        if xml_child is not None:
            data["allow_unconnected"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("REQUIRED-INTERFACE-TREF")
        if xml_child is not None:
            data["port_interface_ref"] = self._read_port_interface_ref(xml_child)

    def _read_pr_port_prototype(self, xml_element: ElementTree.Element) -> ar_element.PRPortPrototype:
        """
        Reads complex type AR:PR-PORT-PROTOTYPE
        Tag variants: 'PR-PORT-PROTOTYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_pr_port_prototype_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.PRPortPrototype(**data)

    def _read_pr_port_prototype_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PR-PORT-PROTOTYPE
        """
        xml_child = child_elements.get("PROVIDED-COM-SPECS")
        if xml_child is not None:
            com_spec_list = []
            for xml_grand_child in xml_child.findall("./*"):
                com_spec_list.append(self._read_provided_com_spec(xml_grand_child))
            data["provided_com_spec"] = com_spec_list
        xml_child = child_elements.get("REQUIRED-COM-SPECS")
        if xml_child is not None:
            com_spec_list = []
            for xml_grand_child in xml_child.findall("./*"):
                com_spec_list.append(self._read_required_com_spec(xml_grand_child))
            data["required_com_spec"] = com_spec_list
        xml_child = child_elements.get("PROVIDED-REQUIRED-INTERFACE-TREF")
        if xml_child is not None:
            data["port_interface_ref"] = self._read_port_interface_ref(xml_child)

    def _read_sw_component_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-COMPONENT-TYPE
        """
        child_elements.skip("SW-COMPONENT-DOCUMENTATIONS")
        child_elements.skip("CONSISTENCY-NEEDSS")
        xml_child = child_elements.get("PORTS")
        if xml_child is not None:
            ports = []
            for xml_grand_child in xml_child.findall("./*"):
                if xml_grand_child.tag == "P-PORT-PROTOTYPE":
                    ports.append(self._read_provide_port_prototype(xml_grand_child))
                elif xml_grand_child.tag == "R-PORT-PROTOTYPE":
                    ports.append(self._read_require_port_prototype(xml_grand_child))
                elif xml_grand_child.tag == "PR-PORT-PROTOTYPE":
                    ports.append(self._read_pr_port_prototype(xml_grand_child))
            data["ports"] = ports
        child_elements.skip("PORT_GROUPS")
        child_elements.skip("SWC-MAPPING-CONSTRAINT-REFS")
        child_elements.skip("UNIT-GROUP-REFS")

    def _read_atomic_sw_component_type(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ATOMIC-SW-COMPONENT-TYPE
        """
        xml_child = child_elements.get("INTERNAL-BEHAVIORS")
        if xml_child is not None:
            # We only support max 1 internal behavior element
            xml_grand_child = xml_child.find("./SWC-INTERNAL-BEHAVIOR")
            if xml_grand_child is not None:
                data["internal_behavior"] = self._read_swc_internal_behavior(xml_grand_child)
        xml_child = child_elements.get("SYMBOL-PROPS")
        if xml_child is not None:
            data["symbol_props"] = self._read_symbol_props(xml_child)

    def _read_application_sw_component_type(self,
                                            xml_element: ElementTree.Element
                                            ) -> ar_element.ApplicationSoftwareComponentType:
        """
        Reads complex type AR:APPLICATION-SW-COMPONENT-TYPE
        Tag variants: 'APPLICATION-SW-COMPONENT-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_component_type(child_elements, data)
        self._read_atomic_sw_component_type(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ApplicationSoftwareComponentType(**data)

    def _read_sw_component_prototype(self, xml_element: ElementTree.Element) -> ar_element.SwComponentPrototype:
        """
        Complex type AR:SW-COMPONENT-PROTOTYPE
        Tag variants: 'SW-COMPONENT-PROTOTYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_component_type(child_elements, data)
        xml_child = child_elements.get("TYPE-TREF")
        if xml_child is not None:
            data["type_ref"] = self._read_sw_component_type_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwComponentPrototype(**data)

    def _read_port_in_composition_type_instance_ref(self,
                                                    xml_element: ElementTree.Element
                                                    ) -> ar_element.PortInCompositionTypeInstanceRef:
        """
        Writes merge of complex types AR:P-PORT-IN-COMPOSITION-INSTANCE-REF
        and R-PORT-IN-COMPOSITION-INSTANCE-REF
        Tag variants: 'PROVIDER-IREF' | 'P-PORT-IN-COMPOSITION-INSTANCE-REF' |
                      'REQUESTER-IREF'| 'R-PORT-IN-COMPOSITION-INSTANCE-REF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-COMPONENT-REF")
        if xml_child is not None:
            data["component_ref"] = self._read_sw_component_prototype_ref(xml_child)
        if xml_element.tag in ("PROVIDER-IREF", "P-PORT-IN-COMPOSITION-INSTANCE-REF"):
            port_ref_tag = "TARGET-P-PORT-REF"
        elif xml_element.tag in ("REQUESTER-IREF", "R-PORT-IN-COMPOSITION-INSTANCE-REF"):
            port_ref_tag = "TARGET-R-PORT-REF"
        else:
            raise ValueError(f"Unknown XML tag: '{xml_element.tag}'")
        xml_child = child_elements.get(port_ref_tag)
        if xml_child is not None:
            data["port_ref"] = self._read_port_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.PortInCompositionTypeInstanceRef(**data)

    def _read_assembly_sw_connector(self, xml_element: ElementTree.Element) -> ar_element.AssemblySwConnector:
        """
        Reads complex type AR:ASSEMBLY-SW-CONNECTOR
        Tag variants: 'ASSEMBLY-SW-CONNECTOR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_connector(child_elements, data)
        xml_child = child_elements.get("PROVIDER-IREF")
        if xml_child is not None:
            data["provide_port"] = self._read_port_in_composition_type_instance_ref(xml_child)
        xml_child = child_elements.get("REQUESTER-IREF")
        if xml_child is not None:
            data["require_port"] = self._read_port_in_composition_type_instance_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AssemblySwConnector(**data)

    def _read_sw_connector(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SW-CONNECTOR
        """
        child_elements.skip("MAPPING-REF")
        child_elements.skip("VARIATION-POINT")

    def _read_delegation_sw_connector(self, xml_element: ElementTree.Element) -> ar_element.DelegationSwConnector:
        """
        Reads complex type AR:DELEGATION-SW-CONNECTOR
        Tag variants: 'DELEGATION-SW-CONNECTOR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_connector(child_elements, data)
        xml_child = child_elements.get("INNER-PORT-IREF")
        if xml_child is not None:
            xml_grand_child = xml_child.find("./*")
            if xml_grand_child.tag in ("P-PORT-IN-COMPOSITION-INSTANCE-REF",
                                       "R-PORT-IN-COMPOSITION-INSTANCE-REF"):
                data["inner_port"] = self._read_port_in_composition_type_instance_ref(xml_grand_child)
        xml_child = child_elements.get("OUTER-PORT-REF")
        if xml_child is not None:
            data["outer_port"] = self._read_port_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DelegationSwConnector(**data)

    def _read_pass_through_sw_connector(self, xml_element: ElementTree.Element) -> ar_element.PassThroughSwConnector:
        """
        Complex type AR:PASS-THROUGH-SW-CONNECTOR
        Tag variants: 'PASS-THROUGH-SW-CONNECTOR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_connector(child_elements, data)
        xml_child = child_elements.get("PROVIDED-OUTER-PORT-REF")
        if xml_child is not None:
            data["provide_port"] = self._read_port_prototype_ref(xml_child)
        xml_child = child_elements.get("REQUIRED-OUTER-PORT-REF")
        if xml_child is not None:
            data["require_port"] = self._read_port_prototype_ref(xml_child)
        child_elements.skip("SERVICE-INTERFACE-ELEMENT-MAPPING-REFS")
        self._report_unprocessed_elements(child_elements)
        return ar_element.PassThroughSwConnector(**data)

    def _read_composition_sw_component_type(self,
                                            xml_element: ElementTree.Element
                                            ) -> ar_element.CompositionSwComponentType:
        """
        Reads complex type AR:COMPOSITION-SW-COMPONENT-TYPE
        Tag variants: 'COMPOSITION-SW-COMPONENT-TYPE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_sw_component_type(child_elements, data)
        self._read_composition_sw_component_type_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.CompositionSwComponentType(**data)

    def _read_composition_sw_component_type_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:COMPOSITION-SW-COMPONENT-TYPE
        """
        xml_child = child_elements.get("COMPONENTS")
        if xml_child is not None:
            component_list = []
            for xml_grand_child in xml_child.findall("./*"):
                component_list.append(self._read_sw_component_prototype(xml_grand_child))
            data["components"] = component_list
        xml_child = child_elements.get("CONNECTORS")
        if xml_child is not None:
            connector_list = []
            for xml_grand_child in xml_child.findall("./*"):
                if xml_grand_child.tag == "ASSEMBLY-SW-CONNECTOR":
                    connector_list.append(self._read_assembly_sw_connector(xml_grand_child))
                elif xml_grand_child.tag == "DELEGATION-SW-CONNECTOR":
                    connector_list.append(self._read_delegation_sw_connector(xml_grand_child))
                elif xml_grand_child.tag == "PASS-THROUGH-SW-CONNECTOR":
                    connector_list.append(self._read_pass_through_sw_connector(xml_grand_child))
            data["connectors"] = connector_list
        child_elements.skip("CONSTANT-VALUE-MAPPING-REFS")
        child_elements.skip("DATA-TYPE-MAPPING-REFS")
        child_elements.skip("INSTANTIATION-RTE-EVENT-PROPSS")

    def _read_swc_implementation(self,
                                 xml_element: ElementTree.Element
                                 ) -> ar_element.SwcImplementation:
        """
        Reads complex type AR:SWC-IMPLEMENTATION
        Tag variants: 'SWC-IMPLEMENTATION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_implementation(child_elements, data)
        self._read_swc_implementation_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwcImplementation(**data)

    def _read_swc_implementation_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:COMPOSITION-SW-COMPONENT-TYPE
        """
        xml_child = child_elements.get("BEHAVIOR-REF")
        if xml_child is not None:
            data["behavior_ref"] = self._read_swc_internal_behavior_ref(xml_child)
        child_elements.skip("PER-INSTANCE-MEMORY-SIZES")  # Not yet supported
        xml_child = child_elements.get("REQUIRED-RTE-VENDOR")
        if xml_child is not None:
            data["required_rte_vendor"] = xml_child.text

    def _read_p_mode_group_in_atomic_swc_instance_ref(self,
                                                      xml_element: ElementTree.Element
                                                      ) -> ar_element.PModeGroupInAtomicSwcInstanceRef:
        """
        Reads complex type AR:P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF' | 'MODE-GROUP-IREF' |
                      'SWC-MODE-GROUP-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-P-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_provided_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-MODE-GROUP-REF")
        if xml_child is not None:
            child_element = self._read_mode_declaration_group_prototype_ref(xml_child)
            data["target_mode_group"] = child_element
        return ar_element.PModeGroupInAtomicSwcInstanceRef(**data)

    def _read_p_operation_in_atomic_swc_instance_ref(self,
                                                     xml_element: ElementTree.Element
                                                     ) -> ar_element.POperationInAtomicSwcInstanceRef:
        """
        Complex type AR:P-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'OPERATION-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-P-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_provided_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-PROVIDED-OPERATION-REF")
        if xml_child is not None:
            data["target_provided_operation"] = self._read_client_server_operation_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.POperationInAtomicSwcInstanceRef(**data)

    def _read_p_trigger_in_atomic_swc_instance_ref(self,
                                                   xml_element: ElementTree.Element
                                                   ) -> ar_element.PTriggerInAtomicSwcTypeInstanceRef:
        """
        Reads complex type AR:P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
        Tag variants: 'P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF' | 'SWC-TRIGGER-IREF' |
                      'TRIGGER-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-P-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_provided_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-TRIGGER-REF")
        if xml_child is not None:
            data["target_trigger"] = self._read_trigger_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.PTriggerInAtomicSwcTypeInstanceRef(**data)

    def _read_r_mode_in_atomic_swc_instance_ref(self,
                                                xml_element: ElementTree.Element
                                                ) -> ar_element.RModeInAtomicSwcInstanceRef:
        """
        Reads complex type AR:R-MODE-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'DISABLED-MODE-IREF' | 'MODE-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_required_port_prototype_ref(xml_child)
        xml_child = child_elements.get("CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF")
        if xml_child is not None:
            child_element = self._read_mode_declaration_group_prototype_ref(xml_child)
            data["context_mode_declaration_group_prototype"] = child_element
        xml_child = child_elements.get("TARGET-MODE-DECLARATION-REF")
        if xml_child is not None:
            data["target_mode_declaration"] = self._read_mode_declaration_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.RModeInAtomicSwcInstanceRef(**data)

    def _read_r_mode_group_in_atomic_swc_instance_ref(self,
                                                      xml_element: ElementTree.Element
                                                      ) -> ar_element.RModeGroupInAtomicSwcInstanceRef:
        """
        Complex type AR:R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-R-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_required_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-MODE-GROUP-REF")
        if xml_child is not None:
            child_element = self._read_mode_declaration_group_prototype_ref(xml_child)
            data["target_mode_group"] = child_element
        return ar_element.RModeGroupInAtomicSwcInstanceRef(**data)

    def _read_r_operation_in_atomic_swc_instance_ref(self,
                                                     xml_element: ElementTree.Element
                                                     ) -> ar_element.ROperationInAtomicSwcInstanceRef:
        """
        Complex type AR:R-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'OPERATION-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-R-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_required_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-REQUIRED-OPERATION-REF")
        if xml_child is not None:
            data["target_required_operation"] = self._read_client_server_operation_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ROperationInAtomicSwcInstanceRef(**data)

    def _read_r_variable_in_atomic_swc_instance_ref(self,
                                                    xml_element: ElementTree.Element
                                                    ) -> ar_element.RVariableInAtomicSwcInstanceRef:
        """
        Reads complex type AR:R-VARIABLE-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'DATA-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-R-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_required_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-DATA-ELEMENT-REF")
        if xml_child is not None:
            data["target_data_element"] = self._read_variable_data_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.RVariableInAtomicSwcInstanceRef(**data)

    def _read_r_trigger_in_atomic_swc_instance_ref(self,
                                                   xml_element: ElementTree.Element
                                                   ) -> ar_element.RTriggerInAtomicSwcInstanceRef:
        """
        Reads complex type AR:R-TRIGGER-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'TRIGGER-IREF' | 'REQUIRED-TRIGGER-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("CONTEXT-R-PORT-REF")
        if xml_child is not None:
            data["context_port"] = self._read_abstract_required_port_prototype_ref(xml_child)
        xml_child = child_elements.get("TARGET-TRIGGER-REF")
        if xml_child is not None:
            data["target_trigger"] = self._read_trigger_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.RTriggerInAtomicSwcInstanceRef(**data)

    # --- Internal Behavior elements

    def _read_variable_in_impl_data_instance_ref(self,
                                                 xml_element: ElementTree.Element
                                                 ) -> ar_element.ArVariableInImplementationDataInstanceRef:
        """
        Reads complex type AR:AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
        Tag variants: 'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE' | 'IMPLEMENTATION-DATA-TYPE-ELEMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_variable_in_impl_data_instance_ref_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ArVariableInImplementationDataInstanceRef(**data)

    def _read_variable_in_impl_data_instance_ref_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
        """
        xml_child = child_elements.get("PORT-PROTOTYPE-REF")
        if xml_child is not None:
            data["port_prototype_ref"] = self._read_port_prototype_ref(xml_child)
        xml_child = child_elements.get("ROOT-VARIABLE-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["root_variable_data_prototype_ref"] = self._read_variable_data_prototype_ref(xml_child)
        xml_child = child_elements.get("CONTEXT-DATA-PROTOTYPE-REFS")
        if xml_child is not None:
            data_prototype_refs = []
            for xml_grand_child in xml_child.findall("./CONTEXT-DATA-PROTOTYPE-REF"):
                data_prototype_refs.append(self._read_abstract_impl_data_type_element_ref(xml_grand_child))
            data["context_data_prototype_refs"] = data_prototype_refs
        xml_child = child_elements.get("TARGET-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["target_data_prototype_ref"] = self._read_abstract_impl_data_type_element_ref(xml_child)

    def _read_variable_in_atomic_swc_type_instance_ref(self,
                                                       xml_element: ElementTree.Element
                                                       ) -> ar_element.VariableInAtomicSWCTypeInstanceRef:
        """
        Reads Complex type AR:VARIABLE-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
        Tag variants: 'AUTOSAR-VARIABLE-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("PORT-PROTOTYPE-REF")
        if xml_child is not None:
            data["port_prototype_ref"] = self._read_port_prototype_ref(xml_child)
        xml_child = child_elements.get("ROOT-VARIABLE-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["root_variable_data_prototype_ref"] = self._read_variable_data_prototype_ref(xml_child)
        # For some reason there can be an unbounded amount of CONTEXT-DATA-PROTOTYPE-REF directly in the
        #  xml element. We need to call skip on child_elements then attempt to manually find the children.
        child_elements.skip("CONTEXT-DATA-PROTOTYPE-REF")
        data_prototype_refs = []
        for xml_child in xml_element.findall("./CONTEXT-DATA-PROTOTYPE-REF"):
            data_prototype_refs.append(self._read_appl_composite_element_data_proto_ref(xml_child))
        if data_prototype_refs:
            data["context_data_prototype_refs"] = data_prototype_refs
        xml_child = child_elements.get("TARGET-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["target_data_prototype_ref"] = self._read_data_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.VariableInAtomicSWCTypeInstanceRef(**data)

    def _read_variable_access(self, xml_element: ElementTree.Element) -> ar_element.VariableAccess:
        """
        Reads complex type AR:VARIABLE-ACCESS
        Tag variants: 'REPLACE-WITH' | 'VARIABLE-ACCESS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_variable_access_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.VariableAccess(**data)

    def _read_variable_access_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:VARIABLE-ACCESS
        """
        xml_child = child_elements.get("ACCESSED-VARIABLE")
        if xml_child is not None:
            data["accessed_variable"] = self._read_autosar_variable_ref(xml_child)
        xml_child = child_elements.get("SCOPE")
        if xml_child is not None:
            data["scope"] = ar_enum.xml_to_enum("VariableAccessScope", xml_child.text)

    def _read_autosar_variable_ref(self, xml_element: ElementTree.Element) -> ar_element.AutosarVariableRef:
        """
        Reads Complex type AR:AUTOSAR-VARIABLE-REF
        Tag variants: 'VARIABLE-INSTANCE' | 'NV-RAM-BLOCK-ELEMENT' | 'READ-NV-DATA' |
                      'WRITTEN-NV-DATA' | 'WRITTEN-READ-NV-DATA' | 'USED-DATA-ELEMENT' |
                      'AUTOSAR-VARIABLE' | 'ACCESSED-VARIABLE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_autosar_variable_ref_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AutosarVariableRef(**data)

    def _read_autosar_variable_ref_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:AUTOSAR-VARIABLE-REF
        """
        xml_child = child_elements.get("AUTOSAR-VARIABLE-IN-IMPL-DATATYPE")
        if xml_child is not None:
            elem = self._read_variable_in_impl_data_instance_ref(xml_child)
            data["ar_variable_in_impl_datatype"] = elem
        xml_child = child_elements.get("AUTOSAR-VARIABLE-IREF")
        if xml_child is not None:
            data["ar_variable_iref"] = self._read_variable_in_atomic_swc_type_instance_ref(xml_child)
        xml_child = child_elements.get("LOCAL-VARIABLE-REF")
        if xml_child is not None:
            data["local_variable_ref"] = self._read_variable_data_prototype_ref(xml_child)

    def _read_executable_entity_activation_reason(self,
                                                  xml_element: ElementTree.Element
                                                  ) -> ar_element.ExecutableEntityActivationReason:
        """
        Reads complex type AR:EXECUTABLE-ENTITY-ACTIVATION-REASON
        Tag variants: 'EXECUTABLE-ENTITY-ACTIVATION-REASON'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_implementation_props(child_elements, data)
        xml_child = child_elements.get("BIT-POSITION")
        if xml_child is not None:
            data["bit_position"] = ar_element.PositiveIntegerValue(xml_child.text).value
        self._report_unprocessed_elements(child_elements)
        return ar_element.ExecutableEntityActivationReason(**data)

    def _read_exclusive_area_ref_conditional(self,
                                             xml_element: ElementTree.Element
                                             ) -> ar_element.ExclusiveAreaRefConditional:
        """
        Reads complex type AR:EXCLUSIVE-AREA-REF-CONDITIONAL
        Tag variants: 'EXCLUSIVE-AREA-REF-CONDITIONAL'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("EXCLUSIVE-AREA-REF")
        if xml_child is not None:
            data["exclusive_area"] = self._read_exclusive_area_ref(xml_child)
        child_elements.skip("VARIATION-POINT")  # Not supported
        self._report_unprocessed_elements(child_elements)
        return ar_element.ExclusiveAreaRefConditional(**data)

    def _read_runnable_entity_argument(self, xml_element: ElementTree.Element) -> ar_element.RunnableEntityArgument:
        """
        Reads complex type AR:RUNNABLE-ENTITY-ARGUMENT
        Tag variants: 'RUNNABLE-ENTITY-ARGUMENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SYMBOL")
        if xml_child is not None:
            data["symbol"] = xml_child.text  # TODO: Check if valid C-STRING
        self._report_unprocessed_elements(child_elements)
        return ar_element.RunnableEntityArgument(**data)

    def _read_abstract_access_point(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SERVER-CALL-POINT
        """
        xml_child = child_elements.get("RETURN-VALUE-PROVISION")
        if xml_child is not None:
            data["return_value_provision"] = ar_enum.xml_to_enum("RteApiReturnValueProvision", xml_child.text)

    def _read_server_call_point(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ABSTRACT-ACCESS-POINT
        """
        xml_child = child_elements.get("OPERATION-IREF")
        if xml_child is not None:
            data["operation"] = self._read_r_operation_in_atomic_swc_instance_ref(xml_child)
        xml_child = child_elements.get("TIMEOUT")
        if xml_child is not None:
            data["timeout"] = self._read_number(xml_child.text)
        child_elements.skip("VARIATION-POINT")

    def _read_async_server_call_point(self, xml_element: ElementTree.Element) -> ar_element.AsynchronousServerCallPoint:
        """
        Reads complex type: AR:ASYNCHRONOUS-SERVER-CALL-POINT
        Tag variants: 'ASYNCHRONOUS-SERVER-CALL-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        self._read_server_call_point(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AsynchronousServerCallPoint(**data)

    def _read_sync_server_call_point(self, xml_element: ElementTree.Element) -> ar_element.SynchronousServerCallPoint:
        """
        Reads complex type: AR:SYNCHRONOUS-SERVER-CALL-POINT
        Tag variants: 'SYNCHRONOUS-SERVER-CALL-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        self._read_server_call_point(child_elements, data)
        xml_child = child_elements.get("CALLED-FROM-WITHIN-EXCLUSIVE-AREA-REF")
        if xml_child is not None:
            data["called_from_within_exclusive_area"] = self._read_exclusive_area_nesting_order_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SynchronousServerCallPoint(**data)

    def _read_async_server_call_result_point(self,
                                             xml_element: ElementTree.Element
                                             ) -> ar_element.AsynchronousServerCallResultPoint:
        """
        Reads complex type: AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT
        Tag variants: 'ASYNCHRONOUS-SERVER-CALL-RESULT-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        self._read_async_server_call_result_point_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AsynchronousServerCallResultPoint(**data)

    def _read_async_server_call_result_point_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:ASYNCHRONOUS-SERVER-CALL-RESULT-POINT
        """
        xml_child = child_elements.get("ASYNCHRONOUS-SERVER-CALL-POINT-REF")
        if xml_child is not None:
            data["async_server_call_point"] = self._read_async_server_call_point_ref(xml_child)

    def _read_external_triggering_point_ident(self,
                                              xml_element: ElementTree.Element
                                              ) -> ar_element.ExternalTriggeringPointIdent:
        """
        Reads complex type AR:EXTERNAL-TRIGGERING-POINT-IDENT
        Tag variants: 'IDENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        return ar_element.ExternalTriggeringPointIdent(**data)

    def _read_external_triggering_point(self, xml_element: ElementTree.Element) -> ar_element.ExternalTriggeringPoint:
        """
        Reads complex type AR:EXTERNAL-TRIGGERING-POINT
        Tag variants: 'EXTERNAL-TRIGGERING-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("IDENT")
        if xml_child is not None:
            data["ident"] = self._read_external_triggering_point_ident(xml_child)
        xml_child = child_elements.get("TRIGGER-IREF")
        if xml_child is not None:
            data["trigger"] = self._read_p_trigger_in_atomic_swc_instance_ref(xml_child)
        child_elements.skip("VARIATION-POINT")
        self._report_unprocessed_elements(child_elements)
        return ar_element.ExternalTriggeringPoint(**data)

    def _read_internal_triggering_point(self, xml_element: ElementTree.Element) -> ar_element.InternalTriggeringPoint:
        """
        Reads complex type AR:INTERNAL-TRIGGERING-POINT
        Tag variants: 'INTERNAL-TRIGGERING-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        xml_child = child_elements.get("SW-IMPL-POLICY")
        if xml_child is not None:
            data["sw_impl_policy"] = ar_enum.xml_to_enum("SwImplPolicy", xml_child.text)
        child_elements.skip("VARIATION-POINT")
        self._report_unprocessed_elements(child_elements)
        return ar_element.InternalTriggeringPoint(**data)

    def _read_mode_access_point_ident(self,
                                      xml_element: ElementTree.Element
                                      ) -> ar_element.ModeAccessPointIdent:
        """
        Complex type AR:MODE-ACCESS-POINT-IDENT
        Tag variants: 'IDENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        self._read_async_server_call_result_point_group(child_elements, data)
        return ar_element.ModeAccessPointIdent(**data)

    def _read_mode_access_point(self, xml_element: ElementTree.Element) -> ar_element.ModeAccessPoint:
        """
        Reads complex type AR:MODE-ACCESS-POINT
        Tag variants: 'MODE-ACCESS-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("IDENT")
        if xml_child is not None:
            data["ident"] = self._read_mode_access_point_ident(xml_child)
        xml_child = child_elements.get("MODE-GROUP-IREF")
        if xml_child is not None and len(xml_child) > 0:
            xml_grand_child = xml_child[0]
            if xml_grand_child.tag == "P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF":
                data["mode_group"] = self._read_p_mode_group_in_atomic_swc_instance_ref(xml_grand_child)
            elif xml_grand_child.tag == "R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF":
                data["mode_group"] = self._read_r_mode_group_in_atomic_swc_instance_ref(xml_grand_child)
        child_elements.skip("VARIATION-POINT")
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeAccessPoint(**data)

    def _read_mode_switch_point(self, xml_element: ElementTree.Element) -> ar_element.ModeSwitchPoint:
        """
        Reads complex Type AR:MODE-SWITCH-POINT
        Tag variants: 'MODE-SWITCH-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        xml_child = child_elements.get("MODE-GROUP-IREF")
        if xml_child is not None:
            data["mode_group"] = self._read_p_mode_group_in_atomic_swc_instance_ref(xml_child)
        child_elements.skip("VARIATION-POINT")
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeSwitchPoint(**data)

    def _read_parameter_in_atomic_swc_type_instance_ref(self,
                                                        xml_element: ElementTree.Element
                                                        ) -> ar_element.ParameterInAtomicSwcTypeInstanceRef:
        """
        Reads complex type AR:PARAMETER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
        Tag variants: 'AUTOSAR-PARAMETER-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("PORT-PROTOTYPE-REF")
        if xml_child is not None:
            data["port_prototype"] = self._read_port_prototype_ref(xml_child)
        xml_child = child_elements.get("ROOT-PARAMETER-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["root_parameter_data_prototype"] = self._read_data_prototype_ref(xml_child)
        xml_child = child_elements.get("CONTEXT-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["context_data_prototype"] = self._read_appl_composite_element_data_proto_ref(xml_child)
        xml_child = child_elements.get("TARGET-DATA-PROTOTYPE-REF")
        if xml_child is not None:
            data["target_data_prototype"] = self._read_data_prototype_ref(xml_child)
        xml_child = child_elements.get("MODE-GROUP-IREF")
        child_elements.skip("VARIATION-POINT")
        self._report_unprocessed_elements(child_elements)
        return ar_element.ParameterInAtomicSwcTypeInstanceRef(**data)

    def _read_autosar_parameter_ref(self, xml_element: ElementTree.Element) -> ar_element.AutosarParameterRef:
        """
        Reads complex type AR:AUTOSAR-PARAMETER-REF
        Tag variants: 'PARAMETER-INSTANCE' | 'ACCESSED-PARAMETER' | 'USED-PARAMETER-ELEMENT' | 'AR-PARAMETER'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("AUTOSAR-PARAMETER-IREF")
        if xml_child is not None:
            data["autosar_parameter"] = self._read_parameter_in_atomic_swc_type_instance_ref(xml_child)
        xml_child = child_elements.get("LOCAL-PARAMETER-REF")
        if xml_child is not None:
            data["local_parameter"] = self._read_data_prototype_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AutosarParameterRef(**data)

    def _read_parameter_access(self, xml_element: ElementTree.Element) -> ar_element.ParameterAccess:
        """
        Reads complex type AR:PARAMETER-ACCESS
        Tag variants: 'PARAMETER-ACCESS'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_abstract_access_point(child_elements, data)
        self._read_parameter_access_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ParameterAccess(**data)

    def _read_parameter_access_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PARAMETER-ACCESS
        """
        xml_child = child_elements.get("ACCESSED-PARAMETER")
        if xml_child is not None:
            data["accessed_parameter"] = self._read_autosar_parameter_ref(xml_child)
        xml_child = child_elements.get("SW-DATA-DEF-PROPS")
        if xml_child is not None:
            data["sw_data_def_props"] = self._read_sw_data_def_props(xml_child)
        child_elements.skip("VARIATION-POINT")

    def _read_wait_point(self, xml_element: ElementTree.Element) -> ar_element.WaitPoint:
        """
        Reads complex type AR:WAIT-POINT
        Tag variants: 'WAIT-POINT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_wait_point_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.WaitPoint(**data)

    def _read_wait_point_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:WAIT-POINT
        """
        xml_child = child_elements.get("TIMEOUT")
        if xml_child is not None:
            data["timeout"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("TRIGGER-REF")
        if xml_child is not None:
            data["trigger"] = self._read_rte_event_ref(xml_child)

    def _read_executable_entity(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:EXECUTABLE-ENTITY
        """
        xml_child = child_elements.get("ACTIVATION-REASONS")
        if xml_child is not None:
            activation_reasons = []
            for xml_grand_child in xml_child.findall("./EXECUTABLE-ENTITY-ACTIVATION-REASON"):
                activation_reasons.append(self._read_executable_entity_activation_reason(xml_grand_child))
            data["activation_reasons"] = activation_reasons
        if not isinstance(self.schema_version, int):
            raise RuntimeError("Schema version is not set, unable to proceed")
        if self.schema_version < 50:
            xml_child = child_elements.get("CAN-ENTER-EXCLUSIVE-AREA-REFS")
            if xml_child is not None:
                can_enter_leave = []
                for xml_grand_child in xml_child.findall("./CAN-ENTER-EXCLUSIVE-AREA-REF"):
                    # The class constructor will automatically upgrade these references to
                    # ExclusiveAreaRefConditional elements.
                    can_enter_leave.append(self._read_exclusive_area_ref(xml_grand_child))
                data["can_enter_leave"] = can_enter_leave
        else:
            xml_child = child_elements.get("CAN-ENTERS")
            if xml_child is not None:
                can_enter_leave = []
                for xml_grand_child in xml_child.findall("./EXCLUSIVE-AREA-REF-CONDITIONAL"):
                    can_enter_leave.append(self._read_exclusive_area_ref_conditional(xml_grand_child))
                data["can_enter_leave"] = can_enter_leave
        xml_child = child_elements.get("EXCLUSIVE-AREA-NESTING-ORDER-REFS")
        if xml_child is not None:
            exclusive_area_nesting_order = []
            for xml_grand_child in xml_child.findall("./EXCLUSIVE-AREA-NESTING-ORDER-REF"):
                exclusive_area_nesting_order.append(self._read_exclusive_area_nesting_order_ref(xml_grand_child))
            data["exclusive_area_nesting_order"] = exclusive_area_nesting_order
        xml_child = child_elements.get("MINIMUM-START-INTERVAL")
        if xml_child is not None:
            data["minimum_start_interval"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("REENTRANCY-LEVEL")
        if xml_child is not None:
            data["reentrancy_level"] = ar_enum.xml_to_enum("ReentrancyLevel", xml_child.text)
        if self.schema_version < 50:
            xml_child = child_elements.get("RUNS-INSIDE-EXCLUSIVE-AREA-REFS")
            if xml_child is not None:
                runs_insides = []
                for xml_grand_child in xml_child.findall("./RUNS-INSIDE-EXCLUSIVE-AREA-REF"):
                    # The class constructor will automatically upgrade these references to
                    # ExclusiveAreaRefConditional elements.
                    runs_insides.append(self._read_exclusive_area_ref(xml_grand_child))
                data["runs_insides"] = runs_insides
        else:
            xml_child = child_elements.get("RUNS-INSIDES")
            if xml_child is not None:
                runs_insides = []
                for xml_grand_child in xml_child.findall("./EXCLUSIVE-AREA-REF-CONDITIONAL"):
                    runs_insides.append(self._read_exclusive_area_ref_conditional(xml_grand_child))
                data["runs_insides"] = runs_insides
        xml_child = child_elements.get('SW-ADDR-METHOD-REF')
        if xml_child is not None:
            data['sw_addr_method'] = self._read_sw_addr_method_ref(xml_child)

    def _read_runnable_entity(self, xml_element: ElementTree.Element) -> ar_element.RunnableEntity:
        """
        Reads complex type AR:RUNNABLE-ENTITY
        Tag variants: 'RUNNABLE-ENTITY'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_executable_entity(child_elements, data)
        self._read_runnable_entity_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.RunnableEntity(**data)

    def _read_runnable_entity_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:RUNNABLE-ENTITY
        """
        xml_child = child_elements.get("ARGUMENTS")
        if xml_child is not None:
            arguments = []
            for xml_grand_child in xml_child.findall("./RUNNABLE-ENTITY-ARGUMENT"):
                arguments.append(self._read_runnable_entity_argument(xml_grand_child))
            data["argument"] = arguments
        xml_child = child_elements.get("ASYNCHRONOUS-SERVER-CALL-RESULT-POINTS")
        if xml_child is not None:
            async_server_call_result_points = []
            for xml_grand_child in xml_child.findall("./ASYNCHRONOUS-SERVER-CALL-RESULT-POINT"):
                async_server_call_result_points.append(self._read_async_server_call_result_point(xml_grand_child))
            data["async_server_call_result_point"] = async_server_call_result_points
        xml_child = child_elements.get('CAN-BE-INVOKED-CONCURRENTLY')
        if xml_child is not None:
            data["can_be_invoked_concurrently"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("DATA-READ-ACCESSS")
        if xml_child is not None:
            data_read_access = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                data_read_access.append(self._read_variable_access(xml_grand_child))
            data["data_read_access"] = data_read_access
        xml_child = child_elements.get("DATA-RECEIVE-POINT-BY-ARGUMENTS")
        if xml_child is not None:
            data_receive_point_by_argument = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                data_receive_point_by_argument.append(self._read_variable_access(xml_grand_child))
            data["data_receive_point_by_argument"] = data_receive_point_by_argument
        xml_child = child_elements.get("DATA-RECEIVE-POINT-BY-VALUES")
        if xml_child is not None:
            data_receive_point_by_value = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                data_receive_point_by_value.append(self._read_variable_access(xml_grand_child))
            data["data_receive_point_by_value"] = data_receive_point_by_value
        xml_child = child_elements.get("DATA-SEND-POINTS")
        if xml_child is not None:
            data_send_points = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                data_send_points.append(self._read_variable_access(xml_grand_child))
            data["data_send_point"] = data_send_points
        xml_child = child_elements.get("DATA-WRITE-ACCESSS")
        if xml_child is not None:
            data_write_access = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                data_write_access.append(self._read_variable_access(xml_grand_child))
            data["data_write_access"] = data_write_access
        xml_child = child_elements.get("EXTERNAL-TRIGGERING-POINTS")
        if xml_child is not None:
            external_triggering_point = []
            for xml_grand_child in xml_child.findall("./EXTERNAL-TRIGGERING-POINT"):
                external_triggering_point.append(self._read_external_triggering_point(xml_grand_child))
            data["external_triggering_point"] = external_triggering_point
        xml_child = child_elements.get("INTERNAL-TRIGGERING-POINTS")
        if xml_child is not None:
            internal_triggering_point = []
            for xml_grand_child in xml_child.findall("./INTERNAL-TRIGGERING-POINT"):
                internal_triggering_point.append(self._read_internal_triggering_point(xml_grand_child))
            data["internal_triggering_point"] = internal_triggering_point
        xml_child = child_elements.get("MODE-ACCESS-POINTS")
        if xml_child is not None:
            mode_access_point = []
            for xml_grand_child in xml_child.findall("./MODE-ACCESS-POINT"):
                mode_access_point.append(self._read_mode_access_point(xml_grand_child))
            data["mode_access_point"] = mode_access_point
        xml_child = child_elements.get("MODE-SWITCH-POINTS")
        if xml_child is not None:
            mode_switch_point = []
            for xml_grand_child in xml_child.findall("./MODE-SWITCH-POINT"):
                mode_switch_point.append(self._read_mode_switch_point(xml_grand_child))
            data["mode_switch_point"] = mode_switch_point
        xml_child = child_elements.get("PARAMETER-ACCESSS")
        if xml_child is not None:
            parameter_access = []
            for xml_grand_child in xml_child.findall("./PARAMETER-ACCESS"):
                parameter_access.append(self._read_parameter_access(xml_grand_child))
            data["parameter_access"] = parameter_access
        xml_child = child_elements.get("READ-LOCAL-VARIABLES")
        if xml_child is not None:
            read_local_variable = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                read_local_variable.append(self._read_variable_access(xml_grand_child))
            data["read_local_variable"] = read_local_variable
        xml_child = child_elements.get("SERVER-CALL-POINTS")
        if xml_child is not None:
            server_call_points = []
            for xml_grand_child in xml_child.findall("./*"):
                if xml_grand_child.tag == "ASYNCHRONOUS-SERVER-CALL-POINT":
                    server_call_points.append(self._read_async_server_call_point(xml_grand_child))
                elif xml_grand_child.tag == "SYNCHRONOUS-SERVER-CALL-POINT":
                    server_call_points.append(self._read_sync_server_call_point(xml_grand_child))
            data["server_call_point"] = server_call_points
        xml_child = child_elements.get("SYMBOL")
        if xml_child is not None:
            data["symbol"] = xml_child.text
        xml_child = child_elements.get("WAIT-POINTS")
        if xml_child is not None:
            wait_points = []
            for xml_grand_child in xml_child.findall("./WAIT-POINT"):
                wait_points.append(self._read_wait_point(xml_grand_child))
            data["wait_point"] = wait_points
        xml_child = child_elements.get("WRITTEN-LOCAL-VARIABLES")
        if xml_child is not None:
            write_local_variables = []
            for xml_grand_child in xml_child.findall("./VARIABLE-ACCESS"):
                write_local_variables.append(self._read_variable_access(xml_grand_child))
            data["write_local_variable"] = write_local_variables
        child_elements.skip("VARIATION-POINT")

    def _read_rte_event_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:RTE-EVENT
        """
        xml_child = child_elements.get("DISABLED-MODE-IREFS")
        if xml_child is not None:
            disabled_modes = []
            for xml_grand_child in xml_child.findall("./DISABLED-MODE-IREF"):
                disabled_modes.append(self._read_r_mode_in_atomic_swc_instance_ref(xml_grand_child))
            data["disabled_modes"] = disabled_modes
        xml_child = child_elements.get("START-ON-EVENT-REF")
        if xml_child is not None:
            data["start_on_event"] = self._read_runnable_entity_ref(xml_child)
        child_elements.skip("VARIATION-POINT")  # Not supported

    def _read_async_server_call_returns_event(self,
                                              xml_element: ElementTree.Element
                                              ) -> ar_element.AsynchronousServerCallReturnsEvent:
        """
        Reads complex type AR:ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT
        Tag variants: 'ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("EVENT-SOURCE-REF")
        if xml_child is not None:
            data["event_source"] = self._read_async_server_call_result_point_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.AsynchronousServerCallReturnsEvent(**data)

    def _read_background_event(self,
                               xml_element: ElementTree.Element
                               ) -> ar_element.BackgroundEvent:
        """
        Reads complex Type AR:BACKGROUND-EVENT
        Tag variants: 'BACKGROUND-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.BackgroundEvent(**data)

    def _read_data_receive_error_event(self,
                                       xml_element: ElementTree.Element
                                       ) -> ar_element.DataReceiveErrorEvent:
        """
        Reads complex Type AR:DATA-RECEIVE-ERROR-EVENT
        Tag variants: 'DATA-RECEIVE-ERROR-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("DATA-IREF")
        if xml_child is not None:
            data["data"] = self._read_r_variable_in_atomic_swc_instance_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataReceiveErrorEvent(**data)

    def _read_data_received_event(self,
                                  xml_element: ElementTree.Element
                                  ) -> ar_element.DataReceivedEvent:
        """
        Reads complex Type AR:DATA-RECEIVED-EVENT
        Tag variants: 'DATA-RECEIVED-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("DATA-IREF")
        if xml_child is not None:
            data["data"] = self._read_r_variable_in_atomic_swc_instance_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataReceivedEvent(**data)

    def _read_data_send_completed_event(self,
                                        xml_element: ElementTree.Element
                                        ) -> ar_element.DataSendCompletedEvent:
        """
        Reads complex Type AR:DATA-SEND-COMPLETED-EVENT
        Tag variants: 'DATA-SEND-COMPLETED-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("EVENT-SOURCE-REF")
        if xml_child is not None:
            data["event_source"] = self._read_variable_access_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataSendCompletedEvent(**data)

    def _read_data_write_completed_event(self,
                                         xml_element: ElementTree.Element
                                         ) -> ar_element.DataWriteCompletedEvent:
        """
        Reads complex type AR:DATA-WRITE-COMPLETED-EVENT
        Tag variants: 'DATA-WRITE-COMPLETED-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("EVENT-SOURCE-REF")
        if xml_child is not None:
            data["event_source"] = self._read_variable_access_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.DataWriteCompletedEvent(**data)

    def _read_external_trigger_occured_event(self,
                                             xml_element: ElementTree.Element
                                             ) -> ar_element.ExternalTriggerOccurredEvent:
        """
        Writes complex type AR:R-TRIGGER-IN-ATOMIC-SWC-INSTANCE-REF
        Tag variants: 'TRIGGER-IREF' | 'REQUIRED-TRIGGER-IREF'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("TRIGGER-IREF")
        if xml_child is not None:
            data["trigger"] = self._read_r_trigger_in_atomic_swc_instance_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ExternalTriggerOccurredEvent(**data)

    def _read_init_event(self,
                         xml_element: ElementTree.Element
                         ) -> ar_element.InitEvent:
        """
        Reads complex Type AR:INIT-EVENT
        Tag variants: 'INIT-EVENT''
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.InitEvent(**data)

    def _read_internal_trigger_occured_event(self,
                                             xml_element: ElementTree.Element
                                             ) -> ar_element.InternalTriggerOccurredEvent:
        """
        Reads complex type AR:INTERNAL-TRIGGER-OCCURRED-EVENT
        Tag variants: 'INTERNAL-TRIGGER-OCCURRED-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("EVENT-SOURCE-REF")
        if xml_child is not None:
            data["event_source"] = self._read_internal_triggering_point_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.InternalTriggerOccurredEvent(**data)

    def _read_mode_switched_ack_event(self,
                                      xml_element: ElementTree.Element
                                      ) -> ar_element.ModeSwitchedAckEvent:
        """
        Reads Complex type MODE-SWITCHED-ACK-EVENT
        Tag variants: 'MODE-SWITCHED-ACK-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("EVENT-SOURCE-REF")
        if xml_child is not None:
            data["event_source"] = self._read_mode_switch_point_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.ModeSwitchedAckEvent(**data)

    def _read_operation_invoked_event(self,
                                      xml_element: ElementTree.Element
                                      ) -> ar_element.OperationInvokedEvent:
        """
        Complex type AR:OPERATION-INVOKED-EVENT
        Tag variants: 'OPERATION-INVOKED-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("OPERATION-IREF")
        if xml_child is not None:
            data["operation"] = self._read_p_operation_in_atomic_swc_instance_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.OperationInvokedEvent(**data)

    def _read_swc_mode_manager_error_event(self,
                                           xml_element: ElementTree.Element
                                           ) -> ar_element.SwcModeManagerErrorEvent:
        """
        Reads complex type AR:SWC-MODE-MANAGER-ERROR-EVENT
        Tag variants: 'SWC-MODE-MANAGER-ERROR-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("MODE-GROUP-IREF")
        if xml_child is not None:
            data["mode_group"] = self._read_p_mode_group_in_atomic_swc_instance_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwcModeManagerErrorEvent(**data)

    def _read_swc_mode_switch_event(self,
                                    xml_element: ElementTree.Element
                                    ) -> ar_element.SwcModeSwitchEvent:
        """
        Reads complex type AR:SWC-MODE-SWITCH-EVENT
        Tag variants: 'SWC-MODE-SWITCH-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        self._read_swc_mode_switch_event_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwcModeSwitchEvent(**data)

    def _read_swc_mode_switch_event_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SWC-MODE-SWITCH-EVENT
        """
        xml_child = child_elements.get("ACTIVATION")
        if xml_child is not None:
            data["activation"] = ar_enum.xml_to_enum("ModeActivationKind", xml_child.text)
        xml_child = child_elements.get("MODE-IREFS")
        if xml_child is not None:
            modes = []
            for xml_grand_child in xml_child.findall("./MODE-IREF"):
                modes.append(self._read_r_mode_in_atomic_swc_instance_ref(xml_grand_child))
            if len(modes) == 0:
                pass
            elif len(modes) == 1:
                data["mode"] = modes[0]
            elif len(modes) == 2:
                data["mode"] = (modes[0], modes[1])
            else:
                self._raise_parse_error(xml_child, "Max two mode references are allowed")

    def _read_timing_event(self,
                           xml_element: ElementTree.Element
                           ) -> ar_element.TimingEvent:
        """
        Reads complex type AR:TIMING-EVENT
        Tag variants: 'TIMING-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        xml_child = child_elements.get("OFFSET")
        if xml_child is not None:
            data["offset"] = self._read_number(xml_child.text)
        xml_child = child_elements.get("PERIOD")
        if xml_child is not None:
            data["period"] = self._read_number(xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.TimingEvent(**data)

    def _read_transformer_hard_error_event(self,
                                           xml_element: ElementTree.Element
                                           ) -> ar_element.TransformerHardErrorEvent:
        """
        Reads complex type AR:TRANSFORMER-HARD-ERROR-EVENT
        Tag variants: 'TRANSFORMER-HARD-ERROR-EVENT'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_rte_event_group(child_elements, data)
        self._read_transformer_hard_error_event_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.TransformerHardErrorEvent(**data)

    def _read_transformer_hard_error_event_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:TRANSFORMER-HARD-ERROR-EVENT
        """
        xml_child = child_elements.get("OPERATION-IREF")
        if xml_child is not None:
            data["operation"] = self._read_p_operation_in_atomic_swc_instance_ref(xml_child)
        xml_child = child_elements.get("REQUIRED-TRIGGER-IREF")
        if xml_child is not None:
            data["required_trigger"] = self._read_r_trigger_in_atomic_swc_instance_ref(xml_child)
        xml_child = child_elements.get("TRIGGER-IREF")
        if xml_child is not None:
            data["trigger"] = self._read_p_trigger_in_atomic_swc_instance_ref(xml_child)

    def _read_port_defined_argument_value(self,
                                          xml_element: ElementTree.Element
                                          ) -> ar_element.PortDefinedArgumentValue:
        """
        Reads complex type AR:PORT-DEFINED-ARGUMENT-VALUE
        Tag variants: 'PORT-DEFINED-ARGUMENT-VALUE'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("VALUE")
        if xml_child is not None:
            try:
                xml_grand_child = xml_child.find("./*")
                if xml_grand_child is not None:
                    data["value"] = self._read_value_specification_element(xml_grand_child)
            except KeyError:
                pass
        xml_child = child_elements.get("VALUE-TYPE-TREF")
        if xml_child is not None:
            data["value_type"] = self._read_impl_data_type_ref(xml_child)
        self._report_unprocessed_elements(child_elements)
        return ar_element.PortDefinedArgumentValue(**data)

    def _read_communication_buffer_locking(self,
                                           xml_element: ElementTree.Element
                                           ) -> ar_element.CommunicationBufferLocking:
        """
        Reads complex type AR:COMMUNICATION-BUFFER-LOCKING
        Tag variantS: 'COMMUNICATION-BUFFER-LOCKING'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        xml_child = child_elements.get("SUPPORT-BUFFER-LOCKING")
        if xml_child is not None:
            data["support_buffer_locking"] = ar_enum.xml_to_enum("SupportBufferLocking", xml_child.text)
        self._report_unprocessed_elements(child_elements)
        return ar_element.CommunicationBufferLocking(**data)

    def _read_port_api_option(self,
                              xml_element: ElementTree.Element
                              ) -> ar_element.PortApiOption:
        """
        Reads complex type AR:PORT-API-OPTION
        Tag variants: 'PORT-API-OPTION'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_port_api_option_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.PortApiOption(**data)

    def _read_port_api_option_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:PORT-API-OPTION
        """
        xml_child = child_elements.get("ENABLE-TAKE-ADDRESS")
        if xml_child is not None:
            data["enable_take_address"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("ERROR-HANDLING")
        if xml_child is not None:
            data["error_handling"] = ar_enum.xml_to_enum("DataTransformationErrorHandling", xml_child.text)
        xml_child = child_elements.get("INDIRECT-API")
        if xml_child is not None:
            data["indirect_api"] = self._read_boolean(xml_child.text)
        xml_child = child_elements.get("PORT-ARG-VALUES")
        if xml_child is not None:
            port_arg_values = []
            for xml_grand_child in xml_child.findall("./PORT-DEFINED-ARGUMENT-VALUE"):
                port_arg_values.append(self._read_port_defined_argument_value(xml_grand_child))
            data["port_arg_values"] = port_arg_values
        xml_child = child_elements.get("PORT-REF")
        if xml_child is not None:
            data["port"] = self._read_port_prototype_ref(xml_child)
        xml_child = child_elements.get("PORT-REF")
        if xml_child is not None:
            data["port"] = self._read_port_prototype_ref(xml_child)
        xml_child = child_elements.get("SUPPORTED-FEATURES")
        if xml_child is not None:
            supported_features = []
            for xml_grand_child in xml_child.findall("./*"):
                if xml_grand_child.tag == "COMMUNICATION-BUFFER-LOCKING":
                    supported_features.append(self._read_communication_buffer_locking(xml_grand_child))
            data["supported_features"] = supported_features
        xml_child = child_elements.get("TRANSFORMER-STATUS-FORWARDING")
        if xml_child is not None:
            data["transformer_status_forwarding"] = ar_enum.xml_to_enum("DataTransformationStatusForwarding",
                                                                        xml_child.text)

    def _read_exclusive_area(self, xml_element: ElementTree.Element) -> ar_element.ExclusiveArea:
        """
        Reads complex type AR:EXCLUSIVE-AREA
        Tag variants: 'EXCLUSIVE-AREA'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        return ar_element.ExclusiveArea(**data)

    def _read_swc_internal_behavior(self, xml_element: ElementTree.Element) -> ar_element.SwcInternalBehavior:
        """
        Reads complex type AR:SWC-INTERNAL-BEHAVIOR
        Tag variants: 'SWC-INTERNAL-BEHAVIOR'
        """
        data = {}
        child_elements = ChildElementMap(xml_element)
        self._read_referrable(child_elements, data)
        self._read_multi_language_referrable(child_elements, data)
        self._read_identifiable(child_elements, xml_element.attrib, data)
        self._read_internal_behavior_group(child_elements, data)
        self._read_swc_internal_behavior_group(child_elements, data)
        self._report_unprocessed_elements(child_elements)
        return ar_element.SwcInternalBehavior(**data)

    def _read_internal_behavior_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:INTERNAL-BEHAVIOR
        """
        child_elements.skip("CONSTANT-MEMORYS")
        child_elements.skip("CONSTANT-VALUE-MAPPING-REFS")
        xml_child = child_elements.get("DATA-TYPE-MAPPING-REFS")
        if xml_child is not None:
            data_type_mappings = []
            for xml_grand_child in xml_child.findall("./DATA-TYPE-MAPPING-REF"):
                data_type_mappings.append(self._read_data_type_mapping_set_ref(xml_grand_child))
            data["data_type_mappings"] = data_type_mappings
        xml_child = child_elements.get("EXCLUSIVE-AREAS")
        if xml_child is not None:
            exclusive_areas = []
            for xml_grand_child in xml_child.findall("./EXCLUSIVE-AREA"):
                exclusive_areas.append(self._read_exclusive_area(xml_grand_child))
            data["exclusive_areas"] = exclusive_areas

        child_elements.skip("EXCLUSIVE-AREA-NESTING-ORDERS")
        child_elements.skip("STATIC-MEMORYS")

    def _read_swc_internal_behavior_group(self, child_elements: ChildElementMap, data: dict) -> None:
        """
        Reads group AR:SWC-INTERNAL-BEHAVIOR
        Most of it will be implemented in a future version
        """
        child_elements.skip("AR-TYPED-PER-INSTANCE-MEMORYS")
        xml_child = child_elements.get("EVENTS")
        if xml_child is not None:
            events = []
            for xml_grand_child in xml_child.findall("./*"):
                events.append(self._read_rte_event_element(xml_grand_child))
            data["events"] = events
        child_elements.skip("EXCLUSIVE-AREA-POLICYS")
        child_elements.skip("EXPLICIT-INTER-RUNNABLE-VARIABLES")
        child_elements.skip("HANDLE-TERMINATION-AND-RESTART")
        child_elements.skip("INCLUDED-DATA-TYPE-SETS")
        child_elements.skip("INCLUDED-MODE-DECLARATION-GROUP-SETS")
        child_elements.skip("INSTANTIATION-DATA-DEF-PROPSS")
        child_elements.skip("PER-INSTANCE-MEMORYS")
        child_elements.skip("PER-INSTANCE-PARAMETERS")
        child_elements.skip("PORT-API-OPTIONS")
        xml_child = child_elements.get("PORT-API-OPTIONS")
        if xml_child is not None:
            port_api_options = []
            for xml_grand_child in xml_child.findall("./PORT-API-OPTION"):
                port_api_options.append(self._read_port_api_option(xml_grand_child))
            data["port_api_options"] = port_api_options
        xml_child = child_elements.get("RUNNABLES")
        if xml_child is not None:
            runnables = []
            for xml_grand_child in xml_child.findall("./RUNNABLE-ENTITY"):
                runnables.append(self._read_runnable_entity(xml_grand_child))
            data["runnables"] = runnables
        child_elements.skip("SERVICE-DEPENDENCYS")
        child_elements.skip("SHARED-PARAMETERS")
        child_elements.skip("SUPPORTS-MULTIPLE-INSTANTIATION")
        child_elements.skip("VARIATION-POINT-PROXYS")
        child_elements.skip("VARIATION-POINT")

    def _read_rte_event_element(self, xml_element: ElementTree.Element) -> RteEventElement:
        """
        Reads one RTE event element
        """
        read_method = self.switcher_rte_event.get(xml_element.tag, None)
        if read_method is not None:
            return read_method(xml_element)
        else:
            raise KeyError(f"Found no reader for '{xml_element.tag}'")
