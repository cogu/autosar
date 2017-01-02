:mod:`autosar.datatype` --- DataTypes
======================================

**Usage:**

.. code-block:: python

   import autosar
   
   ws=autosar.workspace()
   
   dataTypes=ws.createPackage('DataType')
   dataTypes.createSubPackage('DataTypeSemantics', role='CompuMethod')
   dataTypes.createSubPackage('DataTypeUnits', role='Unit')
   
   dataTypes.createIntegerDataType('EngineSpeed_T', min=0, max=65535, offset=0, scaling=1/8, unit='rpm')
   dataTypes.createIntegerDataType('VehicleSpeed_T', min=0, max=65535, offset=0, scaling=1/64,unit='kph')
   dataTypes.createIntegerDataType('Percent_T', min=0, max=255, offset=0, scaling=0.4, unit='Percent')
   dataTypes.createIntegerDataType('CoolantTemp_T', min=0, max=255, offset=-40, scaling=0.5, unit='DegreeC')
   dataTypes.createIntegerDataType('InactiveActive_T', valueTable=[
        'InactiveActive_Inactive',
        'InactiveActive_Active',
        'InactiveActive_Error',
        'InactiveActive_NotAvailable'])
   dataTypes.createIntegerDataType('OnOff_T', valueTable=[
       "OnOff_Off",
       "OnOff_On",
       "OnOff_Error",
       "OnOff_NotAvailable"])
   
   ws.saveXML('DataTypes.arxml')

.. _IntegerDataType:

   .. py:class:: IntegerDataType(name : str, minVal : int = 0, maxVal : int = 0, compuMethodRef : object = None)
      
      The IntegerDataType is used to represent integer data types.
         
   .. py:attribute:: IntegerDataType.name
   
      The name of the object as a string.
     
   .. py:attribute:: IntegerDataType.ref
      
      (readonly) reference to the object as a string.
   .. note::
   
      In order for the object to get a valid reference attribute it must first be added to a package in the workspace.
   
   .. py:attribute:: IntegerDataType.minVal
      
      Minimum value of the integer type (default value=0).

   .. py:attribute:: IntegerDataType.maxVal
      
      Maximum value of the integer type (default value=0).
   
   .. py:attribute:: IntegerDataType.compuMethodRef
   
      reference to a compuMethodRef in case this datatype is going to be used as an enumeration or it represents a physical relation (scaling+offset).
