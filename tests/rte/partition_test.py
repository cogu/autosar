import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
import unittest

### BEGIN TEST DATA

def apply_test_data(ws):
   package=ws.createPackage("DataType", role="DataType")
   package.createSubPackage("DataTypeSemantics", role="CompuMethod")
   package.createSubPackage("DataTypeUnits", role="Unit")
   package.createBooleanDataType('Boolean')
   package.createIntegerDataType('SInt8', -128, 127)
   package.createIntegerDataType('SInt16', -32768, 32767)
   package.createIntegerDataType('SInt32', -2147483648, 2147483647)
   package.createIntegerDataType('UInt8', 0, 255)
   package.createIntegerDataType('UInt16', 0, 65535)
   package.createIntegerDataType('UInt32', 0, 4294967295)
   package.createRealDataType('Float', None, None, minValType='INFINITE', maxValType='INFINITE')
   package.createRealDataType('Double', None, None, minValType='INFINITE', maxValType='INFINITE', hasNaN=True, encoding='DOUBLE')
   package.createIntegerDataType('ButtonStatus_T', valueTable=['ButtonStatus_Released','ButtonStatus_Pressed','ButtonStatus_Error','ButtonStatus_NotAvailable'])
   
   valueTableList = [
                       'VehicleModeInternal_Off',
                       'VehicleModeInternal_Accessory',
                       'VehicleModeInternal_Run',
                       'VehicleModeInternal_Crank',
                       'VehicleModeInternal_Spare1',
                       'VehicleModeInternal_Spare2',
                       'VehicleModeInternal_Error',
                       'VehicleModeInternal_NotAvailable'
                    ]
   package.createIntegerDataType('VehicleModeInternal_T', valueTable=valueTableList)
   package.createIntegerDataType('BspApi_DigitalId_T', 0, 255, offset=0, scaling=1/1, forceFloatScaling=True, unit='Id')
   package.createIntegerDataType('BspApi_DigitalState_T', valueTable=['BspApi_DigitalState_Inactive','BspApi_DigitalState_Active','BspApi_DigitalState_Error','BspApi_DigitalState_NotAvailable'])
   package=ws.createPackage("Constant", role="Constant")
   package.createConstant('ButtonStatus_IV', 'ButtonStatus_T', 3)
   package.createConstant('VehicleModeInternal_IV', 'VehicleModeInternal_T', 7)
   package=ws.createPackage("PortInterface", role="PortInterface")
   package.createSenderReceiverInterface("EcuM_CurrentMode", modeGroups=autosar.ModeGroup("currentMode", "/ModeDclrGroup/EcuM_Mode"), isService=True, adminData={"SDG_GID": "edve:BSWM", "SD": "EcuM"})
   package.createSenderReceiverInterface("ButtonStatus_I", autosar.DataElement('ButtonStatus', 'ButtonStatus_T'))
   package.createSenderReceiverInterface("VehicleModeInternal_I", autosar.DataElement('VehicleModeInternal', 'VehicleModeInternal_T'))
   portInterface=package.createClientServerInterface("BspApi_I", ["GetDiscreteInput", "SetDiscreteOutput"], autosar.ApplicationError("E_NOT_OK", 1), isService=True)
   portInterface["GetDiscreteInput"].createInArgument("inputId", "BspApi_DigitalId_T")
   portInterface["GetDiscreteInput"].createOutArgument("inputValue", "BspApi_DigitalState_T")
   portInterface["SetDiscreteOutput"].createInArgument("outputId", "BspApi_DigitalId_T")
   portInterface["SetDiscreteOutput"].createInArgument("outputValue", "BspApi_DigitalState_T")
   portInterface["SetDiscreteOutput"].possibleErrors = "E_NOT_OK"
   package=ws.createPackage("ModeDclrGroup", role="ModeDclrGroup")
   package.createModeDeclarationGroup("EcuM_Mode", ["POST_RUN", "RUN", "SHUTDOWN", "SLEEP", "STARTUP", "WAKE_SLEEP"], "STARTUP", adminData={"SDG_GID": "edve:BSWM", "SD": "EcuM"})
   package=ws.createPackage("ComponentType", role="ComponentType")
   swc = package.createApplicationSoftwareComponent('SteeringWheelButtonReader')
   swc.createProvidePort('SWS_PushButtonStatus_Back', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createProvidePort('SWS_PushButtonStatus_Down', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createProvidePort('SWS_PushButtonStatus_Enter', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createProvidePort('SWS_PushButtonStatus_Home', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createProvidePort('SWS_PushButtonStatus_Left', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createProvidePort('SWS_PushButtonStatus_Right', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createProvidePort('SWS_PushButtonStatus_Up', 'ButtonStatus_I', initValueRef='ButtonStatus_IV')
   swc.createRequirePort('EcuM_CurrentMode', 'EcuM_CurrentMode')
   swc.createRequirePort('VehicleModeInternal', 'VehicleModeInternal_I', initValueRef='VehicleModeInternal_IV')
   swc.createRequirePort('BspApi', 'BspApi_I')
   
   portAccessList = [
                       'SWS_PushButtonStatus_Back',
                       'SWS_PushButtonStatus_Down',
                       'SWS_PushButtonStatus_Enter',
                       'SWS_PushButtonStatus_Home',
                       'SWS_PushButtonStatus_Left',
                       'SWS_PushButtonStatus_Right',
                       'SWS_PushButtonStatus_Up'
                    ]
   swc.behavior.createRunnable('SteeringWheelButtonReader_Init', portAccess=portAccessList)
   
   portAccessList = [
                       'SWS_PushButtonStatus_Back',
                       'SWS_PushButtonStatus_Down',
                       'SWS_PushButtonStatus_Enter',
                       'SWS_PushButtonStatus_Home',
                       'SWS_PushButtonStatus_Left',
                       'SWS_PushButtonStatus_Right',
                       'SWS_PushButtonStatus_Up'
                    ]
   swc.behavior.createRunnable('SteeringWheelButtonReader_Exit', portAccess=portAccessList)
   
   portAccessList = [
                       'VehicleModeInternal',
                       'SWS_PushButtonStatus_Back',
                       'SWS_PushButtonStatus_Down',
                       'SWS_PushButtonStatus_Enter',
                       'SWS_PushButtonStatus_Home',
                       'SWS_PushButtonStatus_Left',
                       'SWS_PushButtonStatus_Right',
                       'SWS_PushButtonStatus_Up',
                       'BspApi/GetDiscreteInput'
                    ]
   swc.behavior.createRunnable('SteeringWheelButtonReader_Run', portAccess=portAccessList)
   swc.behavior.createTimingEvent('SteeringWheelButtonReader_Run', period=10)
   swc.behavior.createModeSwitchEvent('SteeringWheelButtonReader_Init', 'EcuM_CurrentMode/RUN')

### END TEST DATA

class TestPartition(unittest.TestCase):
   
   def test_addComponent(self):
      ws = autosar.workspace()
      apply_test_data(ws)
      partition = autosar.rte.Partition()
      partition.addComponent(ws.find('/ComponentType/SteeringWheelButtonReader'))
      self.assertEqual(len(partition.components), 1)
   
   def test_unconnected(self):
      ws = autosar.workspace()
      apply_test_data(ws)
      partition = autosar.rte.Partition()
      partition.addComponent(ws.find('/ComponentType/SteeringWheelButtonReader'))
      self.assertEqual(len(partition.components), 1)
      unconnected = list(partition.unconnectedPorts())
      self.assertEqual(len(unconnected), 10)

   

if __name__ == '__main__':
   unittest.main()