import autosar

def apply(ws):
   package=ws.createPackage("DataType", role="DataType")
   package.createSubPackage('DataTypeSemantics', role='CompuMethod')
   package.createSubPackage('DataTypeUnits', role='Unit')
   #enumeration types
   package.createIntegerDataType('DisabledEnabled_T',valueTable=[
        'DisabledEnabled_Disabled',
        'DisabledEnabled_Enabled',
        'DisabledEnabled_Error',
        'DisabledEnabled_NotAvailable'])
   package.createIntegerDataType('InactiveActive_T',valueTable=[
        'InactiveActive_Inactive',
        'InactiveActive_Active',
        'InactiveActive_Error',
        'InactiveActive_NotAvailable'])
   package.createIntegerDataType('OffOn_T',valueTable=[
        'OffOn_Off',
        'OffOn_On',
        'OffOn_Error',
        'OffOn_NotAvailable'])
   
   #physical unit types
   BatteryCurrent_T = package.createIntegerDataType('BatteryCurrent_T', min=0, max=65535, offset=-1600, scaling=0.05, unit="Ampere")
   BatteryCurrent_T.desc = "65024-65279 Error; 65280 - 65535 Not Available"
   BatteryVoltage_T = package.createIntegerDataType('BatteryVoltage_T', min=0, max=65535, offset=-1600, scaling=0.05, unit="Voltage")
   BatteryVoltage_T.desc = "65024-65279 Error; 65280 - 65535 Not Available"
   TemperatureLoRes_T = package.createIntegerDataType('TemperatureLowRes_T', min=0, max=255, offset=-40, scaling=1, unit="DegreeC")
   TemperatureLoRes_T.desc = "254 Error; 255 Not Available"
   package.createIntegerDataType('DistanceHighRes_T', min=0, max=4294967295, offset=0, scaling=1, unit='Meters')
   package.createIntegerDataType('EngineSpeed_T', min=0, max=65535, offset=0, scaling=1/8, unit='RPM')
   package.createIntegerDataType('VehicleSpeed_T', min=0, max=65535, offset=0, scaling=1/64, unit='KPH')
   Hours_T = package.createIntegerDataType('Hours_T', min=0, max=255, offset=1, scaling=1, unit='Hour')
   Hours_T.desc = "24-253 Invalid Range; 254 Error; 255 Not Available"
   Minutes_T = package.createIntegerDataType('Minutes_T', min=0, max=255, offset=1, scaling=1, unit='Minute')
   Minutes_T.desc = "60-253 Invalid Range; 254 Error; 255 Not Available"
   Seconds_T = package.createIntegerDataType('Seconds_T', min=0, max=255, offset=1, scaling=1, unit='Second')
   Seconds_T.desc = "60-253 Invalid Range; 254 Error; 255 Not Available"
   DayOfMonth_T = package.createIntegerDataType('DayOfMonth_T', min=0, max=255, offset=1, scaling=1, unit='DayOfMonth')
   DayOfMonth_T.desc = "31-253 Invalid Range; 254 Error; 255 Not Available"
   Month_T = package.createIntegerDataType('Month_T', min=0, max=255, offset=1, scaling=1, unit='Month')
   Month_T.desc = "12-253 Invalid Range; 254 Error; 255 Not Available"
   Year_T = package.createIntegerDataType('Year_T', min=0, max=255, offset=2000, scaling=1, unit='Year')
   Year_T.desc = "254 Error; 255 Not Available"
   
   #array types
   
   #record types
   elementList = [
                  ('Day','DayOfMonth_T'),
                  ('Month','Month_T'),
                  ('Year','Year_T'),
   ]
   package.createRecordDataType('Date_T', elementList)

   elementList = [
                  ('Seconds','Seconds_T'),
                  ('Minutes','Minutes_T'),
                  ('Hours','Hours_T'),
   ]
   package.createRecordDataType('TimeOfDay_T', elementList)

if __name__ == '__main__':
   ws = autosar.workspace()
   apply(ws)
   ws.saveXML('DataTypes_01.arxml', filters=['DataType'])