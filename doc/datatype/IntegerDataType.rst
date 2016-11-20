IntegerDataType
===============

**Usage:**

.. code-block:: python

   import autosar
   
   ws = autosar.workspace()
   dataTypePackage=ws.createPackage('DataType')
   semanticsPackage=ws.createPackage('DataTypeSemantics')   

   compuMethod=autosar.CompuMethodConst('InactiveActiveSpare_T',['InactiveActiveSpare_Inactive','InactiveActiveSpare_Active','InactiveActiveSpare_Spare','InactiveActiveSpare_NotAvailable'])
   semanticsPackage.append(compuMethod)
   InactiveActiveSpare_T=autosar.IntegerDataType('InactiveActiveSpare_T',0,3,compuMethodRef=compuMethod.ref)
   dataTypePackage.append(InactiveActiveSpare_T)

   ws.saveXML('DataTypes.arxml')

.. _IntegerDataType:

   .. py:class:: IntegerDataType(name : str, minval : int = 0, maxval : int = 0, compuMethodRef : object = None)
      
      The IntegerDataType is used to represent integer data types.
         
   .. py:attribute:: IntegerDataType.name
   
      The name of the object as a string.
     
   .. py:attribute:: IntegerDataType.ref
      
      (readonly) reference to the object as a string.
   .. note::
   
      In order for the object to get a valid reference attribute it must first be added to a package in the workspace.
   
   .. py:attribute:: IntegerDataType.minval
      
      Minimum value of the integer type (default value=0).

   .. py:attribute:: IntegerDataType.maxval
      
      Maximum value of the integer type (default value=0).
   
   .. py:attribute:: IntegerDataType.compuMethodRef
   
      reference to a compuMethodRef in case this datatype is going to be used as an enumeration or it represents a physical relation (scaling+offset).
