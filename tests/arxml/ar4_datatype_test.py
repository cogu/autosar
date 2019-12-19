import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest

def _create_packages(ws):

    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')

def _create_base_types(ws):
    basetypes = ws.find('/DataTypes/BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    basetypes.createSwBaseType('float32', 32, encoding='IEEE754')
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

class ARXML4DataTypeTest(ARXMLTestClass):

    def test_int_to_phys_rational_compu_method(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        compuMethod = package.createCompuMethodRational('VehicleSpeed_T', 0, 1/64, 0, 65535, unit = 'KmPerHour', defaultValue = 65535, forceFloat = True)
        self.assertIsInstance(compuMethod, autosar.datatype.CompuMethod)
        self.assertEqual(compuMethod.unitRef, '/DataTypes/Units/KmPerHour')
        self.assertIsInstance(ws.find(compuMethod.unitRef), autosar.datatype.Unit)
        self.assertIsInstance(compuMethod.intToPhys, autosar.datatype.Computation)
        self.assertIsNone(compuMethod.physToInt)
        self.assertAlmostEqual(float(1/64), compuMethod.intToPhys.elements[0].numerator, places=6)
        self.assertEqual(1, compuMethod.intToPhys.elements[0].denominator)
        file_name = 'ar4_int_to_phys_rational_compu_method.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        compu2 = ws2.find('/DataTypes/CompuMethods/VehicleSpeed_T')
        self.assertIsInstance(compu2, autosar.datatype.CompuMethod)
        self.assertEqual(compu2.name, 'VehicleSpeed_T')
        self.assertEqual(compu2.unitRef, '/DataTypes/Units/KmPerHour')
        compuScale = compu2.intToPhys.elements[0]
        self.assertEqual(compu2.intToPhys.defaultValue, 65535)
        self.assertEqual(compuScale.lowerLimit, 0)
        self.assertEqual(compuScale.upperLimit, 65535)
        self.assertEqual(compuScale.offset, 0)
        self.assertAlmostEqual(compuScale.numerator, float(1/64), places=6)
        self.assertEqual(compuScale.denominator, 1)

    def test_create_phys_to_int_compu_method_rational(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        compuMethod = package.createCompuMethodRationalPhys('SensorToRaw_T', 0, 256, 0, 65535, unit = 'Raw', defaultValue = 65535, forceFloat = True)
        self.assertIsInstance(compuMethod, autosar.datatype.CompuMethod)
        self.assertEqual(compuMethod.unitRef, '/DataTypes/Units/Raw')
        self.assertIsInstance(ws.find(compuMethod.unitRef), autosar.datatype.Unit)
        self.assertIsInstance(compuMethod.physToInt, autosar.datatype.Computation)
        self.assertIsNone(compuMethod.intToPhys)
        self.assertEqual(compuMethod.physToInt.elements[0].numerator, 256)
        self.assertEqual(1, compuMethod.physToInt.elements[0].denominator)
        file_name = 'ar4_phys_to_int_rational_compu_method.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        compu2 = ws2.find('/DataTypes/CompuMethods/SensorToRaw_T')
        self.assertIsInstance(compu2, autosar.datatype.CompuMethod)
        self.assertEqual(compu2.name, 'SensorToRaw_T')
        self.assertEqual(compu2.unitRef, '/DataTypes/Units/Raw')
        compuScale = compu2.physToInt.elements[0]
        self.assertEqual(compu2.physToInt.defaultValue, 65535)
        self.assertEqual(compuScale.lowerLimit, 0)
        self.assertEqual(compuScale.upperLimit, 65535)
        self.assertEqual(compuScale.offset, 0)
        self.assertEqual(compuScale.numerator, 256)
        self.assertEqual(compuScale.denominator, 1)

    def test_create_boolean_compu_method(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        basetypes=package.createSubPackage('BaseTypes')
        basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
        compuMethod = package.createCompuMethodConst('boolean', ['FALSE', 'TRUE'])
        self.assertEqual(compuMethod.ref, '/DataTypes/CompuMethods/boolean')
        self.assertIsNone(compuMethod.intToPhys.defaultValue)
        compuScales = compuMethod.intToPhys.elements
        self.assertEqual(compuScales[0].lowerLimit, 0)
        self.assertEqual(compuScales[0].upperLimit, 0)
        self.assertEqual(compuScales[0].textValue, 'FALSE')
        self.assertEqual(compuScales[1].lowerLimit, 1)
        self.assertEqual(compuScales[1].upperLimit, 1)
        self.assertEqual(compuScales[1].textValue, 'TRUE')
        #test helper propterties
        self.assertEqual(compuMethod.intToPhys.lowerLimit, 0)
        self.assertEqual(compuMethod.intToPhys.upperLimit, 1)
        file_name = 'ar4_boolean_compu_method.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        compu2 = ws2.find(compuMethod.ref)
        self.assertIsInstance(compu2, autosar.datatype.CompuMethod)
        compuScales2 = compuMethod.intToPhys.elements
        self.assertEqual(compuScales2[0].lowerLimit, compuScales[0].lowerLimit)
        self.assertEqual(compuScales2[0].upperLimit, compuScales[0].upperLimit)
        self.assertEqual(compuScales2[0].textValue, compuScales[0].textValue)
        self.assertEqual(compuScales2[1].lowerLimit, compuScales[1].lowerLimit)
        self.assertEqual(compuScales2[1].upperLimit, compuScales[1].upperLimit)
        self.assertEqual(compuScales2[1].textValue, compuScales[1].textValue)

    def test_create_unit(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        unit1 = package.createUnit('deg')
        self.assertIsInstance(unit1, autosar.datatype.Unit)
        self.assertEqual('/DataTypes/Units/deg', unit1.ref)
        file_name = 'ar4_unit.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        unit2 = ws2.find(unit1.ref)
        self.assertIsInstance(unit2, autosar.datatype.Unit)
        self.assertEqual(unit2.displayName, unit1.displayName)

    def test_create_linear_compu_method(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        unit_deg = package.createUnit('deg')
        compuMethod1 = package.createCompuMethodLinear('Pitch_T', lowerLimit=0, upperLimit = 20340, offset = -90, scaling = 1/128, unit = 'deg', forceFloat=False)
        self.assertIsInstance(compuMethod1, autosar.datatype.CompuMethod)
        self.assertEqual('/DataTypes/CompuMethods/Pitch_T', compuMethod1.ref)
        self.assertIsInstance(compuMethod1.intToPhys, autosar.datatype.Computation)
        self.assertIsNone(compuMethod1.physToInt)
        self.assertEqual(-90, compuMethod1.intToPhys.elements[0].offset)
        self.assertEqual(1, compuMethod1.intToPhys.elements[0].numerator)
        self.assertEqual(128, compuMethod1.intToPhys.elements[0].denominator)
        self.assertEqual(0, compuMethod1.intToPhys.elements[0].lowerLimit)
        self.assertEqual(20340, compuMethod1.intToPhys.elements[0].upperLimit)

        file_name = 'ar4_linear_compu_method.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)

        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        compuMethod2 = ws.find(compuMethod1.ref)
        self.assertIsInstance(compuMethod2, autosar.datatype.CompuMethod)
        self.assertIsInstance(compuMethod2.intToPhys, autosar.datatype.Computation)
        self.assertIsNone(compuMethod2.physToInt)
        self.assertEqual(compuMethod2.intToPhys.elements[0].offset, compuMethod1.intToPhys.elements[0].offset)
        self.assertEqual(compuMethod2.intToPhys.elements[0].numerator, compuMethod1.intToPhys.elements[0].numerator)
        self.assertEqual(compuMethod2.intToPhys.elements[0].denominator, compuMethod1.intToPhys.elements[0].denominator)
        self.assertEqual(compuMethod2.intToPhys.elements[0].lowerLimit, compuMethod1.intToPhys.elements[0].lowerLimit)
        self.assertEqual(compuMethod2.intToPhys.elements[0].upperLimit, compuMethod1.intToPhys.elements[0].upperLimit)

    def test_create_internal_constraint(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        constr = package.createInternalDataConstraint('VehicleSpeed_DataConstr', 0, 65535)
        self.assertIsInstance(constr, autosar.datatype.DataConstraint)
        self.assertIsInstance(constr.rules[0], autosar.datatype.InternalConstraint)
        self.assertEqual(constr.ref, '/DataTypes/DataConstrs/VehicleSpeed_DataConstr')
        self.assertEqual(constr.lowerLimit, 0)
        self.assertEqual(constr.upperLimit, 65535)
        file_name = 'ar4_internal_constraint.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        constr2 = ws2.find(constr.ref)
        self.assertIsInstance(constr2, autosar.datatype.DataConstraint)
        self.assertIsInstance(constr2.rules[0], autosar.datatype.InternalConstraint)
        self.assertEqual(constr2.lowerLimit, constr.lowerLimit)
        self.assertEqual(constr2.upperLimit, constr.upperLimit)

    def test_create_physical_constraint(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        constr = package.createPhysicalDataConstraint('VehicleSpeedPhys_DataConstr', 0, 65535)
        self.assertIsInstance(constr, autosar.datatype.DataConstraint)
        self.assertIsInstance(constr.rules[0], autosar.datatype.PhysicalConstraint)
        self.assertEqual(constr.ref, '/DataTypes/DataConstrs/VehicleSpeedPhys_DataConstr')
        self.assertEqual(constr.lowerLimit, 0)
        self.assertEqual(constr.upperLimit, 65535)
        file_name = 'ar4_phys_constraint.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        constr2 = ws2.find(constr.ref)
        self.assertIsInstance(constr2, autosar.datatype.DataConstraint)
        self.assertIsInstance(constr2.rules[0], autosar.datatype.PhysicalConstraint)
        self.assertEqual(constr2.lowerLimit, constr.lowerLimit)
        self.assertEqual(constr2.upperLimit, constr.upperLimit)

    def test_create_boolean_implementation_datatype(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        basetypes=package.find('BaseTypes')
        basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
        dt1 = package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        self.assertEqual(dt1.ref, '/DataTypes/boolean')
        constr = ws.find(dt1.dataConstraintRef)
        self.assertIsInstance(constr, autosar.datatype.DataConstraint)
        self.assertIsInstance(constr.rules[0], autosar.datatype.InternalConstraint)
        self.assertEqual(constr.lowerLimit, 0)
        self.assertEqual(constr.upperLimit, 1)
        file_name = 'ar4_boolean_implementation_datatype.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)

    def test_create_integer_implementation_types(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws.find('/DataTypes')
        basetypes=package.find('BaseTypes')
        basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
        basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
        basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
        uint8_dt1 = package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
        uint16_dt1 = package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
        uint32_dt1 = package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

        self.assertIsInstance(uint8_dt1, autosar.datatype.ImplementationDataType)
        self.assertIsInstance(uint16_dt1, autosar.datatype.ImplementationDataType)
        self.assertIsInstance(uint32_dt1, autosar.datatype.ImplementationDataType)
        self.assertEqual(uint8_dt1.ref, '/DataTypes/uint8')
        self.assertEqual(uint16_dt1.ref, '/DataTypes/uint16')
        self.assertEqual(uint32_dt1.ref, '/DataTypes/uint32')
        self.assertEqual(uint8_dt1.baseTypeRef, '/DataTypes/BaseTypes/uint8')
        self.assertEqual(uint16_dt1.baseTypeRef, '/DataTypes/BaseTypes/uint16')
        self.assertEqual(uint32_dt1.baseTypeRef, '/DataTypes/BaseTypes/uint32')
        file_name = 'ar4_integer_implementation_datatypes.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        uint8_dt2 = ws2.find(uint8_dt1.ref)
        uint16_dt2 = ws2.find(uint16_dt1.ref)
        uint32_dt2 = ws2.find(uint32_dt1.ref)
        self.assertIsInstance(uint8_dt2, autosar.datatype.ImplementationDataType)
        self.assertIsInstance(uint16_dt2, autosar.datatype.ImplementationDataType)
        self.assertIsInstance(uint32_dt2, autosar.datatype.ImplementationDataType)
        self.assertEqual(uint8_dt2.baseTypeRef, uint8_dt1.baseTypeRef)
        self.assertEqual(uint16_dt2.baseTypeRef, uint16_dt1.baseTypeRef)
        self.assertEqual(uint32_dt2.baseTypeRef, uint32_dt1.baseTypeRef)

    def test_create_implementation_array_datatype(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws['DataTypes']
        dt1 = package.createImplementationArrayDataType('u8Array2_T', '/DataTypes/uint8', 2)
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        self.assertEqual(dt1.ref, '/DataTypes/u8Array2_T')

        file_name = 'ar4_array_implementation_datatype.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)

    def test_create_implementation_ref_type(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        dt1 = package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        self.assertEqual(dt1.ref, '/DataTypes/U32Type_T')
        file_name = 'ar4_implementation_type_ref1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)

    def test_create_implementation_ref_type_implicit_constraint(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        dt1 = package.createImplementationDataTypeRef('VehicleSpeed_T',
                                                '/DataTypes/uint16',
                                                offset = 0,
                                                scaling = 1/256,
                                                unit="KmPerHour",
                                                forceFloat=True)
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        self.assertEqual(dt1.ref, '/DataTypes/VehicleSpeed_T')
        constraint1 = ws.find(dt1.dataConstraintRef)
        self.assertEqual(constraint1.name, 'VehicleSpeed_T_DataConstr')
        self.assertEqual(constraint1.lowerLimit, 0)
        self.assertEqual(constraint1.upperLimit, 65535)
        file_name = 'ar4_implementation_type_ref2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'], force = True)

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)

    def test_create_u8_application_data_type(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes/DataConstrs']
        constraint = package.createPhysicalDataConstraint('UINT8_ADT_DataConstr', 0, 255)
        package = ws['DataTypes']
        dt = package.createApplicationPrimitiveDataType('UINT8_ADT', dataConstraint = constraint.ref, swCalibrationAccess = 'READ-ONLY', category = 'VALUE')
        self.assertIsInstance(dt, autosar.datatype.ApplicationPrimitiveDataType)
        self.assertEqual('/DataTypes/UINT8_ADT', dt.ref)
        file_name = 'ar4_u8_adt.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find('/DataTypes/UINT8_ADT')
        self.assertIsInstance(dt2, autosar.datatype.ApplicationPrimitiveDataType)

    def test_create_adt_with_auto_constraint(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createUnit('deg')
        package.createCompuMethodLinear('Pitch_T', lowerLimit=0, upperLimit = 20340, offset = -90, scaling = 1/128, unit = 'deg')
        dt1 = package.createApplicationPrimitiveDataType('Pitch_ADT', compuMethod='Pitch_T', unit = 'deg')
        self.assertIsInstance(dt1, autosar.datatype.ApplicationPrimitiveDataType)
        self.assertEqual(dt1.ref, '/DataTypes/Pitch_ADT')
        self.assertEqual(dt1.unitRef, '/DataTypes/Units/deg')
        self.assertEqual(dt1.compuMethodRef, '/DataTypes/CompuMethods/Pitch_T')
        self.assertEqual(dt1.dataConstraintRef, '/DataTypes/DataConstrs/Pitch_ADT_DataConstr')

        file_name = 'ar4_adt_with_auto_constraint.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ApplicationPrimitiveDataType)

    def test_create_adt_with_data_constraint_and_compu_method(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createUnit('deg')
        compuMethod = package.createCompuMethodLinear('Pitch_T', lowerLimit=0, upperLimit = 20340, offset = -90, scaling = 1/128, unit = 'deg')
        dataConstraint = package.createInternalDataConstraint('Pitch_T_DataConstr', lowerLimit = compuMethod.intToPhys.lowerLimit, upperLimit = compuMethod.intToPhys.upperLimit)
        dt1 = package.createApplicationPrimitiveDataType('Pitch_ADT', compuMethod = compuMethod.ref, dataConstraint = dataConstraint.ref, unit = 'deg')
        self.assertIsInstance(dt1, autosar.datatype.ApplicationPrimitiveDataType)
        self.assertEqual(dt1.ref, '/DataTypes/Pitch_ADT')
        self.assertEqual(dt1.unitRef, '/DataTypes/Units/deg')
        self.assertEqual(dt1.compuMethodRef, '/DataTypes/CompuMethods/Pitch_T')
        self.assertEqual(dt1.dataConstraintRef, '/DataTypes/DataConstrs/Pitch_T_DataConstr')

        file_name = 'ar4_adt_with_data_constraint_and_compu_method.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ApplicationPrimitiveDataType)

    def test_create_u8_application_array_data_type(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes/DataConstrs']
        constraint = package.createPhysicalDataConstraint('UINT8_ADT_DataConstr', 0, 255)
        package = ws['DataTypes']
        adt_elem = package.createApplicationPrimitiveDataType('UINT8_ADT', dataConstraint = constraint.ref, swCalibrationAccess = 'READ-ONLY', category = 'VALUE')
        array_elem = autosar.datatype.ApplicationArrayElement(
            name = 'Data2ByteType_ADTElement',
            category = 'VALUE',
            typeRef = adt_elem.ref,
            arraySize = 2
            )
        array_dt = package.createApplicationArrayDataType(
            'Data2ByteType_ADT',
            array_elem,
            category = 'ARRAY',
            swCalibrationAccess = 'READ-ONLY')
        self.assertEqual('/DataTypes/Data2ByteType_ADT', array_dt.ref)
        file_name = 'ar4_u8_array_adt.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        array_dt2 = ws2.find('/DataTypes/Data2ByteType_ADT')
        self.assertIsInstance(array_dt2, autosar.datatype.ApplicationArrayDataType)

    def test_create_implentation_record_type1(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        dt1 = package.createImplementationRecordDataType('RecordType1_T', [('Elem1', '/DataTypes/uint8'), ('Elem2', '/DataTypes/U32Type_T')] )
        self.assertEqual(dt1.ref, '/DataTypes/RecordType1_T')
        file_name = 'ar4_implementation_record_type1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)


    def test_create_record_type2(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createImplementationDataTypeRef('U32Type_T', '/DataTypes/uint32')
        package.createImplementationArrayDataType('UserName_T', '/DataTypes/uint8', 32)
        dt1 = package.createImplementationRecordDataType('RecordType2_T', [('Elem1', '/DataTypes/U32Type_T'), ('Elem2', '/DataTypes/UserName_T')] )
        self.assertEqual(dt1.ref, '/DataTypes/RecordType2_T')

        file_name = 'ar4_implementation_record_type2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)


    def test_create_ref_type_with_valueTable(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        dt1 = package.createImplementationDataTypeRef('OffOn_T', '/DataTypes/uint8', valueTable=['OffOn_Off', 'OffOn_On', 'OffOn_Error', 'OffOn_NotAvailable'])
        self.assertEqual(dt1.ref, '/DataTypes/OffOn_T')

        file_name = 'ar4_impl_ref_type_vt.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)

    def test_custom_constraint_on_impl_typ(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        package.createInternalDataConstraint('CustomConstraintName', lowerLimit=0, upperLimit=100000)
        package.createImplementationDataTypeRef('U32RefCustom_T', '/DataTypes/uint32', dataConstraint='CustomConstraintName')
        file_name = 'ar4_impl_datatype_ref_custom_constraint.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])


    def test_create_application_record_adt(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        package = ws['DataTypes']
        package.createUnit('deg')
        package.createUnit('m')
        package.createUnit('kmPerHour')
        compu = package.createCompuMethodLinear('Pitch_T', lowerLimit=0, upperLimit = 20340, offset = -90, scaling = 1/128, unit = 'deg')
        constr = package.createInternalDataConstraint('Pitch_DataConstr', lowerLimit = compu.intToPhys.lowerLimit, upperLimit = compu.intToPhys.upperLimit)
        package.createApplicationPrimitiveDataType('Pitch_ADT', compuMethod = compu.ref, dataConstraint = constr.ref, unit = 'deg')
        compu = package.createCompuMethodLinear('Yaw_T', lowerLimit=0, upperLimit = 46080, offset = 0, scaling = 1/128, unit = 'deg')
        constr = package.createInternalDataConstraint('Yaw_DataConstr', lowerLimit = compu.intToPhys.lowerLimit, upperLimit = compu.intToPhys.upperLimit)
        package.createApplicationPrimitiveDataType('Yaw_ADT', compuMethod = compu.ref, dataConstraint = constr.ref, unit = 'deg')
        compu = package.createCompuMethodLinear('Altitude_T', lowerLimit=0, upperLimit = 65535, offset = -2500, scaling = 1/8, unit = 'm')
        constr = package.createInternalDataConstraint('Altitude_DataConstr', lowerLimit = compu.intToPhys.lowerLimit, upperLimit = compu.intToPhys.upperLimit)
        package.createApplicationPrimitiveDataType('Altitude_ADT', compuMethod = compu.ref, dataConstraint = constr.ref, unit = 'm')
        compu = package.createCompuMethodLinear('VehicleSpeed_T', lowerLimit=0, upperLimit = 65535, offset = 0, scaling = 1/64, unit = 'kmPerHour')
        constr = package.createInternalDataConstraint('VehicleSpeed_DataConstr', lowerLimit = compu.intToPhys.lowerLimit, upperLimit = compu.intToPhys.upperLimit)
        package.createApplicationPrimitiveDataType('VehicleSpeed_ADT', compuMethod = compu.ref, dataConstraint = constr.ref, unit = 'kmPerHour')

        dt1 = package.createApplicationRecordDataType('Velocity_ADT',
                                                      [
                                                        ('Bearing', '/DataTypes/Yaw_ADT'),
                                                        ('VehicleSpeed', '/DataTypes/VehicleSpeed_ADT'),
                                                        ('Pitch', '/DataTypes/Pitch_ADT'),
                                                        ('Altitude', '/DataTypes/Altitude_ADT'),
                                                      ])
        self.assertIsInstance(dt1, autosar.datatype.ApplicationRecordDataType)

        file_name = 'ar4_application_record_adt.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ApplicationRecordDataType)
        self.assertEqual(len(dt2.elements), 4)


    def test_create_ref_type_with_bitmask(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)
        package = ws['DataTypes']
        dt1 = package.createImplementationDataTypeRef('DataTypeWithBitMask_T', '/DataTypes/uint8', bitmask=[
            (1, 'MASK1'),
            (2, 'MASK2'),
            (4, 'MASK4'),
            (8, 'MASK8'),
            (16, 'MASK16'),
            (32, 'MASK32'),
            (64, 'MASK64'),
            (128, 'MASK128'),
            ])
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        compu1 = ws.find(dt1.compuMethodRef)
        self.assertIsInstance(compu1, autosar.datatype.CompuMethod)
        file_name = 'ar4_ref_type_bitmask.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)
        compu2 = ws2.find(dt2.compuMethodRef)
        self.assertIsInstance(compu2, autosar.datatype.CompuMethod)
        self.assertEqual(compu2.intToPhys.elements[0].mask, 1)
        self.assertEqual(compu2.intToPhys.elements[1].mask, 2)
        self.assertEqual(compu2.intToPhys.elements[2].mask, 4)
        self.assertEqual(compu2.intToPhys.elements[3].mask, 8)
        self.assertEqual(compu2.intToPhys.elements[4].mask, 16)
        self.assertEqual(compu2.intToPhys.elements[5].mask, 32)
        self.assertEqual(compu2.intToPhys.elements[6].mask, 64)
        self.assertEqual(compu2.intToPhys.elements[7].mask, 128)

    def test_create_float_value_type(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        dt1 = package.createImplementationDataType('float32', '/DataTypes/BaseTypes/float32', '-INF', 'INF', lowerLimitType = 'OPEN', upperLimitType = 'OPEN')
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        dc1 = ws.find(dt1.dataConstraintRef)
        self.assertIsInstance(dc1, autosar.datatype.DataConstraint)
        file_name = 'ar4_float_value_type.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)


    def test_create_float_value_type_with_type_emitter(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        dt1 = package.createImplementationDataType('float32', '/DataTypes/BaseTypes/float32', '-INF', 'INF', typeEmitter='PlatformType', lowerLimitType = 'OPEN', upperLimitType = 'OPEN')
        self.assertIsInstance(dt1, autosar.datatype.ImplementationDataType)
        dc1 = ws.find(dt1.dataConstraintRef)
        self.assertIsInstance(dc1, autosar.datatype.DataConstraint)

        file_name = 'ar4_float_value_type_with_type_emitter.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

    def test_create_implementation_data_type_with_symbol_props(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        package = ws['DataTypes']
        dt1 = package.createImplementationDataType('RTCTime_T', '/DataTypes/BaseTypes/uint32', lowerLimit = 0, upperLimit = 0xFFFFFFFF, typeEmitter='RTE')
        dt1.setSymbolProps('TimeStamp', 'TimeStampSym')
        self.assertEqual(dt1.symbolProps.name, 'TimeStamp')
        self.assertEqual(dt1.symbolProps.symbol, 'TimeStampSym')

        file_name = 'ar4_implementation_data_type_with_symbol_props.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertIsInstance(dt2, autosar.datatype.ImplementationDataType)
        self.assertIsInstance(dt2.symbolProps, autosar.base.SymbolProps)
        self.assertEqual(dt2.symbolProps.name, dt1.symbolProps.name)
        self.assertEqual(dt2.symbolProps.symbol, dt1.symbolProps.symbol)

    def test_auto_create_constraint(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        datatypes = ws['DataTypes']
        dt1 = datatypes.createImplementationDataTypeRef('Seconds_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=63)
        file_name = 'ar4_auto_create_constraint.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)

    def test_auto_create_compumethod_and_unit(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        _create_base_types(ws)

        datatypes = ws['DataTypes']
        dt1 = datatypes.createImplementationDataTypeRef('VehicleSpeed_T',
                                                    implementationTypeRef = '/DataTypes/uint16',
                                                    lowerLimit = 0,
                                                    upperLimit = 65535,
                                                    offset = 0,
                                                    scaling = 1/64,
                                                    unit = 'KmPerHour')
        file_name = 'ar4_auto_create_compumethod_and_unit.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertEqual(dt1.name, dt2.name)

    def test_create_base_type_without_size(self):
        ws = autosar.workspace(version="4.2.2")
        _create_packages(ws)
        base_types = ws.find('DataTypes/BaseTypes')
        self.assertIsNotNone(base_types)

        dt1 = base_types.createSwBaseType('uint8')
        self.assertIsNone(dt1.size)
        file_name = 'ar4_create_base_type_without_size.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'datatype', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/DataTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        dt2 = ws2.find(dt1.ref)
        self.assertEqual(dt1.name, dt2.name)
        self.assertIsNone(dt2.size)

if __name__ == '__main__':
    unittest.main()