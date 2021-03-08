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
    package = ws.createPackage('ModeDclrGroups', role = 'ModeDclrGroup')
    package = ws.createPackage('Constants', role='Constant')
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    package = ws.createPackage('PortInterfaces', role="PortInterface")


def _create_base_types(ws):
    basetypes = ws.find('/DataTypes/BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    basetypes.createSwBaseType('float32', 32, encoding='IEEE754')

def _create_implementation_types(ws):
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')


def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)
    _create_implementation_types(ws)

class ARXML4ModeTest(ARXMLTestClass):


    def test_create_simple_mode_decl_group(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ModeDclrGroups')
        package.createModeDeclarationGroup('BswM_Mode', ["POSTRUN",
                                                         "RUN",
                                                         "SHUTDOWN",
                                                         "STARTUP",
                                                         "WAKEUP"], "STARTUP")

        file_name = 'ar4_simple_mode_decl_group.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'mode', file_name)

        self.save_and_check(ws, expected_file, generated_file, ['/ModeDclrGroups'])
        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        modeGroup = ws2.find('/ModeDclrGroups/BswM_Mode')
        self.assertIsInstance(modeGroup, autosar.mode.ModeDeclarationGroup)
        self.assertEqual(modeGroup.name, "BswM_Mode")


    def test_create_mode_type_mapping(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        modeDeclarationPackage = ws.find('/ModeDclrGroups')
        dataTypePackage = ws.find('/DataTypes')
        BswM_ESH_Mode_Group = modeDeclarationPackage.createModeDeclarationGroup('BswM_ESH_Mode', ["POSTRUN",
                                                         "RUN",
                                                         "SHUTDOWN",
                                                         "STARTUP",
                                                         "WAKEUP"], "STARTUP")

        BswM_ESH_Mode_Type = dataTypePackage.createImplementationDataTypeRef('BswM_ESH_Mode', '/DataTypes/uint8',
                    valueTable = ['STARTUP', 'RUN', 'POSTRUN', 'WAKEUP', 'SHUTDOWN'])
        mappingSet1 = modeDeclarationPackage.createDataTypeMappingSet('BswMMappingSet')
        mapping1 = mappingSet1.createModeRequestMapping(BswM_ESH_Mode_Group.ref, BswM_ESH_Mode_Type.ref)
        file_name = 'ar4_mode_request_mapping.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'mode', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ModeDclrGroups'])
        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        mappingSet2 = ws2.find('/ModeDclrGroups/BswMMappingSet')
        self.assertIsInstance(mappingSet2, autosar.datatype.DataTypeMappingSet)
        self.assertEqual(mappingSet2.findMappedModeRequestRef(mapping1.modeDeclarationGroupRef), mapping1.implementationDataTypeRef)

    def test_create_mode_declaration_with_assigned_values(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        modeDeclarationPackage = ws.find('/ModeDclrGroups')
        elem1 = modeDeclarationPackage.createModeDeclarationGroup('BswM_ESH_Mode', [
            (0, "STARTUP"),
            (1, "RUN"),
            (2, "POSTRUN"),
            (3, "WAKEUP"),
            (4, "SHUTDOWN")], "STARTUP")

        file_name = 'ar4_mode_declaration_with_assigned_values.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'mode', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ModeDclrGroups'])
        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        elem2 = ws2.find(elem1.ref)
        self.assertIsInstance(elem2, autosar.mode.ModeDeclarationGroup)
        self.assertEquals(elem2.modeDeclarations[0].value, 0)
        self.assertEquals(elem2.modeDeclarations[0].name, "STARTUP")
        self.assertEquals(elem2.modeDeclarations[1].value, 1)
        self.assertEquals(elem2.modeDeclarations[1].name, "RUN")
        self.assertEquals(elem2.modeDeclarations[2].value, 2)
        self.assertEquals(elem2.modeDeclarations[2].name, "POSTRUN")
        self.assertEquals(elem2.modeDeclarations[3].value, 3)
        self.assertEquals(elem2.modeDeclarations[3].name, "WAKEUP")
        self.assertEquals(elem2.modeDeclarations[4].value, 4)
        self.assertEquals(elem2.modeDeclarations[4].name, "SHUTDOWN")



if __name__ == '__main__':
    unittest.main()