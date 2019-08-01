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
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')

def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)

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
        
        
if __name__ == '__main__':
    unittest.main()