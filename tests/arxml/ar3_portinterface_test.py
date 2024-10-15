import os, sys

import autosar.element
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest
import warnings
warnings.simplefilter("error", DeprecationWarning)

def _create_packages(ws):

    package = ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')    
    ws.createPackage('PortInterfaces', role="PortInterface")
    

def _create_data_types(ws):
    package = ws.find('/DataTypes')
    package.createIntegerDataType('UInt8', min=0, max=255)
    package.createIntegerDataType('UInt16', min=0, max=65535)
    package.createIntegerDataType('UInt32', min=0, max=4294967295)
    package.createIntegerDataType('Boolean', valueTable=['FALSE','TRUE'])
    package.createIntegerDataType('OffOn_T', valueTable = ['OffOn_Off',
                                                          'OffOn_On',
                                                          'OffOn_Error',
                                                          'OffOn_NotAvailable'
                                                        ])
    package.createIntegerDataType('Seconds_T', min=0, max=63)
    package.createIntegerDataType('Minutes_T', min=0, max=63)
    package.createIntegerDataType('Hours_T', min=0, max=31)
    

def _init_ws(ws):
    _create_packages(ws)
    _create_data_types(ws)

class ARXML3PortInterfaceTest(ARXMLTestClass):
    
    def test_create_sender_receiver_interface_single_element(self):
        ws = autosar.workspace(version="3.0.2")
        _init_ws(ws)
        package = ws.find('/PortInterfaces')
        itf1 =  package.createSenderReceiverInterface('HeaterPwrStat_I', autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'HeaterPwrStat', 'OffOn_T'))
        file_name = 'ar3_sender_receiver_interface_single_element.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)        
        self.save_and_check(ws, expected_file, generated_file)
        # ws2 = autosar.workspace(version="4.2.2")
        # ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        # itf2 = portInterface = ws2.find(itf1.ref)
        # self.assertIsInstance(itf2, autosar.portinterface.SenderReceiverInterface)
        
    # def test_create_sender_receiver_interface_multiple_elements_explicit(self):
    #     ws = autosar.workspace(version="4.2.2")
    #     _init_ws(ws)
    #     package = ws.find('/PortInterfaces')
    #     itf1 = package.createSenderReceiverInterface('SystemTime_I', [
    #         autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'Seconds', '/DataTypes/Seconds_T'),
    #         autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'Minutes', '/DataTypes/Minutes_T'),
    #         autosar.element.AutosarDataPrototype(autosar.element.AutosarDataPrototype.Role.Variable, 'Hours', '/DataTypes/Hours_T')
    #         ])
    #     file_name = 'ar4_sender_receiver_interface_multiple_elements_explicit.arxml'
    #     generated_file = os.path.join(self.output_dir, file_name)
    #     expected_file = os.path.join( 'expected_gen', 'portinterface', file_name)        
    #     self.save_and_check(ws, expected_file, generated_file)
    #     ws2 = autosar.workspace(version="4.2.2")
    #     ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
    #     itf2 = portInterface = ws2.find(itf1.ref)
    #     self.assertIsInstance(itf2, autosar.portinterface.SenderReceiverInterface)        
        
if __name__ == '__main__':
    unittest.main()