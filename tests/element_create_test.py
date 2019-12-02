import os, sys
mod_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, mod_path)
import autosar
import unittest

class TestRealTypeCreate(unittest.TestCase):

    def test_createRealType_AR3_by_explicit_minmax_types(self):
        ws = autosar.workspace(version="3.0.2")
        package = ws.createPackage('DataTypes')
        dataType=package.createRealDataType('Float', None, None, minValType='INFINITE', maxValType='INFINITE')
        self.assertIsInstance(dataType, autosar.datatype.RealDataType)
        self.assertEqual(dataType.minVal, None)
        self.assertEqual(dataType.minValType, 'INFINITE')
        self.assertEqual(dataType.maxVal, None)
        self.assertEqual(dataType.maxValType, 'INFINITE')
        self.assertEqual(dataType.encoding, 'SINGLE')

    def test_createRealType_AR3_with_infinite(self):
        ws = autosar.workspace(version="3.0.2")
        package = ws.createPackage('DataTypes')
        dataType = package.createRealDataType('Float', 'INFINITE', 'INFINITE')
        self.assertIsInstance(dataType, autosar.datatype.RealDataType)
        self.assertEqual(dataType.minVal, None)
        self.assertEqual(dataType.minValType, 'INFINITE')
        self.assertEqual(dataType.maxVal, None)
        self.assertEqual(dataType.maxValType, 'INFINITE')
        self.assertEqual(dataType.encoding, 'SINGLE')

    def test_createRealType_AR3_with_infinite_negative(self):
        ws = autosar.workspace(version="3.0.2")
        package = ws.createPackage('DataTypes')
        dataType = package.createRealDataType('Float', '-INFINITE', 'INFINITE')
        self.assertIsInstance(dataType, autosar.datatype.RealDataType)
        self.assertEqual(dataType.minVal, None)
        self.assertEqual(dataType.minValType, 'INFINITE')
        self.assertEqual(dataType.maxVal, None)
        self.assertEqual(dataType.maxValType, 'INFINITE')
        self.assertEqual(dataType.encoding, 'SINGLE')

    def test_createRealType_AR3_with_inf(self):
        ws = autosar.workspace(version="3.0.2")
        package = ws.createPackage('DataTypes')
        dataType = package.createRealDataType('Float', '-INF', 'INF')
        self.assertIsInstance(dataType, autosar.datatype.RealDataType)
        self.assertEqual(dataType.minVal, None)
        self.assertEqual(dataType.minValType, 'INFINITE')
        self.assertEqual(dataType.maxVal, None)
        self.assertEqual(dataType.maxValType, 'INFINITE')
        self.assertEqual(dataType.encoding, 'SINGLE')

    def test_createRealType_AR4_with_no_constraint_package_set(self):
        ws = autosar.workspace(version="4.2.2")
        basetypes = ws.createPackage('BaseTypes')
        float32_base = basetypes.createBaseType('float32', 32, 'IEEE754')
        package = ws.createPackage('DataTypes')
        with self.assertRaises(RuntimeError) as context:
            dataType = package.createImplementationDataType('float32', float32_base.ref, '-INFINITE', 'INFINITE', lowerLimitType = 'OPEN', upperLimitType = 'OPEN')

    def test_createFloat_AR4_type(self):
        ws = autosar.workspace(version="4.2.2")
        constraints = ws.createPackage('Contraints', role='DataConstraint')
        basetypes = ws.createPackage('BaseTypes')
        float32_base = basetypes.createBaseType('float32', 32, 'IEEE754')
        package = ws.createPackage('DataTypes')
        dataType = package.createImplementationDataType('float32', float32_base.ref, '-INF', 'INF', lowerLimitType = 'OPEN', upperLimitType = 'OPEN')
        self.assertIsInstance(dataType, autosar.datatype.ImplementationDataType)
        dataConstraint = ws.find(dataType.variantProps[0].dataConstraintRef)
        self.assertIsInstance(dataConstraint, autosar.datatype.DataConstraint)
        self.assertEqual(dataConstraint.lowerLimit, float('-inf'))
        self.assertEqual(dataConstraint.upperLimit, float('inf'))
        self.assertEqual(dataConstraint.lowerLimitType, 'OPEN')
        self.assertEqual(dataConstraint.upperLimitType, 'OPEN')


class TestParameterInterfaceCreate(unittest.TestCase):

    def test_createParameterInterface_AR4(self):
        ws = autosar.workspace(version="4.2.2")
        constraints = ws.createPackage('Contraints', role='DataConstraint')
        basetypes = ws.createPackage('BaseTypes')
        uint8_base = basetypes.createBaseType('uint8', 8, None)
        package = ws.createPackage('DataTypes')
        uint8_type = package.createImplementationDataType('uint8', uint8_base.ref, 0, 255)
        package = ws.createPackage('PortInterfaces')
        parameter = autosar.ParameterDataPrototype('v', uint8_type.ref)
        portinterface = package.createParameterInterface('ButtonDebounceTime_I', parameter)
        self.assertIsInstance(portinterface, autosar.portinterface.ParameterInterface)

if __name__ == '__main__':
    unittest.main()
