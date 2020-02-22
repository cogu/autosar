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
    ws.createPackage('Constants', role='Constant')
    ws.createPackage('ComponentTypes', role='ComponentType')
    ws.createPackage('PortInterfaces', role="PortInterface")
    ws.createPackage('ModeDclrGroups', role="ModeDclrGroup")

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

def _create_test_elements(ws):
    package = ws.find('/Constants')
    package.createConstant('VehicleSpeed_IV', 'uint16', 65535)
    package.createConstant('EngineSpeed_IV', 'uint16', 65535)
    package = ws.find('ModeDclrGroups')
    package.createModeDeclarationGroup('VehicleMode', ["OFF",
                                                       "ACCESSORY",
                                                       "RUN",
                                                       "CRANK"], "OFF")

    package = ws.find('/PortInterfaces')
    package.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed', 'uint16'))
    package.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed', 'uint16'))
    portInterface=package.createClientServerInterface('FreeRunningTimer5ms_I', ['GetTime', 'IsTimerElapsed'])
    portInterface['GetTime'].createOutArgument('value', '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("startTime", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createInArgument("duration", '/DataTypes/uint32')
    portInterface["IsTimerElapsed"].createOutArgument("result", '/DataTypes/boolean')
    package.createModeSwitchInterface('VehicleMode_I', autosar.mode.ModeGroup('mode', '/ModeDclrGroups/VehicleMode'))

def _init_ws(ws):
    _create_packages(ws)
    _create_base_types(ws)
    _create_test_elements(ws)

class ARXML4PortCreateTest(ARXMLTestClass):

    def test_create_non_queued_receiver_port_single_data_element_direct_comspec1(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc1 = package.createApplicationSoftwareComponent('MyApplication')
        swc1.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', comspec = {'dataElement': 'VehicleSpeed', 'initValueRef': 'VehicleSpeed_IV'})
        swc1.behavior.createPortAPIOptionDefaults()
        file_name = 'ar4_non_queued_receiver_port_single_data_element_direct_comspec1.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'port', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_non_queued_receiver_port_single_data_element_direct_comspec2(self):
        """
        Same as previous test but does not explicitly name the dataElement (should auto-resolve name)
        """
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc1 = package.createApplicationSoftwareComponent('MyApplication')
        swc1.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', comspec = {'initValueRef': 'VehicleSpeed_IV'})
        swc1.behavior.createPortAPIOptionDefaults()
        file_name = 'ar4_non_queued_receiver_port_single_data_element_direct_comspec2.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'port', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_non_queued_receiver_port_single_data_element(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc1 = package.createApplicationSoftwareComponent('MyApplication')
        swc1.createRequirePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        swc1.behavior.createPortAPIOptionDefaults()
        file_name = 'ar4_non_queued_receiver_port_single_data_element.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'port', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_mode_require_port(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc1 = package.createApplicationSoftwareComponent('MyApplication')
        port1 = swc1.createRequirePort('VehicleMode', 'VehicleMode_I')
        swc1.behavior.createPortAPIOptionDefaults()
        self.assertEqual(port1.portInterfaceRef, '/PortInterfaces/VehicleMode_I')
        comspec1 = port1.comspec[0]
        comspec1.modeGroupRef = '/PortInterfaces/VehicleMode_I/mode'
        file_name = 'ar4_mode_require_port.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'port', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_mode_provide_port(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc1 = package.createApplicationSoftwareComponent('MyApplication')
        port1 = swc1.createProvidePort('VehicleMode', 'VehicleMode_I', modeGroup="mode", queueLength=1, modeSwitchAckTimeout=10)
        swc1.behavior.createPortAPIOptionDefaults()
        self.assertEqual(port1.portInterfaceRef, '/PortInterfaces/VehicleMode_I')
        file_name = 'ar4_mode_provide_port.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'port', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)
        port2 = ws2.find(port1.ref)
        self.assertIsInstance(port2, autosar.port.ProvidePort)
        comspec2 = port2.comspec[0]
        self.assertIsInstance(comspec2, autosar.port.ModeSwitchComSpec)
        self.assertEqual(comspec2.queueLength, 1)
        self.assertEqual(comspec2.modeSwitchAckTimeout, 10)

    def test_create_non_queued_sender_port_single_data_element(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/ComponentTypes')
        swc1 = package.createApplicationSoftwareComponent('MyApplication')
        swc1.createProvidePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef = 'VehicleSpeed_IV')
        swc1.behavior.createPortAPIOptionDefaults()
        file_name = 'ar4_non_queued_sender_port_single_data_element.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'port', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])
        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

if __name__ == '__main__':
    unittest.main()


