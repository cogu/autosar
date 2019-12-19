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
    ws.createPackage('ModeDclrGroups', role = 'ModeDclrGroup')
    ws.createPackage('Constants', role='Constant')
    ws.createPackage('ComponentTypes', role='ComponentType')
    ws.createPackage('PortInterfaces', role="PortInterface")


def _create_data_types(ws):
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
    package.createImplementationDataTypeRef('OffOn_T', implementationTypeRef = '/DataTypes/uint8',
                                            valueTable = ['OffOn_Off',
                                                          'OffOn_On',
                                                          'OffOn_Error',
                                                          'OffOn_NotAvailable'
                                                        ])
    package.createImplementationDataTypeRef('Seconds_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=63)
    package.createImplementationDataTypeRef('Minutes_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=63)
    package.createImplementationDataTypeRef('Hours_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=31)

def _create_mode_declarations(ws):
    package = ws.find('ModeDclrGroups')
    package.createModeDeclarationGroup('VehicleMode', ["OFF",
                                                       "ACCESSORY",
                                                        "RUNNING",
                                                        "CRANKING",
                                                    ], "OFF")


def _init_ws(ws):
    _create_packages(ws)
    _create_data_types(ws)
    _create_mode_declarations(ws)

class ARXML4PortInterfaceTest(ARXMLTestClass):

    def test_create_sender_receiver_interface_single_element(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        pif1 =  package.createSenderReceiverInterface('HeaterPwrStat_I', autosar.element.DataElement('HeaterPwrStat', 'OffOn_T'))
        self.assertEqual(pif1.dataElements[0].typeRef, '/DataTypes/OffOn_T')
        file_name = 'ar4_sender_receiver_interface_single_element.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)
        self.save_and_check(ws, expected_file, generated_file)
        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        pif2 = portInterface = ws2.find(pif1.ref)
        self.assertIsInstance(pif2, autosar.portinterface.SenderReceiverInterface)
        self.assertEqual(len(pif2.dataElements), 1)

    def test_create_sender_receiver_interface_multiple_elements(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        pif1 = package.createSenderReceiverInterface('SystemTime_I', [
            autosar.element.DataElement('Seconds', '/DataTypes/Seconds_T'),
            autosar.element.DataElement('Minutes', '/DataTypes/Minutes_T'),
            autosar.element.DataElement('Hours', '/DataTypes/Hours_T')
            ])
        file_name = 'ar4_sender_receiver_interface_multiple_elements_explicit.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)
        self.save_and_check(ws, expected_file, generated_file)
        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        pif2 = portInterface = ws2.find(pif1.ref)
        self.assertIsInstance(pif2, autosar.portinterface.SenderReceiverInterface)
        self.assertEqual(len(pif2.dataElements), 3)

    def test_create_client_server_interface_single_operation_no_return_no_service(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        pif1=package.createClientServerInterface('FreeRunningTimer_I', ['GetTimeStamp'] )
        pif1['GetTimeStamp'].createOutArgument('value', '/DataTypes/uint32')
        file_name = 'ar4_client_server_interface_single_operation_no_return_no_service.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)
        self.save_and_check(ws, expected_file, generated_file)
        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        pif2 = portInterface = ws2.find(pif1.ref)
        self.assertIsInstance(pif2, autosar.portinterface.ClientServerInterface)
        self.assertEqual(pif2.isService, False)
        self.assertEqual(len(pif2.operations), 1)
        operation = pif2['GetTimeStamp']
        self.assertIsInstance(operation, autosar.portinterface.Operation)

    def test_create_client_server_interface_single_operation_no_return_is_service(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        pif1=package.createClientServerInterface('FreeRunningTimer_I', ['GetTimeStamp'], isService=True )
        arg = pif1['GetTimeStamp'].createOutArgument('value', '/DataTypes/uint32', 'NOT-ACCESSIBLE', 'USE-ARGUMENT-TYPE')

        file_name = 'ar4_client_server_interface_single_operation_no_return_is_service.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)
        self.save_and_check(ws, expected_file, generated_file)

        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        pif2 = portInterface = ws2.find(pif1.ref)
        self.assertIsInstance(pif2, autosar.portinterface.ClientServerInterface)
        self.assertEqual(pif2.isService, True)
        self.assertEqual(len(pif2.operations), 1)
        operation = pif2['GetTimeStamp']
        self.assertIsInstance(operation, autosar.portinterface.Operation)

    def test_create_mode_switch_interface(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        pif1 = package.createModeSwitchInterface('VehicleMode_I', autosar.mode.ModeGroup('mode', 'VehicleMode'))
        self.assertEqual(pif1.modeGroup.typeRef, '/ModeDclrGroups/VehicleMode')

        file_name = 'ar4_create_mode_switch_interface.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)
        self.save_and_check(ws, expected_file, generated_file)

        ws2 = autosar.workspace(version="4.2.2")
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        pif2 = ws2.find(pif1.ref)
        self.assertIsInstance(pif2, autosar.portinterface.ModeSwitchInterface)
        self.assertEqual(pif1.modeGroup.name, pif2.modeGroup.name)
        self.assertEqual(pif1.modeGroup.typeRef, pif2.modeGroup.typeRef)

    def test_create_parameter_interface(self):
        ws = autosar.workspace(version="4.2.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        pif1 = package.createParameterInterface('CruiseControlEnable_I', autosar.element.ParameterDataPrototype('v', 'boolean'))

        file_name = 'ar4_create_parameter_interface.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)
        self.save_and_check(ws, expected_file, generated_file, filters=['/PortInterfaces'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        pif2 = ws2.find(pif1.ref)
        self.assertIsInstance(pif2, autosar.portinterface.ParameterInterface)
        self.assertEqual(len(pif2.parameters), 1)
        param = pif2.parameters[0]
        self.assertEqual(param.name, 'v')
        self.assertEqual(param.typeRef, '/DataTypes/boolean')


if __name__ == '__main__':
    unittest.main()
