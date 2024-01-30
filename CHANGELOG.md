# Changelog

The first name in a bullet point below is the Python class name while the second name is the identifier used in the XML schema (XSD file).

Elements marked as `collectable` means that they can be added directly to a package.
Non-collectable elements are various sub-elements to collectable elements.

## Unreleased

### Added

#### XML Port interface elements

* NvDataInterface | NV-DATA-INTERFACE | `collectable`
* ParameterInterface | PARAMETER-INTERFACE | `collectable`
* SenderReceiverInterface | SENDER-RECEIVER-INTERFACE | `collectable`
* InvalidationPolicy | INVALIDATION-POLICY

#### XML - Data type elements

* ParameterDataPrototype | PARAMETER-DATA-PROTOTYPE
* VariableDataPrototype | VARIABLE-DATA-PROTOTYPE

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
