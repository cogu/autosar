# Changelog

The first name in a bullet point below is the Python class name while the second name is the identifier used in the XML schema (XSD file).

Elements marked as `collectable` means that they can be added directly to a package.
Non-collectable elements are various sub-elements to collectable elements.

## [Unreleased]

### Added

#### XML - Software component elements

* PModeGroupInAtomicSwcInstanceRef | P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF
* POperationInAtomicSwcInstanceRef | P-OPERATION-IN-ATOMIC-SWC-INSTANCE-REF
* PTriggerInAtomicSwcTypeInstanceRef | P-TRIGGER-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
* RModeInAtomicSwcInstanceRef | R-MODE-IN-ATOMIC-SWC-INSTANCE-REF
* RTriggerInAtomicSwcInstanceRef | R-TRIGGER-IN-ATOMIC-SWC-INSTANCE-REF
* RVariableInAtomicSwcInstanceRef | R-VARIABLE-IN-ATOMIC-SWC-INSTANCE-REF

#### XML - SWC internal behavior elements

* AsynchronousServerCallReturnsEvent | ASYNCHRONOUS-SERVER-CALL-RETURNS-EVENT
* BackgroundEvent | BACKGROUND-EVENT
* DataReceivedEvent | DATA-RECEIVED-EVENT
* DataReceiveErrorEvent | DATA-RECEIVE-ERROR-EVENT
* DataSendCompletedEvent | DATA-SEND-COMPLETED-EVENT
* DataWriteCompletedEvent | DATA-WRITE-COMPLETED-EVENT
* ExclusiveAreaRefConditional | EXCLUSIVE-AREA-REF-CONDITIONAL
* ExecutableEntityActivationReason | EXECUTABLE-ENTITY-ACTIVATION-REASON
* ExternalTriggerOccurredEvent | EXTERNAL-TRIGGER-OCCURRED-EVENT
* InitEvent | INIT-EVENT
* InternalTriggerOccurredEvent | INTERNAL-TRIGGER-OCCURRED-EVENT
* ModeSwitchedAckEvent | MODE-SWITCHED-ACK-EVENT
* OperationInvokedEvent | OPERATION-INVOKED-EVENT
* RunnableEntity | RUNNABLE-ENTITY
* SwcInternalBehavior | SWC-INTERNAL-BEHAVIOR (Partly implemented)
  * events
  * runnables
* SwcModeManagerErrorEvent | SWC-MODE-MANAGER-ERROR-EVENT
* SwcModeSwitchEvent | SWC-MODE-SWITCH-EVENT
* TimingEvent | TIMING-EVENT
* TransformerHardErrorEvent | TRANSFORMER-HARD-ERROR-EVENT

#### XML - Reference elements

* AbstractProvidedPortPrototypeRef
* AbstractRequiredPortPrototypeRef
* AsynchronousServerCallResultPointRef
* ExclusiveAreaNestingOrderRef
* ExclusiveAreaRef
* InternalTriggeringPointRef
* ModeSwitchPointRef
* RunnableEntityRef
* SwcImplementationRef
* SwcInternalBehaviorRef
* TriggerRef
* VariableAccessRef


### Fixed

* Fixed parsing error on elements containing `ADMIN-DATA`.

### Changed

* Reader class attempts to resume parsing at next element if an error occurs.
  * To stop parsing on first error, give the option `stop_on_error=True` to method `Reader.read_file`.

## [v0.5.3] - 2024-03-31

### Fixed

* Fixed bug in Reader class for property `QUEUED-RECEIVER-COM-SPEC/QUEUE-LENGTH`

### Added

#### XML - Common structure elements

* DataFilter | DATA-FILTER

#### XML - System template elements

* E2EProfileCompatibilityProps | E-2-E-PROFILE-COMPATIBILITY-PROPS | `collectable`
* EndToEndTransformationComSpecProps | END-TO-END-TRANSFORMATION-COM-SPEC-PROPS

#### XML - Software component elements

* ApplicationSoftwareComponentType | APPLICATION-SW-COMPONENT-TYPE | `collectable`
* CompositionSwComponentType | COMPOSITION-SW-COMPONENT-TYPE | `collectable`
* SwComponentPrototype | SW-COMPONENT-PROTOTYPE
* PortInCompositionTypeInstanceRef | Merge of P-PORT-IN-COMPOSITION-INSTANCE-REF, R-PORT-IN-COMPOSITION-INSTANCE-REF
* AssemblySwConnector | ASSEMBLY-SW-CONNECTOR
* DelegationSwConnector | DELEGATION-SW-CONNECTOR
* PassThroughSwConnector | PASS-THROUGH-SW-CONNECTOR
* ClientComSpec | CLIENT-COM-SPEC
* ModeSwitchedAckRequest | MODE-SWITCHED-ACK-REQUEST
* ModeSwitchReceiverComSpec | MODE-SWITCH-RECEIVER-COM-SPEC
* ModeSwitchSenderComSpec | MODE-SWITCH-SENDER-COM-SPEC
* NonqueuedReceiverComSpec | NONQUEUED-RECEIVER-COM-SPEC
* NonqueuedSenderComSpec | NONQUEUED-SENDER-COM-SPEC
* NvProvideComSpec | NV-PROVIDE-COM-SPEC
* NvRequireComSpec | NV-REQUIRE-COM-SPEC
* ParameterProvideComSpec | PARAMETER-PROVIDE-COM-SPEC
* ParameterRequireComSpec | PARAMETER-REQUIRE-COM-SPEC
* QueuedReceiverComSpec | QUEUED-RECEIVER-COM-SPEC
* QueuedSenderComSpec | QUEUED-SENDER-COM-SPEC
* ReceptionComSpecProps | RECEPTION-COM-SPEC-PROPS
* ServerComSpec | SERVER-COM-SPEC
* TransmissionAcknowledgementRequest | TRANSMISSION-ACKNOWLEDGEMENT-REQUEST
* TransmissionComSpecProps | TRANSMISSION-COM-SPEC-PROPS
* ProvidePortPrototype | P-PORT-PROTOTYPE
* RequirePortPrototype | R-PORT-PROTOTYPE
* PRPortPrototype | PR-PORT-PROTOTYPE

#### XML - SWC internal behavior elements

* ArVariableInImplementationDataInstanceRef | AR-VARIABLE-IN-IMPLEMENTATION-DATA-INSTANCE-REF
* AutosarVariableRef | AUTOSAR-VARIABLE-REF
* VariableAccess | VARIABLE-ACCESS
* VariableInAtomicSWCTypeInstanceRef | VARIABLE-IN-ATOMIC-SWC-TYPE-INSTANCE-REF
* SwcImplementation | SWC-IMPLEMENTATION

#### XML - Reference elements

* ApplicationCompositeElementDataPrototypeRef
* AutosarDataPrototypeRef
* ClientServerOperationRef
* E2EProfileCompatibilityPropsRef
* ModeDeclarationGroupPrototypeRef
* ParameterDataPrototypeRef
* PortPrototypeRef
* SwComponentTypeRef
* SwComponentPrototypeRef

#### Workspace class

New methods:

* create_package_map
* add_element
* find_element
* get_package
* create_document_mapping

### Changed

* The method `Workspace.make_packages` should not be called directly anymore. Use `Workspace.create_package_map` instead.

## [v0.5.2] - 2024-02-11

### Added

#### Workspace

* Various improvements to template classes
* Support project config files

#### XML - Data type elements

* ArgumentDataPrototype | ARGUMENT-DATA-PROTOTYPE
* ParameterDataPrototype | PARAMETER-DATA-PROTOTYPE
* VariableDataPrototype | VARIABLE-DATA-PROTOTYPE

#### XML -  Mode declaration elements

* ModeDeclarationGroup | MODE-DECLARATION-GROUP | `collectable`
* ModeDeclaration | MODE-DECLARATION
* ModeDeclarationGroupPrototype | MODE-DECLARATION-GROUP-PROTOTYPE
* ModeErrorBehavior | MODE-ERROR-BEHAVIOR
* ModeTransition | MODE-TRANSITION

#### XML Port interface elements

* ClientServerInterface | CLIENT-SERVER-INTERFACE | `collectable`
* ModeSwitchInterface | MODE-SWITCH-INTERFACE |  `collectable`
* NvDataInterface | NV-DATA-INTERFACE | `collectable`
* ParameterInterface | PARAMETER-INTERFACE | `collectable`
* SenderReceiverInterface | SENDER-RECEIVER-INTERFACE | `collectable`
* ApplicationError | APPLICATION-ERROR
* ClientServerOperation | CLIENT-SERVER-OPERATION
* InvalidationPolicy | INVALIDATION-POLICY

#### XML - Reference elements

* ApplicationErrorRef
* ModeDeclarationGroupRef
* ModeDeclarationRef
* VariableDataPrototypeRef

## [v0.5.1] - 2023-11-09

### Added

* Value checker for positive integers

#### XML - Data type elements

* ValueList | VALUE-LIST

#### XML - Calibration elements

* SwValueCont | SW-VALUE-CONT
* SwAxisCont | SW-AXIS-CONT
* SwValues | SW-VALUES
* ValueGroup | VALUE-GROUP

#### XML - Constant and Value specification elements

* ConstantSpecification | CONSTANT-SPECIFICATION | `collectable`
* ApplicationValueSpecification | APPLICATION-VALUE-SPECIFICATION
* ArrayValueSpecification | ARRAY-VALUE-SPECIFICATION
* ConstantReference | CONSTANT-REFERENCE
* NotAvailableValueSpecification | NOT-AVAILABLE-VALUE-SPECIFICATION
* NumericalValueSpecification | NUMERICAL-VALUE-SPECIFICATION
* RecordValueSpecification | RECORD-VALUE-SPECIFICATION
* TextValueSpecification | TEXT-VALUE-SPECIFICATION

#### XML - Reference elements

* ConstantRef (different class from ConstantReference)

## [v0.5.0] - 2023-10-27

### Added

#### XML - Documentation elements

* DocumentationBlock | DOCUMENTATION-BLOCK
* EmphasisText | EMPHASIS-TEXT
* MultilanguageLongName | MULTILANGUAGE-LONG-NAME
* MultiLanguageOverviewParagraph | MULTI-LANGUAGE-OVERVIEW-PARAGRAPH
* MultiLanguageParagraph | MULTI-LANGUAGE-PARAGRAPH
* MultiLanguageVerbatim | MULTI-LANGUAGE-VERBATIM
* Subscript | SUPSCRIPT (This not a typo)
* Superscript | SUPSCRIPT
* TechnicalTerm | TT

#### XML - Data type elements

* ApplicationArrayDataType | APPLICATION-ARRAY-DATA-TYPE | `collectable`
* ApplicationPrimitiveDataType |  APPLICATION-PRIMITIVE-DATA-TYPE |  `collectable`
* ApplicationRecordDataType |  APPLICATION-RECORD-DATA-TYPE |  `collectable`
* DataTypeMappingSet | DATA-TYPE-MAPPING-SET | `collectable`
* ImplementationDataType |  IMPLEMENTATION-DATA-TYPE |  `collectable`
* SwBaseType |  SW-BASE-TYPE |  `collectable`
* ApplicationArrayElement |  APPLICATION-ARRAY-ELEMENT
* ApplicationRecordElement |  APPLICATION-RECORD-ELEMENT
* AutosarDataType |  AUTOSAR-DATA-TYPE
* DataTypeMap |  DATA-TYPE-MAP
* ImplementationDataTypeElement |  IMPLEMENTATION-DATA-TYPE-ELEMENT
* SwBitRepresentation | SW-BIT-REPRESENTATION
* SwDataDefProps | SW-DATA-DEF-PROPS
* SwDataDefPropsConditional | SW-DATA-DEF-PROPS-CONDITIONAL + SW-DATA-DEF-PROPS-CONTENT
* SwPointerTargetProps | SW-POINTER-TARGET-PROPS
* SwTextProps | SW-TEXT-PROPS
* SymbolProps | SYMBOL-PROPS

#### XML - Unit elements

* Unit | UNIT | `collectable`

#### XML - Computation and constraint elements

* CompuMethod |  COMPU-METHOD |  `collectable`
* DataConstraint |  DATA-CONSTR |  `collectable`
* CompuConst |  COMPU-CONST
* CompuRational |  COMPU-RATIONAL-COEFFS
* CompuScale |  COMPU-SCALE
* Computation |  COMPU
* DataConstraintRule |  DATA-CONSTR-RULE
* InternalConstraint |  INTERNAL-CONSTRS
* PhysicalConstraint |  PHYS-CONSTRS
* ScaleConstraint |  SCALE-CONSTR

#### XML - Reference elements

These elements exist in Python only. They are returned as objects when calling
the `ref` method on various XML elements.

Only a handful of XML element classes have their corresponding `ref` method implemented (will be fixed later).

* ApplicationDataTypeRef
* AutosarDataTypeRef
* CompuMethodRef
* DataConstraintRef
* FunctionPtrSignatureRef
* ImplementationDataTypeRef
* IndexDataTypeRef
* PhysicalDimensionRef
* SwAddrMethodRef
* SwBaseTypeRef
* UnitRef

#### Implementation Model - Elements

* ArrayType
* BaseType
* PointerType
* RecordType
* RefType
* ScalarType

#### RTE Data Type Generator

* ArrayType
* BaseType
* RecordType
* RefType
* ScalarType
