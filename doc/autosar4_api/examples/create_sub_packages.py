import autosar
ws = autosar.workspace("4.2.2")
datatypes = ws.createPackage('DataTypes')
datatypes.createSubPackage('BaseTypes')
datatypes.createSubPackage('ImplementationTypes', role='DataType')
