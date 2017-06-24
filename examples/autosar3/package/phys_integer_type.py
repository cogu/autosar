import autosar

ws = autosar.workspace()
package=ws.createPackage("DataType", role="DataType")
package.createSubPackage('DataTypeSemantics', role='CompuMethod')
package.createSubPackage('DataTypeUnits', role='Unit')

BatteryCurrent_T = package.createIntegerDataType('BatteryCurrent_T', min=0, max=65535, offset=-1600, scaling=0.05, unit="Ampere")
BatteryCurrent_T.desc = "65024-65279 Error; 65280 - 65535 Not Available"

ws.saveXML('DataTypes.arxml', packages=['DataType'])